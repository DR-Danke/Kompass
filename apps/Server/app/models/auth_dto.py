"""Authentication Data Transfer Objects (DTOs)."""

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserRegisterDTO(BaseModel):
    """Request model for user registration."""

    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserLoginDTO(BaseModel):
    """Request model for user login."""

    email: EmailStr
    password: str


class UserResponseDTO(BaseModel):
    """Response model for user information."""

    id: UUID
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class TokenResponseDTO(BaseModel):
    """Response model for authentication success."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponseDTO
