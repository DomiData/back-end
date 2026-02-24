from typing import List
from pydantic import BaseModel
from app.schema.builder.enums import DashboardGroupBy, DashboardMetric
from app.schema.builder.filters import Filters


class DashboardBuilderInput(BaseModel):
    filters: Filters
    group_by: List[DashboardGroupBy]
    metrics: List[DashboardMetric]
