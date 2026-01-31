# Feature: Product Service for Biblia General Management

## Metadata
issue_number: `3`
adw_id: `0081e866`
issue_json: `{"number":3,"title":"[Kompass] Phase 2B: Product Service - Biblia General Management","body":"..."}`

## Feature Description
Implement the product service layer for managing the Biblia General (master product database) in the Kompass Portfolio & Quotation Automation System. This service provides business logic operations on top of the existing ProductRepository, including auto-generated SKUs, full-text search, bulk import capabilities, and comprehensive image/tag management. The service will be consumed by API routes in Phase 3.

This is Phase 2B (Issue 3 of 33) and runs in parallel with KP-002 (Supplier Service), KP-004 (Portfolio Service), and KP-005 (Client Service).

## User Story
As a product manager
I want to have a comprehensive product service for managing the Biblia General
So that I can efficiently create, search, filter, and manage products including their images and tags for use in portfolios and quotations

## Problem Statement
The application needs a service layer for product management that:
- Provides auto-generated SKU when not provided during product creation
- Supports full-text search across name, description, and SKU fields
- Enables bulk import of products for efficient data loading
- Manages product images with primary image designation
- Handles product tagging for flexible categorization
- Supports advanced filtering by supplier, category, status, price range, MOQ, tags, and image presence

The existing ProductRepository handles data access but lacks business logic for SKU generation, search, bulk operations, and proper response DTO mapping.

## Solution Statement
Implement a ProductService class in `apps/Server/app/services/product_service.py` that:
1. Wraps the ProductRepository with business logic
2. Auto-generates SKU using a pattern like `PRD-{timestamp}-{random}` when not provided
3. Implements full-text search with PostgreSQL ILIKE on name, description, and SKU
4. Provides bulk create with validation and error reporting
5. Manages product images with primary image logic
6. Handles tag management operations
7. Supports comprehensive filtering with has_images and MOQ range filters
8. Returns properly typed DTOs for all operations

## Relevant Files
Use these files to implement the feature:

- `apps/Server/app/repository/kompass_repository.py` - Contains `ProductRepository` class with CRUD operations, image/tag management methods that the service will consume. Key methods: `create()`, `get_by_id()`, `get_all()`, `update()`, `delete()`, `add_tag()`, `remove_tag()`, `add_image()`, `remove_image()`.
- `apps/Server/app/models/kompass_dto.py` - Contains all DTOs including `ProductCreateDTO`, `ProductUpdateDTO`, `ProductResponseDTO`, `ProductListResponseDTO`, `ProductFilterDTO`, `ProductImageResponseDTO`, `TagResponseDTO`, `PaginationDTO`, and `ProductStatus` enum. These are the request/response types the service will use.
- `apps/Server/app/services/auth_service.py` - Reference for service class pattern with singleton instance at module level.
- `apps/Server/app/config/database.py` - Database connection utilities (already used by repository, but service may need for bulk operations).
- `apps/Server/database/schema.sql` - Database schema showing products, product_images, product_tags tables with their columns and constraints.

### New Files
- `apps/Server/app/services/product_service.py` - The main product service implementation
- `apps/Server/tests/test_product_service.py` - Unit tests for the product service

## Implementation Plan

### Phase 1: Foundation
1. Create the ProductService class structure following the singleton pattern from auth_service.py
2. Implement basic CRUD methods that wrap ProductRepository and return proper DTOs
3. Add SKU auto-generation logic for product creation

### Phase 2: Core Implementation
1. Implement full-text search method using PostgreSQL ILIKE patterns
2. Add bulk create functionality with validation and error handling
3. Implement advanced filtering including has_images and MOQ range
4. Add sorting support for name, price_fob_usd, created_at, moq

### Phase 3: Integration
1. Implement image management methods (add, remove, set_primary)
2. Implement tag management methods (add, remove, get_products_by_tag)
3. Add comprehensive unit tests
4. Ensure proper error handling and logging throughout

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create ProductService Class Structure
Create `apps/Server/app/services/product_service.py`:
- Import required dependencies (UUID, List, Optional, Decimal, datetime)
- Import repository: `from app.repository.kompass_repository import ProductRepository, TagRepository, product_repository, tag_repository`
- Import DTOs: `ProductCreateDTO`, `ProductUpdateDTO`, `ProductResponseDTO`, `ProductListResponseDTO`, `ProductFilterDTO`, `ProductImageResponseDTO`, `PaginationDTO`, `ProductStatus`
- Create `ProductService` class with repository injected in constructor
- Create singleton instance `product_service = ProductService()`

### Step 2: Implement SKU Generation
Add private method `_generate_sku()`:
- Generate unique SKU format: `PRD-{YYYYMMDD}-{6_random_alphanum}`
- Use `datetime.now().strftime("%Y%m%d")` for date portion
- Use `secrets.token_hex(3).upper()` for random portion
- Return the generated SKU string

### Step 3: Implement Create Product Method
Add `create_product(request: ProductCreateDTO) -> ProductResponseDTO`:
- If SKU not provided in request, call `_generate_sku()`
- Call `product_repository.create()` with all fields from request
- Handle images from request if provided (iterate and call `add_image`)
- Handle tags from request if provided (iterate and call `add_tag`)
- Map result to `ProductResponseDTO`
- Return the response or raise appropriate exception on failure

### Step 4: Implement Get Product Method
Add `get_product(product_id: UUID) -> ProductResponseDTO`:
- Call `product_repository.get_by_id(product_id)`
- Return None or raise 404 if not found
- Map repository result to `ProductResponseDTO` including images and tags
- Return the response

### Step 5: Implement List Products Method
Add `list_products(filters: ProductFilterDTO, page: int, limit: int) -> ProductListResponseDTO`:
- Extract filter parameters from ProductFilterDTO
- Add support for new filters:
  - `has_images`: Boolean filter - products with at least one image
  - `min_moq` / `max_moq`: Integer range filter on minimum_order_qty
- Call `product_repository.get_all()` with all filter parameters
- Calculate pagination metadata (total, pages)
- Map results to list of `ProductResponseDTO`
- Return `ProductListResponseDTO` with items, pagination, and applied filters

### Step 6: Implement Update Product Method
Add `update_product(product_id: UUID, request: ProductUpdateDTO) -> ProductResponseDTO`:
- Call `product_repository.update()` with only non-None fields from request
- Map result to `ProductResponseDTO`
- Return the response or raise 404 if not found

### Step 7: Implement Delete Product Method (Soft Delete)
Add `delete_product(product_id: UUID) -> bool`:
- Call `product_repository.delete(product_id)` which sets status to 'inactive'
- Return True if deleted, False otherwise

### Step 8: Implement Full-Text Search Method
Add `search_products(query: str) -> List[ProductResponseDTO]`:
- Build SQL ILIKE pattern for searching
- Search across: name, description, sku fields
- Call repository with search parameter (use existing `search` filter in get_all)
- Limit results to reasonable maximum (e.g., 50)
- Map results to list of `ProductResponseDTO`
- Return the list

### Step 9: Implement Bulk Create Method
Add `bulk_create_products(products: List[ProductCreateDTO]) -> BulkCreateResponse`:
- Define `BulkCreateResponse` DTO with: `successful: List[ProductResponseDTO]`, `failed: List[BulkCreateError]`, `total_count: int`, `success_count: int`, `failure_count: int`
- Define `BulkCreateError` DTO with: `index: int`, `sku: Optional[str]`, `error: str`
- Iterate through products list
- For each product, try `create_product()` in try/except
- Track successful and failed creations
- Return comprehensive response with all results

### Step 10: Implement Image Management Methods
Add three image methods:
- `add_product_image(product_id: UUID, image_url: str, is_primary: bool) -> ProductImageResponseDTO`:
  - Call `product_repository.add_image()`
  - Map result to `ProductImageResponseDTO`
- `remove_product_image(product_id: UUID, image_id: UUID) -> bool`:
  - Call `product_repository.remove_image(image_id)`
  - Return success boolean
- `set_primary_image(product_id: UUID, image_id: UUID) -> bool`:
  - Need to add repository method or use raw SQL to:
    1. Set all images for product to is_primary=False
    2. Set specified image to is_primary=True
  - Return success boolean

### Step 11: Implement Tag Management Methods
Add three tag methods:
- `add_tag_to_product(product_id: UUID, tag_id: UUID) -> bool`:
  - Call `product_repository.add_tag(product_id, tag_id)`
  - Return success boolean
- `remove_tag_from_product(product_id: UUID, tag_id: UUID) -> bool`:
  - Call `product_repository.remove_tag(product_id, tag_id)`
  - Return success boolean
- `get_products_by_tag(tag_id: UUID) -> List[ProductResponseDTO]`:
  - Call `product_repository.get_all()` with `tag_ids=[tag_id]`
  - Map results to list of `ProductResponseDTO`
  - Return the list

### Step 12: Add Sorting Support to List Products
Extend `list_products()` to support sorting:
- Add `sort_by` parameter: Optional enum of 'name', 'price_fob_usd', 'created_at', 'moq'
- Add `sort_order` parameter: 'asc' or 'desc'
- Pass sorting to repository (may need to extend repository get_all method)

### Step 13: Add BulkCreateResponse DTO to kompass_dto.py
Add to `apps/Server/app/models/kompass_dto.py`:
```python
class BulkCreateErrorDTO(BaseModel):
    """Error details for a failed bulk create item."""
    index: int
    sku: Optional[str] = None
    error: str

class BulkCreateResponseDTO(BaseModel):
    """Response for bulk create operations."""
    successful: List[ProductResponseDTO] = []
    failed: List[BulkCreateErrorDTO] = []
    total_count: int = 0
    success_count: int = 0
    failure_count: int = 0
```

### Step 14: Extend ProductRepository for Has Images Filter
Add to `apps/Server/app/repository/kompass_repository.py` in `ProductRepository.get_all()`:
- Add `has_images: Optional[bool] = None` parameter
- Add condition: if has_images is True, add subquery to check product_images exists
- Add `min_moq: Optional[int] = None` and `max_moq: Optional[int] = None` parameters
- Add conditions for MOQ range filtering

### Step 15: Extend ProductRepository for Set Primary Image
Add `set_primary_image(product_id: UUID, image_id: UUID) -> bool` to `ProductRepository`:
- Start transaction
- Set all images for product to is_primary=False
- Set specified image to is_primary=True
- Commit and return True, or rollback and return False on error

### Step 16: Extend ProductRepository for Sorting
Add sorting parameters to `ProductRepository.get_all()`:
- Add `sort_by: Optional[str] = None` parameter (allowed: name, unit_price, created_at, minimum_order_qty)
- Add `sort_order: str = 'asc'` parameter
- Modify ORDER BY clause based on parameters

### Step 17: Create Unit Tests
Create `apps/Server/tests/test_product_service.py`:
- Test `_generate_sku()` returns valid format
- Test `create_product()` with and without SKU
- Test `get_product()` returns correct DTO
- Test `list_products()` with various filters
- Test `update_product()` updates correctly
- Test `delete_product()` soft deletes
- Test `search_products()` returns relevant results
- Test `bulk_create_products()` handles success and failure
- Test image management methods
- Test tag management methods
- Use mocking for repository to isolate service logic

### Step 18: Run Validation Commands
Execute all validation commands to ensure the implementation is correct and has zero regressions.

## Testing Strategy
### Unit Tests
- Mock ProductRepository and TagRepository
- Test each service method in isolation
- Verify correct repository method calls
- Verify correct DTO mapping
- Test edge cases (empty lists, not found, validation errors)
- Test SKU generation uniqueness
- Test bulk create error handling

### Edge Cases
- Create product without SKU (auto-generate)
- Create product with duplicate SKU (should fail)
- Search with empty query
- Bulk create with mix of valid and invalid products
- Filter products with no matches
- Set primary image for non-existent product
- Add tag that doesn't exist
- Get products by tag with no products

## Acceptance Criteria
- [ ] All CRUD operations working (create, get, list, update, delete)
- [ ] SKU auto-generation functioning when not provided
- [ ] Image management functional (add, remove, set_primary)
- [ ] Tag management functional (add, remove, get_by_tag)
- [ ] Full-text search returning relevant results on name, description, SKU
- [ ] Bulk import working with validation and error reporting
- [ ] Filtering by supplier_id, category_id, status, price_range, moq_range, tags[], has_images
- [ ] Sorting by name, price_fob_usd, created_at, moq
- [ ] Unit tests passing with good coverage
- [ ] No regressions in existing functionality

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && .venv/bin/ruff check .` - Run Python linter to check code quality
- `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` - Run all Server tests including new product service tests
- `cd apps/Client && npm run typecheck` - Run Client type check (no frontend changes but verify no breaks)
- `cd apps/Client && npm run build` - Run Client build (no frontend changes but verify no breaks)

## Notes
- The ProductRepository already exists with basic CRUD, image, and tag methods - this service layer adds business logic on top
- SKU format `PRD-{YYYYMMDD}-{6char}` provides sortability by date and uniqueness
- Bulk create uses individual creates wrapped in try/except for partial success reporting
- The service follows the same singleton pattern as auth_service.py
- Price field in DTOs is `unit_price` but the issue refers to `price_fob_usd` - they are the same (FOB price in USD is the unit_price)
- MOQ is stored as `minimum_order_qty` in the database
- Full-text search uses PostgreSQL ILIKE for simplicity - could be upgraded to tsvector/tsquery in future
- This service runs in parallel with supplier_service, portfolio_service, and client_service development
