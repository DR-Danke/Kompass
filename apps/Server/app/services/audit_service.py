"""Service for supplier audit processing and AI extraction."""

import base64
import json
import math
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.config import get_settings
from app.models.kompass_dto import (
    AuditType,
    CertificationStatus,
    ExtractionStatus,
    PaginationDTO,
    SupplierAuditListResponseDTO,
    SupplierAuditResponseDTO,
    SupplierType,
)
from app.repository.audit_repository import audit_repository
from app.repository.kompass_repository import SupplierRepository


# Maximum number of pages to process from PDF for extraction
MAX_PDF_PAGES_TO_PROCESS = 20


class AuditService:
    """Service for handling supplier audit operations and AI extraction."""

    def __init__(self) -> None:
        """Initialize the audit service with AI clients."""
        self._anthropic_client = None
        self._openai_client = None
        self._settings = get_settings()

    def _get_anthropic_client(self):
        """Lazily initialize and return the Anthropic client."""
        if self._anthropic_client is None and self._settings.ANTHROPIC_API_KEY:
            try:
                import anthropic

                self._anthropic_client = anthropic.Anthropic(
                    api_key=self._settings.ANTHROPIC_API_KEY
                )
            except ImportError:
                print("WARN [AuditService]: anthropic package not installed")
        return self._anthropic_client

    def _get_openai_client(self):
        """Lazily initialize and return the OpenAI client."""
        if self._openai_client is None and self._settings.OPENAI_API_KEY:
            try:
                import openai

                self._openai_client = openai.OpenAI(
                    api_key=self._settings.OPENAI_API_KEY
                )
            except ImportError:
                print("WARN [AuditService]: openai package not installed")
        return self._openai_client

    def _is_ai_available(self) -> bool:
        """Check if any AI service is configured and available."""
        return bool(
            self._settings.ANTHROPIC_API_KEY or self._settings.OPENAI_API_KEY
        )

    def _get_preferred_ai_provider(self) -> str:
        """Get the preferred AI provider based on configuration."""
        provider = self._settings.EXTRACTION_AI_PROVIDER.lower()
        if provider == "anthropic" and self._settings.ANTHROPIC_API_KEY:
            return "anthropic"
        if provider == "openai" and self._settings.OPENAI_API_KEY:
            return "openai"
        # Fallback to whatever is available
        if self._settings.ANTHROPIC_API_KEY:
            return "anthropic"
        if self._settings.OPENAI_API_KEY:
            return "openai"
        return "none"

    def _build_audit_extraction_prompt(self) -> str:
        """Build the prompt for factory audit data extraction."""
        return """Analyze this factory audit document and extract the following information in JSON format:
{
    "supplier_type": "manufacturer" or "trader" or "unknown",
    "employee_count": <number or null>,
    "factory_area_sqm": <number or null>,
    "production_lines_count": <number or null>,
    "markets_served": {"south_america": <pct>, "north_america": <pct>, "europe": <pct>, "asia": <pct>, "other": <pct>},
    "certifications": ["list", "of", "certifications"],
    "has_machinery_photos": true/false,
    "positive_points": ["strength 1", "strength 2", ...],
    "negative_points": ["concern 1", "concern 2", ...],
    "products_verified": ["product 1", "product 2", ...],
    "audit_date": "YYYY-MM-DD" or null,
    "inspector_name": "name" or null
}

Focus on:
1. Whether this is a true manufacturer or trader/middleman - CRITICAL
2. Production capacity indicators (employees, factory size, production lines)
3. Quality certifications (ISO, CE, etc.)
4. Export market experience (percentages by region)
5. Red flags or concerns (negative_points)
6. Positive highlights (positive_points)
7. Products that were verified during the inspection

If information is not found, use null.
Only return valid JSON, no additional text or explanation."""

    def _parse_audit_extraction_response(
        self, response_text: str
    ) -> Dict[str, Any]:
        """Parse AI response into extraction result dictionary.

        Args:
            response_text: Raw AI response text

        Returns:
            Dictionary with extracted fields
        """
        try:
            # Try to extract JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
            else:
                data = {}
        except json.JSONDecodeError:
            print(f"WARN [AuditService]: Failed to parse JSON: {response_text[:200]}")
            data = {}

        # Normalize supplier_type
        supplier_type = data.get("supplier_type")
        if supplier_type and supplier_type.lower() in ["manufacturer", "trader", "unknown"]:
            supplier_type = supplier_type.lower()
        else:
            supplier_type = "unknown"

        # Parse numeric fields safely
        def safe_int(value) -> Optional[int]:
            if value is None:
                return None
            try:
                return int(value)
            except (ValueError, TypeError):
                return None

        return {
            "supplier_type": supplier_type,
            "employee_count": safe_int(data.get("employee_count")),
            "factory_area_sqm": safe_int(data.get("factory_area_sqm")),
            "production_lines_count": safe_int(data.get("production_lines_count")),
            "markets_served": data.get("markets_served"),
            "certifications": data.get("certifications") or [],
            "has_machinery_photos": bool(data.get("has_machinery_photos")),
            "positive_points": data.get("positive_points") or [],
            "negative_points": data.get("negative_points") or [],
            "products_verified": data.get("products_verified") or [],
            "audit_date": data.get("audit_date"),
            "inspector_name": data.get("inspector_name"),
        }

    def _extract_with_anthropic(
        self, images: List[bytes], media_types: List[str]
    ) -> str:
        """Extract audit data using Claude API with vision.

        Args:
            images: List of image bytes (PDF pages converted to images)
            media_types: List of media types for each image

        Returns:
            AI response text
        """
        client = self._get_anthropic_client()
        if not client:
            raise RuntimeError("Anthropic client not available")

        prompt = self._build_audit_extraction_prompt()

        # Build content with images
        content = []
        for idx, (image_data, media_type) in enumerate(zip(images, media_types)):
            base64_image = base64.b64encode(image_data).decode("utf-8")
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": base64_image,
                },
            })

        content.append({"type": "text", "text": prompt})

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            messages=[{"role": "user", "content": content}],
        )

        return message.content[0].text

    def _extract_with_openai(
        self, images: List[bytes], media_types: List[str]
    ) -> str:
        """Extract audit data using OpenAI API with vision.

        Args:
            images: List of image bytes (PDF pages converted to images)
            media_types: List of media types for each image

        Returns:
            AI response text
        """
        client = self._get_openai_client()
        if not client:
            raise RuntimeError("OpenAI client not available")

        prompt = self._build_audit_extraction_prompt()

        # Build content with images
        content = [{"type": "text", "text": prompt}]
        for image_data, media_type in zip(images, media_types):
            base64_image = base64.b64encode(image_data).decode("utf-8")
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{media_type};base64,{base64_image}"
                },
            })

        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=2048,
            messages=[{"role": "user", "content": content}],
        )

        return response.choices[0].message.content

    def _convert_pdf_to_images(self, pdf_content: bytes) -> List[tuple]:
        """Convert PDF pages to images for vision processing.

        Args:
            pdf_content: Raw PDF file content

        Returns:
            List of (image_bytes, media_type) tuples
        """
        try:
            from pdf2image import convert_from_bytes

            # Convert PDF to images (limit to first MAX_PDF_PAGES_TO_PROCESS pages)
            images = convert_from_bytes(
                pdf_content,
                first_page=1,
                last_page=MAX_PDF_PAGES_TO_PROCESS,
                dpi=150,  # Lower DPI for faster processing
                fmt="jpeg",
            )

            result = []
            for img in images:
                import io
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=85)
                buffer.seek(0)
                result.append((buffer.read(), "image/jpeg"))

            print(f"INFO [AuditService]: Converted {len(result)} PDF pages to images")
            return result

        except ImportError:
            print("ERROR [AuditService]: pdf2image package not installed")
            raise RuntimeError(
                "pdf2image package required for PDF processing. "
                "Install with: pip install pdf2image"
            )
        except Exception as e:
            print(f"ERROR [AuditService]: Failed to convert PDF to images: {e}")
            raise RuntimeError(f"Failed to convert PDF: {e}")

    def upload_audit(
        self,
        supplier_id: UUID,
        document_url: str,
        document_name: str,
        file_size_bytes: int,
        audit_type: AuditType,
    ) -> SupplierAuditResponseDTO:
        """Upload and create an audit record.

        Args:
            supplier_id: UUID of the supplier
            document_url: URL of the uploaded document
            document_name: Name of the document
            file_size_bytes: Size of the file in bytes
            audit_type: Type of audit

        Returns:
            SupplierAuditResponseDTO for the created audit

        Raises:
            ValueError: If supplier_id is invalid or audit creation fails
        """
        print(
            f"INFO [AuditService]: Creating audit for supplier {supplier_id}, "
            f"type={audit_type.value}, file={document_name}"
        )

        audit_data = audit_repository.create(
            supplier_id=supplier_id,
            audit_type=audit_type.value,
            document_url=document_url,
            document_name=document_name,
            file_size_bytes=file_size_bytes,
        )

        if not audit_data:
            raise ValueError("Failed to create audit record")

        return self._dict_to_response_dto(audit_data)

    def process_audit(self, audit_id: UUID) -> SupplierAuditResponseDTO:
        """Process an audit document and extract data using AI.

        Args:
            audit_id: UUID of the audit to process

        Returns:
            SupplierAuditResponseDTO with extracted data

        Raises:
            ValueError: If audit not found or processing fails
        """
        print(f"INFO [AuditService]: Processing audit {audit_id}")

        # Get audit record
        audit_data = audit_repository.get_by_id(audit_id)
        if not audit_data:
            raise ValueError(f"Audit {audit_id} not found")

        # Update status to processing
        audit_repository.update_extraction_status(audit_id, "processing")

        try:
            # Fetch PDF content from URL
            import httpx

            document_url = audit_data["document_url"]
            print(f"INFO [AuditService]: Fetching document from {document_url[:50]}...")

            with httpx.Client(timeout=120.0) as client:
                response = client.get(document_url)
                response.raise_for_status()
                pdf_content = response.content

            print(f"INFO [AuditService]: Downloaded {len(pdf_content)} bytes")

            # Convert PDF to images
            images_with_types = self._convert_pdf_to_images(pdf_content)

            if not images_with_types:
                raise ValueError("Failed to extract pages from PDF")

            # Extract data using AI
            images = [img[0] for img in images_with_types]
            media_types = [img[1] for img in images_with_types]

            if not self._is_ai_available():
                print("WARN [AuditService]: AI not available, skipping extraction")
                audit_repository.update_extraction_results(
                    audit_id=audit_id,
                    extraction_status="completed",
                    extraction_raw_response={"error": "AI service not available"},
                )
                return self._dict_to_response_dto(audit_repository.get_by_id(audit_id))

            provider = self._get_preferred_ai_provider()
            print(f"INFO [AuditService]: Using {provider} for extraction")

            if provider == "anthropic":
                response_text = self._extract_with_anthropic(images, media_types)
            else:
                response_text = self._extract_with_openai(images, media_types)

            # Parse response
            extracted = self._parse_audit_extraction_response(response_text)

            # Update audit with extracted data
            updated_audit = audit_repository.update_extraction_results(
                audit_id=audit_id,
                supplier_type=extracted["supplier_type"],
                employee_count=extracted["employee_count"],
                factory_area_sqm=extracted["factory_area_sqm"],
                production_lines_count=extracted["production_lines_count"],
                markets_served=extracted["markets_served"],
                certifications=extracted["certifications"],
                has_machinery_photos=extracted["has_machinery_photos"],
                positive_points=extracted["positive_points"],
                negative_points=extracted["negative_points"],
                products_verified=extracted["products_verified"],
                audit_date=extracted["audit_date"],
                inspector_name=extracted["inspector_name"],
                extraction_status="completed",
                extraction_raw_response={"raw_response": response_text},
            )

            if not updated_audit:
                raise ValueError("Failed to update audit with extraction results")

            print(f"INFO [AuditService]: Extraction completed for audit {audit_id}")
            return self._dict_to_response_dto(updated_audit)

        except Exception as e:
            print(f"ERROR [AuditService]: Extraction failed for audit {audit_id}: {e}")
            # Update status to failed
            audit_repository.update_extraction_results(
                audit_id=audit_id,
                extraction_status="failed",
                extraction_raw_response={"error": str(e)},
            )
            # Re-fetch and return the audit with failed status
            failed_audit = audit_repository.get_by_id(audit_id)
            if failed_audit:
                return self._dict_to_response_dto(failed_audit)
            raise ValueError(f"Extraction failed: {e}")

    def get_audit(self, audit_id: UUID) -> Optional[SupplierAuditResponseDTO]:
        """Get a single audit by ID.

        Args:
            audit_id: UUID of the audit

        Returns:
            SupplierAuditResponseDTO if found, None otherwise
        """
        audit_data = audit_repository.get_by_id(audit_id)
        if not audit_data:
            return None
        return self._dict_to_response_dto(audit_data)

    def get_supplier_audits(
        self,
        supplier_id: UUID,
        page: int = 1,
        limit: int = 20,
    ) -> SupplierAuditListResponseDTO:
        """Get all audits for a supplier with pagination.

        Args:
            supplier_id: UUID of the supplier
            page: Page number (1-indexed)
            limit: Number of items per page

        Returns:
            SupplierAuditListResponseDTO with paginated results
        """
        audits, total = audit_repository.get_by_supplier_id(
            supplier_id=supplier_id,
            page=page,
            limit=limit,
        )

        items = [self._dict_to_response_dto(audit) for audit in audits]
        pages = math.ceil(total / limit) if limit > 0 else 0

        return SupplierAuditListResponseDTO(
            items=items,
            pagination=PaginationDTO(
                page=page,
                limit=limit,
                total=total,
                pages=pages,
            ),
        )

    def reprocess_audit(self, audit_id: UUID) -> SupplierAuditResponseDTO:
        """Reprocess an audit by resetting extraction and running again.

        Args:
            audit_id: UUID of the audit

        Returns:
            SupplierAuditResponseDTO with new extraction results

        Raises:
            ValueError: If audit not found
        """
        print(f"INFO [AuditService]: Reprocessing audit {audit_id}")

        # Reset extraction fields
        reset_audit = audit_repository.reset_extraction(audit_id)
        if not reset_audit:
            raise ValueError(f"Audit {audit_id} not found")

        # Run extraction again
        return self.process_audit(audit_id)

    def delete_audit(self, audit_id: UUID) -> bool:
        """Delete an audit record.

        Args:
            audit_id: UUID of the audit

        Returns:
            True if deleted, False otherwise
        """
        return audit_repository.delete(audit_id)

    def classify_supplier(self, audit_id: UUID) -> SupplierAuditResponseDTO:
        """Classify a supplier based on extracted audit data.

        Applies a scoring algorithm to the extracted data and generates
        an A/B/C classification with human-readable reasoning.

        Scoring system:
        - supplier_type: manufacturer = +3, trader = +1, unknown = 0
        - certifications count: 3+ = +2, 1-2 = +1, 0 = 0
        - production_lines_count: 3+ = +1, 1-2 = +0.5, 0 = 0
        - negative_points count: 0 = +1, 1-2 = 0, 3+ = -1
        - positive_points count: 3+ = +1, 1-2 = +0.5, 0 = 0
        - markets_served.south_america > 0 = +0.5 (bonus for SA experience)

        Thresholds:
        - Type A: score >= 6
        - Type B: score >= 3 and < 6
        - Type C: score < 3

        Args:
            audit_id: UUID of the audit to classify

        Returns:
            SupplierAuditResponseDTO with classification data

        Raises:
            ValueError: If audit not found or extraction not completed
        """
        print(f"INFO [AuditService]: Classifying audit {audit_id}")

        # Get audit
        audit_data = audit_repository.get_by_id(audit_id)
        if not audit_data:
            raise ValueError(f"Audit {audit_id} not found")

        # Verify extraction is completed
        if audit_data.get("extraction_status") != "completed":
            raise ValueError(
                f"Audit {audit_id} extraction not completed. "
                f"Current status: {audit_data.get('extraction_status')}"
            )

        # Calculate score
        score = 0.0
        reason_parts = []

        # Supplier type scoring
        supplier_type = audit_data.get("supplier_type") or "unknown"
        if supplier_type == "manufacturer":
            score += 3.0
            reason_parts.append("Verified manufacturer (+3)")
        elif supplier_type == "trader":
            score += 1.0
            reason_parts.append("Identified as trader (+1)")
        else:
            reason_parts.append("Supplier type unknown (0)")

        # Certifications scoring
        certifications = audit_data.get("certifications") or []
        cert_count = len(certifications)
        if cert_count >= 3:
            score += 2.0
            reason_parts.append(f"{cert_count} certifications (+2)")
        elif cert_count >= 1:
            score += 1.0
            reason_parts.append(f"{cert_count} certification(s) (+1)")
        else:
            reason_parts.append("No certifications (0)")

        # Production lines scoring
        production_lines = audit_data.get("production_lines_count") or 0
        if production_lines >= 3:
            score += 1.0
            reason_parts.append(f"{production_lines} production lines (+1)")
        elif production_lines >= 1:
            score += 0.5
            reason_parts.append(f"{production_lines} production line(s) (+0.5)")

        # Negative points scoring (penalty)
        negative_points = audit_data.get("negative_points") or []
        neg_count = len(negative_points)
        if neg_count == 0:
            score += 1.0
            reason_parts.append("No negative points (+1)")
        elif neg_count >= 3:
            score -= 1.0
            reason_parts.append(f"{neg_count} negative points (-1)")
        else:
            reason_parts.append(f"{neg_count} negative point(s) (0)")

        # Positive points scoring
        positive_points = audit_data.get("positive_points") or []
        pos_count = len(positive_points)
        if pos_count >= 3:
            score += 1.0
            reason_parts.append(f"{pos_count} positive points (+1)")
        elif pos_count >= 1:
            score += 0.5
            reason_parts.append(f"{pos_count} positive point(s) (+0.5)")

        # South America market experience bonus
        markets_served = audit_data.get("markets_served") or {}
        sa_percentage = markets_served.get("south_america", 0)
        if sa_percentage and sa_percentage > 0:
            score += 0.5
            reason_parts.append(f"South America export experience: {sa_percentage}% (+0.5)")

        # Determine classification
        if score >= 6:
            classification = "A"
            tier_description = "Type A - Preferred supplier"
        elif score >= 3:
            classification = "B"
            tier_description = "Type B - Acceptable supplier"
        else:
            classification = "C"
            tier_description = "Type C - Requires additional verification"

        # Build human-readable reasoning
        reason = (
            f"{tier_description}. "
            f"Total score: {score:.1f}/9 possible. "
            f"Factors: {'; '.join(reason_parts)}."
        )

        print(
            f"INFO [AuditService]: Classification for audit {audit_id}: "
            f"{classification} (score: {score:.1f})"
        )

        # Update audit with classification
        updated_audit = audit_repository.update_classification(
            audit_id=audit_id,
            classification=classification,
            reason=reason,
        )

        if not updated_audit:
            raise ValueError(f"Failed to update classification for audit {audit_id}")

        # Update supplier certification status
        supplier_id = updated_audit["supplier_id"]
        self._update_supplier_certification(
            supplier_id=supplier_id,
            classification=classification,
            audit_id=audit_id,
        )

        return self._dict_to_response_dto(updated_audit)

    def override_classification(
        self,
        audit_id: UUID,
        classification: str,
        notes: str,
        user_id: UUID,
    ) -> SupplierAuditResponseDTO:
        """Override the AI classification with a manual classification.

        Args:
            audit_id: UUID of the audit
            classification: Classification grade (A, B, or C)
            notes: Required notes explaining the override
            user_id: UUID of the user making the override

        Returns:
            SupplierAuditResponseDTO with updated classification

        Raises:
            ValueError: If validation fails or audit not found
        """
        print(
            f"INFO [AuditService]: Override classification for audit {audit_id} "
            f"to {classification} by user {user_id}"
        )

        # Validate classification
        if classification not in ("A", "B", "C"):
            raise ValueError(f"Invalid classification '{classification}'. Must be A, B, or C.")

        # Validate notes (required for overrides)
        if not notes or not notes.strip():
            raise ValueError("Notes are required when overriding classification.")

        # Get audit
        audit_data = audit_repository.get_by_id(audit_id)
        if not audit_data:
            raise ValueError(f"Audit {audit_id} not found")

        # Update manual classification
        updated_audit = audit_repository.update_manual_classification(
            audit_id=audit_id,
            classification=classification,
            notes=notes.strip(),
        )

        if not updated_audit:
            raise ValueError(f"Failed to update manual classification for audit {audit_id}")

        # Update supplier certification status (manual takes precedence)
        supplier_id = updated_audit["supplier_id"]
        self._update_supplier_certification(
            supplier_id=supplier_id,
            classification=classification,
            audit_id=audit_id,
        )

        print(
            f"INFO [AuditService]: Override completed for audit {audit_id}: "
            f"classification={classification}"
        )

        return self._dict_to_response_dto(updated_audit)

    def _update_supplier_certification(
        self,
        supplier_id: UUID,
        classification: str,
        audit_id: UUID,
    ) -> None:
        """Update supplier certification status based on classification.

        Maps classification grade to CertificationStatus enum and updates
        the supplier record.

        Args:
            supplier_id: UUID of the supplier
            classification: Classification grade (A, B, or C)
            audit_id: UUID of the audit that triggered this update
        """
        # Map classification to certification status
        classification_to_status = {
            "A": CertificationStatus.CERTIFIED_A.value,
            "B": CertificationStatus.CERTIFIED_B.value,
            "C": CertificationStatus.CERTIFIED_C.value,
        }

        certification_status = classification_to_status.get(classification)
        if not certification_status:
            print(
                f"WARN [AuditService]: Unknown classification '{classification}', "
                "skipping supplier update"
            )
            return

        supplier_repo = SupplierRepository()
        result = supplier_repo.update_certification_status(
            supplier_id=supplier_id,
            certification_status=certification_status,
            audit_id=audit_id,
        )

        if result:
            print(
                f"INFO [AuditService]: Updated supplier {supplier_id} "
                f"certification to {certification_status}"
            )
        else:
            print(
                f"WARN [AuditService]: Failed to update supplier {supplier_id} "
                f"certification status"
            )

    def _dict_to_response_dto(self, data: Dict[str, Any]) -> SupplierAuditResponseDTO:
        """Convert audit dictionary to response DTO.

        Args:
            data: Audit dictionary from repository

        Returns:
            SupplierAuditResponseDTO
        """
        # Convert supplier_type string to enum
        supplier_type = None
        if data.get("supplier_type"):
            try:
                supplier_type = SupplierType(data["supplier_type"])
            except ValueError:
                supplier_type = SupplierType.UNKNOWN

        # Convert extraction_status string to enum
        extraction_status = ExtractionStatus.PENDING
        if data.get("extraction_status"):
            try:
                extraction_status = ExtractionStatus(data["extraction_status"])
            except ValueError:
                extraction_status = ExtractionStatus.PENDING

        # Convert audit_type string to enum
        audit_type = AuditType.FACTORY_AUDIT
        if data.get("audit_type"):
            try:
                audit_type = AuditType(data["audit_type"])
            except ValueError:
                audit_type = AuditType.FACTORY_AUDIT

        return SupplierAuditResponseDTO(
            id=data["id"],
            supplier_id=data["supplier_id"],
            audit_type=audit_type,
            document_url=data["document_url"],
            document_name=data.get("document_name"),
            file_size_bytes=data.get("file_size_bytes"),
            supplier_type=supplier_type,
            employee_count=data.get("employee_count"),
            factory_area_sqm=data.get("factory_area_sqm"),
            production_lines_count=data.get("production_lines_count"),
            markets_served=data.get("markets_served"),
            certifications=data.get("certifications"),
            has_machinery_photos=data.get("has_machinery_photos", False),
            positive_points=data.get("positive_points"),
            negative_points=data.get("negative_points"),
            products_verified=data.get("products_verified"),
            audit_date=data.get("audit_date"),
            inspector_name=data.get("inspector_name"),
            extraction_status=extraction_status,
            extraction_raw_response=data.get("extraction_raw_response"),
            extracted_at=data.get("extracted_at"),
            ai_classification=data.get("ai_classification"),
            ai_classification_reason=data.get("ai_classification_reason"),
            manual_classification=data.get("manual_classification"),
            classification_notes=data.get("classification_notes"),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )


# Singleton instance
audit_service = AuditService()
