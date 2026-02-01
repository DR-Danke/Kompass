# Feature: Quotation API Routes

## Metadata
issue_number: `19`
adw_id: `0884e820`
issue_json: `{"number":19,"title":"[Kompass] Phase 7B: Quotation API Routes","body":"## Context\n**Current Phase:** Phase 7 of 13 - Pricing & Quotation Routes\n**Current Issue:** KP-019 (Issue 19 of 33)\n**Parallel Execution:** YES - Runs IN PARALLEL with KP-018.\n\n---\n\n## Description\nImplement FastAPI routes for quotation management.\n\n## Requirements\n\n### File: apps/Server/app/api/quotation_routes.py\n\n#### Endpoints\n- GET    /api/quotations               - List quotations\n- POST   /api/quotations               - Create quotation\n- GET    /api/quotations/{id}          - Get quotation with items\n- PUT    /api/quotations/{id}          - Update quotation\n- DELETE /api/quotations/{id}          - Delete quotation\n- POST   /api/quotations/{id}/calculate - Recalculate pricing\n- POST   /api/quotations/{id}/clone    - Clone as new version\n- PUT    /api/quotations/{id}/status   - Update status\n- POST   /api/quotations/{id}/items    - Add line item\n- PUT    /api/quotations/{id}/items/{item_id} - Update line item\n- DELETE /api/quotations/{id}/items/{item_id} - Remove line item\n- GET    /api/quotations/{id}/export/pdf - Generate PDF proforma\n- POST   /api/quotations/{id}/send     - Send via email\n- GET    /api/quotations/share/{token} - Public quotation view (no auth)\n\n## Acceptance Criteria\n- [ ] All endpoints functional\n- [ ] Pricing calculation working\n- [ ] PDF export generating\n- [ ] Email sending working\n- [ ] Public share link working"}`

## Feature Description
This feature extends the existing quotation API routes with additional functionality for the Kompass Portfolio & Quotation System. The quotation routes provide a complete REST API for managing client quotations, including CRUD operations, pricing calculations, line item management, status workflow, PDF proforma generation, email sending, and public share links.

Many of the core quotation endpoints already exist in the codebase (CRUD, clone, pricing, status, line items). This implementation focuses on adding the missing endpoints:
- POST `/api/quotations/{id}/calculate` - Recalculate and persist pricing
- GET `/api/quotations/{id}/export/pdf` - Generate PDF proforma document
- POST `/api/quotations/{id}/send` - Send quotation via email
- GET `/api/quotations/share/{token}` - Public quotation view without authentication

Additionally, the line item endpoints need to be updated to use the nested route pattern `/api/quotations/{id}/items/{item_id}` for consistency with the specification.

## User Story
As a sales representative
I want to create, manage, and share quotations with clients
So that I can efficiently provide pricing information and track quotation status through the sales cycle

## Problem Statement
The current quotation API lacks several key features required for a complete quotation workflow:
1. Cannot trigger recalculation of pricing with persistence
2. Cannot generate PDF proforma documents for client distribution
3. Cannot send quotations directly to clients via email
4. Cannot share quotations via a public link without requiring client authentication
5. Line item update/delete routes use a different pattern than specified

## Solution Statement
Extend the existing `quotation_routes.py` with the missing endpoints following the established patterns in the codebase:
1. Add a POST `/calculate` endpoint that recalculates pricing and persists the results
2. Add a GET `/export/pdf` endpoint using reportlab (following the portfolio PDF pattern)
3. Add a POST `/send` endpoint for email functionality with mock mode support
4. Add a GET `/share/{token}` endpoint using JWT tokens (following the portfolio share pattern)
5. Update line item routes to use the nested pattern `/{id}/items/{item_id}`

## Relevant Files
Use these files to implement the feature:

- `apps/Server/app/api/quotation_routes.py` - Main file to extend with new endpoints (already exists with ~430 lines)
- `apps/Server/app/services/quotation_service.py` - Quotation service to extend with new methods (already exists with ~915 lines)
- `apps/Server/app/models/kompass_dto.py` - DTOs to extend with new request/response models
- `apps/Server/app/api/portfolio_routes.py` - Reference for PDF export and share token patterns
- `apps/Server/app/services/portfolio_service.py` - Reference for PDF generation and share token logic
- `apps/Server/app/api/dependencies.py` - Authentication dependencies
- `apps/Server/app/api/rbac_dependencies.py` - Role-based access control
- `apps/Server/main.py` - Router registration (quotation router already registered)
- `apps/Server/database/schema.sql` - Database schema reference for quotations table
- `apps/Server/tests/api/test_quotation_routes.py` - Existing tests to extend
- `apps/Server/tests/services/test_quotation_service.py` - Existing tests to extend
- `app_docs/feature-bccd1fc5-quotation-service-pricing-engine.md` - Existing quotation service documentation

### New Files
- `apps/Server/app/models/quotation_email_dto.py` - Email-related DTOs for quotation sending

## Implementation Plan
### Phase 1: Foundation
1. Review existing quotation_routes.py and quotation_service.py implementations
2. Add new DTOs to kompass_dto.py for:
   - `QuotationShareTokenResponseDTO` - Share token generation response
   - `QuotationPublicResponseDTO` - Public quotation view (no sensitive data)
   - `QuotationSendEmailRequestDTO` - Email sending request
   - `QuotationSendEmailResponseDTO` - Email sending response
3. Add share_token column to quotations table (or use JWT-based tokens like portfolios)

### Phase 2: Core Implementation
1. Extend `quotation_service.py` with new methods:
   - `recalculate_and_persist(quotation_id)` - Recalculate pricing and update totals
   - `generate_pdf(quotation_id)` - Generate PDF proforma using reportlab
   - `send_email(quotation_id, recipient_email, message)` - Send quotation via email
   - `get_share_token(quotation_id)` - Generate JWT share token
   - `get_by_share_token(token)` - Validate token and return public quotation view

2. Add new endpoints to `quotation_routes.py`:
   - POST `/{quotation_id}/calculate`
   - GET `/{quotation_id}/export/pdf`
   - POST `/{quotation_id}/send`
   - GET `/share/{token}` (public, no auth)

3. Update existing line item routes for consistency:
   - PUT `/{quotation_id}/items/{item_id}` (currently `/items/{item_id}`)
   - DELETE `/{quotation_id}/items/{item_id}` (currently `/items/{item_id}`)

### Phase 3: Integration
1. Ensure all new endpoints integrate with existing authentication and RBAC
2. Add comprehensive error handling for edge cases
3. Implement email mock mode for development/testing
4. Test integration with frontend quotation components

## Step by Step Tasks

### Step 1: Add New DTOs for Quotation Features
- Add `QuotationShareTokenResponseDTO` with fields: `token`, `expires_at`, `quotation_id`
- Add `QuotationPublicResponseDTO` with limited quotation data for public viewing
- Add `QuotationSendEmailRequestDTO` with fields: `recipient_email`, `recipient_name`, `subject`, `message`
- Add `QuotationSendEmailResponseDTO` with fields: `success`, `message`, `sent_at`
- Location: `apps/Server/app/models/kompass_dto.py`

### Step 2: Extend Quotation Service with PDF Generation
- Implement `generate_pdf(quotation_id: UUID) -> Optional[bytes]` method
- Use reportlab library following the portfolio_service.py pattern
- Include quotation header (number, date, client info)
- Include line items table with quantities and prices
- Include totals section (subtotal, freight, insurance, grand total)
- Include terms and conditions
- Include validity period

### Step 3: Extend Quotation Service with Share Token Functionality
- Implement `get_share_token(quotation_id: UUID) -> Optional[QuotationShareTokenResponseDTO]`
- Use JWT tokens following the portfolio_service.py pattern
- Token type: "quotation_share"
- Default expiration: 30 days
- Implement `get_by_share_token(token: str) -> Optional[QuotationPublicResponseDTO]`
- Validate token and return public-safe quotation data

### Step 4: Extend Quotation Service with Email Functionality
- Implement `send_email(quotation_id: UUID, request: QuotationSendEmailRequestDTO) -> QuotationSendEmailResponseDTO`
- Support mock mode via environment variable `EMAIL_MOCK_MODE=true`
- Generate PDF and attach to email
- Include tracking link using share token
- Log email sending attempts

### Step 5: Add POST /calculate Endpoint
- Create `POST /{quotation_id}/calculate` endpoint in quotation_routes.py
- Call `quotation_service.calculate_pricing()` and persist results
- Return updated `QuotationPricingDTO`
- Require authentication

### Step 6: Add GET /export/pdf Endpoint
- Create `GET /{quotation_id}/export/pdf` endpoint
- Use StreamingResponse with `application/pdf` media type
- Generate filename using quotation number
- Require authentication

### Step 7: Add POST /send Endpoint
- Create `POST /{quotation_id}/send` endpoint
- Accept `QuotationSendEmailRequestDTO` body
- Return `QuotationSendEmailResponseDTO`
- Require authentication

### Step 8: Add GET /share/{token} Public Endpoint
- Create `GET /share/{token}` endpoint (no authentication)
- Return `QuotationPublicResponseDTO`
- Return 404 for invalid/expired tokens

### Step 9: Update Line Item Routes for Consistency
- Update `PUT /items/{item_id}` to `PUT /{quotation_id}/items/{item_id}`
- Update `DELETE /items/{item_id}` to `DELETE /{quotation_id}/items/{item_id}`
- Validate that item belongs to the specified quotation
- Maintain backward compatibility if needed (optional)

### Step 10: Add Unit Tests for New Service Methods
- Test `generate_pdf()` returns valid PDF bytes
- Test `get_share_token()` returns valid JWT token
- Test `get_by_share_token()` validates token correctly
- Test `send_email()` with mock mode
- Location: `apps/Server/tests/services/test_quotation_service.py`

### Step 11: Add API Tests for New Endpoints
- Test POST `/calculate` recalculates pricing
- Test GET `/export/pdf` returns PDF response
- Test POST `/send` sends email (mock mode)
- Test GET `/share/{token}` returns public quotation
- Test updated line item routes
- Test authentication requirements
- Location: `apps/Server/tests/api/test_quotation_routes.py`

### Step 12: Run Validation Commands
- Execute all validation commands to ensure zero regressions

## Testing Strategy
### Unit Tests
- Test PDF generation produces valid PDF bytes
- Test share token generation and validation
- Test email sending in mock mode
- Test pricing recalculation updates quotation totals
- Test public response DTO excludes sensitive fields

### Edge Cases
- Invalid/expired share tokens
- Non-existent quotation IDs
- Email sending failures
- PDF generation with empty line items
- Line item update for wrong quotation ID
- Quotation without client (deleted client)
- Large quotations with many line items

## Acceptance Criteria
- [x] All existing endpoints continue to function (CRUD, clone, pricing, status, line items)
- [ ] POST `/calculate` recalculates and persists pricing
- [ ] GET `/export/pdf` generates downloadable PDF proforma
- [ ] POST `/send` sends quotation via email (mock mode for tests)
- [ ] GET `/share/{token}` provides public quotation view without auth
- [ ] Line item routes use nested pattern `/{id}/items/{item_id}`
- [ ] All new endpoints have comprehensive tests
- [ ] All tests pass with zero regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Run static analysis
cd apps/Server && .venv/bin/ruff check .

# Run all Server tests
cd apps/Server && .venv/bin/pytest tests/ -v --tb=short

# Run specific quotation tests
cd apps/Server && .venv/bin/pytest tests/services/test_quotation_service.py -v --tb=short
cd apps/Server && .venv/bin/pytest tests/api/test_quotation_routes.py -v --tb=short

# Run Client type check
cd apps/Client && npm run typecheck

# Run Client build
cd apps/Client && npm run build
```

## Notes
- The existing quotation_routes.py already implements most core endpoints (CRUD, clone, pricing, status, line items)
- Follow the portfolio_service.py pattern for PDF generation using reportlab
- Follow the portfolio_service.py pattern for JWT-based share tokens
- Use EMAIL_MOCK_MODE environment variable to control email sending in development
- The database schema already supports the quotation structure; no migrations needed
- Consider adding a share_token column to quotations table for tracking shared quotations (optional)
- Depends on KP-018 (Pricing Configuration API Routes) running in parallel
