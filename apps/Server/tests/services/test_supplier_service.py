"""Unit tests for SupplierService."""

from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

import pytest

from app.models.kompass_dto import (
    SupplierCreateDTO,
    SupplierStatus,
    SupplierUpdateDTO,
)
from app.services.supplier_service import SupplierService


@pytest.fixture
def supplier_service():
    """Create a fresh SupplierService instance for each test."""
    return SupplierService()


@pytest.fixture
def sample_supplier_data():
    """Sample supplier data for testing."""
    return {
        "id": uuid4(),
        "name": "Test Supplier",
        "code": "TS001",
        "status": "active",
        "contact_name": "John Doe",
        "contact_email": "john@example.com",
        "contact_phone": "123456789",
        "address": "123 Test Street",
        "city": "Shanghai",
        "country": "China",
        "website": "https://example.com",
        "notes": "Test notes",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


class TestEmailValidation:
    """Tests for email validation helper method."""

    def test_valid_email(self, supplier_service):
        """Test that valid email addresses pass validation."""
        assert supplier_service._validate_email("test@example.com") is True
        assert supplier_service._validate_email("user.name@domain.co") is True
        assert supplier_service._validate_email("user+tag@example.org") is True

    def test_invalid_email(self, supplier_service):
        """Test that invalid email addresses fail validation."""
        assert supplier_service._validate_email("invalid") is False
        assert supplier_service._validate_email("@example.com") is False
        assert supplier_service._validate_email("test@") is False
        assert supplier_service._validate_email("test@.com") is False

    def test_empty_email_allowed(self, supplier_service):
        """Test that empty email is allowed (optional field)."""
        assert supplier_service._validate_email("") is True
        assert supplier_service._validate_email(None) is True


class TestWechatNormalization:
    """Tests for WeChat ID normalization helper method."""

    def test_normalize_lowercase(self, supplier_service):
        """Test that WeChat IDs are converted to lowercase."""
        assert supplier_service._normalize_wechat_id("TestID") == "testid"
        assert supplier_service._normalize_wechat_id("UPPERCASE") == "uppercase"

    def test_normalize_strips_whitespace(self, supplier_service):
        """Test that whitespace is stripped from WeChat IDs."""
        assert supplier_service._normalize_wechat_id("  test  ") == "test"
        assert supplier_service._normalize_wechat_id("\ttab\n") == "tab"

    def test_normalize_empty_returns_none(self, supplier_service):
        """Test that empty or None values are returned as-is."""
        assert supplier_service._normalize_wechat_id(None) is None
        assert supplier_service._normalize_wechat_id("") == ""


class TestCreateSupplier:
    """Tests for create_supplier method."""

    @patch("app.services.supplier_service.supplier_repository")
    def test_create_supplier_success(
        self, mock_repo, supplier_service, sample_supplier_data
    ):
        """Test successful supplier creation."""
        mock_repo.create.return_value = sample_supplier_data

        request = SupplierCreateDTO(
            name="Test Supplier",
            code="TS001",
            contact_email="test@example.com",
        )

        result = supplier_service.create_supplier(request)

        assert result.name == "Test Supplier"
        assert result.code == "TS001"
        mock_repo.create.assert_called_once()

    @patch("app.services.supplier_service.supplier_repository")
    def test_create_supplier_with_wechat_normalized(
        self, mock_repo, supplier_service, sample_supplier_data
    ):
        """Test that contact_phone (WeChat) is normalized on create."""
        sample_supplier_data["contact_phone"] = "wechatid"
        mock_repo.create.return_value = sample_supplier_data

        request = SupplierCreateDTO(
            name="Test Supplier",
            contact_phone="  WeChaTID  ",
        )

        supplier_service.create_supplier(request)

        # Check that the normalized value was passed to repository
        call_kwargs = mock_repo.create.call_args.kwargs
        assert call_kwargs["contact_phone"] == "wechatid"

    @patch("app.services.supplier_service.supplier_repository")
    def test_create_supplier_fails(self, mock_repo, supplier_service):
        """Test that ValueError is raised when creation fails."""
        mock_repo.create.return_value = None

        request = SupplierCreateDTO(name="Test Supplier")

        with pytest.raises(ValueError, match="Failed to create supplier"):
            supplier_service.create_supplier(request)


class TestGetSupplier:
    """Tests for get_supplier method."""

    @patch("app.services.supplier_service.supplier_repository")
    def test_get_supplier_found(
        self, mock_repo, supplier_service, sample_supplier_data
    ):
        """Test getting an existing supplier."""
        mock_repo.get_by_id.return_value = sample_supplier_data
        supplier_id = sample_supplier_data["id"]

        result = supplier_service.get_supplier(supplier_id)

        assert result is not None
        assert result.id == supplier_id
        mock_repo.get_by_id.assert_called_once_with(supplier_id)

    @patch("app.services.supplier_service.supplier_repository")
    def test_get_supplier_not_found(self, mock_repo, supplier_service):
        """Test that None is returned for non-existent supplier."""
        mock_repo.get_by_id.return_value = None
        supplier_id = uuid4()

        result = supplier_service.get_supplier(supplier_id)

        assert result is None


class TestListSuppliers:
    """Tests for list_suppliers method."""

    @patch("app.services.supplier_service.supplier_repository")
    def test_list_suppliers_with_pagination(
        self, mock_repo, supplier_service, sample_supplier_data
    ):
        """Test listing suppliers with pagination."""
        mock_repo.get_all_with_filters.return_value = ([sample_supplier_data], 1)

        result = supplier_service.list_suppliers(page=1, limit=20)

        assert len(result.items) == 1
        assert result.pagination.page == 1
        assert result.pagination.limit == 20
        assert result.pagination.total == 1
        assert result.pagination.pages == 1

    @patch("app.services.supplier_service.supplier_repository")
    def test_list_suppliers_with_status_filter(
        self, mock_repo, supplier_service, sample_supplier_data
    ):
        """Test filtering suppliers by status."""
        mock_repo.get_all_with_filters.return_value = ([sample_supplier_data], 1)

        supplier_service.list_suppliers(status=SupplierStatus.ACTIVE)

        call_kwargs = mock_repo.get_all_with_filters.call_args.kwargs
        assert call_kwargs["status"] == "active"

    @patch("app.services.supplier_service.supplier_repository")
    def test_list_suppliers_with_country_filter(
        self, mock_repo, supplier_service, sample_supplier_data
    ):
        """Test filtering suppliers by country."""
        mock_repo.get_all_with_filters.return_value = ([sample_supplier_data], 1)

        supplier_service.list_suppliers(country="China")

        call_kwargs = mock_repo.get_all_with_filters.call_args.kwargs
        assert call_kwargs["country"] == "China"

    @patch("app.services.supplier_service.supplier_repository")
    def test_list_suppliers_with_has_products_filter(
        self, mock_repo, supplier_service, sample_supplier_data
    ):
        """Test filtering suppliers by has_products."""
        mock_repo.get_all_with_filters.return_value = ([sample_supplier_data], 1)

        supplier_service.list_suppliers(has_products=True)

        call_kwargs = mock_repo.get_all_with_filters.call_args.kwargs
        assert call_kwargs["has_products"] is True

    @patch("app.services.supplier_service.supplier_repository")
    def test_list_suppliers_empty_result(self, mock_repo, supplier_service):
        """Test empty result handling."""
        mock_repo.get_all_with_filters.return_value = ([], 0)

        result = supplier_service.list_suppliers()

        assert len(result.items) == 0
        assert result.pagination.total == 0
        assert result.pagination.pages == 0


class TestUpdateSupplier:
    """Tests for update_supplier method."""

    @patch("app.services.supplier_service.supplier_repository")
    def test_update_supplier_success(
        self, mock_repo, supplier_service, sample_supplier_data
    ):
        """Test successful supplier update."""
        mock_repo.get_by_id.return_value = sample_supplier_data
        updated_data = sample_supplier_data.copy()
        updated_data["name"] = "Updated Name"
        mock_repo.update.return_value = updated_data

        supplier_id = sample_supplier_data["id"]
        request = SupplierUpdateDTO(name="Updated Name")

        result = supplier_service.update_supplier(supplier_id, request)

        assert result is not None
        assert result.name == "Updated Name"

    @patch("app.services.supplier_service.supplier_repository")
    def test_update_supplier_not_found(self, mock_repo, supplier_service):
        """Test updating non-existent supplier returns None."""
        mock_repo.get_by_id.return_value = None
        supplier_id = uuid4()

        result = supplier_service.update_supplier(
            supplier_id, SupplierUpdateDTO(name="Test")
        )

        assert result is None
        mock_repo.update.assert_not_called()

    @patch("app.services.supplier_service.supplier_repository")
    def test_update_supplier_normalizes_wechat(
        self, mock_repo, supplier_service, sample_supplier_data
    ):
        """Test that contact_phone is normalized on update."""
        mock_repo.get_by_id.return_value = sample_supplier_data
        updated_data = sample_supplier_data.copy()
        updated_data["contact_phone"] = "normalizedid"
        mock_repo.update.return_value = updated_data

        supplier_id = sample_supplier_data["id"]
        request = SupplierUpdateDTO(contact_phone="  NormalizedID  ")

        supplier_service.update_supplier(supplier_id, request)

        call_kwargs = mock_repo.update.call_args.kwargs
        assert call_kwargs["contact_phone"] == "normalizedid"


class TestDeleteSupplier:
    """Tests for delete_supplier method (hard delete)."""

    @patch("app.services.supplier_service.supplier_repository")
    def test_delete_supplier_success(
        self, mock_supplier_repo, supplier_service, sample_supplier_data
    ):
        """Test successful hard delete with returned counts."""
        mock_supplier_repo.get_by_id.return_value = sample_supplier_data
        mock_supplier_repo.delete.return_value = {
            "deleted": True,
            "products_deleted": 3,
            "audits_deleted": 1,
        }

        supplier_id = sample_supplier_data["id"]
        result = supplier_service.delete_supplier(supplier_id)

        assert result is not None
        assert result["deleted"] is True
        assert result["products_deleted"] == 3
        assert result["audits_deleted"] == 1
        mock_supplier_repo.delete.assert_called_once_with(supplier_id)

    @patch("app.services.supplier_service.supplier_repository")
    def test_delete_supplier_not_found(
        self, mock_supplier_repo, supplier_service
    ):
        """Test deleting non-existent supplier returns None."""
        mock_supplier_repo.get_by_id.return_value = None
        supplier_id = uuid4()

        result = supplier_service.delete_supplier(supplier_id)

        assert result is None
        mock_supplier_repo.delete.assert_not_called()

    @patch("app.services.supplier_service.supplier_repository")
    def test_delete_supplier_no_associated_data(
        self, mock_supplier_repo, supplier_service, sample_supplier_data
    ):
        """Test hard delete of supplier with no products or audits."""
        mock_supplier_repo.get_by_id.return_value = sample_supplier_data
        mock_supplier_repo.delete.return_value = {
            "deleted": True,
            "products_deleted": 0,
            "audits_deleted": 0,
        }

        supplier_id = sample_supplier_data["id"]
        result = supplier_service.delete_supplier(supplier_id)

        assert result is not None
        assert result["products_deleted"] == 0
        assert result["audits_deleted"] == 0

    @patch("app.services.supplier_service.supplier_repository")
    def test_delete_preview(
        self, mock_supplier_repo, supplier_service, sample_supplier_data
    ):
        """Test get_delete_preview returns correct counts."""
        mock_supplier_repo.get_delete_preview.return_value = {
            "supplier_name": "Test Supplier",
            "products_count": 5,
            "audits_count": 2,
        }

        supplier_id = sample_supplier_data["id"]
        result = supplier_service.get_delete_preview(supplier_id)

        assert result is not None
        assert result["supplier_name"] == "Test Supplier"
        assert result["products_count"] == 5
        assert result["audits_count"] == 2
        mock_supplier_repo.get_delete_preview.assert_called_once_with(supplier_id)

    @patch("app.services.supplier_service.supplier_repository")
    def test_delete_preview_not_found(
        self, mock_supplier_repo, supplier_service
    ):
        """Test get_delete_preview returns None for non-existent supplier."""
        mock_supplier_repo.get_delete_preview.return_value = None

        result = supplier_service.get_delete_preview(uuid4())

        assert result is None


class TestSearchSuppliers:
    """Tests for search_suppliers method."""

    @patch("app.services.supplier_service.supplier_repository")
    def test_search_suppliers_returns_matches(
        self, mock_repo, supplier_service, sample_supplier_data
    ):
        """Test that search returns matching suppliers."""
        mock_repo.search.return_value = [sample_supplier_data]

        result = supplier_service.search_suppliers("Test")

        assert len(result) == 1
        assert result[0].name == "Test Supplier"
        mock_repo.search.assert_called_once_with(query="Test", limit=50)

    @patch("app.services.supplier_service.supplier_repository")
    def test_search_suppliers_empty_query_returns_empty(
        self, mock_repo, supplier_service
    ):
        """Test that empty query returns empty list."""
        result = supplier_service.search_suppliers("")

        assert result == []
        mock_repo.search.assert_not_called()

    @patch("app.services.supplier_service.supplier_repository")
    def test_search_suppliers_short_query_returns_empty(
        self, mock_repo, supplier_service
    ):
        """Test that single character query returns empty list."""
        result = supplier_service.search_suppliers("a")

        assert result == []
        mock_repo.search.assert_not_called()

    @patch("app.services.supplier_service.supplier_repository")
    def test_search_suppliers_no_matches(self, mock_repo, supplier_service):
        """Test that search with no matches returns empty list."""
        mock_repo.search.return_value = []

        result = supplier_service.search_suppliers("nonexistent")

        assert result == []

    @patch("app.services.supplier_service.supplier_repository")
    def test_search_suppliers_strips_query(self, mock_repo, supplier_service):
        """Test that search query is stripped of whitespace."""
        mock_repo.search.return_value = []

        supplier_service.search_suppliers("  test  ")

        mock_repo.search.assert_called_once_with(query="test", limit=50)
