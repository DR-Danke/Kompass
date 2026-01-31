"""Unit tests for Product API routes.

Tests cover:
- All CRUD endpoints
- Image management endpoints
- Tag management endpoints
- Authentication and authorization
- Query parameter handling
- Error responses
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.models.kompass_dto import (
    PaginationDTO,
    ProductFilterDTO,
    ProductImageResponseDTO,
    ProductListResponseDTO,
    ProductResponseDTO,
    ProductStatus,
    TagResponseDTO,
)
from main import app


# =============================================================================
# Test Fixtures
# =============================================================================


def create_mock_product_response(
    product_id: Optional[UUID] = None,
    sku: str = "PRD-20250101-ABC123",
    name: str = "Test Product",
    supplier_id: Optional[UUID] = None,
    status_val: ProductStatus = ProductStatus.ACTIVE,
    with_images: bool = False,
    with_tags: bool = False,
) -> ProductResponseDTO:
    """Create a mock ProductResponseDTO for testing."""
    now = datetime.now()
    product_id = product_id or uuid4()
    supplier_id = supplier_id or uuid4()

    images = []
    if with_images:
        images = [
            ProductImageResponseDTO(
                id=uuid4(),
                product_id=product_id,
                url="https://example.com/image1.jpg",
                alt_text="Primary image",
                sort_order=0,
                is_primary=True,
                created_at=now,
                updated_at=now,
            ),
        ]

    tags = []
    if with_tags:
        tags = [
            TagResponseDTO(
                id=uuid4(),
                name="Tag1",
                color="#FF0000",
                created_at=now,
                updated_at=now,
            ),
        ]

    return ProductResponseDTO(
        id=product_id,
        sku=sku,
        name=name,
        description="Test description",
        supplier_id=supplier_id,
        supplier_name="Test Supplier",
        category_id=uuid4(),
        category_name="Test Category",
        hs_code_id=uuid4(),
        hs_code="1234.56.78",
        status=status_val,
        unit_cost=Decimal("10.00"),
        unit_price=Decimal("20.00"),
        currency="USD",
        unit_of_measure="piece",
        minimum_order_qty=10,
        lead_time_days=14,
        weight_kg=Decimal("0.5"),
        dimensions="10x10x10",
        origin_country="China",
        images=images,
        tags=tags,
        created_at=now,
        updated_at=now,
    )


def create_mock_list_response(count: int = 5) -> ProductListResponseDTO:
    """Create a mock ProductListResponseDTO for testing."""
    items = [create_mock_product_response(sku=f"PRD-{i}") for i in range(count)]
    return ProductListResponseDTO(
        items=items,
        pagination=PaginationDTO(page=1, limit=20, total=count, pages=1),
        filters=ProductFilterDTO(),
    )


def create_mock_image_response(
    product_id: Optional[UUID] = None,
    image_id: Optional[UUID] = None,
) -> ProductImageResponseDTO:
    """Create a mock ProductImageResponseDTO for testing."""
    now = datetime.now()
    return ProductImageResponseDTO(
        id=image_id or uuid4(),
        product_id=product_id or uuid4(),
        url="https://example.com/image.jpg",
        alt_text="Test image",
        sort_order=0,
        is_primary=False,
        created_at=now,
        updated_at=now,
    )


def mock_admin_user() -> Dict[str, Any]:
    """Create a mock authenticated admin user."""
    return {
        "id": str(uuid4()),
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin",
        "is_active": True,
    }


def mock_viewer_user() -> Dict[str, Any]:
    """Create a mock viewer user (read-only)."""
    return {
        "id": str(uuid4()),
        "email": "viewer@example.com",
        "first_name": "Viewer",
        "last_name": "User",
        "role": "viewer",
        "is_active": True,
    }


@pytest.fixture
def client():
    """Create a test client with admin auth override."""
    # Override the get_current_user dependency
    async def override_get_current_user():
        return mock_admin_user()

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield TestClient(app)
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def client_viewer():
    """Create a test client with viewer auth override."""
    async def override_get_current_user():
        return mock_viewer_user()

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield TestClient(app)
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def client_no_auth():
    """Create a test client with no auth overrides."""
    # Make sure no overrides are set
    app.dependency_overrides.clear()
    yield TestClient(app)
    app.dependency_overrides.clear()


# =============================================================================
# List Products Tests
# =============================================================================


class TestListProducts:
    """Tests for GET /api/products endpoint."""

    def test_list_products_success(self, client):
        """Test listing products successfully."""
        mock_response = create_mock_list_response(5)

        with patch("app.api.product_routes.product_service.list_products", return_value=mock_response):
            response = client.get("/api/products")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 5
        assert data["pagination"]["total"] == 5

    def test_list_products_with_pagination(self, client):
        """Test listing products with pagination parameters."""
        mock_response = create_mock_list_response(10)
        mock_response.pagination.page = 2
        mock_response.pagination.limit = 10

        with patch("app.api.product_routes.product_service.list_products", return_value=mock_response) as mock_list:
            response = client.get("/api/products?page=2&limit=10")

        assert response.status_code == status.HTTP_200_OK
        mock_list.assert_called_once()
        call_kwargs = mock_list.call_args[1]
        assert call_kwargs["page"] == 2
        assert call_kwargs["limit"] == 10

    def test_list_products_with_filters(self, client):
        """Test listing products with filter parameters."""
        mock_response = create_mock_list_response(1)
        supplier_id = uuid4()
        category_id = uuid4()

        with patch("app.api.product_routes.product_service.list_products", return_value=mock_response) as mock_list:
            response = client.get(
                f"/api/products?supplier_id={supplier_id}&category_id={category_id}&status=active"
            )

        assert response.status_code == status.HTTP_200_OK
        mock_list.assert_called_once()
        call_kwargs = mock_list.call_args[1]
        filters = call_kwargs["filters"]
        assert filters.supplier_id == supplier_id
        assert filters.category_id == category_id
        assert filters.status == ProductStatus.ACTIVE

    def test_list_products_with_price_filters(self, client):
        """Test listing products with price range filters."""
        mock_response = create_mock_list_response(1)

        with patch("app.api.product_routes.product_service.list_products", return_value=mock_response) as mock_list:
            response = client.get("/api/products?price_min=10.00&price_max=100.00")

        assert response.status_code == status.HTTP_200_OK
        filters = mock_list.call_args[1]["filters"]
        assert filters.min_price == Decimal("10.00")
        assert filters.max_price == Decimal("100.00")

    def test_list_products_with_moq_filters(self, client):
        """Test listing products with MOQ range filters."""
        mock_response = create_mock_list_response(1)

        with patch("app.api.product_routes.product_service.list_products", return_value=mock_response) as mock_list:
            response = client.get("/api/products?moq_min=5&moq_max=100")

        assert response.status_code == status.HTTP_200_OK
        call_kwargs = mock_list.call_args[1]
        assert call_kwargs["min_moq"] == 5
        assert call_kwargs["max_moq"] == 100

    def test_list_products_with_tags(self, client):
        """Test listing products with tag filter."""
        mock_response = create_mock_list_response(1)
        tag1 = uuid4()
        tag2 = uuid4()

        with patch("app.api.product_routes.product_service.list_products", return_value=mock_response) as mock_list:
            response = client.get(f"/api/products?tags={tag1},{tag2}")

        assert response.status_code == status.HTTP_200_OK
        filters = mock_list.call_args[1]["filters"]
        assert filters.tag_ids == [tag1, tag2]

    def test_list_products_invalid_tag_uuid(self, client):
        """Test listing products with invalid tag UUID."""
        response = client.get("/api/products?tags=invalid-uuid")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid tag UUID format" in response.json()["detail"]

    def test_list_products_with_has_images(self, client):
        """Test listing products filtering by image presence."""
        mock_response = create_mock_list_response(1)

        with patch("app.api.product_routes.product_service.list_products", return_value=mock_response) as mock_list:
            response = client.get("/api/products?has_images=true")

        assert response.status_code == status.HTTP_200_OK
        assert mock_list.call_args[1]["has_images"] is True

    def test_list_products_with_sorting(self, client):
        """Test listing products with sorting parameters."""
        mock_response = create_mock_list_response(1)

        with patch("app.api.product_routes.product_service.list_products", return_value=mock_response) as mock_list:
            response = client.get("/api/products?sort_by=unit_price&sort_order=desc")

        assert response.status_code == status.HTTP_200_OK
        call_kwargs = mock_list.call_args[1]
        assert call_kwargs["sort_by"] == "unit_price"
        assert call_kwargs["sort_order"] == "desc"

    def test_list_products_unauthorized(self, client_no_auth):
        """Test listing products without authentication."""
        response = client_no_auth.get("/api/products")
        # HTTPBearer returns 403 when no credentials provided
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


# =============================================================================
# Create Product Tests
# =============================================================================


class TestCreateProduct:
    """Tests for POST /api/products endpoint."""

    def test_create_product_success(self, client):
        """Test creating a product successfully."""
        mock_response = create_mock_product_response()
        supplier_id = uuid4()

        with patch("app.api.product_routes.product_service.create_product", return_value=mock_response):
            response = client.post(
                "/api/products",
                json={
                    "name": "Test Product",
                    "supplier_id": str(supplier_id),
                },
            )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == mock_response.name

    def test_create_product_failure(self, client):
        """Test creating a product when service returns None."""
        supplier_id = uuid4()

        with patch("app.api.product_routes.product_service.create_product", return_value=None):
            response = client.post(
                "/api/products",
                json={
                    "name": "Test Product",
                    "supplier_id": str(supplier_id),
                },
            )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Failed to create product" in response.json()["detail"]

    def test_create_product_unauthorized(self, client_no_auth):
        """Test creating a product without authentication."""
        response = client_no_auth.post("/api/products", json={"name": "Test"})
        # HTTPBearer returns 403 when no credentials provided
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_create_product_forbidden_for_viewer(self, client_viewer):
        """Test that viewer role cannot create products."""
        supplier_id = uuid4()

        response = client_viewer.post(
            "/api/products",
            json={
                "name": "Test Product",
                "supplier_id": str(supplier_id),
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


# =============================================================================
# Search Products Tests
# =============================================================================


class TestSearchProducts:
    """Tests for GET /api/products/search endpoint."""

    def test_search_products_success(self, client):
        """Test searching products successfully."""
        mock_results = [create_mock_product_response(name="Widget A")]

        with patch("app.api.product_routes.product_service.search_products", return_value=mock_results):
            response = client.get("/api/products/search?q=Widget")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Widget A"

    def test_search_products_with_limit(self, client):
        """Test search respects limit parameter."""
        mock_results = [create_mock_product_response()]

        with patch("app.api.product_routes.product_service.search_products", return_value=mock_results) as mock_search:
            response = client.get("/api/products/search?q=test&limit=25")

        assert response.status_code == status.HTTP_200_OK
        mock_search.assert_called_once_with(query="test", limit=25)

    def test_search_products_empty_query(self, client):
        """Test search requires a non-empty query parameter."""
        response = client.get("/api/products/search?q=")

        # FastAPI's min_length validation returns 422
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_search_products_unauthorized(self, client_no_auth):
        """Test search without authentication."""
        response = client_no_auth.get("/api/products/search?q=test")
        # HTTPBearer returns 403 when no credentials provided
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


# =============================================================================
# Get Product Tests
# =============================================================================


class TestGetProduct:
    """Tests for GET /api/products/{id} endpoint."""

    def test_get_product_success(self, client):
        """Test getting a product successfully."""
        product_id = uuid4()
        mock_response = create_mock_product_response(product_id=product_id)

        with patch("app.api.product_routes.product_service.get_product", return_value=mock_response):
            response = client.get(f"/api/products/{product_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(product_id)

    def test_get_product_not_found(self, client):
        """Test getting a product that doesn't exist."""
        product_id = uuid4()

        with patch("app.api.product_routes.product_service.get_product", return_value=None):
            response = client.get(f"/api/products/{product_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Product not found" in response.json()["detail"]

    def test_get_product_invalid_uuid(self, client):
        """Test getting a product with invalid UUID."""
        response = client.get("/api/products/invalid-uuid")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_product_unauthorized(self, client_no_auth):
        """Test getting a product without authentication."""
        product_id = uuid4()
        response = client_no_auth.get(f"/api/products/{product_id}")
        # HTTPBearer returns 403 when no credentials provided
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


# =============================================================================
# Update Product Tests
# =============================================================================


class TestUpdateProduct:
    """Tests for PUT /api/products/{id} endpoint."""

    def test_update_product_success(self, client):
        """Test updating a product successfully."""
        product_id = uuid4()
        mock_response = create_mock_product_response(product_id=product_id, name="Updated Name")

        with patch("app.api.product_routes.product_service.update_product", return_value=mock_response):
            response = client.put(
                f"/api/products/{product_id}",
                json={"name": "Updated Name"},
            )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_update_product_not_found(self, client):
        """Test updating a product that doesn't exist."""
        product_id = uuid4()

        with patch("app.api.product_routes.product_service.update_product", return_value=None):
            response = client.put(
                f"/api/products/{product_id}",
                json={"name": "Updated Name"},
            )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_product_forbidden_for_viewer(self, client_viewer):
        """Test that viewer role cannot update products."""
        product_id = uuid4()

        response = client_viewer.put(
            f"/api/products/{product_id}",
            json={"name": "Updated Name"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


# =============================================================================
# Delete Product Tests
# =============================================================================


class TestDeleteProduct:
    """Tests for DELETE /api/products/{id} endpoint."""

    def test_delete_product_success(self, client):
        """Test deleting a product successfully."""
        product_id = uuid4()

        with patch("app.api.product_routes.product_service.delete_product", return_value=True):
            response = client.delete(f"/api/products/{product_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_product_not_found(self, client):
        """Test deleting a product that doesn't exist."""
        product_id = uuid4()

        with patch("app.api.product_routes.product_service.delete_product", return_value=False):
            response = client.delete(f"/api/products/{product_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_product_forbidden_for_viewer(self, client_viewer):
        """Test that viewer role cannot delete products."""
        product_id = uuid4()

        response = client_viewer.delete(f"/api/products/{product_id}")

        assert response.status_code == status.HTTP_403_FORBIDDEN


# =============================================================================
# Image Management Tests
# =============================================================================


class TestImageManagement:
    """Tests for image management endpoints."""

    def test_add_image_success(self, client):
        """Test adding an image to a product."""
        product_id = uuid4()
        mock_product = create_mock_product_response(product_id=product_id)
        mock_image = create_mock_image_response(product_id=product_id)

        with patch("app.api.product_routes.product_service.get_product", return_value=mock_product):
            with patch("app.api.product_routes.product_service.add_product_image", return_value=mock_image):
                response = client.post(
                    f"/api/products/{product_id}/images",
                    json={
                        "url": "https://example.com/image.jpg",
                        "alt_text": "Test image",
                        "sort_order": 0,
                        "is_primary": False,
                    },
                )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["url"] == "https://example.com/image.jpg"

    def test_add_image_product_not_found(self, client):
        """Test adding an image to a non-existent product."""
        product_id = uuid4()

        with patch("app.api.product_routes.product_service.get_product", return_value=None):
            response = client.post(
                f"/api/products/{product_id}/images",
                json={"url": "https://example.com/image.jpg"},
            )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_image_failure(self, client):
        """Test adding an image when service fails."""
        product_id = uuid4()
        mock_product = create_mock_product_response(product_id=product_id)

        with patch("app.api.product_routes.product_service.get_product", return_value=mock_product):
            with patch("app.api.product_routes.product_service.add_product_image", return_value=None):
                response = client.post(
                    f"/api/products/{product_id}/images",
                    json={"url": "https://example.com/image.jpg"},
                )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_remove_image_success(self, client):
        """Test removing an image from a product."""
        product_id = uuid4()
        image_id = uuid4()

        with patch("app.api.product_routes.product_service.remove_product_image", return_value=True):
            response = client.delete(f"/api/products/{product_id}/images/{image_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_remove_image_not_found(self, client):
        """Test removing a non-existent image."""
        product_id = uuid4()
        image_id = uuid4()

        with patch("app.api.product_routes.product_service.remove_product_image", return_value=False):
            response = client.delete(f"/api/products/{product_id}/images/{image_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_set_primary_image_success(self, client):
        """Test setting a primary image."""
        product_id = uuid4()
        image_id = uuid4()

        with patch("app.api.product_routes.product_service.set_primary_image", return_value=True):
            response = client.put(f"/api/products/{product_id}/images/{image_id}/primary")

        assert response.status_code == status.HTTP_200_OK
        assert "successfully" in response.json()["message"]

    def test_set_primary_image_not_found(self, client):
        """Test setting primary image when not found."""
        product_id = uuid4()
        image_id = uuid4()

        with patch("app.api.product_routes.product_service.set_primary_image", return_value=False):
            response = client.put(f"/api/products/{product_id}/images/{image_id}/primary")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_image_endpoints_forbidden_for_viewer(self, client_viewer):
        """Test that viewer role cannot manage images."""
        product_id = uuid4()
        image_id = uuid4()

        add_response = client_viewer.post(
            f"/api/products/{product_id}/images",
            json={"url": "https://example.com/image.jpg"},
        )
        remove_response = client_viewer.delete(
            f"/api/products/{product_id}/images/{image_id}"
        )
        primary_response = client_viewer.put(
            f"/api/products/{product_id}/images/{image_id}/primary"
        )

        assert add_response.status_code == status.HTTP_403_FORBIDDEN
        assert remove_response.status_code == status.HTTP_403_FORBIDDEN
        assert primary_response.status_code == status.HTTP_403_FORBIDDEN


# =============================================================================
# Tag Management Tests
# =============================================================================


class TestTagManagement:
    """Tests for tag management endpoints."""

    def test_add_tag_success(self, client):
        """Test adding a tag to a product."""
        product_id = uuid4()
        tag_id = uuid4()

        with patch("app.api.product_routes.product_service.add_tag_to_product", return_value=True):
            response = client.post(f"/api/products/{product_id}/tags/{tag_id}")

        assert response.status_code == status.HTTP_201_CREATED
        assert "successfully" in response.json()["message"]

    def test_add_tag_failure(self, client):
        """Test adding a tag that already exists."""
        product_id = uuid4()
        tag_id = uuid4()

        with patch("app.api.product_routes.product_service.add_tag_to_product", return_value=False):
            response = client.post(f"/api/products/{product_id}/tags/{tag_id}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_remove_tag_success(self, client):
        """Test removing a tag from a product."""
        product_id = uuid4()
        tag_id = uuid4()

        with patch("app.api.product_routes.product_service.remove_tag_from_product", return_value=True):
            response = client.delete(f"/api/products/{product_id}/tags/{tag_id}")

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_remove_tag_not_found(self, client):
        """Test removing a tag that doesn't exist on product."""
        product_id = uuid4()
        tag_id = uuid4()

        with patch("app.api.product_routes.product_service.remove_tag_from_product", return_value=False):
            response = client.delete(f"/api/products/{product_id}/tags/{tag_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_tag_endpoints_forbidden_for_viewer(self, client_viewer):
        """Test that viewer role cannot manage tags."""
        product_id = uuid4()
        tag_id = uuid4()

        add_response = client_viewer.post(f"/api/products/{product_id}/tags/{tag_id}")
        remove_response = client_viewer.delete(f"/api/products/{product_id}/tags/{tag_id}")

        assert add_response.status_code == status.HTTP_403_FORBIDDEN
        assert remove_response.status_code == status.HTTP_403_FORBIDDEN
