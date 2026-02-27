from typing import Literal
from pydantic import BaseModel
from app.schema.builder.dashboard_input import DashboardBuilderInput
from app.schema.builder.heatmap_input import HeatmapBuilderInput


class ExportBase(BaseModel):
    file_name: str
    export_format: Literal["csv", "xlsx"]


class ExportDashboardData(ExportBase):
    dashboard_input: DashboardBuilderInput


class ExportHeatmapData(ExportBase):
    heatmap_input: HeatmapBuilderInput
