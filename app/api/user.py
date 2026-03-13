from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_firebase_claims
from app.services.user import UserService
from app.api.deps import get_current_user
from app.model.user import User
from app.schema.user import UserCreate, UserResponse
from app.utils.logger import logger

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/sync", status_code=200, response_model=UserResponse)
async def sync_user(
    claims: dict = Depends(get_firebase_claims), db: AsyncSession = Depends(get_db)
):
    try:
        if not claims["email"]:
            raise HTTPException(status_code=400, detail="Email is required")
        user = await UserService.sync(
            db, UserCreate(firebase_uid=claims["uid"], email=claims["email"])
        )
        return UserResponse.model_validate(user)
    except Exception as e:
        logger.error("Failed to synchronize user: %s", e)
        raise HTTPException(status_code=400, detail="Failed to synchronize user") from e


@router.get("/me", status_code=200, response_model=UserResponse)
async def get_user(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)
