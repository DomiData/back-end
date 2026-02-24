from datetime import date
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.health_unit import HealthUnit
from app.model.occurrence import Occurrence


class OccurrenceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_city_report(self, city_code: str, start_date: date, end_date: date):
        stmt = (
            select(
                HealthUnit.name,
                Occurrence.disease_type,
                func.count(Occurrence.id).label("total"),
            )
            .join(HealthUnit, Occurrence.health_unit_id == HealthUnit.cnes_code)
            .where(Occurrence.city_id == city_code)
            .where(Occurrence.notification_date.between(start_date, end_date))
            .group_by(HealthUnit.name, Occurrence.disease_type)
        )

        result = await self.db.execute(stmt)
        return result.all()

    async def get_disease_report_by_city(
        self, city_code: str, disease: str, start_date: date, end_date: date
    ):
        stmt = (
            select(HealthUnit.name, func.count(Occurrence.id).label("total"))
            .join(HealthUnit, Occurrence.health_unit_id == HealthUnit.cnes_code)
            .where(Occurrence.city_id == city_code)
            .where(Occurrence.disease_type == disease)
            .where(Occurrence.notification_date.between(start_date, end_date))
            .group_by(HealthUnit.name)
        )

        result = await self.db.execute(stmt)
        return result.all()

    async def get_disease_report_by_state(
        self, state_code: str, disease: str, start_date: date, end_date: date
    ):
        stmt = (
            select(Occurrence.city_id, func.count(Occurrence.id).label("total"))
            .where(Occurrence.city_id.startswith(state_code))
            .where(Occurrence.disease_type == disease)
            .where(Occurrence.notification_date.between(start_date, end_date))
            .group_by(Occurrence.city_id)
        )

        result = await self.db.execute(stmt)
        return result.all()

    async def get_state_report(self, state_code: str, start_date: date, end_date: date):
        stmt = (
            select(
                Occurrence.city_id,
                Occurrence.disease_type,
                func.count(Occurrence.id).label("total"),
            )
            .where(Occurrence.city_id.startswith(state_code))
            .where(Occurrence.notification_date.between(start_date, end_date))
            .group_by(Occurrence.city_id, Occurrence.disease_type)
        )

        result = await self.db.execute(stmt)
        return result.all()
