from enum import Enum


class CaseInsensitiveEnum(str, Enum):
    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return None


class HeatmapGroupBy(CaseInsensitiveEnum):
    HEALTH_UNIT = "health_unit"
    DISTRICT = "district"
    CITY = "city"


class HeatmapMetric(CaseInsensitiveEnum):
    COUNT = "count"


class DashboardGroupBy(CaseInsensitiveEnum):
    DISEASE = "disease"
    CITY = "city"
    HEALTH_UNIT = "health_unit"
    EVOLUTION = "evolution"
    SEX = "sex"
    DISTRICT = "district"


class DashboardMetric(CaseInsensitiveEnum):
    COUNT = "count"
    AVG_AGE = "avg_age"
    MIN_AGE = "min_age"
    MAX_AGE = "max_age"
    RECOVERY_RATE = "recovery_rate"
    FATALITY_RATE = "fatality_rate"
