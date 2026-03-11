"""Repository for outreach_templates table CRUD operations."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from app.config.database import close_database_connection, get_database_connection


class OutreachTemplateRepository:
    """Data access layer for outreach_templates table."""

    def list_templates(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """List all outreach templates ordered by sort_order.

        Args:
            active_only: If True, only return active templates

        Returns:
            List of template dicts
        """
        conn = get_database_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cur:
                query = """
                    SELECT id, key, name, subject, body, is_active, sort_order,
                           created_at, updated_at
                    FROM outreach_templates
                """
                if active_only:
                    query += " WHERE is_active = true"
                query += " ORDER BY sort_order, key"

                cur.execute(query)
                rows = cur.fetchall()

                columns = [
                    "id", "key", "name", "subject", "body", "is_active",
                    "sort_order", "created_at", "updated_at",
                ]
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"ERROR [OutreachTemplateRepository]: Failed to list templates: {e}")
            return []
        finally:
            close_database_connection(conn)

    def get_by_key(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a template by its unique key.

        Args:
            key: Template key (e.g., 'introduction')

        Returns:
            Template dict or None
        """
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, key, name, subject, body, is_active, sort_order,
                           created_at, updated_at
                    FROM outreach_templates
                    WHERE key = %s
                    """,
                    (key,),
                )
                row = cur.fetchone()
                if row:
                    columns = [
                        "id", "key", "name", "subject", "body", "is_active",
                        "sort_order", "created_at", "updated_at",
                    ]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            print(f"ERROR [OutreachTemplateRepository]: Failed to get template by key: {e}")
            return None
        finally:
            close_database_connection(conn)

    def get_by_id(self, template_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a template by UUID.

        Args:
            template_id: Template UUID

        Returns:
            Template dict or None
        """
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, key, name, subject, body, is_active, sort_order,
                           created_at, updated_at
                    FROM outreach_templates
                    WHERE id = %s
                    """,
                    (str(template_id),),
                )
                row = cur.fetchone()
                if row:
                    columns = [
                        "id", "key", "name", "subject", "body", "is_active",
                        "sort_order", "created_at", "updated_at",
                    ]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            print(f"ERROR [OutreachTemplateRepository]: Failed to get template by id: {e}")
            return None
        finally:
            close_database_connection(conn)

    def update(
        self, template_id: UUID, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a template with the provided fields.

        Args:
            template_id: Template UUID
            updates: Dict of field name -> new value (name, subject, body, is_active)

        Returns:
            Updated template dict or None
        """
        allowed_fields = {"name", "subject", "body", "is_active"}
        filtered = {k: v for k, v in updates.items() if k in allowed_fields and v is not None}

        if not filtered:
            return self.get_by_id(template_id)

        conn = get_database_connection()
        if not conn:
            return None

        try:
            set_clauses = []
            values = []
            for field, value in filtered.items():
                set_clauses.append(f"{field} = %s")
                values.append(value)
            values.append(str(template_id))

            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE outreach_templates
                    SET {', '.join(set_clauses)}
                    WHERE id = %s
                    RETURNING id, key, name, subject, body, is_active, sort_order,
                              created_at, updated_at
                    """,
                    values,
                )
                conn.commit()
                row = cur.fetchone()
                if row:
                    columns = [
                        "id", "key", "name", "subject", "body", "is_active",
                        "sort_order", "created_at", "updated_at",
                    ]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            print(f"ERROR [OutreachTemplateRepository]: Failed to update template: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def reset_to_default(
        self, template_id: UUID, default_values: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """Reset a template to its default values.

        Args:
            template_id: Template UUID
            default_values: Dict with default name, subject, body

        Returns:
            Reset template dict or None
        """
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE outreach_templates
                    SET name = %s, subject = %s, body = %s
                    WHERE id = %s
                    RETURNING id, key, name, subject, body, is_active, sort_order,
                              created_at, updated_at
                    """,
                    (
                        default_values["name"],
                        default_values["subject"],
                        default_values["body"],
                        str(template_id),
                    ),
                )
                conn.commit()
                row = cur.fetchone()
                if row:
                    columns = [
                        "id", "key", "name", "subject", "body", "is_active",
                        "sort_order", "created_at", "updated_at",
                    ]
                    return dict(zip(columns, row))
                return None
        except Exception as e:
            print(f"ERROR [OutreachTemplateRepository]: Failed to reset template: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)


# Singleton instance
outreach_template_repository = OutreachTemplateRepository()
