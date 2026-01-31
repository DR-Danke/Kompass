# Supplier API Routes

**ADW ID:** 98d1d93c
**Date:** 2026-01-31
**Specification:** specs/issue-6-adw-98d1d93c-sdlc_planner-supplier-api-routes.md

## Overview

Implemented complete REST API routes for supplier management in the Kompass Portfolio & Quotation Automation System. This feature exposes the existing supplier service layer through authenticated FastAPI endpoints with CRUD operations, pagination, filtering, search, and related product listing.

## What Was Built

- GET `/api/suppliers` - List suppliers with pagination, filtering (status, country, has_products), and sorting
- POST `/api/suppliers` - Create a new supplier (201 response)
- GET `/api/suppliers/search` - Search suppliers by name, email, or contact phone
- GET `/api/suppliers/{id}` - Get supplier details with product count
- PUT `/api/suppliers/{id}` - Update an existing supplier
- DELETE `/api/suppliers/{id}` - Soft delete a supplier (admin/manager only, RBAC protected)
- GET `/api/suppliers/{id}/products` - List products for a specific supplier with pagination

## Technical Implementation

### Files Modified

- `apps/Server/app/api/supplier_routes.py`: New file with all supplier API endpoints (270 lines)
- `apps/Server/main.py`: Added supplier router registration at `/api/suppliers` prefix
- `apps/Server/tests/api/__init__.py`: New package init for API tests
- `apps/Server/tests/api/test_supplier_routes.py`: Comprehensive unit tests (481 lines)

### Key Changes

- All endpoints require JWT authentication via `get_current_user` dependency
- DELETE endpoint requires admin or manager role via `require_roles(['admin', 'manager'])`
- Status filter converts string to `SupplierStatus` enum with validation
- Search endpoint defined before `/{supplier_id}` to avoid path conflicts
- Product listing uses `ProductFilterDTO` with `supplier_id` filter
- Comprehensive error handling with appropriate HTTP status codes (400, 404, 403)
- Follows existing logging convention: `print(f"INFO/WARN [SupplierRoutes]: ...")`

## How to Use

1. Authenticate and obtain JWT token from `/api/auth/login`
2. Include token in Authorization header: `Bearer <token>`
3. List suppliers:
   ```
   GET /api/suppliers?page=1&limit=20&status=active&country=CN&sort_by=name&sort_order=asc
   ```
4. Create supplier:
   ```
   POST /api/suppliers
   Body: { "name": "Supplier Name", "email": "contact@supplier.com", ... }
   ```
5. Search suppliers:
   ```
   GET /api/suppliers/search?query=keyword
   ```
6. Get supplier with product count:
   ```
   GET /api/suppliers/{supplier_id}
   ```
7. Update supplier:
   ```
   PUT /api/suppliers/{supplier_id}
   Body: { "name": "Updated Name", ... }
   ```
8. Delete supplier (admin/manager only):
   ```
   DELETE /api/suppliers/{supplier_id}
   ```
9. List supplier products:
   ```
   GET /api/suppliers/{supplier_id}/products?page=1&limit=20
   ```

## Configuration

No additional configuration required. Uses existing:
- JWT authentication settings (`JWT_SECRET_KEY`, `JWT_ALGORITHM`)
- Database connection (`DATABASE_URL`)
- CORS settings (`CORS_ORIGINS`)

## Testing

Run supplier route tests:
```bash
cd apps/Server
source .venv/bin/activate
.venv/bin/pytest tests/api/test_supplier_routes.py -v --tb=short
```

Run all server tests:
```bash
.venv/bin/pytest tests/ -v --tb=short
```

## Notes

- The `supplier_service` singleton handles all business logic
- Soft delete sets supplier status to inactive (does not remove records)
- Cannot delete suppliers with active products (returns 400)
- OpenAPI documentation available at `/docs` with full endpoint schemas
- Response models use existing DTOs: `SupplierResponseDTO`, `SupplierListResponseDTO`, `ProductListResponseDTO`
