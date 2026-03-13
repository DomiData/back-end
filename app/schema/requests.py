from pydantic import BaseModel, Field


class NaturalSearchRequest(BaseModel):
    query: str = Field(
        min_length=3,
        max_length=200,
        examples=[
            "Search in natural language. Ex: Total number of Zika cases last year"
        ],
    )
