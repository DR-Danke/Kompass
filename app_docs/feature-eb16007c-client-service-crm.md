# Client Service CRM

**ADW ID:** eb16007c
**Date:** 2026-01-31
**Specification:** specs/issue-11-adw-eb16007c-sdlc_planner-client-service-crm.md

## Overview

A comprehensive client service for CRM (Customer Relationship Management) functionality in the Kompass Portfolio & Quotation Automation System. This feature provides business logic for managing clients throughout their lifecycle, from prospect to active customer, including pipeline management, status history tracking, and timing feasibility calculations.

## What Was Built

- **ClientService class** with core CRUD operations and business logic
- **Client status history tracking** for audit trail purposes
- **Pipeline view** that groups clients by status (prospect, active, inactive)
- **Timing feasibility calculator** to validate project deadlines against production and shipping timelines
- **Client source tracking** for lead origin analytics (website, referral, cold_call, trade_show, linkedin, other)
- **CRM-specific database schema extensions** including `client_status_history` table
- **REST API endpoints** for all client operations with authentication and RBAC
- **Comprehensive unit tests** covering CRUD, pipeline, status history, and timing feasibility

## Technical Implementation

### Files Modified

- `apps/Server/database/schema.sql`: Added CRM fields to clients table (`assigned_to`, `source`, `project_deadline`) and created `client_status_history` table with indexes
- `apps/Server/app/models/kompass_dto.py`: Added 7 new DTOs (`ClientSource` enum, `ClientStatusChangeDTO`, `StatusHistoryResponseDTO`, `QuotationSummaryDTO`, `ClientWithQuotationsDTO`, `PipelineResponseDTO`, `TimingFeasibilityDTO`)
- `apps/Server/app/repository/kompass_repository.py`: Extended `ClientRepository` with new methods for status history, pipeline, and quotation summary
- `apps/Server/main.py`: Registered new client routes at `/api/clients` prefix

### Files Created

- `apps/Server/app/services/client_service.py`: Main service class (567 lines) with business logic
- `apps/Server/app/api/client_routes.py`: REST API endpoints (410 lines) with authentication
- `apps/Server/tests/test_client_service.py`: Unit tests (583 lines) covering all functionality

### Key Changes

- **Pipeline Grouping**: `get_pipeline()` method groups clients by status for sales funnel visualization
- **Status History Tracking**: Every status change is recorded with old/new status, notes, and user who made the change
- **Timing Feasibility**: Calculates if project deadlines are achievable based on production lead time + shipping transit days
- **Soft Delete Protection**: Clients with active quotations cannot be deleted
- **Project Deadline Validation**: Deadlines must be in the future when creating or updating clients
- **Email Validation**: Validates email format using regex pattern

## How to Use

### List Clients with Filtering
```
GET /api/clients?status=active&source=referral&page=1&limit=20
```

### Create a Client
```
POST /api/clients
{
  "company_name": "Acme Corp",
  "contact_name": "John Doe",
  "email": "john@acme.com",
  "status": "prospect",
  "source": "website",
  "project_deadline": "2026-06-15",
  "assigned_to": "uuid-of-sales-rep"
}
```

### Get Pipeline View
```
GET /api/clients/pipeline
```
Returns clients grouped by status:
```json
{
  "prospect": [...],
  "active": [...],
  "inactive": [...]
}
```

### Update Client Status with History
```
POST /api/clients/{client_id}/status
{
  "new_status": "active",
  "notes": "Contract signed"
}
```

### Get Status History
```
GET /api/clients/{client_id}/status-history
```

### Calculate Timing Feasibility
```
GET /api/clients/{client_id}/timing-feasibility?product_lead_time_days=30
```
Returns:
```json
{
  "is_feasible": true,
  "project_deadline": "2026-06-15",
  "production_lead_time_days": 30,
  "shipping_transit_days": 25,
  "total_lead_time_days": 55,
  "days_until_deadline": 135,
  "buffer_days": 80,
  "message": "Feasible with 80 days buffer"
}
```

### Get Client with Quotation Summary
```
GET /api/clients/{client_id}/quotations
```

### Delete Client (Admin/Manager Only)
```
DELETE /api/clients/{client_id}
```
Fails if client has active quotations.

## Configuration

No additional environment variables required. The service uses existing database and authentication configuration.

## Testing

Run the unit tests:
```bash
cd apps/Server
source .venv/bin/activate
.venv/bin/pytest tests/test_client_service.py -v --tb=short
```

The test suite covers:
- CRUD operations (create, read, update, delete)
- Pipeline grouping by status
- Status history recording and retrieval
- Timing feasibility calculations
- Business rule enforcement (future deadline, active quotations check)
- Search functionality by company name and email
- Edge cases (empty pipeline, missing freight rates, same status updates)

## Notes

- All endpoints require authentication via `get_current_user` dependency
- Delete endpoint requires admin or manager role
- Status history uses `changed_by` from the authenticated user
- Timing feasibility uses freight rates to determine shipping transit days (defaults to 30 days if no matching rate found)
- The `ClientSource` enum tracks lead origin for marketing analytics
- Client search matches against company_name, contact_name, and email fields
