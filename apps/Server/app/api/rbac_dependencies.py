"""Role-Based Access Control (RBAC) Dependencies."""

from typing import Any, Callable, Dict, List
from fastapi import Depends, HTTPException
from .dependencies import get_current_user


def require_roles(allowed_roles: List[str]) -> Callable:
    """Create a dependency that checks if user has one of the allowed roles.

    Args:
        allowed_roles: List of roles that are allowed access

    Returns:
        Dependency function that validates user role

    Example:
        @router.delete("/items/{id}")
        async def delete_item(
            current_user: dict = Depends(require_roles(['admin', 'manager']))
        ):
            pass
    """

    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user),
    ) -> Dict[str, Any]:
        user_role = current_user.get("role")

        if user_role not in allowed_roles:
            print(f"WARN [RBAC]: Access denied for role '{user_role}'. Required: {allowed_roles}")
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}",
            )

        return current_user

    return role_checker
