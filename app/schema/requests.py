from pydantic import BaseModel, Field
from datetime import date


class NaturalSearchRequest(BaseModel):
    query: str = Field(
        min_length=3,
        max_length=200,
        examples=[
            "Search in natural language. Ex: Total number of Zika cases last year"
        ],
    )


class CityReportRequest(BaseModel):
    city_code: str = Field(
        min_length=7,
        max_length=7,
        examples=["2507507", "2504009", "2510808"],
    )
    start_date: date = Field(
        examples=["2025-01-01"],
    )
    end_date: date = Field(
        examples=["2025-12-31"],
    )


class DiseaseReportByCityRequest(BaseModel):
    city_code: str = Field(
        min_length=7,
        max_length=7,
        examples=["2507507", "2504009", "2510808"],
    )
    disease_acronym: str = Field(
        min_length=3,
        max_length=100,
        examples=["DENG", "ZIK", "CHIK"],
    )
    start_date: date = Field(
        examples=["2025-01-01"],
    )
    end_date: date = Field(
        examples=["2025-12-31"],
    )


class DiseaseReportByStateRequest(BaseModel):
    state_code: str = Field(
        min_length=2,
        max_length=2,
        examples=["25", "26", "29"],
    )
    disease_acronym: str = Field(
        min_length=3,
        max_length=100,
        examples=["DENG", "ZIK", "CHIK"],
    )
    start_date: date = Field(
        examples=["2025-01-01"],
    )
    end_date: date = Field(
        examples=["2025-12-31"],
    )


class StateReportRequest(BaseModel):
    state_code: str = Field(
        min_length=2,
        max_length=2,
        examples=["25", "26", "29"],
    )
    start_date: date = Field(
        examples=["2025-01-01"],
    )
    end_date: date = Field(
        examples=["2025-12-31"],
    )
