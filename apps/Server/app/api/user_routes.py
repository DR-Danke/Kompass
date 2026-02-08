"""User management API routes (admin only)."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.rbac_dependencies import require_roles
from app.models.auth_dto import (
    UserAdminCreateDTO,
    UserAdminResponseDTO,
    UserAdminUpdateDTO,
    UserChangePasswordDTO,
    UserListResponseDTO,
)
from app.services.user_service import user_service

router = APIRouter(tags=["Users"])


@router.get("", response_model=UserListResponseDTO)
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: dict = Depends(require_roles(["admin"])),
) -> UserListResponseDTO:
    """List all users with pagination and filters.

    Args:
        page: Page number
        limit: Items per page
        search: Search by email or name
        role: Filter by role
        is_active: Filter by active status

    Returns:
        Paginated user list
    """
    print(f"INFO [UserRoutes]: Listing users page={page}")
    return user_service.list_users(
        page=page, limit=limit, search=search, role=role, is_active=is_active
    )


@router.get("/{user_id}", response_model=UserAdminResponseDTO)
async def get_user(
    user_id: UUID,
    current_user: dict = Depends(require_roles(["admin"])),
) -> UserAdminResponseDTO:
    """Get a single user by ID.

    Args:
        user_id: UUID of the user

    Returns:
        User details

    Raises:
        HTTPException 404: If user not found
    """
    print(f"INFO [UserRoutes]: Getting user {user_id}")
    result = user_service.get_user(user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return result


@router.post("", response_model=UserAdminResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserAdminCreateDTO,
    current_user: dict = Depends(require_roles(["admin"])),
) -> UserAdminResponseDTO:
    """Create a new user.

    Args:
        data: User creation data (email, password, role, etc.)

    Returns:
        Created user

    Raises:
        HTTPException 400: If creation fails (e.g., duplicate email)
    """
    print(f"INFO [UserRoutes]: Creating user {data.email}")
    result = user_service.create_user(data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user. Email may already exist.",
        )
    return result


@router.put("/{user_id}", response_model=UserAdminResponseDTO)
async def update_user(
    user_id: UUID,
    data: UserAdminUpdateDTO,
    current_user: dict = Depends(require_roles(["admin"])),
) -> UserAdminResponseDTO:
    """Update a user's details.

    Args:
        user_id: UUID of the user to update
        data: Update data (name, role, is_active)

    Returns:
        Updated user

    Raises:
        HTTPException 404: If user not found
        HTTPException 400: If update fails or self-protection triggered
    """
    print(f"INFO [UserRoutes]: Updating user {user_id}")

    existing = user_service.get_user(user_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        result = user_service.update_user(user_id, data, current_user["id"])
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user.",
        )
    return result


@router.put("/{user_id}/password")
async def change_password(
    user_id: UUID,
    data: UserChangePasswordDTO,
    current_user: dict = Depends(require_roles(["admin"])),
) -> dict:
    """Change a user's password.

    Args:
        user_id: UUID of the user
        data: New password

    Returns:
        Success message

    Raises:
        HTTPException 404: If user not found
        HTTPException 400: If password change fails
    """
    print(f"INFO [UserRoutes]: Changing password for user {user_id}")

    existing = user_service.get_user(user_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    success = user_service.change_password(user_id, data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password.",
        )
    return {"message": "Password changed successfully"}


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: dict = Depends(require_roles(["admin"])),
) -> None:
    """Delete a user.

    Args:
        user_id: UUID of the user to delete

    Raises:
        HTTPException 404: If user not found
        HTTPException 400: If self-deletion attempted
        HTTPException 409: If user has FK references
    """
    print(f"INFO [UserRoutes]: Deleting user {user_id}")

    existing = user_service.get_user(user_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    try:
        success = user_service.delete_user(user_id, current_user["id"])
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete user.",
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
