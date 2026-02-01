"""Unit tests for QuotationService."""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.models.kompass_dto import (
    Incoterm,
    QuotationCloneDTO,
    QuotationCreateDTO,
    QuotationFilterDTO,
    QuotationItemCreateDTO,
    QuotationSendEmailRequestDTO,
    QuotationStatus,
    QuotationStatusTransitionDTO,
    QuotationUpdateDTO,
)
from app.services.quotation_service import (
    STATUS_TRANSITIONS,
    QuotationService,
)


@pytest.fixture
def quotation_service():
    """Create a fresh QuotationService instance with mocked repository."""
    service = QuotationService()
    service.repository = MagicMock()
    return service


# =============================================================================
# QUOTATION FIXTURES
# =============================================================================


@pytest.fixture
def mock_quotation():
    """Sample quotation data."""
    return {
        "id": uuid4(),
        "quotation_number": "QT-000001",
        "client_id": uuid4(),
        "client_name": "Test Client Inc",
        "status": "draft",
        "incoterm": "FOB",
        "currency": "USD",
        "subtotal": Decimal("1000.00"),
        "freight_cost": Decimal("100.00"),
        "insurance_cost": Decimal("50.00"),
        "other_costs": Decimal("200000.00"),  # National freight in COP
        "total": Decimal("1150.00"),
        "discount_percent": Decimal("0.00"),
        "discount_amount": Decimal("0.00"),
        "grand_total": Decimal("1150.00"),
        "notes": "Test quotation",
        "terms_and_conditions": "Standard terms",
        "valid_from": date.today(),
        "valid_until": date.today(),
        "created_by": uuid4(),
        "items": [],
        "item_count": 0,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


@pytest.fixture
def mock_quotation_with_items(mock_quotation):
    """Sample quotation with items."""
    quotation = mock_quotation.copy()
    quotation["items"] = [
        {
            "id": uuid4(),
            "quotation_id": quotation["id"],
            "product_id": None,
            "sku": "SKU001",
            "product_name": "Widget A",
            "description": "A great widget",
            "quantity": 10,
            "unit_of_measure": "piece",
            "unit_cost": Decimal("50.00"),
            "unit_price": Decimal("100.00"),
            "markup_percent": Decimal("100.00"),
            "tariff_percent": Decimal("10.00"),
            "tariff_amount": Decimal("100.00"),
            "freight_amount": Decimal("0.00"),
            "line_total": Decimal("1100.00"),
            "sort_order": 0,
            "notes": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
    ]
    quotation["item_count"] = 1
    quotation["subtotal"] = Decimal("1100.00")
    return quotation


@pytest.fixture
def mock_item():
    """Sample quotation item data."""
    return {
        "id": uuid4(),
        "quotation_id": uuid4(),
        "product_id": None,
        "sku": "SKU001",
        "product_name": "Widget A",
        "description": "A great widget",
        "quantity": 10,
        "unit_of_measure": "piece",
        "unit_cost": Decimal("50.00"),
        "unit_price": Decimal("100.00"),
        "markup_percent": Decimal("100.00"),
        "tariff_percent": Decimal("10.00"),
        "tariff_amount": Decimal("100.00"),
        "freight_amount": Decimal("0.00"),
        "line_total": Decimal("1100.00"),
        "sort_order": 0,
        "notes": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


# =============================================================================
# CREATE QUOTATION TESTS
# =============================================================================


class TestCreateQuotation:
    """Tests for quotation creation."""

    def test_create_quotation_success(self, quotation_service, mock_quotation):
        """Test creating a quotation successfully."""
        quotation_service.repository.create.return_value = mock_quotation
        quotation_service.repository.get_by_id.return_value = mock_quotation

        request = QuotationCreateDTO(
            client_id=mock_quotation["client_id"],
            status=QuotationStatus.DRAFT,
            incoterm=Incoterm.FOB,
            currency="USD",
        )

        result = quotation_service.create_quotation(
            request=request,
            created_by=mock_quotation["created_by"],
        )

        assert result is not None
        assert result.quotation_number == "QT-000001"
        assert result.status == QuotationStatus.DRAFT
        quotation_service.repository.create.assert_called_once()

    def test_create_quotation_with_items(self, quotation_service, mock_quotation_with_items):
        """Test creating a quotation with initial items."""
        quotation_service.repository.create.return_value = mock_quotation_with_items
        quotation_service.repository.get_by_id.return_value = mock_quotation_with_items
        quotation_service.repository.add_item.return_value = mock_quotation_with_items["items"][0]

        request = QuotationCreateDTO(
            client_id=mock_quotation_with_items["client_id"],
            items=[
                QuotationItemCreateDTO(
                    product_name="Widget A",
                    quantity=10,
                    unit_price=Decimal("100.00"),
                )
            ],
        )

        result = quotation_service.create_quotation(
            request=request,
            created_by=mock_quotation_with_items["created_by"],
        )

        assert result is not None
        assert result.item_count == 1

    def test_create_quotation_failure(self, quotation_service):
        """Test quotation creation failure."""
        quotation_service.repository.create.return_value = None

        request = QuotationCreateDTO(client_id=uuid4())

        result = quotation_service.create_quotation(
            request=request,
            created_by=uuid4(),
        )

        assert result is None


# =============================================================================
# GET QUOTATION TESTS
# =============================================================================


class TestGetQuotation:
    """Tests for getting a quotation."""

    def test_get_quotation_found(self, quotation_service, mock_quotation):
        """Test getting a quotation by ID."""
        quotation_service.repository.get_by_id.return_value = mock_quotation

        result = quotation_service.get_quotation(mock_quotation["id"])

        assert result is not None
        assert result.id == mock_quotation["id"]

    def test_get_quotation_not_found(self, quotation_service):
        """Test getting a non-existent quotation."""
        quotation_service.repository.get_by_id.return_value = None

        result = quotation_service.get_quotation(uuid4())

        assert result is None


# =============================================================================
# LIST QUOTATIONS TESTS
# =============================================================================


class TestListQuotations:
    """Tests for listing quotations."""

    def test_list_quotations_with_filters(self, quotation_service, mock_quotation):
        """Test listing quotations with filters."""
        quotation_service.repository.get_all.return_value = ([mock_quotation], 1)

        filters = QuotationFilterDTO(
            client_id=mock_quotation["client_id"],
            status=QuotationStatus.DRAFT,
        )

        result = quotation_service.list_quotations(filters=filters, page=1, limit=20)

        assert len(result.items) == 1
        assert result.pagination.total == 1
        quotation_service.repository.get_all.assert_called_once()

    def test_list_quotations_empty(self, quotation_service):
        """Test listing quotations when none exist."""
        quotation_service.repository.get_all.return_value = ([], 0)

        result = quotation_service.list_quotations()

        assert result.items == []
        assert result.pagination.total == 0


# =============================================================================
# UPDATE QUOTATION TESTS
# =============================================================================


class TestUpdateQuotation:
    """Tests for updating quotations."""

    @patch("app.config.database.get_database_connection")
    @patch("app.config.database.close_database_connection")
    def test_update_quotation_success(
        self, mock_close, mock_get_conn, quotation_service, mock_quotation
    ):
        """Test updating a quotation."""
        # Setup mock connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = (mock_quotation["id"],)
        mock_get_conn.return_value = mock_conn

        quotation_service.repository.get_by_id.return_value = mock_quotation
        updated_quotation = mock_quotation.copy()
        updated_quotation["notes"] = "Updated notes"
        quotation_service.repository.recalculate_totals.return_value = updated_quotation

        request = QuotationUpdateDTO(notes="Updated notes")

        result = quotation_service.update_quotation(mock_quotation["id"], request)

        assert result is not None

    def test_update_quotation_not_found(self, quotation_service):
        """Test updating a non-existent quotation."""
        quotation_service.repository.get_by_id.return_value = None

        request = QuotationUpdateDTO(notes="Updated notes")

        result = quotation_service.update_quotation(uuid4(), request)

        assert result is None


# =============================================================================
# DELETE QUOTATION TESTS
# =============================================================================


class TestDeleteQuotation:
    """Tests for deleting quotations."""

    @patch("app.config.database.get_database_connection")
    @patch("app.config.database.close_database_connection")
    def test_delete_quotation_success(
        self, mock_close, mock_get_conn, quotation_service, mock_quotation
    ):
        """Test deleting a quotation."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = (mock_quotation["id"],)
        mock_get_conn.return_value = mock_conn

        quotation_service.repository.get_by_id.return_value = mock_quotation

        result = quotation_service.delete_quotation(mock_quotation["id"])

        assert result is True

    def test_delete_quotation_not_found(self, quotation_service):
        """Test deleting a non-existent quotation."""
        quotation_service.repository.get_by_id.return_value = None

        result = quotation_service.delete_quotation(uuid4())

        assert result is False


# =============================================================================
# CLONE QUOTATION TESTS
# =============================================================================


class TestCloneQuotation:
    """Tests for cloning quotations."""

    def test_clone_quotation_success(self, quotation_service, mock_quotation_with_items):
        """Test cloning a quotation."""
        cloned = mock_quotation_with_items.copy()
        cloned["id"] = uuid4()
        cloned["quotation_number"] = "QT-000002"
        cloned["status"] = "draft"

        quotation_service.repository.get_by_id.side_effect = [
            mock_quotation_with_items,  # First call for source
            cloned,  # Second call for result
        ]
        quotation_service.repository.create.return_value = cloned
        quotation_service.repository.add_item.return_value = cloned["items"][0]

        result = quotation_service.clone_quotation(
            quotation_id=mock_quotation_with_items["id"],
            created_by=uuid4(),
        )

        assert result is not None
        assert result.quotation_number == "QT-000002"
        assert result.status == QuotationStatus.DRAFT

    def test_clone_quotation_with_notes(self, quotation_service, mock_quotation):
        """Test cloning a quotation with custom notes."""
        cloned = mock_quotation.copy()
        cloned["id"] = uuid4()
        cloned["quotation_number"] = "QT-000002"

        quotation_service.repository.get_by_id.side_effect = [mock_quotation, cloned]
        quotation_service.repository.create.return_value = cloned

        clone_request = QuotationCloneDTO(notes="Special clone notes")

        result = quotation_service.clone_quotation(
            quotation_id=mock_quotation["id"],
            created_by=uuid4(),
            clone_request=clone_request,
        )

        assert result is not None

    def test_clone_quotation_not_found(self, quotation_service):
        """Test cloning a non-existent quotation."""
        quotation_service.repository.get_by_id.return_value = None

        result = quotation_service.clone_quotation(
            quotation_id=uuid4(),
            created_by=uuid4(),
        )

        assert result is None


# =============================================================================
# PRICING ENGINE TESTS
# =============================================================================


class TestCalculatePricing:
    """Tests for pricing calculations."""

    @patch("app.services.quotation_service.pricing_service")
    def test_calculate_pricing_formula(
        self, mock_pricing_service, quotation_service, mock_quotation_with_items
    ):
        """Test pricing calculation with the correct formula."""
        quotation_service.repository.get_by_id.return_value = mock_quotation_with_items

        # Mock pricing settings
        mock_pricing_service.get_all_settings.return_value = {
            "exchange_rate_usd_cop": Decimal("4200.0"),
            "default_margin_percentage": Decimal("20.0"),
            "insurance_percentage": Decimal("1.5"),
            "inspection_cost_usd": Decimal("150.0"),
            "nationalization_cost_cop": Decimal("200000.0"),
        }

        result = quotation_service.calculate_pricing(mock_quotation_with_items["id"])

        assert result is not None
        assert result.subtotal_fob_usd == Decimal("1000.00")  # 10 * 100
        assert result.exchange_rate == Decimal("4200.0")
        assert result.margin_percentage == Decimal("20.0")
        # Verify total_cop is calculated
        assert result.total_cop > 0

    @patch("app.services.quotation_service.pricing_service")
    def test_calculate_pricing_empty_quotation(
        self, mock_pricing_service, quotation_service, mock_quotation
    ):
        """Test pricing calculation for quotation with no items."""
        quotation_service.repository.get_by_id.return_value = mock_quotation

        mock_pricing_service.get_all_settings.return_value = {
            "exchange_rate_usd_cop": Decimal("4200.0"),
            "default_margin_percentage": Decimal("20.0"),
            "insurance_percentage": Decimal("1.5"),
            "inspection_cost_usd": Decimal("150.0"),
            "nationalization_cost_cop": Decimal("200000.0"),
        }

        result = quotation_service.calculate_pricing(mock_quotation["id"])

        assert result is not None
        assert result.subtotal_fob_usd == Decimal("0.00")

    def test_calculate_pricing_quotation_not_found(self, quotation_service):
        """Test pricing calculation for non-existent quotation."""
        quotation_service.repository.get_by_id.return_value = None

        result = quotation_service.calculate_pricing(uuid4())

        assert result is None


# =============================================================================
# LINE ITEM MANAGEMENT TESTS
# =============================================================================


class TestAddItem:
    """Tests for adding line items."""

    def test_add_item_triggers_recalculation(self, quotation_service, mock_quotation, mock_item):
        """Test that adding item triggers recalculation."""
        quotation_service.repository.get_by_id.return_value = mock_quotation
        quotation_service.repository.add_item.return_value = mock_item

        item_request = QuotationItemCreateDTO(
            product_name="Widget A",
            quantity=10,
            unit_price=Decimal("100.00"),
        )

        result = quotation_service.add_item(mock_quotation["id"], item_request)

        assert result is not None
        quotation_service.repository.add_item.assert_called_once()

    def test_add_item_quotation_not_found(self, quotation_service):
        """Test adding item to non-existent quotation."""
        quotation_service.repository.get_by_id.return_value = None

        item_request = QuotationItemCreateDTO(
            product_name="Widget A",
            quantity=10,
            unit_price=Decimal("100.00"),
        )

        result = quotation_service.add_item(uuid4(), item_request)

        assert result is None


class TestRemoveItem:
    """Tests for removing line items."""

    def test_remove_item_triggers_recalculation(self, quotation_service, mock_item):
        """Test that removing item triggers recalculation."""
        quotation_service.repository.remove_item.return_value = True

        result = quotation_service.remove_item(mock_item["id"])

        assert result is True
        quotation_service.repository.remove_item.assert_called_once_with(mock_item["id"])

    def test_remove_item_not_found(self, quotation_service):
        """Test removing non-existent item."""
        quotation_service.repository.remove_item.return_value = False

        result = quotation_service.remove_item(uuid4())

        assert result is False


# =============================================================================
# STATUS WORKFLOW TESTS
# =============================================================================


class TestValidStatusTransition:
    """Tests for valid status transitions."""

    def test_draft_to_sent_valid(self, quotation_service):
        """Test valid transition from draft to sent."""
        result = quotation_service.validate_status_transition("draft", "sent")
        assert result is True

    def test_sent_to_viewed_valid(self, quotation_service):
        """Test valid transition from sent to viewed."""
        result = quotation_service.validate_status_transition("sent", "viewed")
        assert result is True

    def test_viewed_to_negotiating_valid(self, quotation_service):
        """Test valid transition from viewed to negotiating."""
        result = quotation_service.validate_status_transition("viewed", "negotiating")
        assert result is True

    def test_negotiating_to_accepted_valid(self, quotation_service):
        """Test valid transition from negotiating to accepted."""
        result = quotation_service.validate_status_transition("negotiating", "accepted")
        assert result is True

    def test_negotiating_to_rejected_valid(self, quotation_service):
        """Test valid transition from negotiating to rejected."""
        result = quotation_service.validate_status_transition("negotiating", "rejected")
        assert result is True

    def test_any_to_expired_valid(self, quotation_service):
        """Test valid transition to expired from various states."""
        for status in ["sent", "viewed", "negotiating"]:
            result = quotation_service.validate_status_transition(status, "expired")
            assert result is True, f"Expected {status} -> expired to be valid"


class TestInvalidStatusTransition:
    """Tests for invalid status transitions."""

    def test_draft_to_accepted_invalid(self, quotation_service):
        """Test invalid transition from draft to accepted."""
        result = quotation_service.validate_status_transition("draft", "accepted")
        assert result is False

    def test_accepted_to_draft_invalid(self, quotation_service):
        """Test invalid transition from accepted to draft."""
        result = quotation_service.validate_status_transition("accepted", "draft")
        assert result is False

    def test_rejected_to_sent_invalid(self, quotation_service):
        """Test invalid transition from rejected to sent."""
        result = quotation_service.validate_status_transition("rejected", "sent")
        assert result is False


class TestUpdateStatus:
    """Tests for status update operations."""

    def test_update_status_success(self, quotation_service, mock_quotation):
        """Test successful status update."""
        quotation_service.repository.get_by_id.return_value = mock_quotation
        updated = mock_quotation.copy()
        updated["status"] = "sent"
        quotation_service.repository.update_status.return_value = updated

        transition = QuotationStatusTransitionDTO(new_status=QuotationStatus.SENT)

        result = quotation_service.update_status(mock_quotation["id"], transition)

        assert result is not None
        assert result.status == QuotationStatus.SENT

    def test_update_status_invalid_transition(self, quotation_service, mock_quotation):
        """Test status update with invalid transition."""
        quotation_service.repository.get_by_id.return_value = mock_quotation

        transition = QuotationStatusTransitionDTO(new_status=QuotationStatus.ACCEPTED)

        with pytest.raises(ValueError) as exc_info:
            quotation_service.update_status(mock_quotation["id"], transition)

        assert "Invalid status transition" in str(exc_info.value)

    def test_update_status_quotation_not_found(self, quotation_service):
        """Test status update for non-existent quotation."""
        quotation_service.repository.get_by_id.return_value = None

        transition = QuotationStatusTransitionDTO(new_status=QuotationStatus.SENT)

        result = quotation_service.update_status(uuid4(), transition)

        assert result is None


# =============================================================================
# STATUS TRANSITIONS CONSTANT TESTS
# =============================================================================


class TestStatusTransitionsConstant:
    """Tests for the STATUS_TRANSITIONS constant."""

    def test_all_statuses_defined(self):
        """Test that all quotation statuses are defined in transitions."""
        expected_statuses = ["draft", "sent", "viewed", "negotiating", "accepted", "rejected", "expired"]
        for status in expected_statuses:
            assert status in STATUS_TRANSITIONS, f"Status {status} not in STATUS_TRANSITIONS"

    def test_draft_transitions(self):
        """Test draft status transitions."""
        assert STATUS_TRANSITIONS["draft"] == ["sent"]

    def test_sent_transitions(self):
        """Test sent status transitions."""
        expected = ["viewed", "accepted", "rejected", "expired"]
        assert set(STATUS_TRANSITIONS["sent"]) == set(expected)

    def test_viewed_transitions(self):
        """Test viewed status transitions."""
        expected = ["negotiating", "accepted", "rejected", "expired"]
        assert set(STATUS_TRANSITIONS["viewed"]) == set(expected)

    def test_negotiating_transitions(self):
        """Test negotiating status transitions."""
        expected = ["accepted", "rejected", "expired"]
        assert set(STATUS_TRANSITIONS["negotiating"]) == set(expected)

    def test_terminal_states_transitions(self):
        """Test that terminal states have limited transitions."""
        assert STATUS_TRANSITIONS["expired"] == []


# =============================================================================
# RECALCULATE AND PERSIST TESTS
# =============================================================================


class TestRecalculateAndPersist:
    """Tests for recalculate_and_persist method."""

    @patch("app.services.quotation_service.pricing_service")
    def test_recalculate_and_persist_success(
        self, mock_pricing_service, quotation_service, mock_quotation_with_items
    ):
        """Test recalculate_and_persist successfully calculates and persists."""
        quotation_service.repository.get_by_id.return_value = mock_quotation_with_items
        quotation_service.repository.recalculate_totals.return_value = mock_quotation_with_items

        mock_pricing_service.get_all_settings.return_value = {
            "exchange_rate_usd_cop": Decimal("4200.0"),
            "default_margin_percentage": Decimal("20.0"),
            "insurance_percentage": Decimal("1.5"),
            "inspection_cost_usd": Decimal("150.0"),
            "nationalization_cost_cop": Decimal("200000.0"),
        }

        result = quotation_service.recalculate_and_persist(mock_quotation_with_items["id"])

        assert result is not None
        assert result.total_cop > 0
        quotation_service.repository.recalculate_totals.assert_called_once()

    def test_recalculate_and_persist_not_found(self, quotation_service):
        """Test recalculate_and_persist for non-existent quotation."""
        quotation_service.repository.get_by_id.return_value = None

        result = quotation_service.recalculate_and_persist(uuid4())

        assert result is None


# =============================================================================
# PDF GENERATION TESTS
# =============================================================================


class TestGeneratePDF:
    """Tests for PDF generation."""

    def test_generate_pdf_success(self, quotation_service, mock_quotation_with_items):
        """Test generating PDF successfully."""
        quotation_service.repository.get_by_id.return_value = mock_quotation_with_items

        result = quotation_service.generate_pdf(mock_quotation_with_items["id"])

        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 0
        # PDF should start with PDF header
        assert result[:4] == b"%PDF"

    def test_generate_pdf_empty_quotation(self, quotation_service, mock_quotation):
        """Test generating PDF for quotation with no items."""
        quotation_service.repository.get_by_id.return_value = mock_quotation

        result = quotation_service.generate_pdf(mock_quotation["id"])

        assert result is not None
        assert isinstance(result, bytes)
        assert result[:4] == b"%PDF"

    def test_generate_pdf_not_found(self, quotation_service):
        """Test generating PDF for non-existent quotation."""
        quotation_service.repository.get_by_id.return_value = None

        result = quotation_service.generate_pdf(uuid4())

        assert result is None


# =============================================================================
# SHARE TOKEN TESTS
# =============================================================================


class TestShareToken:
    """Tests for share token functionality."""

    @patch("app.services.quotation_service.get_settings")
    def test_get_share_token_success(self, mock_settings, mock_quotation):
        """Test generating share token successfully."""
        mock_settings.return_value = MagicMock(
            JWT_SECRET_KEY="test-secret-key-with-at-least-32-chars",
            JWT_ALGORITHM="HS256",
        )
        service = QuotationService()
        service.repository = MagicMock()
        service.repository.get_by_id.return_value = mock_quotation

        result = service.get_share_token(mock_quotation["id"])

        assert result is not None
        assert result.token is not None
        assert len(result.token) > 0
        assert result.quotation_id == mock_quotation["id"]
        assert result.expires_at is not None

    @patch("app.services.quotation_service.get_settings")
    def test_get_share_token_not_found(self, mock_settings):
        """Test generating share token for non-existent quotation."""
        mock_settings.return_value = MagicMock(
            JWT_SECRET_KEY="test-secret-key-with-at-least-32-chars",
            JWT_ALGORITHM="HS256",
        )
        service = QuotationService()
        service.repository = MagicMock()
        service.repository.get_by_id.return_value = None

        result = service.get_share_token(uuid4())

        assert result is None

    @patch("app.services.quotation_service.get_settings")
    def test_get_by_share_token_success(self, mock_settings, mock_quotation):
        """Test accessing quotation via valid share token."""
        mock_settings.return_value = MagicMock(
            JWT_SECRET_KEY="test-secret-key-with-at-least-32-chars",
            JWT_ALGORITHM="HS256",
        )
        service = QuotationService()
        service.repository = MagicMock()
        service.repository.get_by_id.return_value = mock_quotation

        # Generate a token first
        token_result = service.get_share_token(mock_quotation["id"])
        assert token_result is not None

        # Now access via that token
        result = service.get_by_share_token(token_result.token)

        assert result is not None
        assert result.id == mock_quotation["id"]
        assert result.quotation_number == mock_quotation["quotation_number"]

    @patch("app.services.quotation_service.get_settings")
    def test_get_by_share_token_invalid(self, mock_settings):
        """Test accessing quotation via invalid share token."""
        mock_settings.return_value = MagicMock(
            JWT_SECRET_KEY="test-secret-key-with-at-least-32-chars",
            JWT_ALGORITHM="HS256",
        )
        service = QuotationService()
        service.repository = MagicMock()

        result = service.get_by_share_token("invalid-token")

        assert result is None

    @patch("app.services.quotation_service.get_settings")
    def test_get_by_share_token_quotation_deleted(self, mock_settings, mock_quotation):
        """Test accessing quotation that was deleted after token generation."""
        mock_settings.return_value = MagicMock(
            JWT_SECRET_KEY="test-secret-key-with-at-least-32-chars",
            JWT_ALGORITHM="HS256",
        )
        service = QuotationService()
        service.repository = MagicMock()
        service.repository.get_by_id.side_effect = [mock_quotation, None]

        # Generate token
        token_result = service.get_share_token(mock_quotation["id"])

        # Now quotation is deleted
        result = service.get_by_share_token(token_result.token)

        assert result is None


# =============================================================================
# EMAIL FUNCTIONALITY TESTS
# =============================================================================


class TestSendEmail:
    """Tests for email sending functionality."""

    @patch.dict("os.environ", {"EMAIL_MOCK_MODE": "true"})
    def test_send_email_mock_mode(self, quotation_service, mock_quotation):
        """Test sending email in mock mode."""
        quotation_service.repository.get_by_id.return_value = mock_quotation

        request = QuotationSendEmailRequestDTO(
            recipient_email="test@example.com",
            recipient_name="Test User",
            subject="Test Quotation",
            message="Please review",
            include_pdf=True,
        )

        result = quotation_service.send_email(mock_quotation["id"], request)

        assert result is not None
        assert result.success is True
        assert result.mock_mode is True
        assert result.recipient_email == "test@example.com"

    @patch.dict("os.environ", {"EMAIL_MOCK_MODE": "true"})
    def test_send_email_not_found(self, quotation_service):
        """Test sending email for non-existent quotation."""
        quotation_service.repository.get_by_id.return_value = None

        request = QuotationSendEmailRequestDTO(
            recipient_email="test@example.com",
        )

        result = quotation_service.send_email(uuid4(), request)

        assert result is None

    @patch.dict("os.environ", {"EMAIL_MOCK_MODE": "true"})
    def test_send_email_without_pdf(self, quotation_service, mock_quotation):
        """Test sending email without PDF attachment."""
        quotation_service.repository.get_by_id.return_value = mock_quotation

        request = QuotationSendEmailRequestDTO(
            recipient_email="test@example.com",
            include_pdf=False,
        )

        result = quotation_service.send_email(mock_quotation["id"], request)

        assert result is not None
        assert result.success is True


# =============================================================================
# ITEM VALIDATION TESTS
# =============================================================================


class TestItemValidation:
    """Tests for item validation methods."""

    @patch("app.config.database.get_database_connection")
    @patch("app.config.database.close_database_connection")
    def test_validate_item_belongs_to_quotation_success(
        self, mock_close, mock_get_conn, quotation_service, mock_item
    ):
        """Test validating item belongs to correct quotation."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        # Return a row with matching quotation_id
        quotation_id = uuid4()
        mock_cursor.fetchone.return_value = (
            mock_item["id"],
            quotation_id,  # quotation_id
            None,  # product_id
            "SKU001",
            "Widget A",
            "Description",
            10,
            "piece",
            Decimal("50.00"),
            Decimal("100.00"),
            Decimal("100.00"),
            Decimal("10.00"),
            Decimal("100.00"),
            Decimal("0.00"),
            Decimal("1100.00"),
            0,
            None,
            datetime.now(),
            datetime.now(),
        )
        mock_get_conn.return_value = mock_conn

        result = quotation_service.validate_item_belongs_to_quotation(
            quotation_id, mock_item["id"]
        )

        assert result is True

    @patch("app.config.database.get_database_connection")
    @patch("app.config.database.close_database_connection")
    def test_validate_item_belongs_to_quotation_wrong_quotation(
        self, mock_close, mock_get_conn, quotation_service, mock_item
    ):
        """Test validating item belongs to wrong quotation."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        # Return a row with different quotation_id
        mock_cursor.fetchone.return_value = (
            mock_item["id"],
            uuid4(),  # Different quotation_id
            None,
            "SKU001",
            "Widget A",
            "Description",
            10,
            "piece",
            Decimal("50.00"),
            Decimal("100.00"),
            Decimal("100.00"),
            Decimal("10.00"),
            Decimal("100.00"),
            Decimal("0.00"),
            Decimal("1100.00"),
            0,
            None,
            datetime.now(),
            datetime.now(),
        )
        mock_get_conn.return_value = mock_conn

        result = quotation_service.validate_item_belongs_to_quotation(
            uuid4(), mock_item["id"]
        )

        assert result is False

    @patch("app.config.database.get_database_connection")
    @patch("app.config.database.close_database_connection")
    def test_validate_item_belongs_to_quotation_item_not_found(
        self, mock_close, mock_get_conn, quotation_service
    ):
        """Test validating non-existent item."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = None
        mock_get_conn.return_value = mock_conn

        result = quotation_service.validate_item_belongs_to_quotation(uuid4(), uuid4())

        assert result is False
