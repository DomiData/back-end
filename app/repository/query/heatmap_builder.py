from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.model import Occurrence, HealthUnit
from app.model.builder import (
    HeatmapGroupBy as GroupBy,
    HeatmapMetric as Metric,
    HeatmapBuilderOutput,
)
from app.model.builder.heatmap_input import HeatmapBuilderInput
from app.repository.query.builder import QueryBuilder


class HeatMapQueryBuilder:


    def __init__(self, session: AsyncSession):
        self.qb = QueryBuilder(session)


    async def build(self, params: HeatmapBuilderInput):

        self.qb.apply_filters(params.filters)
        self._apply_group_by(params.group_by)
        self._apply_metric(params.metric)

        rows = await self.qb.execute()

        return [
            HeatmapBuilderOutput(lat=row.lat, lng=row.lng, value=row.value)
            for row in rows
        ]


    def _apply_group_by(self, gb: GroupBy):

        if gb == GroupBy.HEALTH_UNIT:
            self.qb.join("health_unit")
            self.qb.group_by(
                HealthUnit.cnes_code,
                HealthUnit.latitude,
                HealthUnit.longitude,
            )

        elif gb == GroupBy.DISTRICT:
            self.qb.join("health_unit")
            self.qb.group_by(
                HealthUnit.district,
                HealthUnit.latitude,
                HealthUnit.longitude,
            )

        elif gb == GroupBy.CITY:
            self.qb.join("health_unit")
            self.qb.group_by(
                HealthUnit.city_code,
                HealthUnit.latitude,
                HealthUnit.longitude,
            )


    def _apply_metric(self, metric: Metric):
        if metric != Metric.COUNT:
            return

        self.qb.join("health_unit")

        self.qb.select(
            HealthUnit.latitude.label("lat"),
            HealthUnit.longitude.label("lng"),
            func.count(Occurrence.id).label("value"),
        )
