# Portfolio Service for Curated Product Collections

**ADW ID:** 566f84a0
**Date:** 2026-01-31
**Specification:** specs/issue-10-adw-566f84a0-portfolio-service.md

## Overview

This feature implements a comprehensive portfolio service layer for the Kompass Portfolio & Quotation System. The service enables sales teams to create and manage curated product collections, share them with clients via secure share tokens, and auto-generate portfolios from product filter criteria.

## What Was Built

- Complete `PortfolioService` class with business logic layer
- Full CRUD operations for portfolios with DTO mapping
- Portfolio duplication functionality
- Product management within portfolios (add, remove, reorder)
- Auto-creation of portfolios from product filter criteria
- JWT-based share token generation for public portfolio access
- RESTful API routes with authentication and RBAC
- Comprehensive unit tests for service and API layers

## Technical Implementation

### Files Modified

- `apps/Server/app/services/portfolio_service.py`: New portfolio service with all business logic (696 lines)
- `apps/Server/app/api/portfolio_routes.py`: New API routes for portfolio management (544 lines)
- `apps/Server/app/models/kompass_dto.py`: Added 6 new DTOs for portfolio operations
- `apps/Server/app/repository/kompass_repository.py`: Extended with 4 new repository methods
- `apps/Server/main.py`: Registered portfolio router at `/api/portfolios`
- `apps/Server/tests/services/test_portfolio_service.py`: Unit tests for portfolio service (503 lines)
- `apps/Server/tests/api/test_portfolio_routes.py`: API route tests (610 lines)

### Key Changes

- **Service Layer Pattern**: Follows singleton pattern established by `SupplierService` with dependency injection for repository
- **DTO Mapping**: Complete mapping between repository dictionaries and response DTOs
- **Share Token Security**: Uses JWT tokens (30-day expiry) with same secret as auth for secure public access
- **Reorder Validation**: Strict validation requiring all product IDs in portfolio to be provided for reordering
- **RBAC Enforcement**: Create/update/delete operations require admin or manager role; read operations require authentication; public share endpoint requires no auth

### New DTOs

| DTO | Purpose |
|-----|---------|
| `PortfolioFilterDTO` | Filter parameters for portfolio queries (niche_id, is_active, search) |
| `PortfolioShareTokenResponseDTO` | Share token response with expiration |
| `PortfolioPublicResponseDTO` | Public portfolio view (omits is_active field) |
| `ReorderProductsRequestDTO` | Product ID list for reordering |
| `PortfolioDuplicateRequestDTO` | New name for portfolio duplication |
| `PortfolioFromFiltersRequestDTO` | Name, filters, and optional niche for auto-creation |

### New Repository Methods

| Method | Purpose |
|--------|---------|
| `get_by_name(name)` | Check for duplicate portfolio names |
| `search(query, limit)` | Search portfolios by name or description |
| `update_items_sort_orders(portfolio_id, items)` | Batch update product sort orders |
| `get_item_product_ids(portfolio_id)` | Get list of product IDs in portfolio |

## How to Use

### Create a Portfolio

```bash
POST /api/portfolios
Authorization: Bearer <token>  # Requires admin or manager role

{
  "name": "Summer Collection 2026",
  "description": "Curated products for summer season",
  "niche_id": "uuid-of-niche",  # optional
  "is_active": true,
  "items": [  # optional initial items
    {"product_id": "uuid", "sort_order": 0, "notes": "Featured item"}
  ]
}
```

### Add Products to Portfolio

```bash
POST /api/portfolios/{portfolio_id}/products/{product_id}
Authorization: Bearer <token>

{
  "curator_notes": "Great for beach resorts"  # optional
}
```

### Reorder Products

```bash
PUT /api/portfolios/{portfolio_id}/products/reorder
Authorization: Bearer <token>

{
  "product_ids": ["uuid-1", "uuid-2", "uuid-3"]  # All products in desired order
}
```

### Generate Share Link

```bash
POST /api/portfolios/{portfolio_id}/share
Authorization: Bearer <token>

# Response:
{
  "token": "eyJ...",
  "portfolio_id": "uuid",
  "expires_at": "2026-03-02T12:00:00Z"
}
```

### Access Portfolio via Share Token (Public)

```bash
GET /api/portfolios/shared/{token}
# No authentication required
```

### Create Portfolio from Product Filters

```bash
POST /api/portfolios/from-filters
Authorization: Bearer <token>

{
  "name": "Electronics Sale",
  "description": "All electronics on sale",
  "filters": {
    "category_id": "uuid",
    "min_price": 10.00,
    "max_price": 500.00,
    "status": "active"
  }
}
```

## Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| `JWT_SECRET_KEY` | Secret for share token signing | Required |
| `JWT_ALGORITHM` | Algorithm for JWT | HS256 |
| `SHARE_TOKEN_EXPIRE_DAYS` | Token expiration in days | 30 |

## Testing

### Run Portfolio Service Tests

```bash
cd apps/Server
source .venv/bin/activate
.venv/bin/pytest tests/services/test_portfolio_service.py -v --tb=short
```

### Run Portfolio API Tests

```bash
cd apps/Server
source .venv/bin/activate
.venv/bin/pytest tests/api/test_portfolio_routes.py -v --tb=short
```

### Run All Tests

```bash
cd apps/Server
source .venv/bin/activate
.venv/bin/pytest tests/ -v --tb=short
```

## API Endpoints Summary

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | `/api/portfolios` | Yes | Any | List portfolios with filters |
| GET | `/api/portfolios/search?q=` | Yes | Any | Search portfolios |
| GET | `/api/portfolios/shared/{token}` | No | - | Public access via share token |
| POST | `/api/portfolios` | Yes | admin/manager | Create portfolio |
| GET | `/api/portfolios/{id}` | Yes | Any | Get portfolio by ID |
| PUT | `/api/portfolios/{id}` | Yes | admin/manager | Update portfolio |
| DELETE | `/api/portfolios/{id}` | Yes | admin/manager | Soft delete portfolio |
| POST | `/api/portfolios/{id}/duplicate` | Yes | admin/manager | Duplicate portfolio |
| POST | `/api/portfolios/{id}/products/{pid}` | Yes | admin/manager | Add product |
| DELETE | `/api/portfolios/{id}/products/{pid}` | Yes | admin/manager | Remove product |
| PUT | `/api/portfolios/{id}/products/reorder` | Yes | admin/manager | Reorder products |
| POST | `/api/portfolios/{id}/share` | Yes | admin/manager | Generate share token |
| POST | `/api/portfolios/from-filters` | Yes | admin/manager | Create from filters |

## Notes

- Soft delete sets `is_active=False` rather than removing records
- Share tokens expire after 30 days by default
- Inactive portfolios return 404 when accessed via share token
- The `create_from_filters` method respects product status (only includes active products)
- Product reordering uses sequential sort_order values (0, 1, 2, ...)
- Duplicate portfolio names are not allowed
