from sqlalchemy.ext.asyncio import AsyncSession
from app.schema.user import UserCreate, UserResponse
from app.model.user import User
from app.repository.user import UserRepository

class UserService:

    @staticmethod
    async def sync(db: AsyncSession, dto: UserCreate) -> User:
        user = await UserRepository.get_by_email(session=db, email=dto.email)

        if not user:
            new_user = User(email=dto.email, firebase_uid=dto.firebase_uid)
            user = await UserRepository.create(session=db, new_user=new_user)

        return user

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> UserResponse:
        user = await UserRepository.get_by_email(session=db, email=email)
        if not user:
            raise Exception("user not found")
        return UserResponse.model_validate(user)
