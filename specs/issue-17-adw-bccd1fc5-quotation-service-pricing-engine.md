# Feature: Quotation Service with Pricing Engine

## Metadata
issue_number: `17`
adw_id: `bccd1fc5`
issue_json: `{"number":17,"title":"[Kompass] Phase 6B: Quotation Service with Pricing Engine"}`

## Feature Description
Implement a comprehensive quotation service that provides full CRUD operations for quotations with an integrated pricing engine. The service will automatically calculate pricing based on FOB costs, tariffs (HS codes), international/national freight, inspection, insurance, nationalization costs, and configurable margins. It includes support for line item management, status workflow transitions, and quotation cloning functionality.

This feature builds upon the pricing configuration service (KP-016) which provides HS code tariffs, freight rates, and global pricing settings. The quotation service will consume these configurations to perform real-time pricing calculations.

## User Story
As a sales user
I want to create and manage quotations with automatic pricing calculations
So that I can quickly generate accurate quotes for clients with all import costs properly calculated

## Problem Statement
Currently there is no service layer to manage quotations in the Kompass system. While the database schema and repository layer exist for quotations and quotation items, there is no business logic layer to:
- Coordinate quotation lifecycle management
- Calculate comprehensive pricing including tariffs, freight, insurance, and margins
- Validate status transitions
- Clone quotations for new versions
- Manage line items with proper pricing recalculation

## Solution Statement
Create a `QuotationService` class that:
1. Provides full CRUD operations for quotations with validation
2. Implements a pricing engine that calculates total costs using the formula:
   `Total COP = (FOB USD + Tariffs + International Freight + Inspection + Insurance) × Exchange Rate + National Freight COP + Nationalization COP + Margin`
3. Manages line items with automatic tariff and pricing calculations
4. Enforces status workflow transitions
5. Supports quotation cloning for creating new versions
6. Exposes REST API endpoints for all operations

## Relevant Files
Use these files to implement the feature:

### Existing Files to Read/Understand
- `apps/Server/app/services/pricing_service.py` - Dependency: provides HS code tariffs, freight rates, and pricing settings
- `apps/Server/app/services/client_service.py` - Pattern reference for service structure, validation, and DTO mapping
- `apps/Server/app/repository/kompass_repository.py` - Lines 3772-4284: Existing QuotationRepository with CRUD and item management
- `apps/Server/app/models/kompass_dto.py` - Lines 915-1095: Existing quotation DTOs (QuotationStatus, QuotationCreateDTO, QuotationResponseDTO, etc.)
- `apps/Server/app/api/client_routes.py` - Pattern reference for REST endpoint structure
- `apps/Server/database/schema.sql` - Lines 305-365: Quotation and quotation_items table schemas
- `apps/Server/main.py` - Router registration pattern
- `apps/Server/tests/services/test_pricing_service.py` - Test pattern reference
- `.claude/commands/test_e2e.md` - E2E test execution reference
- `.claude/commands/e2e/test_basic_query.md` - E2E test file pattern reference

### Files to Modify
- `apps/Server/app/services/__init__.py` - Add quotation_service export
- `apps/Server/main.py` - Register quotation_routes router
- `apps/Server/app/models/kompass_dto.py` - Add new DTOs for pricing calculation and extended status workflow

### New Files
- `apps/Server/app/services/quotation_service.py` - Main quotation service implementation
- `apps/Server/app/api/quotation_routes.py` - REST API endpoints
- `apps/Server/tests/services/test_quotation_service.py` - Unit tests for quotation service
- `apps/Server/tests/api/test_quotation_routes.py` - API integration tests

## Implementation Plan

### Phase 1: Foundation - DTOs and Schema Updates
Extend the existing DTOs to support the pricing engine requirements and the full status workflow. The database schema already supports the core quotation structure, but we need additional DTOs for pricing calculation results.

Key additions:
- `QuotationPricingDTO` - For pricing calculation results with all cost components
- Extended `QuotationStatus` enum to include 'viewed' and 'negotiating' states
- `QuotationStatusTransitionDTO` - For status change requests
- `QuotationCloneDTO` - For clone requests

### Phase 2: Core Implementation - Quotation Service
Build the service layer following existing patterns from `client_service.py` and `pricing_service.py`:
- Constructor with optional repository injection for testing
- CRUD methods (create, get, list, update, delete)
- Pricing engine with comprehensive cost calculation
- Line item management methods
- Status workflow validation and transitions
- Clone functionality

### Phase 3: Integration - API Routes
Create REST endpoints following the pattern from `client_routes.py`:
- Standard CRUD endpoints with proper authentication
- Pricing calculation endpoint
- Line item management endpoints
- Status update endpoint
- Clone endpoint

## Step by Step Tasks

### Step 1: Add Pricing DTOs
- Read `apps/Server/app/models/kompass_dto.py` to understand existing patterns
- Add `QuotationPricingDTO` class with the following fields:
  - `subtotal_fob_usd: Decimal` - Sum of line items FOB
  - `tariff_total_usd: Decimal` - Total tariff amount
  - `freight_intl_usd: Decimal` - International freight cost
  - `freight_national_cop: Decimal` - National freight in COP
  - `inspection_usd: Decimal` - Inspection cost
  - `insurance_usd: Decimal` - Insurance cost
  - `nationalization_cop: Decimal` - Nationalization cost
  - `subtotal_before_margin_cop: Decimal` - Subtotal before margin
  - `margin_percentage: Decimal` - Applied margin percentage
  - `margin_cop: Decimal` - Margin amount in COP
  - `total_cop: Decimal` - Final total in COP
  - `exchange_rate: Decimal` - Exchange rate used
- Add `QuotationStatusTransitionDTO` for status changes
- Extend `QuotationStatus` enum with VIEWED and NEGOTIATING values
- Update database schema CHECK constraint to include new statuses

### Step 2: Create Quotation Service
- Create `apps/Server/app/services/quotation_service.py`
- Import dependencies: `pricing_service`, `quotation_repository`, DTOs
- Implement `QuotationService` class with:
  - `__init__(self, repository=None)` - Repository injection pattern
  - `create_quotation(request: QuotationCreateDTO, created_by: UUID) -> QuotationResponseDTO`
  - `get_quotation(quotation_id: UUID) -> Optional[QuotationResponseDTO]`
  - `list_quotations(filters: QuotationFilterDTO, page: int, limit: int) -> QuotationListResponseDTO`
  - `update_quotation(quotation_id: UUID, request: QuotationUpdateDTO) -> Optional[QuotationResponseDTO]`
  - `delete_quotation(quotation_id: UUID) -> bool`
  - `clone_quotation(quotation_id: UUID, created_by: UUID) -> Optional[QuotationResponseDTO]`
- Add singleton export: `quotation_service = QuotationService()`

### Step 3: Implement Pricing Engine
- Add pricing engine methods to `QuotationService`:
  - `calculate_pricing(quotation_id: UUID) -> Optional[QuotationPricingDTO]`
    - Get quotation with items
    - Sum line item FOB costs
    - Look up tariff rates for each item using `pricing_service.get_tariff_rate()`
    - Get freight rate using `pricing_service.get_active_rate()`
    - Get pricing settings using `pricing_service.get_all_settings()`
    - Apply pricing formula
  - `_calculate_line_item_pricing(item: QuotationItemResponseDTO) -> Dict` - Calculate per-item costs
  - `recalculate_quotation(quotation_id: UUID) -> Optional[QuotationResponseDTO]` - Recalculate and update totals

### Step 4: Implement Line Item Management
- Add line item methods to `QuotationService`:
  - `add_item(quotation_id: UUID, item: QuotationItemCreateDTO) -> Optional[QuotationItemResponseDTO]`
  - `update_item(item_id: UUID, request: QuotationItemUpdateDTO) -> Optional[QuotationItemResponseDTO]`
  - `remove_item(item_id: UUID) -> bool`
- Ensure each method triggers pricing recalculation

### Step 5: Implement Status Workflow
- Add status workflow methods to `QuotationService`:
  - `validate_status_transition(current_status: str, new_status: str) -> bool`
    - Define valid transitions: draft→sent, sent→viewed, viewed→negotiating, negotiating→accepted/rejected, any→expired
  - `update_status(quotation_id: UUID, new_status: QuotationStatus) -> Optional[QuotationResponseDTO]`
    - Validate transition
    - Update status via repository
    - Log status change
- Create `STATUS_TRANSITIONS` constant mapping valid transitions

### Step 6: Create API Routes
- Create `apps/Server/app/api/quotation_routes.py`
- Import dependencies and create router
- Implement endpoints:
  - `GET /quotations` - List with pagination and filters
  - `POST /quotations` - Create quotation
  - `GET /quotations/{id}` - Get by ID
  - `PUT /quotations/{id}` - Update quotation
  - `DELETE /quotations/{id}` - Delete quotation (admin/manager only)
  - `POST /quotations/{id}/clone` - Clone quotation
  - `GET /quotations/{id}/pricing` - Calculate pricing
  - `PUT /quotations/{id}/status` - Update status
  - `POST /quotations/{id}/items` - Add line item
  - `PUT /quotations/items/{item_id}` - Update line item
  - `DELETE /quotations/items/{item_id}` - Remove line item
- Add proper authentication using `get_current_user` and `require_roles`

### Step 7: Register Routes
- Add import in `apps/Server/main.py`: `from app.api.quotation_routes import router as quotation_router`
- Add router registration: `app.include_router(quotation_router, prefix="/api/quotations")`
- Update `apps/Server/app/services/__init__.py` to export `quotation_service`

### Step 8: Create Unit Tests for Service
- Create `apps/Server/tests/services/test_quotation_service.py`
- Add fixtures for mock quotations, items, and pricing data
- Test cases:
  - `test_create_quotation_success`
  - `test_create_quotation_with_items`
  - `test_get_quotation_found`
  - `test_get_quotation_not_found`
  - `test_list_quotations_with_filters`
  - `test_update_quotation_success`
  - `test_delete_quotation_success`
  - `test_clone_quotation_success`
  - `test_calculate_pricing_formula`
  - `test_add_item_triggers_recalculation`
  - `test_remove_item_triggers_recalculation`
  - `test_valid_status_transition`
  - `test_invalid_status_transition`
  - `test_update_status_success`
  - `test_update_status_invalid_transition`

### Step 9: Create API Integration Tests
- Create `apps/Server/tests/api/test_quotation_routes.py`
- Test all endpoints with authentication
- Test error cases (404, 400, 403)
- Test pagination and filtering

### Step 10: Update Database Migration
- Create migration to update quotations status CHECK constraint to include 'viewed' and 'negotiating'
- This is necessary because the issue requires: draft → sent → viewed → negotiating → accepted → rejected → expired

### Step 11: Run Validation Commands
- Execute all validation commands to ensure zero regressions
- Run linting, type checks, unit tests, and build

## Testing Strategy

### Unit Tests
- Mock repository and pricing_service dependencies
- Test each service method in isolation
- Verify pricing calculations with known values
- Test status transition validation logic
- Test clone creates proper copy with new version

### Edge Cases
- Empty quotation (no line items) pricing calculation
- Invalid status transition attempts
- Non-existent quotation operations
- Missing pricing configuration (HS code not found, no active freight rate)
- Zero quantity line items
- Maximum/minimum decimal values
- Cloning quotation with many items
- Concurrent updates (handled by database transactions)

## Acceptance Criteria
- [ ] CRUD operations working - create, get, list, update, delete quotations
- [ ] Pricing calculation accurate - follows formula: Total COP = (FOB + Tariffs + Freight + Inspection + Insurance) × Exchange Rate + National Freight + Nationalization + Margin
- [ ] Line item management working - add, update, remove items with automatic recalculation
- [ ] Status transitions validated - only valid transitions allowed (draft→sent→viewed→negotiating→accepted/rejected/expired)
- [ ] Cloning creates new version - creates copy with new quotation number and draft status
- [ ] All unit tests pass
- [ ] All API integration tests pass
- [ ] No linting errors
- [ ] No type check errors
- [ ] Build succeeds

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Run linting
cd apps/Server && .venv/bin/ruff check app/services/quotation_service.py app/api/quotation_routes.py

# Run type checking (if mypy is available)
cd apps/Server && .venv/bin/python -m mypy app/services/quotation_service.py --ignore-missing-imports || true

# Run quotation service unit tests
cd apps/Server && .venv/bin/pytest tests/services/test_quotation_service.py -v --tb=short

# Run quotation routes integration tests
cd apps/Server && .venv/bin/pytest tests/api/test_quotation_routes.py -v --tb=short

# Run all Server tests to ensure no regressions
cd apps/Server && .venv/bin/pytest tests/ -v --tb=short

# Run Client type check
cd apps/Client && npm run typecheck

# Run Client build
cd apps/Client && npm run build
```

## Notes

### Pricing Formula Details
The pricing engine implements the following formula:

```
Total COP = (
    Sum of line items FOB USD
    + Tariffs per HS code %
    + International freight USD
    + Inspection USD
    + Insurance % of (FOB + Freight)
) × Exchange Rate USD/COP
+ National freight COP
+ Nationalization COP
+ Margin %
```

Where:
- FOB = sum of (unit_price × quantity) for all line items
- Tariffs = sum of (line FOB × tariff_percent) for each item based on HS code
- Insurance = (FOB + Int'l Freight) × insurance_percentage
- Margin = subtotal_before_margin × margin_percentage

### Status Workflow
Valid status transitions:
- `draft` → `sent` (when quote is sent to client)
- `sent` → `viewed` (when client opens quote)
- `viewed` → `negotiating` (when client responds with questions/counter)
- `negotiating` → `accepted` (client accepts)
- `negotiating` → `rejected` (client rejects)
- `sent` → `accepted` (direct accept without negotiation)
- `sent` → `rejected` (direct reject without viewing)
- Any status → `expired` (when valid_until date passes)

### Dependencies
- Depends on KP-016 (Pricing Configuration Service) being complete
- Uses `pricing_service.get_tariff_rate()` for HS code lookups
- Uses `pricing_service.get_active_rate()` for freight lookups
- Uses `pricing_service.get_all_settings()` for margin, insurance, exchange rate

### Repository Layer
The existing `QuotationRepository` (lines 3772-4284 in kompass_repository.py) provides:
- `create()` with auto-generated quotation number (QT-XXXXXX)
- `get_by_id()` with items included
- `get_all()` with filters (client_id, status, created_by, date range, search)
- `update_status()`
- `recalculate_totals()` - sums line items and applies costs
- `add_item()` / `remove_item()`

The service layer will coordinate these repository methods with business logic validation and pricing engine integration.
