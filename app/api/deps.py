from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from app.core.security import get_firebase_claims
from app.core.database import get_db
from app.services.user import UserService
from app.services.export.export import ExportService
from app.repository.query.dashboard_builder import DashboardQueryBuilder
from app.repository.query.heatmap_builder import HeatMapQueryBuilder
from app.repository.reference import ReferenceRepository
from app.model.user import User


async def get_current_user(
    claims: dict = Depends(get_firebase_claims), db: AsyncSession = Depends(get_db)
) -> User:
    email = claims.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    user = await UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


def get_export_service(
    session: AsyncSession = Depends(get_db),
) -> ExportService:

    dashboard_builder = DashboardQueryBuilder(session)
    heatmap_builder = HeatMapQueryBuilder(session)
    reference_repo = ReferenceRepository(session)

    return ExportService(
        session=session,
        dashboard_builder=dashboard_builder,
        heatmap_builder=heatmap_builder,
        reference_repo=reference_repo,
    )
