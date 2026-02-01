"""Kompass Portfolio & Quotation System repositories for data access."""

import math
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from app.config.database import close_database_connection, get_database_connection


# =============================================================================
# NICHE REPOSITORY
# =============================================================================


class NicheRepository:
    """Data access layer for niches table."""

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        is_active: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Create a new niche.

        Args:
            name: Niche name
            description: Optional description
            is_active: Whether niche is active

        Returns:
            Niche dict if created, None if error
        """
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO niches (name, description, is_active)
                    VALUES (%s, %s, %s)
                    RETURNING id, name, description, is_active, created_at, updated_at
                    """,
                    (name, description, is_active),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "is_active": row[3],
                        "created_at": row[4],
                        "updated_at": row[5],
                    }
                return None
        except Exception as e:
            print(f"ERROR [NicheRepository]: Failed to create niche: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def get_by_id(self, niche_id: UUID) -> Optional[Dict[str, Any]]:
        """Get niche by UUID."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, description, is_active, created_at, updated_at
                    FROM niches
                    WHERE id = %s
                    """,
                    (str(niche_id),),
                )
                row = cur.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "is_active": row[3],
                        "created_at": row[4],
                        "updated_at": row[5],
                    }
                return None
        except Exception as e:
            print(f"ERROR [NicheRepository]: Failed to get niche by id: {e}")
            return None
        finally:
            close_database_connection(conn)

    def get_all(
        self,
        page: int = 1,
        limit: int = 20,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all niches with pagination.

        Returns:
            Tuple of (list of niches, total count)
        """
        conn = get_database_connection()
        if not conn:
            return [], 0

        try:
            with conn.cursor() as cur:
                where_clause = ""
                params: List[Any] = []

                if is_active is not None:
                    where_clause = "WHERE is_active = %s"
                    params.append(is_active)

                cur.execute(
                    f"SELECT COUNT(*) FROM niches {where_clause}",
                    params,
                )
                total = cur.fetchone()[0]

                offset = (page - 1) * limit
                params.extend([limit, offset])

                cur.execute(
                    f"""
                    SELECT id, name, description, is_active, created_at, updated_at
                    FROM niches
                    {where_clause}
                    ORDER BY name
                    LIMIT %s OFFSET %s
                    """,
                    params,
                )
                rows = cur.fetchall()

                items = [
                    {
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "is_active": row[3],
                        "created_at": row[4],
                        "updated_at": row[5],
                    }
                    for row in rows
                ]
                return items, total
        except Exception as e:
            print(f"ERROR [NicheRepository]: Failed to get niches: {e}")
            return [], 0
        finally:
            close_database_connection(conn)

    def update(
        self,
        niche_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update a niche."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            updates = []
            params: List[Any] = []

            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if description is not None:
                updates.append("description = %s")
                params.append(description)
            if is_active is not None:
                updates.append("is_active = %s")
                params.append(is_active)

            if not updates:
                return self.get_by_id(niche_id)

            params.append(str(niche_id))

            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE niches
                    SET {", ".join(updates)}
                    WHERE id = %s
                    RETURNING id, name, description, is_active, created_at, updated_at
                    """,
                    params,
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "name": row[1],
                        "description": row[2],
                        "is_active": row[3],
                        "created_at": row[4],
                        "updated_at": row[5],
                    }
                return None
        except Exception as e:
            print(f"ERROR [NicheRepository]: Failed to update niche: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def delete(self, niche_id: UUID) -> bool:
        """Delete a niche (soft delete by setting is_active=False)."""
        result = self.update(niche_id, is_active=False)
        return result is not None


# =============================================================================
# CATEGORY REPOSITORY
# =============================================================================


class CategoryRepository:
    """Data access layer for categories table."""

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        parent_id: Optional[UUID] = None,
        sort_order: int = 0,
        is_active: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Create a new category."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO categories (name, description, parent_id, sort_order, is_active)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, name, description, parent_id, sort_order, is_active,
                              created_at, updated_at
                    """,
                    (
                        name,
                        description,
                        str(parent_id) if parent_id else None,
                        sort_order,
                        is_active,
                    ),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [CategoryRepository]: Failed to create category: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def get_by_id(self, category_id: UUID) -> Optional[Dict[str, Any]]:
        """Get category by UUID with parent info."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT c.id, c.name, c.description, c.parent_id, c.sort_order,
                           c.is_active, c.created_at, c.updated_at, p.name as parent_name
                    FROM categories c
                    LEFT JOIN categories p ON c.parent_id = p.id
                    WHERE c.id = %s
                    """,
                    (str(category_id),),
                )
                row = cur.fetchone()

                if row:
                    return self._row_to_dict_with_parent(row)
                return None
        except Exception as e:
            print(f"ERROR [CategoryRepository]: Failed to get category: {e}")
            return None
        finally:
            close_database_connection(conn)

    def get_all(
        self,
        page: int = 1,
        limit: int = 20,
        parent_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all categories with pagination."""
        conn = get_database_connection()
        if not conn:
            return [], 0

        try:
            with conn.cursor() as cur:
                conditions = []
                params: List[Any] = []

                if parent_id is not None:
                    conditions.append("c.parent_id = %s")
                    params.append(str(parent_id))
                if is_active is not None:
                    conditions.append("c.is_active = %s")
                    params.append(is_active)

                where_clause = (
                    "WHERE " + " AND ".join(conditions) if conditions else ""
                )

                cur.execute(
                    f"SELECT COUNT(*) FROM categories c {where_clause}",
                    params,
                )
                total = cur.fetchone()[0]

                offset = (page - 1) * limit
                params.extend([limit, offset])

                cur.execute(
                    f"""
                    SELECT c.id, c.name, c.description, c.parent_id, c.sort_order,
                           c.is_active, c.created_at, c.updated_at, p.name as parent_name
                    FROM categories c
                    LEFT JOIN categories p ON c.parent_id = p.id
                    {where_clause}
                    ORDER BY c.sort_order, c.name
                    LIMIT %s OFFSET %s
                    """,
                    params,
                )
                rows = cur.fetchall()

                items = [self._row_to_dict_with_parent(row) for row in rows]
                return items, total
        except Exception as e:
            print(f"ERROR [CategoryRepository]: Failed to get categories: {e}")
            return [], 0
        finally:
            close_database_connection(conn)

    def update(
        self,
        category_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parent_id: Optional[UUID] = None,
        sort_order: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update a category."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            updates = []
            params: List[Any] = []

            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if description is not None:
                updates.append("description = %s")
                params.append(description)
            if parent_id is not None:
                updates.append("parent_id = %s")
                params.append(str(parent_id))
            if sort_order is not None:
                updates.append("sort_order = %s")
                params.append(sort_order)
            if is_active is not None:
                updates.append("is_active = %s")
                params.append(is_active)

            if not updates:
                return self.get_by_id(category_id)

            params.append(str(category_id))

            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE categories
                    SET {", ".join(updates)}
                    WHERE id = %s
                    RETURNING id, name, description, parent_id, sort_order, is_active,
                              created_at, updated_at
                    """,
                    params,
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [CategoryRepository]: Failed to update category: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def delete(self, category_id: UUID) -> bool:
        """Delete a category (soft delete)."""
        result = self.update(category_id, is_active=False)
        return result is not None

    def _row_to_dict(self, row: tuple) -> Dict[str, Any]:
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "parent_id": row[3],
            "sort_order": row[4],
            "is_active": row[5],
            "created_at": row[6],
            "updated_at": row[7],
        }

    def _row_to_dict_with_parent(self, row: tuple) -> Dict[str, Any]:
        d = self._row_to_dict(row)
        d["parent_name"] = row[8] if len(row) > 8 else None
        return d

    def get_children(self, category_id: UUID) -> List[Dict[str, Any]]:
        """Get immediate children of a category."""
        conn = get_database_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, description, parent_id, sort_order,
                           is_active, created_at, updated_at
                    FROM categories
                    WHERE parent_id = %s
                    ORDER BY sort_order, name
                    """,
                    (str(category_id),),
                )
                rows = cur.fetchall()
                return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"ERROR [CategoryRepository]: Failed to get children: {e}")
            return []
        finally:
            close_database_connection(conn)

    def has_products(self, category_id: UUID) -> bool:
        """Check if category has associated products."""
        conn = get_database_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM products WHERE category_id = %s",
                    (str(category_id),),
                )
                count = cur.fetchone()[0]
                return count > 0
        except Exception as e:
            print(f"ERROR [CategoryRepository]: Failed to check products: {e}")
            return False
        finally:
            close_database_connection(conn)

    def has_children(self, category_id: UUID) -> bool:
        """Check if category has child categories."""
        conn = get_database_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM categories WHERE parent_id = %s",
                    (str(category_id),),
                )
                count = cur.fetchone()[0]
                return count > 0
        except Exception as e:
            print(f"ERROR [CategoryRepository]: Failed to check children: {e}")
            return False
        finally:
            close_database_connection(conn)

    def set_parent(
        self, category_id: UUID, parent_id: Optional[UUID]
    ) -> Optional[Dict[str, Any]]:
        """Set parent of a category (for reparenting)."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE categories
                    SET parent_id = %s
                    WHERE id = %s
                    RETURNING id, name, description, parent_id, sort_order, is_active,
                              created_at, updated_at
                    """,
                    (str(parent_id) if parent_id else None, str(category_id)),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [CategoryRepository]: Failed to set parent: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)


# =============================================================================
# TAG REPOSITORY
# =============================================================================


class TagRepository:
    """Data access layer for tags table."""

    def create(
        self,
        name: str,
        color: str = "#000000",
    ) -> Optional[Dict[str, Any]]:
        """Create a new tag."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO tags (name, color)
                    VALUES (%s, %s)
                    RETURNING id, name, color, created_at, updated_at
                    """,
                    (name, color),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "name": row[1],
                        "color": row[2],
                        "created_at": row[3],
                        "updated_at": row[4],
                    }
                return None
        except Exception as e:
            print(f"ERROR [TagRepository]: Failed to create tag: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def get_by_id(self, tag_id: UUID) -> Optional[Dict[str, Any]]:
        """Get tag by UUID."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, color, created_at, updated_at
                    FROM tags
                    WHERE id = %s
                    """,
                    (str(tag_id),),
                )
                row = cur.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "name": row[1],
                        "color": row[2],
                        "created_at": row[3],
                        "updated_at": row[4],
                    }
                return None
        except Exception as e:
            print(f"ERROR [TagRepository]: Failed to get tag: {e}")
            return None
        finally:
            close_database_connection(conn)

    def get_all(
        self,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all tags with pagination."""
        conn = get_database_connection()
        if not conn:
            return [], 0

        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM tags")
                total = cur.fetchone()[0]

                offset = (page - 1) * limit
                cur.execute(
                    """
                    SELECT id, name, color, created_at, updated_at
                    FROM tags
                    ORDER BY name
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset),
                )
                rows = cur.fetchall()

                items = [
                    {
                        "id": row[0],
                        "name": row[1],
                        "color": row[2],
                        "created_at": row[3],
                        "updated_at": row[4],
                    }
                    for row in rows
                ]
                return items, total
        except Exception as e:
            print(f"ERROR [TagRepository]: Failed to get tags: {e}")
            return [], 0
        finally:
            close_database_connection(conn)

    def update(
        self,
        tag_id: UUID,
        name: Optional[str] = None,
        color: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update a tag."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            updates = []
            params: List[Any] = []

            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if color is not None:
                updates.append("color = %s")
                params.append(color)

            if not updates:
                return self.get_by_id(tag_id)

            params.append(str(tag_id))

            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE tags
                    SET {", ".join(updates)}
                    WHERE id = %s
                    RETURNING id, name, color, created_at, updated_at
                    """,
                    params,
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "name": row[1],
                        "color": row[2],
                        "created_at": row[3],
                        "updated_at": row[4],
                    }
                return None
        except Exception as e:
            print(f"ERROR [TagRepository]: Failed to update tag: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def delete(self, tag_id: UUID) -> bool:
        """Delete a tag (hard delete)."""
        conn = get_database_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM tags WHERE id = %s RETURNING id",
                    (str(tag_id),),
                )
                conn.commit()
                return cur.fetchone() is not None
        except Exception as e:
            print(f"ERROR [TagRepository]: Failed to delete tag: {e}")
            conn.rollback()
            return False
        finally:
            close_database_connection(conn)

    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search tags by name using ILIKE."""
        conn = get_database_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, color, created_at, updated_at
                    FROM tags
                    WHERE name ILIKE %s
                    ORDER BY name
                    LIMIT %s
                    """,
                    (f"%{query}%", limit),
                )
                rows = cur.fetchall()

                return [
                    {
                        "id": row[0],
                        "name": row[1],
                        "color": row[2],
                        "created_at": row[3],
                        "updated_at": row[4],
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"ERROR [TagRepository]: Failed to search tags: {e}")
            return []
        finally:
            close_database_connection(conn)

    def get_product_count(self, tag_id: UUID) -> int:
        """Get product count for a single tag."""
        conn = get_database_connection()
        if not conn:
            return 0

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM product_tags WHERE tag_id = %s",
                    (str(tag_id),),
                )
                return cur.fetchone()[0]
        except Exception as e:
            print(f"ERROR [TagRepository]: Failed to get product count: {e}")
            return 0
        finally:
            close_database_connection(conn)

    def get_all_with_counts(self) -> List[Dict[str, Any]]:
        """Get all tags with product counts."""
        conn = get_database_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT t.id, t.name, t.color, t.created_at, t.updated_at,
                           COALESCE(COUNT(pt.product_id), 0) as product_count
                    FROM tags t
                    LEFT JOIN product_tags pt ON t.id = pt.tag_id
                    GROUP BY t.id, t.name, t.color, t.created_at, t.updated_at
                    ORDER BY t.name
                    """
                )
                rows = cur.fetchall()

                return [
                    {
                        "id": row[0],
                        "name": row[1],
                        "color": row[2],
                        "created_at": row[3],
                        "updated_at": row[4],
                        "product_count": row[5],
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"ERROR [TagRepository]: Failed to get tags with counts: {e}")
            return []
        finally:
            close_database_connection(conn)


# =============================================================================
# HS CODE REPOSITORY
# =============================================================================


class HSCodeRepository:
    """Data access layer for hs_codes table."""

    def create(
        self,
        code: str,
        description: str,
        duty_rate: Decimal = Decimal("0.00"),
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a new HS code."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO hs_codes (code, description, duty_rate, notes)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, code, description, duty_rate, notes, created_at, updated_at
                    """,
                    (code, description, duty_rate, notes),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [HSCodeRepository]: Failed to create HS code: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def get_by_id(self, hs_code_id: UUID) -> Optional[Dict[str, Any]]:
        """Get HS code by UUID."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, code, description, duty_rate, notes, created_at, updated_at
                    FROM hs_codes
                    WHERE id = %s
                    """,
                    (str(hs_code_id),),
                )
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [HSCodeRepository]: Failed to get HS code: {e}")
            return None
        finally:
            close_database_connection(conn)

    def get_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Get HS code by code string."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, code, description, duty_rate, notes, created_at, updated_at
                    FROM hs_codes
                    WHERE code = %s
                    """,
                    (code,),
                )
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [HSCodeRepository]: Failed to get HS code by code: {e}")
            return None
        finally:
            close_database_connection(conn)

    def get_all(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all HS codes with pagination."""
        conn = get_database_connection()
        if not conn:
            return [], 0

        try:
            with conn.cursor() as cur:
                where_clause = ""
                params: List[Any] = []

                if search:
                    where_clause = "WHERE code ILIKE %s OR description ILIKE %s"
                    search_pattern = f"%{search}%"
                    params.extend([search_pattern, search_pattern])

                cur.execute(
                    f"SELECT COUNT(*) FROM hs_codes {where_clause}",
                    params,
                )
                total = cur.fetchone()[0]

                offset = (page - 1) * limit
                params.extend([limit, offset])

                cur.execute(
                    f"""
                    SELECT id, code, description, duty_rate, notes, created_at, updated_at
                    FROM hs_codes
                    {where_clause}
                    ORDER BY code
                    LIMIT %s OFFSET %s
                    """,
                    params,
                )
                rows = cur.fetchall()

                items = [self._row_to_dict(row) for row in rows]
                return items, total
        except Exception as e:
            print(f"ERROR [HSCodeRepository]: Failed to get HS codes: {e}")
            return [], 0
        finally:
            close_database_connection(conn)

    def update(
        self,
        hs_code_id: UUID,
        code: Optional[str] = None,
        description: Optional[str] = None,
        duty_rate: Optional[Decimal] = None,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update an HS code."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            updates = []
            params: List[Any] = []

            if code is not None:
                updates.append("code = %s")
                params.append(code)
            if description is not None:
                updates.append("description = %s")
                params.append(description)
            if duty_rate is not None:
                updates.append("duty_rate = %s")
                params.append(duty_rate)
            if notes is not None:
                updates.append("notes = %s")
                params.append(notes)

            if not updates:
                return self.get_by_id(hs_code_id)

            params.append(str(hs_code_id))

            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE hs_codes
                    SET {", ".join(updates)}
                    WHERE id = %s
                    RETURNING id, code, description, duty_rate, notes, created_at, updated_at
                    """,
                    params,
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [HSCodeRepository]: Failed to update HS code: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def delete(self, hs_code_id: UUID) -> bool:
        """Delete an HS code (hard delete)."""
        conn = get_database_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM hs_codes WHERE id = %s RETURNING id",
                    (str(hs_code_id),),
                )
                conn.commit()
                return cur.fetchone() is not None
        except Exception as e:
            print(f"ERROR [HSCodeRepository]: Failed to delete HS code: {e}")
            conn.rollback()
            return False
        finally:
            close_database_connection(conn)

    def _row_to_dict(self, row: tuple) -> Dict[str, Any]:
        return {
            "id": row[0],
            "code": row[1],
            "description": row[2],
            "duty_rate": row[3],
            "notes": row[4],
            "created_at": row[5],
            "updated_at": row[6],
        }


# =============================================================================
# SUPPLIER REPOSITORY
# =============================================================================


class SupplierRepository:
    """Data access layer for suppliers table."""

    def create(
        self,
        name: str,
        code: Optional[str] = None,
        status: str = "active",
        contact_name: Optional[str] = None,
        contact_email: Optional[str] = None,
        contact_phone: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        country: str = "China",
        website: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a new supplier."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO suppliers (
                        name, code, status, contact_name, contact_email, contact_phone,
                        address, city, country, website, notes
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, name, code, status, contact_name, contact_email,
                              contact_phone, address, city, country, website, notes,
                              created_at, updated_at
                    """,
                    (
                        name,
                        code,
                        status,
                        contact_name,
                        contact_email,
                        contact_phone,
                        address,
                        city,
                        country,
                        website,
                        notes,
                    ),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [SupplierRepository]: Failed to create supplier: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def get_by_id(self, supplier_id: UUID) -> Optional[Dict[str, Any]]:
        """Get supplier by UUID."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, code, status, contact_name, contact_email,
                           contact_phone, address, city, country, website, notes,
                           created_at, updated_at
                    FROM suppliers
                    WHERE id = %s
                    """,
                    (str(supplier_id),),
                )
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [SupplierRepository]: Failed to get supplier: {e}")
            return None
        finally:
            close_database_connection(conn)

    def get_all(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all suppliers with pagination."""
        conn = get_database_connection()
        if not conn:
            return [], 0

        try:
            with conn.cursor() as cur:
                conditions = []
                params: List[Any] = []

                if status:
                    conditions.append("status = %s")
                    params.append(status)
                if search:
                    conditions.append("(name ILIKE %s OR code ILIKE %s)")
                    search_pattern = f"%{search}%"
                    params.extend([search_pattern, search_pattern])

                where_clause = (
                    "WHERE " + " AND ".join(conditions) if conditions else ""
                )

                cur.execute(
                    f"SELECT COUNT(*) FROM suppliers {where_clause}",
                    params,
                )
                total = cur.fetchone()[0]

                offset = (page - 1) * limit
                params.extend([limit, offset])

                cur.execute(
                    f"""
                    SELECT id, name, code, status, contact_name, contact_email,
                           contact_phone, address, city, country, website, notes,
                           created_at, updated_at
                    FROM suppliers
                    {where_clause}
                    ORDER BY name
                    LIMIT %s OFFSET %s
                    """,
                    params,
                )
                rows = cur.fetchall()

                items = [self._row_to_dict(row) for row in rows]
                return items, total
        except Exception as e:
            print(f"ERROR [SupplierRepository]: Failed to get suppliers: {e}")
            return [], 0
        finally:
            close_database_connection(conn)

    def update(
        self,
        supplier_id: UUID,
        name: Optional[str] = None,
        code: Optional[str] = None,
        status: Optional[str] = None,
        contact_name: Optional[str] = None,
        contact_email: Optional[str] = None,
        contact_phone: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        website: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update a supplier."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            updates = []
            params: List[Any] = []

            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if code is not None:
                updates.append("code = %s")
                params.append(code)
            if status is not None:
                updates.append("status = %s")
                params.append(status)
            if contact_name is not None:
                updates.append("contact_name = %s")
                params.append(contact_name)
            if contact_email is not None:
                updates.append("contact_email = %s")
                params.append(contact_email)
            if contact_phone is not None:
                updates.append("contact_phone = %s")
                params.append(contact_phone)
            if address is not None:
                updates.append("address = %s")
                params.append(address)
            if city is not None:
                updates.append("city = %s")
                params.append(city)
            if country is not None:
                updates.append("country = %s")
                params.append(country)
            if website is not None:
                updates.append("website = %s")
                params.append(website)
            if notes is not None:
                updates.append("notes = %s")
                params.append(notes)

            if not updates:
                return self.get_by_id(supplier_id)

            params.append(str(supplier_id))

            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE suppliers
                    SET {", ".join(updates)}
                    WHERE id = %s
                    RETURNING id, name, code, status, contact_name, contact_email,
                              contact_phone, address, city, country, website, notes,
                              created_at, updated_at
                    """,
                    params,
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [SupplierRepository]: Failed to update supplier: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def delete(self, supplier_id: UUID) -> bool:
        """Delete a supplier (soft delete by setting status to inactive)."""
        result = self.update(supplier_id, status="inactive")
        return result is not None

    def _row_to_dict(self, row: tuple) -> Dict[str, Any]:
        return {
            "id": row[0],
            "name": row[1],
            "code": row[2],
            "status": row[3],
            "contact_name": row[4],
            "contact_email": row[5],
            "contact_phone": row[6],
            "address": row[7],
            "city": row[8],
            "country": row[9],
            "website": row[10],
            "notes": row[11],
            "created_at": row[12],
            "updated_at": row[13],
        }

    def count_products_by_supplier(self, supplier_id: UUID) -> int:
        """Count products for a specific supplier.

        Args:
            supplier_id: UUID of the supplier

        Returns:
            Number of products for this supplier
        """
        conn = get_database_connection()
        if not conn:
            return 0

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM products WHERE supplier_id = %s",
                    (str(supplier_id),),
                )
                return cur.fetchone()[0]
        except Exception as e:
            print(f"ERROR [SupplierRepository]: Failed to count products: {e}")
            return 0
        finally:
            close_database_connection(conn)

    def get_all_with_filters(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        country: Optional[str] = None,
        has_products: Optional[bool] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all suppliers with extended filtering options.

        Args:
            page: Page number (1-indexed)
            limit: Items per page
            status: Filter by supplier status
            country: Filter by country
            has_products: Filter by whether supplier has products

        Returns:
            Tuple of (list of suppliers, total count)
        """
        conn = get_database_connection()
        if not conn:
            return [], 0

        try:
            with conn.cursor() as cur:
                conditions = []
                params: List[Any] = []

                if status:
                    conditions.append("s.status = %s")
                    params.append(status)
                if country:
                    conditions.append("s.country = %s")
                    params.append(country)

                # Handle has_products filter using subquery
                if has_products is True:
                    conditions.append(
                        "EXISTS (SELECT 1 FROM products p WHERE p.supplier_id = s.id)"
                    )
                elif has_products is False:
                    conditions.append(
                        "NOT EXISTS (SELECT 1 FROM products p WHERE p.supplier_id = s.id)"
                    )

                where_clause = (
                    "WHERE " + " AND ".join(conditions) if conditions else ""
                )

                # Count query
                cur.execute(
                    f"SELECT COUNT(*) FROM suppliers s {where_clause}",
                    params,
                )
                total = cur.fetchone()[0]

                offset = (page - 1) * limit
                params.extend([limit, offset])

                # Main query
                cur.execute(
                    f"""
                    SELECT s.id, s.name, s.code, s.status, s.contact_name, s.contact_email,
                           s.contact_phone, s.address, s.city, s.country, s.website, s.notes,
                           s.created_at, s.updated_at
                    FROM suppliers s
                    {where_clause}
                    ORDER BY s.name
                    LIMIT %s OFFSET %s
                    """,
                    params,
                )
                rows = cur.fetchall()

                items = [self._row_to_dict(row) for row in rows]
                return items, total
        except Exception as e:
            print(f"ERROR [SupplierRepository]: Failed to get suppliers with filters: {e}")
            return [], 0
        finally:
            close_database_connection(conn)

    def search(
        self,
        query: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search suppliers by name, email, or contact phone.

        Args:
            query: Search query string
            limit: Maximum number of results

        Returns:
            List of matching suppliers
        """
        conn = get_database_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cur:
                search_pattern = f"%{query}%"
                cur.execute(
                    """
                    SELECT id, name, code, status, contact_name, contact_email,
                           contact_phone, address, city, country, website, notes,
                           created_at, updated_at
                    FROM suppliers
                    WHERE name ILIKE %s
                       OR contact_email ILIKE %s
                       OR contact_phone ILIKE %s
                       OR code ILIKE %s
                    ORDER BY name
                    LIMIT %s
                    """,
                    (search_pattern, search_pattern, search_pattern, search_pattern, limit),
                )
                rows = cur.fetchall()

                return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"ERROR [SupplierRepository]: Failed to search suppliers: {e}")
            return []
        finally:
            close_database_connection(conn)


# =============================================================================
# PRODUCT REPOSITORY
# =============================================================================


class ProductRepository:
    """Data access layer for products table."""

    def create(
        self,
        sku: str,
        name: str,
        supplier_id: UUID,
        description: Optional[str] = None,
        category_id: Optional[UUID] = None,
        hs_code_id: Optional[UUID] = None,
        status: str = "draft",
        unit_cost: Decimal = Decimal("0.00"),
        unit_price: Decimal = Decimal("0.00"),
        currency: str = "USD",
        unit_of_measure: str = "piece",
        minimum_order_qty: int = 1,
        lead_time_days: Optional[int] = None,
        weight_kg: Optional[Decimal] = None,
        dimensions: Optional[str] = None,
        origin_country: str = "China",
    ) -> Optional[Dict[str, Any]]:
        """Create a new product."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO products (
                        sku, name, description, supplier_id, category_id, hs_code_id,
                        status, unit_cost, unit_price, currency, unit_of_measure,
                        minimum_order_qty, lead_time_days, weight_kg, dimensions,
                        origin_country
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, sku, name, description, supplier_id, category_id,
                              hs_code_id, status, unit_cost, unit_price, currency,
                              unit_of_measure, minimum_order_qty, lead_time_days,
                              weight_kg, dimensions, origin_country, created_at, updated_at
                    """,
                    (
                        sku,
                        name,
                        description,
                        str(supplier_id),
                        str(category_id) if category_id else None,
                        str(hs_code_id) if hs_code_id else None,
                        status,
                        unit_cost,
                        unit_price,
                        currency,
                        unit_of_measure,
                        minimum_order_qty,
                        lead_time_days,
                        weight_kg,
                        dimensions,
                        origin_country,
                    ),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [ProductRepository]: Failed to create product: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def get_by_id(self, product_id: UUID) -> Optional[Dict[str, Any]]:
        """Get product by UUID with related data."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT p.id, p.sku, p.name, p.description, p.supplier_id, p.category_id,
                           p.hs_code_id, p.status, p.unit_cost, p.unit_price, p.currency,
                           p.unit_of_measure, p.minimum_order_qty, p.lead_time_days,
                           p.weight_kg, p.dimensions, p.origin_country, p.created_at,
                           p.updated_at, s.name as supplier_name, c.name as category_name,
                           h.code as hs_code
                    FROM products p
                    LEFT JOIN suppliers s ON p.supplier_id = s.id
                    LEFT JOIN categories c ON p.category_id = c.id
                    LEFT JOIN hs_codes h ON p.hs_code_id = h.id
                    WHERE p.id = %s
                    """,
                    (str(product_id),),
                )
                row = cur.fetchone()

                if row:
                    product = self._row_to_dict_with_joins(row)
                    product["images"] = self._get_product_images(cur, product_id)
                    product["tags"] = self._get_product_tags(cur, product_id)
                    return product
                return None
        except Exception as e:
            print(f"ERROR [ProductRepository]: Failed to get product: {e}")
            return None
        finally:
            close_database_connection(conn)

    def get_all(
        self,
        page: int = 1,
        limit: int = 20,
        category_id: Optional[UUID] = None,
        supplier_id: Optional[UUID] = None,
        status: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        search: Optional[str] = None,
        tag_ids: Optional[List[UUID]] = None,
        has_images: Optional[bool] = None,
        min_moq: Optional[int] = None,
        max_moq: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all products with pagination and filters.

        Args:
            page: Page number (1-indexed)
            limit: Number of items per page
            category_id: Filter by category UUID
            supplier_id: Filter by supplier UUID
            status: Filter by product status
            min_price: Minimum unit price filter
            max_price: Maximum unit price filter
            search: Search term for name, description, and SKU
            tag_ids: Filter by tag UUIDs
            has_images: Filter products with/without images
            min_moq: Minimum order quantity filter
            max_moq: Maximum order quantity filter
            sort_by: Sort field (name, unit_price, created_at, minimum_order_qty)
            sort_order: Sort order (asc or desc)

        Returns:
            Tuple of (list of products, total count)
        """
        conn = get_database_connection()
        if not conn:
            return [], 0

        try:
            with conn.cursor() as cur:
                conditions = []
                params: List[Any] = []

                if category_id:
                    conditions.append("p.category_id = %s")
                    params.append(str(category_id))
                if supplier_id:
                    conditions.append("p.supplier_id = %s")
                    params.append(str(supplier_id))
                if status:
                    conditions.append("p.status = %s")
                    params.append(status)
                if min_price is not None:
                    conditions.append("p.unit_price >= %s")
                    params.append(min_price)
                if max_price is not None:
                    conditions.append("p.unit_price <= %s")
                    params.append(max_price)
                if search:
                    conditions.append(
                        "(p.name ILIKE %s OR p.sku ILIKE %s OR p.description ILIKE %s)"
                    )
                    search_pattern = f"%{search}%"
                    params.extend([search_pattern, search_pattern, search_pattern])
                if tag_ids:
                    placeholders = ", ".join(["%s"] * len(tag_ids))
                    conditions.append(
                        f"""
                        p.id IN (
                            SELECT product_id FROM product_tags
                            WHERE tag_id IN ({placeholders})
                        )
                    """
                    )
                    params.extend([str(tid) for tid in tag_ids])
                if has_images is True:
                    conditions.append(
                        """
                        EXISTS (
                            SELECT 1 FROM product_images pi WHERE pi.product_id = p.id
                        )
                    """
                    )
                elif has_images is False:
                    conditions.append(
                        """
                        NOT EXISTS (
                            SELECT 1 FROM product_images pi WHERE pi.product_id = p.id
                        )
                    """
                    )
                if min_moq is not None:
                    conditions.append("p.minimum_order_qty >= %s")
                    params.append(min_moq)
                if max_moq is not None:
                    conditions.append("p.minimum_order_qty <= %s")
                    params.append(max_moq)

                where_clause = (
                    "WHERE " + " AND ".join(conditions) if conditions else ""
                )

                cur.execute(
                    f"SELECT COUNT(*) FROM products p {where_clause}",
                    params,
                )
                total = cur.fetchone()[0]

                offset = (page - 1) * limit
                params.extend([limit, offset])

                # Build ORDER BY clause
                allowed_sort_fields = {
                    "name": "p.name",
                    "unit_price": "p.unit_price",
                    "created_at": "p.created_at",
                    "minimum_order_qty": "p.minimum_order_qty",
                }
                order_field = allowed_sort_fields.get(sort_by, "p.name")
                order_direction = "DESC" if sort_order.lower() == "desc" else "ASC"
                order_clause = f"ORDER BY {order_field} {order_direction}"

                cur.execute(
                    f"""
                    SELECT p.id, p.sku, p.name, p.description, p.supplier_id, p.category_id,
                           p.hs_code_id, p.status, p.unit_cost, p.unit_price, p.currency,
                           p.unit_of_measure, p.minimum_order_qty, p.lead_time_days,
                           p.weight_kg, p.dimensions, p.origin_country, p.created_at,
                           p.updated_at, s.name as supplier_name, c.name as category_name,
                           h.code as hs_code
                    FROM products p
                    LEFT JOIN suppliers s ON p.supplier_id = s.id
                    LEFT JOIN categories c ON p.category_id = c.id
                    LEFT JOIN hs_codes h ON p.hs_code_id = h.id
                    {where_clause}
                    {order_clause}
                    LIMIT %s OFFSET %s
                    """,
                    params,
                )
                rows = cur.fetchall()

                items = []
                for row in rows:
                    product = self._row_to_dict_with_joins(row)
                    product["images"] = self._get_product_images(cur, product["id"])
                    product["tags"] = self._get_product_tags(cur, product["id"])
                    items.append(product)

                return items, total
        except Exception as e:
            print(f"ERROR [ProductRepository]: Failed to get products: {e}")
            return [], 0
        finally:
            close_database_connection(conn)

    def update(
        self,
        product_id: UUID,
        sku: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        supplier_id: Optional[UUID] = None,
        category_id: Optional[UUID] = None,
        hs_code_id: Optional[UUID] = None,
        status: Optional[str] = None,
        unit_cost: Optional[Decimal] = None,
        unit_price: Optional[Decimal] = None,
        currency: Optional[str] = None,
        unit_of_measure: Optional[str] = None,
        minimum_order_qty: Optional[int] = None,
        lead_time_days: Optional[int] = None,
        weight_kg: Optional[Decimal] = None,
        dimensions: Optional[str] = None,
        origin_country: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update a product."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            updates = []
            params: List[Any] = []

            if sku is not None:
                updates.append("sku = %s")
                params.append(sku)
            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if description is not None:
                updates.append("description = %s")
                params.append(description)
            if supplier_id is not None:
                updates.append("supplier_id = %s")
                params.append(str(supplier_id))
            if category_id is not None:
                updates.append("category_id = %s")
                params.append(str(category_id))
            if hs_code_id is not None:
                updates.append("hs_code_id = %s")
                params.append(str(hs_code_id))
            if status is not None:
                updates.append("status = %s")
                params.append(status)
            if unit_cost is not None:
                updates.append("unit_cost = %s")
                params.append(unit_cost)
            if unit_price is not None:
                updates.append("unit_price = %s")
                params.append(unit_price)
            if currency is not None:
                updates.append("currency = %s")
                params.append(currency)
            if unit_of_measure is not None:
                updates.append("unit_of_measure = %s")
                params.append(unit_of_measure)
            if minimum_order_qty is not None:
                updates.append("minimum_order_qty = %s")
                params.append(minimum_order_qty)
            if lead_time_days is not None:
                updates.append("lead_time_days = %s")
                params.append(lead_time_days)
            if weight_kg is not None:
                updates.append("weight_kg = %s")
                params.append(weight_kg)
            if dimensions is not None:
                updates.append("dimensions = %s")
                params.append(dimensions)
            if origin_country is not None:
                updates.append("origin_country = %s")
                params.append(origin_country)

            if not updates:
                return self.get_by_id(product_id)

            params.append(str(product_id))

            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE products
                    SET {", ".join(updates)}
                    WHERE id = %s
                    RETURNING id
                    """,
                    params,
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self.get_by_id(product_id)
                return None
        except Exception as e:
            print(f"ERROR [ProductRepository]: Failed to update product: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def delete(self, product_id: UUID) -> bool:
        """Delete a product (soft delete by setting status to inactive)."""
        result = self.update(product_id, status="inactive")
        return result is not None

    def add_tag(self, product_id: UUID, tag_id: UUID) -> bool:
        """Add a tag to a product."""
        conn = get_database_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO product_tags (product_id, tag_id)
                    VALUES (%s, %s)
                    ON CONFLICT (product_id, tag_id) DO NOTHING
                    """,
                    (str(product_id), str(tag_id)),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"ERROR [ProductRepository]: Failed to add tag: {e}")
            conn.rollback()
            return False
        finally:
            close_database_connection(conn)

    def remove_tag(self, product_id: UUID, tag_id: UUID) -> bool:
        """Remove a tag from a product."""
        conn = get_database_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM product_tags
                    WHERE product_id = %s AND tag_id = %s
                    """,
                    (str(product_id), str(tag_id)),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"ERROR [ProductRepository]: Failed to remove tag: {e}")
            conn.rollback()
            return False
        finally:
            close_database_connection(conn)

    def add_image(
        self,
        product_id: UUID,
        url: str,
        alt_text: Optional[str] = None,
        sort_order: int = 0,
        is_primary: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Add an image to a product."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                if is_primary:
                    cur.execute(
                        """
                        UPDATE product_images SET is_primary = false
                        WHERE product_id = %s
                        """,
                        (str(product_id),),
                    )

                cur.execute(
                    """
                    INSERT INTO product_images (product_id, url, alt_text, sort_order, is_primary)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, product_id, url, alt_text, sort_order, is_primary,
                              created_at, updated_at
                    """,
                    (str(product_id), url, alt_text, sort_order, is_primary),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "product_id": row[1],
                        "url": row[2],
                        "alt_text": row[3],
                        "sort_order": row[4],
                        "is_primary": row[5],
                        "created_at": row[6],
                        "updated_at": row[7],
                    }
                return None
        except Exception as e:
            print(f"ERROR [ProductRepository]: Failed to add image: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def remove_image(self, image_id: UUID) -> bool:
        """Remove an image from a product."""
        conn = get_database_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM product_images WHERE id = %s RETURNING id",
                    (str(image_id),),
                )
                conn.commit()
                return cur.fetchone() is not None
        except Exception as e:
            print(f"ERROR [ProductRepository]: Failed to remove image: {e}")
            conn.rollback()
            return False
        finally:
            close_database_connection(conn)

    def set_primary_image(self, product_id: UUID, image_id: UUID) -> bool:
        """Set a specific image as the primary image for a product.

        Args:
            product_id: Product UUID
            image_id: Image UUID to set as primary

        Returns:
            True if successful, False otherwise
        """
        conn = get_database_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                # First, set all images for this product to non-primary
                cur.execute(
                    """
                    UPDATE product_images
                    SET is_primary = false
                    WHERE product_id = %s
                    """,
                    (str(product_id),),
                )
                # Then set the specified image as primary
                cur.execute(
                    """
                    UPDATE product_images
                    SET is_primary = true
                    WHERE id = %s AND product_id = %s
                    RETURNING id
                    """,
                    (str(image_id), str(product_id)),
                )
                conn.commit()
                return cur.fetchone() is not None
        except Exception as e:
            print(f"ERROR [ProductRepository]: Failed to set primary image: {e}")
            conn.rollback()
            return False
        finally:
            close_database_connection(conn)

    def _get_product_images(self, cur: Any, product_id: UUID) -> List[Dict[str, Any]]:
        """Get images for a product."""
        cur.execute(
            """
            SELECT id, product_id, url, alt_text, sort_order, is_primary,
                   created_at, updated_at
            FROM product_images
            WHERE product_id = %s
            ORDER BY sort_order, created_at
            """,
            (str(product_id),),
        )
        rows = cur.fetchall()
        return [
            {
                "id": row[0],
                "product_id": row[1],
                "url": row[2],
                "alt_text": row[3],
                "sort_order": row[4],
                "is_primary": row[5],
                "created_at": row[6],
                "updated_at": row[7],
            }
            for row in rows
        ]

    def _get_product_tags(self, cur: Any, product_id: UUID) -> List[Dict[str, Any]]:
        """Get tags for a product."""
        cur.execute(
            """
            SELECT t.id, t.name, t.color, t.created_at, t.updated_at
            FROM tags t
            JOIN product_tags pt ON t.id = pt.tag_id
            WHERE pt.product_id = %s
            ORDER BY t.name
            """,
            (str(product_id),),
        )
        rows = cur.fetchall()
        return [
            {
                "id": row[0],
                "name": row[1],
                "color": row[2],
                "created_at": row[3],
                "updated_at": row[4],
            }
            for row in rows
        ]

    def _row_to_dict(self, row: tuple) -> Dict[str, Any]:
        return {
            "id": row[0],
            "sku": row[1],
            "name": row[2],
            "description": row[3],
            "supplier_id": row[4],
            "category_id": row[5],
            "hs_code_id": row[6],
            "status": row[7],
            "unit_cost": row[8],
            "unit_price": row[9],
            "currency": row[10],
            "unit_of_measure": row[11],
            "minimum_order_qty": row[12],
            "lead_time_days": row[13],
            "weight_kg": row[14],
            "dimensions": row[15],
            "origin_country": row[16],
            "created_at": row[17],
            "updated_at": row[18],
            "images": [],
            "tags": [],
        }

    def _row_to_dict_with_joins(self, row: tuple) -> Dict[str, Any]:
        d = self._row_to_dict(row)
        d["supplier_name"] = row[19] if len(row) > 19 else None
        d["category_name"] = row[20] if len(row) > 20 else None
        d["hs_code"] = row[21] if len(row) > 21 else None
        return d


# =============================================================================
# PORTFOLIO REPOSITORY
# =============================================================================


class PortfolioRepository:
    """Data access layer for portfolios table."""

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        niche_id: Optional[UUID] = None,
        is_active: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """Create a new portfolio."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO portfolios (name, description, niche_id, is_active)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, name, description, niche_id, is_active, created_at, updated_at
                    """,
                    (name, description, str(niche_id) if niche_id else None, is_active),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self.get_by_id(row[0])
                return None
        except Exception as e:
            print(f"ERROR [PortfolioRepository]: Failed to create portfolio: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def get_by_id(self, portfolio_id: UUID) -> Optional[Dict[str, Any]]:
        """Get portfolio by UUID with items."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT p.id, p.name, p.description, p.niche_id, p.is_active,
                           p.created_at, p.updated_at, n.name as niche_name
                    FROM portfolios p
                    LEFT JOIN niches n ON p.niche_id = n.id
                    WHERE p.id = %s
                    """,
                    (str(portfolio_id),),
                )
                row = cur.fetchone()

                if row:
                    portfolio = self._row_to_dict_with_niche(row)
                    portfolio["items"] = self._get_portfolio_items(cur, portfolio_id)
                    portfolio["item_count"] = len(portfolio["items"])
                    return portfolio
                return None
        except Exception as e:
            print(f"ERROR [PortfolioRepository]: Failed to get portfolio: {e}")
            return None
        finally:
            close_database_connection(conn)

    def get_all(
        self,
        page: int = 1,
        limit: int = 20,
        niche_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all portfolios with pagination."""
        conn = get_database_connection()
        if not conn:
            return [], 0

        try:
            with conn.cursor() as cur:
                conditions = []
                params: List[Any] = []

                if niche_id:
                    conditions.append("p.niche_id = %s")
                    params.append(str(niche_id))
                if is_active is not None:
                    conditions.append("p.is_active = %s")
                    params.append(is_active)

                where_clause = (
                    "WHERE " + " AND ".join(conditions) if conditions else ""
                )

                cur.execute(
                    f"SELECT COUNT(*) FROM portfolios p {where_clause}",
                    params,
                )
                total = cur.fetchone()[0]

                offset = (page - 1) * limit
                params.extend([limit, offset])

                cur.execute(
                    f"""
                    SELECT p.id, p.name, p.description, p.niche_id, p.is_active,
                           p.created_at, p.updated_at, n.name as niche_name
                    FROM portfolios p
                    LEFT JOIN niches n ON p.niche_id = n.id
                    {where_clause}
                    ORDER BY p.name
                    LIMIT %s OFFSET %s
                    """,
                    params,
                )
                rows = cur.fetchall()

                items = []
                for row in rows:
                    portfolio = self._row_to_dict_with_niche(row)
                    portfolio["items"] = self._get_portfolio_items(cur, portfolio["id"])
                    portfolio["item_count"] = len(portfolio["items"])
                    items.append(portfolio)

                return items, total
        except Exception as e:
            print(f"ERROR [PortfolioRepository]: Failed to get portfolios: {e}")
            return [], 0
        finally:
            close_database_connection(conn)

    def update(
        self,
        portfolio_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        niche_id: Optional[UUID] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update a portfolio."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            updates = []
            params: List[Any] = []

            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if description is not None:
                updates.append("description = %s")
                params.append(description)
            if niche_id is not None:
                updates.append("niche_id = %s")
                params.append(str(niche_id))
            if is_active is not None:
                updates.append("is_active = %s")
                params.append(is_active)

            if not updates:
                return self.get_by_id(portfolio_id)

            params.append(str(portfolio_id))

            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE portfolios
                    SET {", ".join(updates)}
                    WHERE id = %s
                    RETURNING id
                    """,
                    params,
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self.get_by_id(portfolio_id)
                return None
        except Exception as e:
            print(f"ERROR [PortfolioRepository]: Failed to update portfolio: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def delete(self, portfolio_id: UUID) -> bool:
        """Delete a portfolio (soft delete)."""
        result = self.update(portfolio_id, is_active=False)
        return result is not None

    def add_item(
        self,
        portfolio_id: UUID,
        product_id: UUID,
        sort_order: int = 0,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Add an item to a portfolio."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO portfolio_items (portfolio_id, product_id, sort_order, notes)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (portfolio_id, product_id) DO UPDATE
                    SET sort_order = EXCLUDED.sort_order, notes = EXCLUDED.notes
                    RETURNING id, portfolio_id, product_id, sort_order, notes,
                              created_at, updated_at
                    """,
                    (str(portfolio_id), str(product_id), sort_order, notes),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "portfolio_id": row[1],
                        "product_id": row[2],
                        "sort_order": row[3],
                        "notes": row[4],
                        "created_at": row[5],
                        "updated_at": row[6],
                    }
                return None
        except Exception as e:
            print(f"ERROR [PortfolioRepository]: Failed to add item: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def remove_item(self, portfolio_id: UUID, product_id: UUID) -> bool:
        """Remove an item from a portfolio."""
        conn = get_database_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM portfolio_items
                    WHERE portfolio_id = %s AND product_id = %s
                    """,
                    (str(portfolio_id), str(product_id)),
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"ERROR [PortfolioRepository]: Failed to remove item: {e}")
            conn.rollback()
            return False
        finally:
            close_database_connection(conn)

    def _get_portfolio_items(
        self, cur: Any, portfolio_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get items for a portfolio."""
        cur.execute(
            """
            SELECT pi.id, pi.portfolio_id, pi.product_id, pi.sort_order, pi.notes,
                   pi.created_at, pi.updated_at, p.name as product_name, p.sku as product_sku
            FROM portfolio_items pi
            JOIN products p ON pi.product_id = p.id
            WHERE pi.portfolio_id = %s
            ORDER BY pi.sort_order, p.name
            """,
            (str(portfolio_id),),
        )
        rows = cur.fetchall()
        return [
            {
                "id": row[0],
                "portfolio_id": row[1],
                "product_id": row[2],
                "sort_order": row[3],
                "notes": row[4],
                "created_at": row[5],
                "updated_at": row[6],
                "product_name": row[7],
                "product_sku": row[8],
            }
            for row in rows
        ]

    def _row_to_dict_with_niche(self, row: tuple) -> Dict[str, Any]:
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "niche_id": row[3],
            "is_active": row[4],
            "created_at": row[5],
            "updated_at": row[6],
            "niche_name": row[7] if len(row) > 7 else None,
            "items": [],
            "item_count": 0,
        }


# =============================================================================
# CLIENT REPOSITORY
# =============================================================================


class ClientRepository:
    """Data access layer for clients table."""

    def create(
        self,
        company_name: str,
        contact_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        postal_code: Optional[str] = None,
        niche_id: Optional[UUID] = None,
        status: str = "prospect",
        notes: Optional[str] = None,
        assigned_to: Optional[UUID] = None,
        source: Optional[str] = None,
        project_deadline: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a new client."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO clients (
                        company_name, contact_name, email, phone, address, city,
                        state, country, postal_code, niche_id, status, notes,
                        assigned_to, source, project_deadline
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, company_name, contact_name, email, phone, address,
                              city, state, country, postal_code, niche_id, status, notes,
                              created_at, updated_at
                    """,
                    (
                        company_name,
                        contact_name,
                        email,
                        phone,
                        address,
                        city,
                        state,
                        country,
                        postal_code,
                        str(niche_id) if niche_id else None,
                        status,
                        notes,
                        str(assigned_to) if assigned_to else None,
                        source,
                        project_deadline,
                    ),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self.get_by_id(row[0])
                return None
        except Exception as e:
            print(f"ERROR [ClientRepository]: Failed to create client: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def get_by_id(self, client_id: UUID) -> Optional[Dict[str, Any]]:
        """Get client by UUID."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT c.id, c.company_name, c.contact_name, c.email, c.phone,
                           c.address, c.city, c.state, c.country, c.postal_code,
                           c.niche_id, c.status, c.notes, c.created_at, c.updated_at,
                           n.name as niche_name,
                           c.assigned_to, c.source, c.project_deadline,
                           u.first_name || ' ' || u.last_name as assigned_to_name
                    FROM clients c
                    LEFT JOIN niches n ON c.niche_id = n.id
                    LEFT JOIN users u ON c.assigned_to = u.id
                    WHERE c.id = %s
                    """,
                    (str(client_id),),
                )
                row = cur.fetchone()

                if row:
                    return self._row_to_dict_with_niche(row)
                return None
        except Exception as e:
            print(f"ERROR [ClientRepository]: Failed to get client: {e}")
            return None
        finally:
            close_database_connection(conn)

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get client by email."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT c.id, c.company_name, c.contact_name, c.email, c.phone,
                           c.address, c.city, c.state, c.country, c.postal_code,
                           c.niche_id, c.status, c.notes, c.created_at, c.updated_at,
                           n.name as niche_name,
                           c.assigned_to, c.source, c.project_deadline,
                           u.first_name || ' ' || u.last_name as assigned_to_name
                    FROM clients c
                    LEFT JOIN niches n ON c.niche_id = n.id
                    LEFT JOIN users u ON c.assigned_to = u.id
                    WHERE c.email = %s
                    """,
                    (email,),
                )
                row = cur.fetchone()

                if row:
                    return self._row_to_dict_with_niche(row)
                return None
        except Exception as e:
            print(f"ERROR [ClientRepository]: Failed to get client by email: {e}")
            return None
        finally:
            close_database_connection(conn)

    def get_all(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        niche_id: Optional[UUID] = None,
        search: Optional[str] = None,
        assigned_to: Optional[UUID] = None,
        source: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        sort_by: str = "company_name",
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all clients with pagination and filters."""
        conn = get_database_connection()
        if not conn:
            return [], 0

        try:
            with conn.cursor() as cur:
                conditions = []
                params: List[Any] = []

                if status:
                    conditions.append("c.status = %s")
                    params.append(status)
                if niche_id:
                    conditions.append("c.niche_id = %s")
                    params.append(str(niche_id))
                if search:
                    conditions.append(
                        "(c.company_name ILIKE %s OR c.contact_name ILIKE %s OR c.email ILIKE %s)"
                    )
                    search_pattern = f"%{search}%"
                    params.extend([search_pattern, search_pattern, search_pattern])
                if assigned_to:
                    conditions.append("c.assigned_to = %s")
                    params.append(str(assigned_to))
                if source:
                    conditions.append("c.source = %s")
                    params.append(source)
                if date_from:
                    conditions.append("c.created_at >= %s")
                    params.append(date_from)
                if date_to:
                    conditions.append("c.created_at <= %s")
                    params.append(date_to)

                where_clause = (
                    "WHERE " + " AND ".join(conditions) if conditions else ""
                )

                cur.execute(
                    f"SELECT COUNT(*) FROM clients c {where_clause}",
                    params,
                )
                total = cur.fetchone()[0]

                # Determine sort column
                sort_column = "c.company_name"
                if sort_by == "created_at":
                    sort_column = "c.created_at DESC"
                elif sort_by == "project_deadline":
                    sort_column = "c.project_deadline"
                elif sort_by == "company_name":
                    sort_column = "c.company_name"

                offset = (page - 1) * limit
                params.extend([limit, offset])

                cur.execute(
                    f"""
                    SELECT c.id, c.company_name, c.contact_name, c.email, c.phone,
                           c.address, c.city, c.state, c.country, c.postal_code,
                           c.niche_id, c.status, c.notes, c.created_at, c.updated_at,
                           n.name as niche_name,
                           c.assigned_to, c.source, c.project_deadline,
                           u.first_name || ' ' || u.last_name as assigned_to_name
                    FROM clients c
                    LEFT JOIN niches n ON c.niche_id = n.id
                    LEFT JOIN users u ON c.assigned_to = u.id
                    {where_clause}
                    ORDER BY {sort_column}
                    LIMIT %s OFFSET %s
                    """,
                    params,
                )
                rows = cur.fetchall()

                items = [self._row_to_dict_with_niche(row) for row in rows]
                return items, total
        except Exception as e:
            print(f"ERROR [ClientRepository]: Failed to get clients: {e}")
            return [], 0
        finally:
            close_database_connection(conn)

    def update(
        self,
        client_id: UUID,
        company_name: Optional[str] = None,
        contact_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        postal_code: Optional[str] = None,
        niche_id: Optional[UUID] = None,
        status: Optional[str] = None,
        notes: Optional[str] = None,
        assigned_to: Optional[UUID] = None,
        source: Optional[str] = None,
        project_deadline: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update a client."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            updates = []
            params: List[Any] = []

            if company_name is not None:
                updates.append("company_name = %s")
                params.append(company_name)
            if contact_name is not None:
                updates.append("contact_name = %s")
                params.append(contact_name)
            if email is not None:
                updates.append("email = %s")
                params.append(email)
            if phone is not None:
                updates.append("phone = %s")
                params.append(phone)
            if address is not None:
                updates.append("address = %s")
                params.append(address)
            if city is not None:
                updates.append("city = %s")
                params.append(city)
            if state is not None:
                updates.append("state = %s")
                params.append(state)
            if country is not None:
                updates.append("country = %s")
                params.append(country)
            if postal_code is not None:
                updates.append("postal_code = %s")
                params.append(postal_code)
            if niche_id is not None:
                updates.append("niche_id = %s")
                params.append(str(niche_id))
            if status is not None:
                updates.append("status = %s")
                params.append(status)
            if notes is not None:
                updates.append("notes = %s")
                params.append(notes)
            if assigned_to is not None:
                updates.append("assigned_to = %s")
                params.append(str(assigned_to))
            if source is not None:
                updates.append("source = %s")
                params.append(source)
            if project_deadline is not None:
                updates.append("project_deadline = %s")
                params.append(project_deadline)

            if not updates:
                return self.get_by_id(client_id)

            params.append(str(client_id))

            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE clients
                    SET {", ".join(updates)}
                    WHERE id = %s
                    RETURNING id
                    """,
                    params,
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self.get_by_id(client_id)
                return None
        except Exception as e:
            print(f"ERROR [ClientRepository]: Failed to update client: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def delete(self, client_id: UUID) -> bool:
        """Delete a client (soft delete)."""
        result = self.update(client_id, status="inactive")
        return result is not None

    def _row_to_dict_with_niche(self, row: tuple) -> Dict[str, Any]:
        return {
            "id": row[0],
            "company_name": row[1],
            "contact_name": row[2],
            "email": row[3],
            "phone": row[4],
            "address": row[5],
            "city": row[6],
            "state": row[7],
            "country": row[8],
            "postal_code": row[9],
            "niche_id": row[10],
            "status": row[11],
            "notes": row[12],
            "created_at": row[13],
            "updated_at": row[14],
            "niche_name": row[15] if len(row) > 15 else None,
            "assigned_to": row[16] if len(row) > 16 else None,
            "source": row[17] if len(row) > 17 else None,
            "project_deadline": row[18] if len(row) > 18 else None,
            "assigned_to_name": row[19] if len(row) > 19 else None,
        }

    def get_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all clients with a specific status for pipeline view."""
        conn = get_database_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT c.id, c.company_name, c.contact_name, c.email, c.phone,
                           c.address, c.city, c.state, c.country, c.postal_code,
                           c.niche_id, c.status, c.notes, c.created_at, c.updated_at,
                           n.name as niche_name,
                           c.assigned_to, c.source, c.project_deadline,
                           u.first_name || ' ' || u.last_name as assigned_to_name
                    FROM clients c
                    LEFT JOIN niches n ON c.niche_id = n.id
                    LEFT JOIN users u ON c.assigned_to = u.id
                    WHERE c.status = %s
                    ORDER BY c.company_name
                    """,
                    (status,),
                )
                rows = cur.fetchall()
                return [self._row_to_dict_with_niche(row) for row in rows]
        except Exception as e:
            print(f"ERROR [ClientRepository]: Failed to get clients by status: {e}")
            return []
        finally:
            close_database_connection(conn)

    def create_status_history(
        self,
        client_id: UUID,
        old_status: Optional[str],
        new_status: str,
        notes: Optional[str] = None,
        changed_by: Optional[UUID] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a status history record."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO client_status_history (
                        client_id, old_status, new_status, notes, changed_by
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, client_id, old_status, new_status, notes,
                              changed_by, created_at
                    """,
                    (
                        str(client_id),
                        old_status,
                        new_status,
                        notes,
                        str(changed_by) if changed_by else None,
                    ),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "client_id": row[1],
                        "old_status": row[2],
                        "new_status": row[3],
                        "notes": row[4],
                        "changed_by": row[5],
                        "changed_by_name": None,
                        "created_at": row[6],
                    }
                return None
        except Exception as e:
            print(f"ERROR [ClientRepository]: Failed to create status history: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def get_status_history(self, client_id: UUID) -> List[Dict[str, Any]]:
        """Get status change history for a client."""
        conn = get_database_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT h.id, h.client_id, h.old_status, h.new_status, h.notes,
                           h.changed_by, h.created_at,
                           u.first_name || ' ' || u.last_name as changed_by_name
                    FROM client_status_history h
                    LEFT JOIN users u ON h.changed_by = u.id
                    WHERE h.client_id = %s
                    ORDER BY h.created_at DESC
                    """,
                    (str(client_id),),
                )
                rows = cur.fetchall()
                return [
                    {
                        "id": row[0],
                        "client_id": row[1],
                        "old_status": row[2],
                        "new_status": row[3],
                        "notes": row[4],
                        "changed_by": row[5],
                        "created_at": row[6],
                        "changed_by_name": row[7],
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"ERROR [ClientRepository]: Failed to get status history: {e}")
            return []
        finally:
            close_database_connection(conn)

    def get_quotation_summary(self, client_id: UUID) -> Dict[str, Any]:
        """Get quotation summary for a client."""
        conn = get_database_connection()
        if not conn:
            return {
                "total_quotations": 0,
                "draft_count": 0,
                "sent_count": 0,
                "accepted_count": 0,
                "rejected_count": 0,
                "expired_count": 0,
                "total_value": Decimal("0.00"),
            }

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        COUNT(*) as total_quotations,
                        COUNT(*) FILTER (WHERE status = 'draft') as draft_count,
                        COUNT(*) FILTER (WHERE status = 'sent') as sent_count,
                        COUNT(*) FILTER (WHERE status = 'accepted') as accepted_count,
                        COUNT(*) FILTER (WHERE status = 'rejected') as rejected_count,
                        COUNT(*) FILTER (WHERE status = 'expired') as expired_count,
                        COALESCE(SUM(grand_total), 0) as total_value
                    FROM quotations
                    WHERE client_id = %s
                    """,
                    (str(client_id),),
                )
                row = cur.fetchone()

                if row:
                    return {
                        "total_quotations": row[0],
                        "draft_count": row[1],
                        "sent_count": row[2],
                        "accepted_count": row[3],
                        "rejected_count": row[4],
                        "expired_count": row[5],
                        "total_value": row[6] or Decimal("0.00"),
                    }
                return {
                    "total_quotations": 0,
                    "draft_count": 0,
                    "sent_count": 0,
                    "accepted_count": 0,
                    "rejected_count": 0,
                    "expired_count": 0,
                    "total_value": Decimal("0.00"),
                }
        except Exception as e:
            print(f"ERROR [ClientRepository]: Failed to get quotation summary: {e}")
            return {
                "total_quotations": 0,
                "draft_count": 0,
                "sent_count": 0,
                "accepted_count": 0,
                "rejected_count": 0,
                "expired_count": 0,
                "total_value": Decimal("0.00"),
            }
        finally:
            close_database_connection(conn)

    def has_active_quotations(self, client_id: UUID) -> bool:
        """Check if client has any non-draft, non-expired quotations."""
        conn = get_database_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*) FROM quotations
                    WHERE client_id = %s
                    AND status IN ('sent', 'accepted')
                    """,
                    (str(client_id),),
                )
                row = cur.fetchone()
                return row[0] > 0 if row else False
        except Exception as e:
            print(f"ERROR [ClientRepository]: Failed to check active quotations: {e}")
            return False
        finally:
            close_database_connection(conn)

    def search(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search clients by company name, contact name, or email."""
        conn = get_database_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cur:
                search_pattern = f"%{query}%"
                cur.execute(
                    """
                    SELECT c.id, c.company_name, c.contact_name, c.email, c.phone,
                           c.address, c.city, c.state, c.country, c.postal_code,
                           c.niche_id, c.status, c.notes, c.created_at, c.updated_at,
                           n.name as niche_name,
                           c.assigned_to, c.source, c.project_deadline,
                           u.first_name || ' ' || u.last_name as assigned_to_name
                    FROM clients c
                    LEFT JOIN niches n ON c.niche_id = n.id
                    LEFT JOIN users u ON c.assigned_to = u.id
                    WHERE c.company_name ILIKE %s
                       OR c.contact_name ILIKE %s
                       OR c.email ILIKE %s
                    ORDER BY c.company_name
                    LIMIT %s
                    """,
                    (search_pattern, search_pattern, search_pattern, limit),
                )
                rows = cur.fetchall()
                return [self._row_to_dict_with_niche(row) for row in rows]
        except Exception as e:
            print(f"ERROR [ClientRepository]: Failed to search clients: {e}")
            return []
        finally:
            close_database_connection(conn)


# =============================================================================
# FREIGHT RATE REPOSITORY
# =============================================================================


class FreightRateRepository:
    """Data access layer for freight_rates table."""

    def create(
        self,
        origin: str,
        destination: str,
        incoterm: str = "FOB",
        rate_per_kg: Optional[Decimal] = None,
        rate_per_cbm: Optional[Decimal] = None,
        minimum_charge: Decimal = Decimal("0.00"),
        transit_days: Optional[int] = None,
        is_active: bool = True,
        valid_from: Optional[str] = None,
        valid_until: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a new freight rate."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO freight_rates (
                        origin, destination, incoterm, rate_per_kg, rate_per_cbm,
                        minimum_charge, transit_days, is_active, valid_from, valid_until, notes
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, origin, destination, incoterm, rate_per_kg, rate_per_cbm,
                              minimum_charge, transit_days, is_active, valid_from, valid_until,
                              notes, created_at, updated_at
                    """,
                    (
                        origin,
                        destination,
                        incoterm,
                        rate_per_kg,
                        rate_per_cbm,
                        minimum_charge,
                        transit_days,
                        is_active,
                        valid_from,
                        valid_until,
                        notes,
                    ),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [FreightRateRepository]: Failed to create freight rate: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def get_by_id(self, freight_rate_id: UUID) -> Optional[Dict[str, Any]]:
        """Get freight rate by UUID."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, origin, destination, incoterm, rate_per_kg, rate_per_cbm,
                           minimum_charge, transit_days, is_active, valid_from, valid_until,
                           notes, created_at, updated_at
                    FROM freight_rates
                    WHERE id = %s
                    """,
                    (str(freight_rate_id),),
                )
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [FreightRateRepository]: Failed to get freight rate: {e}")
            return None
        finally:
            close_database_connection(conn)

    def get_all(
        self,
        page: int = 1,
        limit: int = 20,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        incoterm: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all freight rates with pagination."""
        conn = get_database_connection()
        if not conn:
            return [], 0

        try:
            with conn.cursor() as cur:
                conditions = []
                params: List[Any] = []

                if origin:
                    conditions.append("origin ILIKE %s")
                    params.append(f"%{origin}%")
                if destination:
                    conditions.append("destination ILIKE %s")
                    params.append(f"%{destination}%")
                if incoterm:
                    conditions.append("incoterm = %s")
                    params.append(incoterm)
                if is_active is not None:
                    conditions.append("is_active = %s")
                    params.append(is_active)

                where_clause = (
                    "WHERE " + " AND ".join(conditions) if conditions else ""
                )

                cur.execute(
                    f"SELECT COUNT(*) FROM freight_rates {where_clause}",
                    params,
                )
                total = cur.fetchone()[0]

                offset = (page - 1) * limit
                params.extend([limit, offset])

                cur.execute(
                    f"""
                    SELECT id, origin, destination, incoterm, rate_per_kg, rate_per_cbm,
                           minimum_charge, transit_days, is_active, valid_from, valid_until,
                           notes, created_at, updated_at
                    FROM freight_rates
                    {where_clause}
                    ORDER BY origin, destination
                    LIMIT %s OFFSET %s
                    """,
                    params,
                )
                rows = cur.fetchall()

                items = [self._row_to_dict(row) for row in rows]
                return items, total
        except Exception as e:
            print(f"ERROR [FreightRateRepository]: Failed to get freight rates: {e}")
            return [], 0
        finally:
            close_database_connection(conn)

    def update(
        self,
        freight_rate_id: UUID,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        incoterm: Optional[str] = None,
        rate_per_kg: Optional[Decimal] = None,
        rate_per_cbm: Optional[Decimal] = None,
        minimum_charge: Optional[Decimal] = None,
        transit_days: Optional[int] = None,
        is_active: Optional[bool] = None,
        valid_from: Optional[str] = None,
        valid_until: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update a freight rate."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            updates = []
            params: List[Any] = []

            if origin is not None:
                updates.append("origin = %s")
                params.append(origin)
            if destination is not None:
                updates.append("destination = %s")
                params.append(destination)
            if incoterm is not None:
                updates.append("incoterm = %s")
                params.append(incoterm)
            if rate_per_kg is not None:
                updates.append("rate_per_kg = %s")
                params.append(rate_per_kg)
            if rate_per_cbm is not None:
                updates.append("rate_per_cbm = %s")
                params.append(rate_per_cbm)
            if minimum_charge is not None:
                updates.append("minimum_charge = %s")
                params.append(minimum_charge)
            if transit_days is not None:
                updates.append("transit_days = %s")
                params.append(transit_days)
            if is_active is not None:
                updates.append("is_active = %s")
                params.append(is_active)
            if valid_from is not None:
                updates.append("valid_from = %s")
                params.append(valid_from)
            if valid_until is not None:
                updates.append("valid_until = %s")
                params.append(valid_until)
            if notes is not None:
                updates.append("notes = %s")
                params.append(notes)

            if not updates:
                return self.get_by_id(freight_rate_id)

            params.append(str(freight_rate_id))

            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE freight_rates
                    SET {", ".join(updates)}
                    WHERE id = %s
                    RETURNING id, origin, destination, incoterm, rate_per_kg, rate_per_cbm,
                              minimum_charge, transit_days, is_active, valid_from, valid_until,
                              notes, created_at, updated_at
                    """,
                    params,
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [FreightRateRepository]: Failed to update freight rate: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def delete(self, freight_rate_id: UUID) -> bool:
        """Delete a freight rate (soft delete)."""
        result = self.update(freight_rate_id, is_active=False)
        return result is not None

    def _row_to_dict(self, row: tuple) -> Dict[str, Any]:
        return {
            "id": row[0],
            "origin": row[1],
            "destination": row[2],
            "incoterm": row[3],
            "rate_per_kg": row[4],
            "rate_per_cbm": row[5],
            "minimum_charge": row[6],
            "transit_days": row[7],
            "is_active": row[8],
            "valid_from": row[9],
            "valid_until": row[10],
            "notes": row[11],
            "created_at": row[12],
            "updated_at": row[13],
        }


# =============================================================================
# PRICING SETTINGS REPOSITORY
# =============================================================================


class PricingSettingsRepository:
    """Data access layer for pricing_settings table."""

    def create(
        self,
        setting_key: str,
        setting_value: Decimal,
        description: Optional[str] = None,
        is_percentage: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Create a new pricing setting."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO pricing_settings (setting_key, setting_value, description, is_percentage)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, setting_key, setting_value, description, is_percentage,
                              created_at, updated_at
                    """,
                    (setting_key, setting_value, description, is_percentage),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [PricingSettingsRepository]: Failed to create setting: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def get_by_key(self, setting_key: str) -> Optional[Dict[str, Any]]:
        """Get pricing setting by key."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, setting_key, setting_value, description, is_percentage,
                           created_at, updated_at
                    FROM pricing_settings
                    WHERE setting_key = %s
                    """,
                    (setting_key,),
                )
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [PricingSettingsRepository]: Failed to get setting: {e}")
            return None
        finally:
            close_database_connection(conn)

    def get_all(self) -> List[Dict[str, Any]]:
        """Get all pricing settings."""
        conn = get_database_connection()
        if not conn:
            return []

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, setting_key, setting_value, description, is_percentage,
                           created_at, updated_at
                    FROM pricing_settings
                    ORDER BY setting_key
                    """
                )
                rows = cur.fetchall()

                return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            print(f"ERROR [PricingSettingsRepository]: Failed to get settings: {e}")
            return []
        finally:
            close_database_connection(conn)

    def update(
        self,
        setting_key: str,
        setting_value: Optional[Decimal] = None,
        description: Optional[str] = None,
        is_percentage: Optional[bool] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update a pricing setting."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            updates = []
            params: List[Any] = []

            if setting_value is not None:
                updates.append("setting_value = %s")
                params.append(setting_value)
            if description is not None:
                updates.append("description = %s")
                params.append(description)
            if is_percentage is not None:
                updates.append("is_percentage = %s")
                params.append(is_percentage)

            if not updates:
                return self.get_by_key(setting_key)

            params.append(setting_key)

            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE pricing_settings
                    SET {", ".join(updates)}
                    WHERE setting_key = %s
                    RETURNING id, setting_key, setting_value, description, is_percentage,
                              created_at, updated_at
                    """,
                    params,
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [PricingSettingsRepository]: Failed to update setting: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def delete(self, setting_key: str) -> bool:
        """Delete a pricing setting (hard delete)."""
        conn = get_database_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM pricing_settings WHERE setting_key = %s RETURNING id",
                    (setting_key,),
                )
                conn.commit()
                return cur.fetchone() is not None
        except Exception as e:
            print(f"ERROR [PricingSettingsRepository]: Failed to delete setting: {e}")
            conn.rollback()
            return False
        finally:
            close_database_connection(conn)

    def _row_to_dict(self, row: tuple) -> Dict[str, Any]:
        return {
            "id": row[0],
            "setting_key": row[1],
            "setting_value": row[2],
            "description": row[3],
            "is_percentage": row[4],
            "created_at": row[5],
            "updated_at": row[6],
        }


# =============================================================================
# QUOTATION REPOSITORY
# =============================================================================


class QuotationRepository:
    """Data access layer for quotations table."""

    def create(
        self,
        client_id: UUID,
        quotation_number: Optional[str] = None,
        status: str = "draft",
        incoterm: str = "FOB",
        currency: str = "USD",
        freight_cost: Decimal = Decimal("0.00"),
        insurance_cost: Decimal = Decimal("0.00"),
        other_costs: Decimal = Decimal("0.00"),
        discount_percent: Decimal = Decimal("0.00"),
        notes: Optional[str] = None,
        terms_and_conditions: Optional[str] = None,
        valid_from: Optional[str] = None,
        valid_until: Optional[str] = None,
        created_by: Optional[UUID] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a new quotation."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                if not quotation_number:
                    cur.execute(
                        "SELECT COALESCE(MAX(CAST(SUBSTRING(quotation_number FROM 4) AS INTEGER)), 0) + 1 FROM quotations WHERE quotation_number LIKE 'QT-%'"
                    )
                    next_num = cur.fetchone()[0]
                    quotation_number = f"QT-{next_num:06d}"

                cur.execute(
                    """
                    INSERT INTO quotations (
                        quotation_number, client_id, status, incoterm, currency,
                        freight_cost, insurance_cost, other_costs, discount_percent,
                        notes, terms_and_conditions, valid_from, valid_until, created_by
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        quotation_number,
                        str(client_id),
                        status,
                        incoterm,
                        currency,
                        freight_cost,
                        insurance_cost,
                        other_costs,
                        discount_percent,
                        notes,
                        terms_and_conditions,
                        valid_from,
                        valid_until,
                        str(created_by) if created_by else None,
                    ),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self.get_by_id(row[0])
                return None
        except Exception as e:
            print(f"ERROR [QuotationRepository]: Failed to create quotation: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def get_by_id(self, quotation_id: UUID) -> Optional[Dict[str, Any]]:
        """Get quotation by UUID with items."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT q.id, q.quotation_number, q.client_id, q.status, q.incoterm,
                           q.currency, q.subtotal, q.freight_cost, q.insurance_cost,
                           q.other_costs, q.total, q.discount_percent, q.discount_amount,
                           q.grand_total, q.notes, q.terms_and_conditions, q.valid_from,
                           q.valid_until, q.created_by, q.created_at, q.updated_at,
                           c.company_name as client_name
                    FROM quotations q
                    LEFT JOIN clients c ON q.client_id = c.id
                    WHERE q.id = %s
                    """,
                    (str(quotation_id),),
                )
                row = cur.fetchone()

                if row:
                    quotation = self._row_to_dict_with_client(row)
                    quotation["items"] = self._get_quotation_items(cur, quotation_id)
                    quotation["item_count"] = len(quotation["items"])
                    return quotation
                return None
        except Exception as e:
            print(f"ERROR [QuotationRepository]: Failed to get quotation: {e}")
            return None
        finally:
            close_database_connection(conn)

    def get_by_client(
        self,
        client_id: UUID,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get quotations for a client."""
        return self.get_all(page=page, limit=limit, client_id=client_id)

    def get_all(
        self,
        page: int = 1,
        limit: int = 20,
        client_id: Optional[UUID] = None,
        status: Optional[str] = None,
        created_by: Optional[UUID] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all quotations with pagination and filters."""
        conn = get_database_connection()
        if not conn:
            return [], 0

        try:
            with conn.cursor() as cur:
                conditions = []
                params: List[Any] = []

                if client_id:
                    conditions.append("q.client_id = %s")
                    params.append(str(client_id))
                if status:
                    conditions.append("q.status = %s")
                    params.append(status)
                if created_by:
                    conditions.append("q.created_by = %s")
                    params.append(str(created_by))
                if date_from:
                    conditions.append("q.created_at >= %s")
                    params.append(date_from)
                if date_to:
                    conditions.append("q.created_at <= %s")
                    params.append(date_to)
                if search:
                    conditions.append(
                        "(q.quotation_number ILIKE %s OR c.company_name ILIKE %s)"
                    )
                    search_pattern = f"%{search}%"
                    params.extend([search_pattern, search_pattern])

                where_clause = (
                    "WHERE " + " AND ".join(conditions) if conditions else ""
                )

                cur.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM quotations q
                    LEFT JOIN clients c ON q.client_id = c.id
                    {where_clause}
                    """,
                    params,
                )
                total = cur.fetchone()[0]

                offset = (page - 1) * limit
                params.extend([limit, offset])

                cur.execute(
                    f"""
                    SELECT q.id, q.quotation_number, q.client_id, q.status, q.incoterm,
                           q.currency, q.subtotal, q.freight_cost, q.insurance_cost,
                           q.other_costs, q.total, q.discount_percent, q.discount_amount,
                           q.grand_total, q.notes, q.terms_and_conditions, q.valid_from,
                           q.valid_until, q.created_by, q.created_at, q.updated_at,
                           c.company_name as client_name
                    FROM quotations q
                    LEFT JOIN clients c ON q.client_id = c.id
                    {where_clause}
                    ORDER BY q.created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    params,
                )
                rows = cur.fetchall()

                items = []
                for row in rows:
                    quotation = self._row_to_dict_with_client(row)
                    quotation["items"] = self._get_quotation_items(
                        cur, quotation["id"]
                    )
                    quotation["item_count"] = len(quotation["items"])
                    items.append(quotation)

                return items, total
        except Exception as e:
            print(f"ERROR [QuotationRepository]: Failed to get quotations: {e}")
            return [], 0
        finally:
            close_database_connection(conn)

    def update_status(
        self, quotation_id: UUID, status: str
    ) -> Optional[Dict[str, Any]]:
        """Update quotation status."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE quotations
                    SET status = %s
                    WHERE id = %s
                    RETURNING id
                    """,
                    (status, str(quotation_id)),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self.get_by_id(quotation_id)
                return None
        except Exception as e:
            print(f"ERROR [QuotationRepository]: Failed to update status: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def recalculate_totals(self, quotation_id: UUID) -> Optional[Dict[str, Any]]:
        """Recalculate quotation totals from items."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COALESCE(SUM(line_total), 0)
                    FROM quotation_items
                    WHERE quotation_id = %s
                    """,
                    (str(quotation_id),),
                )
                subtotal = cur.fetchone()[0]

                cur.execute(
                    """
                    SELECT freight_cost, insurance_cost, other_costs, discount_percent
                    FROM quotations
                    WHERE id = %s
                    """,
                    (str(quotation_id),),
                )
                row = cur.fetchone()
                if not row:
                    return None

                freight_cost = row[0] or Decimal("0.00")
                insurance_cost = row[1] or Decimal("0.00")
                other_costs = row[2] or Decimal("0.00")
                discount_percent = row[3] or Decimal("0.00")

                total = subtotal + freight_cost + insurance_cost + other_costs
                discount_amount = total * discount_percent / 100
                grand_total = total - discount_amount

                cur.execute(
                    """
                    UPDATE quotations
                    SET subtotal = %s, total = %s, discount_amount = %s, grand_total = %s
                    WHERE id = %s
                    RETURNING id
                    """,
                    (subtotal, total, discount_amount, grand_total, str(quotation_id)),
                )
                conn.commit()

                return self.get_by_id(quotation_id)
        except Exception as e:
            print(f"ERROR [QuotationRepository]: Failed to recalculate totals: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def add_item(
        self,
        quotation_id: UUID,
        product_name: str,
        quantity: int = 1,
        unit_price: Decimal = Decimal("0.00"),
        product_id: Optional[UUID] = None,
        sku: Optional[str] = None,
        description: Optional[str] = None,
        unit_of_measure: str = "piece",
        unit_cost: Decimal = Decimal("0.00"),
        markup_percent: Decimal = Decimal("0.00"),
        tariff_percent: Decimal = Decimal("0.00"),
        tariff_amount: Decimal = Decimal("0.00"),
        freight_amount: Decimal = Decimal("0.00"),
        sort_order: int = 0,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Add an item to a quotation."""
        conn = get_database_connection()
        if not conn:
            return None

        try:
            line_total = quantity * unit_price + tariff_amount + freight_amount

            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO quotation_items (
                        quotation_id, product_id, sku, product_name, description,
                        quantity, unit_of_measure, unit_cost, unit_price, markup_percent,
                        tariff_percent, tariff_amount, freight_amount, line_total,
                        sort_order, notes
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, quotation_id, product_id, sku, product_name, description,
                              quantity, unit_of_measure, unit_cost, unit_price, markup_percent,
                              tariff_percent, tariff_amount, freight_amount, line_total,
                              sort_order, notes, created_at, updated_at
                    """,
                    (
                        str(quotation_id),
                        str(product_id) if product_id else None,
                        sku,
                        product_name,
                        description,
                        quantity,
                        unit_of_measure,
                        unit_cost,
                        unit_price,
                        markup_percent,
                        tariff_percent,
                        tariff_amount,
                        freight_amount,
                        line_total,
                        sort_order,
                        notes,
                    ),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    self.recalculate_totals(quotation_id)
                    return self._item_row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [QuotationRepository]: Failed to add item: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def remove_item(self, item_id: UUID) -> bool:
        """Remove an item from a quotation."""
        conn = get_database_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT quotation_id FROM quotation_items WHERE id = %s",
                    (str(item_id),),
                )
                row = cur.fetchone()
                quotation_id = row[0] if row else None

                cur.execute(
                    "DELETE FROM quotation_items WHERE id = %s RETURNING id",
                    (str(item_id),),
                )
                conn.commit()
                deleted = cur.fetchone() is not None

                if deleted and quotation_id:
                    self.recalculate_totals(quotation_id)

                return deleted
        except Exception as e:
            print(f"ERROR [QuotationRepository]: Failed to remove item: {e}")
            conn.rollback()
            return False
        finally:
            close_database_connection(conn)

    def _get_quotation_items(
        self, cur: Any, quotation_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get items for a quotation."""
        cur.execute(
            """
            SELECT id, quotation_id, product_id, sku, product_name, description,
                   quantity, unit_of_measure, unit_cost, unit_price, markup_percent,
                   tariff_percent, tariff_amount, freight_amount, line_total,
                   sort_order, notes, created_at, updated_at
            FROM quotation_items
            WHERE quotation_id = %s
            ORDER BY sort_order, created_at
            """,
            (str(quotation_id),),
        )
        rows = cur.fetchall()
        return [self._item_row_to_dict(row) for row in rows]

    def _row_to_dict_with_client(self, row: tuple) -> Dict[str, Any]:
        return {
            "id": row[0],
            "quotation_number": row[1],
            "client_id": row[2],
            "status": row[3],
            "incoterm": row[4],
            "currency": row[5],
            "subtotal": row[6],
            "freight_cost": row[7],
            "insurance_cost": row[8],
            "other_costs": row[9],
            "total": row[10],
            "discount_percent": row[11],
            "discount_amount": row[12],
            "grand_total": row[13],
            "notes": row[14],
            "terms_and_conditions": row[15],
            "valid_from": row[16],
            "valid_until": row[17],
            "created_by": row[18],
            "created_at": row[19],
            "updated_at": row[20],
            "client_name": row[21] if len(row) > 21 else None,
            "items": [],
            "item_count": 0,
        }

    def _item_row_to_dict(self, row: tuple) -> Dict[str, Any]:
        return {
            "id": row[0],
            "quotation_id": row[1],
            "product_id": row[2],
            "sku": row[3],
            "product_name": row[4],
            "description": row[5],
            "quantity": row[6],
            "unit_of_measure": row[7],
            "unit_cost": row[8],
            "unit_price": row[9],
            "markup_percent": row[10],
            "tariff_percent": row[11],
            "tariff_amount": row[12],
            "freight_amount": row[13],
            "line_total": row[14],
            "sort_order": row[15],
            "notes": row[16],
            "created_at": row[17],
            "updated_at": row[18],
        }


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def calculate_pagination(total: int, page: int, limit: int) -> Dict[str, int]:
    """Calculate pagination metadata."""
    pages = math.ceil(total / limit) if limit > 0 else 0
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
    }


# =============================================================================
# SINGLETON INSTANCES
# =============================================================================

niche_repository = NicheRepository()
category_repository = CategoryRepository()
tag_repository = TagRepository()
hs_code_repository = HSCodeRepository()
supplier_repository = SupplierRepository()
product_repository = ProductRepository()
portfolio_repository = PortfolioRepository()
client_repository = ClientRepository()
freight_rate_repository = FreightRateRepository()
pricing_settings_repository = PricingSettingsRepository()
quotation_repository = QuotationRepository()
