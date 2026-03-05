from decimal import Decimal
from pydantic import BaseModel


class HeatmapBuilderOutput(BaseModel):
    lat: Decimal
    lng: Decimal
    value: int
