# Product Service for Biblia General Management

**ADW ID:** 0081e866
**Date:** 2026-01-31
**Specification:** specs/issue-3-adw-0081e866-sdlc_planner-product-service-biblia-general.md

## Overview

Implements the product service layer for managing the Biblia General (master product database) in the Kompass Portfolio & Quotation Automation System. This service provides business logic operations including auto-generated SKUs, full-text search, bulk import capabilities, and comprehensive image/tag management.

## What Was Built

- **ProductService class** with singleton pattern for product management operations
- **SKU auto-generation** using format `PRD-{YYYYMMDD}-{6_random_alphanum}`
- **Full-text search** across name, description, and SKU fields
- **Bulk create functionality** with validation and error reporting
- **Image management methods** (add, remove, set primary)
- **Tag management methods** (add, remove, get products by tag)
- **Advanced filtering** with has_images, MOQ range, and sorting support
- **New DTOs** for bulk operations (BulkCreateErrorDTO, BulkCreateResponseDTO)

## Technical Implementation

### Files Modified

- `apps/Server/app/services/product_service.py`: New service file with ProductService class (521 lines)
- `apps/Server/app/models/kompass_dto.py`: Added BulkCreateErrorDTO and BulkCreateResponseDTO, made SKU optional in ProductCreateDTO
- `apps/Server/app/repository/kompass_repository.py`: Extended ProductRepository with new filters and sorting
- `apps/Server/tests/test_product_service.py`: Comprehensive unit tests (907 lines)

### Key Changes

- **ProductService** wraps ProductRepository with business logic for SKU generation, DTO mapping, and bulk operations
- **SKU Generation**: Uses `secrets.token_hex(3).upper()` for 6-character random suffix with date prefix
- **Repository Extensions**:
  - Added `has_images` filter using EXISTS subquery on product_images table
  - Added `min_moq`/`max_moq` filters for minimum order quantity range
  - Added `sort_by` and `sort_order` parameters (name, unit_price, created_at, minimum_order_qty)
  - Extended search to include description field with ILIKE pattern matching
  - Added `set_primary_image()` method with transaction handling

## How to Use

### Creating a Product

```python
from app.services.product_service import product_service
from app.models.kompass_dto import ProductCreateDTO

# Without SKU (auto-generated)
request = ProductCreateDTO(
    name="Widget Pro",
    supplier_id=supplier_uuid,
    unit_price=Decimal("99.99")
)
product = product_service.create_product(request)
# product.sku will be like "PRD-20260131-A1B2C3"

# With custom SKU
request = ProductCreateDTO(
    sku="CUSTOM-001",
    name="Custom Widget",
    supplier_id=supplier_uuid,
    unit_price=Decimal("49.99")
)
product = product_service.create_product(request)
```

### Searching Products

```python
# Full-text search on name, description, and SKU
results = product_service.search_products("widget", limit=50)
```

### Listing with Filters

```python
from app.models.kompass_dto import ProductFilterDTO

filters = ProductFilterDTO(
    supplier_id=supplier_uuid,
    min_price=Decimal("10.00"),
    max_price=Decimal("100.00")
)

response = product_service.list_products(
    filters=filters,
    page=1,
    limit=20,
    has_images=True,
    min_moq=10,
    max_moq=100,
    sort_by="unit_price",
    sort_order="desc"
)
```

### Bulk Import

```python
products = [
    ProductCreateDTO(name="Product 1", supplier_id=uuid1, unit_price=Decimal("10.00")),
    ProductCreateDTO(name="Product 2", supplier_id=uuid2, unit_price=Decimal("20.00")),
]
result = product_service.bulk_create_products(products)
# result.successful: List[ProductResponseDTO]
# result.failed: List[BulkCreateErrorDTO]
# result.success_count, result.failure_count
```

### Image Management

```python
# Add image
image = product_service.add_product_image(
    product_id=product_uuid,
    image_url="https://example.com/image.jpg",
    is_primary=True
)

# Set primary image
product_service.set_primary_image(product_id, image_id)

# Remove image
product_service.remove_product_image(product_id, image_id)
```

### Tag Management

```python
# Add tag
product_service.add_tag_to_product(product_id, tag_id)

# Remove tag
product_service.remove_tag_from_product(product_id, tag_id)

# Get products by tag
products = product_service.get_products_by_tag(tag_id)
```

## Configuration

No additional configuration required. The service uses the existing database connection from `app.config.database`.

## Testing

Run the product service tests:

```bash
cd apps/Server
.venv/bin/pytest tests/test_product_service.py -v --tb=short
```

The test suite includes:
- SKU generation format validation
- CRUD operation tests (create, get, list, update, delete)
- Full-text search tests
- Bulk create with success and failure scenarios
- Image management tests
- Tag management tests
- Filter and pagination tests
- Sorting tests

## Notes

- The service follows the singleton pattern from auth_service.py
- SKU format `PRD-{YYYYMMDD}-{6char}` provides sortability by date and uniqueness
- Bulk create uses individual creates with try/except for partial success reporting
- Full-text search uses PostgreSQL ILIKE for simplicity
- The `unit_price` field in DTOs corresponds to `price_fob_usd` mentioned in the spec (FOB price in USD)
- MOQ is stored as `minimum_order_qty` in the database
- This service will be consumed by API routes in Phase 3 of the Kompass implementation
