"""API integration tests for Kompass module.

Tests cover:
- Authentication requirements for all endpoints
- RBAC enforcement (admin-only operations)
- Cross-service integration (delete constraints)
- Pagination consistency across endpoints
- Error handling and proper status codes
"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.api.supplier_routes import router as supplier_router
from app.models.kompass_dto import (
    PaginationDTO,
    ProductFilterDTO,
    ProductListResponseDTO,
    ProductResponseDTO,
    ProductStatus,
    SupplierListResponseDTO,
    SupplierResponseDTO,
    SupplierStatus,
)


# =============================================================================
# AUTHENTICATION FIXTURES
# =============================================================================


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
def mock_manager_user():
    """Mock manager user for RBAC tests."""
    return {
        "id": str(uuid4()),
        "email": "manager@example.com",
        "role": "manager",
        "is_active": True,
    }


@pytest.fixture
def mock_viewer_user():
    """Mock viewer user for read-only tests."""
    return {
        "id": str(uuid4()),
        "email": "viewer@example.com",
        "role": "viewer",
        "is_active": True,
    }


# =============================================================================
# CLIENT FIXTURES
# =============================================================================


@pytest.fixture
def supplier_app(mock_current_user):
    """Create test FastAPI app with supplier routes."""
    test_app = FastAPI()
    test_app.include_router(supplier_router, prefix="/api/suppliers")
    test_app.dependency_overrides[get_current_user] = lambda: mock_current_user
    return test_app


@pytest.fixture
def supplier_client(supplier_app):
    """Create test client for supplier routes."""
    return TestClient(supplier_app)


@pytest.fixture
def admin_supplier_app(mock_admin_user):
    """Create test FastAPI app with admin user."""
    test_app = FastAPI()
    test_app.include_router(supplier_router, prefix="/api/suppliers")
    test_app.dependency_overrides[get_current_user] = lambda: mock_admin_user
    return test_app


@pytest.fixture
def admin_supplier_client(admin_supplier_app):
    """Create admin test client."""
    return TestClient(admin_supplier_app)


# =============================================================================
# SAMPLE DATA FIXTURES
# =============================================================================


@pytest.fixture
def sample_supplier_response():
    """Create SupplierResponseDTO for testing."""
    return SupplierResponseDTO(
        id=uuid4(),
        name="Test Supplier",
        code="TS001",
        status=SupplierStatus.ACTIVE,
        contact_name="John Doe",
        contact_email="john@example.com",
        contact_phone="123456789",
        address="123 Test Street",
        city="Shanghai",
        country="China",
        website="https://example.com",
        notes="Test notes",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_product_response():
    """Create ProductResponseDTO for testing."""
    return ProductResponseDTO(
        id=uuid4(),
        sku="PRD-001",
        name="Test Product",
        description="Test description",
        supplier_id=uuid4(),
        supplier_name="Test Supplier",
        category_id=None,
        category_name=None,
        hs_code_id=None,
        hs_code=None,
        status=ProductStatus.ACTIVE,
        unit_cost=Decimal("10.00"),
        unit_price=Decimal("20.00"),
        currency="USD",
        unit_of_measure="piece",
        minimum_order_qty=1,
        lead_time_days=None,
        weight_kg=None,
        dimensions=None,
        origin_country="China",
        images=[],
        tags=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


# =============================================================================
# AUTHENTICATION TESTS
# =============================================================================


class TestAuthenticatedEndpoints:
    """Tests for authentication requirements."""

    def test_supplier_list_requires_auth(self):
        """Test that unauthenticated requests are rejected."""
        test_app = FastAPI()
        test_app.include_router(supplier_router, prefix="/api/suppliers")
        unauth_client = TestClient(test_app)
        response = unauth_client.get("/api/suppliers")
        assert response.status_code in [401, 403]

    def test_supplier_create_requires_auth(self):
        """Test that unauthenticated creation is rejected."""
        test_app = FastAPI()
        test_app.include_router(supplier_router, prefix="/api/suppliers")
        unauth_client = TestClient(test_app)
        response = unauth_client.post("/api/suppliers", json={"name": "Test"})
        assert response.status_code in [401, 403]

    def test_supplier_update_requires_auth(self):
        """Test that unauthenticated update is rejected."""
        test_app = FastAPI()
        test_app.include_router(supplier_router, prefix="/api/suppliers")
        unauth_client = TestClient(test_app)
        response = unauth_client.put(f"/api/suppliers/{uuid4()}", json={"name": "Test"})
        assert response.status_code in [401, 403]

    def test_supplier_delete_requires_auth(self):
        """Test that unauthenticated deletion is rejected."""
        test_app = FastAPI()
        test_app.include_router(supplier_router, prefix="/api/suppliers")
        unauth_client = TestClient(test_app)
        response = unauth_client.delete(f"/api/suppliers/{uuid4()}")
        assert response.status_code in [401, 403]


# =============================================================================
# RBAC ENFORCEMENT TESTS
# =============================================================================


class TestRBACEnforcement:
    """Tests for role-based access control."""

    def test_delete_supplier_forbidden_for_regular_user(self, supplier_client):
        """Test delete forbidden for regular users."""
        response = supplier_client.delete(f"/api/suppliers/{uuid4()}")
        assert response.status_code == 403

    @patch("app.api.supplier_routes.supplier_service")
    def test_delete_supplier_allowed_for_admin(
        self, mock_service, admin_supplier_client
    ):
        """Test delete allowed for admin users."""
        mock_service.delete_supplier.return_value = True
        response = admin_supplier_client.delete(f"/api/suppliers/{uuid4()}")
        assert response.status_code == 200
        assert response.json()["message"] == "Supplier deleted successfully"

    @patch("app.api.supplier_routes.supplier_service")
    def test_list_suppliers_allowed_for_all_roles(
        self, mock_service, supplier_client, sample_supplier_response
    ):
        """Test that listing is allowed for all authenticated users."""
        mock_service.list_suppliers.return_value = SupplierListResponseDTO(
            items=[sample_supplier_response],
            pagination=PaginationDTO(page=1, limit=20, total=1, pages=1),
        )
        response = supplier_client.get("/api/suppliers")
        assert response.status_code == 200

    @patch("app.api.supplier_routes.supplier_service")
    def test_create_supplier_allowed_for_user_role(
        self, mock_service, supplier_client, sample_supplier_response
    ):
        """Test that creation is allowed for regular users."""
        mock_service.create_supplier.return_value = sample_supplier_response
        response = supplier_client.post(
            "/api/suppliers",
            json={"name": "New Supplier", "country": "China"},
        )
        assert response.status_code == 201


# =============================================================================
# CROSS-SERVICE INTEGRATION TESTS
# =============================================================================


class TestCrossServiceIntegration:
    """Tests for cross-service interactions."""

    @patch("app.api.supplier_routes.supplier_service")
    def test_delete_supplier_fails_when_products_exist(
        self, mock_service, admin_supplier_client
    ):
        """Test delete blocked when supplier has active products."""
        mock_service.delete_supplier.side_effect = ValueError(
            "Cannot delete supplier with active products"
        )
        response = admin_supplier_client.delete(f"/api/suppliers/{uuid4()}")
        assert response.status_code == 400
        assert "Cannot delete supplier with active products" in response.json()["detail"]

    @patch("app.api.supplier_routes.supplier_service")
    def test_delete_supplier_succeeds_when_no_products(
        self, mock_service, admin_supplier_client
    ):
        """Test delete succeeds when supplier has no products."""
        mock_service.delete_supplier.return_value = True
        response = admin_supplier_client.delete(f"/api/suppliers/{uuid4()}")
        assert response.status_code == 200

    @patch("app.api.supplier_routes.product_service")
    @patch("app.api.supplier_routes.supplier_service")
    def test_get_supplier_products_success(
        self,
        mock_supplier_service,
        mock_product_service,
        supplier_client,
        sample_supplier_response,
        sample_product_response,
    ):
        """Test getting products for a supplier."""
        mock_supplier_service.get_supplier.return_value = sample_supplier_response
        mock_product_service.list_products.return_value = ProductListResponseDTO(
            items=[sample_product_response],
            pagination=PaginationDTO(page=1, limit=20, total=1, pages=1),
            filters=ProductFilterDTO(supplier_id=sample_supplier_response.id),
        )

        response = supplier_client.get(
            f"/api/suppliers/{sample_supplier_response.id}/products"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1

    @patch("app.api.supplier_routes.supplier_service")
    def test_get_supplier_products_supplier_not_found(
        self, mock_service, supplier_client
    ):
        """Test products retrieval when supplier not found."""
        mock_service.get_supplier.return_value = None
        response = supplier_client.get(f"/api/suppliers/{uuid4()}/products")
        assert response.status_code == 404
        assert response.json()["detail"] == "Supplier not found"


# =============================================================================
# PAGINATION TESTS
# =============================================================================


class TestPaginationAcrossEndpoints:
    """Tests for consistent pagination behavior."""

    @patch("app.api.supplier_routes.supplier_service")
    def test_supplier_pagination_defaults(
        self, mock_service, supplier_client, sample_supplier_response
    ):
        """Test default pagination parameters."""
        mock_service.list_suppliers.return_value = SupplierListResponseDTO(
            items=[sample_supplier_response],
            pagination=PaginationDTO(page=1, limit=20, total=1, pages=1),
        )
        response = supplier_client.get("/api/suppliers")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 20

    @patch("app.api.supplier_routes.supplier_service")
    def test_supplier_pagination_custom(
        self, mock_service, supplier_client, sample_supplier_response
    ):
        """Test custom pagination parameters."""
        mock_service.list_suppliers.return_value = SupplierListResponseDTO(
            items=[sample_supplier_response],
            pagination=PaginationDTO(page=2, limit=10, total=15, pages=2),
        )
        response = supplier_client.get("/api/suppliers?page=2&limit=10")
        assert response.status_code == 200
        mock_service.list_suppliers.assert_called_once()
        call_kwargs = mock_service.list_suppliers.call_args.kwargs
        assert call_kwargs["page"] == 2
        assert call_kwargs["limit"] == 10


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


class TestErrorHandling:
    """Tests for proper error responses."""

    @patch("app.api.supplier_routes.supplier_service")
    def test_get_supplier_not_found(self, mock_service, supplier_client):
        """Test 404 response for non-existent supplier."""
        mock_service.get_supplier_with_product_count.return_value = None
        response = supplier_client.get(f"/api/suppliers/{uuid4()}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Supplier not found"

    @patch("app.api.supplier_routes.supplier_service")
    def test_update_supplier_not_found(self, mock_service, supplier_client):
        """Test 404 response for updating non-existent supplier."""
        mock_service.update_supplier.return_value = None
        response = supplier_client.put(
            f"/api/suppliers/{uuid4()}",
            json={"name": "Updated Name"},
        )
        assert response.status_code == 404

    @patch("app.api.supplier_routes.supplier_service")
    def test_create_supplier_validation_error(self, mock_service, supplier_client):
        """Test 400 response for validation errors."""
        mock_service.create_supplier.side_effect = ValueError("Invalid email format")
        response = supplier_client.post(
            "/api/suppliers",
            json={"name": "New Supplier"},
        )
        assert response.status_code == 400
        assert "Invalid email format" in response.json()["detail"]

    @patch("app.api.supplier_routes.supplier_service")
    def test_delete_supplier_not_found(self, mock_service, admin_supplier_client):
        """Test 404 response for deleting non-existent supplier."""
        mock_service.delete_supplier.return_value = False
        response = admin_supplier_client.delete(f"/api/suppliers/{uuid4()}")
        assert response.status_code == 404

    @patch("app.api.supplier_routes.supplier_service")
    def test_list_suppliers_invalid_status(self, mock_service, supplier_client):
        """Test 400 response for invalid status filter."""
        response = supplier_client.get("/api/suppliers?status=invalid_status")
        assert response.status_code == 400
        assert "Invalid status value" in response.json()["detail"]


# =============================================================================
# FILTER TESTS
# =============================================================================


class TestFilterParameters:
    """Tests for filter parameter handling."""

    @patch("app.api.supplier_routes.supplier_service")
    def test_supplier_filter_by_status(
        self, mock_service, supplier_client, sample_supplier_response
    ):
        """Test filtering suppliers by status."""
        mock_service.list_suppliers.return_value = SupplierListResponseDTO(
            items=[sample_supplier_response],
            pagination=PaginationDTO(page=1, limit=20, total=1, pages=1),
        )
        response = supplier_client.get("/api/suppliers?status=active")
        assert response.status_code == 200
        call_kwargs = mock_service.list_suppliers.call_args.kwargs
        assert call_kwargs["status"] == SupplierStatus.ACTIVE

    @patch("app.api.supplier_routes.supplier_service")
    def test_supplier_filter_by_country(
        self, mock_service, supplier_client, sample_supplier_response
    ):
        """Test filtering suppliers by country."""
        mock_service.list_suppliers.return_value = SupplierListResponseDTO(
            items=[sample_supplier_response],
            pagination=PaginationDTO(page=1, limit=20, total=1, pages=1),
        )
        response = supplier_client.get("/api/suppliers?country=China")
        assert response.status_code == 200
        call_kwargs = mock_service.list_suppliers.call_args.kwargs
        assert call_kwargs["country"] == "China"

    @patch("app.api.supplier_routes.supplier_service")
    def test_supplier_filter_by_has_products(
        self, mock_service, supplier_client, sample_supplier_response
    ):
        """Test filtering suppliers by has_products flag."""
        mock_service.list_suppliers.return_value = SupplierListResponseDTO(
            items=[sample_supplier_response],
            pagination=PaginationDTO(page=1, limit=20, total=1, pages=1),
        )
        response = supplier_client.get("/api/suppliers?has_products=true")
        assert response.status_code == 200
        call_kwargs = mock_service.list_suppliers.call_args.kwargs
        assert call_kwargs["has_products"] is True


# =============================================================================
# SEARCH TESTS
# =============================================================================


class TestSearchEndpoints:
    """Tests for search functionality."""

    @patch("app.api.supplier_routes.supplier_service")
    def test_search_suppliers_success(
        self, mock_service, supplier_client, sample_supplier_response
    ):
        """Test successful supplier search."""
        mock_service.search_suppliers.return_value = [sample_supplier_response]
        response = supplier_client.get("/api/suppliers/search?query=test")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        mock_service.search_suppliers.assert_called_once_with("test")

    @patch("app.api.supplier_routes.supplier_service")
    def test_search_suppliers_empty_results(self, mock_service, supplier_client):
        """Test search with no results."""
        mock_service.search_suppliers.return_value = []
        response = supplier_client.get("/api/suppliers/search?query=nonexistent")
        assert response.status_code == 200
        assert response.json() == []

    def test_search_suppliers_short_query(self, supplier_client):
        """Test search with query too short."""
        response = supplier_client.get("/api/suppliers/search?query=a")
        assert response.status_code == 422


# =============================================================================
# CRUD OPERATION TESTS
# =============================================================================


class TestCRUDOperations:
    """Tests for basic CRUD operations via API."""

    @patch("app.api.supplier_routes.supplier_service")
    def test_create_supplier_success(
        self, mock_service, supplier_client, sample_supplier_response
    ):
        """Test successful supplier creation."""
        mock_service.create_supplier.return_value = sample_supplier_response
        response = supplier_client.post(
            "/api/suppliers",
            json={"name": "New Supplier", "country": "China"},
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Test Supplier"
        mock_service.create_supplier.assert_called_once()

    @patch("app.api.supplier_routes.supplier_service")
    def test_get_supplier_success(
        self, mock_service, supplier_client, sample_supplier_response
    ):
        """Test successful supplier retrieval."""
        supplier_dict = {
            "id": sample_supplier_response.id,
            "name": sample_supplier_response.name,
            "code": sample_supplier_response.code,
            "status": sample_supplier_response.status.value,
            "contact_name": sample_supplier_response.contact_name,
            "contact_email": sample_supplier_response.contact_email,
            "contact_phone": sample_supplier_response.contact_phone,
            "address": sample_supplier_response.address,
            "city": sample_supplier_response.city,
            "country": sample_supplier_response.country,
            "website": sample_supplier_response.website,
            "notes": sample_supplier_response.notes,
            "product_count": 5,
            "created_at": sample_supplier_response.created_at,
            "updated_at": sample_supplier_response.updated_at,
        }
        mock_service.get_supplier_with_product_count.return_value = supplier_dict
        response = supplier_client.get(f"/api/suppliers/{sample_supplier_response.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["product_count"] == 5
        assert data["name"] == "Test Supplier"

    @patch("app.api.supplier_routes.supplier_service")
    def test_update_supplier_success(
        self, mock_service, supplier_client, sample_supplier_response
    ):
        """Test successful supplier update."""
        mock_service.update_supplier.return_value = sample_supplier_response
        response = supplier_client.put(
            f"/api/suppliers/{sample_supplier_response.id}",
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
        mock_service.update_supplier.assert_called_once()
