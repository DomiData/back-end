from pydantic import BaseModel, Field


class DiseaseBase(BaseModel):
    acronym: str = Field(..., min_length=2, max_length=10, example="DENG")
    name: str = Field(..., min_length=3, max_length=100, example="Dengue")


class DiseaseResponse(DiseaseBase):
    class Config:
        from_attributes = True
