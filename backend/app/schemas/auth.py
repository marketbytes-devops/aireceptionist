import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr
from backend.app.models.user import UserRole


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: uuid.UUID
    clinic_id: Optional[uuid.UUID] = None
    role: UserRole
    full_name: str
    email: EmailStr


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    clinic_id: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole = UserRole.CLINIC_ADMIN
    clinic_id: Optional[uuid.UUID] = None


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: UserRole
    clinic_id: Optional[uuid.UUID] = None
    is_active: bool

    class Config:
        from_attributes = True

