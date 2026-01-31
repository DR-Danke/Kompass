"""Authentication service for password hashing and JWT operations."""

from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
from jose import JWTError, jwt
from app.config import get_settings


class AuthService:
    """Handles password hashing and JWT token operations."""

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Stored password hash

        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )

    def create_access_token(self, data: dict) -> str:
        """Create a JWT access token.

        Args:
            data: Token payload data (should include 'sub' = user_id)

        Returns:
            Encoded JWT token string
        """
        settings = get_settings()

        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})

        return jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    def decode_access_token(self, token: str) -> Optional[dict]:
        """Decode and validate a JWT access token.

        Args:
            token: JWT token string

        Returns:
            Token payload dict if valid, None if invalid or expired
        """
        settings = get_settings()

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except JWTError as e:
            print(f"WARN [AuthService]: Token decode failed: {e}")
            return None


# Singleton instance
auth_service = AuthService()
