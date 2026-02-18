from sqlalchemy import func
from app.model import Occurrence, Disease, HealthUnit
from app.model.builder import (
    GroupBy,
    Metric,
    DashboardBuilderOutput,
)
from app.model.builder.dashboard_input import DashboardBuilderInput
from app.repository.query.builder import QueryBuilder


class DashboardQueryBuilder:

    def __init__(self, session):
        self.qb = QueryBuilder(session)

    async def build(self, params: DashboardBuilderInput):

        self.qb.apply_filters(params.filters)
        self._apply_group_by(params.group_by)
        self._apply_metric(params.group_by, params.metric)

        rows = await self.qb.execute()

        return [
            DashboardBuilderOutput(label=row.label, value=row.value)
            for row in rows
        ]


    def _apply_group_by(self, gb: GroupBy):

        if gb == GroupBy.DISEASE:
            self.qb.base_join("disease")
            self.qb.group_by(Disease.name)

        elif gb == GroupBy.CITY:
            self.qb.base_join("health_unit")
            self.qb.group_by(HealthUnit.city_code)

        elif gb == GroupBy.HEALTH_UNIT:
            self.qb.base_join("health_unit")
            self.qb.group_by(HealthUnit.name)

        elif gb == GroupBy.EVOLUTION:
            self.qb.group_by(Occurrence.evolution)

        elif gb == GroupBy.SEX:
            self.qb.group_by(Occurrence.patient_sex)

        elif gb == GroupBy.DISTRICT:
            self.qb.base_join("health_unit")
            self.qb.group_by(HealthUnit.district)


    def _apply_metric(self, gb: GroupBy, metric: Metric):

        label_column = self._resolve_label_column(gb)
        value_column = self._resolve_metric_column(metric)

        self.qb.select(
            label_column.label("label"),
            value_column.label("value"),
        )



    def _resolve_label_column(self, group_by):

        if group_by == GroupBy.DISEASE:
            return Disease.name

        elif group_by == GroupBy.CITY:
            return HealthUnit.city_code

        elif group_by == GroupBy.HEALTH_UNIT:
            return HealthUnit.name

        elif group_by == GroupBy.EVOLUTION:
            return Occurrence.evolution

        elif group_by == GroupBy.SEX:
            return Occurrence.patient_sex
        
        elif group_by == GroupBy.DISTRICT:
            return HealthUnit.district


    def _resolve_metric_column(self, metric):

        if metric == Metric.COUNT:
            return func.count(Occurrence.id)

        elif metric == Metric.AVG_AGE:
            return func.avg(Occurrence.patient_age)

        elif metric == Metric.MIN_AGE:
            return func.min(Occurrence.patient_age)

        elif metric == Metric.MAX_AGE:
            return func.max(Occurrence.patient_age)

        
