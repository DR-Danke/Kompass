# Niche Service CRUD

**ADW ID:** 15dd75a7
**Date:** 2026-01-31
**Specification:** specs/issue-12-adw-15dd75a7-niche-service-crud.md

## Overview

Implements a complete CRUD service for managing client niches (client type classifications) in the Kompass Portfolio & Quotation system. Niches categorize clients by business type (e.g., Constructoras, Hoteles, Retailers) for targeted portfolio management. The service includes client count tracking, delete validation to prevent orphaning clients, and a seed script for default niches.

## What Was Built

- **NicheService** - Business logic layer with CRUD operations and client count tracking
- **Niche API Routes** - RESTful endpoints at `/api/niches` with authentication and RBAC
- **Repository Extensions** - New methods for client counting and aggregation queries
- **NicheWithClientCountDTO** - DTO for responses that include client counts
- **Seed Script** - Idempotent script to populate default niches
- **Unit Tests** - Comprehensive test coverage for NicheService
- **Integration Tests** - API route tests with authentication and RBAC validation

## Technical Implementation

### Files Modified

- `apps/Server/app/models/kompass_dto.py`: Added `NicheWithClientCountDTO` class
- `apps/Server/app/repository/kompass_repository.py`: Added `count_clients_by_niche()`, `has_clients()`, and `get_all_with_client_counts()` methods to NicheRepository
- `apps/Server/main.py`: Registered niche router at `/api/niches`

### New Files Created

- `apps/Server/app/services/niche_service.py`: NicheService class with singleton instance
- `apps/Server/app/api/niche_routes.py`: FastAPI router with 5 endpoints
- `apps/Server/database/seed_niches.py`: Seed script for default niches
- `apps/Server/tests/services/test_niche_service.py`: Unit tests (309 lines)
- `apps/Server/tests/api/test_niche_routes.py`: Integration tests (495 lines)

### Key Changes

- **NicheService** follows existing patterns from TagService (count tracking) and CategoryService (delete validation)
- **Delete validation** raises `ValueError` if niche has associated clients, preventing orphaned client records
- **List endpoint** returns all niches with their client counts via efficient LEFT JOIN query
- **RBAC enforcement**: GET endpoints require authentication; POST/PUT/DELETE require admin or manager role
- **Soft delete** pattern: delete operation sets `is_active=False` rather than removing records

## How to Use

1. **List all niches with client counts:**
   ```
   GET /api/niches/
   Authorization: Bearer <token>
   ```

2. **Get a specific niche:**
   ```
   GET /api/niches/{niche_id}
   Authorization: Bearer <token>
   ```

3. **Create a new niche (admin/manager only):**
   ```
   POST /api/niches/
   Authorization: Bearer <token>
   Content-Type: application/json
   {
     "name": "New Niche",
     "description": "Optional description",
     "is_active": true
   }
   ```

4. **Update a niche (admin/manager only):**
   ```
   PUT /api/niches/{niche_id}
   Authorization: Bearer <token>
   Content-Type: application/json
   {
     "name": "Updated Name",
     "description": "Updated description",
     "is_active": true
   }
   ```

5. **Delete a niche (admin/manager only):**
   ```
   DELETE /api/niches/{niche_id}
   Authorization: Bearer <token>
   ```
   Returns 409 Conflict if the niche has associated clients.

6. **Seed default niches:**
   ```bash
   cd apps/Server
   source .venv/bin/activate
   python -m database.seed_niches
   ```

## Configuration

No additional environment variables required. Uses existing database connection and JWT authentication configuration.

## Testing

Run unit tests:
```bash
cd apps/Server && source .venv/bin/activate
python -m pytest tests/services/test_niche_service.py -v --tb=short
```

Run API integration tests:
```bash
cd apps/Server && source .venv/bin/activate
python -m pytest tests/api/test_niche_routes.py -v --tb=short
```

Run all server tests:
```bash
cd apps/Server && source .venv/bin/activate
python -m pytest tests/ -v --tb=short
```

## Notes

- Default niches (Spanish names as per requirements): Constructoras, Estudios de Arquitectura, Desarrolladores, Hoteles, Operadores Rentas Cortas, Retailers
- Seed script is idempotent using `INSERT ... ON CONFLICT DO NOTHING`
- Backend-only feature - no frontend changes required for this phase
- NicheRepository CRUD methods already existed; this feature added client counting and aggregation methods
