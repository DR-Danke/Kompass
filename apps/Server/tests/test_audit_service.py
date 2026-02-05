"""Unit tests for the Audit Service."""

import json
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.models.kompass_dto import (
    AuditType,
    ExtractionStatus,
    SupplierAuditListResponseDTO,
    SupplierAuditResponseDTO,
    SupplierType,
)
from app.services.audit_service import AuditService


@pytest.fixture
def service():
    """Create a fresh AuditService instance for each test."""
    return AuditService()


@pytest.fixture
def mock_settings():
    """Create mock settings with API keys configured."""
    settings = MagicMock()
    settings.ANTHROPIC_API_KEY = "test-anthropic-key"
    settings.OPENAI_API_KEY = "test-openai-key"
    settings.EXTRACTION_AI_PROVIDER = "anthropic"
    settings.EXTRACTION_TIMEOUT_SECONDS = 60
    return settings


@pytest.fixture
def mock_settings_no_ai():
    """Create mock settings without AI keys configured."""
    settings = MagicMock()
    settings.ANTHROPIC_API_KEY = None
    settings.OPENAI_API_KEY = None
    settings.EXTRACTION_AI_PROVIDER = "anthropic"
    settings.EXTRACTION_TIMEOUT_SECONDS = 60
    return settings


@pytest.fixture
def sample_audit_data():
    """Create sample audit data from repository."""
    return {
        "id": uuid4(),
        "supplier_id": uuid4(),
        "audit_type": "factory_audit",
        "document_url": "https://example.com/audit.pdf",
        "document_name": "factory_audit.pdf",
        "file_size_bytes": 1024000,
        "supplier_type": "manufacturer",
        "employee_count": 500,
        "factory_area_sqm": 10000,
        "production_lines_count": 5,
        "markets_served": {
            "south_america": 30,
            "north_america": 40,
            "europe": 20,
            "asia": 10,
        },
        "certifications": ["ISO 9001", "CE"],
        "has_machinery_photos": True,
        "positive_points": ["Modern equipment", "Clean facility"],
        "negative_points": ["Limited storage space"],
        "products_verified": ["Product A", "Product B"],
        "audit_date": "2024-01-15",
        "inspector_name": "John Doe",
        "extraction_status": "completed",
        "extraction_raw_response": {"raw_response": "..."},
        "extracted_at": datetime.utcnow(),
        "ai_classification": None,
        "ai_classification_reason": None,
        "manual_classification": None,
        "classification_notes": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


class TestAuditServiceInit:
    """Tests for AuditService initialization."""

    def test_service_initializes(self, service):
        """Test that service initializes correctly."""
        assert service is not None
        assert service._anthropic_client is None
        assert service._openai_client is None


class TestAIAvailability:
    """Tests for AI availability checking."""

    def test_ai_available_with_anthropic_key(self, service, mock_settings):
        """Test AI is available when Anthropic key is configured."""
        mock_settings.OPENAI_API_KEY = None
        with patch.object(service, "_settings", mock_settings):
            assert service._is_ai_available() is True

    def test_ai_available_with_openai_key(self, service, mock_settings):
        """Test AI is available when OpenAI key is configured."""
        mock_settings.ANTHROPIC_API_KEY = None
        with patch.object(service, "_settings", mock_settings):
            assert service._is_ai_available() is True

    def test_ai_not_available_without_keys(self, service, mock_settings_no_ai):
        """Test AI is not available when no keys are configured."""
        with patch.object(service, "_settings", mock_settings_no_ai):
            assert service._is_ai_available() is False


class TestPreferredProvider:
    """Tests for AI provider selection."""

    def test_prefers_anthropic_when_configured(self, service, mock_settings):
        """Test that Anthropic is preferred when configured."""
        with patch.object(service, "_settings", mock_settings):
            assert service._get_preferred_ai_provider() == "anthropic"

    def test_prefers_openai_when_anthropic_unavailable(self, service, mock_settings):
        """Test fallback to OpenAI when Anthropic is unavailable."""
        mock_settings.ANTHROPIC_API_KEY = None
        mock_settings.EXTRACTION_AI_PROVIDER = "anthropic"
        with patch.object(service, "_settings", mock_settings):
            assert service._get_preferred_ai_provider() == "openai"

    def test_returns_none_when_no_provider(self, service, mock_settings_no_ai):
        """Test returns 'none' when no provider is available."""
        with patch.object(service, "_settings", mock_settings_no_ai):
            assert service._get_preferred_ai_provider() == "none"


class TestParseAuditExtractionResponse:
    """Tests for parsing AI extraction responses."""

    def test_parses_valid_json_response(self, service):
        """Test parsing a valid JSON response."""
        response = json.dumps({
            "supplier_type": "manufacturer",
            "employee_count": 500,
            "factory_area_sqm": 10000,
            "production_lines_count": 5,
            "markets_served": {
                "south_america": 30,
                "north_america": 40,
                "europe": 20,
                "asia": 10,
            },
            "certifications": ["ISO 9001", "CE"],
            "has_machinery_photos": True,
            "positive_points": ["Modern equipment"],
            "negative_points": ["Small warehouse"],
            "products_verified": ["Widget A"],
            "audit_date": "2024-01-15",
            "inspector_name": "John Doe",
        })
        result = service._parse_audit_extraction_response(response)

        assert result["supplier_type"] == "manufacturer"
        assert result["employee_count"] == 500
        assert result["factory_area_sqm"] == 10000
        assert result["production_lines_count"] == 5
        assert result["markets_served"]["south_america"] == 30
        assert "ISO 9001" in result["certifications"]
        assert result["has_machinery_photos"] is True
        assert "Modern equipment" in result["positive_points"]
        assert "Small warehouse" in result["negative_points"]
        assert "Widget A" in result["products_verified"]
        assert result["audit_date"] == "2024-01-15"
        assert result["inspector_name"] == "John Doe"

    def test_parses_partial_json_response(self, service):
        """Test parsing a response with missing fields."""
        response = json.dumps({
            "supplier_type": "trader",
            "employee_count": 50,
        })
        result = service._parse_audit_extraction_response(response)

        assert result["supplier_type"] == "trader"
        assert result["employee_count"] == 50
        assert result["factory_area_sqm"] is None
        assert result["certifications"] == []

    def test_handles_invalid_json(self, service):
        """Test handling of invalid JSON response."""
        response = "This is not valid JSON"
        result = service._parse_audit_extraction_response(response)

        assert result["supplier_type"] == "unknown"
        assert result["employee_count"] is None

    def test_extracts_json_from_text(self, service):
        """Test extracting JSON embedded in text."""
        response = 'Here is the result: {"supplier_type": "manufacturer", "employee_count": 100} end.'
        result = service._parse_audit_extraction_response(response)

        assert result["supplier_type"] == "manufacturer"
        assert result["employee_count"] == 100

    def test_normalizes_supplier_type(self, service):
        """Test that supplier type is normalized to lowercase."""
        response = json.dumps({"supplier_type": "MANUFACTURER"})
        result = service._parse_audit_extraction_response(response)

        assert result["supplier_type"] == "manufacturer"

    def test_handles_invalid_supplier_type(self, service):
        """Test handling of invalid supplier type."""
        response = json.dumps({"supplier_type": "invalid_type"})
        result = service._parse_audit_extraction_response(response)

        assert result["supplier_type"] == "unknown"


class TestBuildAuditExtractionPrompt:
    """Tests for the extraction prompt builder."""

    def test_prompt_contains_required_fields(self, service):
        """Test that prompt includes all required extraction fields."""
        prompt = service._build_audit_extraction_prompt()

        assert "supplier_type" in prompt
        assert "employee_count" in prompt
        assert "factory_area_sqm" in prompt
        assert "production_lines_count" in prompt
        assert "markets_served" in prompt
        assert "certifications" in prompt
        assert "has_machinery_photos" in prompt
        assert "positive_points" in prompt
        assert "negative_points" in prompt
        assert "products_verified" in prompt
        assert "audit_date" in prompt
        assert "inspector_name" in prompt

    def test_prompt_requests_json_format(self, service):
        """Test that prompt requests JSON output."""
        prompt = service._build_audit_extraction_prompt()

        assert "JSON" in prompt


class TestUploadAudit:
    """Tests for audit upload functionality."""

    @patch("app.services.audit_service.audit_repository")
    def test_upload_audit_creates_record(self, mock_repo, service):
        """Test that upload_audit creates an audit record."""
        supplier_id = uuid4()
        audit_id = uuid4()

        mock_repo.create.return_value = {
            "id": audit_id,
            "supplier_id": supplier_id,
            "audit_type": "factory_audit",
            "document_url": "https://example.com/audit.pdf",
            "document_name": "audit.pdf",
            "file_size_bytes": 1024000,
            "supplier_type": None,
            "employee_count": None,
            "factory_area_sqm": None,
            "production_lines_count": None,
            "markets_served": None,
            "certifications": None,
            "has_machinery_photos": False,
            "positive_points": None,
            "negative_points": None,
            "products_verified": None,
            "audit_date": None,
            "inspector_name": None,
            "extraction_status": "pending",
            "extraction_raw_response": None,
            "extracted_at": None,
            "ai_classification": None,
            "ai_classification_reason": None,
            "manual_classification": None,
            "classification_notes": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = service.upload_audit(
            supplier_id=supplier_id,
            document_url="https://example.com/audit.pdf",
            document_name="audit.pdf",
            file_size_bytes=1024000,
            audit_type=AuditType.FACTORY_AUDIT,
        )

        assert isinstance(result, SupplierAuditResponseDTO)
        assert result.id == audit_id
        assert result.supplier_id == supplier_id
        assert result.extraction_status == ExtractionStatus.PENDING
        mock_repo.create.assert_called_once()

    @patch("app.services.audit_service.audit_repository")
    def test_upload_audit_raises_on_failure(self, mock_repo, service):
        """Test that upload_audit raises ValueError on failure."""
        mock_repo.create.return_value = None

        with pytest.raises(ValueError, match="Failed to create audit record"):
            service.upload_audit(
                supplier_id=uuid4(),
                document_url="https://example.com/audit.pdf",
                document_name="audit.pdf",
                file_size_bytes=1024000,
                audit_type=AuditType.FACTORY_AUDIT,
            )


class TestGetAudit:
    """Tests for retrieving audits."""

    @patch("app.services.audit_service.audit_repository")
    def test_get_audit_returns_dto(self, mock_repo, service, sample_audit_data):
        """Test that get_audit returns a response DTO."""
        mock_repo.get_by_id.return_value = sample_audit_data

        result = service.get_audit(sample_audit_data["id"])

        assert isinstance(result, SupplierAuditResponseDTO)
        assert result.id == sample_audit_data["id"]
        assert result.supplier_type == SupplierType.MANUFACTURER

    @patch("app.services.audit_service.audit_repository")
    def test_get_audit_returns_none_when_not_found(self, mock_repo, service):
        """Test that get_audit returns None when audit not found."""
        mock_repo.get_by_id.return_value = None

        result = service.get_audit(uuid4())

        assert result is None


class TestGetSupplierAudits:
    """Tests for listing supplier audits."""

    @patch("app.services.audit_service.audit_repository")
    def test_get_supplier_audits_returns_paginated_list(
        self, mock_repo, service, sample_audit_data
    ):
        """Test that get_supplier_audits returns paginated results."""
        mock_repo.get_by_supplier_id.return_value = ([sample_audit_data], 1)

        result = service.get_supplier_audits(
            supplier_id=sample_audit_data["supplier_id"],
            page=1,
            limit=20,
        )

        assert isinstance(result, SupplierAuditListResponseDTO)
        assert len(result.items) == 1
        assert result.pagination.total == 1
        assert result.pagination.page == 1

    @patch("app.services.audit_service.audit_repository")
    def test_get_supplier_audits_empty_list(self, mock_repo, service):
        """Test that get_supplier_audits handles empty results."""
        mock_repo.get_by_supplier_id.return_value = ([], 0)

        result = service.get_supplier_audits(
            supplier_id=uuid4(),
            page=1,
            limit=20,
        )

        assert isinstance(result, SupplierAuditListResponseDTO)
        assert len(result.items) == 0
        assert result.pagination.total == 0


class TestReprocessAudit:
    """Tests for reprocessing audits."""

    @patch("app.services.audit_service.audit_repository")
    def test_reprocess_resets_and_extracts(self, mock_repo, service, sample_audit_data):
        """Test that reprocess resets extraction and runs again."""
        # Reset returns the reset audit
        reset_data = sample_audit_data.copy()
        reset_data["extraction_status"] = "pending"
        reset_data["supplier_type"] = None
        mock_repo.reset_extraction.return_value = reset_data

        # Processing returns completed audit
        mock_repo.get_by_id.return_value = reset_data
        mock_repo.update_extraction_status.return_value = reset_data
        mock_repo.update_extraction_results.return_value = sample_audit_data

        # Mock httpx to fail (no actual URL)
        with patch("httpx.Client") as mock_httpx:
            mock_response = MagicMock()
            mock_response.content = b"mock pdf content"
            mock_client = MagicMock()
            mock_client.get.return_value = mock_response
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_httpx.return_value = mock_client

            # Mock PDF conversion to fail gracefully
            with patch.object(
                service, "_convert_pdf_to_images", side_effect=RuntimeError("Test error")
            ):
                service.reprocess_audit(sample_audit_data["id"])

        mock_repo.reset_extraction.assert_called_once_with(sample_audit_data["id"])

    @patch("app.services.audit_service.audit_repository")
    def test_reprocess_raises_when_not_found(self, mock_repo, service):
        """Test that reprocess raises ValueError when audit not found."""
        mock_repo.reset_extraction.return_value = None

        with pytest.raises(ValueError, match="not found"):
            service.reprocess_audit(uuid4())


class TestDeleteAudit:
    """Tests for deleting audits."""

    @patch("app.services.audit_service.audit_repository")
    def test_delete_audit_returns_true_on_success(self, mock_repo, service):
        """Test that delete_audit returns True on success."""
        mock_repo.delete.return_value = True

        result = service.delete_audit(uuid4())

        assert result is True

    @patch("app.services.audit_service.audit_repository")
    def test_delete_audit_returns_false_on_failure(self, mock_repo, service):
        """Test that delete_audit returns False on failure."""
        mock_repo.delete.return_value = False

        result = service.delete_audit(uuid4())

        assert result is False


class TestDictToResponseDto:
    """Tests for converting dict to response DTO."""

    def test_converts_all_fields(self, service, sample_audit_data):
        """Test that all fields are converted correctly."""
        result = service._dict_to_response_dto(sample_audit_data)

        assert isinstance(result, SupplierAuditResponseDTO)
        assert result.id == sample_audit_data["id"]
        assert result.supplier_id == sample_audit_data["supplier_id"]
        assert result.audit_type == AuditType.FACTORY_AUDIT
        assert result.document_url == sample_audit_data["document_url"]
        assert result.supplier_type == SupplierType.MANUFACTURER
        assert result.employee_count == 500
        assert result.extraction_status == ExtractionStatus.COMPLETED

    def test_handles_null_supplier_type(self, service, sample_audit_data):
        """Test handling of null supplier type."""
        sample_audit_data["supplier_type"] = None
        result = service._dict_to_response_dto(sample_audit_data)

        assert result.supplier_type is None

    def test_handles_invalid_supplier_type(self, service, sample_audit_data):
        """Test handling of invalid supplier type."""
        sample_audit_data["supplier_type"] = "invalid"
        result = service._dict_to_response_dto(sample_audit_data)

        assert result.supplier_type == SupplierType.UNKNOWN

    def test_handles_missing_optional_fields(self, service):
        """Test handling of missing optional fields."""
        minimal_data = {
            "id": uuid4(),
            "supplier_id": uuid4(),
            "audit_type": "factory_audit",
            "document_url": "https://example.com/audit.pdf",
            "document_name": None,
            "file_size_bytes": None,
            "supplier_type": None,
            "employee_count": None,
            "factory_area_sqm": None,
            "production_lines_count": None,
            "markets_served": None,
            "certifications": None,
            "has_machinery_photos": False,
            "positive_points": None,
            "negative_points": None,
            "products_verified": None,
            "audit_date": None,
            "inspector_name": None,
            "extraction_status": "pending",
            "extraction_raw_response": None,
            "extracted_at": None,
            "ai_classification": None,
            "ai_classification_reason": None,
            "manual_classification": None,
            "classification_notes": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        result = service._dict_to_response_dto(minimal_data)

        assert isinstance(result, SupplierAuditResponseDTO)
        assert result.document_name is None
        assert result.supplier_type is None
        assert result.extraction_status == ExtractionStatus.PENDING


class TestProcessAudit:
    """Tests for audit processing."""

    @patch("app.services.audit_service.audit_repository")
    def test_process_audit_raises_when_not_found(self, mock_repo, service):
        """Test that process_audit raises ValueError when audit not found."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="not found"):
            service.process_audit(uuid4())

    @patch("app.services.audit_service.audit_repository")
    @patch("httpx.Client")
    def test_process_audit_updates_status_to_processing(
        self, mock_httpx, mock_repo, service, sample_audit_data
    ):
        """Test that process_audit updates status to processing."""
        sample_audit_data["extraction_status"] = "pending"
        mock_repo.get_by_id.return_value = sample_audit_data
        mock_repo.update_extraction_status.return_value = sample_audit_data

        # Mock httpx
        mock_response = MagicMock()
        mock_response.content = b"mock pdf content"
        mock_response.raise_for_status = MagicMock()
        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_httpx.return_value = mock_client

        # Mock PDF conversion to fail
        with patch.object(
            service, "_convert_pdf_to_images", side_effect=RuntimeError("Test error")
        ):
            mock_repo.update_extraction_results.return_value = sample_audit_data
            service.process_audit(sample_audit_data["id"])

        mock_repo.update_extraction_status.assert_called_with(
            sample_audit_data["id"], "processing"
        )
