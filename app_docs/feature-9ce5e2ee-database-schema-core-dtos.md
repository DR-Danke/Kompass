# Database Schema and Core DTOs for Kompass Portfolio & Quotation System

**ADW ID:** 9ce5e2ee
**Date:** 2026-01-31
**Specification:** specs/issue-1-adw-9ce5e2ee-sdlc_planner-database-schema-core-dtos.md

## Overview

This feature implements the foundational database schema and core data transfer objects (DTOs) for the Kompass Portfolio & Quotation Automation System. It provides 15 database tables with proper constraints, indexes, and foreign key relationships, along with comprehensive Pydantic DTOs and repository classes for all entities. This is Phase 1 of 13 and serves as the foundation for all subsequent features.

## What Was Built

- **15 database tables** for suppliers, products, portfolios, clients, quotations, and reference data
- **5 status enums** (SupplierStatus, ProductStatus, ClientStatus, QuotationStatus, Incoterm)
- **50+ Pydantic DTOs** for create, update, response, and list operations
- **10 repository classes** with CRUD operations following the singleton pattern
- **Auto-update triggers** for all tables with `updated_at` columns
- **Comprehensive indexing** on frequently queried columns

## Technical Implementation

### Files Modified

- `apps/Server/database/schema.sql`: Added 15 Kompass tables with constraints, indexes, and triggers (~370 lines added)
- `apps/Server/app/models/kompass_dto.py`: Created all DTOs (851 lines) - enums, request/response models, pagination
- `apps/Server/app/repository/kompass_repository.py`: Created repository layer (3315 lines) - CRUD for all entities

### Key Changes

- **Core Reference Tables**: `niches`, `categories` (hierarchical), `tags`, `hs_codes` for product classification
- **Supplier & Product Tables**: `suppliers`, `products`, `product_images`, `product_tags` for the master product database (Biblia General)
- **Portfolio Tables**: `portfolios`, `portfolio_items` for curated product collections by client niche
- **Client & Pricing Tables**: `clients`, `freight_rates`, `pricing_settings` for customer management and global pricing config
- **Quotation Tables**: `quotations`, `quotation_items` for quote generation with detailed line items and pricing breakdown

### Database Schema Overview

```
Core Reference:
  niches              - Client types (constructor, architect, hotel, retailer)
  categories          - Hierarchical product categories with parent_id self-reference
  tags                - Flexible product tagging system
  hs_codes            - Tariff classification codes with duty rates

Suppliers & Products:
  suppliers           - Chinese vendor registry with status, contact info
  products            - Master product database with pricing, dimensions, lead times
  product_images      - Product gallery with sort_order
  product_tags        - Many-to-many product-tag relationships

Portfolios:
  portfolios          - Curated product collections for client niches
  portfolio_items     - Products within portfolios

Clients & Pricing:
  clients             - Client/prospect registry with niche association
  freight_rates       - Origin/destination shipping rates by incoterm
  pricing_settings    - Global pricing parameters (markup percentages, etc.)

Quotations:
  quotations          - Client quotes with totals, validity period, status
  quotation_items     - Line items with quantity, pricing breakdown, tariffs
```

### DTO Structure

All DTOs follow the existing pattern from `auth_dto.py`:

```python
# Enums for status fields
class SupplierStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_REVIEW = "pending_review"

# Request DTOs with Pydantic validation
class SupplierCreateDTO(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    status: SupplierStatus = SupplierStatus.ACTIVE
    # ... other fields with validation

# Response DTOs with from_attributes config
class SupplierResponseDTO(BaseModel):
    id: UUID
    name: str
    status: SupplierStatus
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}

# Paginated list responses
class SupplierListResponseDTO(BaseModel):
    items: List[SupplierResponseDTO]
    pagination: PaginationDTO
```

### Repository Pattern

All repositories follow the singleton pattern from `user_repository.py`:

```python
class SupplierRepository:
    def create(self, name: str, ...) -> Optional[Dict[str, Any]]:
        conn = get_database_connection()
        # ... SQL INSERT with RETURNING

    def get_by_id(self, supplier_id: UUID) -> Optional[Dict[str, Any]]:
        # ... SQL SELECT

    def get_all(self, page: int, limit: int, ...) -> Tuple[List[Dict], int]:
        # ... SQL SELECT with pagination

    def update(self, supplier_id: UUID, ...) -> Optional[Dict[str, Any]]:
        # ... SQL UPDATE with dynamic fields

    def delete(self, supplier_id: UUID) -> bool:
        # Soft delete (set inactive)

# Singleton instance
supplier_repository = SupplierRepository()
```

## How to Use

### 1. Run Database Migration

```bash
psql $DATABASE_URL -f apps/Server/database/schema.sql
```

### 2. Import DTOs in API Routes

```python
from app.models.kompass_dto import (
    SupplierCreateDTO,
    SupplierResponseDTO,
    SupplierListResponseDTO,
    PaginationDTO,
)
```

### 3. Use Repositories for Data Access

```python
from app.repository.kompass_repository import (
    supplier_repository,
    product_repository,
    portfolio_repository,
    client_repository,
    quotation_repository,
)

# Create a supplier
supplier = supplier_repository.create(
    name="Shenzhen Electronics Co.",
    status=SupplierStatus.ACTIVE,
    city="Shenzhen",
    country="China"
)

# Get with pagination
suppliers, total = supplier_repository.get_all(page=1, limit=20)
```

### 4. Build API Endpoints

```python
@router.post("/suppliers", response_model=SupplierResponseDTO)
async def create_supplier(
    data: SupplierCreateDTO,
    current_user: dict = Depends(get_current_user)
):
    result = supplier_repository.create(
        name=data.name,
        code=data.code,
        status=data.status.value,
        # ... other fields
    )
    return SupplierResponseDTO(**result)
```

## Configuration

No additional configuration required. Uses existing database connection from `app/config/database.py`.

### Monetary Values

All monetary values use `DECIMAL(12,2)` for precision:
- `unit_cost`, `unit_price` on products
- `rate_per_kg`, `rate_per_cbm` on freight rates
- `subtotal`, `total`, `grand_total` on quotations

### Status Fields

All status fields use VARCHAR with CHECK constraints matching enum values:
- `suppliers.status`: active, inactive, pending_review
- `products.status`: active, inactive, draft, discontinued
- `clients.status`: active, inactive, prospect
- `quotations.status`: draft, sent, accepted, rejected, expired

## Testing

### Verify DTO Imports

```bash
cd apps/Server && source .venv/bin/activate
python -c "from app.models.kompass_dto import *; print('DTOs imported successfully')"
```

### Verify Repository Imports

```bash
cd apps/Server && source .venv/bin/activate
python -c "from app.repository.kompass_repository import *; print('Repositories imported successfully')"
```

### Run Linting

```bash
cd apps/Server && .venv/bin/ruff check .
```

### Run Tests

```bash
cd apps/Server && .venv/bin/pytest tests/ -v --tb=short
```

## Notes

- This is Phase 1 of 13 (Foundation) and must be completed first as all other phases depend on this schema
- The repository layer uses raw SQL with psycopg2 (no ORM) following existing patterns
- Soft deletes are used for all entities (set `is_active=False` or `status='inactive'`)
- All tables include `created_at` and `updated_at` audit fields with auto-update triggers
- Foreign keys use UUID types with `ON DELETE RESTRICT` or `ON DELETE SET NULL` as appropriate
- The quotation system supports complex pricing with tariffs, freight, insurance, and discounts
