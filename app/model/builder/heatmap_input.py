from pydantic import BaseModel
from app.model.builder.enums import GroupBy, Metric, Metric
from app.model.builder.filters import Filters


class HeatmapBuilderInput(BaseModel):
    filters: Filters
    group_by: GroupBy
    metric: Metric = Metric.COUNT