from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, select, func
from app.model import Occurrence, Disease, HealthUnit
from app.model.heatmap_builder import (
    GroupBy,
    HeatmapQueryBuilderInput,
    Metric,
    HeatmapBuilderOutput,
)


class HeatMapQueryBuilder:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.stmt: Select[Any] = select(Occurrence)
        self._joined: set[str] = set()

    async def build(self, params: HeatmapQueryBuilderInput):
        self._apply_filters(params)
        self._apply_group_by(params)
        self._apply_metric(params)

        result = await self.session.execute(self.stmt)
        rows = result.all()

        return [
            HeatmapBuilderOutput(lat=row.lat, lng=row.lng, value=row.value)
            for row in rows
        ]

    def _join_disease(self):
        if "disease" not in self._joined:
            self.stmt = self.stmt.join(Disease)
            self._joined.add("disease")

    def _join_health_unit(self):
        if "health_unit" not in self._joined:
            self.stmt = self.stmt.join(HealthUnit)
            self._joined.add("health_unit")

    def _apply_filters(self, params: HeatmapQueryBuilderInput):
        f = params.filters

        if f.disease_acronym:
            self._join_disease()
            self.stmt = self.stmt.where(Disease.acronym == f.disease_acronym)

        if f.start_date:
            self.stmt = self.stmt.where(Occurrence.notification_date >= f.start_date)

        if f.end_date:
            self.stmt = self.stmt.where(Occurrence.notification_date <= f.end_date)

        if f.min_age is not None:
            self.stmt = self.stmt.where(Occurrence.patient_age >= f.min_age)

        if f.max_age is not None:
            self.stmt = self.stmt.where(Occurrence.patient_age <= f.max_age)

        if f.patient_sex:
            self.stmt = self.stmt.where(Occurrence.patient_sex == f.patient_sex)

        if f.evolution:
            self.stmt = self.stmt.where(Occurrence.evolution == f.evolution)

        if f.unit_type:
            self._join_health_unit()
            self.stmt = self.stmt.where(HealthUnit.unit_type == f.unit_type)

        if f.city_code:
            self._join_health_unit()
            self.stmt = self.stmt.where(HealthUnit.city_code == f.city_code)

    def _apply_group_by(self, params: HeatmapQueryBuilderInput):
        gb = params.group_by

        if gb == GroupBy.HEALTH_UNIT:
            self._join_health_unit()
            self.stmt = self.stmt.group_by(
                HealthUnit.cnes_code,
                HealthUnit.latitude,
                HealthUnit.longitude,
            )

        elif gb == GroupBy.DISTRICT:
            self._join_health_unit()
            self.stmt = self.stmt.group_by(
                HealthUnit.district,
                HealthUnit.latitude,
                HealthUnit.longitude,
            )

        elif gb == GroupBy.CITY:
            self._join_health_unit()
            self.stmt = self.stmt.group_by(
                HealthUnit.city_code,
                HealthUnit.latitude,
                HealthUnit.longitude,
            )

    def _apply_metric(self, params: HeatmapQueryBuilderInput):
        if params.metric != Metric.COUNT:
            return

        self._join_health_unit()

        self.stmt = self.stmt.with_only_columns(
            HealthUnit.latitude.label("lat"),
            HealthUnit.longitude.label("lng"),
            func.count(Occurrence.id).label("value"),
        )
