"""Authentication Data Transfer Objects (DTOs)."""

from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


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


# =============================================================================
# ADMIN USER MANAGEMENT DTOs
# =============================================================================


class UserAdminCreateDTO(BaseModel):
    """Request model for admin user creation."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Literal["admin", "manager", "user", "viewer"] = "user"


class UserAdminUpdateDTO(BaseModel):
    """Request model for admin user update."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[Literal["admin", "manager", "user", "viewer"]] = None
    is_active: Optional[bool] = None


class UserAdminResponseDTO(BaseModel):
    """Response model for admin user management (includes timestamps)."""

    id: UUID
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponseDTO(BaseModel):
    """Paginated list of users."""

    items: List[UserAdminResponseDTO]
    total: int
    page: int
    limit: int
    pages: int


class UserChangePasswordDTO(BaseModel):
    """Request model for admin password change."""

    new_password: str = Field(..., min_length=8)
