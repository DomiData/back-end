from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.base import Base
from app.core.config import settings

engine = create_async_engine(str(settings.DATABASE_URL))
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db():
    async with SessionLocal() as db:
        yield db
