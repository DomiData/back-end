from typing import List
from pydantic import BaseModel
from app.model.builder.enums import GroupBy, Metric
from app.model.builder.filters import Filters


class DashboardBuilderInput(BaseModel):
    filters: Filters
    group_by: GroupBy
    metrics: List[Metric]
 