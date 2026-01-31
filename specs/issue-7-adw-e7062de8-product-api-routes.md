# Feature: Product API Routes (Biblia General)

## Metadata
issue_number: `7`
adw_id: `e7062de8`
issue_json: `{"number":7,"title":"[Kompass] Phase 3B: Product API Routes (Biblia General)","body":"## Context\n**Project:** Kompass Portfolio & Quotation Automation System\n**Current Phase:** Phase 3 of 13 - API Routes Part 1\n**Current Issue:** KP-007 (Issue 7 of 33)\n**Parallel Execution:** YES - Runs IN PARALLEL with KP-006, KP-008, KP-009.\n\n---\n\n## Description\nImplement FastAPI routes for product management (Biblia General).\n\n## Requirements\n\n### File: apps/Server/app/api/product_routes.py\n\n#### Endpoints\n- GET    /api/products              - List products (paginated, filterable)\n- POST   /api/products              - Create product\n- GET    /api/products/{id}         - Get product with images and tags\n- PUT    /api/products/{id}         - Update product\n- DELETE /api/products/{id}         - Soft delete product\n- POST   /api/products/{id}/images  - Add image to product\n- DELETE /api/products/{id}/images/{image_id} - Remove image\n- PUT    /api/products/{id}/images/{image_id}/primary - Set primary image\n- POST   /api/products/{id}/tags/{tag_id} - Add tag\n- DELETE /api/products/{id}/tags/{tag_id} - Remove tag\n- GET    /api/products/search       - Full-text search\n\n#### Query Parameters (GET /api/products)\n- `supplier_id`: UUID\n- `category_id`: UUID\n- `status`: draft | active | discontinued\n- `price_min`: decimal\n- `price_max`: decimal\n- `moq_min`: int\n- `moq_max`: int\n- `tags`: comma-separated UUIDs\n- `has_images`: boolean\n- `page`, `limit`, `sort_by`, `sort_order`\n\n#### File Upload for Images\n- Accept multipart/form-data\n- Store in Supabase Storage\n- Generate thumbnail\n\n## Dependencies\n- Phase 2 (KP-003) must be complete\n\n## Acceptance Criteria\n- [ ] All endpoints functional\n- [ ] Image upload working\n- [ ] Tag management working\n- [ ] Complex filtering working\n- [ ] Full-text search returning relevant results"}`

## Feature Description
Implement FastAPI routes for product management (Biblia General) in the Kompass Portfolio & Quotation Automation System. This feature exposes the existing ProductService functionality through a RESTful API, enabling CRUD operations, image management, tag management, advanced filtering, and full-text search for products.

## User Story
As a system administrator or product manager
I want to manage products through a RESTful API
So that I can create, read, update, and delete products along with their images and tags programmatically

## Problem Statement
The ProductService and ProductRepository have been implemented in Phase 2 (KP-003), but there are no API routes to expose this functionality. Without API routes, the frontend cannot interact with the product data, and third-party integrations cannot access product information.

## Solution Statement
Create a FastAPI router (`product_routes.py`) that exposes all ProductService methods through RESTful endpoints. The routes will follow existing patterns from `auth_routes.py`, use JWT authentication via `get_current_user` dependency, and implement RBAC using `require_roles` for protected operations. The API will support advanced filtering through query parameters and handle image URLs (not file uploads in this phase - Supabase Storage integration is a future enhancement).

## Relevant Files
Use these files to implement the feature:

- `apps/Server/app/services/product_service.py` - Contains the ProductService singleton with all business logic methods that the routes will call
- `apps/Server/app/models/kompass_dto.py` - Contains all DTOs (ProductCreateDTO, ProductUpdateDTO, ProductResponseDTO, ProductFilterDTO, ProductListResponseDTO, ProductImageCreateDTO, etc.)
- `apps/Server/app/api/auth_routes.py` - Reference for route structure, error handling, and logging patterns
- `apps/Server/app/api/dependencies.py` - Contains `get_current_user` dependency for authentication
- `apps/Server/app/api/rbac_dependencies.py` - Contains `require_roles` dependency for role-based access control
- `apps/Server/main.py` - Where the new router needs to be registered
- `apps/Server/tests/test_product_service.py` - Reference for testing patterns and mock fixtures
- `app_docs/feature-0081e866-product-service-biblia-general.md` - Documentation for ProductService methods

### New Files
- `apps/Server/app/api/product_routes.py` - New file containing all product API routes
- `apps/Server/tests/test_product_routes.py` - Unit tests for the product routes

## Implementation Plan
### Phase 1: Foundation
1. Create the `product_routes.py` file with basic router setup
2. Import required dependencies (ProductService, DTOs, auth dependencies)
3. Implement the router with the `/products` prefix and appropriate tags

### Phase 2: Core Implementation
1. Implement CRUD endpoints:
   - `GET /products` - List products with filtering and pagination
   - `POST /products` - Create a new product
   - `GET /products/{id}` - Get a single product by ID
   - `PUT /products/{id}` - Update a product
   - `DELETE /products/{id}` - Soft delete a product
2. Implement image management endpoints:
   - `POST /products/{id}/images` - Add image to product
   - `DELETE /products/{id}/images/{image_id}` - Remove image
   - `PUT /products/{id}/images/{image_id}/primary` - Set primary image
3. Implement tag management endpoints:
   - `POST /products/{id}/tags/{tag_id}` - Add tag to product
   - `DELETE /products/{id}/tags/{tag_id}` - Remove tag from product
4. Implement search endpoint:
   - `GET /products/search` - Full-text search

### Phase 3: Integration
1. Register the router in `main.py`
2. Write comprehensive unit tests
3. Validate all endpoints work correctly

## Step by Step Tasks

### Step 1: Create Product Routes File
- Create `apps/Server/app/api/product_routes.py`
- Import dependencies: FastAPI (APIRouter, HTTPException, Depends, Query), UUID, List, Optional, Decimal
- Import `product_service` singleton from `app.services.product_service`
- Import DTOs from `app.models.kompass_dto`
- Import `get_current_user` from `app.api.dependencies`
- Import `require_roles` from `app.api.rbac_dependencies`
- Create router with `tags=["Products"]`

### Step 2: Implement GET /products (List Products)
- Define endpoint with pagination query params: `page` (default 1), `limit` (default 20)
- Add filter query params: `supplier_id`, `category_id`, `status`, `price_min`, `price_max`, `moq_min`, `moq_max`, `tags` (comma-separated UUIDs), `has_images`
- Add sorting params: `sort_by`, `sort_order`
- Require authentication via `get_current_user`
- Parse `tags` string into list of UUIDs
- Build `ProductFilterDTO` from query params
- Call `product_service.list_products()`
- Return `ProductListResponseDTO`

### Step 3: Implement POST /products (Create Product)
- Define endpoint accepting `ProductCreateDTO` body
- Require authentication and role check: `require_roles(['admin', 'manager'])`
- Call `product_service.create_product()`
- Return 201 status with `ProductResponseDTO`
- Raise 400 on failure

### Step 4: Implement GET /products/search (Search Products)
- Define endpoint with `q` query param (search query) and `limit` param (default 50)
- Require authentication
- Call `product_service.search_products()`
- Return list of `ProductResponseDTO`
- Note: This must be defined BEFORE `/products/{id}` to avoid route conflict

### Step 5: Implement GET /products/{id} (Get Single Product)
- Define endpoint with `product_id` path parameter (UUID)
- Require authentication
- Call `product_service.get_product()`
- Return `ProductResponseDTO`
- Raise 404 if not found

### Step 6: Implement PUT /products/{id} (Update Product)
- Define endpoint with `product_id` path parameter and `ProductUpdateDTO` body
- Require authentication and role check: `require_roles(['admin', 'manager'])`
- Call `product_service.update_product()`
- Return `ProductResponseDTO`
- Raise 404 if not found

### Step 7: Implement DELETE /products/{id} (Delete Product)
- Define endpoint with `product_id` path parameter
- Require authentication and role check: `require_roles(['admin', 'manager'])`
- Call `product_service.delete_product()`
- Return 204 No Content on success
- Raise 404 if not found

### Step 8: Implement POST /products/{id}/images (Add Image)
- Define endpoint with `product_id` path parameter
- Accept `ProductImageCreateDTO` body (url, alt_text, sort_order, is_primary)
- Require authentication and role check: `require_roles(['admin', 'manager'])`
- Verify product exists first
- Call `product_service.add_product_image()`
- Return 201 with `ProductImageResponseDTO`
- Raise 404 if product not found, 400 on failure

### Step 9: Implement DELETE /products/{id}/images/{image_id} (Remove Image)
- Define endpoint with `product_id` and `image_id` path parameters
- Require authentication and role check: `require_roles(['admin', 'manager'])`
- Call `product_service.remove_product_image()`
- Return 204 No Content on success
- Raise 404 if not found

### Step 10: Implement PUT /products/{id}/images/{image_id}/primary (Set Primary Image)
- Define endpoint with `product_id` and `image_id` path parameters
- Require authentication and role check: `require_roles(['admin', 'manager'])`
- Call `product_service.set_primary_image()`
- Return 200 with success message
- Raise 404 if not found or failed

### Step 11: Implement POST /products/{id}/tags/{tag_id} (Add Tag)
- Define endpoint with `product_id` and `tag_id` path parameters
- Require authentication and role check: `require_roles(['admin', 'manager'])`
- Call `product_service.add_tag_to_product()`
- Return 201 with success message
- Raise 400 if failed (may already exist)

### Step 12: Implement DELETE /products/{id}/tags/{tag_id} (Remove Tag)
- Define endpoint with `product_id` and `tag_id` path parameters
- Require authentication and role check: `require_roles(['admin', 'manager'])`
- Call `product_service.remove_tag_from_product()`
- Return 204 No Content on success
- Raise 404 if not found

### Step 13: Register Router in main.py
- Import `router as products_router` from `app.api.product_routes`
- Add `app.include_router(products_router, prefix="/api/products")` in `create_app()`

### Step 14: Create Unit Tests for Product Routes
- Create `apps/Server/tests/test_product_routes.py`
- Use pytest and FastAPI TestClient
- Mock the `product_service` singleton
- Test all endpoints:
  - Test list products with various filters
  - Test create product (success and failure)
  - Test get product (found and not found)
  - Test update product (success and not found)
  - Test delete product (success and not found)
  - Test search products
  - Test image management endpoints
  - Test tag management endpoints
- Test authentication (401 without token)
- Test authorization (403 without proper role)

### Step 15: Run Validation Commands
- Run all tests and validation commands to ensure feature works with zero regressions

## Testing Strategy
### Unit Tests
- Test each endpoint with valid inputs returns expected response
- Test authentication enforcement (401 without token)
- Test role-based access control (403 for viewer role on write endpoints)
- Test 404 responses for non-existent resources
- Test 400 responses for invalid inputs
- Test query parameter parsing (tags comma-separated, status enum)
- Test pagination and sorting parameters

### Edge Cases
- Empty tags parameter vs no tags parameter
- Invalid UUID format in path/query parameters
- Decimal precision for price filters
- Large page numbers with small result sets
- Search with empty or whitespace-only query
- Setting primary image when one already exists
- Adding duplicate tag to product
- Deleting non-existent image/tag

## Acceptance Criteria
- [ ] All 11 endpoints are implemented and functional
- [ ] Authentication is required for all endpoints
- [ ] Write operations (POST, PUT, DELETE) require admin or manager role
- [ ] List endpoint supports all specified query parameters
- [ ] Search endpoint returns relevant results via full-text search
- [ ] Image management (add, remove, set primary) works correctly
- [ ] Tag management (add, remove) works correctly
- [ ] Proper HTTP status codes returned (200, 201, 204, 400, 401, 403, 404)
- [ ] Logging follows established pattern: `print(f"INFO [ProductRoutes]: ...")`
- [ ] All unit tests pass
- [ ] Router registered in main.py
- [ ] API documentation available at /docs

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Run Server tests
cd apps/Server && .venv/bin/pytest tests/ -v --tb=short

# Run ruff linting
cd apps/Server && .venv/bin/ruff check .

# Run Client type check (no changes expected, but verify no regressions)
cd apps/Client && npm run typecheck

# Run Client build
cd apps/Client && npm run build
```

## Notes
- **Image Storage**: This implementation handles image URLs only. The issue mentions Supabase Storage and thumbnail generation, but the existing ProductService already works with URLs. Supabase Storage file upload integration can be added as a future enhancement.
- **Soft Delete**: The delete endpoint performs a soft delete by setting status to inactive, following the existing service behavior.
- **Route Order**: The `/products/search` endpoint must be defined BEFORE `/products/{id}` to avoid FastAPI treating "search" as a product ID.
- **Tags Parsing**: The tags query parameter accepts comma-separated UUIDs and needs to be parsed into a list.
- **Status Enum**: The status query parameter maps to ProductStatus enum (draft, active, inactive, discontinued).
- **Parallel Execution**: This issue runs in parallel with KP-006, KP-008, KP-009, so no dependencies on other API routes.
