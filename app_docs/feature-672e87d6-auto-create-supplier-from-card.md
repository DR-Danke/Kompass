# Auto-Create Supplier from Business Card

**ADW ID:** 672e87d6
**Date:** 2026-03-09
**Specification:** specs/issue-142-adw-672e87d6-sdlc_planner-auto-create-supplier-from-card.md

## Overview

Adds one-click supplier creation from AI-extracted business card data on the Card Capture page. When a business card has been extracted, users can click "Crear Proveedor" to auto-create a supplier record with trade fair metadata, duplicate detection by email/phone, and automatic capture-to-supplier linking.

## What Was Built

- **Backend endpoint** `POST /api/extract/business-cards/{id}/create-supplier` for creating suppliers from extracted cards
- **Duplicate detection** by email (case-insensitive) and phone before creation
- **Trade fair metadata** stored on suppliers: `source`, `fair_name`, `capture_date`, `wechat_id`
- **Source filter** on `GET /api/suppliers?source=trade_fair` to list trade-fair-sourced suppliers
- **Frontend UI** with "Crear Proveedor" button, duplicate warning alerts, success confirmation, and "Proveedor vinculado" chip
- **Backend unit tests** for the service and route layers
- **E2E test spec** for the full workflow

## Technical Implementation

### Files Modified

- `apps/Server/app/models/kompass_dto.py`: Added `SupplierFromCardResultDTO` with success/duplicate/supplier fields
- `apps/Server/app/repository/kompass_repository.py`: Added `find_duplicate_supplier()`, `create_with_trade_fair_metadata()`, and `source` filter to `get_all_with_filters()`
- `apps/Server/app/services/supplier_service.py`: Added `create_supplier_from_card()` orchestration method and `source` param to `list_suppliers()`
- `apps/Server/app/api/extraction_routes.py`: Added `POST /business-cards/{capture_id}/create-supplier` endpoint
- `apps/Server/app/api/supplier_routes.py`: Added `source` query parameter to `list_suppliers()` route
- `apps/Client/src/types/kompass.ts`: Added `SupplierFromCardResult` interface
- `apps/Client/src/services/kompassService.ts`: Added `createSupplierFromCard()` to `businessCardService`
- `apps/Client/src/pages/kompass/CardCapturePage.tsx`: Added create supplier button, duplicate warnings, success alerts, and linked chip
- `apps/Server/tests/services/test_supplier_service.py`: Unit tests for `create_supplier_from_card()`
- `apps/Server/tests/test_extraction_routes.py`: API endpoint tests
- `.claude/commands/e2e/test_auto_create_supplier_from_card.md`: E2E test spec

### Key Changes

- **Orchestration flow**: `create_supplier_from_card()` retrieves capture → validates status is `extracted` → extracts fields → checks duplicates → creates supplier with trade fair metadata → links capture → updates status to `confirmed`
- **Duplicate detection**: `find_duplicate_supplier()` queries by `LOWER(contact_email)` OR `contact_phone`, returning the first match with extended fields
- **Trade fair metadata**: New `create_with_trade_fair_metadata()` repository method extends the base `create()` with `source`, `fair_name`, `capture_date`, `wechat_id` columns — kept separate to avoid breaking existing supplier creation
- **Supplier name resolution**: Uses `company_name` if available, falls back to `contact_name`, raises error if neither exists
- **Invalid email handling**: Silently nullifies invalid emails rather than failing creation

## How to Use

1. Navigate to **Captura Tarjetas** (Card Capture) page
2. Upload a business card photo with a trade fair name
3. Wait for AI extraction to complete (status becomes `extracted`)
4. Click **"Crear Proveedor"** button on the extracted card
5. If no duplicate is found: supplier is created, capture shows "Proveedor vinculado" chip
6. If a duplicate is detected: a warning alert shows the existing supplier name, capture is marked as rejected
7. Filter trade fair suppliers via **Proveedores** page using the `source=trade_fair` filter (API level)

## Configuration

No new environment variables or configuration required. Uses existing database columns (`source`, `fair_name`, `capture_date`, `wechat_id` on `suppliers` table) and capture status values (`confirmed`, `rejected`).

## Testing

- **Unit tests**: `cd apps/Server && python -m pytest tests/services/test_supplier_service.py -v --tb=short`
- **API tests**: `cd apps/Server && python -m pytest tests/test_extraction_routes.py -v --tb=short`
- **Type check**: `cd apps/Client && npx tsc --noEmit`
- **E2E**: Run `/e2e:test_auto_create_supplier_from_card` slash command

## Notes

- Pipeline status defaults to `"contacted"` for trade fair suppliers
- Country defaults to `"China"` for all card-created suppliers
- The `duplicate_detected` status is not in the DB CHECK constraint, so `rejected` is used instead
- Concurrent creation requests are guarded by checking `supplier_id` on the capture before proceeding
