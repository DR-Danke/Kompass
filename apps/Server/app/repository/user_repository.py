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

    def get_user_by_id_full(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Get user by UUID including timestamps.

        Args:
            user_id: User UUID

        Returns:
            User dict with timestamps if found, None otherwise
        """
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, email, first_name, last_name, role, is_active,
                           created_at, updated_at
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
                        "first_name": row[2],
                        "last_name": row[3],
                        "role": row[4],
                        "is_active": row[5],
                        "created_at": row[6],
                        "updated_at": row[7],
                    }
                return None
        except Exception as e:
            print(f"ERROR [UserRepository]: Failed to get user by id (full): {e}")
            return None
        finally:
            close_database_connection(conn)

    def list_users(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> list:
        """List users with pagination and optional filters.

        Args:
            page: Page number (1-based)
            limit: Items per page
            search: Search term for email/name
            role: Filter by role
            is_active: Filter by active status

        Returns:
            List of user dicts
        """
        conn = get_database_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cur:
                conditions = []
                params: list = []

                if search:
                    conditions.append(
                        "(email ILIKE %s OR first_name ILIKE %s OR last_name ILIKE %s)"
                    )
                    search_param = f"%{search}%"
                    params.extend([search_param, search_param, search_param])

                if role:
                    conditions.append("role = %s")
                    params.append(role)

                if is_active is not None:
                    conditions.append("is_active = %s")
                    params.append(is_active)

                where_clause = ""
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)

                offset = (page - 1) * limit
                params.extend([limit, offset])

                cur.execute(
                    f"""
                    SELECT id, email, first_name, last_name, role, is_active,
                           created_at, updated_at
                    FROM users
                    {where_clause}
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    params,
                )
                rows = cur.fetchall()

                return [
                    {
                        "id": row[0],
                        "email": row[1],
                        "first_name": row[2],
                        "last_name": row[3],
                        "role": row[4],
                        "is_active": row[5],
                        "created_at": row[6],
                        "updated_at": row[7],
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"ERROR [UserRepository]: Failed to list users: {e}")
            return []
        finally:
            close_database_connection(conn)

    def count_users(
        self,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        """Count users with optional filters.

        Args:
            search: Search term for email/name
            role: Filter by role
            is_active: Filter by active status

        Returns:
            Total count of matching users
        """
        conn = get_database_connection()
        if not conn:
            return 0

        try:
            with conn.cursor() as cur:
                conditions = []
                params: list = []

                if search:
                    conditions.append(
                        "(email ILIKE %s OR first_name ILIKE %s OR last_name ILIKE %s)"
                    )
                    search_param = f"%{search}%"
                    params.extend([search_param, search_param, search_param])

                if role:
                    conditions.append("role = %s")
                    params.append(role)

                if is_active is not None:
                    conditions.append("is_active = %s")
                    params.append(is_active)

                where_clause = ""
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)

                cur.execute(
                    f"""
                    SELECT COUNT(*) FROM users {where_clause}
                    """,
                    params or None,
                )
                row = cur.fetchone()
                return row[0] if row else 0
        except Exception as e:
            print(f"ERROR [UserRepository]: Failed to count users: {e}")
            return 0
        finally:
            close_database_connection(conn)

    def update_user(self, user_id: UUID, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user fields.

        Args:
            user_id: User UUID
            data: Dict of fields to update (first_name, last_name, role, is_active)

        Returns:
            Updated user dict or None if failed
        """
        conn = get_database_connection()
        if not conn:
            return None

        try:
            set_parts = []
            params: list = []
            for key, value in data.items():
                if key in ("first_name", "last_name", "role", "is_active"):
                    set_parts.append(f"{key} = %s")
                    params.append(value)

            if not set_parts:
                return self.get_user_by_id_full(user_id)

            set_parts.append("updated_at = NOW()")
            params.append(str(user_id))

            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE users
                    SET {', '.join(set_parts)}
                    WHERE id = %s
                    RETURNING id, email, first_name, last_name, role, is_active,
                              created_at, updated_at
                    """,
                    params,
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "email": row[1],
                        "first_name": row[2],
                        "last_name": row[3],
                        "role": row[4],
                        "is_active": row[5],
                        "created_at": row[6],
                        "updated_at": row[7],
                    }
                return None
        except Exception as e:
            print(f"ERROR [UserRepository]: Failed to update user: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def update_password(self, user_id: UUID, password_hash: str) -> bool:
        """Update user password hash.

        Args:
            user_id: User UUID
            password_hash: New bcrypt hash

        Returns:
            True if updated, False otherwise
        """
        conn = get_database_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE users
                    SET password_hash = %s, updated_at = NOW()
                    WHERE id = %s
                    """,
                    (password_hash, str(user_id)),
                )
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            print(f"ERROR [UserRepository]: Failed to update password: {e}")
            conn.rollback()
            return False
        finally:
            close_database_connection(conn)

    def delete_user(self, user_id: UUID) -> bool:
        """Delete a user (hard delete).

        Args:
            user_id: User UUID

        Returns:
            True if deleted, False otherwise

        Raises:
            Exception: If FK constraints prevent deletion
        """
        conn = get_database_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM users WHERE id = %s",
                    (str(user_id),),
                )
                conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            print(f"ERROR [UserRepository]: Failed to delete user: {e}")
            conn.rollback()
            raise
        finally:
            close_database_connection(conn)


# Singleton instance
user_repository = UserRepository()
