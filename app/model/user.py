from app.core.database import Base
from datetime import datetime
from sqlalchemy import String, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column
import uuid

class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
    primary_key=True,
    default=uuid.uuid4
    )
    firebase_uid: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)