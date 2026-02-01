# Feature: Niche Service CRUD

## Metadata
issue_number: `12`
adw_id: `15dd75a7`
issue_json: `{"number":12,"title":"[Kompass] Phase 4C: Niche Service","body":"Implement niche service for client type management..."}`

## Feature Description
Implement a niche service for managing client type classifications (niches) in the Kompass Portfolio & Quotation system. Niches represent client segments like Constructoras, Estudios de Arquitectura, Desarrolladores, Hoteles, Operadores Rentas Cortas, and Retailers. The service provides CRUD operations with client count tracking and delete validation to prevent orphaning clients.

## User Story
As a Kompass system administrator
I want to manage client niches (client type classifications)
So that I can categorize and segment clients for targeted portfolio management and quotations

## Problem Statement
The Kompass system needs a way to categorize clients by business type (niche). While the database schema and basic repository exist for niches, there is no service layer with business logic for client count tracking, delete validation, or API routes to expose this functionality to the frontend.

## Solution Statement
Create a NicheService that wraps the existing NicheRepository with business logic for:
- CRUD operations (create, read, update, delete)
- Client count aggregation when listing niches
- Delete validation (prevent deletion if niche has associated clients)
- Seed data population for default niches

Additionally, create API routes to expose these operations via RESTful endpoints.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/app/repository/kompass_repository.py` - Contains existing NicheRepository with basic CRUD. Need to add `count_clients_by_niche()` and `has_clients()` methods.
- `apps/Server/app/models/kompass_dto.py` - Contains existing Niche DTOs (NicheCreateDTO, NicheUpdateDTO, NicheResponseDTO, NicheListResponseDTO). Need to add `NicheWithClientCountDTO`.
- `apps/Server/app/services/tag_service.py` - Reference for service pattern with count tracking (TagService with `list_tags()` returning TagWithCountDTO).
- `apps/Server/app/services/category_service.py` - Reference for service pattern with delete validation.
- `apps/Server/app/api/category_routes.py` - Reference for API route patterns with authentication and RBAC.
- `apps/Server/main.py` - Register the new niche router.
- `apps/Server/database/schema.sql:54-64` - Niches table schema reference.
- `apps/Server/database/schema.sql:236-246` - Clients table with niche_id foreign key reference.
- `app_docs/feature-9ce5e2ee-database-schema-core-dtos.md` - Documentation for Kompass database schema and DTOs.

### New Files
- `apps/Server/app/services/niche_service.py` - New NicheService with business logic
- `apps/Server/app/api/niche_routes.py` - New API routes for niche CRUD
- `apps/Server/tests/services/test_niche_service.py` - Unit tests for NicheService
- `apps/Server/tests/api/test_niche_routes.py` - Integration tests for niche API routes
- `apps/Server/database/seed_niches.py` - Seed script for default niches

## Implementation Plan
### Phase 1: Foundation
- Add `count_clients_by_niche()` method to NicheRepository to count clients associated with a niche
- Add `has_clients()` method to NicheRepository to check if a niche has any clients (for delete validation)
- Add `NicheWithClientCountDTO` to kompass_dto.py for responses that include client counts

### Phase 2: Core Implementation
- Create `NicheService` class in `apps/Server/app/services/niche_service.py` with methods:
  - `create_niche(request: NicheCreateDTO) -> NicheResponseDTO`
  - `get_niche(niche_id: UUID) -> NicheWithClientCountDTO`
  - `list_niches() -> List[NicheWithClientCountDTO]` - Returns all niches with client counts
  - `update_niche(niche_id: UUID, request: NicheUpdateDTO) -> NicheResponseDTO`
  - `delete_niche(niche_id: UUID) -> bool` - Fails if niche has clients

### Phase 3: Integration
- Create `niche_routes.py` API router with endpoints:
  - `POST /api/niches/` - Create niche (admin/manager only)
  - `GET /api/niches/` - List all niches with client counts
  - `GET /api/niches/{niche_id}` - Get niche by ID with client count
  - `PUT /api/niches/{niche_id}` - Update niche (admin/manager only)
  - `DELETE /api/niches/{niche_id}` - Delete niche (admin/manager only)
- Register router in `main.py`
- Create seed script for default niches

## Step by Step Tasks

### Step 1: Add Repository Methods
- Open `apps/Server/app/repository/kompass_repository.py`
- Add `count_clients_by_niche(niche_id: UUID) -> int` method to NicheRepository
  - Query: `SELECT COUNT(*) FROM clients WHERE niche_id = %s`
- Add `has_clients(niche_id: UUID) -> bool` method to NicheRepository
  - Returns True if count > 0
- Add `get_all_with_client_counts() -> List[Dict[str, Any]]` method to NicheRepository
  - Query with LEFT JOIN to count clients per niche

### Step 2: Add DTOs
- Open `apps/Server/app/models/kompass_dto.py`
- Add `NicheWithClientCountDTO` class after `NicheResponseDTO`:
  ```python
  class NicheWithClientCountDTO(BaseModel):
      """Response model for niche data with client count."""
      id: UUID
      name: str
      description: Optional[str] = None
      is_active: bool
      client_count: int = 0
      created_at: datetime
      updated_at: datetime
      model_config = {"from_attributes": True}
  ```

### Step 3: Create NicheService
- Create new file `apps/Server/app/services/niche_service.py`
- Implement `NicheService` class following the pattern from `tag_service.py`:
  - `create_niche()` - Create via repository, return NicheResponseDTO
  - `get_niche()` - Get by ID, add client count, return NicheWithClientCountDTO
  - `list_niches()` - Get all with client counts, return List[NicheWithClientCountDTO]
  - `update_niche()` - Check exists, update via repository
  - `delete_niche()` - Check exists, validate no clients, soft delete via repository
- Add singleton instance: `niche_service = NicheService()`

### Step 4: Create Unit Tests for NicheService
- Create new file `apps/Server/tests/services/test_niche_service.py`
- Test classes following pattern from `test_tag_service.py`:
  - `TestCreateNiche` - Success, failure cases
  - `TestGetNiche` - Existing niche with count, non-existent
  - `TestListNiches` - With counts, empty list
  - `TestUpdateNiche` - Name, description, is_active, non-existent
  - `TestDeleteNiche` - Success, has clients (should fail), non-existent
- Use `@patch("app.services.niche_service.niche_repository")` for mocking

### Step 5: Create API Routes
- Create new file `apps/Server/app/api/niche_routes.py`
- Implement routes following pattern from `category_routes.py`:
  - `POST /` - Create niche (requires auth)
  - `GET /` - List niches with client counts (requires auth)
  - `GET /{niche_id}` - Get niche by ID (requires auth)
  - `PUT /{niche_id}` - Update niche (requires admin/manager role)
  - `DELETE /{niche_id}` - Delete niche (requires admin/manager role)
- Use proper HTTP status codes: 201 for create, 204 for delete, 404 for not found, 409 for conflict (has clients)

### Step 6: Register Router
- Open `apps/Server/main.py`
- Add import: `from app.api.niche_routes import router as niche_router`
- Register router: `app.include_router(niche_router, prefix="/api/niches")`

### Step 7: Create API Integration Tests
- Create new file `apps/Server/tests/api/test_niche_routes.py`
- Test all endpoints following pattern from `test_tag_routes.py`:
  - Test authentication required
  - Test RBAC for admin/manager operations
  - Test CRUD operations
  - Test delete validation (409 when has clients)

### Step 8: Create Seed Script
- Create new file `apps/Server/database/seed_niches.py`
- Implement `seed_default_niches()` function that inserts:
  - Constructoras
  - Estudios de Arquitectura
  - Desarrolladores
  - Hoteles
  - Operadores Rentas Cortas
  - Retailers
- Use INSERT ... ON CONFLICT DO NOTHING to be idempotent

### Step 9: Run Validation Commands
- Run all tests and validations to ensure zero regressions

## Testing Strategy
### Unit Tests
- Test NicheService CRUD operations with mocked repository
- Test client count retrieval with various counts (0, 1, many)
- Test delete validation blocks deletion when niche has clients
- Test delete validation allows deletion when niche has no clients

### Edge Cases
- Create niche with duplicate name (should fail due to UNIQUE constraint)
- Update niche to duplicate name (should fail)
- Delete niche that doesn't exist (should return False)
- Delete niche with clients (should raise ValueError or return False)
- List niches when none exist (should return empty list)
- Get niche with zero clients (client_count should be 0)

## Acceptance Criteria
- [x] NicheRepository has `count_clients_by_niche()` and `has_clients()` methods
- [x] NicheWithClientCountDTO is defined in kompass_dto.py
- [x] NicheService implements all CRUD operations
- [x] `list_niches()` returns niches with accurate client counts
- [x] `delete_niche()` fails if niche has associated clients
- [x] API routes are created and registered at `/api/niches`
- [x] All routes require authentication
- [x] Create/Update/Delete routes require admin or manager role
- [x] Unit tests cover NicheService with >90% coverage
- [x] API integration tests cover all endpoints
- [x] Seed script populates default niches
- [x] All tests pass with zero regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && source .venv/bin/activate && python -m pytest tests/services/test_niche_service.py -v --tb=short` - Run NicheService unit tests
- `cd apps/Server && source .venv/bin/activate && python -m pytest tests/api/test_niche_routes.py -v --tb=short` - Run niche API route tests
- `cd apps/Server && source .venv/bin/activate && python -m pytest tests/ -v --tb=short` - Run all Server tests to validate zero regressions
- `cd apps/Server && source .venv/bin/activate && python -m ruff check .` - Run linter to check for code quality issues
- `cd apps/Client && npm run typecheck` - Run Client type check to validate no TypeScript errors (if any client changes)
- `cd apps/Client && npm run build` - Run Client build to validate no build errors

## Notes
- The NicheRepository already exists with basic CRUD operations in `kompass_repository.py`. We are extending it with client count methods.
- The niches table schema already exists in `schema.sql` with indexes on name and is_active.
- The clients table has a foreign key reference to niches (niche_id), which we'll use for counting.
- This is a backend-only feature - no frontend changes are required for Phase 4C.
- The seed script should be idempotent (safe to run multiple times).
- Following the existing patterns: TagService for count tracking, CategoryService for delete validation.
- Default niches are Spanish names as specified in the issue requirements.
