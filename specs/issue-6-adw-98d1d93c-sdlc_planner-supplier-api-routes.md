# Feature: Supplier API Routes

## Metadata
issue_number: `6`
adw_id: `98d1d93c`
issue_json: `{"number":6,"title":"[Kompass] Phase 3A: Supplier API Routes","body":"...Phase 3 of 13 - API Routes Part 1..."}`

## Feature Description
Implement FastAPI routes for supplier management in the Kompass Portfolio & Quotation Automation System. This feature creates a complete REST API layer for suppliers, including CRUD operations, pagination, filtering, search, and related product listing. The API routes connect to the existing supplier service layer and expose all supplier functionality through authenticated endpoints with proper RBAC controls.

## User Story
As an authenticated user of the Kompass system
I want to manage suppliers through a REST API
So that I can create, read, update, delete, search, and filter supplier records, as well as view products associated with each supplier

## Problem Statement
The backend currently has a complete supplier service layer (supplier_service.py) with business logic for supplier CRUD operations, but there are no HTTP endpoints exposing this functionality to clients. API consumers need a way to interact with supplier data through standard REST conventions with proper authentication, authorization, pagination, and error handling.

## Solution Statement
Create a new `supplier_routes.py` file implementing all required FastAPI endpoints that delegate to the existing supplier_service. The routes will follow established patterns from auth_routes.py for consistency, implement full RBAC using existing dependencies, support rich query parameters for filtering/sorting/pagination, and integrate seamlessly with the existing application through router registration in main.py.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/main.py` - Main application entry point where the supplier router must be registered
- `apps/Server/app/api/auth_routes.py` - Reference implementation for route patterns, error handling, and response models
- `apps/Server/app/api/dependencies.py` - Authentication dependency (`get_current_user`) to protect endpoints
- `apps/Server/app/api/rbac_dependencies.py` - RBAC dependency (`require_roles`) for admin/manager-only endpoints
- `apps/Server/app/services/supplier_service.py` - Business logic layer with all supplier operations (singleton: `supplier_service`)
- `apps/Server/app/services/product_service.py` - Product service for listing products by supplier (singleton: `product_service`)
- `apps/Server/app/models/kompass_dto.py` - Pydantic DTOs for request/response models (SupplierCreateDTO, SupplierUpdateDTO, SupplierResponseDTO, SupplierListResponseDTO, PaginationDTO, ProductListResponseDTO)
- `apps/Server/tests/services/test_supplier_service.py` - Reference for test patterns and fixtures
- `app_docs/feature-02b42491-supplier-service-crud.md` - Documentation for supplier service patterns
- `app_docs/feature-9ce5e2ee-database-schema-core-dtos.md` - Documentation for Kompass database schema and DTOs

### New Files
- `apps/Server/app/api/supplier_routes.py` - New file: FastAPI router with all supplier endpoints
- `apps/Server/tests/api/__init__.py` - New file: Package init for API tests
- `apps/Server/tests/api/test_supplier_routes.py` - New file: Unit tests for supplier API routes

## Implementation Plan
### Phase 1: Foundation
1. Create the supplier_routes.py file with router setup and imports
2. Implement basic CRUD endpoints (GET, POST, PUT, DELETE for single suppliers)
3. Register the router in main.py

### Phase 2: Core Implementation
1. Implement list endpoint with full query parameter support (pagination, filtering, sorting)
2. Implement search endpoint
3. Implement products-by-supplier endpoint
4. Add comprehensive error handling and logging

### Phase 3: Integration
1. Create test directory structure for API tests
2. Write unit tests for all endpoints
3. Validate OpenAPI documentation generation
4. Run full validation suite

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create Supplier Routes File with Router Setup
- Create `apps/Server/app/api/supplier_routes.py`
- Add module docstring explaining the purpose
- Import required dependencies:
  - `from uuid import UUID`
  - `from typing import Optional, List`
  - `from fastapi import APIRouter, HTTPException, Depends, Query`
  - Authentication dependencies from `.dependencies`
  - RBAC dependencies from `.rbac_dependencies`
  - DTOs from `app.models.kompass_dto`
  - Services from `app.services.supplier_service` and `app.services.product_service`
- Create router: `router = APIRouter(tags=["Suppliers"])`

### Step 2: Implement GET /suppliers (List with Pagination/Filtering)
- Create async endpoint `list_suppliers()`
- Add Query parameters:
  - `status: Optional[str] = Query(None, description="Filter by status: active | inactive | pending_review")`
  - `country: Optional[str] = Query(None, description="Filter by country")`
  - `has_products: Optional[bool] = Query(None, description="Filter by whether supplier has products")`
  - `page: int = Query(1, ge=1, description="Page number")`
  - `limit: int = Query(20, ge=1, le=100, description="Items per page")`
  - `sort_by: str = Query("name", description="Sort by: name | created_at")`
  - `sort_order: str = Query("asc", description="Sort order: asc | desc")`
- Add authentication dependency: `current_user: dict = Depends(get_current_user)`
- Convert status string to SupplierStatus enum if provided
- Call `supplier_service.list_suppliers()` with parameters
- Return `SupplierListResponseDTO` with response_model annotation
- Add logging: `print(f"INFO [SupplierRoutes]: Listing suppliers, page {page}")`

### Step 3: Implement POST /suppliers (Create)
- Create async endpoint `create_supplier()`
- Accept `request: SupplierCreateDTO` body parameter
- Add authentication dependency
- Call `supplier_service.create_supplier(request)`
- Handle `ValueError` exceptions by raising `HTTPException(status_code=400, detail=str(e))`
- Return created supplier with `status_code=201`
- Add response_model annotation: `SupplierResponseDTO`
- Add logging for success and failure cases

### Step 4: Implement GET /suppliers/search
- Create async endpoint `search_suppliers()`
- Note: This route must be defined BEFORE the `/{supplier_id}` route to avoid path conflicts
- Add Query parameter: `query: str = Query(..., min_length=2, description="Search query")`
- Add authentication dependency
- Call `supplier_service.search_suppliers(query)`
- Return `List[SupplierResponseDTO]`
- Handle empty results gracefully

### Step 5: Implement GET /suppliers/{supplier_id} (Get Detail with Product Count)
- Create async endpoint `get_supplier(supplier_id: UUID)`
- Add authentication dependency
- Call `supplier_service.get_supplier_with_product_count(supplier_id)`
- If result is None, raise `HTTPException(status_code=404, detail="Supplier not found")`
- Return supplier dict with product_count included
- Add logging for found/not found cases

### Step 6: Implement PUT /suppliers/{supplier_id} (Update)
- Create async endpoint `update_supplier(supplier_id: UUID, request: SupplierUpdateDTO)`
- Add authentication dependency
- Call `supplier_service.update_supplier(supplier_id, request)`
- Handle `ValueError` exceptions by raising `HTTPException(status_code=400, detail=str(e))`
- If result is None, raise `HTTPException(status_code=404, detail="Supplier not found")`
- Return updated `SupplierResponseDTO`
- Add logging for success cases

### Step 7: Implement DELETE /suppliers/{supplier_id} (Soft Delete)
- Create async endpoint `delete_supplier(supplier_id: UUID)`
- Add RBAC dependency: `current_user: dict = Depends(require_roles(['admin', 'manager']))`
- Call `supplier_service.delete_supplier(supplier_id)`
- Handle `ValueError` exceptions (e.g., "Cannot delete supplier with active products") by raising `HTTPException(status_code=400, detail=str(e))`
- If result is False, raise `HTTPException(status_code=404, detail="Supplier not found")`
- Return `{"message": "Supplier deleted successfully"}` with `status_code=200`
- Add logging for success/failure/blocked cases

### Step 8: Implement GET /suppliers/{supplier_id}/products
- Create async endpoint `get_supplier_products(supplier_id: UUID)`
- Add Query parameters for pagination:
  - `page: int = Query(1, ge=1)`
  - `limit: int = Query(20, ge=1, le=100)`
- Add authentication dependency
- First verify supplier exists using `supplier_service.get_supplier(supplier_id)`
- If supplier not found, raise `HTTPException(status_code=404, detail="Supplier not found")`
- Use `product_service.list_products()` with `filters=ProductFilterDTO(supplier_id=supplier_id)`
- Return `ProductListResponseDTO`
- Add logging

### Step 9: Register Router in main.py
- Edit `apps/Server/main.py`
- Add import: `from app.api.supplier_routes import router as supplier_router`
- Add router registration in `create_app()`:
  - `app.include_router(supplier_router, prefix="/api/suppliers", tags=["Suppliers"])`
- Place after auth_router registration

### Step 10: Create Test Directory Structure
- Create `apps/Server/tests/api/__init__.py` (empty file or package docstring)

### Step 11: Create Unit Tests for Supplier Routes
- Create `apps/Server/tests/api/test_supplier_routes.py`
- Add imports for pytest, unittest.mock, FastAPI TestClient
- Create fixtures:
  - `sample_supplier_data` fixture (similar to test_supplier_service.py)
  - `mock_supplier_service` fixture
  - `mock_product_service` fixture
  - `client` fixture using FastAPI TestClient
- Write test classes:
  - `TestListSuppliers`: test pagination, filtering, authentication
  - `TestCreateSupplier`: test success, validation errors, authentication
  - `TestGetSupplier`: test found, not found, authentication
  - `TestUpdateSupplier`: test success, not found, validation errors
  - `TestDeleteSupplier`: test success, not found, active products, RBAC enforcement
  - `TestSearchSuppliers`: test results, empty results, short query
  - `TestGetSupplierProducts`: test success, supplier not found

### Step 12: Run Validation Commands
- Execute the validation commands listed below to ensure the feature works correctly with zero regressions

## Testing Strategy
### Unit Tests
- Test each endpoint with mocked service dependencies
- Test authentication enforcement (401 for unauthenticated requests)
- Test RBAC enforcement (403 for unauthorized roles on DELETE)
- Test input validation (400 for invalid data)
- Test not found scenarios (404 responses)
- Test successful operations with correct response codes and shapes

### Edge Cases
- Empty search query (should return empty list gracefully)
- Search query with only whitespace
- Pagination with page > total pages (should return empty items)
- Deleting supplier with active products (should return 400)
- Updating non-existent supplier (should return 404)
- Invalid UUID format in path parameters
- Status filter with invalid value
- Limit exceeding max (100)

## Acceptance Criteria
- [ ] GET /api/suppliers returns paginated list with filtering support
- [ ] POST /api/suppliers creates supplier and returns 201
- [ ] GET /api/suppliers/search returns matching suppliers
- [ ] GET /api/suppliers/{id} returns supplier with product_count
- [ ] PUT /api/suppliers/{id} updates supplier
- [ ] DELETE /api/suppliers/{id} soft deletes supplier (admin/manager only)
- [ ] GET /api/suppliers/{id}/products returns paginated products
- [ ] All endpoints require authentication (401 without token)
- [ ] DELETE requires admin or manager role (403 for other roles)
- [ ] OpenAPI docs at /docs show all endpoints with schemas
- [ ] All tests pass
- [ ] Ruff linting passes
- [ ] TypeScript client build passes (no breaking changes)

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/98d1d93c/apps/Server && source .venv/bin/activate && .venv/bin/ruff check app/api/supplier_routes.py` - Lint the new routes file
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/98d1d93c/apps/Server && source .venv/bin/activate && .venv/bin/pytest tests/ -v --tb=short` - Run all Server tests
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/98d1d93c/apps/Server && source .venv/bin/activate && .venv/bin/ruff check .` - Full linting check
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/98d1d93c/apps/Client && npm run typecheck` - Run Client type check
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/98d1d93c/apps/Client && npm run build` - Run Client build

## Notes
- The supplier_service singleton is already available at `app.services.supplier_service.supplier_service`
- The product_service singleton is already available at `app.services.product_service.product_service`
- The SupplierStatus enum supports: `active`, `inactive`, `pending_review`
- The delete operation is a soft delete (sets status to inactive via the service)
- The service already handles validation for:
  - Email format validation
  - WeChat ID normalization (stored in contact_phone field)
  - Blocking deletion of suppliers with active products
- Follow existing logging convention: `print(f"INFO/WARN/ERROR [SupplierRoutes]: message")`
- The `/search` route must be defined before `/{supplier_id}` to avoid FastAPI treating "search" as a UUID
- The `get_supplier_with_product_count` method returns a dict, not a DTO, which includes the product_count field
