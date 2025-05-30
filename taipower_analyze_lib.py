import importlib
import pandas as pd
from dataclasses import dataclass
import electricity_lib as ec_lib

importlib.reload(ec_lib)

# 設定合約類型與釋放類型
RAW_CONTRACT_TYPE = ec_lib.ContractType.HIGH_PRESSURE_THREE_PHASE
CONTRACT_TYPE = ec_lib.ContractType.HIGH_PRESSURE_THREE_PHASE
RELEASE_TYPE = ec_lib.ReleaseType.AVERAGE
CHARGE_TYPE = ec_lib.ChargeType.AVERAGE

# 讀取 Excel 檔案
METER_NO = "澤米"
METER_DATA_FILE_PATH = f"./data/meter_{METER_NO}_data.xlsx"
METER_CONTRACT_FILE_PATH = f"./data/info_{METER_NO}_data.xlsx"
OUTPUT_FOLDER = f"./output/{METER_NO}/{CONTRACT_TYPE.value}/"

BATTERY_BUFFER = 0.9
BATTERY_DECAY = 0.98
BATTERY_DOD = 0.2

# 設定電池容量
DEVICE_NUMBER = 15
BATTERY_KWH = 261 * DEVICE_NUMBER * BATTERY_BUFFER
BATTERY_KW = 125 * DEVICE_NUMBER * BATTERY_BUFFER

KWH_PRICE = 9000
DR_AVG_PRICE = 280
DR_REACTION_FREQ = 1 / 24 / 30
DR_ENERGY_PRICE = 4
NEW_CONTRACT_BUFFER = 1.1
CHARGE_LOSS = 0.85

MONTH_LIST = [
    "一月",
    "二月",
    "三月",
    "四月",
    "五月",
    "六月",
    "七月",
    "八月",
    "九月",
    "十月",
    "十一月",
    "十二月",
]

# columns define
# 預設資訊欄位
DEFAULT_DROP_COLS = ["經常", "儲冷尖峰", "儲冷半尖峰", "儲冷週六半尖峰", "儲冷離峰", "太陽光電"]
SUM_COLS = ["尖峰", "半尖峰", "週六半尖峰", "離峰"]


# 基本用電資訊欄位名稱
@dataclass
class MeterUsageColumns:
    time_col: str = "時間"
    usage_col: str = "用電總量"
    battery_kw_col: str = "電池放電功率"
    charge_kwh_col: str = "電池充電量"
    release_kwh_col: str = "電池放電量"
    battery_kwh_col: str = "電池容量"
    usage_with_battery_col: str = "增加電池後用電量"
    dr_volume_col: str = "需量反應投標量"


@dataclass
class ElectricPriceColumns:
    elec_charge_price_col: str = "原始流動電價"
    elec_charge_price_with_battery_col: str = "增加電池後流動電價"
    demand_price_col: str = "需量價金"


@dataclass
class ElectricParameters:
    raw_elec_type_dict: dict
    elec_type_dict: dict
    release_hour_dict: dict
    charge_hour_dict: dict
    raw_contract_type = ec_lib.ContractType = RAW_CONTRACT_TYPE
    contract_type: ec_lib.ContractType = CONTRACT_TYPE
    release_type: ec_lib.ReleaseType = RELEASE_TYPE
    CHARGE_TYPE: ec_lib.ChargeType = CHARGE_TYPE


@dataclass
class ElecetricPriceParameters:
    raw_charge_price_dict: dict
    new_charge_price_dict: dict
    raw_contract_price_dict: dict
    contract_price_dict: dict


@dataclass
class YearlyProfitColumns:
    year_col: str = "年度"
    charge_profit_col: str = "尖離峰套利利潤"
    contract_profit_col: str = "基本電價差利潤"
    dr_profit_col: str = "需量反應價金"
    total_profit_col: str = "年度效益"
    cumulative_profit_col: str = "累計效益"


def build_output_folder():
    """
    建立輸出資料夾
    """
    import os
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)


def contract_df_to_dict(df):
    return {
        ec_lib.UsageType.PEAK: df["UsuallyContract"].values[0],
        ec_lib.UsageType.SEMI_PEAK: df["NoSummerOrHalfRushContract"].values[0],
        ec_lib.UsageType.SATURDAY_SEMI_PEAK:
        df["SaturdayHalfContract"].values[0],
        ec_lib.UsageType.OFF_PEAK: df["NoRushContract"].values[0],
    }


def group_all_data_withour_dr_in_freq(
    data,
    freq,
    usage_cols: MeterUsageColumns,
    elec_price_cols: ElectricPriceColumns,
):
    # 按日期統計用電總量
    return (data.groupby(pd.Grouper(key=usage_cols.time_col, freq=freq)).agg({
        usage_cols.usage_col:
        "sum",
        usage_cols.battery_kw_col:
        "mean",
        usage_cols.battery_kwh_col:
        "mean",
        usage_cols.usage_with_battery_col:
        "sum",
        usage_cols.charge_kwh_col:
        "sum",
        usage_cols.release_kwh_col:
        "sum",
        elec_price_cols.elec_charge_price_col:
        "sum",
        elec_price_cols.elec_charge_price_with_battery_col:
        "sum",
    }).reset_index())


def group_all_data_in_freq(
    data,
    freq,
    usage_cols: MeterUsageColumns,
    elec_price_cols: ElectricPriceColumns,
):
    # 按日期統計用電總量
    return (data.groupby(pd.Grouper(key=usage_cols.time_col, freq=freq)).agg({
        usage_cols.usage_col:
        "sum",
        usage_cols.battery_kw_col:
        "mean",
        usage_cols.battery_kwh_col:
        "mean",
        usage_cols.usage_with_battery_col:
        "sum",
        usage_cols.charge_kwh_col:
        "sum",
        usage_cols.release_kwh_col:
        "sum",
        usage_cols.dr_volume_col:
        "sum",
        elec_price_cols.elec_charge_price_col:
        "sum",
        elec_price_cols.elec_charge_price_with_battery_col:
        "sum",
        elec_price_cols.demand_price_col:
        "sum",
    }).reset_index())


def group_max_data_in_freq(
    data,
    freq,
    usage_cols: MeterUsageColumns,
    elec_price_cols: ElectricPriceColumns,
):
    # 按日期統計用電總量
    return (data.groupby(pd.Grouper(key=usage_cols.time_col, freq=freq)).agg({
        usage_cols.usage_col:
        "max",
        usage_cols.battery_kw_col:
        "max",
        usage_cols.battery_kwh_col:
        "max",
        usage_cols.usage_with_battery_col:
        "max",
        usage_cols.charge_kwh_col:
        "max",
        usage_cols.release_kwh_col:
        "max",
        usage_cols.dr_volume_col:
        "max",
        elec_price_cols.elec_charge_price_col:
        "max",
        elec_price_cols.elec_charge_price_with_battery_col:
        "max",
        elec_price_cols.demand_price_col:
        "max",
    }).reset_index())


def group_max_data_without_dr_in_freq(
    data,
    freq,
    usage_cols: MeterUsageColumns,
    elec_price_cols: ElectricPriceColumns,
):
    # 按日期統計用電總量
    return (data.groupby(pd.Grouper(key=usage_cols.time_col, freq=freq)).agg({
        usage_cols.usage_col:
        "max",
        usage_cols.battery_kw_col:
        "max",
        usage_cols.battery_kwh_col:
        "max",
        usage_cols.usage_with_battery_col:
        "max",
        usage_cols.charge_kwh_col:
        "max",
        usage_cols.release_kwh_col:
        "max",
        elec_price_cols.elec_charge_price_col:
        "max",
        elec_price_cols.elec_charge_price_with_battery_col:
        "max",
    }).reset_index())


def is_expensive_hour(datetime, elec_params: ElectricParameters):
    result = False
    usage_type = ec_lib.get_usage_type_from_dict(datetime,
                                                 elec_params.elec_type_dict)
    is_summer = ec_lib.is_summer(datetime)
    if elec_params.contract_type == ec_lib.ContractType.HIGH_PRESSURE_THREE_PHASE:
        if is_summer and usage_type == ec_lib.UsageType.PEAK:
            result = True
        elif not is_summer and usage_type == ec_lib.UsageType.SEMI_PEAK:
            result = True
    elif elec_params.contract_type == ec_lib.ContractType.HIGH_PRESSURE_BATCH:
        if usage_type == ec_lib.UsageType.PEAK:
            result = True
    return result


def filter_expensive_usage(
    data,
    usage_cols: MeterUsageColumns,
    elec_params: ElectricParameters,
):
    return data[data[usage_cols.time_col].apply(
        lambda x: is_expensive_hour(x, elec_params))]


def filter_expensive_usage_in_freq(
    data,
    freq,
    usage_cols: MeterUsageColumns,
    elec_price_cols: ElectricPriceColumns,
    elec_params: ElectricParameters,
):
    """
    顯示尖峰時段用電總量的函數
    :param data: 數據集
    :param time_col: 時間欄位名稱
    :param usage_col: 用電總量欄位名稱
    """
    # 篩選需要的時間段和欄位
    expensive_hour_data = filter_expensive_usage(data, usage_cols, elec_params)
    return group_all_data_withour_dr_in_freq(expensive_hour_data, freq,
                                             usage_cols, elec_price_cols)


def cal_default_charge_kw(date, charge_hour_dict,
                          charge_type: ec_lib.ChargeType):
    charge_hour_list = []
    if ec_lib.is_summer(date):
        charge_hour_list = charge_hour_dict.get(ec_lib.SeasonType.SUMMER)
    else:
        charge_hour_list = charge_hour_dict.get(ec_lib.SeasonType.NONSUMMER)
    charge_hour_list = pd.to_datetime(charge_hour_list, format="%H:%M:%S")
    charge_power = 0.0
    for i in range(0, len(charge_hour_list), 2):
        start_time = charge_hour_list[i]
        end_time = charge_hour_list[i + 1]
        if start_time.time() <= date.time() <= end_time.time():
            if charge_type == ec_lib.ChargeType.MAX:
                charge_power = BATTERY_KW
            elif charge_type == ec_lib.ChargeType.AVERAGE:
                time_duration = (end_time - start_time).seconds + 1
                if i > 1:
                    next_start_time = charge_hour_list[0]
                    if end_time.time() == (next_start_time -
                                           pd.Timedelta(seconds=1)).time():
                        next_end_time = charge_hour_list[1]
                        time_duration += (next_end_time -
                                          next_start_time).seconds + 1
                charge_power = (BATTERY_KWH *
                                (1 - BATTERY_DOD)) / (time_duration / 3600.0)
            break
    return charge_power


def cal_default_release_kw(date, release_hour_dict, release_type):
    release_hour_list = []
    if ec_lib.is_summer(date):
        release_hour_list = release_hour_dict.get(ec_lib.SeasonType.SUMMER)
    else:
        release_hour_list = release_hour_dict.get(ec_lib.SeasonType.NONSUMMER)
    release_hour_list = pd.to_datetime(release_hour_list, format="%H:%M:%S")
    release_power = 0.0
    for i in range(0, len(release_hour_list), 2):
        start_time = release_hour_list[i]
        end_time = release_hour_list[i + 1]
        if start_time.time() <= date.time() <= end_time.time():
            if release_type == ec_lib.ReleaseType.MAX:
                release_power = BATTERY_KW
            elif release_type == ec_lib.ReleaseType.AVERAGE:
                average_power = BATTERY_KWH * (1 - BATTERY_DOD) / ((
                    (end_time - start_time).seconds + 1) / 3600.0)
                release_power = (average_power if average_power <= BATTERY_KW
                                 else BATTERY_KW)
            break
    return release_power


def cal_actual_release_power(usage, default_release_kw, last_remain_kw,
                             last_battery_kwh):
    release_kw = 0.0
    usage_kw = usage * 4
    if last_battery_kwh > BATTERY_KWH * BATTERY_DOD:
        if usage_kw > default_release_kw:
            sum_kw = default_release_kw + last_remain_kw
            if sum_kw <= BATTERY_KW:
                if usage_kw > sum_kw:
                    release_kw = sum_kw
                else:
                    release_kw = usage_kw
            else:
                if usage_kw > BATTERY_KW:
                    release_kw = BATTERY_KW
                else:
                    release_kw = usage_kw
        else:
            release_kw = usage_kw
        if release_kw / 4 > (last_battery_kwh - BATTERY_KWH * BATTERY_DOD):
            release_kw = (last_battery_kwh - BATTERY_KWH * BATTERY_DOD) * 4
    return release_kw


def process_battery_usage(
    row,
    meter_usage_col: MeterUsageColumns,
    elec_parameters: ElectricParameters,
    remain_battery_kw_list,
    battery_kwh_list,
):
    date_time = row[meter_usage_col.time_col]
    origin_usage = row[meter_usage_col.usage_col]
    last_remain_kw = (remain_battery_kw_list[-1]
                      if len(remain_battery_kw_list) > 0 else 0.0)
    last_battery_kwh = battery_kwh_list[-1] if len(
        battery_kwh_list) > 0 else 0.0
    battery_kw, charge_kw = 0.0, 0.0
    if ec_lib.get_day_type(date_time) == ec_lib.DayType.WORKDAY:
        charge_kw = cal_default_charge_kw(date_time,
                                          elec_parameters.charge_hour_dict,
                                          elec_parameters.CHARGE_TYPE)
        if charge_kw == 0.0:
            default_release_kw = cal_default_release_kw(
                date_time,
                elec_parameters.release_hour_dict,
                elec_parameters.release_type,
            )
            if default_release_kw != 0.0 and last_battery_kwh > 0.0:
                battery_kw = cal_actual_release_power(origin_usage,
                                                      default_release_kw,
                                                      last_remain_kw,
                                                      last_battery_kwh)
                if battery_kw < (default_release_kw + last_remain_kw):
                    remain_battery_kw_list.append((default_release_kw +
                                                   last_remain_kw) -
                                                  battery_kw)
                else:
                    remain_battery_kw_list.append(0.0)
            else:
                battery_kw = 0.0
        else:
            if (BATTERY_KWH - last_battery_kwh) > charge_kw / 4:
                battery_kw = -charge_kw
            else:
                battery_kw = -(BATTERY_KWH - last_battery_kwh) * 4
            remain_battery_kw_list.append(0.0)
    battery_kwh = battery_kw / 4
    battery_kwh_list.append(last_battery_kwh - battery_kwh)
    return (
        battery_kw,
        last_battery_kwh - battery_kwh,
        origin_usage - battery_kwh,
        battery_kwh / CHARGE_LOSS if battery_kwh < 0 else 0.0,
        battery_kwh if battery_kwh > 0 else 0.0,
    )


def cal_dr_volume_and_price(usage_kwh, battery_kw, battery_kwh):
    """
    計算 DR 量&價錢
    :param usage_kwh: 用電量
    :param battery_kw: 電池功率
    :return: DR 量&價錢
    """
    dr_volume = 0
    if battery_kw < BATTERY_KW:
        remain_kw = BATTERY_KW - battery_kw
        if remain_kw > usage_kwh:
            dr_volume = usage_kwh
        else:
            dr_volume = remain_kw
    if dr_volume > battery_kwh:
        dr_volume = battery_kwh
    dr_mwh = dr_volume / 1000
    dr_price = (dr_mwh * DR_AVG_PRICE +
                dr_mwh * 1000 * DR_REACTION_FREQ * DR_ENERGY_PRICE)
    return (
        dr_mwh,
        dr_price,
    )


def cal_hourly_dr_price(raw_data, meter_usage_cols: MeterUsageColumns,
                        elec_price_cols: ElectricPriceColumns):
    """
    計算每小時的 DR 量&價格
    :param raw_data: 原始數據
    :param meter_usage_cols: 用電欄位名稱
    :return: 每小時的 DR 量&價格
    """
    hourly_data = group_all_data_withour_dr_in_freq(raw_data, "h",
                                                    meter_usage_cols,
                                                    elec_price_cols)
    hourly_data[[
        meter_usage_cols.dr_volume_col, elec_price_cols.demand_price_col
    ]] = (pd.DataFrame(
        hourly_data.apply(
            lambda row: cal_dr_volume_and_price(
                row[meter_usage_cols.usage_with_battery_col],
                row[meter_usage_cols.battery_kw_col],
                row[meter_usage_cols.battery_kwh_col],
            ),
            axis=1,
        ).tolist(), ))

    return hourly_data


def cal_elec_price(
    row,
    meter_usage_cols: MeterUsageColumns,
    elec_params: ElectricParameters,
    elec_price_params: ElecetricPriceParameters,
):
    datetime = row[meter_usage_cols.time_col]
    raw_contract_elec_type = ec_lib.get_usage_type_from_dict(
        datetime, elec_params.raw_elec_type_dict)
    new_contract_elec_type = ec_lib.get_usage_type_from_dict(
        datetime, elec_params.elec_type_dict)
    raw_price_dict = elec_price_params.raw_charge_price_dict.get(
        ec_lib.SeasonType.SUMMER if ec_lib.is_summer(datetime) else ec_lib.
        SeasonType.NONSUMMER)
    new_price_dict = elec_price_params.new_charge_price_dict.get(
        ec_lib.SeasonType.SUMMER if ec_lib.is_summer(datetime) else ec_lib.
        SeasonType.NONSUMMER)
    raw_elec_price = raw_price_dict.get(raw_contract_elec_type)
    new_elec_price = new_price_dict.get(new_contract_elec_type)
    return (
        row[meter_usage_cols.usage_col] * raw_elec_price,
        (row[meter_usage_cols.usage_col] - row[meter_usage_cols.charge_kwh_col]
         - row[meter_usage_cols.release_kwh_col]) * new_elec_price,
    )


def cal_new_contract_volume(
    raw_data,
    meter_usage_cols: MeterUsageColumns,
    elec_type_dict: dict,
    contract_type: ec_lib.ContractType,
):
    """
    計算新合約的用電量
    :param raw_data: 原始數據
    :param meter_usage_cols: 用電欄位名稱
    :return: 新合約的用電量
    """
    (
        max_usually_contract_volume,
        max_semi_peak_contract_volume,
        max_saturday_semi_peak_contract_volume,
        max_off_peak_contract_volume,
    ) = (0.0, 0.0, 0.0, 0.0)
    for index, row in raw_data.iterrows():
        date_time = row[meter_usage_cols.time_col]
        usage_type = ec_lib.get_usage_type_from_dict(date_time, elec_type_dict)
        usage_kw = row[meter_usage_cols.usage_with_battery_col] * 4
        if (usage_type == ec_lib.UsageType.PEAK
            ) and usage_kw > max_usually_contract_volume:
            max_usually_contract_volume = usage_kw
        elif (usage_type == ec_lib.UsageType.SEMI_PEAK
              ) and usage_kw > max_semi_peak_contract_volume:
            max_semi_peak_contract_volume = usage_kw
        elif (usage_type == ec_lib.UsageType.SATURDAY_SEMI_PEAK
              or usage_type == ec_lib.UsageType.OFF_PEAK
              ) and usage_kw > max_saturday_semi_peak_contract_volume:
            max_saturday_semi_peak_contract_volume = usage_kw
    max_semi_peak_contract_volume -= max_usually_contract_volume
    max_saturday_semi_peak_contract_volume = (
        max_saturday_semi_peak_contract_volume - max_usually_contract_volume -
        max_semi_peak_contract_volume)
    if contract_type == ec_lib.ContractType.HIGH_PRESSURE_BATCH:
        return {
            ec_lib.UsageType.PEAK:
            max_usually_contract_volume * NEW_CONTRACT_BUFFER,
            ec_lib.UsageType.SATURDAY_SEMI_PEAK:
            ((max_semi_peak_contract_volume +
              max_saturday_semi_peak_contract_volume) * NEW_CONTRACT_BUFFER if
             (max_semi_peak_contract_volume +
              max_saturday_semi_peak_contract_volume) > 0 else 0.0),
            ec_lib.UsageType.OFF_PEAK:
            max_off_peak_contract_volume,
        }
    elif contract_type == ec_lib.ContractType.HIGH_PRESSURE_THREE_PHASE:
        return {
            ec_lib.UsageType.PEAK:
            max_usually_contract_volume * NEW_CONTRACT_BUFFER,
            ec_lib.UsageType.SEMI_PEAK:
            (max_semi_peak_contract_volume * NEW_CONTRACT_BUFFER
             if max_semi_peak_contract_volume > 0 else 0.0),
            ec_lib.UsageType.SATURDAY_SEMI_PEAK:
            (max_saturday_semi_peak_contract_volume * NEW_CONTRACT_BUFFER
             if max_saturday_semi_peak_contract_volume > 0 else 0.0),
            ec_lib.UsageType.OFF_PEAK:
            max_off_peak_contract_volume,
        }


def cal_basic_price(contract_volume: dict, price_dict: dict):
    total_price = 0
    for i in contract_volume.keys():
        total_price += contract_volume.get(i) * price_dict.get(i)
    return total_price


def cal_monthly_basic_price(
    contract_volume: dict,
    contract_price_dict: dict,
):
    summer_price = cal_basic_price(
        contract_volume,
        contract_price_dict.get(ec_lib.SeasonType.SUMMER),
    )
    non_summer_price = cal_basic_price(
        contract_volume,
        contract_price_dict.get(ec_lib.SeasonType.NONSUMMER),
    )
    month_price_dict = {}
    for i in range(1, 13):
        if i in [5, 10]:
            month_price_dict.update(
                {MONTH_LIST[i - 1]: (summer_price + non_summer_price) / 2})
        elif i in [6, 7, 8, 9]:
            month_price_dict.update({MONTH_LIST[i - 1]: summer_price})
        else:
            month_price_dict.update({MONTH_LIST[i - 1]: non_summer_price})
    return month_price_dict


def cal_year_profit(
    monthly_data,
    contract_monthly_basic_price: dict,
    new_monthly_basic_price: dict,
    elec_price_cols: ElectricPriceColumns,
    yearly_profit_cols: YearlyProfitColumns,
):
    """
    計算年度效益
    :param monthly_data: 月度數據
    :param contract_monthly_basic_price: 原始合約電價
    :param new_monthly_basic_price: 新合約電價
    :param elec_price_cols: 電價效益欄位名稱
    :return: 年度效益
    """
    building_cost = -(BATTERY_KWH / BATTERY_BUFFER * KWH_PRICE)
    result = pd.DataFrame(columns=yearly_profit_cols.__dict__.values())
    result.loc[0] = [
        "建置年",
        0,
        0,
        0,
        0,
        building_cost,
    ]
    charge_profit = (
        monthly_data[elec_price_cols.elec_charge_price_col] -
        monthly_data[elec_price_cols.elec_charge_price_with_battery_col]
    ).sum()
    contract_profit = sum(contract_monthly_basic_price[key] -
                          new_monthly_basic_price[key]
                          for key in contract_monthly_basic_price)
    dr_profit = monthly_data[elec_price_cols.demand_price_col].sum()
    for i in range(1, 21):
        total_profit = charge_profit + contract_profit + dr_profit
        result.loc[i] = [
            f"第 {i} 年",
            charge_profit,
            contract_profit,
            dr_profit,
            total_profit,
            result.loc[i - 1][yearly_profit_cols.cumulative_profit_col] +
            total_profit,
        ]
        charge_profit *= BATTERY_DECAY
        contract_profit *= BATTERY_DECAY
        dr_profit *= BATTERY_DECAY

    result[yearly_profit_cols.cumulative_profit_col] = result[
        yearly_profit_cols.cumulative_profit_col].apply(
            lambda x: "{:.0f}".format(x))

    return result


def sum_profit(row, elec_price_cols: ElectricPriceColumns):
    """
    計算每行利潤
    :param row: 數據行
    :param elec_price_cols: 電價欄位名稱
    :return: 利潤
    """
    return row[elec_price_cols.elec_charge_price_col] - row[
        elec_price_cols.elec_charge_price_with_battery_col] + row[
            elec_price_cols.demand_price_col]


def find_most_profit_day(daily_data, meter_usage_cols: MeterUsageColumns,
                         elec_price_cols: ElectricPriceColumns):
    summer_profit_date, non_summer_profit_date = None, None
    summer_profit, non_summer_profit = 0.0, 0.0
    for index, row in daily_data.iterrows():
        date = row[meter_usage_cols.time_col]
        row_profit = sum_profit(row, elec_price_cols)
        if ec_lib.is_summer(date):
            if summer_profit_date is None or row_profit > summer_profit:
                summer_profit_date = date
                summer_profit = row_profit
        else:
            if non_summer_profit_date is None or row_profit > non_summer_profit:
                non_summer_profit_date = date
                non_summer_profit = row_profit
    return (summer_profit_date, non_summer_profit_date)
