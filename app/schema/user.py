from uuid import UUID
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: UUID
    firebase_uid: str
    is_active: bool

    class Config:
        orm_mode = True
