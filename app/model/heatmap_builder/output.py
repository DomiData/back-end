from pydantic import BaseModel


class HeatmapBuilderOutput(BaseModel):
    lat: float
    lng: float
    value: int 