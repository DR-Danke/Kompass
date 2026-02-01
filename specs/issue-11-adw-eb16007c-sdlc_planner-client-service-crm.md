# Feature: Client Service (CRM)

## Metadata
issue_number: `11`
adw_id: `eb16007c`
issue_json: `{"number":11,"title":"[Kompass] Phase 4B: Client Service (CRM)","body":"Implement client service for CRM functionality."}`

## Feature Description
Implement a comprehensive client service for CRM (Customer Relationship Management) functionality in the Kompass Portfolio & Quotation Automation System. This service layer provides business logic for managing clients throughout their lifecycle, from prospect to active customer. The service includes:

1. **Core CRUD Operations**: Create, read, update, and delete clients with full validation
2. **Pipeline Management**: Group clients by status for sales pipeline visualization
3. **Status History Tracking**: Track status changes with timestamps and notes for audit purposes
4. **Advanced Filtering**: Filter clients by status, niche, assigned user, source, and date ranges
5. **Timing Feasibility**: Calculate whether project deadlines are achievable based on production and shipping timelines

## User Story
As a sales team member
I want to manage clients through a CRM pipeline with status tracking
So that I can efficiently progress leads through the sales funnel and ensure timely project delivery

## Problem Statement
The Kompass system needs a robust client management service to:
- Track prospects as they move through the sales pipeline
- Maintain history of status changes for accountability
- Ensure project deadlines are feasible given production and shipping constraints
- Provide pipeline views grouped by client status for sales team visibility

## Solution Statement
Create a `ClientService` class following the existing service patterns (similar to `SupplierService`) that:
1. Wraps the existing `ClientRepository` with business logic
2. Extends the database schema to support CRM-specific fields (assigned_to, source, project_deadline, status history)
3. Implements pipeline grouping and status history tracking
4. Adds timing feasibility calculations based on freight rates and lead times
5. Exposes functionality through RESTful API routes

## Relevant Files
Use these files to implement the feature:

### Existing Files to Modify:
- `apps/Server/database/schema.sql` - Add CRM-specific columns to clients table and create client_status_history table
- `apps/Server/app/models/kompass_dto.py` - Add new DTOs for CRM functionality (status history, pipeline, timing feasibility)
- `apps/Server/app/repository/kompass_repository.py` - Extend ClientRepository with new methods for status history and pipeline
- `apps/Server/main.py` - Register new client_routes router

### New Files:
- `apps/Server/app/services/client_service.py` - Main client service with business logic
- `apps/Server/app/api/client_routes.py` - REST API endpoints for client operations
- `apps/Server/tests/test_client_service.py` - Unit tests for client service

## Implementation Plan

### Phase 1: Foundation
Extend the database schema to support CRM-specific fields:
- Add columns to clients table: `assigned_to`, `source`, `project_deadline`
- Create `client_status_history` table to track status changes with timestamps and notes
- Update DTOs to include new fields and response models

### Phase 2: Core Implementation
Build the client service with:
- Core CRUD operations wrapping the repository
- Pipeline method to group clients by status
- Status update method that records history
- Status history retrieval
- Timing feasibility calculations

### Phase 3: Integration
Create API routes and integrate with the application:
- RESTful endpoints for all client operations
- Pipeline endpoint for grouped client views
- Status history endpoint for audit trail
- Timing validation endpoint for deadline feasibility

## Step by Step Tasks

### Task 1: Update Database Schema
- Add new columns to `clients` table in `apps/Server/database/schema.sql`:
  - `assigned_to UUID REFERENCES users(id) ON DELETE SET NULL`
  - `source VARCHAR(50)` (values: website, referral, cold_call, trade_show, linkedin, other)
  - `project_deadline DATE`
- Create `client_status_history` table:
  ```sql
  CREATE TABLE IF NOT EXISTS client_status_history (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
      old_status VARCHAR(20),
      new_status VARCHAR(20) NOT NULL,
      notes TEXT,
      changed_by UUID REFERENCES users(id) ON DELETE SET NULL,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
  );
  ```
- Add indexes for new columns and history table

### Task 2: Extend DTOs in kompass_dto.py
- Add `ClientSource` enum with values: website, referral, cold_call, trade_show, linkedin, other
- Update `ClientCreateDTO` to include: `assigned_to`, `source`, `project_deadline`
- Update `ClientUpdateDTO` with same optional fields
- Update `ClientResponseDTO` to include: `assigned_to`, `assigned_to_name`, `source`, `project_deadline`
- Add `ClientStatusChangeDTO` for recording status changes with notes
- Add `StatusHistoryResponseDTO` for status history entries
- Add `ClientWithQuotationsDTO` that includes quotation history summary
- Add `PipelineResponseDTO` with Dict[str, List[ClientResponseDTO]] structure
- Add `TimingFeasibilityDTO` with feasibility result and breakdown

### Task 3: Extend ClientRepository in kompass_repository.py
- Update `create()` method to include new fields (assigned_to, source, project_deadline)
- Update `get_by_id()` to join with users table for assigned_to_name
- Update `get_all()` to support new filters:
  - `assigned_to` filter
  - `source` filter
  - `date_from` and `date_to` for created_at range
  - `sort_by` parameter (company_name, created_at, project_deadline)
- Add `get_by_status()` method for pipeline grouping
- Add `create_status_history()` method to insert status change records
- Add `get_status_history()` method to retrieve history for a client
- Add `get_client_with_quotations()` method that includes quotation summary
- Update `_row_to_dict_with_niche()` to include new fields

### Task 4: Create ClientService in apps/Server/app/services/client_service.py
- Create `ClientService` class following `SupplierService` pattern
- Implement core methods:
  - `create_client(request: ClientCreateDTO) -> ClientResponseDTO`
  - `get_client(client_id: UUID) -> Optional[ClientResponseDTO]` - basic client info
  - `get_client_with_quotations(client_id: UUID) -> Optional[ClientWithQuotationsDTO]` - includes quotation history
  - `list_clients(filters, page, limit, sort_by) -> ClientListResponseDTO`
  - `update_client(client_id: UUID, request: ClientUpdateDTO) -> Optional[ClientResponseDTO]`
  - `delete_client(client_id: UUID) -> bool` - soft delete (set status to inactive)
  - `search_clients(query: str) -> List[ClientResponseDTO]`
- Implement pipeline methods:
  - `get_pipeline() -> Dict[str, List[ClientResponseDTO]]` - group clients by status
  - `update_status(client_id: UUID, new_status: str, notes: str, changed_by: UUID) -> ClientResponseDTO` - update status with history
  - `get_status_history(client_id: UUID) -> List[StatusHistoryResponseDTO]`
- Implement business rules:
  - Validate `project_deadline` is in future when creating/updating
  - Prevent deletion of clients with active quotations (similar to supplier/products pattern)
- Implement timing feasibility:
  - `calculate_timing_feasibility(client_id: UUID, product_lead_time_days: int) -> TimingFeasibilityDTO`
  - Consider: production lead time + shipping transit days vs project_deadline
  - Query freight_rates for transit_days based on client location
- Create singleton: `client_service = ClientService()`

### Task 5: Create Client API Routes in apps/Server/app/api/client_routes.py
- Create router with `APIRouter(tags=["Clients"])`
- Implement endpoints following `supplier_routes.py` pattern:
  - `GET /` - List clients with pagination and filters
  - `POST /` - Create client
  - `GET /search` - Search clients
  - `GET /pipeline` - Get clients grouped by status
  - `GET /{client_id}` - Get client by ID
  - `GET /{client_id}/quotations` - Get client with quotation history
  - `PUT /{client_id}` - Update client
  - `DELETE /{client_id}` - Soft delete (admin/manager only)
  - `POST /{client_id}/status` - Update status with notes (records history)
  - `GET /{client_id}/status-history` - Get status change history
  - `GET /{client_id}/timing-feasibility` - Calculate timing feasibility
- Apply authentication with `Depends(get_current_user)` on all routes
- Apply `Depends(require_roles(['admin', 'manager']))` on delete route
- Use consistent error handling (400 for validation, 404 for not found)
- Use consistent logging pattern: `print(f"INFO [ClientRoutes]: ...")`

### Task 6: Register Routes in main.py
- Import client router: `from app.api.client_routes import router as client_router`
- Register router: `app.include_router(client_router, prefix="/api/clients")`

### Task 7: Create Unit Tests in apps/Server/tests/test_client_service.py
- Test CRUD operations:
  - `test_create_client_success`
  - `test_create_client_with_all_fields`
  - `test_get_client_not_found`
  - `test_list_clients_pagination`
  - `test_list_clients_filters`
  - `test_update_client_success`
  - `test_delete_client_with_active_quotations_fails`
- Test pipeline operations:
  - `test_get_pipeline_groups_by_status`
  - `test_update_status_records_history`
  - `test_get_status_history`
- Test business rules:
  - `test_project_deadline_must_be_future`
  - `test_timing_feasibility_calculation`
- Test search:
  - `test_search_clients_by_company_name`
  - `test_search_clients_by_email`

### Task 8: Run Validation Commands
- Run validation commands to ensure feature works correctly with zero regressions

## Testing Strategy

### Unit Tests
- Mock repository for service layer testing
- Test all CRUD operations with valid and invalid inputs
- Test pipeline grouping logic
- Test status history recording
- Test timing feasibility calculations
- Test business rule enforcement (future deadline, active quotations check)

### Edge Cases
- Empty pipeline (no clients in any status)
- Client with no quotation history
- Timing feasibility with missing freight rates
- Status update to same status (should still record history)
- Client deletion when already inactive
- Search with special characters
- Pagination boundary conditions (page 0, negative limit)
- Project deadline exactly today (invalid - must be future)

## Acceptance Criteria
- [ ] CRUD operations working for clients with all new CRM fields
- [ ] Pipeline grouping returns clients organized by status
- [ ] Status history is recorded on every status change
- [ ] Status history can be retrieved for any client
- [ ] Timing validation correctly compares lead times vs project deadline
- [ ] Cannot create client with past project_deadline
- [ ] Cannot delete client with active quotations
- [ ] All API endpoints require authentication
- [ ] Delete endpoint requires admin/manager role
- [ ] All unit tests pass
- [ ] Static analysis passes (ruff check)
- [ ] Server tests pass (pytest)
- [ ] Server builds and starts successfully

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && source .venv/bin/activate && .venv/bin/ruff check .` - Run linter to validate code style
- `cd apps/Server && source .venv/bin/activate && .venv/bin/pytest tests/ -v --tb=short` - Run all Server tests including new client service tests
- `cd apps/Server && source .venv/bin/activate && python -c "from app.services.client_service import client_service; print('Service imports successfully')"` - Verify service module imports
- `cd apps/Server && source .venv/bin/activate && python -c "from app.api.client_routes import router; print('Routes import successfully')"` - Verify routes module imports
- `cd apps/Server && source .venv/bin/activate && python -c "from main import app; print('Main app imports successfully')"` - Verify main app with new routes imports

## Notes
- The existing `ClientRepository` class in `kompass_repository.py` already has basic CRUD operations implemented - extend rather than replace
- The `client_repository` singleton already exists at line 3761 of `kompass_repository.py`
- Follow the `SupplierService` pattern closely for consistency
- The `ClientStatus` enum already exists with values: active, inactive, prospect
- Consider adding more statuses later (e.g., qualified, negotiation, closed_won, closed_lost) but start with existing enum
- Timing feasibility is calculated per-request based on current freight rates and product lead times
- Status history uses `changed_by` from the authenticated user (passed from API route)
- Source field helps track lead origin for marketing analytics
