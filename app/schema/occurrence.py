from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class OccurrenceBase(BaseModel):
    disease_type: str
    health_unit_id: str
    notification_date: date
    patient_age: Optional[int] = None
    patient_sex: Optional[str] = Field(None, max_length=1, pattern="^[MF]$")
    evolution: Optional[str] = None


class OccurrenceCreate(OccurrenceBase):
    pass


class OccurrenceResponse(OccurrenceBase):
    id: int

    class Config:
        from_attributes = True
