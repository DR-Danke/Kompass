"""Repository for supplier audits table."""

import json
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from app.config.database import close_database_connection, get_database_connection


class AuditRepository:
    """Data access layer for supplier_audits table."""

    def create(
        self,
        supplier_id: UUID,
        audit_type: str,
        document_url: str,
        document_name: Optional[str] = None,
        file_size_bytes: Optional[int] = None,
        audit_date: Optional[str] = None,
        inspector_name: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Create a new supplier audit record.

        Args:
            supplier_id: UUID of the supplier
            audit_type: Type of audit (factory_audit or container_inspection)
            document_url: URL of the uploaded document
            document_name: Optional name of the document
            file_size_bytes: Optional file size in bytes
            audit_date: Optional date of the audit
            inspector_name: Optional name of the inspector

        Returns:
            Audit dict if created, None if error
        """
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO supplier_audits (
                        supplier_id, audit_type, document_url, document_name,
                        file_size_bytes, audit_date, inspector_name, extraction_status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
                    RETURNING id, supplier_id, audit_type, document_url, document_name,
                              file_size_bytes, supplier_type, employee_count, factory_area_sqm,
                              production_lines_count, markets_served, certifications,
                              has_machinery_photos, positive_points, negative_points,
                              products_verified, audit_date, inspector_name, extraction_status,
                              extraction_raw_response, extracted_at, ai_classification,
                              ai_classification_reason, manual_classification, classification_notes,
                              created_at, updated_at
                    """,
                    (
                        str(supplier_id),
                        audit_type,
                        document_url,
                        document_name,
                        file_size_bytes,
                        audit_date,
                        inspector_name,
                    ),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [AuditRepository]: Failed to create audit: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def get_by_id(self, audit_id: UUID) -> Optional[Dict[str, Any]]:
        """Get audit by UUID.

        Args:
            audit_id: UUID of the audit

        Returns:
            Audit dict if found, None otherwise
        """
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, supplier_id, audit_type, document_url, document_name,
                           file_size_bytes, supplier_type, employee_count, factory_area_sqm,
                           production_lines_count, markets_served, certifications,
                           has_machinery_photos, positive_points, negative_points,
                           products_verified, audit_date, inspector_name, extraction_status,
                           extraction_raw_response, extracted_at, ai_classification,
                           ai_classification_reason, manual_classification, classification_notes,
                           created_at, updated_at
                    FROM supplier_audits
                    WHERE id = %s
                    """,
                    (str(audit_id),),
                )
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [AuditRepository]: Failed to get audit by id: {e}")
            return None
        finally:
            close_database_connection(conn)

    def get_by_supplier_id(
        self,
        supplier_id: UUID,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get all audits for a supplier with pagination.

        Args:
            supplier_id: UUID of the supplier
            page: Page number (1-indexed)
            limit: Number of items per page

        Returns:
            Tuple of (list of audits, total count)
        """
        conn = get_database_connection()
        if not conn:
            return [], 0

        try:
            with conn.cursor() as cur:
                # Get total count
                cur.execute(
                    "SELECT COUNT(*) FROM supplier_audits WHERE supplier_id = %s",
                    (str(supplier_id),),
                )
                total = cur.fetchone()[0]

                # Get paginated results
                offset = (page - 1) * limit
                cur.execute(
                    """
                    SELECT id, supplier_id, audit_type, document_url, document_name,
                           file_size_bytes, supplier_type, employee_count, factory_area_sqm,
                           production_lines_count, markets_served, certifications,
                           has_machinery_photos, positive_points, negative_points,
                           products_verified, audit_date, inspector_name, extraction_status,
                           extraction_raw_response, extracted_at, ai_classification,
                           ai_classification_reason, manual_classification, classification_notes,
                           created_at, updated_at
                    FROM supplier_audits
                    WHERE supplier_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (str(supplier_id), limit, offset),
                )
                rows = cur.fetchall()

                items = [self._row_to_dict(row) for row in rows]
                return items, total
        except Exception as e:
            print(f"ERROR [AuditRepository]: Failed to get audits by supplier: {e}")
            return [], 0
        finally:
            close_database_connection(conn)

    def update_extraction_status(
        self,
        audit_id: UUID,
        status: str,
    ) -> Optional[Dict[str, Any]]:
        """Update the extraction status of an audit.

        Args:
            audit_id: UUID of the audit
            status: New extraction status

        Returns:
            Updated audit dict if successful, None otherwise
        """
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE supplier_audits
                    SET extraction_status = %s, updated_at = NOW()
                    WHERE id = %s
                    RETURNING id, supplier_id, audit_type, document_url, document_name,
                              file_size_bytes, supplier_type, employee_count, factory_area_sqm,
                              production_lines_count, markets_served, certifications,
                              has_machinery_photos, positive_points, negative_points,
                              products_verified, audit_date, inspector_name, extraction_status,
                              extraction_raw_response, extracted_at, ai_classification,
                              ai_classification_reason, manual_classification, classification_notes,
                              created_at, updated_at
                    """,
                    (status, str(audit_id)),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [AuditRepository]: Failed to update extraction status: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def update_extraction_results(
        self,
        audit_id: UUID,
        supplier_type: Optional[str] = None,
        employee_count: Optional[int] = None,
        factory_area_sqm: Optional[int] = None,
        production_lines_count: Optional[int] = None,
        markets_served: Optional[dict] = None,
        certifications: Optional[List[str]] = None,
        has_machinery_photos: bool = False,
        positive_points: Optional[List[str]] = None,
        negative_points: Optional[List[str]] = None,
        products_verified: Optional[List[str]] = None,
        audit_date: Optional[str] = None,
        inspector_name: Optional[str] = None,
        extraction_status: str = "completed",
        extraction_raw_response: Optional[dict] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update extraction results for an audit.

        Args:
            audit_id: UUID of the audit
            supplier_type: Type of supplier (manufacturer/trader/unknown)
            employee_count: Number of employees
            factory_area_sqm: Factory area in square meters
            production_lines_count: Number of production lines
            markets_served: Dict of market percentages
            certifications: List of certifications
            has_machinery_photos: Whether audit has machinery photos
            positive_points: List of positive points
            negative_points: List of negative points
            products_verified: List of verified products
            audit_date: Date of the audit
            inspector_name: Name of the inspector
            extraction_status: New extraction status
            extraction_raw_response: Raw AI response

        Returns:
            Updated audit dict if successful, None otherwise
        """
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE supplier_audits
                    SET supplier_type = %s,
                        employee_count = %s,
                        factory_area_sqm = %s,
                        production_lines_count = %s,
                        markets_served = %s,
                        certifications = %s,
                        has_machinery_photos = %s,
                        positive_points = %s,
                        negative_points = %s,
                        products_verified = %s,
                        audit_date = COALESCE(%s, audit_date),
                        inspector_name = COALESCE(%s, inspector_name),
                        extraction_status = %s,
                        extraction_raw_response = %s,
                        extracted_at = NOW(),
                        updated_at = NOW()
                    WHERE id = %s
                    RETURNING id, supplier_id, audit_type, document_url, document_name,
                              file_size_bytes, supplier_type, employee_count, factory_area_sqm,
                              production_lines_count, markets_served, certifications,
                              has_machinery_photos, positive_points, negative_points,
                              products_verified, audit_date, inspector_name, extraction_status,
                              extraction_raw_response, extracted_at, ai_classification,
                              ai_classification_reason, manual_classification, classification_notes,
                              created_at, updated_at
                    """,
                    (
                        supplier_type,
                        employee_count,
                        factory_area_sqm,
                        production_lines_count,
                        json.dumps(markets_served) if markets_served else None,
                        certifications,
                        has_machinery_photos,
                        positive_points,
                        negative_points,
                        products_verified,
                        audit_date,
                        inspector_name,
                        extraction_status,
                        json.dumps(extraction_raw_response) if extraction_raw_response else None,
                        str(audit_id),
                    ),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [AuditRepository]: Failed to update extraction results: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def reset_extraction(self, audit_id: UUID) -> Optional[Dict[str, Any]]:
        """Reset extraction fields for an audit to allow reprocessing.

        Args:
            audit_id: UUID of the audit

        Returns:
            Updated audit dict if successful, None otherwise
        """
        conn = get_database_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE supplier_audits
                    SET supplier_type = NULL,
                        employee_count = NULL,
                        factory_area_sqm = NULL,
                        production_lines_count = NULL,
                        markets_served = NULL,
                        certifications = NULL,
                        has_machinery_photos = false,
                        positive_points = NULL,
                        negative_points = NULL,
                        products_verified = NULL,
                        extraction_status = 'pending',
                        extraction_raw_response = NULL,
                        extracted_at = NULL,
                        ai_classification = NULL,
                        ai_classification_reason = NULL,
                        updated_at = NOW()
                    WHERE id = %s
                    RETURNING id, supplier_id, audit_type, document_url, document_name,
                              file_size_bytes, supplier_type, employee_count, factory_area_sqm,
                              production_lines_count, markets_served, certifications,
                              has_machinery_photos, positive_points, negative_points,
                              products_verified, audit_date, inspector_name, extraction_status,
                              extraction_raw_response, extracted_at, ai_classification,
                              ai_classification_reason, manual_classification, classification_notes,
                              created_at, updated_at
                    """,
                    (str(audit_id),),
                )
                conn.commit()
                row = cur.fetchone()

                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            print(f"ERROR [AuditRepository]: Failed to reset extraction: {e}")
            conn.rollback()
            return None
        finally:
            close_database_connection(conn)

    def delete(self, audit_id: UUID) -> bool:
        """Delete an audit record.

        Args:
            audit_id: UUID of the audit

        Returns:
            True if deleted, False otherwise
        """
        conn = get_database_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM supplier_audits WHERE id = %s RETURNING id",
                    (str(audit_id),),
                )
                conn.commit()
                return cur.fetchone() is not None
        except Exception as e:
            print(f"ERROR [AuditRepository]: Failed to delete audit: {e}")
            conn.rollback()
            return False
        finally:
            close_database_connection(conn)

    def _row_to_dict(self, row: tuple) -> Dict[str, Any]:
        """Convert a database row to a dictionary.

        Args:
            row: Database row tuple

        Returns:
            Dictionary with audit fields
        """
        # Parse markets_served from JSON string if needed
        markets_served = row[10]
        if isinstance(markets_served, str):
            try:
                markets_served = json.loads(markets_served)
            except (json.JSONDecodeError, TypeError):
                markets_served = None

        # Parse extraction_raw_response from JSON string if needed
        extraction_raw_response = row[19]
        if isinstance(extraction_raw_response, str):
            try:
                extraction_raw_response = json.loads(extraction_raw_response)
            except (json.JSONDecodeError, TypeError):
                extraction_raw_response = None

        return {
            "id": row[0],
            "supplier_id": row[1],
            "audit_type": row[2],
            "document_url": row[3],
            "document_name": row[4],
            "file_size_bytes": row[5],
            "supplier_type": row[6],
            "employee_count": row[7],
            "factory_area_sqm": row[8],
            "production_lines_count": row[9],
            "markets_served": markets_served,
            "certifications": row[11],
            "has_machinery_photos": row[12] or False,
            "positive_points": row[13],
            "negative_points": row[14],
            "products_verified": row[15],
            "audit_date": row[16],
            "inspector_name": row[17],
            "extraction_status": row[18],
            "extraction_raw_response": extraction_raw_response,
            "extracted_at": row[20],
            "ai_classification": row[21],
            "ai_classification_reason": row[22],
            "manual_classification": row[23],
            "classification_notes": row[24],
            "created_at": row[25],
            "updated_at": row[26],
        }


# Singleton instance
audit_repository = AuditRepository()
