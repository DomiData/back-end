from typing import List
from pydantic import BaseModel
from app.schema.builder.enums import DashboardGroupBy, DashboardMetric
from app.schema.builder.filters import Filters


class DashboardBuilderInput(BaseModel):
    filters: Filters
    group_by: DashboardGroupBy
    metrics: List[DashboardMetric]
 