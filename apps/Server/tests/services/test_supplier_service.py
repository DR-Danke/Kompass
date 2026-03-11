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


class TestCreateSupplierFromCard:
    """Tests for create_supplier_from_card method."""

    @pytest.fixture
    def extracted_capture(self):
        """Sample extracted business card capture."""
        return {
            "id": uuid4(),
            "image_url": "https://example.com/card.jpg",
            "status": "extracted",
            "company_name": "Test Corp",
            "contact_name": "Zhang Wei",
            "contact_email": "zhang@testcorp.cn",
            "contact_phone": "+86-13800138000",
            "contact_wechat": "zhangwei_wechat",
            "website": "https://testcorp.cn",
            "address": "123 Factory Road, Guangzhou",
            "supplier_id": None,
            "fair_name": "Canton Fair 2026",
            "notes": None,
            "captured_by": str(uuid4()),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

    @pytest.fixture
    def created_supplier_data(self):
        """Sample created supplier data returned by repository."""
        return {
            "id": uuid4(),
            "name": "Test Corp",
            "code": None,
            "status": "active",
            "contact_name": "Zhang Wei",
            "contact_email": "zhang@testcorp.cn",
            "contact_phone": "+86-13800138000",
            "address": "123 Factory Road, Guangzhou",
            "city": None,
            "country": "China",
            "website": "https://testcorp.cn",
            "notes": None,
            "certification_status": "uncertified",
            "pipeline_status": "contacted",
            "latest_audit_id": None,
            "certified_at": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

    @patch("app.services.supplier_service.supplier_repository")
    @patch("app.services.supplier_service.business_card_service")
    def test_create_supplier_from_card_success(
        self, mock_bcs, mock_repo, supplier_service, extracted_capture, created_supplier_data
    ):
        """Test successful supplier creation from extracted card."""
        mock_bcs.get_capture.return_value = extracted_capture
        mock_repo.find_duplicate_supplier.return_value = None
        mock_repo.create_with_trade_fair_metadata.return_value = created_supplier_data

        capture_id = extracted_capture["id"]
        result = supplier_service.create_supplier_from_card(capture_id)

        assert result.success is True
        assert result.supplier_id == created_supplier_data["id"]
        assert result.supplier_name == "Test Corp"
        assert result.is_duplicate is False
        mock_repo.create_with_trade_fair_metadata.assert_called_once()
        # Verify capture was linked
        mock_bcs.update_capture.assert_called_once_with(
            capture_id,
            {"supplier_id": str(created_supplier_data["id"]), "status": "confirmed"},
        )

    @patch("app.services.supplier_service.supplier_repository")
    @patch("app.services.supplier_service.business_card_service")
    def test_duplicate_detection_by_email(
        self, mock_bcs, mock_repo, supplier_service, extracted_capture
    ):
        """Test duplicate detection when email matches existing supplier."""
        mock_bcs.get_capture.return_value = extracted_capture
        existing_supplier = {
            "id": uuid4(),
            "name": "Existing Corp",
        }
        mock_repo.find_duplicate_supplier.return_value = existing_supplier

        result = supplier_service.create_supplier_from_card(extracted_capture["id"])

        assert result.success is False
        assert result.is_duplicate is True
        assert result.duplicate_supplier_id == existing_supplier["id"]
        assert result.duplicate_supplier_name == "Existing Corp"
        mock_repo.create_with_trade_fair_metadata.assert_not_called()
        # Capture should be marked as rejected
        mock_bcs.update_capture.assert_called_once_with(
            extracted_capture["id"], {"status": "rejected"}
        )

    @patch("app.services.supplier_service.supplier_repository")
    @patch("app.services.supplier_service.business_card_service")
    def test_reject_non_extracted_status(
        self, mock_bcs, mock_repo, supplier_service, extracted_capture
    ):
        """Test rejection when capture status is not 'extracted'."""
        extracted_capture["status"] = "pending"
        mock_bcs.get_capture.return_value = extracted_capture

        with pytest.raises(ValueError, match="Only 'extracted' captures"):
            supplier_service.create_supplier_from_card(extracted_capture["id"])

    @patch("app.services.supplier_service.supplier_repository")
    @patch("app.services.supplier_service.business_card_service")
    def test_reject_already_linked_capture(
        self, mock_bcs, mock_repo, supplier_service, extracted_capture
    ):
        """Test rejection when capture already has a linked supplier."""
        extracted_capture["supplier_id"] = str(uuid4())
        mock_bcs.get_capture.return_value = extracted_capture

        with pytest.raises(ValueError, match="already linked"):
            supplier_service.create_supplier_from_card(extracted_capture["id"])

    @patch("app.services.supplier_service.supplier_repository")
    @patch("app.services.supplier_service.business_card_service")
    def test_reject_no_name(
        self, mock_bcs, mock_repo, supplier_service, extracted_capture
    ):
        """Test rejection when no company or contact name extracted."""
        extracted_capture["company_name"] = None
        extracted_capture["contact_name"] = None
        mock_bcs.get_capture.return_value = extracted_capture

        with pytest.raises(ValueError, match="No company or contact name"):
            supplier_service.create_supplier_from_card(extracted_capture["id"])

    @patch("app.services.supplier_service.supplier_repository")
    @patch("app.services.supplier_service.business_card_service")
    def test_fallback_to_contact_name(
        self, mock_bcs, mock_repo, supplier_service, extracted_capture, created_supplier_data
    ):
        """Test that contact_name is used when company_name is missing, with fallback note."""
        extracted_capture["company_name"] = None
        created_supplier_data["name"] = "Zhang Wei"
        mock_bcs.get_capture.return_value = extracted_capture
        mock_repo.find_duplicate_supplier.return_value = None
        mock_repo.create_with_trade_fair_metadata.return_value = created_supplier_data

        result = supplier_service.create_supplier_from_card(extracted_capture["id"])

        assert result.success is True
        call_kwargs = mock_repo.create_with_trade_fair_metadata.call_args.kwargs
        assert call_kwargs["name"] == "Zhang Wei"
        assert call_kwargs["notes"] is not None
        assert "Revisión manual requerida" in call_kwargs["notes"]

    @patch("app.services.supplier_service.supplier_repository")
    @patch("app.services.supplier_service.business_card_service")
    def test_whitespace_only_company_name_falls_back_to_contact(
        self, mock_bcs, mock_repo, supplier_service, extracted_capture, created_supplier_data
    ):
        """Test that whitespace-only company_name falls back to contact_name."""
        extracted_capture["company_name"] = "   "
        created_supplier_data["name"] = "Zhang Wei"
        mock_bcs.get_capture.return_value = extracted_capture
        mock_repo.find_duplicate_supplier.return_value = None
        mock_repo.create_with_trade_fair_metadata.return_value = created_supplier_data

        result = supplier_service.create_supplier_from_card(extracted_capture["id"])

        assert result.success is True
        call_kwargs = mock_repo.create_with_trade_fair_metadata.call_args.kwargs
        assert call_kwargs["name"] == "Zhang Wei"
        assert call_kwargs["notes"] is not None
        assert "Revisión manual requerida" in call_kwargs["notes"]

    @patch("app.services.supplier_service.supplier_repository")
    @patch("app.services.supplier_service.business_card_service")
    def test_whitespace_only_both_names_raises_error(
        self, mock_bcs, mock_repo, supplier_service, extracted_capture
    ):
        """Test that whitespace-only company_name and contact_name raises ValueError."""
        extracted_capture["company_name"] = "   "
        extracted_capture["contact_name"] = "  "
        mock_bcs.get_capture.return_value = extracted_capture

        with pytest.raises(ValueError, match="No company or contact name"):
            supplier_service.create_supplier_from_card(extracted_capture["id"])

    @patch("app.services.supplier_service.supplier_repository")
    @patch("app.services.supplier_service.business_card_service")
    def test_fallback_note_added_when_using_contact_name(
        self, mock_bcs, mock_repo, supplier_service, extracted_capture, created_supplier_data
    ):
        """Test that fallback note is added when contact_name is used as supplier name."""
        extracted_capture["company_name"] = ""
        created_supplier_data["name"] = "Zhang Wei"
        mock_bcs.get_capture.return_value = extracted_capture
        mock_repo.find_duplicate_supplier.return_value = None
        mock_repo.create_with_trade_fair_metadata.return_value = created_supplier_data

        supplier_service.create_supplier_from_card(extracted_capture["id"])

        call_kwargs = mock_repo.create_with_trade_fair_metadata.call_args.kwargs
        assert call_kwargs["name"] == "Zhang Wei"
        assert call_kwargs["notes"] == "Nombre de empresa no encontrado — se usó el nombre del contacto. Revisión manual requerida."

    @patch("app.services.supplier_service.supplier_repository")
    @patch("app.services.supplier_service.business_card_service")
    def test_skip_duplicate_check_no_email_no_phone(
        self, mock_bcs, mock_repo, supplier_service, extracted_capture, created_supplier_data
    ):
        """Test that duplicate check is skipped when no email and no phone."""
        extracted_capture["contact_email"] = None
        extracted_capture["contact_phone"] = None
        mock_bcs.get_capture.return_value = extracted_capture
        mock_repo.find_duplicate_supplier.return_value = None
        mock_repo.create_with_trade_fair_metadata.return_value = created_supplier_data

        result = supplier_service.create_supplier_from_card(extracted_capture["id"])

        assert result.success is True
        mock_repo.find_duplicate_supplier.assert_called_once_with(email=None, phone=None)

    @patch("app.services.supplier_service.supplier_repository")
    @patch("app.services.supplier_service.business_card_service")
    def test_trade_fair_metadata_passed(
        self, mock_bcs, mock_repo, supplier_service, extracted_capture, created_supplier_data
    ):
        """Test that trade fair metadata is correctly passed to repository."""
        mock_bcs.get_capture.return_value = extracted_capture
        mock_repo.find_duplicate_supplier.return_value = None
        mock_repo.create_with_trade_fair_metadata.return_value = created_supplier_data

        supplier_service.create_supplier_from_card(extracted_capture["id"])

        call_kwargs = mock_repo.create_with_trade_fair_metadata.call_args.kwargs
        assert call_kwargs["source"] == "trade_fair"
        assert call_kwargs["fair_name"] == "Canton Fair 2026"
        assert call_kwargs["pipeline_status"] == "contacted"
        assert call_kwargs["country"] == "China"
        assert call_kwargs["wechat_id"] == "zhangwei_wechat"
