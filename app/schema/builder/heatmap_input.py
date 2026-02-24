from pydantic import BaseModel
from app.schema.builder.enums import HeatmapGroupBy, HeatmapMetric
from app.schema.builder.filters import Filters


class HeatmapBuilderInput(BaseModel):
    filters: Filters
    group_by: HeatmapGroupBy
    metric: HeatmapMetric = HeatmapMetric.COUNT
