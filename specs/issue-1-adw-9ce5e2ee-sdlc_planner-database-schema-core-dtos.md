# Feature: Database Schema and Core DTOs for Kompass Portfolio & Quotation System

## Metadata
issue_number: `1`
adw_id: `9ce5e2ee`
issue_json: `{"number":1,"title":"[Kompass] Phase 1: Database Schema and Core DTOs","body":"..."}`

## Feature Description
Create the foundational database schema and core DTOs for the Kompass Portfolio & Quotation Automation System. This system automates portfolio creation and quotation generation for a China sourcing/trading business. The system handles suppliers, products (Biblia General), curated portfolios, clients, and complex pricing with tariffs/freight.

This is Phase 1 of 13 (Foundation) and must be completed first as it creates the database schema and core types that all other issues depend on.

## User Story
As a system administrator
I want to have a robust database schema and DTO layer for the Kompass system
So that the subsequent phases can build upon a solid foundation for supplier management, product catalogs, portfolios, clients, and quotations

## Problem Statement
The Kompass system requires a comprehensive database structure to manage:
- Supplier registry with Chinese vendors
- Master product database (Biblia General) with categories, tags, and images
- Curated product portfolios for different client segments (niches)
- Client/prospect registry
- Complex pricing including HS codes, freight rates, and global settings
- Quotation generation with line items

Without this foundational schema and DTOs, no application features can be built.

## Solution Statement
Implement 15 database tables with proper constraints, indexes, and foreign key relationships. Create comprehensive Pydantic DTOs for all entities including enums, request/response models, and pagination support. Build base repository classes following the existing pattern in `user_repository.py`.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/database/schema.sql` - Existing schema file to append new Kompass tables. Contains the `users` table and `update_updated_at_column()` trigger function.
- `apps/Server/app/models/auth_dto.py` - Reference for DTO patterns using Pydantic BaseModel with `model_config = {"from_attributes": True}`.
- `apps/Server/app/repository/user_repository.py` - Reference for repository pattern using `get_database_connection()` and `close_database_connection()`, singleton instances.
- `apps/Server/app/config/database.py` - Database connection utilities to be used in repositories.

### New Files
- `apps/Server/app/models/kompass_dto.py` - All Kompass DTOs (enums, requests, responses, pagination)
- `apps/Server/app/repository/kompass_repository.py` - All Kompass repositories (Supplier, Product, Portfolio, Client, Quotation)

## Implementation Plan

### Phase 1: Foundation
1. Design the database schema with all 15 tables following the existing pattern
2. Ensure proper use of UUID primary keys with `gen_random_uuid()`
3. Include audit fields (created_at, updated_at) with auto-update triggers
4. Use DECIMAL for monetary values (not FLOAT)

### Phase 2: Core Implementation
1. Create all DTOs with proper Pydantic validation
2. Define enums for status fields
3. Implement request/response patterns matching existing code
4. Add pagination support for list operations

### Phase 3: Integration
1. Build repository classes following the singleton pattern
2. Implement CRUD operations for each entity
3. Add filtering capabilities for products and quotations

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create Database Schema - Core Reference Tables
Append to `apps/Server/database/schema.sql`:
- `niches` table - Client types (constructor, architect, hotel, retailer, etc.)
- `categories` table - Hierarchical product categories with parent_id self-reference
- `tags` table - Flexible product tagging system
- `hs_codes` table - Tariff classification codes

### Step 2: Create Database Schema - Supplier and Product Tables
- `suppliers` table with status enum, contact info, audit fields
- `products` table with foreign keys to suppliers and categories, DECIMAL pricing
- `product_images` table with sort_order for gallery
- `product_tags` junction table for many-to-many relationship

### Step 3: Create Database Schema - Portfolio Tables
- `portfolios` table with niche_id foreign key
- `portfolio_items` junction table linking portfolios to products

### Step 4: Create Database Schema - Client and Pricing Tables
- `clients` table with contact info and status
- `freight_rates` table with origin/destination and DECIMAL rates
- `pricing_settings` table for global pricing parameters (markup percentages, etc.)

### Step 5: Create Database Schema - Quotation Tables
- `quotations` table with client_id, status, totals, validity period
- `quotation_items` table with product details, quantities, pricing breakdown

### Step 6: Create Auto-Update Triggers for All Tables
- Create `update_<table>_updated_at` triggers for each table with `updated_at` column

### Step 7: Create DTOs - Enums
Create `apps/Server/app/models/kompass_dto.py`:
- `SupplierStatus` enum (active, inactive, pending_review)
- `ProductStatus` enum (active, inactive, draft, discontinued)
- `ClientStatus` enum (active, inactive, prospect)
- `QuotationStatus` enum (draft, sent, accepted, rejected, expired)
- `Incoterm` enum (FOB, CIF, EXW, DDP, etc.)

### Step 8: Create DTOs - Supplier Models
- `SupplierCreateDTO` - Request for creating suppliers
- `SupplierUpdateDTO` - Request for updating suppliers
- `SupplierResponseDTO` - Response with full supplier data
- `SupplierListResponseDTO` - Paginated list response

### Step 9: Create DTOs - Product Models
- `ProductCreateDTO` - Request with category_id, supplier_id, pricing
- `ProductUpdateDTO` - Request for updates
- `ProductResponseDTO` - Full product with category/supplier info
- `ProductListResponseDTO` - Paginated with filter metadata
- `ProductImageDTO` - Image gallery item
- `ProductFilterDTO` - Filtering parameters

### Step 10: Create DTOs - Portfolio Models
- `PortfolioCreateDTO` - Request with niche_id and initial items
- `PortfolioUpdateDTO` - Request for updates
- `PortfolioResponseDTO` - Full portfolio with items
- `PortfolioItemDTO` - Item within portfolio
- `PortfolioListResponseDTO` - Paginated list

### Step 11: Create DTOs - Client Models
- `ClientCreateDTO` - Request for creating clients
- `ClientUpdateDTO` - Request for updates
- `ClientResponseDTO` - Full client data
- `ClientListResponseDTO` - Paginated list

### Step 12: Create DTOs - Quotation Models
- `QuotationCreateDTO` - Request with items array
- `QuotationUpdateDTO` - Request for updates
- `QuotationResponseDTO` - Full quotation with calculated totals
- `QuotationItemDTO` - Line item with pricing breakdown
- `QuotationListResponseDTO` - Paginated list

### Step 13: Create DTOs - Supporting Models
- `NicheResponseDTO` - Niche reference data
- `CategoryResponseDTO` - Category with parent hierarchy
- `TagResponseDTO` - Tag reference data
- `HSCodeResponseDTO` - HS code with duty rates
- `FreightRateResponseDTO` - Freight rate data
- `PricingSettingsResponseDTO` - Global pricing config
- `PaginationDTO` - Pagination metadata (page, limit, total, pages)

### Step 14: Create Repository - Base Classes and Supplier Repository
Create `apps/Server/app/repository/kompass_repository.py`:
- `SupplierRepository` class with:
  - `create()` - Insert new supplier
  - `get_by_id()` - Get single supplier
  - `get_all()` - List with pagination
  - `update()` - Update supplier
  - `delete()` - Soft delete (set inactive)
- Singleton instance `supplier_repository`

### Step 15: Create Repository - Product Repository
- `ProductRepository` class with:
  - `create()` - Insert with image handling
  - `get_by_id()` - Get with category/supplier joins
  - `get_all()` - List with filters (category, supplier, status, price range)
  - `update()` - Update product
  - `delete()` - Soft delete
  - `add_tag()` / `remove_tag()` - Tag management
  - `add_image()` / `remove_image()` - Image management
- Singleton instance `product_repository`

### Step 16: Create Repository - Portfolio Repository
- `PortfolioRepository` class with:
  - `create()` - Insert portfolio with items
  - `get_by_id()` - Get with items and products
  - `get_all()` - List with pagination
  - `update()` - Update portfolio metadata
  - `add_item()` / `remove_item()` - Item management
- Singleton instance `portfolio_repository`

### Step 17: Create Repository - Client Repository
- `ClientRepository` class with:
  - `create()` - Insert new client
  - `get_by_id()` - Get single client
  - `get_by_email()` - Lookup by email
  - `get_all()` - List with pagination and filtering
  - `update()` - Update client
  - `delete()` - Soft delete
- Singleton instance `client_repository`

### Step 18: Create Repository - Quotation Repository
- `QuotationRepository` class with:
  - `create()` - Insert quotation with items
  - `get_by_id()` - Get with items and client info
  - `get_by_client()` - List quotations for a client
  - `get_all()` - List with pagination and filters
  - `update_status()` - Change quotation status
  - `recalculate_totals()` - Recalculate from items
- Singleton instance `quotation_repository`

### Step 19: Create Repository - Reference Data Repositories
- `NicheRepository` - CRUD for niches
- `CategoryRepository` - CRUD with hierarchy support
- `TagRepository` - CRUD for tags
- `HSCodeRepository` - CRUD for HS codes
- `FreightRateRepository` - CRUD for freight rates
- `PricingSettingsRepository` - Get/Update global settings
- Singleton instances for each

### Step 20: Run Validation Commands
Execute all validation commands to ensure the implementation is correct.

## Testing Strategy

### Unit Tests
- Test all DTO validation rules (required fields, field types, enums)
- Test repository CRUD operations with mock database
- Test pagination calculations
- Test filter logic in ProductRepository

### Edge Cases
- Empty string handling for optional fields
- UUID validation for foreign keys
- DECIMAL precision for monetary values
- Hierarchical category queries (parent/child)
- Quotation total recalculation with various item combinations

## Acceptance Criteria
- [ ] All 15 database tables created with proper constraints and indexes
- [ ] Foreign key relationships established between all related tables
- [ ] All enums defined (SupplierStatus, ProductStatus, ClientStatus, QuotationStatus, Incoterm)
- [ ] All request DTOs have Pydantic validation
- [ ] All response DTOs have `model_config = {"from_attributes": True}`
- [ ] All list responses include pagination metadata
- [ ] Base repository classes implemented following existing patterns
- [ ] All repositories have singleton instances
- [ ] Database migration runs successfully (psql schema.sql)
- [ ] Python syntax is valid (no import errors)
- [ ] Ruff linting passes

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/9ce5e2ee/apps/Server && source .venv/bin/activate && python -c "from app.models.kompass_dto import *; print('DTOs imported successfully')"` - Verify DTO imports work
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/9ce5e2ee/apps/Server && source .venv/bin/activate && python -c "from app.repository.kompass_repository import *; print('Repositories imported successfully')"` - Verify repository imports work
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/9ce5e2ee/apps/Server && .venv/bin/ruff check .` - Run ruff linting
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/9ce5e2ee/apps/Server && .venv/bin/pytest tests/ -v --tb=short` - Run existing tests

## Notes
- This is Phase 1 of 13 and must be completed FIRST as all other phases depend on this schema
- After this issue, Phase 2 begins with 4 parallel backend service implementations (KP-002, KP-003, KP-004, KP-005)
- Follow existing patterns from `auth_dto.py` and `user_repository.py`
- Use DECIMAL(12,2) for monetary values to handle prices up to 9,999,999,999.99
- All status fields should use VARCHAR with CHECK constraints matching enum values
- Include indexes on frequently queried columns (foreign keys, status, email)
- The repository layer uses raw SQL with psycopg2 (no ORM)
