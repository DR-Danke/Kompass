"""Repository for business_card_captures table."""

from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from app.config.database import close_database_connection, get_database_connection


class BusinessCardCaptureRepository:
    """Data access layer for business_card_captures table."""

    _COLUMNS = """
        id, image_url, status,
        company_name, contact_name, contact_email, contact_phone,
        contact_wechat, website, address,
        supplier_id, fair_name, notes, captured_by,
        extraction_raw_response, created_at, updated_at
    """

    def create(
        self,
        image_url: str,
        fair_name: Optional[str] = None,
        notes: Optional[str] = None,
        captured_by: Optional[UUID] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a new business card capture record.

        Args:
            image_url: URL of the uploaded image
            fair_name: Optional trade fair name
            notes: Optional notes
            captured_by: Optional UUID of the user who captured

        Returns:
            Capture dict if created, None if error
        """
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO business_card_captures (
                        image_url, fair_name, notes, captured_by, status
                    )
                    VALUES (%s, %s, %s, %s, 'pending')
                    RETURNING {self._COLUMNS}
                    """,
                    (
                        image_url,
                        fair_name,
                        notes,
                        str(captured_by) if captured_by else None,
                    ),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [BusinessCardCaptureRepository]: Failed to create capture: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def get_by_id(self, capture_id: UUID) -> Optional[Dict[str, Any]]:
        """Get capture by UUID.

        Args:
            capture_id: UUID of the capture

        Returns:
            Capture dict if found, None otherwise
        """
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT {self._COLUMNS}
                    FROM business_card_captures
                    WHERE id = %s
                    """,
                    (str(capture_id),),
                )
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [BusinessCardCaptureRepository]: Failed to get capture by id: {e}")
            return None
        finally:
            close_database_connection(conn)

    def list_captures(
        self,
        status_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """List captures with optional status filter and pagination.

        Args:
            status_filter: Optional status to filter by
            limit: Number of items to return
            offset: Number of items to skip

        Returns:
            Tuple of (list of captures, total count)
        """
        conn = get_database_connection()
        if not conn:
            return [], 0

        try:
            with conn.cursor() as cur:
                where_clause = ""
                params: list = []

                if status_filter:
                    where_clause = "WHERE status = %s"
                    params.append(status_filter)

                # Get total count
                cur.execute(
                    f"SELECT COUNT(*) FROM business_card_captures {where_clause}",
                    params,
                )
                total = cur.fetchone()[0]

                # Get paginated results
                cur.execute(
                    f"""
                    SELECT {self._COLUMNS}
                    FROM business_card_captures
                    {where_clause}
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    params + [limit, offset],
                )
                rows = cur.fetchall()

                items = [self._row_to_dict(row) for row in rows]
                return items, total
        except Exception as e:
            print(f"ERROR [BusinessCardCaptureRepository]: Failed to list captures: {e}")
            return [], 0
        finally:
            close_database_connection(conn)

    def update(
        self,
        capture_id: UUID,
        updates: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Update a capture record with provided fields.

        Args:
            capture_id: UUID of the capture
            updates: Dictionary of field names to new values

        Returns:
            Updated capture dict if successful, None otherwise
        """
        if not updates:
            return self.get_by_id(capture_id)

        conn = get_database_connection()
        if not conn:
            return None

        try:
            # Build SET clause dynamically
            set_parts = []
            values = []
            for key, value in updates.items():
                set_parts.append(f"{key} = %s")
                values.append(value)

            set_clause = ", ".join(set_parts)
            values.append(str(capture_id))

            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE business_card_captures
                    SET {set_clause}, updated_at = NOW()
                    WHERE id = %s
                    RETURNING {self._COLUMNS}
                    """,
                    values,
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [BusinessCardCaptureRepository]: Failed to update capture: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def _row_to_dict(self, row: tuple) -> Dict[str, Any]:
        """Convert a database row to a dictionary.

        Args:
            row: Database row tuple

        Returns:
            Dictionary with capture fields
        """
        return {
            "id": row[0],
            "image_url": row[1],
            "status": row[2],
            "company_name": row[3],
            "contact_name": row[4],
            "contact_email": row[5],
            "contact_phone": row[6],
            "contact_wechat": row[7],
            "website": row[8],
            "address": row[9],
            "supplier_id": row[10],
            "fair_name": row[11],
            "notes": row[12],
            "captured_by": row[13],
            "extraction_raw_response": row[14],
            "created_at": row[15],
            "updated_at": row[16],
        }


# Singleton instance
business_card_repository = BusinessCardCaptureRepository()
