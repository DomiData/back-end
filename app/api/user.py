from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_firebase_claims
from app.services.user import UserService
from app.api.deps import get_current_user
from app.model.user import User
from app.schema.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/sync", status_code=200, response_model=UserResponse)
async def sync_user(
    claims: dict = Depends(get_firebase_claims), db: AsyncSession = Depends(get_db)
):
    try:
        print("trying to sync user")
        if not claims["email"]:
            raise HTTPException(status_code=400, detail="Email is required")

        user_in = UserCreate(firebase_uid=claims["uid"], email=claims["email"])

        return await UserService.sync(db, user_in)
    except Exception as e:
        # Log error
        raise HTTPException(status_code=400, detail="Failed to synchronize user") from e


@router.get("/me", status_code=200, response_model=UserResponse)
async def get_user(user: User = Depends(get_current_user)):
    return user
