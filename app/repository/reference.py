from decimal import Decimal

from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from app.model.health_unit import HealthUnit


class ReferenceRepository:
    def __init__(self, session: AsyncSession):

        self.session = session

    async def get_health_units_by_coordinates(
        self, coordinates: list[tuple[Decimal, Decimal]]
    ):
        if not coordinates:
            return []

        stmt = select(HealthUnit.latitude, HealthUnit.longitude, HealthUnit.name).where(
            tuple_(HealthUnit.latitude, HealthUnit.longitude).in_(coordinates)
        )

        result = await self.session.execute(stmt)
        return result.all()
