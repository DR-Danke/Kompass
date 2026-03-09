"""Service for business card capture operations."""

from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from app.repository.business_card_repository import business_card_repository


class BusinessCardService:
    """Business logic for business card capture operations."""

    def create_capture(
        self,
        image_url: str,
        fair_name: Optional[str] = None,
        notes: Optional[str] = None,
        captured_by: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Create a new business card capture.

        Args:
            image_url: URL of the uploaded image
            fair_name: Optional trade fair name
            notes: Optional notes
            captured_by: Optional UUID of the capturing user

        Returns:
            Capture dictionary

        Raises:
            ValueError: If creation fails
        """
        print(
            f"INFO [BusinessCardService]: Creating capture, "
            f"fair_name={fair_name}, captured_by={captured_by}"
        )

        result = business_card_repository.create(
            image_url=image_url,
            fair_name=fair_name,
            notes=notes,
            captured_by=captured_by,
        )

        if not result:
            raise ValueError("Failed to create business card capture record")

        print(f"INFO [BusinessCardService]: Created capture {result['id']}")
        return result

    def get_capture(self, capture_id: UUID) -> Dict[str, Any]:
        """Get a single capture by ID.

        Args:
            capture_id: UUID of the capture

        Returns:
            Capture dictionary

        Raises:
            ValueError: If capture not found
        """
        result = business_card_repository.get_by_id(capture_id)
        if not result:
            raise ValueError(f"Business card capture {capture_id} not found")
        return result

    def list_captures(
        self,
        status_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """List captures with optional filtering.

        Args:
            status_filter: Optional status to filter by
            limit: Number of items to return
            offset: Number of items to skip

        Returns:
            Tuple of (list of captures, total count)
        """
        print(
            f"INFO [BusinessCardService]: Listing captures, "
            f"status={status_filter}, limit={limit}, offset={offset}"
        )
        return business_card_repository.list_captures(
            status_filter=status_filter,
            limit=limit,
            offset=offset,
        )

    def update_capture(
        self,
        capture_id: UUID,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a capture record.

        Args:
            capture_id: UUID of the capture
            updates: Dictionary of field names to new values

        Returns:
            Updated capture dictionary

        Raises:
            ValueError: If update fails
        """
        print(f"INFO [BusinessCardService]: Updating capture {capture_id}")

        result = business_card_repository.update(capture_id, updates)
        if not result:
            raise ValueError(f"Failed to update business card capture {capture_id}")
        return result


# Singleton instance
business_card_service = BusinessCardService()
