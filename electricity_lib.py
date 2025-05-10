from enum import Enum
from datetime import datetime
import requests
import pandas as pd


def get_holiday_list(year):
    url = f"https://cdn.jsdelivr.net/gh/ruyut/TaiwanCalendar/data/{year}.json"
    response = requests.get(url)
    response_json = response.json()
    holiday_list = [item["date"] for item in response_json if item["isHoliday"]]
    return holiday_list


taiwan_holiday = get_holiday_list(datetime.now().year)
taiwan_holiday.append(get_holiday_list(datetime.now().year - 1))


class ContractType(str, Enum):
    HIGH_PRESSURE_THREE_PHASE = "高壓三段"
    HIGH_PRESSURE_BATCH = "高壓批次"


class ReleaseType(str, Enum):
    AVERAGE = "平均"
    MAX = "最大"


class SeasonType(str, Enum):
    SUMMER = "夏季"
    NONSUMMER = "非夏季"


class UsageType(str, Enum):
    PEAK = "尖峰"
    SEMI_PEAK = "半尖峰"
    SATURDAY_SEMI_PEAK = "週六半尖峰"
    OFF_PEAK = "離峰"


class DayType(str, Enum):
    WORKDAY = "工作日"
    SATURDAY = "週六"
    HOLIDAY = "週日與節假日"


def get_release_hour_dict(contract_type, release_type):
    if contract_type == ContractType.HIGH_PRESSURE_THREE_PHASE:
        if release_type == ReleaseType.AVERAGE:
            return {
                SeasonType.SUMMER: ["16:00:00", "21:00:00"],
                SeasonType.NONSUMMER: ["06:00:00", "11:00:00", "14:00:00", "23:59:59"],
            }
        elif release_type == ReleaseType.MAX:
            return {
                SeasonType.SUMMER: ["20:00:00", "22:00:00"],
                SeasonType.NONSUMMER: ["09:00:00", "11:00:00", "22:00:00", "23:59:59"],
            }
    elif contract_type == ContractType.HIGH_PRESSURE_BATCH:
        if release_type == ReleaseType.AVERAGE:
            return {
                SeasonType.SUMMER: ["15:30:00", "21:30:00"],
                SeasonType.NONSUMMER: ["15:30:00", "21:30:00"],
            }
        elif release_type == ReleaseType.MAX:
            return {
                SeasonType.SUMMER: ["19:30:00", "21:30:00"],
                SeasonType.NONSUMMER: ["19:30:00", "21:30:00"],
            }


def get_charege_hour_dict(contract_type):
    if contract_type == ContractType.HIGH_PRESSURE_THREE_PHASE:
        return {
            SeasonType.SUMMER: ["00:00:00", "02:00:00"],
            SeasonType.NONSUMMER: ["00:00:00", "02:00:00", "11:00:00", "13:00:00"],
        }
    elif contract_type == ContractType.HIGH_PRESSURE_BATCH:
        return {
            SeasonType.SUMMER: ["21:30:00", "23:30:00"],
            SeasonType.NONSUMMER: ["21:30:00", "23:30:00"],
        }


def is_summer(date_time):
    if (date_time.month > 5 or (date_time.month == 5 and date_time.day >= 16)) and (
        date_time.month < 10 or (date_time.month == 10 and date_time.day <= 15)
    ):
        return True
    else:
        return False


def get_elec_type_dict(contract_type):
    if contract_type == ContractType.HIGH_PRESSURE_THREE_PHASE:
        return {
            SeasonType.SUMMER: {
                UsageType.PEAK: ["16:00:00", "22:00:00"],
                UsageType.SEMI_PEAK: ["9:00:00", "16:00:00", "22:00:00", "23:59:59"],
                UsageType.SATURDAY_SEMI_PEAK: ["08:00:00", "15:30:00"],
                UsageType.OFF_PEAK: ["00:00:00", "09:00:00"],
            },
            SeasonType.NONSUMMER: {
                UsageType.SEMI_PEAK: ["06:00:00", "11:00:00", "14:00:00", "23:59:59"],
                UsageType.SATURDAY_SEMI_PEAK: [
                    "06:00:00",
                    "11:00:00",
                    "14:00:00",
                    "23:59:59",
                ],
                UsageType.OFF_PEAK: ["00:00:00", "06:00:00", "11:00:00", "14:00:00"],
            },
        }
    elif contract_type == ContractType.HIGH_PRESSURE_BATCH:
        return {
            SeasonType.SUMMER: {
                UsageType.PEAK: ["15:30:00", "21:30:00"],
                UsageType.SATURDAY_SEMI_PEAK: ["15:30:00", "21:30:00"],
                UsageType.OFF_PEAK: ["00:00:00", "15:30:00", "21:30:00", "23:59:59"],
            },
            SeasonType.NONSUMMER: {
                UsageType.PEAK: ["15:30:00", "21:30:00"],
                UsageType.SATURDAY_SEMI_PEAK: ["15:30:00", "21:30:00"],
                UsageType.OFF_PEAK: ["00:00:00", "15:30:00", "21:30:00", "23:59:59"],
            },
        }


def get_contract_price_dict(contract_type):
    if contract_type == ContractType.HIGH_PRESSURE_THREE_PHASE:
        return {
            SeasonType.SUMMER: {
                UsageType.PEAK: 217.3,
                UsageType.SEMI_PEAK: 160.6,
                UsageType.SATURDAY_SEMI_PEAK: 43.4,
                UsageType.OFF_PEAK: 43.4,
            },
            SeasonType.NONSUMMER: {
                UsageType.PEAK: 160.6,
                UsageType.SEMI_PEAK: 160.6,
                UsageType.SATURDAY_SEMI_PEAK: 32.1,
                UsageType.OFF_PEAK: 32.1,
            },
        }
    elif contract_type == ContractType.HIGH_PRESSURE_BATCH:
        return {
            SeasonType.SUMMER: {
                UsageType.PEAK: 217.3,
                UsageType.SATURDAY_SEMI_PEAK: 43.4,
                UsageType.OFF_PEAK: 43.4,
            },
            SeasonType.NONSUMMER: {
                UsageType.PEAK: 160.6,
                UsageType.SATURDAY_SEMI_PEAK: 32.1,
                UsageType.OFF_PEAK: 32.1,
            },
        }


def get_charge_price_dict(contract_type):
    if contract_type == ContractType.HIGH_PRESSURE_THREE_PHASE:
        return {
            SeasonType.SUMMER: {
                UsageType.PEAK: 8.69,
                UsageType.SEMI_PEAK: 5.38,
                UsageType.SATURDAY_SEMI_PEAK: 2.5,
                UsageType.OFF_PEAK: 2.4,
            },
            SeasonType.NONSUMMER: {
                UsageType.SEMI_PEAK: 5.03,
                UsageType.SATURDAY_SEMI_PEAK: 2.31,
                UsageType.OFF_PEAK: 2.18,
            },
        }
    elif contract_type == ContractType.HIGH_PRESSURE_BATCH:
        return {
            SeasonType.SUMMER: {
                UsageType.PEAK: 11.44,
                UsageType.SATURDAY_SEMI_PEAK: 3.2,
                UsageType.OFF_PEAK: 2.99,
            },
            SeasonType.NONSUMMER: {
                UsageType.PEAK: 10.8,
                UsageType.SATURDAY_SEMI_PEAK: 2.89,
                UsageType.OFF_PEAK: 2.67,
            },
        }


def get_day_type(pd_timestamp):
    date_obj = pd_timestamp.strftime("%Y%m%d")
    day_type = DayType.WORKDAY
    if date_obj in taiwan_holiday:
        if pd_timestamp.weekday() == 5:
            day_type = DayType.SATURDAY
        else:
            day_type = DayType.HOLIDAY
    return day_type


def get_usage_type_from_dict(datetime, electric_type_dict: dict):
    """
    判斷datetime處於哪種用電類型的函數
    :param datetime: 日期時間
    :param eletric_type_dict: 用電參數
    :return: 用電類型
    """
    result_type = UsageType.OFF_PEAK
    daily_type_dict = electric_type_dict.get(
        SeasonType.SUMMER if is_summer(datetime) else SeasonType.NONSUMMER
    )
    day_type = get_day_type(datetime)
    if day_type == DayType.WORKDAY:
        # verify peak, semi-peak and off peak
        for type, time_list in daily_type_dict.items():
            if type != UsageType.SATURDAY_SEMI_PEAK:
                time_list = pd.to_datetime(time_list, format="%H:%M:%S").time
                date_time = datetime.time()
                for i in range(0, len(time_list), 2):
                    start_time = time_list[i]
                    end_time = time_list[i + 1]
                    if start_time <= date_time <= end_time:
                        result_type = type
                        break    
    elif day_type == DayType.SATURDAY:
        # verify sat-semi-peak
        time_list = daily_type_dict.get(UsageType.SATURDAY_SEMI_PEAK)
        time_list = pd.to_datetime(time_list, format="%H:%M:%S").time
        date_time = datetime.time()
        for i in range(0, len(time_list), 2):
            start_time = time_list[i]
            end_time = time_list[i + 1]
            if start_time <= date_time <= end_time:
                result_type = UsageType.SATURDAY_SEMI_PEAK
                break
    return result_type


if __name__ == "__main__":
    example_date = "2025-01-01 00:00:00"
    print(f"{example_date} is workday = {get_day_type(example_date)}")
    example_date = "2025-04-22 00:00:00"
    print(f"{example_date} is workday = {get_day_type(example_date)}")
    contract_type = ContractType.HIGH_PRESSURE_THREE_PHASE
    season = SeasonType.NONSUMMER
    usage_hours = get_elec_type_dict(contract_type)[season]
    print(f"Usage hours for {contract_type.value} in {season.value}:")
    for usage, hours in usage_hours.items():
        print(f"{usage.value}: {', '.join(hours)}")
