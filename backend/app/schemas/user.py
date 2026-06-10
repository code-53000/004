from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    full_name: str
    role: str
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class User(UserBase):
    id: int
    is_active: bool
    password_hash: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


Token.update_forward_refs()
