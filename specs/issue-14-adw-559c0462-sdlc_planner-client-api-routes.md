# Feature: Client API Routes

## Metadata
issue_number: `14`
adw_id: `559c0462`
issue_json: `{"number":14,"title":"[Kompass] Phase 5B: Client API Routes","body":"Implement FastAPI routes for client management (CRM)."}`

## Feature Description
Align and validate FastAPI routes for client management (CRM) to match the specified endpoint contracts. The client_routes.py file already exists with a comprehensive implementation of client CRUD, pipeline management, status history, and timing feasibility endpoints. This task validates the existing implementation and makes minor adjustments to ensure endpoint paths and HTTP methods match the specification exactly.

## User Story
As a frontend developer
I want consistent and well-documented client API endpoints
So that I can reliably integrate client CRM functionality with predictable endpoint paths and HTTP methods

## Problem Statement
The existing `client_routes.py` implementation is comprehensive but has two minor discrepancies from the specification:
1. Status update endpoint uses `POST /{client_id}/status` instead of `PUT /{client_id}/status`
2. Status history endpoint uses `GET /{client_id}/status-history` instead of `GET /{client_id}/history`

Additionally, we need to ensure all endpoints are properly tested and validated.

## Solution Statement
Update the existing `client_routes.py` to:
1. Change status update from `POST` to `PUT` for REST compliance (PUT is more appropriate for updating a resource)
2. Add an alias route `GET /{client_id}/history` that redirects to the existing status-history functionality (or rename the existing endpoint)
3. Run comprehensive tests to validate all endpoints work correctly

## Relevant Files
Use these files to implement the feature:

- `apps/Server/app/api/client_routes.py` - Existing client API routes that need minor adjustments
- `apps/Server/app/services/client_service.py` - Client service with business logic (already complete, reference only)
- `apps/Server/app/models/kompass_dto.py` - DTOs for client operations (reference for response types)
- `apps/Server/main.py` - Router registration (already configured at `/api/clients`)
- `apps/Server/tests/test_client_service.py` - Existing tests for client service (reference)
- `app_docs/feature-eb16007c-client-service-crm.md` - Documentation for the client service CRM feature

### New Files
- `apps/Server/tests/api/test_client_routes.py` - Integration tests for client API routes

## Implementation Plan
### Phase 1: Foundation
- Review existing `client_routes.py` implementation against the specification
- Identify the two discrepancies that need to be addressed

### Phase 2: Core Implementation
- Update `POST /{client_id}/status` to `PUT /{client_id}/status` for REST compliance
- Add `GET /{client_id}/history` endpoint as an alias or rename `status-history` to `history`
- Update docstrings to reflect the changes

### Phase 3: Integration
- Create integration tests for all client API endpoints
- Run validation commands to ensure zero regressions

## Step by Step Tasks

### Step 1: Review Current Implementation
- Read `apps/Server/app/api/client_routes.py` to confirm current endpoint structure
- Document which endpoints match spec and which need adjustment

### Step 2: Update Status Endpoint HTTP Method
- Open `apps/Server/app/api/client_routes.py`
- Change `@router.post("/{client_id}/status", ...)` to `@router.put("/{client_id}/status", ...)`
- This makes the endpoint REST-compliant (PUT for updating a resource)
- Keep the same function signature and implementation

### Step 3: Add History Endpoint Alias
- In `apps/Server/app/api/client_routes.py`, add a new endpoint:
  ```python
  @router.get("/{client_id}/history", response_model=List[StatusHistoryResponseDTO])
  async def get_client_history(
      client_id: UUID,
      current_user: dict = Depends(get_current_user),
  ) -> List[StatusHistoryResponseDTO]:
      """Get status change history for a client (alias for /status-history)."""
      return await get_status_history(client_id, current_user)
  ```
- This provides both `/history` and `/status-history` endpoints for backward compatibility

### Step 4: Create API Integration Tests
- Create `apps/Server/tests/api/test_client_routes.py`
- Test all 9 endpoints specified in the issue:
  - `GET /api/clients` - List clients (paginated)
  - `POST /api/clients` - Create client
  - `GET /api/clients/{id}` - Get client detail
  - `PUT /api/clients/{id}` - Update client
  - `DELETE /api/clients/{id}` - Delete client
  - `GET /api/clients/pipeline` - Get pipeline (grouped by status)
  - `PUT /api/clients/{id}/status` - Update status
  - `GET /api/clients/{id}/history` - Get status change history
  - `GET /api/clients/{id}/quotations` - Get client's quotations
- Test authentication requirements for all endpoints
- Test RBAC for delete endpoint (admin/manager only)
- Mock the client_service to avoid database dependencies

### Step 5: Run Validation Commands
- Run all tests and linting to ensure zero regressions

## Testing Strategy
### Unit Tests
- Mock client_service in API route tests
- Test successful responses for all endpoints
- Test 404 responses for non-existent clients
- Test 400 responses for validation errors
- Test 401/403 responses for authentication/authorization failures

### Edge Cases
- List clients with no results (empty pagination)
- Pipeline with empty status groups
- Status update to same status (should still work)
- Delete client with active quotations (should fail with 400)
- History for client with no history (empty list)

## Acceptance Criteria
- [ ] All endpoints functional
  - GET /api/clients - List with pagination and filtering
  - POST /api/clients - Create new client
  - GET /api/clients/{id} - Get single client
  - PUT /api/clients/{id} - Update client
  - DELETE /api/clients/{id} - Soft delete (admin/manager only)
  - GET /api/clients/pipeline - Pipeline view grouped by status
  - PUT /api/clients/{id}/status - Update status with history
  - GET /api/clients/{id}/history - Get status change history
  - GET /api/clients/{id}/quotations - Get quotation summary
- [ ] Pipeline grouping correct (groups by prospect, active, inactive)
- [ ] Status history working (records changes with timestamp and user)
- [ ] All endpoints require authentication
- [ ] Delete endpoint requires admin/manager role
- [ ] Integration tests pass for all endpoints
- [ ] Static analysis (ruff) passes
- [ ] Server tests pass with zero regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && source .venv/bin/activate && python -m pytest tests/api/test_client_routes.py -v --tb=short` - Run client API route integration tests
- `cd apps/Server && source .venv/bin/activate && python -m pytest tests/test_client_service.py -v --tb=short` - Run client service unit tests
- `cd apps/Server && source .venv/bin/activate && python -m pytest tests/ -v --tb=short` - Run all Server tests to validate zero regressions
- `cd apps/Server && source .venv/bin/activate && python -m ruff check .` - Run linter to check for code quality issues
- `cd apps/Client && npm run typecheck` - Run Client type check to validate no TypeScript errors
- `cd apps/Client && npm run build` - Run Client build to validate no build errors

## Notes
- The existing `client_routes.py` implementation is comprehensive and well-structured. Only minor adjustments are needed.
- The status endpoint method change from POST to PUT is a REST best practice - PUT is idempotent and appropriate for update operations.
- Adding the `/history` alias maintains backward compatibility with any existing clients using `/status-history`.
- The client service layer (`client_service.py`) is already complete with all necessary business logic - no changes required there.
- The DTOs in `kompass_dto.py` are already defined correctly for all response types.
- The router is already registered in `main.py` at the `/api/clients` prefix.
- This is primarily a validation and minor alignment task rather than new implementation.
