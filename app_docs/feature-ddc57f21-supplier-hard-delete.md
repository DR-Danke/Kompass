# Supplier Hard Delete

**ADW ID:** ddc57f21
**Date:** 2026-02-07
**Specification:** specs/issue-107-adw-ddc57f21-sdlc_planner-delete-suppliers-hard-delete.md

## Overview

Converted the supplier delete functionality from a soft delete (setting status to inactive) to a hard delete that permanently removes the supplier and all associated data from the database. This enables users to fully clean up test suppliers and their associated audit reports, products, and related records.

## What Was Built

- Hard delete repository method with transactional cascade ordering
- Delete preview endpoint to show users what will be removed before confirming
- Enhanced frontend confirmation dialog with permanent deletion warning and cascade counts
- Updated API response to include counts of deleted associated records

## Technical Implementation

### Files Modified

- `apps/Server/app/repository/kompass_repository.py`: Replaced soft delete (`UPDATE status = inactive`) with hard delete using proper cascade ordering within a single transaction. Added `get_delete_preview()` method.
- `apps/Server/app/services/supplier_service.py`: Removed the active products check that blocked deletion. Updated `delete_supplier()` to return deletion counts. Added `get_delete_preview()` method.
- `apps/Server/app/api/supplier_routes.py`: Updated `DELETE /suppliers/{id}` to return deletion counts. Added `GET /suppliers/{id}/delete-preview` endpoint.
- `apps/Client/src/pages/kompass/SuppliersPage.tsx`: Enhanced delete confirmation dialog with warning alert, cascade preview (products/audits counts), and "Delete Permanently" button.
- `apps/Client/src/services/kompassService.ts`: Added `getDeletePreview()` method. Updated `delete()` to return `SupplierDeleteResponse`.
- `apps/Client/src/types/kompass.ts`: Added `SupplierDeletePreview` and `SupplierDeleteResponse` interfaces.
- `apps/Server/tests/services/test_supplier_service.py`: Updated tests for hard delete behavior and delete preview.
- `apps/Server/tests/api/test_supplier_routes.py`: Updated tests for new response format and delete-preview endpoint.
- `.claude/commands/e2e/test_delete_supplier_hard.md`: New E2E test spec for validating hard delete flow.

### Key Changes

- **Cascade ordering**: The repository clears `latest_audit_id` (circular FK) first, then deletes products (which CASCADE to images, tags, portfolio items and SET NULL on quotation items), then deletes the supplier itself (which CASCADE deletes audits). All within a single transaction.
- **Delete preview**: New `GET /suppliers/{id}/delete-preview` endpoint returns `supplier_name`, `products_count`, and `audits_count` so the frontend can display what will be removed.
- **No more product blocking**: Previously, suppliers with active products could not be deleted. Now all associated products are deleted as part of the cascade.
- **Quotation preservation**: `quotation_items.product_id` is set to NULL on product deletion, preserving quotation history (product name, SKU, pricing data remain intact).

## How to Use

1. Navigate to the **Suppliers** page
2. Click the delete action on a supplier row
3. A confirmation dialog appears showing:
   - A warning that the action is irreversible
   - The number of products and audit reports that will be deleted
4. Click **Delete Permanently** to confirm
5. The supplier and all associated data are removed from the database

## Configuration

No additional configuration required. The feature uses existing RBAC — only `admin` and `manager` roles can delete suppliers.

## Testing

- **Unit tests**: `cd apps/Server && .venv/bin/pytest tests/services/test_supplier_service.py -v --tb=short -k delete`
- **API route tests**: `cd apps/Server && .venv/bin/pytest tests/api/test_supplier_routes.py -v --tb=short -k delete`
- **Frontend type check**: `cd apps/Client && npx tsc --noEmit`
- **E2E test**: Run `/test_e2e` with the `e2e/test_delete_supplier_hard.md` spec

## Notes

- The database schema's `ON DELETE CASCADE` on `supplier_audits.supplier_id` handles audit cleanup automatically when the supplier is deleted.
- `products.supplier_id` has `ON DELETE RESTRICT`, which is why products must be explicitly deleted before the supplier.
- The circular FK between `suppliers.latest_audit_id` and `supplier_audits.id` must be cleared (SET NULL) before deletion to avoid constraint violations.
