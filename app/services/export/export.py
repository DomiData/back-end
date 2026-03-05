from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.repository.query.dashboard_builder import DashboardQueryBuilder
from app.repository.query.heatmap_builder import (
    HeatMapQueryBuilder,
    HeatmapBuilderOutput,
)
from app.repository.reference import ReferenceRepository
from app.schema.export import ExportDashboardData, ExportHeatmapData
from app.services.export.export_context import ExportContext


class ExportService:
    def __init__(
        self,
        session: AsyncSession,
        reference_repo: ReferenceRepository,
        dashboard_builder: DashboardQueryBuilder,
        heatmap_builder: HeatMapQueryBuilder,
    ):
        self.session = session
        self.reference_repo = reference_repo
        self.dashboard_builder = dashboard_builder
        self.heatmap_builder = heatmap_builder

    async def export_dashboard(self, dto: ExportDashboardData):
        raw_data = await self.dashboard_builder.build(dto.dashboard_input)
        data = await self.normalize_dashboard_output_data(raw_data=raw_data)
        return await ExportContext.execute(export_format=dto.export_format, data=data)

    async def export_heatmap_data(self, dto: ExportHeatmapData):
        raw_data = await self.heatmap_builder.build(dto.heatmap_input)
        data = await self.normalize_heatmap_output_data(raw_data)
        return await ExportContext.execute(export_format=dto.export_format, data=data)

    async def normalize_heatmap_output_data(
        self, heatmap_points: List[HeatmapBuilderOutput]
    ) -> List[dict]:
        coords = [(unity.lat, unity.lng) for unity in heatmap_points]
        db_units = await self.reference_repo.get_health_units_by_coordinates(
            coordinates=coords
        )
        unit_map = {(row.latitude, row.longitude): row.name for row in db_units}

        normalized_data = []
        for point in heatmap_points:
            name = unit_map.get((point.lat, point.lng), "Unidade desconhecida")
            normalized_data.append({"unidade": name, "casos": point.value})
        return normalized_data

    async def normalize_dashboard_output_data(self, raw_data: List[dict]) -> List[dict]:
        key_mapping = {
            "disease_name": "doença",
            "count": "casos",
            "avg_age": "idade média",
            "min_age": "menor idade registrada",
            "max_age": "maior idade registrada",
            "recovery_rate": "taxa de recuperação",
            "evolution_not_registered": "evolução não registrada",
            "fatality_rate": "taxa de fatalidade",
        }

        normalized_data = []
        for metric in raw_data:
            normalized_metric = {}

            for key, value in metric.items():
                new_key = key_mapping.get(key, key)

                if isinstance(value, Decimal):
                    normalized_metric[new_key] = round(float(value), 2)
                else:
                    normalized_metric[new_key] = value

            normalized_data.append(normalized_metric)

        return normalized_data
