"""Unit tests for supplier certification and pipeline endpoints."""

from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

import pytest

from app.models.kompass_dto import (
    SupplierCertificationSummaryDTO,
    SupplierListResponseDTO,
    SupplierPipelineStatus,
    SupplierResponseDTO,
)
from app.services.supplier_service import SupplierService


@pytest.fixture
def service():
    """Create a fresh SupplierService instance for each test."""
    return SupplierService()


@pytest.fixture
def sample_supplier_data():
    """Create sample supplier data."""
    return {
        "id": uuid4(),
        "name": "Test Supplier",
        "code": "SUP001",
        "status": "active",
        "contact_name": "John Doe",
        "contact_email": "john@supplier.com",
        "contact_phone": "+86123456789",
        "address": "123 Factory St",
        "city": "Shenzhen",
        "country": "China",
        "website": "https://supplier.com",
        "notes": "Test notes",
        "certification_status": "certified_a",
        "pipeline_status": "certified",
        "latest_audit_id": uuid4(),
        "certified_at": datetime.utcnow(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


@pytest.fixture
def sample_certification_summary_data():
    """Create sample certification summary data."""
    return {
        "id": uuid4(),
        "name": "Test Supplier",
        "code": "SUP001",
        "status": "active",
        "country": "China",
        "certification_status": "certified_a",
        "pipeline_status": "certified",
        "certified_at": datetime.utcnow(),
        "latest_audit_id": uuid4(),
        "latest_audit_date": datetime.utcnow().date(),
        "ai_classification": "A",
        "manual_classification": None,
    }


class TestListCertifiedSuppliers:
    """Tests for list_certified_suppliers() method."""

    @patch("app.services.supplier_service.supplier_repository")
    def test_returns_certified_suppliers(
        self, mock_repo, service, sample_supplier_data
    ):
        """Test that list_certified_suppliers returns certified suppliers."""
        mock_repo.get_by_certification_status.return_value = (
            [sample_supplier_data],
            1,
        )

        result = service.list_certified_suppliers(page=1, limit=20)

        assert isinstance(result, SupplierListResponseDTO)
        assert len(result.items) == 1
        assert result.pagination.total == 1
        mock_repo.get_by_certification_status.assert_called_once_with(
            grade=None,
            page=1,
            limit=20,
        )

    @patch("app.services.supplier_service.supplier_repository")
    def test_filters_by_grade_a(self, mock_repo, service, sample_supplier_data):
        """Test filtering by grade A."""
        mock_repo.get_by_certification_status.return_value = (
            [sample_supplier_data],
            1,
        )

        result = service.list_certified_suppliers(grade="A", page=1, limit=20)

        assert isinstance(result, SupplierListResponseDTO)
        mock_repo.get_by_certification_status.assert_called_once_with(
            grade="A",
            page=1,
            limit=20,
        )

    @patch("app.services.supplier_service.supplier_repository")
    def test_filters_by_grade_b(self, mock_repo, service, sample_supplier_data):
        """Test filtering by grade B."""
        sample_supplier_data["certification_status"] = "certified_b"
        mock_repo.get_by_certification_status.return_value = (
            [sample_supplier_data],
            1,
        )

        result = service.list_certified_suppliers(grade="B", page=1, limit=20)

        assert isinstance(result, SupplierListResponseDTO)
        mock_repo.get_by_certification_status.assert_called_once_with(
            grade="B",
            page=1,
            limit=20,
        )

    @patch("app.services.supplier_service.supplier_repository")
    def test_filters_by_grade_c(self, mock_repo, service, sample_supplier_data):
        """Test filtering by grade C."""
        sample_supplier_data["certification_status"] = "certified_c"
        mock_repo.get_by_certification_status.return_value = (
            [sample_supplier_data],
            1,
        )

        result = service.list_certified_suppliers(grade="C", page=1, limit=20)

        assert isinstance(result, SupplierListResponseDTO)
        mock_repo.get_by_certification_status.assert_called_once_with(
            grade="C",
            page=1,
            limit=20,
        )

    def test_raises_on_invalid_grade(self, service):
        """Test that invalid grade raises ValueError."""
        with pytest.raises(ValueError, match="Invalid grade"):
            service.list_certified_suppliers(grade="X", page=1, limit=20)

    @patch("app.services.supplier_service.supplier_repository")
    def test_returns_empty_list_when_no_certified_suppliers(self, mock_repo, service):
        """Test that empty list is returned when no certified suppliers exist."""
        mock_repo.get_by_certification_status.return_value = ([], 0)

        result = service.list_certified_suppliers(page=1, limit=20)

        assert isinstance(result, SupplierListResponseDTO)
        assert len(result.items) == 0
        assert result.pagination.total == 0


class TestListSuppliersByPipeline:
    """Tests for list_suppliers_by_pipeline() method."""

    @patch("app.services.supplier_service.supplier_repository")
    def test_returns_suppliers_by_pipeline_contacted(
        self, mock_repo, service, sample_supplier_data
    ):
        """Test filtering by contacted pipeline status."""
        sample_supplier_data["pipeline_status"] = "contacted"
        mock_repo.get_by_pipeline_status.return_value = ([sample_supplier_data], 1)

        result = service.list_suppliers_by_pipeline(
            pipeline_status=SupplierPipelineStatus.CONTACTED,
            page=1,
            limit=20,
        )

        assert isinstance(result, SupplierListResponseDTO)
        assert len(result.items) == 1
        mock_repo.get_by_pipeline_status.assert_called_once_with(
            pipeline_status="contacted",
            page=1,
            limit=20,
        )

    @patch("app.services.supplier_service.supplier_repository")
    def test_returns_suppliers_by_pipeline_potential(
        self, mock_repo, service, sample_supplier_data
    ):
        """Test filtering by potential pipeline status."""
        sample_supplier_data["pipeline_status"] = "potential"
        mock_repo.get_by_pipeline_status.return_value = ([sample_supplier_data], 1)

        result = service.list_suppliers_by_pipeline(
            pipeline_status=SupplierPipelineStatus.POTENTIAL,
            page=1,
            limit=20,
        )

        assert isinstance(result, SupplierListResponseDTO)
        mock_repo.get_by_pipeline_status.assert_called_once_with(
            pipeline_status="potential",
            page=1,
            limit=20,
        )

    @patch("app.services.supplier_service.supplier_repository")
    def test_returns_suppliers_by_pipeline_quoted(
        self, mock_repo, service, sample_supplier_data
    ):
        """Test filtering by quoted pipeline status."""
        sample_supplier_data["pipeline_status"] = "quoted"
        mock_repo.get_by_pipeline_status.return_value = ([sample_supplier_data], 1)

        result = service.list_suppliers_by_pipeline(
            pipeline_status=SupplierPipelineStatus.QUOTED,
            page=1,
            limit=20,
        )

        assert isinstance(result, SupplierListResponseDTO)
        mock_repo.get_by_pipeline_status.assert_called_once_with(
            pipeline_status="quoted",
            page=1,
            limit=20,
        )

    @patch("app.services.supplier_service.supplier_repository")
    def test_returns_suppliers_by_pipeline_certified(
        self, mock_repo, service, sample_supplier_data
    ):
        """Test filtering by certified pipeline status."""
        sample_supplier_data["pipeline_status"] = "certified"
        mock_repo.get_by_pipeline_status.return_value = ([sample_supplier_data], 1)

        result = service.list_suppliers_by_pipeline(
            pipeline_status=SupplierPipelineStatus.CERTIFIED,
            page=1,
            limit=20,
        )

        assert isinstance(result, SupplierListResponseDTO)
        mock_repo.get_by_pipeline_status.assert_called_once_with(
            pipeline_status="certified",
            page=1,
            limit=20,
        )

    @patch("app.services.supplier_service.supplier_repository")
    def test_returns_suppliers_by_pipeline_active(
        self, mock_repo, service, sample_supplier_data
    ):
        """Test filtering by active pipeline status."""
        sample_supplier_data["pipeline_status"] = "active"
        mock_repo.get_by_pipeline_status.return_value = ([sample_supplier_data], 1)

        result = service.list_suppliers_by_pipeline(
            pipeline_status=SupplierPipelineStatus.ACTIVE,
            page=1,
            limit=20,
        )

        assert isinstance(result, SupplierListResponseDTO)
        mock_repo.get_by_pipeline_status.assert_called_once_with(
            pipeline_status="active",
            page=1,
            limit=20,
        )

    @patch("app.services.supplier_service.supplier_repository")
    def test_returns_suppliers_by_pipeline_inactive(
        self, mock_repo, service, sample_supplier_data
    ):
        """Test filtering by inactive pipeline status."""
        sample_supplier_data["pipeline_status"] = "inactive"
        mock_repo.get_by_pipeline_status.return_value = ([sample_supplier_data], 1)

        result = service.list_suppliers_by_pipeline(
            pipeline_status=SupplierPipelineStatus.INACTIVE,
            page=1,
            limit=20,
        )

        assert isinstance(result, SupplierListResponseDTO)
        mock_repo.get_by_pipeline_status.assert_called_once_with(
            pipeline_status="inactive",
            page=1,
            limit=20,
        )

    @patch("app.services.supplier_service.supplier_repository")
    def test_returns_empty_list_when_no_suppliers(self, mock_repo, service):
        """Test that empty list is returned when no suppliers match."""
        mock_repo.get_by_pipeline_status.return_value = ([], 0)

        result = service.list_suppliers_by_pipeline(
            pipeline_status=SupplierPipelineStatus.CONTACTED,
            page=1,
            limit=20,
        )

        assert isinstance(result, SupplierListResponseDTO)
        assert len(result.items) == 0
        assert result.pagination.total == 0


class TestUpdatePipelineStatus:
    """Tests for update_pipeline_status() method."""

    @patch("app.services.supplier_service.supplier_repository")
    def test_updates_pipeline_status_successfully(
        self, mock_repo, service, sample_supplier_data
    ):
        """Test successful pipeline status update."""
        mock_repo.get_by_id.return_value = sample_supplier_data
        updated_data = sample_supplier_data.copy()
        updated_data["pipeline_status"] = "active"
        mock_repo.update_pipeline_status.return_value = updated_data

        result = service.update_pipeline_status(
            supplier_id=sample_supplier_data["id"],
            pipeline_status=SupplierPipelineStatus.ACTIVE,
        )

        assert isinstance(result, SupplierResponseDTO)
        mock_repo.update_pipeline_status.assert_called_once_with(
            supplier_id=sample_supplier_data["id"],
            pipeline_status="active",
        )

    @patch("app.services.supplier_service.supplier_repository")
    def test_returns_none_when_supplier_not_found(self, mock_repo, service):
        """Test that None is returned when supplier not found."""
        mock_repo.get_by_id.return_value = None

        result = service.update_pipeline_status(
            supplier_id=uuid4(),
            pipeline_status=SupplierPipelineStatus.ACTIVE,
        )

        assert result is None
        mock_repo.update_pipeline_status.assert_not_called()

    @patch("app.services.supplier_service.supplier_repository")
    def test_returns_none_when_update_fails(
        self, mock_repo, service, sample_supplier_data
    ):
        """Test that None is returned when update fails."""
        mock_repo.get_by_id.return_value = sample_supplier_data
        mock_repo.update_pipeline_status.return_value = None

        result = service.update_pipeline_status(
            supplier_id=sample_supplier_data["id"],
            pipeline_status=SupplierPipelineStatus.ACTIVE,
        )

        assert result is None


class TestGetCertificationSummary:
    """Tests for get_certification_summary() method."""

    @patch("app.services.supplier_service.supplier_repository")
    def test_returns_certification_summary_with_audit(
        self, mock_repo, service, sample_certification_summary_data
    ):
        """Test that certification summary is returned with audit data."""
        mock_repo.get_with_certification_details.return_value = (
            sample_certification_summary_data
        )

        result = service.get_certification_summary(sample_certification_summary_data["id"])

        assert isinstance(result, SupplierCertificationSummaryDTO)
        assert result.ai_classification == "A"
        assert result.latest_audit_id is not None
        mock_repo.get_with_certification_details.assert_called_once_with(
            sample_certification_summary_data["id"]
        )

    @patch("app.services.supplier_service.supplier_repository")
    def test_returns_certification_summary_without_audit(self, mock_repo, service):
        """Test that certification summary is returned with null audit fields."""
        supplier_id = uuid4()
        summary_data = {
            "id": supplier_id,
            "name": "Test Supplier",
            "code": "SUP001",
            "status": "active",
            "country": "China",
            "certification_status": "uncertified",
            "pipeline_status": "contacted",
            "certified_at": None,
            "latest_audit_id": None,
            "latest_audit_date": None,
            "ai_classification": None,
            "manual_classification": None,
        }
        mock_repo.get_with_certification_details.return_value = summary_data

        result = service.get_certification_summary(supplier_id)

        assert isinstance(result, SupplierCertificationSummaryDTO)
        assert result.latest_audit_id is None
        assert result.ai_classification is None
        assert result.certified_at is None

    @patch("app.services.supplier_service.supplier_repository")
    def test_returns_none_when_supplier_not_found(self, mock_repo, service):
        """Test that None is returned when supplier not found."""
        mock_repo.get_with_certification_details.return_value = None

        result = service.get_certification_summary(uuid4())

        assert result is None


class TestPaginationCalculation:
    """Tests for pagination calculation in listing methods."""

    @patch("app.services.supplier_service.supplier_repository")
    def test_calculates_pages_correctly(
        self, mock_repo, service, sample_supplier_data
    ):
        """Test that pages are calculated correctly."""
        # 45 total items with limit 20 = 3 pages
        mock_repo.get_by_certification_status.return_value = (
            [sample_supplier_data],
            45,
        )

        result = service.list_certified_suppliers(page=1, limit=20)

        assert result.pagination.pages == 3
        assert result.pagination.total == 45
        assert result.pagination.limit == 20

    @patch("app.services.supplier_service.supplier_repository")
    def test_handles_zero_total(self, mock_repo, service):
        """Test that zero total results in zero pages."""
        mock_repo.get_by_certification_status.return_value = ([], 0)

        result = service.list_certified_suppliers(page=1, limit=20)

        assert result.pagination.pages == 0
        assert result.pagination.total == 0
