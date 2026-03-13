from app.model.user import User
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid


class UserRepository:
    @staticmethod
    async def create(session: AsyncSession, new_user: User) -> User:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    @staticmethod
    async def get_by_email(session: AsyncSession, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await session.scalar(stmt)
        return result

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await session.scalar(stmt)
        return result
