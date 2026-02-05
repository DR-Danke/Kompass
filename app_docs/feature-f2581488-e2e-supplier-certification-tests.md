# E2E Supplier Certification Tests

**ADW ID:** f2581488
**Date:** 2026-02-05
**Specification:** specs/issue-86-adw-f2581488-sdlc_planner-e2e-supplier-certification-tests.md

## Overview

Comprehensive end-to-end test coverage for the Supplier Certification feature, including API route tests for all audit endpoints, service unit tests for edge cases, and a detailed E2E test command covering the complete certification workflow from audit upload through classification and filtering.

## What Was Built

- **API Route Tests** - Complete test coverage for all `/api/suppliers/{supplier_id}/audits/*` endpoints with RBAC verification
- **Service Edge Case Tests** - Additional unit tests for status transitions and classification edge cases
- **E2E Test Command** - Comprehensive manual/automated test specification for the full certification workflow

## Technical Implementation

### Files Modified

- `apps/Server/tests/api/test_audit_routes.py`: New file with 981 lines covering 7 test classes and 30+ test cases for audit API endpoints
- `apps/Server/tests/test_audit_service.py`: Added 267 lines with 3 new test classes for edge cases
- `.claude/commands/e2e/test_supplier_certification_workflow.md`: New 631-line comprehensive E2E test command
- `playwright-mcp-config.json`: Minor configuration update

### Key Changes

- **Upload Endpoint Tests**: Validates PDF upload, file type rejection, size limits (25MB), filename requirements, and RBAC (viewers forbidden)
- **List/Get Endpoint Tests**: Pagination, empty results, audit retrieval, and supplier ownership validation
- **Reprocess/Delete Tests**: RBAC enforcement (admin/manager only), 404/400 error handling
- **Classify/Override Tests**: Extraction completion requirements, notes validation, invalid grade rejection
- **Status Transition Tests**: Verifies `pending -> processing -> completed/failed` transitions
- **Classification Edge Cases**: Handles empty markets_served, empty certifications, and trader vs manufacturer scoring

## How to Use

### Running API Route Tests

```bash
cd apps/Server
../.venv/bin/pytest tests/api/test_audit_routes.py -v --tb=short
```

### Running Service Tests

```bash
cd apps/Server
../.venv/bin/pytest tests/test_audit_service.py -v --tb=short
```

### Running E2E Tests

The E2E test command can be executed via:

```bash
# Manual execution using the test command
/e2e:test_supplier_certification_workflow

# Or using Puppeteer script from the command documentation
```

### Running All Tests

```bash
cd apps/Server
../.venv/bin/pytest tests/ -v --tb=short
```

## Configuration

No additional configuration required. Tests use mocked dependencies and don't require database access.

## Testing

The test suite covers:

| Test Class | Tests | Coverage |
|------------|-------|----------|
| TestUploadAudit | 6 | PDF validation, size limits, RBAC |
| TestListSupplierAudits | 4 | Pagination, empty results, viewer access |
| TestGetAudit | 3 | Retrieval, 404, supplier ownership |
| TestReprocessAudit | 6 | RBAC (admin/manager), error handling |
| TestDeleteAudit | 5 | RBAC, 204 response, error handling |
| TestClassifyAudit | 5 | Extraction requirements, supplier status |
| TestOverrideClassification | 7 | Notes validation, invalid grades, RBAC |
| TestStatusTransitions | 2 | Failed/completed status handling |
| TestClassificationEdgeCases | 3 | Empty markets, empty certs, trader scoring |

## Notes

- RBAC roles tested: `viewer` (read-only), `user` (upload/classify), `admin`/`manager` (full access)
- File upload tests use mock PDF content since actual AI extraction requires external APIs
- The 25MB file size limit is validated at the route level
- Classification grades limited to A, B, C - invalid grades (D, X) return 400/422
- E2E test includes 41 detailed steps with screenshot checkpoints for visual verification
