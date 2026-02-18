from datetime import date
from typing import Optional
from pydantic import BaseModel


class Filters(BaseModel):
    disease_acronym: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    patient_sex: Optional[str] = None
    evolution: Optional[str] = None
    unit_type: Optional[str] = None
    city_code: Optional[str] = None