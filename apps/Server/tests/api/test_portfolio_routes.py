"""Unit tests for portfolio API routes."""

from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.api.portfolio_routes import router
from app.models.kompass_dto import (
    PaginationDTO,
    PortfolioListResponseDTO,
    PortfolioPublicResponseDTO,
    PortfolioResponseDTO,
    PortfolioShareTokenResponseDTO,
)


@pytest.fixture
def mock_current_user():
    """Mock current user for authentication."""
    return {
        "id": str(uuid4()),
        "email": "test@example.com",
        "role": "user",
        "is_active": True,
    }


@pytest.fixture
def mock_admin_user():
    """Mock admin user for RBAC tests."""
    return {
        "id": str(uuid4()),
        "email": "admin@example.com",
        "role": "admin",
        "is_active": True,
    }


@pytest.fixture
def sample_portfolio_data():
    """Sample portfolio data for testing."""
    return {
        "id": uuid4(),
        "name": "Test Portfolio",
        "description": "Test description",
        "niche_id": uuid4(),
        "niche_name": "Test Niche",
        "is_active": True,
        "items": [],
        "item_count": 0,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }


@pytest.fixture
def sample_portfolio_response(sample_portfolio_data):
    """Create PortfolioResponseDTO from sample data."""
    return PortfolioResponseDTO(**sample_portfolio_data)


@pytest.fixture
def sample_public_response(sample_portfolio_data):
    """Create PortfolioPublicResponseDTO from sample data."""
    return PortfolioPublicResponseDTO(
        id=sample_portfolio_data["id"],
        name=sample_portfolio_data["name"],
        description=sample_portfolio_data["description"],
        niche_name=sample_portfolio_data["niche_name"],
        items=[],
        item_count=0,
        created_at=sample_portfolio_data["created_at"],
    )


@pytest.fixture
def app(mock_current_user):
    """Create test FastAPI app with regular user dependency overrides."""
    test_app = FastAPI()
    test_app.include_router(router, prefix="/api/portfolios")

    # Override auth dependency
    test_app.dependency_overrides[get_current_user] = lambda: mock_current_user

    return test_app


@pytest.fixture
def client(app):
    """Create test client with regular user."""
    return TestClient(app)


@pytest.fixture
def admin_client(mock_admin_user):
    """Create test client with admin user for RBAC tests."""
    test_app = FastAPI()
    test_app.include_router(router, prefix="/api/portfolios")

    # Override auth dependency with admin user
    test_app.dependency_overrides[get_current_user] = lambda: mock_admin_user

    return TestClient(test_app)


@pytest.fixture
def public_client():
    """Create test client without authentication for public endpoint tests."""
    test_app = FastAPI()
    test_app.include_router(router, prefix="/api/portfolios")
    # No auth override - testing public endpoint
    return TestClient(test_app)


class TestListPortfolios:
    """Tests for GET /portfolios endpoint."""

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_list_portfolios_success(
        self, mock_service, client, sample_portfolio_response
    ):
        """Test successful portfolio listing."""
        mock_service.list_portfolios.return_value = PortfolioListResponseDTO(
            items=[sample_portfolio_response],
            pagination=PaginationDTO(page=1, limit=20, total=1, pages=1),
        )

        response = client.get("/api/portfolios")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["pagination"]["page"] == 1

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_list_portfolios_with_filters(
        self, mock_service, client, sample_portfolio_response
    ):
        """Test portfolio listing with filters."""
        mock_service.list_portfolios.return_value = PortfolioListResponseDTO(
            items=[sample_portfolio_response],
            pagination=PaginationDTO(page=1, limit=20, total=1, pages=1),
        )

        niche_id = uuid4()
        response = client.get(
            f"/api/portfolios?niche_id={niche_id}&is_active=true&page=2&limit=10"
        )

        assert response.status_code == 200
        mock_service.list_portfolios.assert_called_once()

    def test_list_portfolios_unauthenticated(self):
        """Test that unauthenticated requests are rejected."""
        test_app = FastAPI()
        test_app.include_router(router, prefix="/api/portfolios")
        unauth_client = TestClient(test_app)
        response = unauth_client.get("/api/portfolios")

        assert response.status_code in [401, 403]


class TestSearchPortfolios:
    """Tests for GET /portfolios/search endpoint."""

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_search_portfolios_success(
        self, mock_service, client, sample_portfolio_response
    ):
        """Test successful portfolio search."""
        mock_service.list_portfolios.return_value = PortfolioListResponseDTO(
            items=[sample_portfolio_response],
            pagination=PaginationDTO(page=1, limit=50, total=1, pages=1),
        )

        response = client.get("/api/portfolios/search?q=test")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_search_portfolios_empty_results(self, mock_service, client):
        """Test search with no results."""
        mock_service.list_portfolios.return_value = PortfolioListResponseDTO(
            items=[],
            pagination=PaginationDTO(page=1, limit=50, total=0, pages=0),
        )

        response = client.get("/api/portfolios/search?q=nonexistent")

        assert response.status_code == 200
        assert response.json() == []


class TestPublicShareEndpoint:
    """Tests for GET /portfolios/shared/{token} endpoint."""

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_get_portfolio_by_share_token_success(
        self, mock_service, public_client, sample_public_response
    ):
        """Test getting portfolio by valid share token (no auth required)."""
        mock_service.get_by_share_token.return_value = sample_public_response

        response = public_client.get("/api/portfolios/shared/valid-token")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_public_response.name
        mock_service.get_by_share_token.assert_called_once_with("valid-token")

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_get_portfolio_by_share_token_invalid(self, mock_service, public_client):
        """Test getting portfolio with invalid share token."""
        mock_service.get_by_share_token.return_value = None

        response = public_client.get("/api/portfolios/shared/invalid-token")

        assert response.status_code == 404


class TestCreatePortfolio:
    """Tests for POST /portfolios endpoint."""

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_create_portfolio_success(
        self, mock_service, admin_client, sample_portfolio_response
    ):
        """Test successful portfolio creation (requires admin/manager)."""
        mock_service.create_portfolio.return_value = sample_portfolio_response

        response = admin_client.post(
            "/api/portfolios",
            json={"name": "New Portfolio", "description": "New description"},
        )

        assert response.status_code == 201
        assert response.json()["name"] == "Test Portfolio"
        mock_service.create_portfolio.assert_called_once()

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_create_portfolio_fails(self, mock_service, admin_client):
        """Test portfolio creation failure."""
        mock_service.create_portfolio.return_value = None

        response = admin_client.post(
            "/api/portfolios",
            json={"name": "New Portfolio"},
        )

        assert response.status_code == 400

    def test_create_portfolio_forbidden_for_regular_user(self, client):
        """Test create forbidden for regular users."""
        response = client.post(
            "/api/portfolios",
            json={"name": "Test"},
        )

        assert response.status_code == 403


class TestGetPortfolio:
    """Tests for GET /portfolios/{portfolio_id} endpoint."""

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_get_portfolio_success(
        self, mock_service, client, sample_portfolio_response
    ):
        """Test successful portfolio retrieval."""
        mock_service.get_portfolio.return_value = sample_portfolio_response
        portfolio_id = sample_portfolio_response.id

        response = client.get(f"/api/portfolios/{portfolio_id}")

        assert response.status_code == 200
        assert response.json()["name"] == "Test Portfolio"

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_get_portfolio_not_found(self, mock_service, client):
        """Test portfolio not found."""
        mock_service.get_portfolio.return_value = None

        response = client.get(f"/api/portfolios/{uuid4()}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Portfolio not found"


class TestUpdatePortfolio:
    """Tests for PUT /portfolios/{portfolio_id} endpoint."""

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_update_portfolio_success(
        self, mock_service, admin_client, sample_portfolio_response
    ):
        """Test successful portfolio update."""
        mock_service.update_portfolio.return_value = sample_portfolio_response
        portfolio_id = sample_portfolio_response.id

        response = admin_client.put(
            f"/api/portfolios/{portfolio_id}",
            json={"name": "Updated Name"},
        )

        assert response.status_code == 200
        mock_service.update_portfolio.assert_called_once()

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_update_portfolio_not_found(self, mock_service, admin_client):
        """Test update portfolio not found."""
        mock_service.update_portfolio.return_value = None

        response = admin_client.put(
            f"/api/portfolios/{uuid4()}",
            json={"name": "Updated Name"},
        )

        assert response.status_code == 404

    def test_update_portfolio_forbidden_for_regular_user(self, client):
        """Test update forbidden for regular users."""
        response = client.put(
            f"/api/portfolios/{uuid4()}",
            json={"name": "Test"},
        )

        assert response.status_code == 403


class TestDeletePortfolio:
    """Tests for DELETE /portfolios/{portfolio_id} endpoint."""

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_delete_portfolio_success(self, mock_service, admin_client):
        """Test successful portfolio deletion."""
        mock_service.delete_portfolio.return_value = True

        response = admin_client.delete(f"/api/portfolios/{uuid4()}")

        assert response.status_code == 204

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_delete_portfolio_not_found(self, mock_service, admin_client):
        """Test delete portfolio not found."""
        mock_service.delete_portfolio.return_value = False

        response = admin_client.delete(f"/api/portfolios/{uuid4()}")

        assert response.status_code == 404

    def test_delete_portfolio_forbidden_for_regular_user(self, client):
        """Test delete forbidden for regular users."""
        response = client.delete(f"/api/portfolios/{uuid4()}")

        assert response.status_code == 403


class TestDuplicatePortfolio:
    """Tests for POST /portfolios/{portfolio_id}/duplicate endpoint."""

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_duplicate_portfolio_success(
        self, mock_service, admin_client, sample_portfolio_response
    ):
        """Test successful portfolio duplication."""
        mock_service.duplicate_portfolio.return_value = sample_portfolio_response
        portfolio_id = uuid4()

        response = admin_client.post(
            f"/api/portfolios/{portfolio_id}/duplicate",
            json={"new_name": "Duplicated Portfolio"},
        )

        assert response.status_code == 201
        mock_service.duplicate_portfolio.assert_called_once()

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_duplicate_portfolio_source_not_found(self, mock_service, admin_client):
        """Test duplicate when source portfolio not found."""
        mock_service.duplicate_portfolio.return_value = None
        mock_service.get_portfolio.return_value = None
        portfolio_id = uuid4()

        response = admin_client.post(
            f"/api/portfolios/{portfolio_id}/duplicate",
            json={"new_name": "Duplicated Portfolio"},
        )

        assert response.status_code == 404

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_duplicate_portfolio_name_exists(
        self, mock_service, admin_client, sample_portfolio_response
    ):
        """Test duplicate when new name already exists."""
        mock_service.duplicate_portfolio.return_value = None
        mock_service.get_portfolio.return_value = sample_portfolio_response
        portfolio_id = uuid4()

        response = admin_client.post(
            f"/api/portfolios/{portfolio_id}/duplicate",
            json={"new_name": "Existing Name"},
        )

        assert response.status_code == 400


class TestProductManagement:
    """Tests for product management endpoints."""

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_add_product_success(self, mock_service, admin_client):
        """Test adding product to portfolio."""
        mock_service.add_product_to_portfolio.return_value = True
        portfolio_id = uuid4()
        product_id = uuid4()

        response = admin_client.post(
            f"/api/portfolios/{portfolio_id}/products/{product_id}",
            json={"curator_notes": "Great product"},
        )

        assert response.status_code == 201
        assert "successfully" in response.json()["message"]

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_add_product_portfolio_not_found(
        self, mock_service, admin_client, sample_portfolio_response
    ):
        """Test adding product when portfolio not found."""
        mock_service.add_product_to_portfolio.return_value = False
        mock_service.get_portfolio.return_value = None
        portfolio_id = uuid4()
        product_id = uuid4()

        response = admin_client.post(
            f"/api/portfolios/{portfolio_id}/products/{product_id}",
        )

        assert response.status_code == 404

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_remove_product_success(self, mock_service, admin_client):
        """Test removing product from portfolio."""
        mock_service.remove_product_from_portfolio.return_value = True
        portfolio_id = uuid4()
        product_id = uuid4()

        response = admin_client.delete(
            f"/api/portfolios/{portfolio_id}/products/{product_id}",
        )

        assert response.status_code == 204

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_remove_product_not_found(self, mock_service, admin_client):
        """Test removing product not in portfolio."""
        mock_service.remove_product_from_portfolio.return_value = False
        portfolio_id = uuid4()
        product_id = uuid4()

        response = admin_client.delete(
            f"/api/portfolios/{portfolio_id}/products/{product_id}",
        )

        assert response.status_code == 404

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_reorder_products_success(self, mock_service, admin_client):
        """Test reordering products."""
        mock_service.reorder_products.return_value = True
        portfolio_id = uuid4()

        response = admin_client.put(
            f"/api/portfolios/{portfolio_id}/products/reorder",
            json={"product_ids": [str(uuid4()), str(uuid4())]},
        )

        assert response.status_code == 200
        assert "successfully" in response.json()["message"]

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_reorder_products_mismatch(
        self, mock_service, admin_client, sample_portfolio_response
    ):
        """Test reordering with mismatched product IDs."""
        mock_service.reorder_products.return_value = False
        mock_service.get_portfolio.return_value = sample_portfolio_response
        portfolio_id = uuid4()

        response = admin_client.put(
            f"/api/portfolios/{portfolio_id}/products/reorder",
            json={"product_ids": [str(uuid4())]},
        )

        assert response.status_code == 400

    def test_product_management_forbidden_for_regular_user(self, client):
        """Test product management forbidden for regular users."""
        portfolio_id = uuid4()
        product_id = uuid4()

        # Add product
        response = client.post(f"/api/portfolios/{portfolio_id}/products/{product_id}")
        assert response.status_code == 403

        # Remove product
        response = client.delete(f"/api/portfolios/{portfolio_id}/products/{product_id}")
        assert response.status_code == 403

        # Reorder products
        response = client.put(
            f"/api/portfolios/{portfolio_id}/products/reorder",
            json={"product_ids": []},
        )
        assert response.status_code == 403


class TestShareToken:
    """Tests for POST /portfolios/{portfolio_id}/share endpoint."""

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_generate_share_token_success(self, mock_service, admin_client):
        """Test generating share token."""
        portfolio_id = uuid4()
        mock_service.get_share_token.return_value = PortfolioShareTokenResponseDTO(
            token="test-token",
            portfolio_id=portfolio_id,
            expires_at=datetime.now(),
        )

        response = admin_client.post(f"/api/portfolios/{portfolio_id}/share")

        assert response.status_code == 200
        data = response.json()
        assert data["token"] == "test-token"
        assert data["portfolio_id"] == str(portfolio_id)

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_generate_share_token_not_found(self, mock_service, admin_client):
        """Test generating token for non-existent portfolio."""
        mock_service.get_share_token.return_value = None
        portfolio_id = uuid4()

        response = admin_client.post(f"/api/portfolios/{portfolio_id}/share")

        assert response.status_code == 404

    def test_share_token_forbidden_for_regular_user(self, client):
        """Test share token generation forbidden for regular users."""
        portfolio_id = uuid4()
        response = client.post(f"/api/portfolios/{portfolio_id}/share")

        assert response.status_code == 403


class TestCreateFromFilters:
    """Tests for POST /portfolios/from-filters endpoint."""

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_create_from_filters_success(
        self, mock_service, admin_client, sample_portfolio_response
    ):
        """Test creating portfolio from filters."""
        mock_service.create_from_filters.return_value = sample_portfolio_response

        response = admin_client.post(
            "/api/portfolios/from-filters",
            json={
                "name": "Filtered Portfolio",
                "filters": {"status": "active"},
            },
        )

        assert response.status_code == 201
        mock_service.create_from_filters.assert_called_once()

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_create_from_filters_name_exists(self, mock_service, admin_client):
        """Test creating portfolio with existing name."""
        mock_service.create_from_filters.return_value = None

        response = admin_client.post(
            "/api/portfolios/from-filters",
            json={
                "name": "Existing Name",
                "filters": {},
            },
        )

        assert response.status_code == 400

    def test_create_from_filters_forbidden_for_regular_user(self, client):
        """Test create from filters forbidden for regular users."""
        response = client.post(
            "/api/portfolios/from-filters",
            json={
                "name": "Test",
                "filters": {},
            },
        )

        assert response.status_code == 403


class TestPdfExport:
    """Tests for GET /portfolios/{portfolio_id}/export/pdf endpoint."""

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_export_pdf_success(
        self, mock_service, client, sample_portfolio_response
    ):
        """Test successful PDF export."""
        # Mock PDF bytes
        pdf_bytes = b"%PDF-1.4 mock pdf content"
        mock_service.generate_pdf.return_value = pdf_bytes
        mock_service.get_portfolio.return_value = sample_portfolio_response
        portfolio_id = sample_portfolio_response.id

        response = client.get(f"/api/portfolios/{portfolio_id}/export/pdf")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]
        assert response.content == pdf_bytes
        mock_service.generate_pdf.assert_called_once_with(portfolio_id)

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_export_pdf_not_found(self, mock_service, client):
        """Test PDF export for non-existent portfolio."""
        mock_service.generate_pdf.return_value = None
        portfolio_id = uuid4()

        response = client.get(f"/api/portfolios/{portfolio_id}/export/pdf")

        assert response.status_code == 404
        assert response.json()["detail"] == "Portfolio not found"

    def test_export_pdf_requires_auth(self):
        """Test that PDF export requires authentication."""
        test_app = FastAPI()
        test_app.include_router(router, prefix="/api/portfolios")
        unauth_client = TestClient(test_app)
        portfolio_id = uuid4()

        response = unauth_client.get(f"/api/portfolios/{portfolio_id}/export/pdf")

        assert response.status_code in [401, 403]


class TestShareAliasEndpoint:
    """Tests for GET /portfolios/share/{token} alias endpoint."""

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_share_alias_success(
        self, mock_service, public_client, sample_public_response
    ):
        """Test getting portfolio via /share/{token} alias (no auth required)."""
        mock_service.get_by_share_token.return_value = sample_public_response

        response = public_client.get("/api/portfolios/share/valid-token")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_public_response.name
        mock_service.get_by_share_token.assert_called_once_with("valid-token")

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_share_alias_invalid_token(self, mock_service, public_client):
        """Test /share/{token} with invalid token."""
        mock_service.get_by_share_token.return_value = None

        response = public_client.get("/api/portfolios/share/invalid-token")

        assert response.status_code == 404


class TestItemsAliasEndpoints:
    """Tests for /items path alias endpoints."""

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_add_item_via_items_endpoint(self, mock_service, admin_client):
        """Test adding product via POST /items endpoint."""
        mock_service.add_product_to_portfolio.return_value = True
        portfolio_id = uuid4()
        product_id = uuid4()

        response = admin_client.post(
            f"/api/portfolios/{portfolio_id}/items",
            json={"product_id": str(product_id), "curator_notes": "Great product"},
        )

        assert response.status_code == 201
        assert "successfully" in response.json()["message"]
        mock_service.add_product_to_portfolio.assert_called_once()

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_add_item_portfolio_not_found(
        self, mock_service, admin_client
    ):
        """Test POST /items when portfolio not found."""
        mock_service.add_product_to_portfolio.return_value = False
        mock_service.get_portfolio.return_value = None
        portfolio_id = uuid4()
        product_id = uuid4()

        response = admin_client.post(
            f"/api/portfolios/{portfolio_id}/items",
            json={"product_id": str(product_id)},
        )

        assert response.status_code == 404

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_remove_item_via_items_endpoint(self, mock_service, admin_client):
        """Test removing product via DELETE /items/{product_id} endpoint."""
        mock_service.remove_product_from_portfolio.return_value = True
        portfolio_id = uuid4()
        product_id = uuid4()

        response = admin_client.delete(
            f"/api/portfolios/{portfolio_id}/items/{product_id}",
        )

        assert response.status_code == 204
        mock_service.remove_product_from_portfolio.assert_called_once_with(
            portfolio_id, product_id
        )

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_remove_item_not_found(self, mock_service, admin_client):
        """Test DELETE /items/{product_id} when product not in portfolio."""
        mock_service.remove_product_from_portfolio.return_value = False
        portfolio_id = uuid4()
        product_id = uuid4()

        response = admin_client.delete(
            f"/api/portfolios/{portfolio_id}/items/{product_id}",
        )

        assert response.status_code == 404

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_reorder_via_items_endpoint(self, mock_service, admin_client):
        """Test reordering via PUT /items/reorder endpoint."""
        mock_service.reorder_products.return_value = True
        portfolio_id = uuid4()

        response = admin_client.put(
            f"/api/portfolios/{portfolio_id}/items/reorder",
            json={"product_ids": [str(uuid4()), str(uuid4())]},
        )

        assert response.status_code == 200
        assert "successfully" in response.json()["message"]

    @patch("app.api.portfolio_routes.portfolio_service")
    def test_reorder_items_mismatch(
        self, mock_service, admin_client, sample_portfolio_response
    ):
        """Test PUT /items/reorder with mismatched product IDs."""
        mock_service.reorder_products.return_value = False
        mock_service.get_portfolio.return_value = sample_portfolio_response
        portfolio_id = uuid4()

        response = admin_client.put(
            f"/api/portfolios/{portfolio_id}/items/reorder",
            json={"product_ids": [str(uuid4())]},
        )

        assert response.status_code == 400

    def test_items_endpoints_forbidden_for_regular_user(self, client):
        """Test /items endpoints forbidden for regular users."""
        portfolio_id = uuid4()
        product_id = uuid4()

        # Add item
        response = client.post(
            f"/api/portfolios/{portfolio_id}/items",
            json={"product_id": str(product_id)},
        )
        assert response.status_code == 403

        # Remove item
        response = client.delete(f"/api/portfolios/{portfolio_id}/items/{product_id}")
        assert response.status_code == 403

        # Reorder items
        response = client.put(
            f"/api/portfolios/{portfolio_id}/items/reorder",
            json={"product_ids": []},
        )
        assert response.status_code == 403
