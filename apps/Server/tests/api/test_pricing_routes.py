"""Unit tests for pricing API routes."""

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
def mock_hs_code():
    """Sample HS code data."""
    return {
        "id": uuid4(),
        "code": "8471.30.00",
        "description": "Portable automatic data processing machines",
        "duty_rate": Decimal("5.00"),
        "notes": "Laptops and notebooks",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


@pytest.fixture
def mock_hs_code_response(mock_hs_code):
    """Sample HS code response DTO."""
    from app.models.kompass_dto import HSCodeResponseDTO

    return HSCodeResponseDTO(**mock_hs_code)


@pytest.fixture
def mock_hs_code_list_response(mock_hs_code_response):
    """Sample HS code list response DTO."""
    from app.models.kompass_dto import HSCodeListResponseDTO, PaginationDTO

    return HSCodeListResponseDTO(
        items=[mock_hs_code_response],
        pagination=PaginationDTO(page=1, limit=20, total=1, pages=1),
    )


@pytest.fixture
def mock_freight_rate():
    """Sample freight rate data."""
    return {
        "id": uuid4(),
        "origin": "Shanghai",
        "destination": "Bogota",
        "incoterm": "FOB",
        "rate_per_kg": Decimal("2.50"),
        "rate_per_cbm": Decimal("150.00"),
        "minimum_charge": Decimal("100.00"),
        "transit_days": 35,
        "is_active": True,
        "valid_from": date.today(),
        "valid_until": None,
        "notes": "Standard sea freight",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


@pytest.fixture
def mock_freight_rate_response(mock_freight_rate):
    """Sample freight rate response DTO."""
    from app.models.kompass_dto import FreightRateResponseDTO

    return FreightRateResponseDTO(**mock_freight_rate)


@pytest.fixture
def mock_freight_rate_list_response(mock_freight_rate_response):
    """Sample freight rate list response DTO."""
    from app.models.kompass_dto import FreightRateListResponseDTO, PaginationDTO

    return FreightRateListResponseDTO(
        items=[mock_freight_rate_response],
        pagination=PaginationDTO(page=1, limit=20, total=1, pages=1),
    )


@pytest.fixture
def mock_pricing_setting():
    """Sample pricing setting data."""
    return {
        "id": uuid4(),
        "setting_key": "default_margin_percentage",
        "setting_value": Decimal("20.0"),
        "description": "Default profit margin percentage",
        "is_percentage": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


@pytest.fixture
def mock_pricing_setting_response(mock_pricing_setting):
    """Sample pricing setting response DTO."""
    from app.models.kompass_dto import PricingSettingResponseDTO

    return PricingSettingResponseDTO(**mock_pricing_setting)


# =============================================================================
# HS CODE TESTS
# =============================================================================


class TestListHSCodes:
    """Tests for GET /api/pricing/hs-codes."""

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_list_hs_codes_returns_paginated_results(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        client,
        mock_user,
        mock_hs_code_list_response,
    ):
        """Test listing HS codes returns paginated results."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_pricing_service.list_hs_codes.return_value = mock_hs_code_list_response

        response = client.get(
            "/api/pricing/hs-codes",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["code"] == "8471.30.00"
        assert data["pagination"]["total"] == 1

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_list_hs_codes_with_search(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        client,
        mock_user,
        mock_hs_code_list_response,
    ):
        """Test listing HS codes with search parameter."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_pricing_service.list_hs_codes.return_value = mock_hs_code_list_response

        response = client.get(
            "/api/pricing/hs-codes?search=laptop",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        mock_pricing_service.list_hs_codes.assert_called_once_with(
            search="laptop", page=1, limit=20
        )

    def test_list_hs_codes_requires_auth(self, client):
        """Test listing HS codes requires authentication."""
        response = client.get("/api/pricing/hs-codes")
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]


class TestCreateHSCode:
    """Tests for POST /api/pricing/hs-codes."""

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_create_hs_code_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        client,
        mock_user,
        mock_hs_code_response,
    ):
        """Test creating an HS code successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_pricing_service.create_hs_code.return_value = mock_hs_code_response

        response = client.post(
            "/api/pricing/hs-codes",
            json={
                "code": "8471.30.00",
                "description": "Portable automatic data processing machines",
                "duty_rate": "5.00",
            },
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["code"] == "8471.30.00"

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_create_hs_code_failure_returns_400(
        self, mock_user_repo, mock_auth_service, mock_pricing_service, client, mock_user
    ):
        """Test HS code creation failure returns 400."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_pricing_service.create_hs_code.return_value = None

        response = client.post(
            "/api/pricing/hs-codes",
            json={"code": "DUPLICATE", "description": "Test"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGetHSCode:
    """Tests for GET /api/pricing/hs-codes/{hs_code_id}."""

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_hs_code_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        client,
        mock_user,
        mock_hs_code_response,
    ):
        """Test getting an HS code by ID."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_pricing_service.get_hs_code.return_value = mock_hs_code_response

        response = client.get(
            f"/api/pricing/hs-codes/{mock_hs_code_response.id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["code"] == "8471.30.00"

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_hs_code_not_found_returns_404(
        self, mock_user_repo, mock_auth_service, mock_pricing_service, client, mock_user
    ):
        """Test getting non-existent HS code returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_pricing_service.get_hs_code.return_value = None

        response = client.get(
            f"/api/pricing/hs-codes/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateHSCode:
    """Tests for PUT /api/pricing/hs-codes/{hs_code_id}."""

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_hs_code_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        client,
        mock_admin_user,
        mock_hs_code_response,
    ):
        """Test updating an HS code successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_pricing_service.get_hs_code.return_value = mock_hs_code_response
        mock_pricing_service.update_hs_code.return_value = mock_hs_code_response

        response = client.put(
            f"/api/pricing/hs-codes/{mock_hs_code_response.id}",
            json={"duty_rate": "7.50"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_hs_code_requires_admin_or_manager(
        self, mock_user_repo, mock_auth_service, mock_pricing_service, client, mock_user
    ):
        """Test update requires admin or manager role."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user

        response = client.put(
            f"/api/pricing/hs-codes/{uuid4()}",
            json={"duty_rate": "7.50"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_hs_code_manager_allowed(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        client,
        mock_manager_user,
        mock_hs_code_response,
    ):
        """Test manager role can update HS codes."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_manager_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_manager_user
        mock_pricing_service.get_hs_code.return_value = mock_hs_code_response
        mock_pricing_service.update_hs_code.return_value = mock_hs_code_response

        response = client.put(
            f"/api/pricing/hs-codes/{mock_hs_code_response.id}",
            json={"duty_rate": "7.50"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_hs_code_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        client,
        mock_admin_user,
    ):
        """Test updating non-existent HS code returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_pricing_service.get_hs_code.return_value = None

        response = client.put(
            f"/api/pricing/hs-codes/{uuid4()}",
            json={"duty_rate": "7.50"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteHSCode:
    """Tests for DELETE /api/pricing/hs-codes/{hs_code_id}."""

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_hs_code_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        client,
        mock_admin_user,
        mock_hs_code_response,
    ):
        """Test deleting an HS code successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_pricing_service.get_hs_code.return_value = mock_hs_code_response

        response = client.delete(
            f"/api/pricing/hs-codes/{mock_hs_code_response.id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_hs_code_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        client,
        mock_admin_user,
    ):
        """Test deleting non-existent HS code returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_pricing_service.get_hs_code.return_value = None

        response = client.delete(
            f"/api/pricing/hs-codes/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_hs_code_requires_admin_or_manager(
        self, mock_user_repo, mock_auth_service, mock_pricing_service, client, mock_user
    ):
        """Test delete requires admin or manager role."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user

        response = client.delete(
            f"/api/pricing/hs-codes/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


# =============================================================================
# FREIGHT RATE TESTS
# =============================================================================


class TestListFreightRates:
    """Tests for GET /api/pricing/freight-rates."""

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_list_freight_rates_returns_paginated_results(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        client,
        mock_user,
        mock_freight_rate_list_response,
    ):
        """Test listing freight rates returns paginated results."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_pricing_service.list_freight_rates.return_value = mock_freight_rate_list_response

        response = client.get(
            "/api/pricing/freight-rates",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["origin"] == "Shanghai"

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_list_freight_rates_with_filters(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        client,
        mock_user,
        mock_freight_rate_list_response,
    ):
        """Test listing freight rates with origin/destination filters."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_pricing_service.list_freight_rates.return_value = mock_freight_rate_list_response

        response = client.get(
            "/api/pricing/freight-rates?origin=Shanghai&destination=Bogota",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        mock_pricing_service.list_freight_rates.assert_called_once_with(
            origin="Shanghai", destination="Bogota", page=1, limit=20
        )


class TestCreateFreightRate:
    """Tests for POST /api/pricing/freight-rates."""

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_create_freight_rate_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        client,
        mock_user,
        mock_freight_rate_response,
    ):
        """Test creating a freight rate successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_pricing_service.create_freight_rate.return_value = mock_freight_rate_response

        response = client.post(
            "/api/pricing/freight-rates",
            json={
                "origin": "Shanghai",
                "destination": "Bogota",
                "incoterm": "FOB",
                "rate_per_kg": "2.50",
                "minimum_charge": "100.00",
            },
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["origin"] == "Shanghai"

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_create_freight_rate_failure_returns_400(
        self, mock_user_repo, mock_auth_service, mock_pricing_service, client, mock_user
    ):
        """Test freight rate creation failure returns 400."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_pricing_service.create_freight_rate.return_value = None

        response = client.post(
            "/api/pricing/freight-rates",
            json={
                "origin": "Test",
                "destination": "Test",
                "incoterm": "FOB",
                "minimum_charge": "0",
            },
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGetActiveFreightRate:
    """Tests for GET /api/pricing/freight-rates/active."""

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_active_rate_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        client,
        mock_user,
        mock_freight_rate_response,
    ):
        """Test getting active freight rate for a route."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_pricing_service.get_active_rate.return_value = mock_freight_rate_response

        response = client.get(
            "/api/pricing/freight-rates/active?origin=Shanghai&destination=Bogota",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["origin"] == "Shanghai"
        assert data["destination"] == "Bogota"

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_active_rate_not_found_returns_404(
        self, mock_user_repo, mock_auth_service, mock_pricing_service, client, mock_user
    ):
        """Test getting active rate returns 404 when no active rate exists."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_pricing_service.get_active_rate.return_value = None

        response = client.get(
            "/api/pricing/freight-rates/active?origin=Unknown&destination=Unknown",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestUpdateFreightRate:
    """Tests for PUT /api/pricing/freight-rates/{rate_id}."""

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_freight_rate_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        client,
        mock_admin_user,
        mock_freight_rate_response,
    ):
        """Test updating a freight rate successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_pricing_service.update_freight_rate.return_value = mock_freight_rate_response

        response = client.put(
            f"/api/pricing/freight-rates/{mock_freight_rate_response.id}",
            json={"rate_per_kg": "3.00"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_freight_rate_requires_admin_or_manager(
        self, mock_user_repo, mock_auth_service, mock_pricing_service, client, mock_user
    ):
        """Test update requires admin or manager role."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user

        response = client.put(
            f"/api/pricing/freight-rates/{uuid4()}",
            json={"rate_per_kg": "3.00"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_freight_rate_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        client,
        mock_admin_user,
    ):
        """Test updating non-existent freight rate returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_pricing_service.update_freight_rate.return_value = None

        response = client.put(
            f"/api/pricing/freight-rates/{uuid4()}",
            json={"rate_per_kg": "3.00"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteFreightRate:
    """Tests for DELETE /api/pricing/freight-rates/{rate_id}."""

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_freight_rate_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        client,
        mock_admin_user,
        mock_freight_rate_response,
    ):
        """Test deleting (soft delete) a freight rate successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_pricing_service.update_freight_rate.return_value = mock_freight_rate_response

        response = client.delete(
            f"/api/pricing/freight-rates/{mock_freight_rate_response.id}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_delete_freight_rate_not_found_returns_404(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        client,
        mock_admin_user,
    ):
        """Test deleting non-existent freight rate returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_pricing_service.update_freight_rate.return_value = None

        response = client.delete(
            f"/api/pricing/freight-rates/{uuid4()}",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


# =============================================================================
# PRICING SETTINGS TESTS
# =============================================================================


class TestGetPricingSettings:
    """Tests for GET /api/pricing/settings."""

    @patch("app.repository.kompass_repository.pricing_settings_repository")
    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_get_settings_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        mock_settings_repo,
        client,
        mock_user,
        mock_pricing_setting,
    ):
        """Test getting all pricing settings."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_user
        mock_pricing_service.initialize_default_settings.return_value = 0
        mock_settings_repo.get_all.return_value = [mock_pricing_setting]

        response = client.get(
            "/api/pricing/settings",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "settings" in data
        assert len(data["settings"]) == 1
        assert data["settings"][0]["setting_key"] == "default_margin_percentage"

    def test_get_settings_requires_auth(self, client):
        """Test getting settings requires authentication."""
        response = client.get("/api/pricing/settings")
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]


class TestUpdatePricingSetting:
    """Tests for PUT /api/pricing/settings/{setting_key}."""

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_setting_success(
        self,
        mock_user_repo,
        mock_auth_service,
        mock_pricing_service,
        client,
        mock_admin_user,
        mock_pricing_setting_response,
    ):
        """Test updating a pricing setting successfully."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_pricing_service.update_setting.return_value = mock_pricing_setting_response

        response = client.put(
            "/api/pricing/settings/default_margin_percentage",
            json={"setting_value": "25.0"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["setting_key"] == "default_margin_percentage"

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_setting_requires_admin_only(
        self, mock_user_repo, mock_auth_service, mock_pricing_service, client, mock_manager_user
    ):
        """Test update setting requires admin role (not manager)."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_manager_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_manager_user

        response = client.put(
            "/api/pricing/settings/default_margin_percentage",
            json={"setting_value": "25.0"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_setting_not_found_returns_404(
        self, mock_user_repo, mock_auth_service, mock_pricing_service, client, mock_admin_user
    ):
        """Test updating non-existent setting returns 404."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user
        mock_pricing_service.update_setting.return_value = None

        response = client.put(
            "/api/pricing/settings/nonexistent_key",
            json={"setting_value": "100.0"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("app.api.pricing_routes.pricing_service")
    @patch("app.api.dependencies.auth_service")
    @patch("app.api.dependencies.user_repository")
    def test_update_setting_requires_value(
        self, mock_user_repo, mock_auth_service, mock_pricing_service, client, mock_admin_user
    ):
        """Test update setting requires setting_value."""
        mock_auth_service.decode_access_token.return_value = {"sub": mock_admin_user["id"]}
        mock_user_repo.get_user_by_id.return_value = mock_admin_user

        response = client.put(
            "/api/pricing/settings/default_margin_percentage",
            json={},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "setting_value is required" in response.json()["detail"]
