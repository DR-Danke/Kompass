# Kompass Portfolio & Quotation System - ADW Implementation Prompts

**Document Version:** 1.0
**Created:** January 31, 2026
**Purpose:** GitHub issue prompts for parallel ADW execution

---

## Quick Reference

| Metric | Value |
|--------|-------|
| Total Issues | 33 |
| Parallel Phases | 13 |
| Max Concurrent ADWs | 4 |
| Backend Files | ~25 new files |
| Frontend Files | ~20 new files |
| Database Tables | 15 new tables |
| API Endpoints | ~50 new endpoints |

---

## Dependency Graph

```
Phase 1: Foundation
    └── KP-001 (Database Schema & DTOs)
            │
            ▼
Phase 2: Backend Core Services (4 parallel)
    ├── KP-002 (Supplier Service)
    ├── KP-003 (Product Service)
    ├── KP-004 (Category/Tag Service)
    └── KP-005 (Data Extraction Service)
            │
            ▼
Phase 3: API Routes Part 1 (4 parallel)
    ├── KP-006 (Supplier Routes)
    ├── KP-007 (Product Routes)
    ├── KP-008 (Category/Tag Routes)
    └── KP-009 (Data Extraction Routes)
            │
            ▼
Phase 4: Portfolio & Client Backend (3 parallel)
    ├── KP-010 (Portfolio Service)
    ├── KP-011 (Client Service)
    └── KP-012 (Niche Service)
            │
            ▼
Phase 5: API Routes Part 2 (3 parallel)
    ├── KP-013 (Portfolio Routes)
    ├── KP-014 (Client Routes)
    └── KP-015 (Niche Routes)
            │
            ▼
Phase 6: Pricing & Quotation Backend (Sequential)
    ├── KP-016 (Pricing Config Service)
    └── KP-017 (Quotation Service) ←── KP-016
            │
            ▼
Phase 7: Pricing & Quotation Routes (2 parallel)
    ├── KP-018 (Pricing Routes)
    └── KP-019 (Quotation Routes)
            │
            ▼
Phase 8: Frontend Foundation
    └── KP-020 (Types & Service Layer)
            │
            ▼
Phase 9: Frontend Core (4 parallel)
    ├── KP-021 (Suppliers Page)
    ├── KP-022 (Products Catalog)
    ├── KP-023 (Import Wizard)
    └── KP-024 (Categories Page)
            │
            ▼
Phase 10: Frontend Portfolio & Clients (3 parallel)
    ├── KP-025 (Portfolio Builder)
    ├── KP-026 (Clients Pipeline)
    └── KP-027 (Niches Config)
            │
            ▼
Phase 11: Frontend Quotation (2 parallel)
    ├── KP-028 (Quotation Creator)
    └── KP-029 (Pricing Config UI)
            │
            ▼
Phase 12: Dashboard & Export (2 parallel)
    ├── KP-030 (Dashboard KPIs)
    └── KP-031 (PDF Generation)
            │
            ▼
Phase 13: Testing & Documentation (2 parallel)
    ├── KP-032 (E2E Tests)
    └── KP-033 (Documentation)
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI + Python 3.11.9 |
| Database | Supabase PostgreSQL |
| Auth | Custom JWT (existing) |
| AI Extraction | Claude/OpenAI Vision API |
| Image Processing | rembg or remove.bg API |
| PDF Generation | WeasyPrint |
| Frontend | React 19 + MUI + TypeScript |
| File Storage | Supabase Storage |
| Deployment | Vercel (FE) + Render (BE) |

---

## Phase 1: Foundation (Sequential)

### KP-001: Database Schema & Core DTOs

**Title:** `[Kompass] Phase 1: Database Schema and Core DTOs`

**Body:**
```markdown
## Context
**Project:** Kompass Portfolio & Quotation Automation System
**Overview:** We are building a system to automate portfolio creation and quotation generation for a China sourcing/trading business. The system handles suppliers, products (Biblia General), curated portfolios, clients, and complex pricing with tariffs/freight. The implementation is divided into 13 phases with 33 total issues.

**Current Phase:** Phase 1 of 13 - Foundation
**Current Issue:** KP-001 (Issue 1 of 33)
**Parallel Execution:** NO - This issue must be completed FIRST as it creates the database schema and core types that all other issues depend on.

**What comes next:** After this issue, Phase 2 begins with 4 parallel backend service implementations (KP-002, KP-003, KP-004, KP-005).

---

## Description
Create the foundational database schema and core DTOs for the Kompass Portfolio & Quotation system.

## Requirements

### Database Tables (apps/Server/database/schema.sql - append to existing)

1. `niches` - Client types (constructor, architect, hotel, retailer, etc.)
2. `categories` - Product categories (hierarchical with parent_id)
3. `suppliers` - Chinese supplier registry
4. `products` - Master product database (Biblia General)
5. `product_images` - Product image gallery
6. `tags` - Flexible product tagging
7. `product_tags` - Many-to-many product-tag relationship
8. `portfolios` - Curated product collections
9. `portfolio_items` - Products in portfolios
10. `clients` - Client/prospect registry
11. `hs_codes` - Tariff classification codes
12. `freight_rates` - Shipping cost by route
13. `pricing_settings` - Global pricing parameters
14. `quotations` - Quote headers
15. `quotation_items` - Quote line items

### DTOs (apps/Server/app/models/kompass_dto.py)
- Enums: SupplierStatus, ProductStatus, ClientStatus, QuotationStatus, Incoterm
- Request DTOs: CreateSupplier, UpdateSupplier, CreateProduct, CreatePortfolio, CreateClient, CreateQuotation
- Response DTOs: SupplierResponse, ProductResponse, PortfolioResponse, ClientResponse, QuotationResponse
- List DTOs with pagination support

### Repository Base (apps/Server/app/repository/kompass_repository.py)
- SupplierRepository with CRUD
- ProductRepository with CRUD + filtering
- PortfolioRepository
- ClientRepository
- QuotationRepository

## Acceptance Criteria
- [ ] All 15 database tables created with proper constraints and indexes
- [ ] Foreign key relationships established
- [ ] All DTOs defined with Pydantic validation
- [ ] Base repository classes implemented
- [ ] Database migration runs successfully

## Technical Notes
- Follow existing patterns from `apps/Server/database/schema.sql`
- Use UUID primary keys with `gen_random_uuid()`
- Include audit fields (created_at, updated_at)
- Add auto-update triggers for updated_at
- Use DECIMAL for monetary values (not FLOAT)

Include workflow: adw_plan_build_test_iso model_set heavy
```

**ADW Command:**
```bash
cd adws && uv run adw_plan_build_test_iso.py KP-001
```

---

## Phase 2: Backend Core Services (4 Parallel)

### KP-002: Supplier Service

**Title:** `[Kompass] Phase 2A: Supplier Service - CRUD & Management`

**Body:**
```markdown
## Context
**Project:** Kompass Portfolio & Quotation Automation System
**Overview:** We are building a system to automate portfolio creation and quotation generation for a China sourcing/trading business. The system handles suppliers, products (Biblia General), curated portfolios, clients, and complex pricing with tariffs/freight. The implementation is divided into 13 phases with 33 total issues.

**Current Phase:** Phase 2 of 13 - Backend Core Services
**Current Issue:** KP-002 (Issue 2 of 33)
**Parallel Execution:** YES - This issue runs IN PARALLEL with KP-003, KP-004, and KP-005. All 4 backend services are being developed simultaneously in separate worktrees.

**What was completed:** Phase 1 (KP-001) - Database schema and core DTOs are now available.
**What comes next:** After Phase 2, we move to Phase 3 (API Routes Part 1) which also runs 4 issues in parallel.

---

## Description
Implement the supplier service for managing Chinese supplier information.

## Requirements

### File: apps/Server/app/services/supplier_service.py

#### Core Methods
- `create_supplier(request: CreateSupplierDTO) -> SupplierResponse` - Create new supplier
- `get_supplier(supplier_id: UUID) -> SupplierResponse` - Get single supplier with product count
- `list_suppliers(filters: SupplierFilters, page: int, limit: int) -> PaginatedResponse` - List with filtering
- `update_supplier(supplier_id: UUID, request: UpdateSupplierDTO) -> SupplierResponse` - Update supplier
- `delete_supplier(supplier_id: UUID) -> bool` - Soft delete (set status=inactive)
- `search_suppliers(query: str) -> List[SupplierResponse]` - Search by name, email, wechat

#### Filtering Support
- Filter by: status (active/inactive), country, has_products (bool)
- Sort by: name, created_at, product_count

#### Business Rules
- Prevent deletion if supplier has active products
- Validate email format
- Normalize WeChat ID (lowercase)

## Dependencies
- Phase 1 (KP-001) must be complete
- Requires: kompass_repository.py, kompass_dto.py

## Acceptance Criteria
- [ ] All CRUD operations working
- [ ] Filtering and pagination functional
- [ ] Soft delete implemented
- [ ] Search returning relevant results
- [ ] Unit tests passing

Include workflow: adw_plan_build_test_iso
```

---

### KP-003: Product Service

**Title:** `[Kompass] Phase 2B: Product Service - Biblia General Management`

**Body:**
```markdown
## Context
**Project:** Kompass Portfolio & Quotation Automation System
**Overview:** We are building a system to automate portfolio creation and quotation generation for a China sourcing/trading business. The system handles suppliers, products (Biblia General), curated portfolios, clients, and complex pricing with tariffs/freight. The implementation is divided into 13 phases with 33 total issues.

**Current Phase:** Phase 2 of 13 - Backend Core Services
**Current Issue:** KP-003 (Issue 3 of 33)
**Parallel Execution:** YES - This issue runs IN PARALLEL with KP-002, KP-004, and KP-005. All 4 backend services are being developed simultaneously in separate worktrees.

**What was completed:** Phase 1 (KP-001) - Database schema and core DTOs are now available.
**What comes next:** After Phase 2, we move to Phase 3 (API Routes Part 1) which also runs 4 issues in parallel.

---

## Description
Implement the product service for managing the Biblia General (master product database).

## Requirements

### File: apps/Server/app/services/product_service.py

#### Core Methods
- `create_product(request: CreateProductDTO) -> ProductResponse` - Create with auto-generated SKU if not provided
- `get_product(product_id: UUID) -> ProductResponse` - Get with images and tags
- `list_products(filters: ProductFilters, page: int, limit: int) -> PaginatedResponse` - List with filtering
- `update_product(product_id: UUID, request: UpdateProductDTO) -> ProductResponse` - Update product
- `delete_product(product_id: UUID) -> bool` - Soft delete
- `search_products(query: str) -> List[ProductResponse]` - Full-text search on name, description, SKU
- `bulk_create_products(products: List[CreateProductDTO]) -> BulkCreateResponse` - Batch import

#### Image Management
- `add_product_image(product_id: UUID, image_url: str, is_primary: bool) -> ProductImageResponse`
- `remove_product_image(product_id: UUID, image_id: UUID) -> bool`
- `set_primary_image(product_id: UUID, image_id: UUID) -> bool`

#### Tag Management
- `add_tag_to_product(product_id: UUID, tag_id: UUID) -> bool`
- `remove_tag_from_product(product_id: UUID, tag_id: UUID) -> bool`
- `get_products_by_tag(tag_id: UUID) -> List[ProductResponse]`

#### Filtering Support
- Filter by: supplier_id, category_id, status, price_range (min/max), moq_range, tags[], has_images
- Sort by: name, price_fob_usd, created_at, moq

## Dependencies
- Phase 1 (KP-001) must be complete

## Acceptance Criteria
- [ ] All CRUD operations working
- [ ] Image management functional
- [ ] Tag management functional
- [ ] Full-text search returning relevant results
- [ ] Bulk import working with validation
- [ ] Unit tests passing

Include workflow: adw_plan_build_test_iso model_set heavy
```

---

### KP-004: Category & Tag Service

**Title:** `[Kompass] Phase 2C: Category and Tag Management Service`

**Body:**
```markdown
## Context
**Project:** Kompass Portfolio & Quotation Automation System
**Overview:** We are building a system to automate portfolio creation and quotation generation for a China sourcing/trading business. The system handles suppliers, products (Biblia General), curated portfolios, clients, and complex pricing with tariffs/freight. The implementation is divided into 13 phases with 33 total issues.

**Current Phase:** Phase 2 of 13 - Backend Core Services
**Current Issue:** KP-004 (Issue 4 of 33)
**Parallel Execution:** YES - This issue runs IN PARALLEL with KP-002, KP-003, and KP-005. All 4 backend services are being developed simultaneously in separate worktrees.

**What was completed:** Phase 1 (KP-001) - Database schema and core DTOs are now available.
**What comes next:** After Phase 2, we move to Phase 3 (API Routes Part 1) which also runs 4 issues in parallel.

---

## Description
Implement services for managing product categories (hierarchical) and tags.

## Requirements

### File: apps/Server/app/services/category_service.py

#### Category Methods
- `create_category(request: CreateCategoryDTO) -> CategoryResponse` - Create with optional parent
- `get_category(category_id: UUID) -> CategoryResponse` - Get with children
- `list_categories() -> List[CategoryTreeNode]` - Return tree structure
- `update_category(category_id: UUID, request: UpdateCategoryDTO) -> CategoryResponse`
- `delete_category(category_id: UUID) -> bool` - Fail if has products or children
- `move_category(category_id: UUID, new_parent_id: UUID) -> CategoryResponse` - Reparent

#### Tree Operations
- Build nested tree from flat database records
- Calculate depth and path for each node
- Get all descendants of a category

### File: apps/Server/app/services/tag_service.py

#### Tag Methods
- `create_tag(request: CreateTagDTO) -> TagResponse` - Create with color
- `get_tag(tag_id: UUID) -> TagResponse` - Get with product count
- `list_tags() -> List[TagResponse]` - All tags with counts
- `update_tag(tag_id: UUID, request: UpdateTagDTO) -> TagResponse`
- `delete_tag(tag_id: UUID) -> bool` - Cascade removes product associations
- `search_tags(query: str) -> List[TagResponse]` - For autocomplete

## Dependencies
- Phase 1 (KP-001) must be complete

## Acceptance Criteria
- [ ] Category CRUD working
- [ ] Hierarchical tree building correctly
- [ ] Tag CRUD working
- [ ] Product counts accurate
- [ ] Delete validations working
- [ ] Unit tests passing

Include workflow: adw_plan_build_test_iso
```

---

### KP-005: Data Extraction Service

**Title:** `[Kompass] Phase 2D: AI Data Extraction Service`

**Body:**
```markdown
## Context
**Project:** Kompass Portfolio & Quotation Automation System
**Overview:** We are building a system to automate portfolio creation and quotation generation for a China sourcing/trading business. The system handles suppliers, products (Biblia General), curated portfolios, clients, and complex pricing with tariffs/freight. The implementation is divided into 13 phases with 33 total issues.

**Current Phase:** Phase 2 of 13 - Backend Core Services
**Current Issue:** KP-005 (Issue 5 of 33)
**Parallel Execution:** YES - This issue runs IN PARALLEL with KP-002, KP-003, and KP-004. All 4 backend services are being developed simultaneously in separate worktrees.

**What was completed:** Phase 1 (KP-001) - Database schema and core DTOs are now available.
**What comes next:** After Phase 2, we move to Phase 3 (API Routes Part 1) which also runs 4 issues in parallel.

---

## Description
Implement AI-powered data extraction from supplier catalogs (PDF, Excel, images).

## Requirements

### File: apps/Server/app/services/extraction_service.py

#### File Processing
- `process_pdf(file_path: str) -> List[ExtractedProduct]` - Extract from PDF catalog
- `process_excel(file_path: str) -> List[ExtractedProduct]` - Parse Excel spreadsheet
- `process_image(file_path: str) -> ExtractedProduct` - Extract from single product image
- `process_batch(file_paths: List[str]) -> ExtractionResult` - Process multiple files

#### AI Extraction (Claude/OpenAI Vision)
- `extract_product_data(image_or_text: str) -> ExtractedProduct`:
  - sku/reference
  - name/description
  - price (if visible)
  - moq (if visible)
  - dimensions
  - material
  - suggested_category

#### Image Processing
- `remove_background(image_url: str) -> str` - Returns URL of processed image
- `resize_image(image_url: str, width: int, height: int) -> str`
- `find_higher_quality_image(image_url: str) -> Optional[str]` - Reverse image search

#### HS Code Suggestion
- `suggest_hs_code(product_description: str) -> HsCodeSuggestion`:
  - code
  - description
  - confidence_score

### DTOs
```python
class ExtractedProduct(BaseModel):
    sku: Optional[str]
    name: str
    description: Optional[str]
    price_fob_usd: Optional[Decimal]
    moq: Optional[int]
    dimensions: Optional[str]
    material: Optional[str]
    suggested_category: Optional[str]
    image_urls: List[str]
    confidence_score: float
    raw_text: str

class ExtractionResult(BaseModel):
    products: List[ExtractedProduct]
    total_extracted: int
    errors: List[str]
    warnings: List[str]
```

## Dependencies
- Phase 1 (KP-001) must be complete
- Environment variable: ANTHROPIC_API_KEY or OPENAI_API_KEY
- Optional: REMOVEBG_API_KEY for background removal

## Acceptance Criteria
- [ ] PDF extraction working
- [ ] Excel parsing working
- [ ] Image extraction working
- [ ] Background removal functional
- [ ] HS code suggestions returning relevant codes
- [ ] Graceful fallback when AI unavailable
- [ ] Unit tests with mocked AI responses

Include workflow: adw_plan_build_test_iso model_set heavy
```

---

**Phase 2 Parallel Execution:**
```bash
cd adws
uv run adw_plan_build_test_iso.py KP-002 &
uv run adw_plan_build_test_iso.py KP-003 &
uv run adw_plan_build_test_iso.py KP-004 &
uv run adw_plan_build_test_iso.py KP-005 &
wait
```

---

## Phase 3: API Routes Part 1 (4 Parallel)

### KP-006: Supplier Routes

**Title:** `[Kompass] Phase 3A: Supplier API Routes`

**Body:**
```markdown
## Context
**Project:** Kompass Portfolio & Quotation Automation System
**Overview:** Building a system to automate portfolio creation and quotation generation. 13 phases, 33 total issues.

**Current Phase:** Phase 3 of 13 - API Routes Part 1
**Current Issue:** KP-006 (Issue 6 of 33)
**Parallel Execution:** YES - This issue runs IN PARALLEL with KP-007, KP-008, and KP-009.

**What was completed:** Phase 1-2 (KP-001 to KP-005) - Database, DTOs, and backend services are now available.
**What comes next:** After Phase 3, we move to Phase 4 (Portfolio & Client Backend).

---

## Description
Implement FastAPI routes for supplier management.

## Requirements

### File: apps/Server/app/api/supplier_routes.py

#### Endpoints
GET    /api/suppliers              - List suppliers (paginated, filterable)
POST   /api/suppliers              - Create supplier
GET    /api/suppliers/{id}         - Get supplier detail with product count
PUT    /api/suppliers/{id}         - Update supplier
DELETE /api/suppliers/{id}         - Soft delete supplier
GET    /api/suppliers/{id}/products - List products from this supplier
GET    /api/suppliers/search       - Search suppliers by query

#### Query Parameters (GET /api/suppliers)
- `status`: active | inactive
- `country`: string
- `has_products`: boolean
- `page`: int (default 1)
- `limit`: int (default 20, max 100)
- `sort_by`: name | created_at | product_count
- `sort_order`: asc | desc

### Register Router
- Add to apps/Server/main.py: `app.include_router(supplier_routes.router, prefix="/api", tags=["suppliers"])`

#### RBAC
- All endpoints require authentication
- Delete requires admin or manager role

## Dependencies
- Phase 2 (KP-002) must be complete

## Acceptance Criteria
- [ ] All endpoints functional
- [ ] Pagination working
- [ ] Filtering working
- [ ] RBAC enforced
- [ ] OpenAPI docs generated

Include workflow: adw_plan_build_test_iso
```

---

### KP-007: Product Routes

**Title:** `[Kompass] Phase 3B: Product API Routes (Biblia General)`

**Body:**
```markdown
## Context
**Project:** Kompass Portfolio & Quotation Automation System
**Current Phase:** Phase 3 of 13 - API Routes Part 1
**Current Issue:** KP-007 (Issue 7 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-006, KP-008, KP-009.

---

## Description
Implement FastAPI routes for product management (Biblia General).

## Requirements

### File: apps/Server/app/api/product_routes.py

#### Endpoints
GET    /api/products              - List products (paginated, filterable)
POST   /api/products              - Create product
GET    /api/products/{id}         - Get product with images and tags
PUT    /api/products/{id}         - Update product
DELETE /api/products/{id}         - Soft delete product
POST   /api/products/{id}/images  - Add image to product
DELETE /api/products/{id}/images/{image_id} - Remove image
PUT    /api/products/{id}/images/{image_id}/primary - Set primary image
POST   /api/products/{id}/tags/{tag_id} - Add tag
DELETE /api/products/{id}/tags/{tag_id} - Remove tag
GET    /api/products/search       - Full-text search

#### Query Parameters (GET /api/products)
- `supplier_id`: UUID
- `category_id`: UUID
- `status`: draft | active | discontinued
- `price_min`: decimal
- `price_max`: decimal
- `moq_min`: int
- `moq_max`: int
- `tags`: comma-separated UUIDs
- `has_images`: boolean
- `page`, `limit`, `sort_by`, `sort_order`

#### File Upload for Images
- Accept multipart/form-data
- Store in Supabase Storage
- Generate thumbnail

## Dependencies
- Phase 2 (KP-003) must be complete

## Acceptance Criteria
- [ ] All endpoints functional
- [ ] Image upload working
- [ ] Tag management working
- [ ] Complex filtering working
- [ ] Full-text search returning relevant results

Include workflow: adw_plan_build_test_iso
```

---

### KP-008: Category & Tag Routes

**Title:** `[Kompass] Phase 3C: Category and Tag API Routes`

**Body:**
```markdown
## Context
**Project:** Kompass Portfolio & Quotation Automation System
**Current Phase:** Phase 3 of 13 - API Routes Part 1
**Current Issue:** KP-008 (Issue 8 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-006, KP-007, KP-009.

---

## Description
Implement FastAPI routes for categories and tags.

## Requirements

### File: apps/Server/app/api/category_routes.py

#### Category Endpoints
GET    /api/categories            - List as tree structure
POST   /api/categories            - Create category
GET    /api/categories/{id}       - Get category with children
PUT    /api/categories/{id}       - Update category
DELETE /api/categories/{id}       - Delete (fails if has products)
PUT    /api/categories/{id}/move  - Move to new parent

### File: apps/Server/app/api/tag_routes.py

#### Tag Endpoints
GET    /api/tags                  - List all tags with product counts
POST   /api/tags                  - Create tag
GET    /api/tags/{id}             - Get tag detail
PUT    /api/tags/{id}             - Update tag
DELETE /api/tags/{id}             - Delete tag (cascades)
GET    /api/tags/search           - Search for autocomplete

## Dependencies
- Phase 2 (KP-004) must be complete

## Acceptance Criteria
- [ ] Category tree returned correctly
- [ ] Category operations working
- [ ] Tag operations working
- [ ] Search autocomplete functional

Include workflow: adw_plan_build_test_iso
```

---

### KP-009: Data Extraction Routes

**Title:** `[Kompass] Phase 3D: Data Extraction API Routes`

**Body:**
```markdown
## Context
**Project:** Kompass Portfolio & Quotation Automation System
**Current Phase:** Phase 3 of 13 - API Routes Part 1
**Current Issue:** KP-009 (Issue 9 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-006, KP-007, KP-008.

---

## Description
Implement FastAPI routes for AI-powered data extraction.

## Requirements

### File: apps/Server/app/api/extraction_routes.py

#### Endpoints
POST   /api/extract/upload        - Upload file(s) for extraction
GET    /api/extract/{job_id}      - Get extraction job status
GET    /api/extract/{job_id}/results - Get extracted products
POST   /api/extract/{job_id}/confirm - Confirm and import products
POST   /api/extract/image/process - Process single image (background removal)
POST   /api/extract/hs-code/suggest - Suggest HS code for description

#### Upload Endpoint Details
- Accept: multipart/form-data
- Supported files: .pdf, .xlsx, .xls, .docx, .png, .jpg, .jpeg
- Max file size: 20MB
- Returns: job_id for async tracking

#### Extraction Job Response
```json
{
  "job_id": "uuid",
  "status": "processing" | "completed" | "failed",
  "progress": 75,
  "total_files": 3,
  "processed_files": 2,
  "extracted_products": [...],
  "errors": []
}
```

## Dependencies
- Phase 2 (KP-005) must be complete

## Acceptance Criteria
- [ ] File upload working
- [ ] Async job tracking functional
- [ ] Extraction results returned
- [ ] Import confirmation working
- [ ] HS code suggestion working

Include workflow: adw_plan_build_test_iso
```

---

**Phase 3 Parallel Execution:**
```bash
cd adws
uv run adw_plan_build_test_iso.py KP-006 &
uv run adw_plan_build_test_iso.py KP-007 &
uv run adw_plan_build_test_iso.py KP-008 &
uv run adw_plan_build_test_iso.py KP-009 &
wait
```

---

## Phase 4: Portfolio & Client Backend (3 Parallel)

### KP-010: Portfolio Service

**Title:** `[Kompass] Phase 4A: Portfolio Service`

**Body:**
```markdown
## Context
**Project:** Kompass Portfolio & Quotation Automation System
**Current Phase:** Phase 4 of 13 - Portfolio & Client Backend
**Current Issue:** KP-010 (Issue 10 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-011 and KP-012.

---

## Description
Implement portfolio service for curated product collections.

## Requirements

### File: apps/Server/app/services/portfolio_service.py

#### Core Methods
- `create_portfolio(request: CreatePortfolioDTO) -> PortfolioResponse`
- `get_portfolio(portfolio_id: UUID) -> PortfolioResponse` - With products
- `list_portfolios(filters, page, limit) -> PaginatedResponse`
- `update_portfolio(portfolio_id: UUID, request) -> PortfolioResponse`
- `delete_portfolio(portfolio_id: UUID) -> bool`
- `duplicate_portfolio(portfolio_id: UUID, new_name: str) -> PortfolioResponse`

#### Product Management
- `add_product_to_portfolio(portfolio_id: UUID, product_id: UUID, curator_notes: str) -> bool`
- `remove_product_from_portfolio(portfolio_id: UUID, product_id: UUID) -> bool`
- `reorder_products(portfolio_id: UUID, product_ids: List[UUID]) -> bool`

#### Portfolio Generation
- `create_from_filters(name: str, filters: ProductFilters) -> PortfolioResponse` - Auto-create from filter criteria
- `get_share_token(portfolio_id: UUID) -> str` - Generate public share link
- `get_by_share_token(token: str) -> PortfolioResponse` - Public access

## Dependencies
- Phase 3 must be complete

## Acceptance Criteria
- [ ] CRUD operations working
- [ ] Product management in portfolio working
- [ ] Share token generation working
- [ ] Auto-creation from filters working

Include workflow: adw_plan_build_test_iso
```

---

### KP-011: Client Service

**Title:** `[Kompass] Phase 4B: Client Service (CRM)`

**Body:**
```markdown
## Context
**Project:** Kompass Portfolio & Quotation Automation System
**Current Phase:** Phase 4 of 13 - Portfolio & Client Backend
**Current Issue:** KP-011 (Issue 11 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-010 and KP-012.

---

## Description
Implement client service for CRM functionality.

## Requirements

### File: apps/Server/app/services/client_service.py

#### Core Methods
- `create_client(request: CreateClientDTO) -> ClientResponse`
- `get_client(client_id: UUID) -> ClientResponse` - With quotation history
- `list_clients(filters, page, limit) -> PaginatedResponse`
- `update_client(client_id: UUID, request) -> ClientResponse`
- `delete_client(client_id: UUID) -> bool`

#### Pipeline Methods
- `get_pipeline() -> Dict[str, List[ClientResponse]]` - Grouped by status
- `update_status(client_id: UUID, new_status: str, notes: str) -> ClientResponse`
- `get_status_history(client_id: UUID) -> List[StatusChange]`

#### Filtering
- Filter by: status, niche_id, assigned_to, source, date_range
- Sort by: company_name, created_at, project_deadline

#### Business Rules
- Track status change history
- Validate project_deadline is in future
- Calculate timing feasibility (production + shipping vs deadline)

## Dependencies
- Phase 3 must be complete

## Acceptance Criteria
- [ ] CRUD operations working
- [ ] Pipeline grouping correct
- [ ] Status history tracking
- [ ] Timing validation working

Include workflow: adw_plan_build_test_iso
```

---

### KP-012: Niche Service

**Title:** `[Kompass] Phase 4C: Niche Service`

**Body:**
```markdown
## Context
**Project:** Kompass Portfolio & Quotation Automation System
**Current Phase:** Phase 4 of 13 - Portfolio & Client Backend
**Current Issue:** KP-012 (Issue 12 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-010 and KP-011.

---

## Description
Implement niche service for client type management.

## Requirements

### File: apps/Server/app/services/niche_service.py

#### Methods
- `create_niche(request: CreateNicheDTO) -> NicheResponse`
- `get_niche(niche_id: UUID) -> NicheResponse`
- `list_niches() -> List[NicheResponse]` - With client counts
- `update_niche(niche_id: UUID, request) -> NicheResponse`
- `delete_niche(niche_id: UUID) -> bool` - Fail if has clients

#### Default Niches (seed data)
- Constructoras
- Estudios de Arquitectura
- Desarrolladores
- Hoteles
- Operadores Rentas Cortas
- Retailers

## Dependencies
- Phase 3 must be complete

## Acceptance Criteria
- [ ] CRUD operations working
- [ ] Client counts accurate
- [ ] Delete validation working
- [ ] Seed data populated

Include workflow: adw_plan_build_test_iso
```

---

**Phase 4 Parallel Execution:**
```bash
cd adws
uv run adw_plan_build_test_iso.py KP-010 &
uv run adw_plan_build_test_iso.py KP-011 &
uv run adw_plan_build_test_iso.py KP-012 &
wait
```

---

## Phase 5: API Routes Part 2 (3 Parallel)

### KP-013: Portfolio Routes

**Title:** `[Kompass] Phase 5A: Portfolio API Routes`

**Body:**
```markdown
## Context
**Current Phase:** Phase 5 of 13 - API Routes Part 2
**Current Issue:** KP-013 (Issue 13 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-014 and KP-015.

---

## Description
Implement FastAPI routes for portfolio management.

## Requirements

### File: apps/Server/app/api/portfolio_routes.py

#### Endpoints
GET    /api/portfolios              - List portfolios
POST   /api/portfolios              - Create portfolio
GET    /api/portfolios/{id}         - Get portfolio with products
PUT    /api/portfolios/{id}         - Update portfolio
DELETE /api/portfolios/{id}         - Delete portfolio
POST   /api/portfolios/{id}/duplicate - Duplicate portfolio
POST   /api/portfolios/{id}/items   - Add product to portfolio
DELETE /api/portfolios/{id}/items/{product_id} - Remove product
PUT    /api/portfolios/{id}/items/reorder - Reorder products
GET    /api/portfolios/{id}/export/pdf - Generate PDF export
GET    /api/portfolios/share/{token} - Public portfolio view (no auth)

## Acceptance Criteria
- [ ] All endpoints functional
- [ ] PDF export generating
- [ ] Public share link working

Include workflow: adw_plan_build_test_iso
```

---

### KP-014: Client Routes

**Title:** `[Kompass] Phase 5B: Client API Routes`

**Body:**
```markdown
## Context
**Current Phase:** Phase 5 of 13 - API Routes Part 2
**Current Issue:** KP-014 (Issue 14 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-013 and KP-015.

---

## Description
Implement FastAPI routes for client management (CRM).

## Requirements

### File: apps/Server/app/api/client_routes.py

#### Endpoints
GET    /api/clients                 - List clients (paginated)
POST   /api/clients                 - Create client
GET    /api/clients/{id}            - Get client detail
PUT    /api/clients/{id}            - Update client
DELETE /api/clients/{id}            - Delete client
GET    /api/clients/pipeline        - Get pipeline (grouped by status)
PUT    /api/clients/{id}/status     - Update status
GET    /api/clients/{id}/history    - Get status change history
GET    /api/clients/{id}/quotations - Get client's quotations

## Acceptance Criteria
- [ ] All endpoints functional
- [ ] Pipeline grouping correct
- [ ] Status history working

Include workflow: adw_plan_build_test_iso
```

---

### KP-015: Niche Routes

**Title:** `[Kompass] Phase 5C: Niche API Routes`

**Body:**
```markdown
## Context
**Current Phase:** Phase 5 of 13 - API Routes Part 2
**Current Issue:** KP-015 (Issue 15 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-013 and KP-014.

---

## Description
Implement FastAPI routes for niche management.

## Requirements

### File: apps/Server/app/api/niche_routes.py

#### Endpoints
GET    /api/niches                  - List niches with client counts
POST   /api/niches                  - Create niche
GET    /api/niches/{id}             - Get niche detail
PUT    /api/niches/{id}             - Update niche
DELETE /api/niches/{id}             - Delete niche

## Acceptance Criteria
- [ ] All endpoints functional
- [ ] Client counts accurate

Include workflow: adw_plan_build_test_iso
```

---

**Phase 5 Parallel Execution:**
```bash
cd adws
uv run adw_plan_build_test_iso.py KP-013 &
uv run adw_plan_build_test_iso.py KP-014 &
uv run adw_plan_build_test_iso.py KP-015 &
wait
```

---

## Phase 6: Pricing & Quotation Backend (Sequential)

### KP-016: Pricing Configuration Service

**Title:** `[Kompass] Phase 6A: Pricing Configuration Service`

**Body:**
```markdown
## Context
**Current Phase:** Phase 6 of 13 - Pricing & Quotation Backend
**Current Issue:** KP-016 (Issue 16 of 33)
**Parallel Execution:** NO - KP-017 depends on this completing first.

---

## Description
Implement pricing configuration service for HS codes, freight rates, and settings.

## Requirements

### File: apps/Server/app/services/pricing_service.py

#### HS Code Methods
- `create_hs_code(request) -> HsCodeResponse`
- `get_hs_code(hs_code_id: UUID) -> HsCodeResponse`
- `list_hs_codes(search: str) -> List[HsCodeResponse]`
- `update_hs_code(hs_code_id: UUID, request) -> HsCodeResponse`
- `get_tariff_rate(hs_code: str) -> Decimal` - Get tariff % for code
- `search_hs_codes(query: str) -> List[HsCodeResponse]` - Search by code or description

#### Freight Rate Methods
- `create_freight_rate(request) -> FreightRateResponse`
- `list_freight_rates(origin: str, destination: str) -> List[FreightRateResponse]`
- `get_active_rate(origin: str, destination: str, container_type: str) -> FreightRateResponse`
- `update_freight_rate(rate_id: UUID, request) -> FreightRateResponse`
- `check_expired_rates() -> List[FreightRateResponse]` - Alert on expired

#### Pricing Settings Methods
- `get_setting(key: str) -> Decimal`
- `update_setting(key: str, value: Decimal, updated_by: UUID) -> PricingSettingResponse`
- `get_all_settings() -> Dict[str, Decimal]`

#### Default Settings
- `default_margin_percentage`: 20.0
- `inspection_cost_usd`: 150.0
- `insurance_percentage`: 1.5
- `nationalization_cost_cop`: 200000.0
- `exchange_rate_usd_cop`: 4200.0

## Acceptance Criteria
- [ ] HS code management working
- [ ] Freight rate management working
- [ ] Settings management working
- [ ] Search functionality working

Include workflow: adw_plan_build_test_iso
```

---

### KP-017: Quotation Service

**Title:** `[Kompass] Phase 6B: Quotation Service with Pricing Engine`

**Body:**
```markdown
## Context
**Current Phase:** Phase 6 of 13 - Pricing & Quotation Backend
**Current Issue:** KP-017 (Issue 17 of 33)
**Parallel Execution:** NO - Depends on KP-016 completing first.

---

## Description
Implement quotation service with automatic pricing calculation.

## Requirements

### File: apps/Server/app/services/quotation_service.py

#### Core Methods
- `create_quotation(request: CreateQuotationDTO) -> QuotationResponse`
- `get_quotation(quotation_id: UUID) -> QuotationResponse` - With line items
- `list_quotations(filters, page, limit) -> PaginatedResponse`
- `update_quotation(quotation_id: UUID, request) -> QuotationResponse`
- `delete_quotation(quotation_id: UUID) -> bool`
- `clone_quotation(quotation_id: UUID) -> QuotationResponse` - New version

#### Pricing Engine
- `calculate_pricing(quotation_id: UUID) -> QuotationPricing`:
```python
class QuotationPricing:
    subtotal_fob_usd: Decimal
    tariff_total_usd: Decimal
    freight_intl_usd: Decimal
    freight_national_cop: Decimal
    inspection_usd: Decimal
    insurance_usd: Decimal
    nationalization_cop: Decimal
    subtotal_before_margin_cop: Decimal
    margin_percentage: Decimal
    margin_cop: Decimal
    total_cop: Decimal
```

#### Pricing Formula
```
Total COP = (
    (Sum of line items FOB USD)
    + (Tariffs per HS code %)
    + (International freight)
    + (Inspection)
    + (Insurance %)
) × Exchange Rate
+ (National freight COP)
+ (Nationalization COP)
+ (Margin %)
```

#### Line Item Methods
- `add_item(quotation_id: UUID, item: QuotationItemDTO) -> QuotationItemResponse`
- `update_item(item_id: UUID, quantity: int) -> QuotationItemResponse`
- `remove_item(item_id: UUID) -> bool`

#### Status Workflow
- draft → sent → viewed → negotiating → accepted → rejected → expired
- `update_status(quotation_id: UUID, new_status: str) -> QuotationResponse`
- `validate_status_transition(current: str, new: str) -> bool`

## Dependencies
- KP-016 must be complete (pricing configuration)

## Acceptance Criteria
- [ ] CRUD operations working
- [ ] Pricing calculation accurate
- [ ] Line item management working
- [ ] Status transitions validated
- [ ] Cloning creates new version

Include workflow: adw_plan_build_test_iso model_set heavy
```

---

**Phase 6 Sequential Execution:**
```bash
cd adws
uv run adw_plan_build_test_iso.py KP-016
uv run adw_plan_build_test_iso.py KP-017
```

---

## Phase 7: Pricing & Quotation Routes (2 Parallel)

### KP-018: Pricing Routes

**Title:** `[Kompass] Phase 7A: Pricing Configuration API Routes`

**Body:**
```markdown
## Context
**Current Phase:** Phase 7 of 13 - Pricing & Quotation Routes
**Current Issue:** KP-018 (Issue 18 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-019.

---

## Description
Implement FastAPI routes for pricing configuration.

## Requirements

### File: apps/Server/app/api/pricing_routes.py

#### HS Code Endpoints
GET    /api/pricing/hs-codes         - List/search HS codes
POST   /api/pricing/hs-codes         - Create HS code
GET    /api/pricing/hs-codes/{id}    - Get HS code
PUT    /api/pricing/hs-codes/{id}    - Update HS code
DELETE /api/pricing/hs-codes/{id}    - Delete HS code

#### Freight Rate Endpoints
GET    /api/pricing/freight-rates    - List freight rates
POST   /api/pricing/freight-rates    - Create freight rate
PUT    /api/pricing/freight-rates/{id} - Update freight rate
DELETE /api/pricing/freight-rates/{id} - Delete freight rate
GET    /api/pricing/freight-rates/active - Get active rate for route

#### Settings Endpoints
GET    /api/pricing/settings         - Get all settings
PUT    /api/pricing/settings         - Update settings (admin only)

## Acceptance Criteria
- [ ] All endpoints functional
- [ ] Search working for HS codes
- [ ] Admin-only access for settings update

Include workflow: adw_plan_build_test_iso
```

---

### KP-019: Quotation Routes

**Title:** `[Kompass] Phase 7B: Quotation API Routes`

**Body:**
```markdown
## Context
**Current Phase:** Phase 7 of 13 - Pricing & Quotation Routes
**Current Issue:** KP-019 (Issue 19 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-018.

---

## Description
Implement FastAPI routes for quotation management.

## Requirements

### File: apps/Server/app/api/quotation_routes.py

#### Endpoints
GET    /api/quotations               - List quotations
POST   /api/quotations               - Create quotation
GET    /api/quotations/{id}          - Get quotation with items
PUT    /api/quotations/{id}          - Update quotation
DELETE /api/quotations/{id}          - Delete quotation
POST   /api/quotations/{id}/calculate - Recalculate pricing
POST   /api/quotations/{id}/clone    - Clone as new version
PUT    /api/quotations/{id}/status   - Update status
POST   /api/quotations/{id}/items    - Add line item
PUT    /api/quotations/{id}/items/{item_id} - Update line item
DELETE /api/quotations/{id}/items/{item_id} - Remove line item
GET    /api/quotations/{id}/export/pdf - Generate PDF proforma
POST   /api/quotations/{id}/send     - Send via email
GET    /api/quotations/share/{token} - Public quotation view (no auth)

## Acceptance Criteria
- [ ] All endpoints functional
- [ ] Pricing calculation working
- [ ] PDF export generating
- [ ] Email sending working
- [ ] Public share link working

Include workflow: adw_plan_build_test_iso
```

---

**Phase 7 Parallel Execution:**
```bash
cd adws
uv run adw_plan_build_test_iso.py KP-018 &
uv run adw_plan_build_test_iso.py KP-019 &
wait
```

---

## Phase 8: Frontend Foundation (Sequential)

### KP-020: Frontend Types & Service Layer

**Title:** `[Kompass] Phase 8: Frontend Types and API Service`

**Body:**
```markdown
## Context
**Current Phase:** Phase 8 of 13 - Frontend Foundation
**Current Issue:** KP-020 (Issue 20 of 33)
**Parallel Execution:** NO - Must complete before Phase 9-12 frontend work.

---

## Description
Create TypeScript types and API service layer for Kompass frontend.

## Requirements

### File: apps/Client/src/types/kompass.ts

```typescript
// Enums
export type SupplierStatus = 'active' | 'inactive';
export type ProductStatus = 'draft' | 'active' | 'discontinued';
export type ClientStatus = 'lead' | 'qualified' | 'quoting' | 'negotiating' | 'won' | 'lost';
export type QuotationStatus = 'draft' | 'sent' | 'viewed' | 'negotiating' | 'accepted' | 'rejected' | 'expired';
export type Incoterm = 'FOB' | 'CIF' | 'DDP';

// Interfaces
export interface Supplier { ... }
export interface Product { ... }
export interface Category { ... }
export interface Tag { ... }
export interface Portfolio { ... }
export interface Client { ... }
export interface Quotation { ... }
export interface QuotationItem { ... }
export interface HsCode { ... }
export interface FreightRate { ... }
export interface PricingSetting { ... }
// ... all required types
```

### File: apps/Client/src/services/kompassService.ts

```typescript
export const kompassService = {
  // Suppliers
  getSuppliers: (filters) => Promise<PaginatedResponse<Supplier>>,
  createSupplier: (data) => Promise<Supplier>,
  // ... all API methods for all modules
};
```

### Update: apps/Client/src/components/layout/Sidebar.tsx
- Add Kompass menu section with icons:
  - Dashboard
  - Suppliers
  - Products (Biblia General)
  - Portfolios
  - Clients
  - Quotations
  - Settings (Pricing, Categories)

### Update: apps/Client/src/App.tsx
- Add routes for all Kompass pages

## Acceptance Criteria
- [ ] All types defined matching backend DTOs
- [ ] Service methods for all endpoints
- [ ] Sidebar navigation added
- [ ] Routes configured
- [ ] TypeScript strict mode passing

Include workflow: adw_plan_build_iso
```

---

**Phase 8 Execution:**
```bash
cd adws
uv run adw_plan_build_iso.py KP-020
```

---

## Phase 9: Frontend Core Pages (4 Parallel)

### KP-021: Suppliers Page

**Title:** `[Kompass] Phase 9A: Suppliers Management Page`

**Body:**
```markdown
## Context
**Current Phase:** Phase 9 of 13 - Frontend Core Pages
**Current Issue:** KP-021 (Issue 21 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-022, KP-023, KP-024.

---

## Description
Create suppliers management page with list, create, and edit functionality.

## Requirements

### File: apps/Client/src/pages/kompass/SuppliersPage.tsx

#### Features
- Data table with columns: Name, Country, WeChat, Email, Status, Product Count, Actions
- Search bar with instant filtering
- Status filter dropdown
- "Add Supplier" button opening dialog form
- Edit action opening same dialog pre-filled
- Delete with confirmation
- Click row to see supplier detail with products

### File: apps/Client/src/components/kompass/SupplierForm.tsx
- Dialog form with fields: name, country, wechat_id, email, website, contact_person, phone, trade_fair_origin, notes
- Validation with react-hook-form
- Create and Edit modes

## Acceptance Criteria
- [ ] List rendering with all columns
- [ ] Search working
- [ ] Create form functional
- [ ] Edit form functional
- [ ] Delete with confirmation

Include workflow: adw_plan_build_iso
```

---

### KP-022: Products Catalog Page (Biblia General)

**Title:** `[Kompass] Phase 9B: Products Catalog Page (Biblia General)`

**Body:**
```markdown
## Context
**Current Phase:** Phase 9 of 13 - Frontend Core Pages
**Current Issue:** KP-022 (Issue 22 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-021, KP-023, KP-024.

---

## Description
Create the main products catalog page with grid and table views.

## Requirements

### File: apps/Client/src/pages/kompass/ProductsPage.tsx

#### Views
- **Grid View:** Product cards with image, name, SKU, price, supplier
- **Table View:** Data table with sortable columns
- Toggle between views

#### Filter Panel
- Supplier dropdown
- Category tree selector
- Price range slider
- MOQ range
- Tags multi-select
- Status dropdown
- Has images checkbox

#### Features
- Full-text search bar
- Pagination with page size selector
- Sort by dropdown
- "Add Product" button
- Bulk actions: Delete selected, Add to portfolio

### File: apps/Client/src/components/kompass/ProductCard.tsx
- Product image with fallback
- Name, SKU, price display
- Status badge
- Supplier link
- Quick actions (edit, delete, add to portfolio)

### File: apps/Client/src/components/kompass/ProductForm.tsx
- Multi-step form or tabbed:
  1. Basic info (name, SKU, description, supplier, category)
  2. Pricing (price_fob, moq, hs_code)
  3. Details (material, dimensions, weight, customizable, lead_time)
  4. Images (upload, drag-to-reorder, set primary)
  5. Tags (multi-select with autocomplete)

## Acceptance Criteria
- [ ] Grid view rendering
- [ ] Table view rendering
- [ ] All filters working
- [ ] Search working
- [ ] Create/edit form complete
- [ ] Image upload working

Include workflow: adw_plan_build_iso model_set heavy
```

---

### KP-023: Product Import Wizard

**Title:** `[Kompass] Phase 9C: Product Import Wizard`

**Body:**
```markdown
## Context
**Current Phase:** Phase 9 of 13 - Frontend Core Pages
**Current Issue:** KP-023 (Issue 23 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-021, KP-022, KP-024.

---

## Description
Create multi-step import wizard for AI-powered catalog extraction.

## Requirements

### File: apps/Client/src/pages/kompass/ImportWizardPage.tsx

#### Steps
1. **Upload:** Drag-and-drop zone for PDF/Excel/images, file list preview
2. **Processing:** Progress bar, extraction status, real-time updates
3. **Review:** Editable table of extracted products, validation errors highlighted, select/deselect products
4. **Confirm:** Summary of products to import, supplier selection, duplicate warnings

#### Features
- Step indicator with back/next navigation
- Cancel with confirmation
- Save draft functionality
- Batch validation before import

### File: apps/Client/src/components/kompass/ExtractedProductTable.tsx
- Editable cells for all fields
- Validation errors shown inline
- Row checkbox for selection
- Image preview
- Confidence score indicator

## Acceptance Criteria
- [ ] File upload working
- [ ] Processing progress displayed
- [ ] Review table editable
- [ ] Validation errors shown
- [ ] Import completing successfully

Include workflow: adw_plan_build_iso
```

---

### KP-024: Categories & Tags Page

**Title:** `[Kompass] Phase 9D: Categories and Tags Management Page`

**Body:**
```markdown
## Context
**Current Phase:** Phase 9 of 13 - Frontend Core Pages
**Current Issue:** KP-024 (Issue 24 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-021, KP-022, KP-023.

---

## Description
Create management page for product categories and tags.

## Requirements

### File: apps/Client/src/pages/kompass/CategoriesPage.tsx

#### Category Section
- Tree view with expand/collapse
- Drag-and-drop to reparent
- Add child button on each node
- Edit/delete actions
- Product count per category

#### Tag Section
- Tag chips with color
- Search/filter
- Create tag dialog (name, color picker)
- Edit/delete actions
- Product count per tag

### File: apps/Client/src/components/kompass/CategoryTree.tsx
- Recursive tree component
- Expand/collapse icons
- Drag-and-drop support with react-dnd

### File: apps/Client/src/components/kompass/TagChip.tsx
- Colored chip with name
- Delete icon on hover

## Acceptance Criteria
- [ ] Category tree rendering
- [ ] Drag-and-drop reparenting
- [ ] Tag management working
- [ ] Product counts accurate

Include workflow: adw_plan_build_iso
```

---

**Phase 9 Parallel Execution:**
```bash
cd adws
uv run adw_plan_build_iso.py KP-021 &
uv run adw_plan_build_iso.py KP-022 &
uv run adw_plan_build_iso.py KP-023 &
uv run adw_plan_build_iso.py KP-024 &
wait
```

---

## Phase 10: Frontend Portfolio & Clients (3 Parallel)

### KP-025: Portfolio Builder Page

**Title:** `[Kompass] Phase 10A: Portfolio Builder Page`

**Body:**
```markdown
## Context
**Current Phase:** Phase 10 of 13 - Frontend Portfolio & Clients
**Current Issue:** KP-025 (Issue 25 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-026 and KP-027.

---

## Description
Create interactive portfolio builder with product selection.

## Requirements

### File: apps/Client/src/pages/kompass/PortfolioBuilderPage.tsx

#### Layout (Two-column)
- **Left Panel (40%):** Product catalog mini-view with search and filters
- **Right Panel (60%):** Current portfolio with products, drag-to-reorder

#### Top Bar
- Portfolio name (editable)
- Niche selector dropdown
- Status toggle (draft/published)
- Save, Preview PDF, Copy share link buttons

#### Product Selection
- Click product in left panel to add to portfolio
- Drag products within portfolio to reorder
- Remove button on each portfolio item
- Curator notes input per item

### File: apps/Client/src/pages/kompass/PortfoliosListPage.tsx
- Grid of portfolio cards
- Card shows: name, niche, product count, status badge, cover image
- Actions: Open, Duplicate, Delete, Copy share link

## Acceptance Criteria
- [ ] Portfolio builder functional
- [ ] Product add/remove working
- [ ] Reorder working
- [ ] PDF preview generating
- [ ] Share link working

Include workflow: adw_plan_build_iso
```

---

### KP-026: Clients Pipeline Page

**Title:** `[Kompass] Phase 10B: Clients Pipeline Page (Kanban)`

**Body:**
```markdown
## Context
**Current Phase:** Phase 10 of 13 - Frontend Portfolio & Clients
**Current Issue:** KP-026 (Issue 26 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-025 and KP-027.

---

## Description
Create client pipeline page with Kanban board and list views.

## Requirements

### File: apps/Client/src/pages/kompass/ClientsPage.tsx

#### Kanban View (default)
- Columns: Lead → Qualified → Quoting → Negotiating → Won | Lost
- Cards with: Company name, contact, niche badge, project deadline, last activity
- Drag-and-drop between columns (updates status)
- Click card to open detail drawer

#### List View
- Data table with all client fields
- Toggle between Kanban and List

#### Client Detail Drawer
- All client information
- Edit button
- Quotation history
- Status change history
- Notes section

### File: apps/Client/src/components/kompass/ClientForm.tsx
- Dialog form for create/edit
- Fields: company_name, contact_name, email, phone, whatsapp, niche, project_name, project_deadline, incoterm_preference, source, notes

### File: apps/Client/src/components/kompass/ClientCard.tsx
- Compact card for Kanban
- Niche badge color-coded
- Deadline indicator (green if on track, red if near)

## Acceptance Criteria
- [ ] Kanban view rendering
- [ ] Drag-and-drop status change
- [ ] List view rendering
- [ ] Detail drawer functional
- [ ] Create/edit form working

Include workflow: adw_plan_build_iso
```

---

### KP-027: Niches Configuration Page

**Title:** `[Kompass] Phase 10C: Niches Configuration Page`

**Body:**
```markdown
## Context
**Current Phase:** Phase 10 of 13 - Frontend Portfolio & Clients
**Current Issue:** KP-027 (Issue 27 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-025 and KP-026.

---

## Description
Create niches configuration page for client type management.

## Requirements

### File: apps/Client/src/pages/kompass/NichesPage.tsx

#### Features
- Simple list/cards of niches
- Each shows: name, description, client count
- Add niche button
- Edit/delete actions
- Delete blocked if has clients

### File: apps/Client/src/components/kompass/NicheForm.tsx
- Dialog form with: name, description

## Acceptance Criteria
- [ ] List rendering
- [ ] Create/edit working
- [ ] Delete validation

Include workflow: adw_plan_build_iso
```

---

**Phase 10 Parallel Execution:**
```bash
cd adws
uv run adw_plan_build_iso.py KP-025 &
uv run adw_plan_build_iso.py KP-026 &
uv run adw_plan_build_iso.py KP-027 &
wait
```

---

## Phase 11: Frontend Quotation (2 Parallel)

### KP-028: Quotation Creator Page

**Title:** `[Kompass] Phase 11A: Quotation Creator Page`

**Body:**
```markdown
## Context
**Current Phase:** Phase 11 of 13 - Frontend Quotation
**Current Issue:** KP-028 (Issue 28 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-029.

---

## Description
Create comprehensive quotation creator with live pricing calculation.

## Requirements

### File: apps/Client/src/pages/kompass/QuotationCreatorPage.tsx

#### Steps/Sections
1. **Client Selection:** Search existing or create new, show project timing validation
2. **Product Selection:** Browse Biblia General or select from Portfolio, add to quote
3. **Line Items:** Table with product, quantity (editable), unit price, line total
4. **Pricing Panel:** Live calculation showing all cost components
5. **Summary:** Grand total in COP, payment terms, validity period, notes

#### Line Items Table
- Product image thumbnail
- Product name/SKU
- Quantity input
- Unit FOB price (editable override)
- HS code
- Line total
- Remove button

#### Pricing Panel (right sidebar)
- Subtotal FOB USD
- Tariffs breakdown
- International freight
- National freight
- Inspection
- Insurance
- Nationalization
- Margin %
- **Total COP** (highlighted)

#### Actions
- Save Draft
- Calculate (refresh pricing)
- Preview PDF
- Send via Email
- Copy share link

### File: apps/Client/src/pages/kompass/QuotationsListPage.tsx
- Data table of quotations
- Columns: Quote #, Client, Total COP, Status, Created, Valid Until, Actions
- Status badges color-coded
- Filter by status, client, date range

## Acceptance Criteria
- [ ] Client selection working
- [ ] Product selection working
- [ ] Live pricing calculation
- [ ] PDF preview generating
- [ ] Email sending functional

Include workflow: adw_plan_build_iso model_set heavy
```

---

### KP-029: Pricing Configuration Page

**Title:** `[Kompass] Phase 11B: Pricing Configuration Page`

**Body:**
```markdown
## Context
**Current Phase:** Phase 11 of 13 - Frontend Quotation
**Current Issue:** KP-029 (Issue 29 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-028.

---

## Description
Create pricing configuration page for HS codes, freight rates, and settings.

## Requirements

### File: apps/Client/src/pages/kompass/PricingConfigPage.tsx

#### Tabs
1. **HS Codes:** Searchable table, create/edit dialog, columns: Code, Description, Tariff %
2. **Freight Rates:** Table with origin, destination, container type, rate, validity
3. **Settings:** Form with default margin, inspection cost, insurance %, etc.

#### HS Code Search
- Instant search by code or description
- Add new code button

#### Freight Rate Management
- Filter by origin/destination
- Highlight expired rates
- Add new rate button

#### Settings Form
- Number inputs with validation
- Exchange rate (USD to COP)
- Save button with confirmation

## Acceptance Criteria
- [ ] HS codes management working
- [ ] Freight rates management working
- [ ] Settings save working
- [ ] Expired rate warnings shown

Include workflow: adw_plan_build_iso
```

---

**Phase 11 Parallel Execution:**
```bash
cd adws
uv run adw_plan_build_iso.py KP-028 &
uv run adw_plan_build_iso.py KP-029 &
wait
```

---

## Phase 12: Dashboard & Export (2 Parallel)

### KP-030: Dashboard with KPIs

**Title:** `[Kompass] Phase 12A: Dashboard with KPIs`

**Body:**
```markdown
## Context
**Current Phase:** Phase 12 of 13 - Dashboard & Export
**Current Issue:** KP-030 (Issue 30 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-031.

---

## Description
Create main dashboard with key performance indicators.

## Requirements

### File: apps/Client/src/pages/kompass/DashboardPage.tsx

#### KPI Cards (top row)
- Total Products in Biblia General
- Products Added This Month
- Active Suppliers
- Quotations Sent This Week
- Pipeline Value (sum of quoting + negotiating)

#### Charts
- Quotations by Status (pie chart)
- Quotations Trend (line chart - sent vs accepted over time)
- Top Products Quoted (bar chart)

#### Recent Activity
- Latest products added
- Latest quotations sent
- Latest clients added

#### Quick Actions
- Add Product button
- Create Quotation button
- Import Catalog button

## Acceptance Criteria
- [ ] All KPIs displaying correct values
- [ ] Charts rendering
- [ ] Activity feed showing recent items
- [ ] Quick actions working

Include workflow: adw_plan_build_iso
```

---

### KP-031: PDF Generation & Export

**Title:** `[Kompass] Phase 12B: PDF Generation Service`

**Body:**
```markdown
## Context
**Current Phase:** Phase 12 of 13 - Dashboard & Export
**Current Issue:** KP-031 (Issue 31 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-030.

---

## Description
Implement PDF generation for portfolios and quotations.

## Requirements

### File: apps/Server/app/services/pdf_service.py

#### Portfolio PDF
- Cover page with portfolio name, niche, Kompass branding
- Product pages with image, name, SKU, description
- QR code linking to digital version
- Page numbers

#### Quotation PDF (Proforma Invoice)
- Company header with logo
- Client information
- Quotation number, date, validity
- Product table with images, quantities, prices
- Pricing breakdown
- Payment terms
- Footer with contact info

### Templates
- Use WeasyPrint or ReportLab
- HTML/CSS templates for layouts
- Company branding assets

### File: apps/Server/app/api/pdf_routes.py
- GET /api/portfolios/{id}/pdf - Generate portfolio PDF
- GET /api/quotations/{id}/pdf - Generate proforma PDF

## Acceptance Criteria
- [ ] Portfolio PDF generating correctly
- [ ] Quotation PDF generating correctly
- [ ] Branding applied
- [ ] QR codes working
- [ ] Performance acceptable (<10 seconds)

Include workflow: adw_plan_build_test_iso
```

---

**Phase 12 Parallel Execution:**
```bash
cd adws
uv run adw_plan_build_iso.py KP-030 &
uv run adw_plan_build_test_iso.py KP-031 &
wait
```

---

## Phase 13: Testing & Documentation (2 Parallel)

### KP-032: E2E Tests

**Title:** `[Kompass] Phase 13A: End-to-End Test Suite`

**Body:**
```markdown
## Context
**Current Phase:** Phase 13 of 13 - Testing & Documentation (FINAL PHASE)
**Current Issue:** KP-032 (Issue 32 of 33)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-033.

---

## Description
Create comprehensive E2E test suite for Kompass module.

## Requirements

### Test Scenarios

#### Supplier Flow
1. Create supplier
2. Update supplier
3. List and filter suppliers
4. Delete supplier

#### Product Flow
1. Create product with images and tags
2. Bulk import from Excel
3. Search products
4. Filter by category, price, tags

#### Portfolio Flow
1. Create portfolio
2. Add products
3. Reorder products
4. Generate PDF
5. Share via link

#### Quotation Flow
1. Select client
2. Add products
3. Calculate pricing
4. Generate proforma PDF
5. Send via email

### Test Files
- apps/Server/tests/test_kompass/
  - test_supplier_service.py
  - test_product_service.py
  - test_portfolio_service.py
  - test_quotation_service.py
  - test_pricing_service.py
  - test_api_routes.py

## Acceptance Criteria
- [ ] All test scenarios passing
- [ ] Coverage > 80%
- [ ] Tests run in < 5 minutes
- [ ] No flaky tests

Include workflow: adw_plan_build_test_iso model_set heavy
```

---

### KP-033: Documentation

**Title:** `[Kompass] Phase 13B: Documentation and CLAUDE.md Update`

**Body:**
```markdown
## Context
**Current Phase:** Phase 13 of 13 - Testing & Documentation (FINAL PHASE)
**Current Issue:** KP-033 (Issue 33 of 33 - FINAL ISSUE)
**Parallel Execution:** YES - Runs IN PARALLEL with KP-032.

---

## Description
Create documentation and update CLAUDE.md with Kompass module information.

## Requirements

### File: ai_docs/KOMPASS_MODULE_GUIDE.md
1. Module overview
2. Architecture diagram
3. API endpoint reference
4. Database schema
5. Pricing formula explanation
6. Configuration options
7. Deployment notes

### File: ai_docs/KOMPASS_USER_GUIDE.md
1. Supplier management guide
2. Product catalog (Biblia General) guide
3. Portfolio creation guide
4. Quotation workflow guide
5. Pricing configuration guide

### Update: CLAUDE.md
- Add Kompass module section
- Document new routes and services
- Add new slash commands if applicable
- Update project structure

### UI Polish Checklist
- Consistent spacing
- Loading skeletons
- Empty states
- Error messages
- Mobile responsiveness

## Acceptance Criteria
- [ ] Technical documentation complete
- [ ] User guide complete
- [ ] CLAUDE.md updated
- [ ] UI consistent and polished

Include workflow: adw_plan_build_document_iso
```

---

**Phase 13 Parallel Execution:**
```bash
cd adws
uv run adw_plan_build_test_iso.py KP-032 &
uv run adw_plan_build_document_iso.py KP-033 &
wait
```

---

## Complete Execution Script

Save as `adws/run_kompass_implementation.sh`:

```bash
#!/bin/bash
# Kompass Portfolio & Quotation System - Parallel ADW Execution
# Usage: ./run_kompass_implementation.sh

set -e
cd "$(dirname "$0")"

echo "=========================================="
echo "Kompass Portfolio & Quotation System"
echo "=========================================="

# Phase 1: Foundation (Sequential)
echo ""
echo "=== PHASE 1: Foundation ==="
uv run adw_plan_build_test_iso.py KP-001
echo "Phase 1 complete."

# Phase 2: Backend Core Services (4 parallel)
echo ""
echo "=== PHASE 2: Backend Core Services (4 parallel) ==="
uv run adw_plan_build_test_iso.py KP-002 &
uv run adw_plan_build_test_iso.py KP-003 &
uv run adw_plan_build_test_iso.py KP-004 &
uv run adw_plan_build_test_iso.py KP-005 &
wait
echo "Phase 2 complete."

# Phase 3: API Routes Part 1 (4 parallel)
echo ""
echo "=== PHASE 3: API Routes Part 1 (4 parallel) ==="
uv run adw_plan_build_test_iso.py KP-006 &
uv run adw_plan_build_test_iso.py KP-007 &
uv run adw_plan_build_test_iso.py KP-008 &
uv run adw_plan_build_test_iso.py KP-009 &
wait
echo "Phase 3 complete."

# Phase 4: Portfolio & Client Backend (3 parallel)
echo ""
echo "=== PHASE 4: Portfolio & Client Backend (3 parallel) ==="
uv run adw_plan_build_test_iso.py KP-010 &
uv run adw_plan_build_test_iso.py KP-011 &
uv run adw_plan_build_test_iso.py KP-012 &
wait
echo "Phase 4 complete."

# Phase 5: API Routes Part 2 (3 parallel)
echo ""
echo "=== PHASE 5: API Routes Part 2 (3 parallel) ==="
uv run adw_plan_build_test_iso.py KP-013 &
uv run adw_plan_build_test_iso.py KP-014 &
uv run adw_plan_build_test_iso.py KP-015 &
wait
echo "Phase 5 complete."

# Phase 6: Pricing & Quotation Backend (Sequential)
echo ""
echo "=== PHASE 6: Pricing & Quotation Backend (Sequential) ==="
uv run adw_plan_build_test_iso.py KP-016
uv run adw_plan_build_test_iso.py KP-017
echo "Phase 6 complete."

# Phase 7: Pricing & Quotation Routes (2 parallel)
echo ""
echo "=== PHASE 7: Pricing & Quotation Routes (2 parallel) ==="
uv run adw_plan_build_test_iso.py KP-018 &
uv run adw_plan_build_test_iso.py KP-019 &
wait
echo "Phase 7 complete."

# Phase 8: Frontend Foundation (Sequential)
echo ""
echo "=== PHASE 8: Frontend Foundation ==="
uv run adw_plan_build_iso.py KP-020
echo "Phase 8 complete."

# Phase 9: Frontend Core (4 parallel)
echo ""
echo "=== PHASE 9: Frontend Core (4 parallel) ==="
uv run adw_plan_build_iso.py KP-021 &
uv run adw_plan_build_iso.py KP-022 &
uv run adw_plan_build_iso.py KP-023 &
uv run adw_plan_build_iso.py KP-024 &
wait
echo "Phase 9 complete."

# Phase 10: Frontend Portfolio & Clients (3 parallel)
echo ""
echo "=== PHASE 10: Frontend Portfolio & Clients (3 parallel) ==="
uv run adw_plan_build_iso.py KP-025 &
uv run adw_plan_build_iso.py KP-026 &
uv run adw_plan_build_iso.py KP-027 &
wait
echo "Phase 10 complete."

# Phase 11: Frontend Quotation (2 parallel)
echo ""
echo "=== PHASE 11: Frontend Quotation (2 parallel) ==="
uv run adw_plan_build_iso.py KP-028 &
uv run adw_plan_build_iso.py KP-029 &
wait
echo "Phase 11 complete."

# Phase 12: Dashboard & Export (2 parallel)
echo ""
echo "=== PHASE 12: Dashboard & Export (2 parallel) ==="
uv run adw_plan_build_iso.py KP-030 &
uv run adw_plan_build_test_iso.py KP-031 &
wait
echo "Phase 12 complete."

# Phase 13: Testing & Documentation (2 parallel)
echo ""
echo "=== PHASE 13: Testing & Documentation (2 parallel) ==="
uv run adw_plan_build_test_iso.py KP-032 &
uv run adw_plan_build_document_iso.py KP-033 &
wait
echo "Phase 13 complete."

echo ""
echo "=========================================="
echo "Kompass Implementation Complete!"
echo "=========================================="
```

---

## Files Summary

### Backend Files to Create
```
apps/Server/database/schema.sql (append)
apps/Server/app/models/kompass_dto.py
apps/Server/app/repository/kompass_repository.py
apps/Server/app/services/
├── supplier_service.py
├── product_service.py
├── category_service.py
├── tag_service.py
├── extraction_service.py
├── portfolio_service.py
├── client_service.py
├── niche_service.py
├── pricing_service.py
├── quotation_service.py
└── pdf_service.py
apps/Server/app/api/
├── supplier_routes.py
├── product_routes.py
├── category_routes.py
├── tag_routes.py
├── extraction_routes.py
├── portfolio_routes.py
├── client_routes.py
├── niche_routes.py
├── pricing_routes.py
├── quotation_routes.py
└── pdf_routes.py
apps/Server/tests/test_kompass/
```

### Frontend Files to Create
```
apps/Client/src/types/kompass.ts
apps/Client/src/services/kompassService.ts
apps/Client/src/pages/kompass/
├── DashboardPage.tsx
├── SuppliersPage.tsx
├── ProductsPage.tsx
├── ImportWizardPage.tsx
├── CategoriesPage.tsx
├── PortfoliosListPage.tsx
├── PortfolioBuilderPage.tsx
├── ClientsPage.tsx
├── NichesPage.tsx
├── QuotationsListPage.tsx
├── QuotationCreatorPage.tsx
└── PricingConfigPage.tsx
apps/Client/src/components/kompass/
├── SupplierForm.tsx
├── ProductCard.tsx
├── ProductForm.tsx
├── ExtractedProductTable.tsx
├── CategoryTree.tsx
├── TagChip.tsx
├── ClientForm.tsx
├── ClientCard.tsx
├── NicheForm.tsx
└── ...
```

### Files to Modify
```
apps/Server/main.py                           # Register routers
apps/Client/src/App.tsx                       # Add routes
apps/Client/src/components/layout/Sidebar.tsx # Add menu items
CLAUDE.md                                     # Update with module docs
```

---

## Issue Labels

For GitHub issues, use these labels:
- `kompass` - All Kompass module issues
- `backend` - Backend-only issues
- `frontend` - Frontend-only issues
- `database` - Schema changes
- `ai` - AI integration issues
- `phase-1` through `phase-13` - Phase grouping
- `parallel-safe` - Can run in parallel with others in same phase
