"""Service for business card capture operations."""

import base64

import httpx

from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from app.repository.business_card_repository import business_card_repository
from app.services.extraction_service import extraction_service


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

    def approve_card(self, capture_id: UUID) -> Dict[str, Any]:
        """Approve a business card capture and create a supplier.

        Args:
            capture_id: UUID of the capture to approve

        Returns:
            SupplierFromCardResultDTO from supplier_service

        Raises:
            ValueError: If capture not found or status is not 'extracted'
        """
        from app.services.supplier_service import supplier_service

        capture = self.get_capture(capture_id)
        if capture["status"] != "extracted":
            raise ValueError(
                f"Cannot approve card with status '{capture['status']}'. "
                "Only 'extracted' captures can be approved."
            )

        print(f"INFO [BusinessCardService]: Approving card {capture_id}")
        result = supplier_service.create_supplier_from_card(capture_id)
        return result

    def reject_card(
        self,
        capture_id: UUID,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Reject a business card capture.

        Args:
            capture_id: UUID of the capture to reject
            reason: Optional rejection reason

        Returns:
            Updated capture dictionary

        Raises:
            ValueError: If capture not found or status is invalid
        """
        capture = self.get_capture(capture_id)
        allowed = ("extracted", "pending", "failed")
        if capture["status"] not in allowed:
            raise ValueError(
                f"Cannot reject card with status '{capture['status']}'. "
                f"Only {allowed} captures can be rejected."
            )

        print(f"INFO [BusinessCardService]: Rejecting card {capture_id}")

        updates: Dict[str, Any] = {"status": "rejected"}
        if reason:
            existing_notes = capture.get("notes") or ""
            if existing_notes:
                updates["notes"] = f"{existing_notes}\nRechazo: {reason}"
            else:
                updates["notes"] = f"Rechazo: {reason}"

        result = business_card_repository.update(capture_id, updates)
        if not result:
            raise ValueError(f"Failed to reject business card capture {capture_id}")
        return result

    def extract_card(self, capture_id: UUID) -> Dict[str, Any]:
        """Run AI extraction on a business card capture.

        Args:
            capture_id: UUID of the capture to extract

        Returns:
            Updated capture dictionary with extracted fields

        Raises:
            ValueError: If capture not found or status invalid
        """
        capture = self.get_capture(capture_id)
        status = capture["status"]

        if status not in ("pending", "failed"):
            raise ValueError(
                f"Cannot extract card with status '{status}'. "
                "Only 'pending' or 'failed' captures can be extracted."
            )

        # Set status to processing
        print(f"INFO [BusinessCardService]: Starting extraction for {capture_id}")
        business_card_repository.update(capture_id, {"status": "processing"})

        try:
            # Retrieve image data
            image_data = self._get_image_data(capture["image_url"])

            # Call AI extraction
            result = extraction_service.extract_business_card_data(image_data)

            # Build update dict from extraction result
            updates: Dict[str, Any] = {
                "status": "extracted",
                "company_name": result.get("company_name"),
                "contact_name": result.get("contact_name"),
                "contact_email": result.get("contact_email"),
                "contact_phone": result.get("contact_phone"),
                "contact_wechat": result.get("contact_wechat"),
                "website": result.get("website"),
                "address": result.get("address"),
                "extraction_raw_response": self._to_json(result),
            }

            # Flag for manual review when company_name is null
            if updates["company_name"] is None:
                existing_notes = capture.get("notes") or ""
                review_note = "Company name could not be determined — manual review required"
                if existing_notes:
                    updates["notes"] = f"{existing_notes}\n{review_note}"
                else:
                    updates["notes"] = review_note
                print(f"INFO [BusinessCardService]: Company name null for {capture_id}, flagged for manual review")

            updated = business_card_repository.update(capture_id, updates)
            if not updated:
                raise ValueError(f"Failed to update capture {capture_id} after extraction")

            print(f"INFO [BusinessCardService]: Extraction completed for {capture_id}")
            return updated

        except Exception as e:
            print(f"ERROR [BusinessCardService]: Extraction failed for {capture_id}: {e}")
            error_response = {"error": str(e)}
            business_card_repository.update(
                capture_id,
                {
                    "status": "failed",
                    "extraction_raw_response": self._to_json(error_response),
                },
            )
            raise

    def _get_image_data(self, image_url: str) -> bytes:
        """Retrieve image bytes from a URL or base64 data URI.

        Args:
            image_url: Either a base64 data URI or an HTTP URL

        Returns:
            Raw image bytes
        """
        if image_url.startswith("data:"):
            # base64 data URI — extract the base64 portion after the comma
            _, encoded = image_url.split(",", 1)
            return base64.b64decode(encoded)

        # HTTP(S) URL — download
        with httpx.Client(timeout=30) as client:
            response = client.get(image_url)
            response.raise_for_status()
            return response.content

    @staticmethod
    def _to_json(data: dict) -> str:
        """Serialize dict to JSON string for JSONB storage."""
        import json
        return json.dumps(data, ensure_ascii=False, default=str)


# Singleton instance
business_card_service = BusinessCardService()
