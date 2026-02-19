from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schema.builder.filters import Filters
from app.model.disease import Disease
from app.model.health_unit import HealthUnit
from app.model.occurrence import Occurrence


class QueryBuilder:

    JOINS = {
        "disease": Disease,
        "health_unit": HealthUnit,
    }


    def __init__(self, session: AsyncSession):
        self.session = session
        self.stmt = select(Occurrence)
        self._joined = set()


    async def execute(self):
        result = await self.session.execute(self.stmt)
        return result.all()
    
    
    def select(self, *columns):
        self.stmt = self.stmt.with_only_columns(*columns)


    def base_join(self, key):
        if key not in self._joined:
            model = self.JOINS[key]
            self.stmt = self.stmt.join(model)
            self._joined.add(key)


    def where(self, condition):
        self.stmt = self.stmt.where(condition)


    def group_by(self, *columns):
        self.stmt = self.stmt.group_by(*columns)

    
    def apply_filters(self, f: Filters):

        if f.disease_acronym:
            self.base_join("disease")
            self.where(Disease.acronym == f.disease_acronym)

        if f.start_date:
            self.where(Occurrence.notification_date >= f.start_date)

        if f.end_date:
            self.where(Occurrence.notification_date <= f.end_date)

        if f.min_age is not None:
            self.where(Occurrence.patient_age >= f.min_age)

        if f.max_age is not None:
            self.where(Occurrence.patient_age <= f.max_age)

        if f.patient_sex:
            self.where(Occurrence.patient_sex == f.patient_sex)

        if f.evolution:
            self.where(Occurrence.evolution == f.evolution)

        if f.unit_type:
            self.base_join("health_unit")
            self.where(HealthUnit.unit_type == f.unit_type)

        if f.city_code:
            self.base_join("health_unit")
            self.where(HealthUnit.city_code == f.city_code)

