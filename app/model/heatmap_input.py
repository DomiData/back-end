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
    disease_acronym: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    patient_sex: Optional[str] = None
    evolution: Optional[str] = None
    unit_type: Optional[str] = None
    city_code: Optional[str] = None

class HeatmapQueryInput(BaseModel):
    filters: HeatmapFilters
    group_by: GroupBy
    metric: Metric = Metric.COUNT
