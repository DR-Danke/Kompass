"""User management service for admin operations."""

import math
from typing import Optional
from uuid import UUID

from app.models.auth_dto import (
    UserAdminCreateDTO,
    UserAdminResponseDTO,
    UserAdminUpdateDTO,
    UserChangePasswordDTO,
    UserListResponseDTO,
)
from app.repository.user_repository import user_repository
from app.services.auth_service import auth_service


class UserService:
    """Business logic for admin user management."""

    def list_users(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> UserListResponseDTO:
        """List users with pagination and filters.

        Args:
            page: Page number (1-based)
            limit: Items per page
            search: Search term for email/name
            role: Filter by role
            is_active: Filter by active status

        Returns:
            Paginated user list response
        """
        print(f"INFO [UserService]: Listing users page={page} limit={limit}")
        total = user_repository.count_users(search=search, role=role, is_active=is_active)
        rows = user_repository.list_users(
            page=page, limit=limit, search=search, role=role, is_active=is_active
        )
        items = [UserAdminResponseDTO(**row) for row in rows]
        pages = math.ceil(total / limit) if limit > 0 else 0

        return UserListResponseDTO(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )

    def get_user(self, user_id: UUID) -> Optional[UserAdminResponseDTO]:
        """Get a single user by ID.

        Args:
            user_id: User UUID

        Returns:
            User response or None
        """
        print(f"INFO [UserService]: Getting user {user_id}")
        row = user_repository.get_user_by_id_full(user_id)
        if not row:
            return None
        return UserAdminResponseDTO(**row)

    def create_user(self, data: UserAdminCreateDTO) -> Optional[UserAdminResponseDTO]:
        """Create a new user with admin-specified role.

        Args:
            data: User creation data

        Returns:
            Created user response or None
        """
        print(f"INFO [UserService]: Creating user {data.email} with role {data.role}")

        # Check for existing email
        existing = user_repository.get_user_by_email(data.email)
        if existing:
            print(f"WARN [UserService]: Email already exists: {data.email}")
            return None

        password_hash = auth_service.hash_password(data.password)
        result = user_repository.create_user(
            email=data.email,
            password_hash=password_hash,
            first_name=data.first_name,
            last_name=data.last_name,
            role=data.role,
        )
        if not result:
            return None

        # Fetch the full user with timestamps
        return self.get_user(result["id"])

    def update_user(
        self, user_id: UUID, data: UserAdminUpdateDTO, current_user_id: UUID
    ) -> Optional[UserAdminResponseDTO]:
        """Update user fields.

        Args:
            user_id: User UUID to update
            data: Update data
            current_user_id: ID of the admin performing the update

        Returns:
            Updated user response or None

        Raises:
            ValueError: If admin tries to deactivate themselves
        """
        print(f"INFO [UserService]: Updating user {user_id}")

        # Self-protection: prevent admin from deactivating themselves
        if str(user_id) == str(current_user_id) and data.is_active is False:
            raise ValueError("Cannot deactivate your own account")

        # Self-protection: prevent admin from changing their own role
        if str(user_id) == str(current_user_id) and data.role is not None:
            raise ValueError("Cannot change your own role")

        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            return self.get_user(user_id)

        result = user_repository.update_user(user_id, update_data)
        if not result:
            return None
        return UserAdminResponseDTO(**result)

    def change_password(self, user_id: UUID, data: UserChangePasswordDTO) -> bool:
        """Change a user's password.

        Args:
            user_id: User UUID
            data: New password data

        Returns:
            True if password changed
        """
        print(f"INFO [UserService]: Changing password for user {user_id}")
        password_hash = auth_service.hash_password(data.new_password)
        return user_repository.update_password(user_id, password_hash)

    def delete_user(self, user_id: UUID, current_user_id: UUID) -> bool:
        """Delete a user.

        Args:
            user_id: User UUID to delete
            current_user_id: ID of the admin performing the delete

        Returns:
            True if deleted

        Raises:
            ValueError: If admin tries to delete themselves or FK constraint fails
        """
        print(f"INFO [UserService]: Deleting user {user_id}")

        if str(user_id) == str(current_user_id):
            raise ValueError("Cannot delete your own account")

        try:
            return user_repository.delete_user(user_id)
        except Exception as e:
            error_msg = str(e).lower()
            if "foreign key" in error_msg or "violates" in error_msg:
                raise ValueError(
                    "Cannot delete user because they have associated records. "
                    "Consider deactivating them instead."
                ) from e
            raise


# Singleton instance
user_service = UserService()
