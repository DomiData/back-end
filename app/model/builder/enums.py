from enum import Enum


class HeatmapGroupBy(str, Enum):
    HEALTH_UNIT = "health_unit"
    DISTRICT = "district"
    CITY = "city"


class HeatmapMetric(str, Enum):
    COUNT = "count"


class DashboardGroupBy(str, Enum):
    DISEASE = "disease"
    CITY = "city"
    HEALTH_UNIT = "health_unit"
    EVOLUTION = "evolution"
    SEX = "sex"
    DISTRICT = "district"


class DashboardMetric(str, Enum):
    COUNT = "count"
    AVG_AGE = "avg_age"
    MIN_AGE = "min_age"
    MAX_AGE = "max_age"
