from enum import Enum
from datetime import datetime
import requests


def get_holiday_list(year):
    url = f"https://cdn.jsdelivr.net/gh/ruyut/TaiwanCalendar/data/{year}.json"
    response = requests.get(url)
    response_json = response.json()
    holiday_list = [item['date']
                    for item in response_json if item['isHoliday']]
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


def get_release_hour_dict(contract_type, release_type):
    if contract_type == ContractType.HIGH_PRESSURE_THREE_PHASE:
        if release_type == ReleaseType.AVERAGE:
            return {
                SeasonType.SUMMER: ["16:00:00", "21:00:00"],
                SeasonType.NONSUMMER:
                ["06:00:00", "11:00:00", "14:00:00", "23:59:59"]
            }
        elif release_type == ReleaseType.MAX:
            return {
                SeasonType.SUMMER: ["20:00:00", "22:00:00"],
                SeasonType.NONSUMMER:
                ["09:00:00", "11:00:00", "22:00:00", "23:59:59"]
            }
    elif contract_type == ContractType.HIGH_PRESSURE_BATCH:
        if release_type == ReleaseType.AVERAGE:
            return {
                SeasonType.SUMMER: ["15:30:00", "21:30:00"],
                SeasonType.NONSUMMER: ["15:30:00", "21:30:00"]
            }
        elif release_type == ReleaseType.MAX:
            return {
                SeasonType.SUMMER: ["19:30:00", "21:30:00"],
                SeasonType.NONSUMMER: ["19:30:00", "21:30:00"]
            }


def get_charege_hour_dict(contract_type):
    if contract_type == ContractType.HIGH_PRESSURE_THREE_PHASE:
        return {
            SeasonType.SUMMER: ["00:00:00", "02:00:00"],
            SeasonType.NONSUMMER: ["00:00:00",
                                   "02:00:00", "11:00:00", "13:00:00"]
        }
    elif contract_type == ContractType.HIGH_PRESSURE_BATCH:
        return {
            SeasonType.SUMMER: ["21:30:00", "23:30:00"],
            SeasonType.NONSUMMER: ["21:30:00", "23:30:00"]
        }


def is_summer(date_time):
    if (date_time.month > 5 or
        (date_time.month == 5 and date_time.day >= 16)) and (
            date_time.month < 10 or
            (date_time.month == 10 and date_time.day <= 15)):
        return True
    else:
        return False


def get_elec_type_dict(contract_type):
    if contract_type == ContractType.HIGH_PRESSURE_THREE_PHASE:
        return {
            SeasonType.SUMMER: {
                UsageType.PEAK: ["16:00:00", "22:00:00"],
                UsageType.SEMI_PEAK:
                ["9:00:00", "16:00:00", "22:00:00", "23:59:59"],
                UsageType.SATURDAY_SEMI_PEAK: ["08:00:00", "15:30:00"],
                UsageType.OFF_PEAK: ["00:00:00", "09:00:00"]
            },
            SeasonType.NONSUMMER: {
                UsageType.SEMI_PEAK:
                ["06:00:00", "11:00:00", "14:00:00", "23:59:59"],
                UsageType.SATURDAY_SEMI_PEAK:
                ["06:00:00", "11:00:00", "14:00:00", "23:59:59"],
                UsageType.OFF_PEAK:
                ["00:00:00", "06:00:00", "11:00:00", "14:00:00"]
            }
        }
    elif contract_type == ContractType.HIGH_PRESSURE_BATCH:
        return {
            SeasonType.SUMMER: {
                UsageType.PEAK: ["15:30:00", "21:30:00"],
                UsageType.SATURDAY_SEMI_PEAK: ["15:30:00", "21:30:00"],
                UsageType.OFF_PEAK:
                ["00:00:00", "15:30:00", "21:30:00", "23:59:59"],
            },
            SeasonType.NONSUMMER: {
                UsageType.PEAK: ["15:30:00", "21:30:00"],
                UsageType.SATURDAY_SEMI_PEAK: ["15:30:00", "21:30:00"],
                UsageType.OFF_PEAK:
                ["00:00:00", "15:30:00", "21:30:00", "23:59:59"],
            }
        }


def is_workday(pd_timestamp):
    date_obj = pd_timestamp.strftime("%Y%m%d")
    # 判斷是否為工作日
    return date_obj not in taiwan_holiday


if __name__ == "__main__":
    example_date = "2025-01-01 00:00:00"
    print(f"{example_date} is workday = {is_workday(example_date)}")
    example_date = "2025-04-22 00:00:00"
    print(f"{example_date} is workday = {is_workday(example_date)}")
    contract_type = ContractType.HIGH_PRESSURE_THREE_PHASE
    season = SeasonType.NONSUMMER
    usage_hours = get_elec_type_dict(contract_type)[season]
    print(f"Usage hours for {contract_type.value} in {season.value}:")
    for usage, hours in usage_hours.items():
        print(f"{usage.value}: {', '.join(hours)}")
