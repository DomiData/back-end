from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from app.core.security import get_firebase_claims
from app.core.database import get_db
from app.repository.occurrence import OccurrenceRepository
from app.services.report import ReportService
from app.services.user import UserService
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


async def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    return ReportService(OccurrenceRepository(db))
