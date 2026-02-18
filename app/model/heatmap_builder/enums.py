from enum import Enum


class GroupBy(str, Enum):
    HEALTH_UNIT = "health_unit"
    DISTRICT = "district"
    CITY = "city"


class Metric(str, Enum):
    COUNT = "count"
