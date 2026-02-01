# Pricing Configuration API Routes

**ADW ID:** b6ca4629
**Date:** 2026-02-01
**Specification:** specs/issue-18-adw-b6ca4629-pricing-config-api-routes.md

## Overview

This feature implements FastAPI routes for the pricing configuration module in the Kompass Portfolio & Quotation system. The routes expose REST API endpoints for managing HS codes (with tariff/duty rates), freight rates (with validity tracking and origin/destination filtering), and global pricing settings. The implementation integrates with the existing `pricing_service` singleton and follows established patterns from other route modules.

## What Was Built

- **HS Code Endpoints**: Full CRUD operations for Harmonized System codes including search/pagination
- **Freight Rate Endpoints**: CRUD operations with origin/destination filtering and active rate lookup
- **Pricing Settings Endpoints**: Get/update operations for global pricing configuration
- **Role-Based Access Control**: Admin/manager restrictions on write operations, admin-only for settings updates
- **Comprehensive Unit Tests**: 922 lines of tests covering all endpoints, authentication, and RBAC

## Technical Implementation

### Files Modified

- `apps/Server/app/api/pricing_routes.py`: New FastAPI router (391 lines) implementing all pricing configuration endpoints
- `apps/Server/main.py`: Router registration with `/api/pricing` prefix
- `apps/Server/tests/api/test_pricing_routes.py`: Comprehensive unit tests (922 lines)

### Key Changes

- **HS Code endpoints** at `/api/pricing/hs-codes`:
  - `GET /hs-codes` - List/search with pagination (page, limit, search params)
  - `POST /hs-codes` - Create new HS code (authenticated)
  - `GET /hs-codes/{id}` - Get by UUID
  - `PUT /hs-codes/{id}` - Update (admin/manager only)
  - `DELETE /hs-codes/{id}` - Delete (admin/manager only)

- **Freight Rate endpoints** at `/api/pricing/freight-rates`:
  - `GET /freight-rates` - List with origin/destination filters and pagination
  - `POST /freight-rates` - Create new rate (authenticated)
  - `GET /freight-rates/active` - Get active rate for route (origin/destination query params)
  - `PUT /freight-rates/{id}` - Update rate (admin/manager only)
  - `DELETE /freight-rates/{id}` - Soft delete via is_active=False (admin/manager only)

- **Pricing Settings endpoints** at `/api/pricing/settings`:
  - `GET /settings` - Get all pricing settings (authenticated)
  - `PUT /settings/{key}` - Update individual setting (admin only)

### Authentication & Authorization

All endpoints require authentication via `get_current_user` dependency. Write operations (POST, PUT, DELETE) for HS codes and freight rates require `admin` or `manager` roles. Settings updates are restricted to `admin` role only.

## How to Use

1. **List HS Codes with Search**:
   ```bash
   GET /api/pricing/hs-codes?search=8471&page=1&limit=20
   Authorization: Bearer <token>
   ```

2. **Create HS Code**:
   ```bash
   POST /api/pricing/hs-codes
   Authorization: Bearer <token>
   Content-Type: application/json

   {
     "code": "8471.30.00",
     "description": "Portable digital computers",
     "tariff_rate": 0.05,
     "duty_rate": 0.10
   }
   ```

3. **Get Active Freight Rate for Route**:
   ```bash
   GET /api/pricing/freight-rates/active?origin=Shanghai&destination=Bogota
   Authorization: Bearer <token>
   ```

4. **Update Pricing Setting** (admin only):
   ```bash
   PUT /api/pricing/settings/default_margin
   Authorization: Bearer <admin-token>
   Content-Type: application/json

   {
     "setting_value": "0.15"
   }
   ```

## Configuration

No additional environment variables required. The routes use the existing `pricing_service` singleton which connects to the configured PostgreSQL database.

## Testing

Run the pricing routes tests:

```bash
cd apps/Server
source .venv/bin/activate
.venv/bin/pytest tests/api/test_pricing_routes.py -v --tb=short
```

Run all server tests:

```bash
.venv/bin/pytest tests/ -v --tb=short
```

Run linting:

```bash
.venv/bin/ruff check app/api/pricing_routes.py
.venv/bin/ruff check tests/api/test_pricing_routes.py
```

## Notes

- The freight rate delete operation implements soft delete by setting `is_active=False` since the pricing service doesn't have an explicit delete method
- The settings endpoint initializes default settings if they don't exist before returning
- HS code delete currently only validates existence (soft delete via is_active field could be added if the hs_codes table supports it)
- The active freight rate lookup uses validity dates to determine the currently active rate for a route
