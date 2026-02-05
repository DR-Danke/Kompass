# Supplier Audit and Certification API Routes

**ADW ID:** 9b1fc60c
**Date:** 2026-02-04
**Specification:** specs/issue-82-adw-9b1fc60c-supplier-audit-api-routes.md

## Overview

This feature adds REST API endpoints for managing supplier certification and pipeline status workflows. It enables procurement managers to filter suppliers by certification grades (A/B/C), track suppliers through the onboarding pipeline, update pipeline status, and retrieve consolidated certification summaries with audit history.

## What Was Built

- `GET /api/suppliers/certified` - List only certified suppliers with optional grade filtering
- `GET /api/suppliers/pipeline/{status}` - List suppliers by pipeline status
- `PUT /api/suppliers/{supplier_id}/pipeline-status` - Update supplier pipeline status (admin/manager only)
- `GET /api/suppliers/{supplier_id}/certification` - Get certification summary with latest audit info
- New DTOs for request/response handling
- Repository methods for certification and pipeline queries
- Comprehensive unit tests for all endpoints

## Technical Implementation

### Files Modified

- `apps/Server/app/api/supplier_routes.py`: Added 4 new endpoint handlers for certification and pipeline operations
- `apps/Server/app/models/kompass_dto.py`: Added `SupplierPipelineStatusUpdateDTO` and `SupplierCertificationSummaryDTO` classes
- `apps/Server/app/services/supplier_service.py`: Added business logic methods for listing, filtering, and updating certification data
- `apps/Server/app/repository/kompass_repository.py`: Added 5 new repository methods for database operations with certification fields
- `apps/Server/tests/test_supplier_certification_routes.py`: Created 447 lines of unit tests covering all endpoints and edge cases

### Key Changes

- **Route ordering**: Static routes (`/certified`, `/pipeline/{status}`) are placed before dynamic routes (`/{supplier_id}`) to prevent routing conflicts
- **Extended row mapping**: Added `_row_to_dict_extended()` method to include certification fields (`certification_status`, `pipeline_status`, `latest_audit_id`, `certified_at`)
- **Audit join**: The certification summary endpoint joins with `supplier_audits` table to include `ai_classification` and `manual_classification`
- **RBAC enforcement**: Pipeline status update requires admin or manager role
- **Grade validation**: The certified endpoint validates grade parameter (A, B, C only)

## How to Use

### List Certified Suppliers

```bash
# Get all certified suppliers
GET /api/suppliers/certified

# Filter by grade
GET /api/suppliers/certified?grade=A
GET /api/suppliers/certified?grade=B
GET /api/suppliers/certified?grade=C

# With pagination
GET /api/suppliers/certified?page=1&limit=20
```

### List Suppliers by Pipeline Status

```bash
# Valid statuses: contacted, potential, quoted, certified, active, inactive
GET /api/suppliers/pipeline/contacted
GET /api/suppliers/pipeline/certified?page=1&limit=20
```

### Update Pipeline Status

```bash
# Requires admin or manager role
PUT /api/suppliers/{supplier_id}/pipeline-status
Content-Type: application/json

{
    "pipeline_status": "quoted"
}
```

### Get Certification Summary

```bash
GET /api/suppliers/{supplier_id}/certification

# Response includes:
# - Basic supplier info (id, name, code, status, country)
# - Certification status and pipeline status
# - certified_at timestamp
# - Latest audit info (audit_id, audit_date, ai_classification, manual_classification)
```

## Configuration

No additional configuration required. The endpoints use existing authentication and RBAC infrastructure.

## Testing

Run the unit tests:

```bash
cd apps/Server
.venv/bin/pytest tests/test_supplier_certification_routes.py -v
```

Test coverage includes:
- Authentication requirements for all endpoints
- RBAC enforcement for pipeline status update
- Empty results handling
- Grade filtering validation
- Invalid status handling (400 errors)
- Not found scenarios (404 errors)
- Suppliers with and without audit history

## Notes

- The certification status values are: `uncertified`, `certified_a`, `certified_b`, `certified_c`
- The pipeline status values are: `contacted`, `potential`, `quoted`, `certified`, `active`, `inactive`
- Suppliers without audits will have null values for `latest_audit_id`, `latest_audit_date`, `ai_classification`, and `manual_classification` in the certification summary
- The `/certified` endpoint only returns suppliers with `certified_a`, `certified_b`, or `certified_c` status
