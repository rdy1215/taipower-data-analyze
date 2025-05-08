import importlib
import pandas as pd
import electricity_lib as ec_lib

importlib.reload(ec_lib)

# 讀取 Excel 檔案
FILE_PATH = "test_data.xlsx"
# 設定合約類型與釋放類型
CONTRACT_TYPE = ec_lib.ContractType.HIGH_PRESSURE_THREE_PHASE
RELEASE_TYPE = ec_lib.ReleaseType.MAX
# 設定電池容量
BATTERY_KWH = 261 * 2 * 0.95
BATTERY_KW = 125 * 2 * 0.95

# columns define
TIME_COL = "時間"
USAGE_COL = "用電總量"
BATTERY_KW_COL = "電池放電功率"
BATTERY_KWH_COL = "電池容量"
USAGE_WITH_BATTERY_COL = "增加電池後用電量"
DEFAULT_DROP_COLS = ["儲冷尖峰", "儲冷半尖峰", "儲冷週六半尖峰", "儲冷離峰", "太陽光電"]
SUM_COLS = ["尖峰", "半尖峰", "週六半尖峰", "離峰"]


def in_peak_hour(date, elec_type_dict):
    """
    判斷是否在尖峰時段的函數
    :param date: 日期
    :param time: 時間
    :param elec_type_dict: 尖峰時段字典
    :return: 是否在尖峰時段
    """
    result = False
    peak_hour = []
    if ec_lib.is_summer(date):
        peak_hour = elec_type_dict.get(ec_lib.SeasonType.SUMMER).get(
            ec_lib.UsageType.PEAK
        )
    else:
        elec_hour_dict = elec_type_dict.get(ec_lib.SeasonType.NONSUMMER)
        if ec_lib.UsageType.PEAK in elec_hour_dict:
            peak_hour = elec_hour_dict.get(ec_lib.UsageType.PEAK)
        else:
            peak_hour = elec_hour_dict.get(ec_lib.UsageType.SEMI_PEAK)
    peak_hour = pd.to_datetime(peak_hour, format="%H:%M:%S").time
    date_time = date.time()
    # 判斷時間是否在尖峰時段
    for i in range(0, len(peak_hour), 2):
        start_time = peak_hour[i]
        end_time = peak_hour[i + 1]
        if start_time <= date_time <= end_time:
            result = True
            break
    return result


def get_peak_hour_usage(data, time_col, usage_col, elec_type_dict):
    """
    顯示尖峰時段用電總量的函數
    :param data: 數據集
    :param time_col: 時間欄位名稱
    :param usage_col: 用電總量欄位名稱
    """
    # 篩選需要的時間段和欄位
    filtered_data = data[
        data[time_col].apply(lambda x: in_peak_hour(x, elec_type_dict))
    ]
    # 按日期統計用電總量
    return filtered_data.groupby(filtered_data[time_col].dt.date)[usage_col].sum()


def cal_default_charge_kw(date, charge_hour_dict):
    charge_hour_list = []
    if ec_lib.is_summer(date):
        charge_hour_list = charge_hour_dict.get(ec_lib.SeasonType.SUMMER)
    else:
        charge_hour_list = charge_hour_dict.get(ec_lib.SeasonType.NONSUMMER)
    charge_hour_list = pd.to_datetime(charge_hour_list, format="%H:%M:%S").time
    charge_power = 0.0
    for i in range(0, len(charge_hour_list), 2):
        start_time = charge_hour_list[i]
        end_time = charge_hour_list[i + 1]
        if start_time <= date.time() <= end_time:
            charge_power = BATTERY_KW
            break
    return charge_power


def cal_default_release_kw(date, release_hour_dict, release_type):
    release_hour_list = []
    if ec_lib.is_summer(date):
        release_hour_list = release_hour_dict.get(ec_lib.SeasonType.SUMMER)
    else:
        release_hour_list = release_hour_dict.get(ec_lib.SeasonType.NONSUMMER)
    release_hour_list = pd.to_datetime(release_hour_list, format="%H:%M:%S").time
    release_power = 0.0
    for i in range(0, len(release_hour_list), 2):
        start_time = release_hour_list[i]
        end_time = release_hour_list[i + 1]
        if start_time <= date.time() <= end_time:
            if release_type == ec_lib.ReleaseType.MAX:
                release_power = BATTERY_KW
            elif release_type == ec_lib.ReleaseType.AVERAGE:
                release_power = (
                    BATTERY_KWH / ((end_time - start_time).seconds + 1) / 3600.0
                )
            break
    return release_power


def cal_actual_release_power(usage, default_release_kw, last_remain_kw):
    release_kw = 0.0
    usage_kw = usage * 4
    if usage_kw > default_release_kw:
        if last_remain_kw > 0.0:
            sum_kw = default_release_kw + last_remain_kw
            if usage_kw > sum_kw and sum_kw <= BATTERY_KW:
                release_kw = sum_kw
            elif usage_kw > sum_kw and sum_kw > BATTERY_KW:
                release_kw = BATTERY_KW
            else:
                release_kw = usage_kw
        else:
            release_kw = default_release_kw
    else:
        release_kw = usage_kw
    return release_kw


def process_battery_usage(
    row,
    time_col,
    usage_col,
    release_hour_dict,
    charge_hour_dict,
    release_type,
    remain_battery_kw_list,
    battery_kwh_list,
):
    date_time = row[time_col]
    origin_usage = row[usage_col]
    last_remain_kw = (
        remain_battery_kw_list[-1] if len(remain_battery_kw_list) > 0 else 0.0
    )
    last_battery_kwh = battery_kwh_list[-1] if len(battery_kwh_list) > 0 else 0.0
    battery_kw = 0.0
    if ec_lib.is_workday(date_time):
        charge_kw = cal_default_charge_kw(date_time, charge_hour_dict)
        if charge_kw == 0.0:
            default_release_kw = cal_default_release_kw(
                date_time, release_hour_dict, release_type
            )
            if default_release_kw != 0.0:
                battery_kw = cal_actual_release_power(
                    origin_usage, default_release_kw, last_remain_kw
                )
                if battery_kw < (default_release_kw + last_remain_kw):
                    remain_battery_kw_list.append(
                        (default_release_kw + last_remain_kw) - battery_kw
                    )
                else:
                    remain_battery_kw_list.append(0.0)
            else:
                battery_kw = 0.0
        else:
            if (BATTERY_KWH - last_battery_kwh) > charge_kw / 4:
                battery_kw = -charge_kw
            else:
                battery_kw = -(BATTERY_KWH - last_battery_kwh) * 4
    battery_kwh = battery_kw / 4
    battery_kwh_list.append(last_battery_kwh - battery_kwh)
    return battery_kw, last_battery_kwh - battery_kwh, origin_usage - battery_kwh
