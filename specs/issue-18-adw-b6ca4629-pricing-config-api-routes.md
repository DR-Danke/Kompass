# Feature: Pricing Configuration API Routes

## Metadata
issue_number: `18`
adw_id: `b6ca4629`
issue_json: ``

## Feature Description
Implement FastAPI routes for the pricing configuration module in the Kompass Portfolio & Quotation system. This feature exposes REST API endpoints for managing HS codes (with tariff/duty rates), freight rates (with validity tracking and origin/destination filtering), and global pricing settings. The routes integrate with the existing `pricing_service` singleton and follow established patterns from existing route modules like `niche_routes.py`.

## User Story
As a Kompass system administrator or manager
I want to manage pricing configuration through REST API endpoints
So that I can configure HS codes, freight rates, and pricing settings for quotation calculations

## Problem Statement
The pricing configuration service (`pricing_service.py`) has been implemented with full CRUD operations for HS codes, freight rates, and pricing settings. However, there are no API routes to expose this functionality to frontend clients or external systems. Without these routes, the pricing data cannot be managed through the application's REST API.

## Solution Statement
Create a new `pricing_routes.py` file that implements FastAPI routes following the established patterns in the codebase. The routes will:
- Expose CRUD endpoints for HS codes with search functionality
- Expose CRUD endpoints for freight rates with origin/destination filtering and active rate lookup
- Expose get/update endpoints for pricing settings with admin-only access for updates
- Use proper authentication (get_current_user) and role-based access control (require_roles)
- Follow existing error handling patterns (404 for not found, 400 for failures, 403 for unauthorized)

## Relevant Files
Use these files to implement the feature:

- `apps/Server/app/services/pricing_service.py` - The existing pricing service singleton with all business logic for HS codes, freight rates, and settings. This is the primary dependency for the routes.
- `apps/Server/app/api/niche_routes.py` - Reference implementation showing the route patterns, authentication, RBAC, error handling, and logging conventions to follow.
- `apps/Server/app/api/rbac_dependencies.py` - Contains the `require_roles` dependency for admin-only endpoints.
- `apps/Server/app/api/dependencies.py` - Contains the `get_current_user` dependency for authentication.
- `apps/Server/app/models/kompass_dto.py` - Contains all DTO definitions for HS codes, freight rates, and pricing settings (Create, Update, Response, List DTOs).
- `apps/Server/main.py` - Entry point where the new router needs to be registered.
- `apps/Server/tests/api/test_niche_routes.py` - Reference for unit test patterns with mocking.
- `app_docs/feature-d2c2988b-pricing-config-service.md` - Documentation of the pricing service functionality.

### New Files
- `apps/Server/app/api/pricing_routes.py` - New FastAPI router for pricing configuration endpoints
- `apps/Server/tests/api/test_pricing_routes.py` - Unit tests for the pricing routes

## Implementation Plan
### Phase 1: Foundation
1. Create the `pricing_routes.py` file with the APIRouter and necessary imports
2. Import the pricing_service singleton, DTOs, and dependencies

### Phase 2: Core Implementation
1. Implement HS Code endpoints:
   - GET `/api/pricing/hs-codes` - List/search HS codes with pagination
   - POST `/api/pricing/hs-codes` - Create HS code (authenticated)
   - GET `/api/pricing/hs-codes/{id}` - Get single HS code
   - PUT `/api/pricing/hs-codes/{id}` - Update HS code (admin/manager)
   - DELETE `/api/pricing/hs-codes/{id}` - Delete HS code (admin/manager)

2. Implement Freight Rate endpoints:
   - GET `/api/pricing/freight-rates` - List freight rates with origin/destination filters
   - POST `/api/pricing/freight-rates` - Create freight rate (authenticated)
   - PUT `/api/pricing/freight-rates/{id}` - Update freight rate (admin/manager)
   - DELETE `/api/pricing/freight-rates/{id}` - Delete freight rate (admin/manager)
   - GET `/api/pricing/freight-rates/active` - Get active rate for route (query params)

3. Implement Settings endpoints:
   - GET `/api/pricing/settings` - Get all pricing settings (authenticated)
   - PUT `/api/pricing/settings` - Update settings (admin only)

### Phase 3: Integration
1. Register the router in `main.py` with prefix `/api/pricing`
2. Create comprehensive unit tests following `test_niche_routes.py` patterns
3. Validate all endpoints work correctly with the service layer

## Step by Step Tasks

### Step 1: Create the pricing_routes.py file
- Create `apps/Server/app/api/pricing_routes.py`
- Add imports for FastAPI (APIRouter, Depends, HTTPException, status, Query)
- Add imports for typing (List, Optional)
- Add imports for UUID
- Import `get_current_user` from `app.api.dependencies`
- Import `require_roles` from `app.api.rbac_dependencies`
- Import all required DTOs from `app.models.kompass_dto`
- Import `pricing_service` from `app.services.pricing_service`
- Create `router = APIRouter(tags=["Pricing"])`

### Step 2: Implement HS Code list/search endpoint
- Implement `GET /hs-codes` endpoint
- Accept query parameters: `search` (Optional[str]), `page` (int, default 1), `limit` (int, default 20)
- Require authentication with `get_current_user`
- Return `HSCodeListResponseDTO`
- Add logging for the operation

### Step 3: Implement HS Code create endpoint
- Implement `POST /hs-codes` endpoint
- Accept `HSCodeCreateDTO` body
- Require authentication with `get_current_user`
- Return `HSCodeResponseDTO` with 201 status
- Return 400 if creation fails
- Add logging

### Step 4: Implement HS Code get by ID endpoint
- Implement `GET /hs-codes/{hs_code_id}` endpoint
- Accept UUID path parameter
- Require authentication
- Return `HSCodeResponseDTO`
- Return 404 if not found

### Step 5: Implement HS Code update endpoint
- Implement `PUT /hs-codes/{hs_code_id}` endpoint
- Accept UUID path parameter and `HSCodeUpdateDTO` body
- Require admin or manager role with `require_roles(["admin", "manager"])`
- Return `HSCodeResponseDTO`
- Return 404 if not found, 400 if update fails

### Step 6: Implement HS Code delete endpoint
- Implement `DELETE /hs-codes/{hs_code_id}` endpoint
- Accept UUID path parameter
- Require admin or manager role
- Return 204 No Content on success
- Return 404 if not found, 400 if delete fails

### Step 7: Implement Freight Rate list endpoint
- Implement `GET /freight-rates` endpoint
- Accept query parameters: `origin`, `destination`, `page`, `limit`
- Require authentication
- Return `FreightRateListResponseDTO`

### Step 8: Implement Freight Rate create endpoint
- Implement `POST /freight-rates` endpoint
- Accept `FreightRateCreateDTO` body
- Require authentication
- Return `FreightRateResponseDTO` with 201 status
- Return 400 if creation fails

### Step 9: Implement Freight Rate update endpoint
- Implement `PUT /freight-rates/{rate_id}` endpoint
- Accept UUID path parameter and `FreightRateUpdateDTO` body
- Require admin or manager role
- Return `FreightRateResponseDTO`
- Return 404 if not found, 400 if update fails

### Step 10: Implement Freight Rate delete endpoint
- Implement `DELETE /freight-rates/{rate_id}` endpoint
- Accept UUID path parameter
- Require admin or manager role
- Return 204 No Content
- Return 404 if not found
- Note: Service doesn't have explicit delete, so either implement soft-delete via update (is_active=False) or add delete method to service

### Step 11: Implement active rate lookup endpoint
- Implement `GET /freight-rates/active` endpoint
- Accept query parameters: `origin` (required), `destination` (required)
- Require authentication
- Return `FreightRateResponseDTO`
- Return 404 if no active rate found for the route

### Step 12: Implement Settings get endpoint
- Implement `GET /settings` endpoint
- Require authentication
- Return `PricingSettingsResponseDTO` containing list of all settings

### Step 13: Implement Settings update endpoint
- Implement `PUT /settings` endpoint
- Accept `PricingSettingUpdateDTO` body with `setting_key` and `setting_value`
- Require admin role only with `require_roles(["admin"])`
- Return `PricingSettingResponseDTO`
- Return 404 if setting key not found, 400 if update fails

### Step 14: Register router in main.py
- Import the router in `apps/Server/main.py`
- Add `app.include_router(pricing_router, prefix="/api/pricing")`

### Step 15: Create unit tests for HS Code endpoints
- Create `apps/Server/tests/api/test_pricing_routes.py`
- Follow patterns from `test_niche_routes.py`
- Create fixtures: client, mock_user, mock_admin_user, mock_manager_user
- Create fixtures for mock HS code data
- Test list HS codes returns paginated results
- Test create HS code success and failure
- Test get HS code by ID success and 404
- Test update HS code with admin/manager role
- Test update requires appropriate role (403 for regular user)
- Test delete HS code with admin/manager role

### Step 16: Create unit tests for Freight Rate endpoints
- Test list freight rates with filters
- Test create freight rate
- Test update freight rate with role check
- Test delete freight rate
- Test get active rate for route
- Test get active rate returns 404 when no active rate

### Step 17: Create unit tests for Settings endpoints
- Test get all settings
- Test update setting with admin role
- Test update setting fails for non-admin (403)
- Test update non-existent setting returns 404

### Step 18: Run validation commands
- Run all tests to ensure no regressions
- Run linting checks
- Run type checks

## Testing Strategy
### Unit Tests
- Mock `pricing_service` to isolate route logic
- Mock `auth_service` and `user_repository` for authentication
- Test success cases for all endpoints
- Test authentication requirements (401/403 without token)
- Test role-based access control (403 for unauthorized roles)
- Test error cases (404 not found, 400 bad request)
- Test query parameter handling for search and filters

### Edge Cases
- Empty search query returns all HS codes
- No freight rates match origin/destination filter
- No active rate exists for a route
- Update with empty/partial data
- Delete non-existent resources
- Non-admin trying to update settings

## Acceptance Criteria
- [ ] All HS code endpoints functional (GET list, POST, GET by ID, PUT, DELETE)
- [ ] Search working for HS codes (by code or description)
- [ ] All freight rate endpoints functional (GET list, POST, PUT, DELETE, GET active)
- [ ] Origin/destination filtering working for freight rates
- [ ] Active rate lookup returns correct rate based on validity dates
- [ ] Settings GET endpoint returns all pricing settings
- [ ] Settings PUT endpoint restricted to admin role only
- [ ] All endpoints require authentication
- [ ] Write operations (POST, PUT, DELETE) follow RBAC rules
- [ ] Unit tests pass with >90% coverage for the routes file
- [ ] No linting errors
- [ ] No type errors

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Run all Server tests
cd apps/Server && source .venv/bin/activate && .venv/bin/pytest tests/ -v --tb=short

# Run specific pricing routes tests
cd apps/Server && .venv/bin/pytest tests/api/test_pricing_routes.py -v --tb=short

# Run linting on new file
cd apps/Server && .venv/bin/ruff check app/api/pricing_routes.py

# Run linting on test file
cd apps/Server && .venv/bin/ruff check tests/api/test_pricing_routes.py

# Run Client type check
cd apps/Client && npm run typecheck

# Run Client build
cd apps/Client && npm run build
```

## Notes
- The `pricing_service` already has all the business logic implemented; the routes are purely HTTP layer
- The freight rate delete can be implemented as soft-delete (set `is_active=False`) using the existing `update_freight_rate` method since the service doesn't have an explicit delete method
- The settings update endpoint should accept a key-value pair, not a list of settings, to allow updating individual settings
- Consider adding an endpoint for `check_expired_rates` in the future for admin alerts
- The Incoterm enum from `kompass_dto.py` should be used for freight rate validation
