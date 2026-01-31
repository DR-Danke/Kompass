"""API Dependencies for authentication."""

from typing import Any, Dict
from uuid import UUID
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import auth_service
from app.repository.user_repository import user_repository

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """Validate JWT token and return current user.

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        User dict with id, email, role, is_active, etc.

    Raises:
        HTTPException 401: If token invalid or user not found
    """
    token = credentials.credentials

    # Decode token
    payload = auth_service.decode_access_token(token)

    if not payload:
        print("WARN [Dependencies]: Invalid or expired token")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Get user ID from token
    user_id = payload.get("sub")
    if not user_id:
        print("WARN [Dependencies]: Token missing user ID")
        raise HTTPException(status_code=401, detail="Invalid token")

    # Get user from database
    try:
        user = user_repository.get_user_by_id(UUID(user_id))
    except ValueError:
        print(f"WARN [Dependencies]: Invalid user ID format: {user_id}")
        raise HTTPException(status_code=401, detail="Invalid token")

    if not user:
        print(f"WARN [Dependencies]: User not found: {user_id}")
        raise HTTPException(status_code=401, detail="User not found")

    if not user.get("is_active"):
        print(f"WARN [Dependencies]: Inactive user: {user_id}")
        raise HTTPException(status_code=401, detail="User is inactive")

    return {
        "id": str(user["id"]),
        "email": user["email"],
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "role": user["role"],
        "is_active": user["is_active"],
    }
