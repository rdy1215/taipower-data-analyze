from enum import Enum
import pandas as pd


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


if __name__ == "__main__":
    contract_type = ContractType.HIGH_PRESSURE_THREE_PHASE
    season = SeasonType.NONSUMMER
    usage_hours = get_elec_type_dict(contract_type)[season]
    print(f"Usage hours for {contract_type.value} in {season.value}:")
    for usage, hours in usage_hours.items():
        print(f"{usage.value}: {', '.join(hours)}")
