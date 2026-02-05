"""Unit tests for supplier classification logic."""

from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.models.kompass_dto import (
    CertificationStatus,
    SupplierAuditResponseDTO,
)
from app.services.audit_service import AuditService


@pytest.fixture
def service():
    """Create a fresh AuditService instance for each test."""
    return AuditService()


@pytest.fixture
def sample_audit_data_completed():
    """Create sample audit data with extraction completed."""
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
        "certifications": ["ISO 9001", "CE", "SGS"],
        "has_machinery_photos": True,
        "positive_points": ["Modern equipment", "Clean facility", "Experienced staff"],
        "negative_points": [],
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


@pytest.fixture
def sample_audit_data_type_b():
    """Create sample audit data that scores Type B."""
    return {
        "id": uuid4(),
        "supplier_id": uuid4(),
        "audit_type": "factory_audit",
        "document_url": "https://example.com/audit.pdf",
        "document_name": "factory_audit.pdf",
        "file_size_bytes": 1024000,
        "supplier_type": "manufacturer",
        "employee_count": 100,
        "factory_area_sqm": 2000,
        "production_lines_count": 2,
        "markets_served": {
            "asia": 80,
            "europe": 20,
        },
        "certifications": ["ISO 9001"],
        "has_machinery_photos": True,
        "positive_points": ["Good quality"],
        "negative_points": ["Limited capacity", "Old equipment"],
        "products_verified": ["Product A"],
        "audit_date": "2024-01-15",
        "inspector_name": "Jane Smith",
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


@pytest.fixture
def sample_audit_data_type_c():
    """Create sample audit data that scores Type C."""
    return {
        "id": uuid4(),
        "supplier_id": uuid4(),
        "audit_type": "factory_audit",
        "document_url": "https://example.com/audit.pdf",
        "document_name": "factory_audit.pdf",
        "file_size_bytes": 1024000,
        "supplier_type": "trader",
        "employee_count": 10,
        "factory_area_sqm": None,
        "production_lines_count": 0,
        "markets_served": None,
        "certifications": [],
        "has_machinery_photos": False,
        "positive_points": [],
        "negative_points": ["No factory visit", "Unclear documentation", "Missing certifications"],
        "products_verified": [],
        "audit_date": "2024-01-15",
        "inspector_name": "Inspector",
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


class TestClassifySupplier:
    """Tests for classify_supplier() method."""

    @patch("app.services.audit_service.audit_repository")
    @patch("app.services.audit_service.SupplierRepository")
    def test_classifies_type_a_for_excellent_supplier(
        self, mock_supplier_repo_class, mock_audit_repo, service, sample_audit_data_completed
    ):
        """Test Type A classification for manufacturer with good metrics."""
        mock_audit_repo.get_by_id.return_value = sample_audit_data_completed

        classified_data = sample_audit_data_completed.copy()
        classified_data["ai_classification"] = "A"
        classified_data["ai_classification_reason"] = "Type A - Preferred supplier..."
        mock_audit_repo.update_classification.return_value = classified_data

        mock_supplier_repo = MagicMock()
        mock_supplier_repo.update_certification_status.return_value = {"id": sample_audit_data_completed["supplier_id"]}
        mock_supplier_repo_class.return_value = mock_supplier_repo

        result = service.classify_supplier(sample_audit_data_completed["id"])

        assert isinstance(result, SupplierAuditResponseDTO)
        assert result.ai_classification == "A"
        mock_audit_repo.update_classification.assert_called_once()
        call_args = mock_audit_repo.update_classification.call_args
        assert call_args[1]["classification"] == "A"
        assert "Type A" in call_args[1]["reason"]

    @patch("app.services.audit_service.audit_repository")
    @patch("app.services.audit_service.SupplierRepository")
    def test_classifies_type_b_for_moderate_supplier(
        self, mock_supplier_repo_class, mock_audit_repo, service, sample_audit_data_type_b
    ):
        """Test Type B classification for moderate scores."""
        mock_audit_repo.get_by_id.return_value = sample_audit_data_type_b

        classified_data = sample_audit_data_type_b.copy()
        classified_data["ai_classification"] = "B"
        classified_data["ai_classification_reason"] = "Type B - Acceptable supplier..."
        mock_audit_repo.update_classification.return_value = classified_data

        mock_supplier_repo = MagicMock()
        mock_supplier_repo.update_certification_status.return_value = {"id": sample_audit_data_type_b["supplier_id"]}
        mock_supplier_repo_class.return_value = mock_supplier_repo

        result = service.classify_supplier(sample_audit_data_type_b["id"])

        assert result.ai_classification == "B"
        call_args = mock_audit_repo.update_classification.call_args
        assert call_args[1]["classification"] == "B"
        assert "Type B" in call_args[1]["reason"]

    @patch("app.services.audit_service.audit_repository")
    @patch("app.services.audit_service.SupplierRepository")
    def test_classifies_type_c_for_trader_with_issues(
        self, mock_supplier_repo_class, mock_audit_repo, service, sample_audit_data_type_c
    ):
        """Test Type C classification for trader with many issues."""
        mock_audit_repo.get_by_id.return_value = sample_audit_data_type_c

        classified_data = sample_audit_data_type_c.copy()
        classified_data["ai_classification"] = "C"
        classified_data["ai_classification_reason"] = "Type C - Requires verification..."
        mock_audit_repo.update_classification.return_value = classified_data

        mock_supplier_repo = MagicMock()
        mock_supplier_repo.update_certification_status.return_value = {"id": sample_audit_data_type_c["supplier_id"]}
        mock_supplier_repo_class.return_value = mock_supplier_repo

        result = service.classify_supplier(sample_audit_data_type_c["id"])

        assert result.ai_classification == "C"
        call_args = mock_audit_repo.update_classification.call_args
        assert call_args[1]["classification"] == "C"
        assert "Type C" in call_args[1]["reason"]

    @patch("app.services.audit_service.audit_repository")
    def test_raises_when_audit_not_found(self, mock_audit_repo, service):
        """Test that classify_supplier raises ValueError when audit not found."""
        mock_audit_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="not found"):
            service.classify_supplier(uuid4())

    @patch("app.services.audit_service.audit_repository")
    def test_raises_when_extraction_not_completed(
        self, mock_audit_repo, service, sample_audit_data_completed
    ):
        """Test that classify_supplier raises ValueError when extraction not completed."""
        sample_audit_data_completed["extraction_status"] = "pending"
        mock_audit_repo.get_by_id.return_value = sample_audit_data_completed

        with pytest.raises(ValueError, match="extraction not completed"):
            service.classify_supplier(sample_audit_data_completed["id"])

    @patch("app.services.audit_service.audit_repository")
    @patch("app.services.audit_service.SupplierRepository")
    def test_updates_supplier_certification_status(
        self, mock_supplier_repo_class, mock_audit_repo, service, sample_audit_data_completed
    ):
        """Test that supplier certification_status is updated after classification."""
        mock_audit_repo.get_by_id.return_value = sample_audit_data_completed

        classified_data = sample_audit_data_completed.copy()
        classified_data["ai_classification"] = "A"
        mock_audit_repo.update_classification.return_value = classified_data

        mock_supplier_repo = MagicMock()
        mock_supplier_repo.update_certification_status.return_value = {"id": sample_audit_data_completed["supplier_id"]}
        mock_supplier_repo_class.return_value = mock_supplier_repo

        service.classify_supplier(sample_audit_data_completed["id"])

        mock_supplier_repo.update_certification_status.assert_called_once_with(
            supplier_id=sample_audit_data_completed["supplier_id"],
            certification_status=CertificationStatus.CERTIFIED_A.value,
            audit_id=sample_audit_data_completed["id"],
        )

    @patch("app.services.audit_service.audit_repository")
    @patch("app.services.audit_service.SupplierRepository")
    def test_reasoning_is_human_readable(
        self, mock_supplier_repo_class, mock_audit_repo, service, sample_audit_data_completed
    ):
        """Test that classification reasoning is human-readable."""
        mock_audit_repo.get_by_id.return_value = sample_audit_data_completed

        classified_data = sample_audit_data_completed.copy()
        classified_data["ai_classification"] = "A"
        mock_audit_repo.update_classification.return_value = classified_data

        mock_supplier_repo = MagicMock()
        mock_supplier_repo.update_certification_status.return_value = {"id": sample_audit_data_completed["supplier_id"]}
        mock_supplier_repo_class.return_value = mock_supplier_repo

        service.classify_supplier(sample_audit_data_completed["id"])

        call_args = mock_audit_repo.update_classification.call_args
        reason = call_args[1]["reason"]

        # Check that reason includes key elements
        assert "Type A" in reason
        assert "score" in reason.lower()
        assert "manufacturer" in reason.lower()
        assert "certifications" in reason.lower()

    @patch("app.services.audit_service.audit_repository")
    @patch("app.services.audit_service.SupplierRepository")
    def test_south_america_bonus_applied(
        self, mock_supplier_repo_class, mock_audit_repo, service, sample_audit_data_completed
    ):
        """Test that South America experience bonus is applied."""
        mock_audit_repo.get_by_id.return_value = sample_audit_data_completed

        classified_data = sample_audit_data_completed.copy()
        classified_data["ai_classification"] = "A"
        mock_audit_repo.update_classification.return_value = classified_data

        mock_supplier_repo = MagicMock()
        mock_supplier_repo.update_certification_status.return_value = {"id": sample_audit_data_completed["supplier_id"]}
        mock_supplier_repo_class.return_value = mock_supplier_repo

        service.classify_supplier(sample_audit_data_completed["id"])

        call_args = mock_audit_repo.update_classification.call_args
        reason = call_args[1]["reason"]

        # Check that SA bonus is mentioned
        assert "South America" in reason


class TestOverrideClassification:
    """Tests for override_classification() method."""

    @patch("app.services.audit_service.audit_repository")
    @patch("app.services.audit_service.SupplierRepository")
    def test_successful_override_with_notes(
        self, mock_supplier_repo_class, mock_audit_repo, service, sample_audit_data_completed
    ):
        """Test successful override with required notes."""
        mock_audit_repo.get_by_id.return_value = sample_audit_data_completed

        override_data = sample_audit_data_completed.copy()
        override_data["manual_classification"] = "B"
        override_data["classification_notes"] = "Downgrading due to recent quality issues."
        mock_audit_repo.update_manual_classification.return_value = override_data

        mock_supplier_repo = MagicMock()
        mock_supplier_repo.update_certification_status.return_value = {"id": sample_audit_data_completed["supplier_id"]}
        mock_supplier_repo_class.return_value = mock_supplier_repo

        result = service.override_classification(
            audit_id=sample_audit_data_completed["id"],
            classification="B",
            notes="Downgrading due to recent quality issues.",
            user_id=uuid4(),
        )

        assert isinstance(result, SupplierAuditResponseDTO)
        assert result.manual_classification == "B"
        mock_audit_repo.update_manual_classification.assert_called_once()

    @patch("app.services.audit_service.audit_repository")
    def test_raises_when_notes_empty(self, mock_audit_repo, service, sample_audit_data_completed):
        """Test that override raises ValueError when notes are empty."""
        mock_audit_repo.get_by_id.return_value = sample_audit_data_completed

        with pytest.raises(ValueError, match="Notes are required"):
            service.override_classification(
                audit_id=sample_audit_data_completed["id"],
                classification="B",
                notes="",
                user_id=uuid4(),
            )

    @patch("app.services.audit_service.audit_repository")
    def test_raises_when_notes_whitespace_only(
        self, mock_audit_repo, service, sample_audit_data_completed
    ):
        """Test that override raises ValueError when notes are whitespace only."""
        mock_audit_repo.get_by_id.return_value = sample_audit_data_completed

        with pytest.raises(ValueError, match="Notes are required"):
            service.override_classification(
                audit_id=sample_audit_data_completed["id"],
                classification="B",
                notes="   ",
                user_id=uuid4(),
            )

    @patch("app.services.audit_service.audit_repository")
    def test_raises_when_audit_not_found(self, mock_audit_repo, service):
        """Test that override raises ValueError when audit not found."""
        mock_audit_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="not found"):
            service.override_classification(
                audit_id=uuid4(),
                classification="B",
                notes="Valid notes",
                user_id=uuid4(),
            )

    def test_raises_when_invalid_classification(self, service):
        """Test that override raises ValueError for invalid classification."""
        with pytest.raises(ValueError, match="Invalid classification"):
            service.override_classification(
                audit_id=uuid4(),
                classification="D",
                notes="Valid notes",
                user_id=uuid4(),
            )

    @patch("app.services.audit_service.audit_repository")
    @patch("app.services.audit_service.SupplierRepository")
    def test_supplier_status_reflects_override(
        self, mock_supplier_repo_class, mock_audit_repo, service, sample_audit_data_completed
    ):
        """Test that supplier status reflects the manual override."""
        mock_audit_repo.get_by_id.return_value = sample_audit_data_completed

        override_data = sample_audit_data_completed.copy()
        override_data["manual_classification"] = "C"
        override_data["classification_notes"] = "Critical issues discovered."
        mock_audit_repo.update_manual_classification.return_value = override_data

        mock_supplier_repo = MagicMock()
        mock_supplier_repo.update_certification_status.return_value = {"id": sample_audit_data_completed["supplier_id"]}
        mock_supplier_repo_class.return_value = mock_supplier_repo

        service.override_classification(
            audit_id=sample_audit_data_completed["id"],
            classification="C",
            notes="Critical issues discovered.",
            user_id=uuid4(),
        )

        mock_supplier_repo.update_certification_status.assert_called_once_with(
            supplier_id=sample_audit_data_completed["supplier_id"],
            certification_status=CertificationStatus.CERTIFIED_C.value,
            audit_id=sample_audit_data_completed["id"],
        )


class TestClassificationScoring:
    """Tests for classification scoring algorithm."""

    @patch("app.services.audit_service.audit_repository")
    @patch("app.services.audit_service.SupplierRepository")
    def test_all_nulls_classifies_as_type_c(
        self, mock_supplier_repo_class, mock_audit_repo, service
    ):
        """Test that audit with all nulls classifies as Type C."""
        null_audit_data = {
            "id": uuid4(),
            "supplier_id": uuid4(),
            "audit_type": "factory_audit",
            "document_url": "https://example.com/audit.pdf",
            "document_name": "factory_audit.pdf",
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
            "extraction_status": "completed",
            "extraction_raw_response": None,
            "extracted_at": datetime.utcnow(),
            "ai_classification": None,
            "ai_classification_reason": None,
            "manual_classification": None,
            "classification_notes": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        mock_audit_repo.get_by_id.return_value = null_audit_data

        classified_data = null_audit_data.copy()
        classified_data["ai_classification"] = "C"
        mock_audit_repo.update_classification.return_value = classified_data

        mock_supplier_repo = MagicMock()
        mock_supplier_repo.update_certification_status.return_value = {"id": null_audit_data["supplier_id"]}
        mock_supplier_repo_class.return_value = mock_supplier_repo

        service.classify_supplier(null_audit_data["id"])

        call_args = mock_audit_repo.update_classification.call_args
        assert call_args[1]["classification"] == "C"

    @patch("app.services.audit_service.audit_repository")
    @patch("app.services.audit_service.SupplierRepository")
    def test_manufacturer_with_certs_scores_type_a(
        self, mock_supplier_repo_class, mock_audit_repo, service
    ):
        """Test that manufacturer with 3+ certs and no negatives scores Type A."""
        good_audit_data = {
            "id": uuid4(),
            "supplier_id": uuid4(),
            "audit_type": "factory_audit",
            "document_url": "https://example.com/audit.pdf",
            "document_name": "factory_audit.pdf",
            "file_size_bytes": 1024000,
            "supplier_type": "manufacturer",
            "employee_count": 200,
            "factory_area_sqm": 5000,
            "production_lines_count": 3,
            "markets_served": {"south_america": 20},
            "certifications": ["ISO 9001", "CE", "FDA"],
            "has_machinery_photos": True,
            "positive_points": ["Good", "Quality", "Fast"],
            "negative_points": [],
            "products_verified": ["Product A"],
            "audit_date": "2024-01-15",
            "inspector_name": "Inspector",
            "extraction_status": "completed",
            "extraction_raw_response": None,
            "extracted_at": datetime.utcnow(),
            "ai_classification": None,
            "ai_classification_reason": None,
            "manual_classification": None,
            "classification_notes": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        mock_audit_repo.get_by_id.return_value = good_audit_data

        classified_data = good_audit_data.copy()
        classified_data["ai_classification"] = "A"
        mock_audit_repo.update_classification.return_value = classified_data

        mock_supplier_repo = MagicMock()
        mock_supplier_repo.update_certification_status.return_value = {"id": good_audit_data["supplier_id"]}
        mock_supplier_repo_class.return_value = mock_supplier_repo

        service.classify_supplier(good_audit_data["id"])

        call_args = mock_audit_repo.update_classification.call_args
        assert call_args[1]["classification"] == "A"


class TestUpdateSupplierCertification:
    """Tests for _update_supplier_certification helper method."""

    @patch("app.services.audit_service.SupplierRepository")
    def test_maps_a_to_certified_a(self, mock_supplier_repo_class, service):
        """Test that classification A maps to certified_a status."""
        mock_supplier_repo = MagicMock()
        mock_supplier_repo.update_certification_status.return_value = {"id": uuid4()}
        mock_supplier_repo_class.return_value = mock_supplier_repo

        supplier_id = uuid4()
        audit_id = uuid4()
        service._update_supplier_certification(supplier_id, "A", audit_id)

        mock_supplier_repo.update_certification_status.assert_called_once_with(
            supplier_id=supplier_id,
            certification_status="certified_a",
            audit_id=audit_id,
        )

    @patch("app.services.audit_service.SupplierRepository")
    def test_maps_b_to_certified_b(self, mock_supplier_repo_class, service):
        """Test that classification B maps to certified_b status."""
        mock_supplier_repo = MagicMock()
        mock_supplier_repo.update_certification_status.return_value = {"id": uuid4()}
        mock_supplier_repo_class.return_value = mock_supplier_repo

        supplier_id = uuid4()
        audit_id = uuid4()
        service._update_supplier_certification(supplier_id, "B", audit_id)

        mock_supplier_repo.update_certification_status.assert_called_once_with(
            supplier_id=supplier_id,
            certification_status="certified_b",
            audit_id=audit_id,
        )

    @patch("app.services.audit_service.SupplierRepository")
    def test_maps_c_to_certified_c(self, mock_supplier_repo_class, service):
        """Test that classification C maps to certified_c status."""
        mock_supplier_repo = MagicMock()
        mock_supplier_repo.update_certification_status.return_value = {"id": uuid4()}
        mock_supplier_repo_class.return_value = mock_supplier_repo

        supplier_id = uuid4()
        audit_id = uuid4()
        service._update_supplier_certification(supplier_id, "C", audit_id)

        mock_supplier_repo.update_certification_status.assert_called_once_with(
            supplier_id=supplier_id,
            certification_status="certified_c",
            audit_id=audit_id,
        )
