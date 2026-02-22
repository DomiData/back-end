from sqlalchemy import func
from app.model import Occurrence, Disease, HealthUnit
from app.schema.builder import (
    DashboardGroupBy as GroupBy,
    DashboardMetric as Metric,
)
from app.schema.builder.dashboard_input import DashboardBuilderInput
from app.repository.query.builder import QueryBuilder
from typing import List


class DashboardQueryBuilder:

    def __init__(self, session):
        self.qb = QueryBuilder(session)
        self.all_columns = []

    async def build(self, params: DashboardBuilderInput):

        self.qb.apply_filters(params.filters)
        self._apply_group_by(params.group_by)
        self._apply_metric(params.group_by, params.metrics)

        rows = await self.qb.execute()
        result = []

        for row in rows:
            row_dict = {}
            for item in self.all_columns:
                row_dict[item] = getattr(row, item)
            result.append(row_dict)

        return result


    def _apply_group_by(self, gb: List[GroupBy]):

        if GroupBy.DISEASE in gb:
            self.qb.base_join("disease")
            self.qb.group_by(Disease.name)

        if GroupBy.CITY in gb:
            self.qb.base_join("health_unit")
            self.qb.group_by(HealthUnit.city_code)

        if GroupBy.HEALTH_UNIT in gb:
            self.qb.base_join("health_unit")
            self.qb.group_by(HealthUnit.name)

        if GroupBy.EVOLUTION in gb:
            self.qb.group_by(Occurrence.evolution)

        if GroupBy.SEX in gb:
            self.qb.group_by(Occurrence.patient_sex)

        if GroupBy.DISTRICT in gb:
            self.qb.base_join("health_unit")
            self.qb.group_by(HealthUnit.district)


    def _apply_metric(self, gb: List[GroupBy], metrics: List[Metric]):
        
        label_columns = self._resolve_label_column(gb)
        value_columns = self._resolve_metric_column(metrics)

        self.all_columns = [col.key for col in (label_columns + value_columns)]

        self.qb.select(
           *label_columns,
           *value_columns
        )



    def _resolve_label_column(self, group_by: List[GroupBy]):

        columns = []

        if GroupBy.DISEASE in group_by:
            columns.append(Disease.name.label("disease_name"))

        if GroupBy.CITY in group_by:
            columns.append(HealthUnit.city_code.label("city_code"))

        if GroupBy.HEALTH_UNIT in group_by:
            columns.append(HealthUnit.name.label("health_unit_name"))

        if GroupBy.EVOLUTION in group_by:
            columns.append(Occurrence.evolution.label("evolution"))

        if GroupBy.SEX in group_by:
            columns.append(Occurrence.patient_sex.label("patient_sex"))
        
        if GroupBy.DISTRICT in group_by:
            columns.append(HealthUnit.district.label("district"))

        return columns

    def _resolve_metric_column(self, metric: List[Metric]):

        columns = []

        if Metric.COUNT in metric:
            columns.append(func.count(Occurrence.id).label("count"))

        if Metric.AVG_AGE in metric:
            columns.append(func.avg(Occurrence.patient_age).label("avg_age"))

        if Metric.MIN_AGE in metric:
            columns.append(func.min(Occurrence.patient_age).label("min_age"))

        if Metric.MAX_AGE in metric:
            columns.append(func.max(Occurrence.patient_age).label("max_age"))

        
        return columns