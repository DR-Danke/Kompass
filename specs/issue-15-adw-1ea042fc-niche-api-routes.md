# Feature: Niche API Routes

## Metadata
issue_number: `15`
adw_id: `1ea042fc`
issue_json: `{"number":15,"title":"[Kompass] Phase 5C: Niche API Routes","body":"## Context\n**Current Phase:** Phase 5 of 13 - API Routes Part 2\n**Current Issue:** KP-015 (Issue 15 of 33)\n**Parallel Execution:** YES - Runs IN PARALLEL with KP-013 and KP-014.\n\n---\n\n## Description\nImplement FastAPI routes for niche management.\n\n## Requirements\n\n### File: apps/Server/app/api/niche_routes.py\n\n#### Endpoints\n- GET    /api/niches                  - List niches with client counts\n- POST   /api/niches                  - Create niche\n- GET    /api/niches/{id}             - Get niche detail\n- PUT    /api/niches/{id}             - Update niche\n- DELETE /api/niches/{id}             - Delete niche\n\n## Acceptance Criteria\n- [ ] All endpoints functional\n- [ ] Client counts accurate\n\nInclude workflow: adw_plan_build_test_iso\n\n---\n\n## Full Implementation Reference\nFor complete implementation details, dependency graph, and execution commands, see:\n**ai_docs/KOMPASS_ADW_IMPLEMENTATION_PROMPTS.md**\n\nThis document contains all 33 issues, parallel execution instructions, and the complete bash script for automated deployment."}`

## Feature Description
This feature implements FastAPI REST API routes for managing niches (client type classifications) in the Kompass Portfolio & Quotation system. Niches categorize clients by business segment (e.g., Constructoras, Hoteles, Retailers) enabling targeted portfolio management and client organization.

**NOTE:** This feature is already fully implemented in the codebase. This plan validates the existing implementation meets all acceptance criteria.

## User Story
As an admin or manager user
I want to manage niches via REST API endpoints
So that I can categorize clients by business type for better portfolio targeting

## Problem Statement
The Kompass system needs a way to classify clients into business segments (niches) to enable targeted portfolio management and improve client organization. API endpoints are required for CRUD operations on niches with proper authentication and authorization.

## Solution Statement
Implement a complete set of FastAPI REST endpoints for niche management:
- List all niches with their associated client counts (GET /api/niches)
- Create new niches (POST /api/niches)
- Get individual niche details (GET /api/niches/{id})
- Update existing niches (PUT /api/niches/{id})
- Delete niches with validation (DELETE /api/niches/{id})

All endpoints are protected by JWT authentication, with write operations requiring admin or manager roles.

## Relevant Files
Use these files to validate the feature:

### Existing Implementation Files
- `apps/Server/app/api/niche_routes.py` - FastAPI router with all 5 endpoints (already implemented)
- `apps/Server/app/services/niche_service.py` - Business logic layer with CRUD operations (already implemented)
- `apps/Server/app/repository/kompass_repository.py` - Repository with `NicheRepository` class including `count_clients_by_niche()`, `has_clients()`, and `get_all_with_client_counts()` methods
- `apps/Server/app/models/kompass_dto.py` - Contains `NicheCreateDTO`, `NicheUpdateDTO`, `NicheResponseDTO`, `NicheWithClientCountDTO`
- `apps/Server/main.py` - Router registration at `/api/niches` (line 75)
- `apps/Server/app/api/dependencies.py` - JWT authentication dependency `get_current_user`
- `apps/Server/app/api/rbac_dependencies.py` - RBAC dependency `require_roles`

### Test Files
- `apps/Server/tests/api/test_niche_routes.py` - Comprehensive API route tests (496 lines)
- `apps/Server/tests/services/test_niche_service.py` - Unit tests for niche service

### Documentation
- `app_docs/feature-15dd75a7-niche-service-crud.md` - Feature documentation from prior implementation

## Implementation Plan
### Phase 1: Validation
Since the feature is already implemented, validate that all components are in place and working correctly.

### Phase 2: Test Execution
Run all existing tests to confirm the implementation meets acceptance criteria.

### Phase 3: Acceptance Criteria Verification
Verify each acceptance criterion is met:
1. All endpoints functional - validated via route tests
2. Client counts accurate - validated via service tests and list endpoint tests

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Verify Route Implementation
- Confirm `apps/Server/app/api/niche_routes.py` exists with all 5 endpoints:
  - GET `/` - list_niches
  - POST `/` - create_niche
  - GET `/{niche_id}` - get_niche
  - PUT `/{niche_id}` - update_niche
  - DELETE `/{niche_id}` - delete_niche
- Confirm proper authentication (get_current_user) on all endpoints
- Confirm RBAC (require_roles) on PUT and DELETE endpoints

### Step 2: Verify Service Implementation
- Confirm `apps/Server/app/services/niche_service.py` exists with:
  - `create_niche()`
  - `get_niche()` - returns NicheWithClientCountDTO with client_count
  - `list_niches()` - returns list with client counts
  - `update_niche()`
  - `delete_niche()` - validates no associated clients before delete

### Step 3: Verify DTOs
- Confirm DTOs in `apps/Server/app/models/kompass_dto.py`:
  - `NicheCreateDTO` with name, description, is_active fields
  - `NicheUpdateDTO` with optional fields
  - `NicheResponseDTO` with all fields plus timestamps
  - `NicheWithClientCountDTO` with client_count field

### Step 4: Verify Router Registration
- Confirm in `apps/Server/main.py`:
  - Import: `from app.api.niche_routes import router as niche_router`
  - Registration: `app.include_router(niche_router, prefix="/api/niches")`

### Step 5: Run Unit Tests
- Execute niche service unit tests
- Verify all tests pass

### Step 6: Run API Route Tests
- Execute niche route integration tests
- Verify all tests pass including:
  - Authentication required tests
  - RBAC enforcement tests
  - Client count accuracy tests
  - 409 Conflict on delete with clients tests

### Step 7: Run Full Validation Commands
- Run all Server tests
- Run Client type check
- Run Client build

## Testing Strategy
### Unit Tests
- NicheService CRUD operations
- Client count calculation
- Delete validation (cannot delete niche with clients)

### Edge Cases
- List empty niches (returns empty array)
- Get non-existent niche (returns 404)
- Update non-existent niche (returns 404)
- Delete non-existent niche (returns 404)
- Delete niche with associated clients (returns 409)
- Create with duplicate name (returns 400)
- Unauthorized access (returns 401/403)
- Non-admin/manager trying to update/delete (returns 403)

## Acceptance Criteria
1. **All endpoints functional**
   - GET /api/niches returns list of niches with client counts
   - POST /api/niches creates new niche and returns 201
   - GET /api/niches/{id} returns niche detail with client count
   - PUT /api/niches/{id} updates niche (admin/manager only)
   - DELETE /api/niches/{id} deletes niche (admin/manager only, fails if has clients)

2. **Client counts accurate**
   - List endpoint returns accurate client_count for each niche
   - Get endpoint returns accurate client_count for the niche
   - Client counts are calculated via efficient LEFT JOIN query

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Run niche service unit tests
cd apps/Server && source .venv/bin/activate && python -m pytest tests/services/test_niche_service.py -v --tb=short

# Run niche route integration tests
cd apps/Server && source .venv/bin/activate && python -m pytest tests/api/test_niche_routes.py -v --tb=short

# Run all Server tests to ensure no regressions
cd apps/Server && source .venv/bin/activate && python -m pytest tests/ -v --tb=short

# Run linting
cd apps/Server && source .venv/bin/activate && python -m ruff check .

# Run Client type check
cd apps/Client && npm run typecheck

# Run Client build
cd apps/Client && npm run build
```

## Notes
- This feature is **already fully implemented** in the codebase per `app_docs/feature-15dd75a7-niche-service-crud.md`
- The implementation follows existing patterns from TagService (count tracking) and CategoryService (delete validation)
- Default niches include: Constructoras, Estudios de Arquitectura, Desarrolladores, Hoteles, Operadores Rentas Cortas, Retailers
- Soft delete pattern is used (sets `is_active=False`)
- Backend-only feature - no frontend UI changes required for this phase
- Runs in parallel with KP-013 (Client API Routes) and KP-014 (Portfolio API Routes)
