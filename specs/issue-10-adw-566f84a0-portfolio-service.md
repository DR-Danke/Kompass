# Feature: Portfolio Service for Curated Product Collections

## Metadata
issue_number: `10`
adw_id: `566f84a0`
issue_json: `{"number":10,"title":"[Kompass] Phase 4A: Portfolio Service","body":"## Context\n**Project:** Kompass Portfolio & Quotation Automation System\n**Current Phase:** Phase 4 of 13 - Portfolio & Client Backend\n**Current Issue:** KP-010 (Issue 10 of 33)\n**Parallel Execution:** YES - Runs IN PARALLEL with KP-011 and KP-012.\n\n---\n\n## Description\nImplement portfolio service for curated product collections.\n\n## Requirements\n\n### File: apps/Server/app/services/portfolio_service.py\n\n#### Core Methods\n- `create_portfolio(request: CreatePortfolioDTO) -> PortfolioResponse`\n- `get_portfolio(portfolio_id: UUID) -> PortfolioResponse` - With products\n- `list_portfolios(filters, page, limit) -> PaginatedResponse`\n- `update_portfolio(portfolio_id: UUID, request) -> PortfolioResponse`\n- `delete_portfolio(portfolio_id: UUID) -> bool`\n- `duplicate_portfolio(portfolio_id: UUID, new_name: str) -> PortfolioResponse`\n\n#### Product Management\n- `add_product_to_portfolio(portfolio_id: UUID, product_id: UUID, curator_notes: str) -> bool`\n- `remove_product_from_portfolio(portfolio_id: UUID, product_id: UUID) -> bool`\n- `reorder_products(portfolio_id: UUID, product_ids: List[UUID]) -> bool`\n\n#### Portfolio Generation\n- `create_from_filters(name: str, filters: ProductFilters) -> PortfolioResponse` - Auto-create from filter criteria\n- `get_share_token(portfolio_id: UUID) -> str` - Generate public share link\n- `get_by_share_token(token: str) -> PortfolioResponse` - Public access\n\n## Acceptance Criteria\n- [ ] CRUD operations working\n- [ ] Product management in portfolio working\n- [ ] Share token generation working\n- [ ] Auto-creation from filters working"}`

## Feature Description
Implement a comprehensive portfolio service layer for the Kompass Portfolio & Quotation System. This service manages curated product collections that can be shared with clients. Portfolios allow sales teams to assemble product selections tailored to specific client niches, generate shareable links for client review, and automatically create portfolios based on product filter criteria.

The service builds on top of the existing PortfolioRepository (already implemented in `kompass_repository.py`) and adds business logic for portfolio duplication, product reordering, auto-creation from filters, and secure share token generation for public access.

## User Story
As a sales manager or curator
I want to create and manage curated product portfolios
So that I can share tailored product selections with clients and streamline the quotation process

## Problem Statement
The Kompass system has a repository layer for portfolios but lacks a service layer to handle business logic such as:
- Duplicating portfolios with a new name
- Reordering products within a portfolio
- Auto-generating portfolios from product filter criteria
- Creating secure share tokens for public portfolio access
- Retrieving portfolios via share tokens without authentication

## Solution Statement
Create a `PortfolioService` class in `apps/Server/app/services/portfolio_service.py` that:
1. Wraps the existing `PortfolioRepository` with business logic
2. Implements all CRUD operations with proper DTO mapping
3. Adds portfolio duplication functionality
4. Implements product reordering with sort_order management
5. Provides auto-creation from product filters using the existing ProductRepository
6. Generates JWT-based share tokens for secure public access
7. Supports retrieving portfolios via share tokens without authentication

The service will follow the same patterns established by `SupplierService` and `ProductService`.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/app/repository/kompass_repository.py` - Contains the existing `PortfolioRepository` class (lines 2158-2469) with basic CRUD, `add_item`, `remove_item`, and `_get_portfolio_items` methods. The service will extend this with business logic.
- `apps/Server/app/models/kompass_dto.py` - Contains existing DTOs including `PortfolioCreateDTO`, `PortfolioUpdateDTO`, `PortfolioResponseDTO`, `PortfolioListResponseDTO`, `PortfolioItemCreateDTO`, `PortfolioItemResponseDTO`, `ProductFilterDTO`, and `PaginationDTO`. May need to add share token DTOs.
- `apps/Server/app/services/supplier_service.py` - Reference implementation for service layer patterns (singleton pattern, DTO mapping, error handling, logging conventions).
- `apps/Server/app/services/product_service.py` - Reference implementation for product filtering, pagination, and bulk operations.
- `apps/Server/app/api/product_routes.py` - Reference implementation for API route patterns (authentication, RBAC, error handling).
- `apps/Server/app/api/dependencies.py` - Contains `get_current_user` dependency for JWT authentication.
- `apps/Server/app/api/rbac_dependencies.py` - Contains `require_roles` dependency for role-based access control.
- `apps/Server/main.py` - Main FastAPI application where new router will be registered.
- `apps/Server/tests/services/test_supplier_service.py` - Reference for unit test patterns using pytest and mocking.

### New Files
- `apps/Server/app/services/portfolio_service.py` - New portfolio service implementation
- `apps/Server/app/api/portfolio_routes.py` - New portfolio API routes
- `apps/Server/tests/services/test_portfolio_service.py` - Unit tests for portfolio service
- `apps/Server/tests/api/test_portfolio_routes.py` - API route tests

## Implementation Plan

### Phase 1: Foundation
1. Add any missing DTOs to `kompass_dto.py` for share token functionality
2. Extend `PortfolioRepository` with methods for share token storage/retrieval and product reordering
3. Create the base `PortfolioService` class with CRUD operations

### Phase 2: Core Implementation
1. Implement product management methods (add, remove, reorder)
2. Implement portfolio duplication
3. Implement auto-creation from product filters
4. Implement share token generation and retrieval

### Phase 3: Integration
1. Create API routes with proper authentication and RBAC
2. Register routes in main.py
3. Write comprehensive unit tests
4. Run validation commands

## Step by Step Tasks

### Step 1: Extend DTOs for Share Token Functionality
- Add `PortfolioShareTokenDTO` with fields: `token: str`, `portfolio_id: UUID`, `expires_at: Optional[datetime]`
- Add `PortfolioPublicResponseDTO` for public access (omit sensitive fields if needed)
- Add `PortfolioFilterDTO` for list filtering (niche_id, is_active, search)
- Add `ReorderProductsRequestDTO` with fields: `product_ids: List[UUID]`

### Step 2: Extend PortfolioRepository with Additional Methods
- Add `update_item_sort_order(portfolio_id: UUID, product_id: UUID, sort_order: int) -> bool` method
- Add `update_items_sort_orders(portfolio_id: UUID, items: List[Tuple[UUID, int]]) -> bool` for batch reorder
- Add `get_by_name(name: str) -> Optional[Dict]` for checking duplicate names
- Add `search(query: str, limit: int = 50) -> List[Dict]` for portfolio search
- Add optional `share_token` column handling if not exists in schema (store in portfolios table or new table)

### Step 3: Create Portfolio Service with Core CRUD Operations
- Create `apps/Server/app/services/portfolio_service.py`
- Implement `__init__` method with repository injection pattern (following `SupplierService`)
- Implement `_map_to_response_dto` helper method
- Implement `_map_item_to_response_dto` helper method
- Implement `create_portfolio(request: PortfolioCreateDTO) -> Optional[PortfolioResponseDTO]`
- Implement `get_portfolio(portfolio_id: UUID) -> Optional[PortfolioResponseDTO]`
- Implement `list_portfolios(filters, page, limit) -> PortfolioListResponseDTO`
- Implement `update_portfolio(portfolio_id: UUID, request: PortfolioUpdateDTO) -> Optional[PortfolioResponseDTO]`
- Implement `delete_portfolio(portfolio_id: UUID) -> bool`
- Create singleton instance `portfolio_service`

### Step 4: Implement Portfolio Duplication
- Implement `duplicate_portfolio(portfolio_id: UUID, new_name: str) -> Optional[PortfolioResponseDTO]`
- Copy all portfolio items with their notes and sort_order
- Validate that new_name doesn't already exist
- Return the newly created portfolio with all items

### Step 5: Implement Product Management Methods
- Implement `add_product_to_portfolio(portfolio_id: UUID, product_id: UUID, curator_notes: Optional[str] = None) -> bool`
- Implement `remove_product_from_portfolio(portfolio_id: UUID, product_id: UUID) -> bool`
- Implement `reorder_products(portfolio_id: UUID, product_ids: List[UUID]) -> bool`
  - Validate all product_ids exist in portfolio
  - Update sort_order based on list position
  - Use batch update for efficiency

### Step 6: Implement Auto-Creation from Product Filters
- Implement `create_from_filters(name: str, filters: ProductFilterDTO, description: Optional[str] = None, niche_id: Optional[UUID] = None) -> Optional[PortfolioResponseDTO]`
- Query products using existing ProductRepository with filters
- Create new portfolio and add all matching products
- Set sort_order based on product order from query

### Step 7: Implement Share Token Functionality
- Implement `get_share_token(portfolio_id: UUID) -> Optional[str]`
  - Generate JWT-based token with portfolio_id payload
  - Token should include expiration (configurable, default 30 days)
  - Store token in portfolio metadata or separate tracking
- Implement `get_by_share_token(token: str) -> Optional[PortfolioResponseDTO]`
  - Validate and decode JWT token
  - Return portfolio if valid and not expired
  - This method should NOT require authentication

### Step 8: Create Portfolio API Routes
- Create `apps/Server/app/api/portfolio_routes.py`
- `GET /portfolios` - List portfolios with pagination and filters (requires auth)
- `POST /portfolios` - Create portfolio (requires admin/manager role)
- `GET /portfolios/search` - Search portfolios (requires auth)
- `GET /portfolios/{portfolio_id}` - Get portfolio by ID (requires auth)
- `PUT /portfolios/{portfolio_id}` - Update portfolio (requires admin/manager role)
- `DELETE /portfolios/{portfolio_id}` - Soft delete portfolio (requires admin/manager role)
- `POST /portfolios/{portfolio_id}/duplicate` - Duplicate portfolio (requires admin/manager role)
- `POST /portfolios/{portfolio_id}/products/{product_id}` - Add product to portfolio (requires admin/manager role)
- `DELETE /portfolios/{portfolio_id}/products/{product_id}` - Remove product from portfolio (requires admin/manager role)
- `PUT /portfolios/{portfolio_id}/products/reorder` - Reorder products (requires admin/manager role)
- `POST /portfolios/{portfolio_id}/share` - Generate share token (requires admin/manager role)
- `GET /portfolios/shared/{token}` - Get portfolio by share token (PUBLIC - no auth)
- `POST /portfolios/from-filters` - Create portfolio from product filters (requires admin/manager role)

### Step 9: Register Routes in main.py
- Import portfolio_routes router
- Add `app.include_router(portfolio_router, prefix="/api/portfolios")`

### Step 10: Create Unit Tests for Portfolio Service
- Create `apps/Server/tests/services/test_portfolio_service.py`
- Test `create_portfolio` with mocked repository
- Test `get_portfolio` found and not found cases
- Test `list_portfolios` with pagination and filters
- Test `update_portfolio` success and not found cases
- Test `delete_portfolio` success and not found cases
- Test `duplicate_portfolio` with items copied
- Test `add_product_to_portfolio` and `remove_product_from_portfolio`
- Test `reorder_products` with validation
- Test `create_from_filters` integration
- Test `get_share_token` token generation
- Test `get_by_share_token` with valid and expired tokens

### Step 11: Create API Route Tests
- Create `apps/Server/tests/api/test_portfolio_routes.py`
- Test all endpoints with authentication mocking
- Test RBAC enforcement for admin/manager routes
- Test public share token endpoint without auth
- Test error cases (404, 400, 403)

### Step 12: Run Validation Commands
- Run all tests and ensure they pass
- Run linting and type checking
- Verify build succeeds

## Testing Strategy

### Unit Tests
- Mock `PortfolioRepository` to isolate service logic
- Mock `ProductRepository` for filter-based creation tests
- Test all DTO mapping functions
- Test JWT token generation and validation
- Test edge cases: empty portfolios, duplicate names, invalid product IDs

### Edge Cases
- Duplicate portfolio with empty items list
- Reorder products with invalid product_id not in portfolio
- Create from filters with no matching products
- Share token expired
- Share token for non-existent portfolio
- Adding product already in portfolio (should update, not duplicate)
- Deleting portfolio that doesn't exist
- Listing portfolios with no results

## Acceptance Criteria
- [ ] `create_portfolio` creates a new portfolio and returns it with all items
- [ ] `get_portfolio` returns a portfolio with all products loaded
- [ ] `list_portfolios` returns paginated list with filters working
- [ ] `update_portfolio` updates name, description, niche_id, is_active
- [ ] `delete_portfolio` performs soft delete (sets is_active=False)
- [ ] `duplicate_portfolio` creates copy with new name and all items
- [ ] `add_product_to_portfolio` adds product with optional curator notes
- [ ] `remove_product_from_portfolio` removes product from portfolio
- [ ] `reorder_products` updates sort_order for all products in order
- [ ] `create_from_filters` creates portfolio with products matching filters
- [ ] `get_share_token` generates valid JWT token for portfolio
- [ ] `get_by_share_token` returns portfolio for valid token (no auth required)
- [ ] All API endpoints properly enforce authentication and RBAC
- [ ] Public share endpoint works without authentication
- [ ] All unit tests pass
- [ ] All API tests pass

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && source .venv/bin/activate && .venv/bin/ruff check .` - Run linting to check for code style issues
- `cd apps/Server && source .venv/bin/activate && .venv/bin/pytest tests/services/test_portfolio_service.py -v --tb=short` - Run portfolio service unit tests
- `cd apps/Server && source .venv/bin/activate && .venv/bin/pytest tests/api/test_portfolio_routes.py -v --tb=short` - Run portfolio API route tests
- `cd apps/Server && source .venv/bin/activate && .venv/bin/pytest tests/ -v --tb=short` - Run all Server tests to validate zero regressions
- `cd apps/Client && npm run typecheck` - Run Client type check to validate zero regressions
- `cd apps/Client && npm run build` - Run Client build to validate zero regressions

## Notes
- The PortfolioRepository already exists with basic CRUD and item management methods. The service layer adds business logic on top.
- JWT tokens for share links should use the same JWT library (`python-jose`) already used for authentication.
- The share token secret should use `JWT_SECRET_KEY` from settings or a dedicated `PORTFOLIO_SHARE_SECRET` env var.
- Consider adding token expiration configuration via environment variable (e.g., `PORTFOLIO_SHARE_TOKEN_EXPIRE_DAYS=30`).
- The `create_from_filters` method should respect product status (only include active products).
- Portfolio items use `sort_order` field for ordering - the reorder method should update these values sequentially (0, 1, 2, ...).
- This feature runs in parallel with KP-011 (Client Service) and KP-012 (Pricing Service) - avoid conflicts with shared files like `main.py`.
