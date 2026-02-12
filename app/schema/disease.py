from pydantic import BaseModel, ConfigDict, Field


class DiseaseBase(BaseModel):
    acronym: str = Field(..., min_length=2, max_length=10, examples=["DENG"])
    name: str = Field(..., min_length=3, max_length=100, examples=["Dengue"])


class DiseaseResponse(DiseaseBase):
    model_config = ConfigDict(from_attributes=True)
