"""Unit tests for quotation API routes."""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Sample user data for authentication."""
    return {
        "id": str(uuid4()),
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "role": "user",
        "is_active": True,
    }


@pytest.fixture
def mock_admin_user():
    """Sample admin user data for authorization."""
    return {
        "id": str(uuid4()),
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin",
        "is_active": True,
    }


@pytest.fixture
def mock_manager_user():
    """Sample manager user data for authorization."""
    return {
        "id": str(uuid4()),
        "email": "manager@example.com",
        "first_name": "Manager",
        "last_name": "User",
        "role": "manager",
        "is_active": True,
    }


@pytest.fixture
def mock_quotation_data():
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
        "other_costs": Decimal("0.00"),
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
def mock_quotation_response(mock_quotation_data):
    """Sample quotation response DTO."""
    from app.models.kompass_dto import QuotationResponseDTO

    return QuotationResponseDTO(**mock_quotation_data)


@pytest.fixture
def mock_quotation_list_response(mock_quotation_response):
    """Sample quotation list response DTO."""
    from app.models.kompass_dto import PaginationDTO, QuotationListResponseDTO

    return QuotationListResponseDTO(
        items=[mock_quotation_response],
        pagination=PaginationDTO(page=1, limit=20, total=1, pages=1),
    )


@pytest.fixture
def mock_item_data(mock_quotation_data):
    """Sample quotation item data."""
    return {
        "id": uuid4(),
        "quotation_id": mock_quotation_data["id"],
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


@pytest.fixture
def mock_item_response(mock_item_data):
    """Sample quotation item response DTO."""
    from app.models.kompass_dto import QuotationItemResponseDTO

    return QuotationItemResponseDTO(**mock_item_data)


@pytest.fixture
def mock_pricing_response(mock_quotation_data):
    """Sample pricing calculation response."""
    from app.models.kompass_dto import QuotationPricingDTO

    return QuotationPricingDTO(
        quotation_id=mock_quotation_data["id"],
        subtotal_fob_usd=Decimal("1000.00"),
        tariff_total_usd=Decimal("100.00"),
        freight_intl_usd=Decimal("100.00"),
        freight_national_cop=Decimal("200000.00"),
        inspection_usd=Decimal("150.00"),
        insurance_usd=Decimal("18.00"),
        nationalization_cop=Decimal("200000.00"),
        subtotal_before_margin_cop=Decimal("6145600.00"),
        margin_percentage=Decimal("20.00"),
        margin_cop=Decimal("1229120.00"),
        total_cop=Decimal("7374720.00"),
        exchange_rate=Decimal("4200.00"),
    )


@pytest.fixture
def mock_share_token_response(mock_quotation_data):
    """Sample share token response."""
    from app.models.kompass_dto import QuotationShareTokenResponseDTO

    return QuotationShareTokenResponseDTO(
        token="test-jwt-token",
        quotation_id=mock_quotation_data["id"],
        expires_at=datetime.now(),
    )


@pytest.fixture
def mock_public_quotation_response(mock_quotation_data):
    """Sample public quotation response."""
    from app.models.kompass_dto import QuotationPublicResponseDTO

    return QuotationPublicResponseDTO(
        id=mock_quotation_data["id"],
        quotation_number=mock_quotation_data["quotation_number"],
        client_name=mock_quotation_data["client_name"],
        status=mock_quotation_data["status"],
        incoterm=mock_quotation_data["incoterm"],
        currency=mock_quotation_data["currency"],
        subtotal=mock_quotation_data["subtotal"],
        freight_cost=mock_quotation_data["freight_cost"],
        insurance_cost=mock_quotation_data["insurance_cost"],
        other_costs=mock_quotation_data["other_costs"],
        total=mock_quotation_data["total"],
        discount_percent=mock_quotation_data["discount_percent"],
        grand_total=mock_quotation_data["grand_total"],
        notes=mock_quotation_data["notes"],
        terms_and_conditions=mock_quotation_data["terms_and_conditions"],
        valid_from=mock_quotation_data["valid_from"],
        valid_until=mock_quotation_data["valid_until"],
        items=[],
        item_count=0,
        created_at=mock_quotation_data["created_at"],
    )


@pytest.fixture
def mock_send_email_response():
    """Sample email send response."""
    from app.models.kompass_dto import QuotationSendEmailResponseDTO

    return QuotationSendEmailResponseDTO(
        success=True,
        message="Email sent successfully (mock mode)",
        sent_at=datetime.now(),
        recipient_email="test@example.com",
        mock_mode=True,
    )


# =============================================================================
# LIST QUOTATIONS TESTS
# =============================================================================


class TestListQuotations:
    """Tests for GET /api/quotations."""

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_list_quotations_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
        mock_quotation_list_response,
    ):
        """Test listing quotations returns paginated list."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.list_quotations.return_value = mock_quotation_list_response

        response = client.get(
            "/api/quotations",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert data["pagination"]["total"] == 1

    def test_list_quotations_requires_auth(self, client):
        """Test listing quotations requires authentication."""
        response = client.get("/api/quotations")

        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_list_quotations_with_status_filter(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
        mock_quotation_list_response,
    ):
        """Test listing quotations with status filter."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.list_quotations.return_value = mock_quotation_list_response

        response = client.get(
            "/api/quotations?status=draft",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_list_quotations_invalid_status_returns_400(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
    ):
        """Test listing quotations with invalid status returns 400."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user

        response = client.get(
            "/api/quotations?status=invalid_status",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# =============================================================================
# CREATE QUOTATION TESTS
# =============================================================================


class TestCreateQuotation:
    """Tests for POST /api/quotations."""

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_create_quotation_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
        mock_quotation_response,
    ):
        """Test creating a quotation successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.create_quotation.return_value = mock_quotation_response

        response = client.post(
            "/api/quotations",
            json={"client_id": str(mock_quotation_response.client_id)},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["quotation_number"] == "QT-000001"

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_create_quotation_failure_returns_400(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
    ):
        """Test quotation creation failure returns 400."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.create_quotation.return_value = None

        response = client.post(
            "/api/quotations",
            json={"client_id": str(uuid4())},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


# =============================================================================
# GET QUOTATION TESTS
# =============================================================================


class TestGetQuotation:
    """Tests for GET /api/quotations/{quotation_id}."""

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_quotation_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
        mock_quotation_response,
    ):
        """Test getting a quotation by ID."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.get_quotation.return_value = mock_quotation_response

        response = client.get(
            f"/api/quotations/{mock_quotation_response.id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["quotation_number"] == "QT-000001"

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_quotation_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
    ):
        """Test getting non-existent quotation returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.get_quotation.return_value = None

        response = client.get(
            f"/api/quotations/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# UPDATE QUOTATION TESTS
# =============================================================================


class TestUpdateQuotation:
    """Tests for PUT /api/quotations/{quotation_id}."""

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_quotation_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
        mock_quotation_response,
    ):
        """Test updating a quotation successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.update_quotation.return_value = mock_quotation_response

        response = client.put(
            f"/api/quotations/{mock_quotation_response.id}",
            json={"notes": "Updated notes"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_quotation_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
    ):
        """Test updating non-existent quotation returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.update_quotation.return_value = None

        response = client.put(
            f"/api/quotations/{uuid4()}",
            json={"notes": "Updated notes"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# DELETE QUOTATION TESTS
# =============================================================================


class TestDeleteQuotation:
    """Tests for DELETE /api/quotations/{quotation_id}."""

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_quotation_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_admin_user,
        mock_quotation_response,
    ):
        """Test deleting a quotation successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_quotation_service.delete_quotation.return_value = True

        response = client.delete(
            f"/api/quotations/{mock_quotation_response.id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Quotation deleted successfully"

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_quotation_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_admin_user,
    ):
        """Test deleting non-existent quotation returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_quotation_service.delete_quotation.return_value = False

        response = client.delete(
            f"/api/quotations/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_quotation_requires_admin_or_manager(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
    ):
        """Test delete requires admin or manager role."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user

        response = client.delete(
            f"/api/quotations/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


# =============================================================================
# CLONE QUOTATION TESTS
# =============================================================================


class TestCloneQuotation:
    """Tests for POST /api/quotations/{quotation_id}/clone."""

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_clone_quotation_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
        mock_quotation_response,
    ):
        """Test cloning a quotation successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        cloned = mock_quotation_response.model_copy()
        cloned.quotation_number = "QT-000002"
        mock_quotation_service.clone_quotation.return_value = cloned

        response = client.post(
            f"/api/quotations/{mock_quotation_response.id}/clone",
            json={},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_201_CREATED

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_clone_quotation_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
    ):
        """Test cloning non-existent quotation returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.clone_quotation.return_value = None

        response = client.post(
            f"/api/quotations/{uuid4()}/clone",
            json={},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# PRICING CALCULATION TESTS
# =============================================================================


class TestCalculatePricing:
    """Tests for GET /api/quotations/{quotation_id}/pricing."""

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_calculate_pricing_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
        mock_pricing_response,
    ):
        """Test calculating pricing successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.calculate_pricing.return_value = mock_pricing_response

        response = client.get(
            f"/api/quotations/{mock_pricing_response.quotation_id}/pricing",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "subtotal_fob_usd" in data
        assert "total_cop" in data

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_calculate_pricing_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
    ):
        """Test calculating pricing for non-existent quotation returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.calculate_pricing.return_value = None

        response = client.get(
            f"/api/quotations/{uuid4()}/pricing",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# STATUS UPDATE TESTS
# =============================================================================


class TestUpdateStatus:
    """Tests for PUT /api/quotations/{quotation_id}/status."""

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_status_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
        mock_quotation_response,
    ):
        """Test updating quotation status successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        updated = mock_quotation_response.model_copy()
        updated.status = "sent"
        mock_quotation_service.update_status.return_value = updated

        response = client.put(
            f"/api/quotations/{mock_quotation_response.id}/status",
            json={"new_status": "sent"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_status_invalid_transition_returns_400(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
        mock_quotation_response,
    ):
        """Test invalid status transition returns 400."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.update_status.side_effect = ValueError(
            "Invalid status transition"
        )

        response = client.put(
            f"/api/quotations/{mock_quotation_response.id}/status",
            json={"new_status": "accepted"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_status_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
    ):
        """Test updating status for non-existent quotation returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.update_status.return_value = None

        response = client.put(
            f"/api/quotations/{uuid4()}/status",
            json={"new_status": "sent"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# LINE ITEM TESTS
# =============================================================================


class TestAddItem:
    """Tests for POST /api/quotations/{quotation_id}/items."""

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_add_item_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
        mock_quotation_response,
        mock_item_response,
    ):
        """Test adding an item to quotation successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.add_item.return_value = mock_item_response

        response = client.post(
            f"/api/quotations/{mock_quotation_response.id}/items",
            json={
                "product_name": "Widget A",
                "quantity": 10,
                "unit_price": "100.00",
            },
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["product_name"] == "Widget A"

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_add_item_quotation_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
    ):
        """Test adding item to non-existent quotation returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.add_item.return_value = None

        response = client.post(
            f"/api/quotations/{uuid4()}/items",
            json={
                "product_name": "Widget A",
                "quantity": 10,
                "unit_price": "100.00",
            },
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateItem:
    """Tests for PUT /api/quotations/{quotation_id}/items/{item_id}."""

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_item_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
        mock_item_response,
    ):
        """Test updating an item successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.validate_item_belongs_to_quotation.return_value = True
        mock_quotation_service.update_item.return_value = mock_item_response

        response = client.put(
            f"/api/quotations/{mock_item_response.quotation_id}/items/{mock_item_response.id}",
            json={"quantity": 20},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_item_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
    ):
        """Test updating non-existent item returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.validate_item_belongs_to_quotation.return_value = True
        mock_quotation_service.update_item.return_value = None

        response = client.put(
            f"/api/quotations/{uuid4()}/items/{uuid4()}",
            json={"quantity": 20},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestRemoveItem:
    """Tests for DELETE /api/quotations/{quotation_id}/items/{item_id}."""

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_remove_item_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
        mock_item_response,
    ):
        """Test removing an item successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.validate_item_belongs_to_quotation.return_value = True
        mock_quotation_service.remove_item.return_value = True

        response = client.delete(
            f"/api/quotations/{mock_item_response.quotation_id}/items/{mock_item_response.id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Item removed successfully"

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_remove_item_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
    ):
        """Test removing non-existent item returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.validate_item_belongs_to_quotation.return_value = True
        mock_quotation_service.remove_item.return_value = False

        response = client.delete(
            f"/api/quotations/{uuid4()}/items/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# RECALCULATE AND PERSIST TESTS
# =============================================================================


class TestRecalculateAndPersist:
    """Tests for POST /api/quotations/{quotation_id}/calculate."""

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_recalculate_and_persist_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
        mock_pricing_response,
    ):
        """Test recalculating pricing successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.recalculate_and_persist.return_value = mock_pricing_response

        response = client.post(
            f"/api/quotations/{mock_pricing_response.quotation_id}/calculate",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "subtotal_fob_usd" in data
        assert "total_cop" in data

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_recalculate_and_persist_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
    ):
        """Test recalculating pricing for non-existent quotation returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.recalculate_and_persist.return_value = None

        response = client.post(
            f"/api/quotations/{uuid4()}/calculate",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# PDF EXPORT TESTS
# =============================================================================


class TestExportPDF:
    """Tests for GET /api/quotations/{quotation_id}/export/pdf."""

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_export_pdf_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
        mock_quotation_response,
    ):
        """Test exporting PDF successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.generate_pdf.return_value = b"%PDF-1.4 test content"
        mock_quotation_service.get_quotation.return_value = mock_quotation_response

        response = client.get(
            f"/api/quotations/{mock_quotation_response.id}/export/pdf",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/pdf"
        assert "Content-Disposition" in response.headers

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_export_pdf_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
    ):
        """Test exporting PDF for non-existent quotation returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.generate_pdf.return_value = None

        response = client.get(
            f"/api/quotations/{uuid4()}/export/pdf",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# SEND EMAIL TESTS
# =============================================================================


class TestSendEmail:
    """Tests for POST /api/quotations/{quotation_id}/send."""

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_send_email_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
        mock_quotation_response,
        mock_send_email_response,
    ):
        """Test sending email successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.send_email.return_value = mock_send_email_response

        response = client.post(
            f"/api/quotations/{mock_quotation_response.id}/send",
            json={
                "recipient_email": "test@example.com",
                "subject": "Test Quotation",
                "message": "Please review",
            },
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["recipient_email"] == "test@example.com"

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_send_email_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
    ):
        """Test sending email for non-existent quotation returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.send_email.return_value = None

        response = client.post(
            f"/api/quotations/{uuid4()}/send",
            json={"recipient_email": "test@example.com"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# SHARE TOKEN TESTS
# =============================================================================


class TestShareToken:
    """Tests for share token endpoints."""

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_generate_share_token_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
        mock_share_token_response,
    ):
        """Test generating share token successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.get_share_token.return_value = mock_share_token_response

        response = client.post(
            f"/api/quotations/{mock_share_token_response.quotation_id}/share",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "token" in data
        assert "expires_at" in data

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_generate_share_token_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
    ):
        """Test generating share token for non-existent quotation returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.get_share_token.return_value = None

        response = client.post(
            f"/api/quotations/{uuid4()}/share",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPublicShareEndpoint:
    """Tests for GET /api/quotations/share/{token} (public endpoint)."""

    @patch("app.api.quotation_routes.quotation_service")
    def test_get_by_share_token_success(
        self,
        mock_quotation_service,
        client,
        mock_public_quotation_response,
    ):
        """Test accessing quotation via share token (no auth required)."""
        mock_quotation_service.get_by_share_token.return_value = mock_public_quotation_response

        response = client.get("/api/quotations/share/valid-token")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["quotation_number"] == "QT-000001"

    @patch("app.api.quotation_routes.quotation_service")
    def test_get_by_share_token_invalid_returns_404(
        self,
        mock_quotation_service,
        client,
    ):
        """Test accessing quotation via invalid share token returns 404."""
        mock_quotation_service.get_by_share_token.return_value = None

        response = client.get("/api/quotations/share/invalid-token")

        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# NESTED LINE ITEM ROUTE TESTS
# =============================================================================


class TestNestedLineItemRoutes:
    """Tests for nested line item routes /{quotation_id}/items/{item_id}."""

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_item_nested_route_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
        mock_quotation_response,
        mock_item_response,
    ):
        """Test updating an item via nested route successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.validate_item_belongs_to_quotation.return_value = True
        mock_quotation_service.update_item.return_value = mock_item_response

        response = client.put(
            f"/api/quotations/{mock_quotation_response.id}/items/{mock_item_response.id}",
            json={"quantity": 20},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_item_wrong_quotation_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
    ):
        """Test updating item with wrong quotation ID returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.validate_item_belongs_to_quotation.return_value = False

        response = client.put(
            f"/api/quotations/{uuid4()}/items/{uuid4()}",
            json={"quantity": 20},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_remove_item_nested_route_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
        mock_quotation_response,
        mock_item_response,
    ):
        """Test removing an item via nested route successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.validate_item_belongs_to_quotation.return_value = True
        mock_quotation_service.remove_item.return_value = True

        response = client.delete(
            f"/api/quotations/{mock_quotation_response.id}/items/{mock_item_response.id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Item removed successfully"

    @patch("app.api.quotation_routes.quotation_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_remove_item_wrong_quotation_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_quotation_service,
        client,
        mock_user,
    ):
        """Test removing item with wrong quotation ID returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_quotation_service.validate_item_belongs_to_quotation.return_value = False

        response = client.delete(
            f"/api/quotations/{uuid4()}/items/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
