# Client API Routes

**ADW ID:** 559c0462
**Date:** 2026-01-31
**Specification:** specs/issue-14-adw-559c0462-sdlc_planner-client-api-routes.md

## Overview

This feature aligns the Client API routes for REST compliance and adds a history endpoint alias for backward compatibility. The implementation updates the status endpoint HTTP method from POST to PUT and adds a new `/history` alias endpoint.

## What Was Built

- Changed status update endpoint from POST to PUT for REST compliance
- Added `/history` alias endpoint for backward compatibility with `/status-history`
- Comprehensive integration tests for all 9 client API endpoints

## Technical Implementation

### Files Modified

- `apps/Server/app/api/client_routes.py`: Updated status endpoint method and added history alias
- `apps/Server/tests/api/test_client_routes.py`: New integration test suite (939 lines)

### Key Changes

- `PUT /{client_id}/status` replaces `POST /{client_id}/status` for updating client status (REST compliance - PUT is idempotent and appropriate for updates)
- Added `GET /{client_id}/history` endpoint that delegates to the existing `get_status_history` function, providing an alias for `/status-history`
- Integration tests cover all 9 endpoints with authentication, authorization, and edge case testing:
  - `GET /api/clients` - List with pagination
  - `POST /api/clients` - Create client
  - `GET /api/clients/{id}` - Get client detail
  - `PUT /api/clients/{id}` - Update client
  - `DELETE /api/clients/{id}` - Delete (admin/manager only)
  - `GET /api/clients/pipeline` - Pipeline view
  - `PUT /api/clients/{id}/status` - Update status
  - `GET /api/clients/{id}/history` - Status history alias
  - `GET /api/clients/{id}/quotations` - Quotation summary

## How to Use

1. **Update Client Status** (using PUT instead of POST):
   ```bash
   PUT /api/clients/{client_id}/status
   Content-Type: application/json
   Authorization: Bearer <token>

   {"new_status": "active", "notes": "Converted to active client"}
   ```

2. **Get Status History** (either endpoint works):
   ```bash
   # Original endpoint
   GET /api/clients/{client_id}/status-history

   # New alias
   GET /api/clients/{client_id}/history
   ```

## Configuration

No additional configuration required. The endpoints use existing authentication and RBAC dependencies.

## Testing

Run integration tests:
```bash
cd apps/Server && source .venv/bin/activate && python -m pytest tests/api/test_client_routes.py -v --tb=short
```

Test coverage includes:
- Authentication requirements for all endpoints
- RBAC enforcement (admin/manager only for delete)
- 404 responses for non-existent clients
- 400 responses for validation errors
- Empty result handling for lists and history

## Notes

- The `/status-history` endpoint remains available; `/history` is an alias for backward compatibility
- All endpoints require JWT authentication via the `get_current_user` dependency
- DELETE endpoint enforces admin/manager role via `require_roles` RBAC dependency
