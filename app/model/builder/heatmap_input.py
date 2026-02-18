from pydantic import BaseModel
from app.model.builder.enums import HeatmapGroupBy, HeatmapMetric
from app.model.builder.filters import Filters


class HeatmapBuilderInput(BaseModel):
    filters: Filters
    group_by: HeatmapGroupBy
    metric: HeatmapMetric = HeatmapMetric.COUNT