# Category and Tag API Routes

**ADW ID:** c58228ec
**Date:** 2026-01-31
**Specification:** specs/issue-8-adw-c58228ec-sdlc_planner-category-tag-api-routes.md

## Overview

This feature implements FastAPI REST API routes for managing hierarchical product categories and flexible tags in the Kompass Portfolio & Quotation System. The routes expose CRUD endpoints for both entities, including specialized tree operations for categories and tag search functionality for autocomplete.

## What Was Built

- Category API routes with full CRUD operations and tree structure support
- Tag API routes with full CRUD operations and search autocomplete
- JWT authentication on all endpoints
- Role-based access control (admin/manager) for write operations
- Comprehensive unit tests for both route modules

## Technical Implementation

### Files Modified

- `apps/Server/app/api/category_routes.py`: New file - Category API routes with 6 endpoints
- `apps/Server/app/api/tag_routes.py`: New file - Tag API routes with 6 endpoints
- `apps/Server/main.py`: Router registration for `/api/categories` and `/api/tags`
- `apps/Server/tests/api/__init__.py`: New test package init
- `apps/Server/tests/api/test_category_routes.py`: New file - Category routes unit tests
- `apps/Server/tests/api/test_tag_routes.py`: New file - Tag routes unit tests

### Key Changes

- **Category Routes** (`/api/categories`):
  - `GET /` - List categories as nested tree structure
  - `POST /` - Create category (201 on success, 400 if parent not found)
  - `GET /{category_id}` - Get category by ID (404 if not found)
  - `PUT /{category_id}` - Update category (requires admin/manager role)
  - `DELETE /{category_id}` - Soft delete category (409 if has children/products)
  - `PUT /{category_id}/move` - Move category to new parent (400 if creates cycle)

- **Tag Routes** (`/api/tags`):
  - `GET /` - List all tags with product counts
  - `GET /search` - Search tags for autocomplete (defined before `/{tag_id}` to avoid path collision)
  - `POST /` - Create tag (201 on success)
  - `GET /{tag_id}` - Get tag with product count (404 if not found)
  - `PUT /{tag_id}` - Update tag (requires admin/manager role)
  - `DELETE /{tag_id}` - Hard delete tag with FK cascade

- **Authentication/Authorization**:
  - All endpoints require JWT authentication via `get_current_user`
  - Write operations (POST, PUT, DELETE) require `admin` or `manager` role via `require_roles`

## How to Use

1. **List Categories as Tree**:
   ```bash
   curl -H "Authorization: Bearer <token>" http://localhost:8000/api/categories
   ```

2. **Create a Category**:
   ```bash
   curl -X POST -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"name": "Electronics", "description": "Electronic products"}' \
     http://localhost:8000/api/categories
   ```

3. **Move a Category**:
   ```bash
   curl -X PUT -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"new_parent_id": "uuid-of-new-parent"}' \
     http://localhost:8000/api/categories/{category_id}/move
   ```

4. **Search Tags for Autocomplete**:
   ```bash
   curl -H "Authorization: Bearer <token>" \
     "http://localhost:8000/api/tags/search?query=elec&limit=10"
   ```

5. **Create a Tag**:
   ```bash
   curl -X POST -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"name": "wireless"}' \
     http://localhost:8000/api/tags
   ```

## Configuration

No additional configuration required. The routes use existing:
- JWT authentication from `app.api.dependencies`
- RBAC from `app.api.rbac_dependencies`
- CategoryService and TagService from Phase 2

## Testing

Run the route tests:
```bash
cd apps/Server
.venv/bin/pytest tests/api/test_category_routes.py tests/api/test_tag_routes.py -v --tb=short
```

Run all server tests:
```bash
cd apps/Server
.venv/bin/pytest tests/ -v --tb=short
```

## Notes

- The `/api/tags/search` endpoint is defined before `/{tag_id}` to prevent FastAPI from treating "search" as a UUID
- Category delete uses soft delete (is_active=False) while tag delete is a hard delete with FK cascade
- The `CategoryMoveDTO` Pydantic model is defined locally in category_routes.py with just `new_parent_id: Optional[UUID]`
- All routes follow the logging pattern: `print(f"INFO/WARN [CategoryRoutes/TagRoutes]: message")`
