# Feature: Add API routes for supplier audits and certification

## Metadata
issue_number: `82`
adw_id: `9b1fc60c`
issue_json: `{number:82,title:feat: Add API routes for supplier audits and certification,body:...}`

## Feature Description
This feature adds REST API endpoints for managing supplier audits and the certification workflow. The majority of audit endpoints are already implemented in `audit_routes.py`. This feature focuses on adding the remaining supplier certification endpoints to `supplier_routes.py` and ensuring all endpoints are properly integrated and tested.

The certification endpoints will allow users to:
- List certified suppliers (filtered by certification status)
- List suppliers by pipeline status
- Update supplier pipeline status
- Get a certification summary for a specific supplier

## User Story
As a procurement manager
I want to filter and manage suppliers by their certification and pipeline status
So that I can efficiently track supplier qualification progress and focus on certified suppliers

## Problem Statement
While audit endpoints exist for uploading and processing supplier audit documents, there's no way to:
1. Filter suppliers by certification status (A/B/C or uncertified)
2. Filter suppliers by pipeline status in the onboarding workflow
3. Update supplier pipeline status independently
4. Get a consolidated view of a supplier's certification information with audit history

## Solution Statement
Add four new endpoints to `supplier_routes.py`:
1. `GET /api/suppliers/certified` - List only certified suppliers (with optional grade filter)
2. `GET /api/suppliers/pipeline/{status}` - List suppliers by pipeline status
3. `PUT /api/suppliers/{supplier_id}/pipeline-status` - Update pipeline status
4. `GET /api/suppliers/{supplier_id}/certification` - Get certification summary with latest audit info

The implementation will follow existing patterns in the codebase, using the service layer for business logic and the repository layer for data access.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/app/api/supplier_routes.py` - Add new certification and pipeline endpoints here
- `apps/Server/app/api/audit_routes.py` - Reference for existing audit endpoint patterns (already complete)
- `apps/Server/app/api/dependencies.py` - Authentication dependency `get_current_user`
- `apps/Server/app/api/rbac_dependencies.py` - Role-based access control for admin/manager endpoints
- `apps/Server/app/services/supplier_service.py` - Add business logic for new endpoints
- `apps/Server/app/repository/kompass_repository.py` - `SupplierRepository` class needs new query methods
- `apps/Server/app/models/kompass_dto.py` - Contains existing DTOs, may need new response DTOs
- `apps/Server/main.py` - Router registration (audit_router already registered)
- `apps/Server/database/schema.sql` - Reference for database schema with `certification_status` and `pipeline_status` columns
- `apps/Server/tests/test_audit_service.py` - Example test patterns for audit functionality
- `apps/Server/tests/test_classification.py` - Example test patterns for classification

### New Files
- `apps/Server/tests/test_supplier_certification_routes.py` - Unit tests for new certification endpoints

## Implementation Plan
### Phase 1: Foundation
1. Add new DTO classes in `kompass_dto.py` for certification summary response
2. Add repository methods in `kompass_repository.py` for:
   - Get suppliers by certification status
   - Get suppliers by pipeline status
   - Update pipeline status
   - Get supplier with full certification details

### Phase 2: Core Implementation
1. Add service layer methods in `supplier_service.py` for:
   - List certified suppliers
   - List suppliers by pipeline status
   - Update pipeline status
   - Get certification summary
2. Add API route handlers in `supplier_routes.py` for all four endpoints

### Phase 3: Integration
1. Ensure proper route ordering (static routes before dynamic path parameters)
2. Add comprehensive unit tests
3. Validate all endpoints work end-to-end

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add New DTOs to kompass_dto.py
- Add `SupplierPipelineStatusUpdateDTO` for pipeline status update request
- Add `SupplierCertificationSummaryDTO` for certification summary response that includes:
  - Basic supplier info
  - Certification status and tier
  - Pipeline status
  - Latest audit ID and date
  - Certification date
  - Latest audit classification (both AI and manual)

### Step 2: Add Repository Methods to SupplierRepository
- Add `get_by_certification_status()` method to filter by certification status with pagination
- Add `get_by_pipeline_status()` method to filter by pipeline status with pagination
- Add `update_pipeline_status()` method to update only the pipeline_status field
- Add `get_with_certification_details()` method to get supplier with latest audit info joined

### Step 3: Add Service Layer Methods to SupplierService
- Add `list_certified_suppliers()` method that calls repository and converts to DTOs
- Add `list_suppliers_by_pipeline()` method that calls repository and converts to DTOs
- Add `update_pipeline_status()` method with validation
- Add `get_certification_summary()` method that combines supplier and audit data

### Step 4: Add API Route Handlers to supplier_routes.py
- Add `GET /certified` endpoint for listing certified suppliers
  - Query params: `grade` (optional A/B/C), `page`, `limit`
  - Returns `SupplierListResponseDTO`
- Add `GET /pipeline/{status}` endpoint for listing by pipeline status
  - Path param: `status` (contacted/potential/quoted/certified/active/inactive)
  - Query params: `page`, `limit`
  - Returns `SupplierListResponseDTO`
- Add `PUT /{supplier_id}/pipeline-status` endpoint for updating pipeline status
  - Request body: `SupplierPipelineStatusUpdateDTO`
  - Returns `SupplierResponseDTO`
- Add `GET /{supplier_id}/certification` endpoint for certification summary
  - Returns `SupplierCertificationSummaryDTO`

**IMPORTANT:** Place static routes (`/certified`, `/pipeline/{status}`) BEFORE dynamic routes (`/{supplier_id}`) in the file to prevent routing conflicts.

### Step 5: Create Unit Tests
- Create `test_supplier_certification_routes.py` with tests for:
  - List certified suppliers (empty, with results, filtered by grade)
  - List suppliers by pipeline status (all valid statuses)
  - Update pipeline status (success, not found, invalid status)
  - Get certification summary (with audit, without audit, not found)

### Step 6: Run Validation Commands
- Run all validation commands to ensure zero regressions

## Testing Strategy
### Unit Tests
- Test each new endpoint with valid inputs
- Test authentication requirements
- Test RBAC for pipeline status update (admin/manager only)
- Test 404 responses for non-existent suppliers
- Test invalid status values return 400

### Edge Cases
- Supplier with no audits (certification summary should have null audit fields)
- Supplier with multiple audits (should return latest)
- Empty result sets for filtered queries
- Invalid UUID format for supplier_id
- Invalid certification grade filter
- Invalid pipeline status values

## Acceptance Criteria
- [ ] GET /api/suppliers/certified returns only suppliers with certification_status in (certified_a, certified_b, certified_c)
- [ ] GET /api/suppliers/certified?grade=A returns only certified_a suppliers
- [ ] GET /api/suppliers/pipeline/{status} returns suppliers filtered by pipeline_status
- [ ] PUT /api/suppliers/{supplier_id}/pipeline-status updates the pipeline status and returns updated supplier
- [ ] PUT /api/suppliers/{supplier_id}/pipeline-status requires admin or manager role
- [ ] GET /api/suppliers/{supplier_id}/certification returns certification summary with audit data
- [ ] All endpoints require authentication
- [ ] Proper error codes returned (400 for invalid input, 404 for not found)
- [ ] OpenAPI docs automatically updated with new endpoints
- [ ] All existing tests pass
- [ ] New unit tests pass

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` - Run all Server tests
- `cd apps/Server && .venv/bin/ruff check .` - Run linting
- `cd apps/Client && npm run typecheck` - Run Client type check (verify no breaking type changes)
- `cd apps/Client && npm run build` - Run Client build

## Notes
- The existing `audit_routes.py` already has all audit-specific endpoints implemented:
  - POST /api/suppliers/{supplier_id}/audits (upload)
  - GET /api/suppliers/{supplier_id}/audits (list)
  - GET /api/suppliers/{supplier_id}/audits/{audit_id} (get details)
  - POST /api/suppliers/{supplier_id}/audits/{audit_id}/reprocess
  - PUT /api/suppliers/{supplier_id}/audits/{audit_id}/classification (override)
  - DELETE /api/suppliers/{supplier_id}/audits/{audit_id}
  - POST /api/suppliers/{supplier_id}/audits/{audit_id}/classify

- The `audit_router` is already registered at `/api/suppliers` prefix in `main.py`

- The database schema already has `certification_status` and `pipeline_status` columns on the `suppliers` table with proper CHECK constraints and indexes

- The `SupplierRepository._row_to_dict()` method currently returns 14 fields but doesn't include certification fields. Need to update to include `certification_status`, `pipeline_status`, `latest_audit_id`, and `certified_at` in queries that need them.

- The `SupplierResponseDTO` already has `certification_status`, `pipeline_status`, `latest_audit_id`, and `certified_at` fields defined, but the repository `_row_to_dict` method doesn't populate them. This needs to be fixed for the certification endpoints to work correctly.
