# Feature: Category and Tag API Routes

## Metadata
issue_number: `8`
adw_id: `c58228ec`
issue_json: `{"number":8,"title":"[Kompass] Phase 3C: Category and Tag API Routes","body":"Implement FastAPI routes for categories and tags."}`

## Feature Description
Implement FastAPI REST API routes for managing hierarchical product categories and flexible tags in the Kompass Portfolio & Quotation System. This includes CRUD endpoints for both entities, specialized tree operations for categories (list as tree, move to new parent), and tag search functionality for autocomplete. These routes will consume the existing CategoryService and TagService from Phase 2.

## User Story
As an API consumer (frontend application or integration)
I want to access REST endpoints for managing categories and tags
So that I can organize products into hierarchies and apply flexible tagging for filtering

## Problem Statement
The Kompass system has complete service and repository layers for categories and tags (implemented in Phase 2), but these are not exposed via HTTP endpoints. Without API routes, the frontend cannot interact with categories and tags, blocking the product management UI functionality.

## Solution Statement
Create two FastAPI route modules (`category_routes.py` and `tag_routes.py`) that:
1. Expose CRUD operations via standard REST endpoints
2. Apply JWT authentication to all endpoints
3. Apply role-based access control (admin/manager) for write operations
4. Return proper HTTP status codes and error messages
5. Follow existing route patterns established in `auth_routes.py`

## Relevant Files
Use these files to implement the feature:

- `apps/Server/main.py` - Register the new routers with FastAPI app
- `apps/Server/app/api/auth_routes.py` - Reference pattern for route implementation
- `apps/Server/app/api/dependencies.py` - Import `get_current_user` for authentication
- `apps/Server/app/api/rbac_dependencies.py` - Import `require_roles` for authorization
- `apps/Server/app/services/category_service.py` - Existing category service with all business logic
- `apps/Server/app/services/tag_service.py` - Existing tag service with all business logic
- `apps/Server/app/models/kompass_dto.py` - All DTOs for categories and tags already defined
- `apps/Server/tests/services/test_category_service.py` - Reference pattern for testing
- `apps/Server/tests/services/test_tag_service.py` - Reference pattern for testing

### New Files
- `apps/Server/app/api/category_routes.py` - Category API routes
- `apps/Server/app/api/tag_routes.py` - Tag API routes
- `apps/Server/tests/api/__init__.py` - Test package init
- `apps/Server/tests/api/test_category_routes.py` - Category routes unit tests
- `apps/Server/tests/api/test_tag_routes.py` - Tag routes unit tests

## Implementation Plan
### Phase 1: Foundation
1. Create the category routes file with router setup and imports
2. Create the tag routes file with router setup and imports
3. Set up test infrastructure for route testing

### Phase 2: Core Implementation
1. Implement all category endpoints following the specification:
   - GET /api/categories - List as tree structure
   - POST /api/categories - Create category
   - GET /api/categories/{id} - Get category with children
   - PUT /api/categories/{id} - Update category
   - DELETE /api/categories/{id} - Delete (fails if has products)
   - PUT /api/categories/{id}/move - Move to new parent

2. Implement all tag endpoints following the specification:
   - GET /api/tags - List all tags with product counts
   - POST /api/tags - Create tag
   - GET /api/tags/{id} - Get tag detail
   - PUT /api/tags/{id} - Update tag
   - DELETE /api/tags/{id} - Delete tag (cascades)
   - GET /api/tags/search - Search for autocomplete

### Phase 3: Integration
1. Register routers in main.py
2. Write comprehensive unit tests
3. Run validation commands

## Step by Step Tasks

### Step 1: Create Category Routes File
Create `apps/Server/app/api/category_routes.py` with the following structure:

- Import FastAPI router, HTTPException, Depends
- Import authentication dependencies (`get_current_user`, `require_roles`)
- Import category service singleton (`category_service`)
- Import all category DTOs from `kompass_dto.py`
- Create APIRouter with tag "Categories"
- Implement the following endpoints:

**GET / (list_categories)**
- Returns `List[CategoryTreeNode]` as tree structure
- Requires authentication (`get_current_user`)
- Uses `category_service.list_categories()`

**POST / (create_category)**
- Request body: `CategoryCreateDTO`
- Response: `CategoryResponseDTO` with status 201
- Requires authentication
- Returns 400 if creation fails (e.g., parent not found)
- Uses `category_service.create_category()`

**GET /{category_id} (get_category)**
- Path param: `category_id: UUID`
- Response: `CategoryResponseDTO`
- Requires authentication
- Returns 404 if not found
- Uses `category_service.get_category()`

**PUT /{category_id} (update_category)**
- Path param: `category_id: UUID`
- Request body: `CategoryUpdateDTO`
- Response: `CategoryResponseDTO`
- Requires admin or manager role
- Returns 404 if not found
- Returns 400 if update fails (cycle prevention, invalid parent)
- Uses `category_service.update_category()`

**DELETE /{category_id} (delete_category)**
- Path param: `category_id: UUID`
- Response: 204 No Content
- Requires admin or manager role
- Returns 409 Conflict if category has children or products
- Uses `category_service.delete_category()`

**PUT /{category_id}/move (move_category)**
- Path param: `category_id: UUID`
- Request body: Pydantic model with `new_parent_id: Optional[UUID]`
- Response: `CategoryResponseDTO`
- Requires admin or manager role
- Returns 404 if category or new parent not found
- Returns 400 if move creates cycle
- Uses `category_service.move_category()`

### Step 2: Create Tag Routes File
Create `apps/Server/app/api/tag_routes.py` with the following structure:

- Import FastAPI router, HTTPException, Depends, Query
- Import authentication dependencies
- Import tag service singleton (`tag_service`)
- Import all tag DTOs from `kompass_dto.py`
- Create APIRouter with tag "Tags"
- Implement the following endpoints:

**GET / (list_tags)**
- Response: `List[TagWithCountDTO]`
- Requires authentication
- Uses `tag_service.list_tags()`

**GET /search (search_tags)**
- Query params: `query: str`, `limit: int = 20`
- Response: `List[TagResponseDTO]`
- Requires authentication
- For autocomplete functionality
- Uses `tag_service.search_tags()`
- IMPORTANT: This route must be defined BEFORE `/{tag_id}` to avoid path collision

**POST / (create_tag)**
- Request body: `TagCreateDTO`
- Response: `TagResponseDTO` with status 201
- Requires authentication
- Returns 400 if creation fails
- Uses `tag_service.create_tag()`

**GET /{tag_id} (get_tag)**
- Path param: `tag_id: UUID`
- Response: `TagWithCountDTO`
- Requires authentication
- Returns 404 if not found
- Uses `tag_service.get_tag()`

**PUT /{tag_id} (update_tag)**
- Path param: `tag_id: UUID`
- Request body: `TagUpdateDTO`
- Response: `TagResponseDTO`
- Requires admin or manager role
- Returns 404 if not found
- Uses `tag_service.update_tag()`

**DELETE /{tag_id} (delete_tag)**
- Path param: `tag_id: UUID`
- Response: 204 No Content
- Requires admin or manager role
- Returns 404 if not found
- Uses `tag_service.delete_tag()`

### Step 3: Register Routers in main.py
Update `apps/Server/main.py`:

- Add imports for the new routers:
  ```python
  from app.api.category_routes import router as category_router
  from app.api.tag_routes import router as tag_router
  ```

- Register routers in `create_app()` function after existing routers:
  ```python
  app.include_router(category_router, prefix="/api/categories")
  app.include_router(tag_router, prefix="/api/tags")
  ```

### Step 4: Create Test Infrastructure
Create `apps/Server/tests/api/__init__.py` as empty package init file.

### Step 5: Create Category Routes Tests
Create `apps/Server/tests/api/test_category_routes.py`:

- Test all category endpoints with mocked service layer
- Test authentication requirements (401 without token)
- Test authorization requirements (403 for non-admin on write ops)
- Test error cases (404, 400, 409)
- Use pytest fixtures for mock data
- Use `unittest.mock.patch` to mock `category_service`

Test cases to include:
- `test_list_categories_returns_tree`
- `test_list_categories_requires_auth`
- `test_create_category_success`
- `test_create_category_with_invalid_parent_returns_400`
- `test_get_category_success`
- `test_get_category_not_found_returns_404`
- `test_update_category_success`
- `test_update_category_requires_admin_or_manager`
- `test_delete_category_success`
- `test_delete_category_with_children_returns_409`
- `test_move_category_success`
- `test_move_category_cycle_returns_400`

### Step 6: Create Tag Routes Tests
Create `apps/Server/tests/api/test_tag_routes.py`:

- Test all tag endpoints with mocked service layer
- Test authentication requirements
- Test authorization requirements for write operations
- Test search endpoint with query params
- Test error cases (404, 400)

Test cases to include:
- `test_list_tags_returns_with_counts`
- `test_list_tags_requires_auth`
- `test_search_tags_success`
- `test_search_tags_empty_query_returns_empty`
- `test_create_tag_success`
- `test_get_tag_success`
- `test_get_tag_not_found_returns_404`
- `test_update_tag_success`
- `test_update_tag_requires_admin_or_manager`
- `test_delete_tag_success`
- `test_delete_tag_not_found_returns_404`

### Step 7: Run Validation Commands
Execute all validation commands to ensure zero regressions.

## Testing Strategy
### Unit Tests
- Mock the service layer to test route logic in isolation
- Test each endpoint for success and error cases
- Test authentication and authorization dependencies
- Use FastAPI TestClient for HTTP-level testing

### Edge Cases
- Creating category with non-existent parent ID
- Deleting category that has children (should fail)
- Deleting category that has products (should fail)
- Moving category to itself (should fail)
- Moving category to its own descendant (should fail)
- Search with empty or whitespace-only query
- Search with special characters
- Creating duplicate tag names (if uniqueness enforced)

## Acceptance Criteria
- [ ] Category tree returned correctly from GET /api/categories
- [ ] All category CRUD operations working (create, read, update, delete)
- [ ] Category move operation working with cycle prevention
- [ ] All tag CRUD operations working
- [ ] Tag search autocomplete functional
- [ ] All endpoints require JWT authentication
- [ ] Write operations (POST, PUT, DELETE) require admin or manager role
- [ ] Proper HTTP status codes returned (201, 204, 400, 401, 403, 404, 409)
- [ ] All unit tests passing
- [ ] Static analysis (ruff) passing
- [ ] Server starts without errors

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && source .venv/bin/activate && python -c "from app.api.category_routes import router; from app.api.tag_routes import router; print('Routes imported successfully')"` - Verify route files import correctly
- `cd apps/Server && .venv/bin/ruff check .` - Run linter to check for code style issues
- `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` - Run all Server tests
- `cd apps/Server && .venv/bin/pytest tests/api/test_category_routes.py tests/api/test_tag_routes.py -v --tb=short` - Run specific route tests
- `cd apps/Server && python -m uvicorn main:app --host 0.0.0.0 --port 8000 &` then `curl -s http://localhost:8000/api/health | jq .` - Verify server starts and health check works

## Notes
- The service layer (CategoryService, TagService) is already fully implemented in Phase 2
- All DTOs are already defined in `kompass_dto.py`
- Follow the logging pattern: `print(f"INFO/WARN/ERROR [CategoryRoutes]: message")`
- The `/api/tags/search` endpoint must be defined BEFORE `/{tag_id}` to avoid FastAPI treating "search" as a UUID
- Category delete uses soft delete (is_active=False) while tag delete is a hard delete with FK cascade
- For the move endpoint, create a small Pydantic model for the request body: `CategoryMoveDTO` with just `new_parent_id: Optional[UUID]`
