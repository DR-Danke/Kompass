"""User repository for data access."""

from typing import Any, Dict, Optional
from uuid import UUID
from app.config.database import get_database_connection, close_database_connection


class UserRepository:
    """Data access layer for users table."""

    def create_user(
        self,
        email: str,
        password_hash: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: str = "user",
    ) -> Optional[Dict[str, Any]]:
        """Create a new user.

        Args:
            email: User email (stored as lowercase)
            password_hash: Hashed password
            first_name: Optional first name
            last_name: Optional last name
            role: User role (default: 'user')

        Returns:
            User dict if created, None if error
        """
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (email, password_hash, first_name, last_name, role)
                    VALUES (LOWER(%s), %s, %s, %s, %s)
                    RETURNING id, email, password_hash, first_name, last_name, role, is_active
                    """,
                    (email, password_hash, first_name, last_name, role),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "email": row[1],
                        "password_hash": row[2],
                        "first_name": row[3],
                        "last_name": row[4],
                        "role": row[5],
                        "is_active": row[6],
                    }
                return None
        except Exception as e:
            print(f"ERROR [UserRepository]: Failed to create user: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address.

        Args:
            email: User email (case-insensitive)

        Returns:
            User dict if found, None otherwise
        """
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, email, password_hash, first_name, last_name, role, is_active
                    FROM users
                    WHERE email = LOWER(%s)
                    """,
                    (email,),
                )
                row = cur.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "email": row[1],
                        "password_hash": row[2],
                        "first_name": row[3],
                        "last_name": row[4],
                        "role": row[5],
                        "is_active": row[6],
                    }
                return None
        except Exception as e:
            print(f"ERROR [UserRepository]: Failed to get user by email: {e}")
            return None
        finally:
            close_database_connection(conn)

    def get_user_by_id(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get user by UUID.

        Args:
            user_id: User UUID

        Returns:
            User dict if found, None otherwise
        """
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, email, password_hash, first_name, last_name, role, is_active
                    FROM users
                    WHERE id = %s
                    """,
                    (str(user_id),),
                )
                row = cur.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "email": row[1],
                        "password_hash": row[2],
                        "first_name": row[3],
                        "last_name": row[4],
                        "role": row[5],
                        "is_active": row[6],
                    }
                return None
        except Exception as e:
            print(f"ERROR [UserRepository]: Failed to get user by id: {e}")
            return None
        finally:
            close_database_connection(conn)


# Singleton instance
user_repository = UserRepository()
