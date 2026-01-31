"""Authentication routes."""

from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from app.models.auth_dto import (
    UserRegisterDTO,
    UserLoginDTO,
    TokenResponseDTO,
    UserResponseDTO,
)
from app.services.auth_service import auth_service
from app.repository.user_repository import user_repository
from .dependencies import get_current_user

router = APIRouter(tags=["Authentication"])


@router.post("/register", response_model=TokenResponseDTO, status_code=201)
async def register(data: UserRegisterDTO) -> TokenResponseDTO:
    """Register a new user.

    Args:
        data: User registration data

    Returns:
        TokenResponseDTO with access token and user info

    Raises:
        HTTPException 400: If email already registered
    """
    print(f"INFO [AuthRoutes]: Registration attempt for: {data.email}")

    # Check if email exists
    existing = user_repository.get_user_by_email(data.email)
    if existing:
        print(f"WARN [AuthRoutes]: Email already registered: {data.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    password_hash = auth_service.hash_password(data.password)

    # Create user
    user = user_repository.create_user(
        email=data.email,
        password_hash=password_hash,
        first_name=data.first_name,
        last_name=data.last_name,
    )

    if not user:
        print("ERROR [AuthRoutes]: Failed to create user")
        raise HTTPException(status_code=500, detail="Failed to create user")

    # Generate token
    token = auth_service.create_access_token({"sub": str(user["id"])})

    print(f"INFO [AuthRoutes]: User registered successfully: {data.email}")

    return TokenResponseDTO(
        access_token=token,
        user=UserResponseDTO(
            id=user["id"],
            email=user["email"],
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            role=user["role"],
            is_active=user["is_active"],
        ),
    )


@router.post("/login", response_model=TokenResponseDTO)
async def login(data: UserLoginDTO) -> TokenResponseDTO:
    """Authenticate user and return token.

    Args:
        data: Login credentials

    Returns:
        TokenResponseDTO with access token and user info

    Raises:
        HTTPException 401: If credentials invalid or account inactive
    """
    print(f"INFO [AuthRoutes]: Login attempt for: {data.email}")

    # Get user by email
    user = user_repository.get_user_by_email(data.email)

    if not user:
        print(f"WARN [AuthRoutes]: User not found: {data.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password
    if not auth_service.verify_password(data.password, user["password_hash"]):
        print(f"WARN [AuthRoutes]: Invalid password for: {data.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check if active
    if not user.get("is_active"):
        print(f"WARN [AuthRoutes]: Inactive account: {data.email}")
        raise HTTPException(status_code=401, detail="Account is inactive")

    # Generate token
    token = auth_service.create_access_token({"sub": str(user["id"])})

    print(f"INFO [AuthRoutes]: Login successful for: {data.email}")

    return TokenResponseDTO(
        access_token=token,
        user=UserResponseDTO(
            id=user["id"],
            email=user["email"],
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            role=user["role"],
            is_active=user["is_active"],
        ),
    )


@router.get("/me", response_model=UserResponseDTO)
async def get_me(current_user: dict = Depends(get_current_user)) -> UserResponseDTO:
    """Get current authenticated user.

    Args:
        current_user: Injected by dependency

    Returns:
        UserResponseDTO with current user info
    """
    return UserResponseDTO(
        id=UUID(current_user["id"]),
        email=current_user["email"],
        first_name=current_user.get("first_name"),
        last_name=current_user.get("last_name"),
        role=current_user["role"],
        is_active=current_user["is_active"],
    )
