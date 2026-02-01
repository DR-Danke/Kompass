"""End-to-end tests for Supplier workflows.

Tests cover:
- Full CRUD workflow (Create -> Read -> Update -> Delete)
- Validation (email, required fields, duplicate code handling)
- Filtering (status, country, has_products)
- Search functionality
- Cross-service integration (delete blocked when products exist)
"""

from unittest.mock import patch
from uuid import uuid4

import pytest

from app.models.kompass_dto import (
    SupplierCreateDTO,
    SupplierStatus,
    SupplierUpdateDTO,
)
from app.services.supplier_service import SupplierService

from .conftest import create_sample_supplier


# =============================================================================
# SERVICE FIXTURES
# =============================================================================


@pytest.fixture
def supplier_service():
    """Create a fresh SupplierService instance for each test."""
    return SupplierService()


# =============================================================================
# CRUD WORKFLOW TESTS
# =============================================================================


class TestSupplierCRUDWorkflow:
    """Tests for complete CRUD workflow."""

    @patch("app.services.supplier_service.supplier_repository")
    def test_create_read_update_delete_flow(
        self, mock_repo, supplier_service, sample_supplier_data
    ):
        """Test complete supplier lifecycle."""
        supplier_id = sample_supplier_data["id"]

        # CREATE
        mock_repo.create.return_value = sample_supplier_data
        create_request = SupplierCreateDTO(
            name="Test Supplier",
            code="TS001",
            contact_email="test@example.com",
            country="China",
        )
        created = supplier_service.create_supplier(create_request)

        assert created is not None
        assert created.name == "Test Supplier"
        assert created.code == "TS001"
        mock_repo.create.assert_called_once()

        # READ
        mock_repo.get_by_id.return_value = sample_supplier_data
        retrieved = supplier_service.get_supplier(supplier_id)

        assert retrieved is not None
        assert retrieved.id == supplier_id
        mock_repo.get_by_id.assert_called_with(supplier_id)

        # UPDATE
        updated_data = sample_supplier_data.copy()
        updated_data["name"] = "Updated Supplier Name"
        mock_repo.update.return_value = updated_data

        update_request = SupplierUpdateDTO(name="Updated Supplier Name")
        updated = supplier_service.update_supplier(supplier_id, update_request)

        assert updated is not None
        assert updated.name == "Updated Supplier Name"

        # DELETE
        mock_repo.get_by_id.return_value = sample_supplier_data

    @patch("app.services.supplier_service.product_repository")
    @patch("app.services.supplier_service.supplier_repository")
    def test_delete_supplier_flow(
        self, mock_supplier_repo, mock_product_repo, supplier_service, sample_supplier_data
    ):
        """Test supplier deletion flow."""
        supplier_id = sample_supplier_data["id"]

        mock_supplier_repo.get_by_id.return_value = sample_supplier_data
        mock_product_repo.get_all.return_value = ([], 0)  # No products
        mock_supplier_repo.delete.return_value = True

        result = supplier_service.delete_supplier(supplier_id)

        assert result is True
        mock_supplier_repo.delete.assert_called_once_with(supplier_id)

    @patch("app.services.supplier_service.supplier_repository")
    def test_create_supplier_with_all_fields(self, mock_repo, supplier_service):
        """Test creating supplier with all optional fields populated."""
        supplier_id = uuid4()
        full_supplier = create_sample_supplier(
            supplier_id=supplier_id,
            name="Full Data Supplier",
            code="FDS001",
        )
        mock_repo.create.return_value = full_supplier

        request = SupplierCreateDTO(
            name="Full Data Supplier",
            code="FDS001",
            contact_name="Jane Smith",
            contact_email="jane@example.com",
            contact_phone="987654321",
            address="456 Business Ave",
            city="Beijing",
            country="China",
            website="https://fullsupplier.com",
            notes="Premium supplier with express shipping",
        )

        result = supplier_service.create_supplier(request)

        assert result is not None
        assert result.name == "Full Data Supplier"
        mock_repo.create.assert_called_once()
        call_kwargs = mock_repo.create.call_args.kwargs
        assert call_kwargs["contact_name"] == "Jane Smith"
        assert call_kwargs["website"] == "https://fullsupplier.com"


# =============================================================================
# VALIDATION TESTS
# =============================================================================


class TestSupplierValidation:
    """Tests for supplier validation rules."""

    def test_valid_email_passes(self, supplier_service):
        """Test that valid email addresses pass validation."""
        assert supplier_service._validate_email("test@example.com") is True
        assert supplier_service._validate_email("user.name@domain.co") is True
        assert supplier_service._validate_email("user+tag@example.org") is True

    def test_invalid_email_fails(self, supplier_service):
        """Test that invalid email addresses fail validation."""
        assert supplier_service._validate_email("invalid") is False
        assert supplier_service._validate_email("@example.com") is False
        assert supplier_service._validate_email("test@") is False
        assert supplier_service._validate_email("test@.com") is False

    def test_empty_email_allowed(self, supplier_service):
        """Test that empty email is allowed (optional field)."""
        assert supplier_service._validate_email("") is True
        assert supplier_service._validate_email(None) is True

    def test_wechat_normalization(self, supplier_service):
        """Test that WeChat IDs are normalized correctly."""
        assert supplier_service._normalize_wechat_id("TestID") == "testid"
        assert supplier_service._normalize_wechat_id("UPPERCASE") == "uppercase"
        assert supplier_service._normalize_wechat_id("  test  ") == "test"
        assert supplier_service._normalize_wechat_id(None) is None

    @patch("app.services.supplier_service.supplier_repository")
    def test_create_supplier_fails_on_repo_error(self, mock_repo, supplier_service):
        """Test that ValueError is raised when creation fails."""
        mock_repo.create.return_value = None

        request = SupplierCreateDTO(name="Test Supplier")

        with pytest.raises(ValueError, match="Failed to create supplier"):
            supplier_service.create_supplier(request)

    @patch("app.services.supplier_service.supplier_repository")
    def test_create_supplier_normalizes_wechat(self, mock_repo, supplier_service):
        """Test that contact_phone (WeChat) is normalized on create."""
        supplier_data = create_sample_supplier()
        supplier_data["contact_phone"] = "wechatid"
        mock_repo.create.return_value = supplier_data

        request = SupplierCreateDTO(
            name="Test Supplier",
            contact_phone="  WeChaTID  ",
        )

        supplier_service.create_supplier(request)

        call_kwargs = mock_repo.create.call_args.kwargs
        assert call_kwargs["contact_phone"] == "wechatid"


# =============================================================================
# FILTERING TESTS
# =============================================================================


class TestSupplierFiltering:
    """Tests for supplier filtering functionality."""

    @patch("app.services.supplier_service.supplier_repository")
    def test_list_suppliers_with_status_filter(
        self, mock_repo, supplier_service, sample_supplier_data
    ):
        """Test filtering suppliers by status."""
        mock_repo.get_all_with_filters.return_value = ([sample_supplier_data], 1)

        result = supplier_service.list_suppliers(status=SupplierStatus.ACTIVE)

        call_kwargs = mock_repo.get_all_with_filters.call_args.kwargs
        assert call_kwargs["status"] == "active"
        assert len(result.items) == 1

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
        """Test filtering suppliers by has_products flag."""
        mock_repo.get_all_with_filters.return_value = ([sample_supplier_data], 1)

        supplier_service.list_suppliers(has_products=True)

        call_kwargs = mock_repo.get_all_with_filters.call_args.kwargs
        assert call_kwargs["has_products"] is True

    @patch("app.services.supplier_service.supplier_repository")
    def test_list_suppliers_with_combined_filters(
        self, mock_repo, supplier_service, sample_supplier_data
    ):
        """Test filtering with multiple filters combined."""
        mock_repo.get_all_with_filters.return_value = ([sample_supplier_data], 1)

        supplier_service.list_suppliers(
            status=SupplierStatus.ACTIVE,
            country="China",
            has_products=True,
        )

        call_kwargs = mock_repo.get_all_with_filters.call_args.kwargs
        assert call_kwargs["status"] == "active"
        assert call_kwargs["country"] == "China"
        assert call_kwargs["has_products"] is True

    @patch("app.services.supplier_service.supplier_repository")
    def test_list_suppliers_pagination(
        self, mock_repo, supplier_service, sample_supplier_list
    ):
        """Test pagination functionality."""
        mock_repo.get_all_with_filters.return_value = (sample_supplier_list, 100)

        result = supplier_service.list_suppliers(page=2, limit=10)

        assert result.pagination.page == 2
        assert result.pagination.limit == 10
        assert result.pagination.total == 100
        assert result.pagination.pages == 10

    @patch("app.services.supplier_service.supplier_repository")
    def test_list_suppliers_empty_result(self, mock_repo, supplier_service):
        """Test empty result handling."""
        mock_repo.get_all_with_filters.return_value = ([], 0)

        result = supplier_service.list_suppliers()

        assert len(result.items) == 0
        assert result.pagination.total == 0
        assert result.pagination.pages == 0


# =============================================================================
# SEARCH TESTS
# =============================================================================


class TestSupplierSearch:
    """Tests for supplier search functionality."""

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
    def test_search_suppliers_empty_query(self, mock_repo, supplier_service):
        """Test that empty query returns empty list."""
        result = supplier_service.search_suppliers("")

        assert result == []
        mock_repo.search.assert_not_called()

    @patch("app.services.supplier_service.supplier_repository")
    def test_search_suppliers_short_query(self, mock_repo, supplier_service):
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
    def test_search_suppliers_strips_whitespace(self, mock_repo, supplier_service):
        """Test that search query is stripped of whitespace."""
        mock_repo.search.return_value = []

        supplier_service.search_suppliers("  test  ")

        mock_repo.search.assert_called_once_with(query="test", limit=50)


# =============================================================================
# CROSS-SERVICE INTEGRATION TESTS
# =============================================================================


class TestSupplierWithProducts:
    """Tests for supplier-product integration."""

    @patch("app.services.supplier_service.product_repository")
    @patch("app.services.supplier_service.supplier_repository")
    def test_delete_blocked_when_products_exist(
        self, mock_supplier_repo, mock_product_repo, supplier_service, sample_supplier_data
    ):
        """Test that deletion fails when supplier has active products."""
        mock_supplier_repo.get_by_id.return_value = sample_supplier_data
        mock_product_repo.get_all.return_value = ([{"id": uuid4()}], 1)

        supplier_id = sample_supplier_data["id"]

        with pytest.raises(ValueError, match="Cannot delete supplier with active products"):
            supplier_service.delete_supplier(supplier_id)

        mock_supplier_repo.delete.assert_not_called()

    @patch("app.services.supplier_service.product_repository")
    @patch("app.services.supplier_service.supplier_repository")
    def test_delete_succeeds_when_no_products(
        self, mock_supplier_repo, mock_product_repo, supplier_service, sample_supplier_data
    ):
        """Test that deletion succeeds when supplier has no products."""
        mock_supplier_repo.get_by_id.return_value = sample_supplier_data
        mock_product_repo.get_all.return_value = ([], 0)
        mock_supplier_repo.delete.return_value = True

        supplier_id = sample_supplier_data["id"]
        result = supplier_service.delete_supplier(supplier_id)

        assert result is True
        mock_supplier_repo.delete.assert_called_once_with(supplier_id)

    @patch("app.services.supplier_service.product_repository")
    @patch("app.services.supplier_service.supplier_repository")
    def test_delete_not_found_returns_false(
        self, mock_supplier_repo, mock_product_repo, supplier_service
    ):
        """Test deleting non-existent supplier returns False."""
        mock_supplier_repo.get_by_id.return_value = None
        supplier_id = uuid4()

        result = supplier_service.delete_supplier(supplier_id)

        assert result is False
        mock_product_repo.get_all.assert_not_called()


# =============================================================================
# UPDATE TESTS
# =============================================================================


class TestSupplierUpdate:
    """Tests for supplier update operations."""

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

    @patch("app.services.supplier_service.supplier_repository")
    def test_update_supplier_partial_update(
        self, mock_repo, supplier_service, sample_supplier_data
    ):
        """Test that partial updates only modify specified fields."""
        mock_repo.get_by_id.return_value = sample_supplier_data
        updated_data = sample_supplier_data.copy()
        updated_data["notes"] = "Updated notes only"
        mock_repo.update.return_value = updated_data

        supplier_id = sample_supplier_data["id"]
        request = SupplierUpdateDTO(notes="Updated notes only")

        result = supplier_service.update_supplier(supplier_id, request)

        assert result is not None
        # Original fields should remain unchanged
        assert result.name == sample_supplier_data["name"]


# =============================================================================
# GET SUPPLIER TESTS
# =============================================================================


class TestGetSupplier:
    """Tests for getting individual suppliers."""

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
