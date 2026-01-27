from datetime import date
from enum import Enum
from pydantic import BaseModel
from typing import Optional

class GroupBy(str, Enum):
    HEALTH_UNIT = "health_unit"
    DISTRICT = "district"
    CITY = "city"
    DISEASE = "disease"
    DATE = "date"

class Metric(str, Enum):
    COUNT = "count"

class HeatmapFilters(BaseModel):
    disease_acronym: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    min_age: Optional[int]
    max_age: Optional[int]
    patient_sex: Optional[str]
    evolution: Optional[str]
    unit_type: Optional[str]
    city_code: Optional[str]

class HeatmapQueryInput(BaseModel):
    filters: HeatmapFilters
    group_by: GroupBy
    metric: Metric = Metric.COUNT
