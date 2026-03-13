from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict
from app.model.role import Role
from typing import List


class UserBase(BaseModel):
    email: EmailStr
    firebase_uid: str


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    roles: List[Role]
    model_config = ConfigDict(from_attributes=True)
