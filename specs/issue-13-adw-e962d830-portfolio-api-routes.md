# Feature: Portfolio API Routes Implementation

## Metadata
issue_number: `13`
adw_id: `e962d830`
issue_json: `{"number":13,"title":"[Kompass] Phase 5A: Portfolio API Routes","body":"## Context\n**Current Phase:** Phase 5 of 13 - API Routes Part 2\n**Current Issue:** KP-013 (Issue 13 of 33)\n**Parallel Execution:** YES - Runs IN PARALLEL with KP-014 and KP-015.\n\n---\n\n## Description\nImplement FastAPI routes for portfolio management.\n\n## Requirements\n\n### File: apps/Server/app/api/portfolio_routes.py\n\n#### Endpoints\n- GET    /api/portfolios              - List portfolios\n- POST   /api/portfolios              - Create portfolio\n- GET    /api/portfolios/{id}         - Get portfolio with products\n- PUT    /api/portfolios/{id}         - Update portfolio\n- DELETE /api/portfolios/{id}         - Delete portfolio\n- POST   /api/portfolios/{id}/duplicate - Duplicate portfolio\n- POST   /api/portfolios/{id}/items   - Add product to portfolio\n- DELETE /api/portfolios/{id}/items/{product_id} - Remove product\n- PUT    /api/portfolios/{id}/items/reorder - Reorder products\n- GET    /api/portfolios/{id}/export/pdf - Generate PDF export\n- GET    /api/portfolios/share/{token} - Public portfolio view (no auth)\n\n## Acceptance Criteria\n- [ ] All endpoints functional\n- [ ] PDF export generating\n- [ ] Public share link working"}`

## Feature Description
This feature completes the Portfolio API Routes implementation for the Kompass Portfolio & Quotation System. The portfolio routes enable sales teams to manage curated product collections that can be shared with clients. The implementation adds PDF export functionality and aligns the route paths with the specification.

Most of the portfolio CRUD and product management endpoints are already implemented. This plan focuses on:
1. Adding the missing PDF export endpoint
2. Adding alternative route paths for `/items` endpoints (for specification compliance)
3. Ensuring the public share endpoint follows the specified path pattern

## User Story
As a sales manager
I want to export portfolios as PDF documents and share them with clients via public links
So that I can present curated product selections professionally to potential buyers

## Problem Statement
The current portfolio routes implementation is missing the PDF export functionality specified in the requirements. Additionally, the route paths for product management use `/products` instead of the specified `/items` path pattern, and the public share route uses `/shared/{token}` instead of `/share/{token}`.

## Solution Statement
Implement the missing PDF export endpoint using a PDF generation library (reportlab or weasyprint), and add alias routes for the `/items` path pattern to ensure specification compliance while maintaining backward compatibility with existing `/products` routes.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/app/api/portfolio_routes.py` - Main portfolio API routes file that needs the PDF export endpoint and alias routes
- `apps/Server/app/services/portfolio_service.py` - Portfolio service layer that may need PDF generation method
- `apps/Server/app/models/kompass_dto.py` - DTOs for portfolio operations (existing DTOs are sufficient)
- `apps/Server/app/repository/kompass_repository.py` - Portfolio repository for data access (existing methods are sufficient)
- `apps/Server/main.py` - Main app entry point where portfolio router is registered
- `apps/Server/requirements.txt` - Dependencies file for adding PDF library
- `apps/Server/app/api/dependencies.py` - Authentication dependencies
- `apps/Server/app/api/rbac_dependencies.py` - RBAC dependencies for route protection
- `apps/Server/tests/api/test_portfolio_routes.py` - Existing API tests that need new test cases
- `apps/Server/tests/services/test_portfolio_service.py` - Existing service tests that may need new test cases

### New Files
- None - all changes will be made to existing files

## Implementation Plan

### Phase 1: Foundation - PDF Library Setup
Add the PDF generation library to dependencies and create the service method for PDF generation. The PDF should include:
- Portfolio name and description
- List of products with their names, SKUs, and pricing information
- Product images (if available)
- Generation timestamp

### Phase 2: Core Implementation - PDF Export Endpoint
Implement the PDF export endpoint that:
- Accepts portfolio ID as path parameter
- Retrieves the portfolio with all products
- Generates a formatted PDF document
- Returns the PDF as a downloadable file with appropriate content-type headers

### Phase 3: Integration - Route Path Aliases
Add alias routes for the `/items` path pattern to maintain specification compliance:
- POST `/api/portfolios/{id}/items` → Add product to portfolio
- DELETE `/api/portfolios/{id}/items/{product_id}` → Remove product from portfolio
- PUT `/api/portfolios/{id}/items/reorder` → Reorder products in portfolio
- GET `/api/portfolios/share/{token}` → Public portfolio view (alias for `/shared/{token}`)

## Step by Step Tasks

### Step 1: Add PDF Library Dependency
- Open `apps/Server/requirements.txt`
- Add `reportlab>=4.0.0` for PDF generation (lightweight, pure Python library)
- This library is suitable for generating product catalog-style PDFs

### Step 2: Create PDF Generation Method in Portfolio Service
- Open `apps/Server/app/services/portfolio_service.py`
- Add a new method `generate_pdf(portfolio_id: UUID) -> Optional[bytes]` that:
  - Retrieves the portfolio with all products
  - Creates a PDF document with portfolio details
  - Includes product listing with names, SKUs, and prices
  - Returns the PDF as bytes or None if portfolio not found

### Step 3: Implement PDF Export Endpoint
- Open `apps/Server/app/api/portfolio_routes.py`
- Add endpoint `GET /{portfolio_id}/export/pdf`:
  - Requires authentication (any authenticated user can export)
  - Calls `portfolio_service.generate_pdf()`
  - Returns StreamingResponse with `application/pdf` content type
  - Sets Content-Disposition header for file download
  - Returns 404 if portfolio not found

### Step 4: Add Alias Routes for /items Path Pattern
- Open `apps/Server/app/api/portfolio_routes.py`
- Add alias endpoint `POST /{portfolio_id}/items` that calls the same handler as `/{portfolio_id}/products/{product_id}`
  - Note: The items endpoint takes product_id in the request body, not the path
- Add alias endpoint `DELETE /{portfolio_id}/items/{product_id}` pointing to same handler
- Add alias endpoint `PUT /{portfolio_id}/items/reorder` pointing to same handler
- Add alias endpoint `GET /share/{token}` pointing to same handler as `/shared/{token}`

### Step 5: Add Unit Tests for PDF Export
- Open `apps/Server/tests/api/test_portfolio_routes.py`
- Add new test class `TestPdfExport` with tests:
  - `test_export_pdf_success` - Test successful PDF generation
  - `test_export_pdf_not_found` - Test 404 for non-existent portfolio
  - `test_export_pdf_requires_auth` - Test authentication is required

### Step 6: Add Unit Tests for Alias Routes
- Open `apps/Server/tests/api/test_portfolio_routes.py`
- Add test cases for the `/items` path aliases:
  - `test_add_item_via_items_endpoint` - Test POST /items
  - `test_remove_item_via_items_endpoint` - Test DELETE /items/{product_id}
  - `test_reorder_via_items_endpoint` - Test PUT /items/reorder
  - `test_share_via_share_endpoint` - Test GET /share/{token}

### Step 7: Run Validation Commands
Execute the validation commands to ensure all implementations are correct with zero regressions.

## Testing Strategy

### Unit Tests
- Test PDF export endpoint returns proper content type (`application/pdf`)
- Test PDF export requires authentication
- Test PDF export returns 404 for non-existent portfolios
- Test alias routes work identically to original routes
- Mock the portfolio service to isolate route testing

### Edge Cases
- Empty portfolio (no products) - should still generate a valid PDF
- Portfolio with many products - test pagination/performance
- Invalid portfolio ID format - should return 422
- Expired share token - should return 404

## Acceptance Criteria
- [x] GET /api/portfolios - List portfolios (already implemented)
- [x] POST /api/portfolios - Create portfolio (already implemented)
- [x] GET /api/portfolios/{id} - Get portfolio with products (already implemented)
- [x] PUT /api/portfolios/{id} - Update portfolio (already implemented)
- [x] DELETE /api/portfolios/{id} - Delete portfolio (already implemented)
- [x] POST /api/portfolios/{id}/duplicate - Duplicate portfolio (already implemented)
- [ ] POST /api/portfolios/{id}/items - Add product to portfolio (alias to be added)
- [ ] DELETE /api/portfolios/{id}/items/{product_id} - Remove product (alias to be added)
- [ ] PUT /api/portfolios/{id}/items/reorder - Reorder products (alias to be added)
- [ ] GET /api/portfolios/{id}/export/pdf - Generate PDF export (to be implemented)
- [ ] GET /api/portfolios/share/{token} - Public portfolio view (alias to be added)
- [ ] All new endpoints have unit tests
- [ ] All existing tests pass

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && source .venv/bin/activate && pip install -r requirements.txt` - Install dependencies including new PDF library
- `cd apps/Server && source .venv/bin/activate && .venv/bin/pytest tests/api/test_portfolio_routes.py -v --tb=short` - Run portfolio API tests
- `cd apps/Server && source .venv/bin/activate && .venv/bin/pytest tests/services/test_portfolio_service.py -v --tb=short` - Run portfolio service tests
- `cd apps/Server && source .venv/bin/activate && .venv/bin/pytest tests/ -v --tb=short` - Run all server tests
- `cd apps/Server && source .venv/bin/activate && .venv/bin/ruff check .` - Run linting checks
- `cd apps/Client && npm run typecheck` - Run Client type check to validate no frontend regressions
- `cd apps/Client && npm run build` - Run Client build to validate no frontend regressions

## Notes

### Existing Implementation Status
The portfolio routes are largely implemented with the following endpoints:
- `GET /api/portfolios` - List portfolios with pagination and filtering
- `GET /api/portfolios/search` - Search portfolios by name/description
- `GET /api/portfolios/shared/{token}` - Public access via share token
- `POST /api/portfolios` - Create portfolio (admin/manager only)
- `GET /api/portfolios/{id}` - Get portfolio by ID
- `PUT /api/portfolios/{id}` - Update portfolio (admin/manager only)
- `DELETE /api/portfolios/{id}` - Soft delete portfolio (admin/manager only)
- `POST /api/portfolios/{id}/duplicate` - Duplicate portfolio (admin/manager only)
- `POST /api/portfolios/{id}/products/{product_id}` - Add product to portfolio
- `DELETE /api/portfolios/{id}/products/{product_id}` - Remove product from portfolio
- `PUT /api/portfolios/{id}/products/reorder` - Reorder products in portfolio
- `POST /api/portfolios/{id}/share` - Generate share token (admin/manager only)
- `POST /api/portfolios/from-filters` - Create portfolio from product filters

### PDF Generation Approach
Using `reportlab` library for PDF generation because:
- Pure Python, no external dependencies like wkhtmltopdf
- Lightweight and fast
- Good support for tables and product listings
- Widely used and well-documented

### Route Path Alias Strategy
Rather than refactoring existing endpoints, we add aliases to maintain backward compatibility:
- Existing `/products` routes remain functional
- New `/items` routes point to the same handlers
- This prevents breaking changes for any existing integrations
