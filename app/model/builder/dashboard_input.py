from typing import List
from pydantic import BaseModel
from app.model.builder.enums import DashboardGroupBy, DashboardMetric
from app.model.builder.filters import Filters


class DashboardBuilderInput(BaseModel):
    filters: Filters
    group_by: DashboardGroupBy
    metrics: List[DashboardMetric]
 