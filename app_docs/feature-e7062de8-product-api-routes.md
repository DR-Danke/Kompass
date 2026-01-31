# Product API Routes (Biblia General)

**ADW ID:** e7062de8
**Date:** 2026-01-31
**Specification:** specs/issue-7-adw-e7062de8-product-api-routes.md

## Overview

RESTful API routes for product management in the Kompass Portfolio & Quotation system. This feature exposes the ProductService functionality through FastAPI endpoints, enabling CRUD operations, image management, tag management, advanced filtering, and full-text search for products.

## What Was Built

- 11 RESTful API endpoints for product management
- CRUD operations for products (list, create, get, update, delete)
- Image management endpoints (add, remove, set primary)
- Tag management endpoints (add, remove)
- Full-text search endpoint
- Advanced filtering with pagination and sorting
- Comprehensive unit test coverage (731 lines of tests)

## Technical Implementation

### Files Modified

- `apps/Server/app/api/product_routes.py`: New file containing all 11 product API endpoints with authentication and RBAC
- `apps/Server/main.py`: Router registration for product routes at `/api/products` prefix
- `apps/Server/tests/test_product_routes.py`: Comprehensive unit tests for all endpoints

### Key Changes

- **Router with Authentication**: All endpoints require JWT authentication via `get_current_user` dependency
- **RBAC Enforcement**: Write operations (POST, PUT, DELETE) require `admin` or `manager` role via `require_roles` dependency
- **Route Ordering**: Search endpoint (`/products/search`) defined before `/{product_id}` to prevent route conflicts
- **Advanced Filtering**: List endpoint supports filtering by supplier, category, status, price range, MOQ range, tags, and image presence
- **Soft Delete**: Delete endpoint performs soft delete by setting product status to inactive

### Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/products` | List products with filters/pagination | User |
| POST | `/api/products` | Create product | Admin/Manager |
| GET | `/api/products/search` | Full-text search | User |
| GET | `/api/products/{id}` | Get single product | User |
| PUT | `/api/products/{id}` | Update product | Admin/Manager |
| DELETE | `/api/products/{id}` | Soft delete product | Admin/Manager |
| POST | `/api/products/{id}/images` | Add image | Admin/Manager |
| DELETE | `/api/products/{id}/images/{image_id}` | Remove image | Admin/Manager |
| PUT | `/api/products/{id}/images/{image_id}/primary` | Set primary image | Admin/Manager |
| POST | `/api/products/{id}/tags/{tag_id}` | Add tag | Admin/Manager |
| DELETE | `/api/products/{id}/tags/{tag_id}` | Remove tag | Admin/Manager |

## How to Use

1. **List Products with Filtering**
   ```bash
   GET /api/products?page=1&limit=20&status=active&category_id=<uuid>&price_min=100
   ```

2. **Create a Product**
   ```bash
   POST /api/products
   Content-Type: application/json
   Authorization: Bearer <token>

   {
     "name": "Product Name",
     "supplier_id": "<uuid>",
     "category_id": "<uuid>",
     "unit_price": 99.99,
     "minimum_order_qty": 10
   }
   ```

3. **Search Products**
   ```bash
   GET /api/products/search?q=search_term&limit=50
   ```

4. **Manage Images**
   ```bash
   POST /api/products/{id}/images
   {
     "url": "https://example.com/image.jpg",
     "alt_text": "Product image",
     "is_primary": true
   }
   ```

5. **Manage Tags**
   ```bash
   POST /api/products/{id}/tags/{tag_id}
   DELETE /api/products/{id}/tags/{tag_id}
   ```

## Configuration

No additional configuration required. The routes use existing authentication and service layer infrastructure.

**Required Environment Variables** (already configured):
- `JWT_SECRET_KEY`: For authentication
- `DATABASE_URL`: For database access

## Testing

Run the product routes tests:
```bash
cd apps/Server && .venv/bin/pytest tests/test_product_routes.py -v --tb=short
```

Run all server tests:
```bash
cd apps/Server && .venv/bin/pytest tests/ -v --tb=short
```

## Notes

- **Image Storage**: This implementation handles image URLs only. Supabase Storage file upload integration can be added as a future enhancement.
- **Soft Delete**: The delete endpoint sets product status to inactive rather than hard deleting records.
- **Tags Parameter**: The tags query parameter accepts comma-separated UUIDs (e.g., `?tags=uuid1,uuid2,uuid3`).
- **Status Values**: Valid status values are `draft`, `active`, `inactive`, `discontinued`.
- **Logging Pattern**: All endpoints use `print(f"INFO [ProductRoutes]: ...")` for consistent logging.
