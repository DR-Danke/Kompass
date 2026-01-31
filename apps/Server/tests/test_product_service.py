"""Unit tests for ProductService.

Tests cover:
- SKU generation
- CRUD operations
- Full-text search
- Bulk create
- Image management
- Tag management
- Filtering and sorting
"""

import re
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from app.models.kompass_dto import (
    ProductCreateDTO,
    ProductFilterDTO,
    ProductImageCreateDTO,
    ProductStatus,
    ProductUpdateDTO,
)
from app.services.product_service import ProductService


# =============================================================================
# Test Fixtures
# =============================================================================


def create_mock_product(
    product_id: Optional[UUID] = None,
    sku: str = "PRD-20250101-ABC123",
    name: str = "Test Product",
    supplier_id: Optional[UUID] = None,
    status: str = "active",
    with_images: bool = False,
    with_tags: bool = False,
) -> Dict[str, Any]:
    """Create a mock product dictionary for testing."""
    now = datetime.now()
    product_id = product_id or uuid4()
    supplier_id = supplier_id or uuid4()

    product = {
        "id": product_id,
        "sku": sku,
        "name": name,
        "description": "Test description",
        "supplier_id": supplier_id,
        "supplier_name": "Test Supplier",
        "category_id": uuid4(),
        "category_name": "Test Category",
        "hs_code_id": uuid4(),
        "hs_code": "1234.56.78",
        "status": status,
        "unit_cost": Decimal("10.00"),
        "unit_price": Decimal("20.00"),
        "currency": "USD",
        "unit_of_measure": "piece",
        "minimum_order_qty": 10,
        "lead_time_days": 14,
        "weight_kg": Decimal("0.5"),
        "dimensions": "10x10x10",
        "origin_country": "China",
        "created_at": now,
        "updated_at": now,
        "images": [],
        "tags": [],
    }

    if with_images:
        product["images"] = [
            {
                "id": uuid4(),
                "product_id": product_id,
                "url": "https://example.com/image1.jpg",
                "alt_text": "Primary image",
                "sort_order": 0,
                "is_primary": True,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": uuid4(),
                "product_id": product_id,
                "url": "https://example.com/image2.jpg",
                "alt_text": "Secondary image",
                "sort_order": 1,
                "is_primary": False,
                "created_at": now,
                "updated_at": now,
            },
        ]

    if with_tags:
        product["tags"] = [
            {
                "id": uuid4(),
                "name": "Tag1",
                "color": "#FF0000",
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": uuid4(),
                "name": "Tag2",
                "color": "#00FF00",
                "created_at": now,
                "updated_at": now,
            },
        ]

    return product


@pytest.fixture
def mock_repository():
    """Create a mock ProductRepository."""
    return MagicMock()


@pytest.fixture
def product_service(mock_repository):
    """Create a ProductService with a mock repository."""
    return ProductService(repository=mock_repository)


# =============================================================================
# SKU Generation Tests
# =============================================================================


class TestSKUGeneration:
    """Tests for SKU auto-generation."""

    def test_generate_sku_format(self, product_service):
        """Test that generated SKU follows the correct format."""
        sku = product_service._generate_sku()

        # Format: PRD-{YYYYMMDD}-{6_random_alphanum}
        pattern = r"^PRD-\d{8}-[A-F0-9]{6}$"
        assert re.match(pattern, sku), f"SKU '{sku}' does not match expected pattern"

    def test_generate_sku_date_portion(self, product_service):
        """Test that SKU contains today's date."""
        sku = product_service._generate_sku()
        today = datetime.now().strftime("%Y%m%d")
        assert today in sku, f"SKU '{sku}' does not contain today's date"

    def test_generate_sku_uniqueness(self, product_service):
        """Test that generated SKUs are unique."""
        skus = [product_service._generate_sku() for _ in range(100)]
        assert len(skus) == len(set(skus)), "Generated SKUs should be unique"


# =============================================================================
# Create Product Tests
# =============================================================================


class TestCreateProduct:
    """Tests for product creation."""

    def test_create_product_with_provided_sku(
        self, product_service, mock_repository
    ):
        """Test creating a product with a provided SKU."""
        product_id = uuid4()
        supplier_id = uuid4()
        mock_product = create_mock_product(
            product_id=product_id,
            sku="CUSTOM-SKU-001",
            supplier_id=supplier_id,
        )

        mock_repository.create.return_value = {"id": product_id}
        mock_repository.get_by_id.return_value = mock_product

        request = ProductCreateDTO(
            sku="CUSTOM-SKU-001",
            name="Test Product",
            supplier_id=supplier_id,
        )

        result = product_service.create_product(request)

        assert result is not None
        assert result.sku == "CUSTOM-SKU-001"
        mock_repository.create.assert_called_once()
        call_kwargs = mock_repository.create.call_args
        assert call_kwargs[1]["sku"] == "CUSTOM-SKU-001"

    def test_create_product_auto_generates_sku(
        self, product_service, mock_repository
    ):
        """Test that SKU is auto-generated when not provided."""
        product_id = uuid4()
        supplier_id = uuid4()

        # Mock will be called with auto-generated SKU
        def create_side_effect(**kwargs):
            # Verify SKU follows auto-generated pattern
            assert kwargs["sku"].startswith("PRD-")
            return {"id": product_id}

        mock_repository.create.side_effect = create_side_effect
        mock_repository.get_by_id.return_value = create_mock_product(
            product_id=product_id,
            supplier_id=supplier_id,
        )

        request = ProductCreateDTO(
            sku=None,  # None SKU should trigger auto-generation
            name="Test Product",
            supplier_id=supplier_id,
        )

        result = product_service.create_product(request)

        assert result is not None
        mock_repository.create.assert_called_once()

    def test_create_product_with_images(
        self, product_service, mock_repository
    ):
        """Test creating a product with images."""
        product_id = uuid4()
        supplier_id = uuid4()

        mock_repository.create.return_value = {"id": product_id}
        mock_repository.add_image.return_value = {"id": uuid4()}
        mock_repository.get_by_id.return_value = create_mock_product(
            product_id=product_id,
            supplier_id=supplier_id,
            with_images=True,
        )

        request = ProductCreateDTO(
            sku="TEST-001",
            name="Test Product",
            supplier_id=supplier_id,
            images=[
                ProductImageCreateDTO(url="https://example.com/img1.jpg", is_primary=True),
                ProductImageCreateDTO(url="https://example.com/img2.jpg"),
            ],
        )

        result = product_service.create_product(request)

        assert result is not None
        assert len(result.images) == 2
        assert mock_repository.add_image.call_count == 2

    def test_create_product_with_tags(
        self, product_service, mock_repository
    ):
        """Test creating a product with tags."""
        product_id = uuid4()
        supplier_id = uuid4()
        tag_ids = [uuid4(), uuid4()]

        mock_repository.create.return_value = {"id": product_id}
        mock_repository.add_tag.return_value = True
        mock_repository.get_by_id.return_value = create_mock_product(
            product_id=product_id,
            supplier_id=supplier_id,
            with_tags=True,
        )

        request = ProductCreateDTO(
            sku="TEST-001",
            name="Test Product",
            supplier_id=supplier_id,
            tag_ids=tag_ids,
        )

        result = product_service.create_product(request)

        assert result is not None
        assert len(result.tags) == 2
        assert mock_repository.add_tag.call_count == 2

    def test_create_product_returns_none_on_failure(
        self, product_service, mock_repository
    ):
        """Test that create returns None when repository fails."""
        mock_repository.create.return_value = None

        request = ProductCreateDTO(
            sku="TEST-001",
            name="Test Product",
            supplier_id=uuid4(),
        )

        result = product_service.create_product(request)

        assert result is None


# =============================================================================
# Get Product Tests
# =============================================================================


class TestGetProduct:
    """Tests for getting a product by ID."""

    def test_get_product_found(self, product_service, mock_repository):
        """Test getting a product that exists."""
        product_id = uuid4()
        mock_product = create_mock_product(product_id=product_id)
        mock_repository.get_by_id.return_value = mock_product

        result = product_service.get_product(product_id)

        assert result is not None
        assert result.id == product_id
        mock_repository.get_by_id.assert_called_once_with(product_id)

    def test_get_product_not_found(self, product_service, mock_repository):
        """Test getting a product that doesn't exist."""
        mock_repository.get_by_id.return_value = None

        result = product_service.get_product(uuid4())

        assert result is None

    def test_get_product_includes_images_and_tags(
        self, product_service, mock_repository
    ):
        """Test that get_product includes images and tags."""
        product_id = uuid4()
        mock_product = create_mock_product(
            product_id=product_id,
            with_images=True,
            with_tags=True,
        )
        mock_repository.get_by_id.return_value = mock_product

        result = product_service.get_product(product_id)

        assert result is not None
        assert len(result.images) == 2
        assert len(result.tags) == 2


# =============================================================================
# List Products Tests
# =============================================================================


class TestListProducts:
    """Tests for listing products with filters."""

    def test_list_products_basic(self, product_service, mock_repository):
        """Test basic product listing."""
        mock_products = [
            create_mock_product(sku=f"PRD-{i}") for i in range(5)
        ]
        mock_repository.get_all.return_value = (mock_products, 5)

        result = product_service.list_products()

        assert len(result.items) == 5
        assert result.pagination.total == 5

    def test_list_products_with_pagination(
        self, product_service, mock_repository
    ):
        """Test product listing with pagination."""
        mock_products = [create_mock_product() for _ in range(10)]
        mock_repository.get_all.return_value = (mock_products, 100)

        result = product_service.list_products(page=2, limit=10)

        assert result.pagination.page == 2
        assert result.pagination.limit == 10
        assert result.pagination.total == 100
        assert result.pagination.pages == 10

    def test_list_products_with_filters(
        self, product_service, mock_repository
    ):
        """Test product listing with filters."""
        mock_products = [create_mock_product()]
        mock_repository.get_all.return_value = (mock_products, 1)

        filters = ProductFilterDTO(
            status=ProductStatus.ACTIVE,
            min_price=Decimal("10.00"),
            max_price=Decimal("100.00"),
        )

        product_service.list_products(filters=filters)

        mock_repository.get_all.assert_called_once()
        call_kwargs = mock_repository.get_all.call_args[1]
        assert call_kwargs["status"] == "active"
        assert call_kwargs["min_price"] == Decimal("10.00")
        assert call_kwargs["max_price"] == Decimal("100.00")

    def test_list_products_with_has_images_filter(
        self, product_service, mock_repository
    ):
        """Test filtering products by image presence."""
        mock_products = [create_mock_product(with_images=True)]
        mock_repository.get_all.return_value = (mock_products, 1)

        product_service.list_products(has_images=True)

        call_kwargs = mock_repository.get_all.call_args[1]
        assert call_kwargs["has_images"] is True

    def test_list_products_with_moq_range(
        self, product_service, mock_repository
    ):
        """Test filtering products by MOQ range."""
        mock_products = [create_mock_product()]
        mock_repository.get_all.return_value = (mock_products, 1)

        product_service.list_products(min_moq=5, max_moq=100)

        call_kwargs = mock_repository.get_all.call_args[1]
        assert call_kwargs["min_moq"] == 5
        assert call_kwargs["max_moq"] == 100

    def test_list_products_with_sorting(
        self, product_service, mock_repository
    ):
        """Test product listing with sorting."""
        mock_products = [create_mock_product()]
        mock_repository.get_all.return_value = (mock_products, 1)

        product_service.list_products(
            sort_by="unit_price", sort_order="desc"
        )

        call_kwargs = mock_repository.get_all.call_args[1]
        assert call_kwargs["sort_by"] == "unit_price"
        assert call_kwargs["sort_order"] == "desc"


# =============================================================================
# Update Product Tests
# =============================================================================


class TestUpdateProduct:
    """Tests for updating a product."""

    def test_update_product_success(self, product_service, mock_repository):
        """Test successful product update."""
        product_id = uuid4()
        mock_product = create_mock_product(
            product_id=product_id,
            name="Updated Name",
        )
        mock_repository.update.return_value = mock_product

        request = ProductUpdateDTO(name="Updated Name")
        result = product_service.update_product(product_id, request)

        assert result is not None
        assert result.name == "Updated Name"

    def test_update_product_not_found(
        self, product_service, mock_repository
    ):
        """Test updating a product that doesn't exist."""
        mock_repository.update.return_value = None

        request = ProductUpdateDTO(name="Updated Name")
        result = product_service.update_product(uuid4(), request)

        assert result is None

    def test_update_product_partial_fields(
        self, product_service, mock_repository
    ):
        """Test that only provided fields are updated."""
        product_id = uuid4()
        mock_product = create_mock_product(product_id=product_id)
        mock_repository.update.return_value = mock_product

        request = ProductUpdateDTO(
            name="New Name",
            unit_price=Decimal("99.99"),
        )
        product_service.update_product(product_id, request)

        call_kwargs = mock_repository.update.call_args[1]
        assert "name" in call_kwargs
        assert "unit_price" in call_kwargs
        assert "sku" not in call_kwargs
        assert "description" not in call_kwargs


# =============================================================================
# Delete Product Tests
# =============================================================================


class TestDeleteProduct:
    """Tests for deleting a product."""

    def test_delete_product_success(self, product_service, mock_repository):
        """Test successful product deletion."""
        mock_repository.delete.return_value = True

        result = product_service.delete_product(uuid4())

        assert result is True

    def test_delete_product_not_found(
        self, product_service, mock_repository
    ):
        """Test deleting a product that doesn't exist."""
        mock_repository.delete.return_value = False

        result = product_service.delete_product(uuid4())

        assert result is False


# =============================================================================
# Search Products Tests
# =============================================================================


class TestSearchProducts:
    """Tests for full-text search."""

    def test_search_products_returns_results(
        self, product_service, mock_repository
    ):
        """Test search returns matching products."""
        mock_products = [
            create_mock_product(name="Widget A"),
            create_mock_product(name="Widget B"),
        ]
        mock_repository.get_all.return_value = (mock_products, 2)

        results = product_service.search_products("Widget")

        assert len(results) == 2
        call_kwargs = mock_repository.get_all.call_args[1]
        assert call_kwargs["search"] == "Widget"

    def test_search_products_empty_query(
        self, product_service, mock_repository
    ):
        """Test search with empty query returns empty list."""
        results = product_service.search_products("")

        assert results == []
        mock_repository.get_all.assert_not_called()

    def test_search_products_whitespace_query(
        self, product_service, mock_repository
    ):
        """Test search with whitespace query returns empty list."""
        results = product_service.search_products("   ")

        assert results == []
        mock_repository.get_all.assert_not_called()

    def test_search_products_respects_limit(
        self, product_service, mock_repository
    ):
        """Test search respects the limit parameter."""
        mock_products = [create_mock_product()]
        mock_repository.get_all.return_value = (mock_products, 1)

        product_service.search_products("test", limit=25)

        call_kwargs = mock_repository.get_all.call_args[1]
        assert call_kwargs["limit"] == 25


# =============================================================================
# Bulk Create Tests
# =============================================================================


class TestBulkCreateProducts:
    """Tests for bulk product creation."""

    def test_bulk_create_all_success(
        self, product_service, mock_repository
    ):
        """Test bulk create with all products succeeding."""
        supplier_id = uuid4()

        def create_side_effect(**kwargs):
            return {"id": uuid4()}

        mock_repository.create.side_effect = create_side_effect
        mock_repository.get_by_id.return_value = create_mock_product(
            supplier_id=supplier_id
        )

        products = [
            ProductCreateDTO(sku=f"SKU-{i}", name=f"Product {i}", supplier_id=supplier_id)
            for i in range(3)
        ]

        result = product_service.bulk_create_products(products)

        assert result.total_count == 3
        assert result.success_count == 3
        assert result.failure_count == 0
        assert len(result.successful) == 3
        assert len(result.failed) == 0

    def test_bulk_create_partial_failure(
        self, product_service, mock_repository
    ):
        """Test bulk create with some products failing."""
        supplier_id = uuid4()
        call_count = [0]

        def create_side_effect(**kwargs):
            call_count[0] += 1
            if call_count[0] == 2:
                return None  # Second product fails
            return {"id": uuid4()}

        mock_repository.create.side_effect = create_side_effect
        mock_repository.get_by_id.return_value = create_mock_product(
            supplier_id=supplier_id
        )

        products = [
            ProductCreateDTO(sku=f"SKU-{i}", name=f"Product {i}", supplier_id=supplier_id)
            for i in range(3)
        ]

        result = product_service.bulk_create_products(products)

        assert result.total_count == 3
        assert result.success_count == 2
        assert result.failure_count == 1
        assert len(result.failed) == 1
        assert result.failed[0].index == 1

    def test_bulk_create_with_exception(
        self, product_service, mock_repository
    ):
        """Test bulk create handles exceptions gracefully."""
        supplier_id = uuid4()
        call_count = [0]

        def create_side_effect(**kwargs):
            call_count[0] += 1
            if call_count[0] == 2:
                raise Exception("Database error")
            return {"id": uuid4()}

        mock_repository.create.side_effect = create_side_effect
        mock_repository.get_by_id.return_value = create_mock_product(
            supplier_id=supplier_id
        )

        products = [
            ProductCreateDTO(sku=f"SKU-{i}", name=f"Product {i}", supplier_id=supplier_id)
            for i in range(3)
        ]

        result = product_service.bulk_create_products(products)

        assert result.failure_count == 1
        assert "Database error" in result.failed[0].error

    def test_bulk_create_empty_list(self, product_service, mock_repository):
        """Test bulk create with empty list."""
        result = product_service.bulk_create_products([])

        assert result.total_count == 0
        assert result.success_count == 0
        assert result.failure_count == 0


# =============================================================================
# Image Management Tests
# =============================================================================


class TestImageManagement:
    """Tests for image management methods."""

    def test_add_product_image_success(
        self, product_service, mock_repository
    ):
        """Test adding an image to a product."""
        product_id = uuid4()
        now = datetime.now()
        mock_image = {
            "id": uuid4(),
            "product_id": product_id,
            "url": "https://example.com/image.jpg",
            "alt_text": "Test image",
            "sort_order": 0,
            "is_primary": True,
            "created_at": now,
            "updated_at": now,
        }
        mock_repository.add_image.return_value = mock_image

        result = product_service.add_product_image(
            product_id=product_id,
            image_url="https://example.com/image.jpg",
            is_primary=True,
            alt_text="Test image",
        )

        assert result is not None
        assert result.url == "https://example.com/image.jpg"
        assert result.is_primary is True

    def test_add_product_image_failure(
        self, product_service, mock_repository
    ):
        """Test adding an image when repository fails."""
        mock_repository.add_image.return_value = None

        result = product_service.add_product_image(
            product_id=uuid4(),
            image_url="https://example.com/image.jpg",
        )

        assert result is None

    def test_remove_product_image_success(
        self, product_service, mock_repository
    ):
        """Test removing an image from a product."""
        mock_repository.remove_image.return_value = True

        result = product_service.remove_product_image(uuid4(), uuid4())

        assert result is True

    def test_remove_product_image_failure(
        self, product_service, mock_repository
    ):
        """Test removing an image that doesn't exist."""
        mock_repository.remove_image.return_value = False

        result = product_service.remove_product_image(uuid4(), uuid4())

        assert result is False

    def test_set_primary_image_success(
        self, product_service, mock_repository
    ):
        """Test setting a primary image."""
        mock_repository.set_primary_image.return_value = True

        result = product_service.set_primary_image(uuid4(), uuid4())

        assert result is True

    def test_set_primary_image_failure(
        self, product_service, mock_repository
    ):
        """Test setting primary image when it fails."""
        mock_repository.set_primary_image.return_value = False

        result = product_service.set_primary_image(uuid4(), uuid4())

        assert result is False


# =============================================================================
# Tag Management Tests
# =============================================================================


class TestTagManagement:
    """Tests for tag management methods."""

    def test_add_tag_to_product_success(
        self, product_service, mock_repository
    ):
        """Test adding a tag to a product."""
        mock_repository.add_tag.return_value = True

        result = product_service.add_tag_to_product(uuid4(), uuid4())

        assert result is True

    def test_add_tag_to_product_failure(
        self, product_service, mock_repository
    ):
        """Test adding a tag that fails."""
        mock_repository.add_tag.return_value = False

        result = product_service.add_tag_to_product(uuid4(), uuid4())

        assert result is False

    def test_remove_tag_from_product_success(
        self, product_service, mock_repository
    ):
        """Test removing a tag from a product."""
        mock_repository.remove_tag.return_value = True

        result = product_service.remove_tag_from_product(uuid4(), uuid4())

        assert result is True

    def test_remove_tag_from_product_failure(
        self, product_service, mock_repository
    ):
        """Test removing a tag that fails."""
        mock_repository.remove_tag.return_value = False

        result = product_service.remove_tag_from_product(uuid4(), uuid4())

        assert result is False

    def test_get_products_by_tag(
        self, product_service, mock_repository
    ):
        """Test getting products by tag."""
        tag_id = uuid4()
        mock_products = [
            create_mock_product(with_tags=True) for _ in range(3)
        ]
        mock_repository.get_all.return_value = (mock_products, 3)

        results = product_service.get_products_by_tag(tag_id)

        assert len(results) == 3
        call_kwargs = mock_repository.get_all.call_args[1]
        assert call_kwargs["tag_ids"] == [tag_id]

    def test_get_products_by_tag_no_results(
        self, product_service, mock_repository
    ):
        """Test getting products by tag with no matches."""
        mock_repository.get_all.return_value = ([], 0)

        results = product_service.get_products_by_tag(uuid4())

        assert results == []


# =============================================================================
# DTO Mapping Tests
# =============================================================================


class TestDTOMapping:
    """Tests for DTO mapping."""

    def test_map_to_response_dto_complete(
        self, product_service, mock_repository
    ):
        """Test mapping a complete product to response DTO."""
        mock_product = create_mock_product(
            with_images=True,
            with_tags=True,
        )

        result = product_service._map_to_response_dto(mock_product)

        assert result.id == mock_product["id"]
        assert result.sku == mock_product["sku"]
        assert result.name == mock_product["name"]
        assert result.status == ProductStatus.ACTIVE
        assert len(result.images) == 2
        assert len(result.tags) == 2

    def test_map_to_response_dto_minimal(
        self, product_service, mock_repository
    ):
        """Test mapping a minimal product to response DTO."""
        mock_product = create_mock_product()

        result = product_service._map_to_response_dto(mock_product)

        assert result.id == mock_product["id"]
        assert result.images == []
        assert result.tags == []

    def test_map_to_response_dto_handles_none_values(
        self, product_service, mock_repository
    ):
        """Test mapping handles None values correctly."""
        mock_product = create_mock_product()
        mock_product["weight_kg"] = None
        mock_product["lead_time_days"] = None
        mock_product["dimensions"] = None

        result = product_service._map_to_response_dto(mock_product)

        assert result.weight_kg is None
        assert result.lead_time_days is None
        assert result.dimensions is None
