# Feature: Delete Suppliers (Hard Delete)

## Metadata
issue_number: `107`
adw_id: `ddc57f21`
issue_json: `{"number":107,"title":"Functionality to delete suppliers","body":"Please add a functionality to delete suppliers. We uploaded a set of test suppliers we need to remove, including the associated audit report. "}`

## Feature Description
Convert the existing supplier delete functionality from a soft delete (setting status to inactive) to a **hard delete** that permanently removes the supplier and all associated data from the database. The user explicitly needs to remove test suppliers and their associated audit reports, which requires actual deletion from the database rather than just hiding them.

The current implementation sets the supplier's `status` to `"inactive"` but the data remains in the database. The user needs the data to be permanently removed, including cascading deletion of related records (supplier audits, products, product images, product tags, portfolio items, and quotation items referencing those products).

## User Story
As an admin or manager
I want to permanently delete suppliers and all their associated data (audits, products)
So that I can clean up test data and remove suppliers that are no longer relevant from the database entirely

## Problem Statement
The current delete functionality only performs a soft delete (setting status to inactive), which leaves the supplier data and all associated records (audits, products) in the database. Users who uploaded test suppliers need to permanently remove them, including associated audit reports, to keep the database clean.

## Solution Statement
Modify the existing delete endpoint to perform a **hard delete** instead of a soft delete. The hard delete will:
1. Clear the supplier's `latest_audit_id` FK reference first (to avoid circular FK constraint)
2. Delete all associated products (which will CASCADE delete product_images, product_tags, portfolio_items, and SET NULL on quotation_items)
3. Delete all associated supplier_audits (already CASCADE from suppliers table)
4. Delete the supplier record itself
5. All within a single database transaction for atomicity
6. Update the frontend confirmation dialog to clearly warn about permanent deletion and list what will be deleted (products count, audits)

## Relevant Files
Use these files to implement the feature:

### Backend
- `apps/Server/app/repository/kompass_repository.py` — Contains `SupplierRepository.delete()` method (line 1472-1475) that currently does soft delete. Must be changed to hard delete with proper cascade handling. Also contains `count_products_by_supplier()` (line 1495-1515) which will be reused for validation.
- `apps/Server/app/services/supplier_service.py` — Contains `delete_supplier()` method (line 281-320) that currently checks for active products and blocks deletion. Must be updated to perform hard delete with cascading and remove the product check restriction (or change it to an informational warning).
- `apps/Server/app/api/supplier_routes.py` — Contains `DELETE /suppliers/{supplier_id}` endpoint (line 406-441). Must be updated to reflect hard delete behavior and return count of deleted associated records.
- `apps/Server/app/models/kompass_dto.py` — May need a new DTO for the delete response to include counts of deleted associated records.
- `apps/Server/database/schema.sql` — Reference for FK constraints. Key constraints:
  - `supplier_audits.supplier_id → suppliers.id ON DELETE CASCADE` (auto-handled)
  - `products.supplier_id → suppliers.id ON DELETE RESTRICT` (blocks deletion — must handle products first)
  - `suppliers.latest_audit_id → supplier_audits.id ON DELETE SET NULL` (must clear first to avoid circular reference)

### Frontend
- `apps/Client/src/pages/kompass/SuppliersPage.tsx` — Contains delete dialog and confirmation logic (lines 360-391). Must update confirmation dialog to warn about permanent deletion and show what will be deleted.
- `apps/Client/src/services/kompassService.ts` — Contains `supplierService.delete()` method (lines 189-192). May need to handle the new response format.
- `apps/Client/src/types/kompass.ts` — May need new type for delete response.

### Tests
- `apps/Server/tests/services/test_supplier_service.py` — Contains `TestDeleteSupplier` class (line 284-331). Must update tests to reflect hard delete behavior.
- `apps/Server/tests/api/test_supplier_routes.py` — Contains `TestDeleteSupplier` class (line 371-409). Must update tests to reflect hard delete response.

### Documentation
- `ai_docs/KOMPASS_MODULE_GUIDE.md` — Reference for understanding module architecture.
- `.claude/commands/test_e2e.md` — For understanding how to create and run E2E tests.
- `.claude/commands/e2e/test_basic_query.md` — Example E2E test file pattern.

### New Files
- `.claude/commands/e2e/test_delete_supplier_hard.md` — New E2E test file to validate hard delete functionality.

## Implementation Plan
### Phase 1: Foundation
Update the backend repository layer to support hard delete with proper cascade handling within a single transaction. This is the foundational change that everything else depends on.

### Phase 2: Core Implementation
Update the service layer to remove the active products restriction and implement the hard delete logic with proper cascade ordering. Update the API route to return meaningful deletion results (counts of deleted records). Update the frontend confirmation dialog to warn about permanent deletion.

### Phase 3: Integration
Update all tests to reflect the new hard delete behavior. Create E2E test to validate the complete flow. Run full validation suite.

## Step by Step Tasks

### Step 1: Update SupplierRepository — Add hard_delete method
- In `apps/Server/app/repository/kompass_repository.py`:
  - Rename existing `delete()` method to keep backward compatibility or replace it directly
  - Implement a new `delete()` method that performs a hard delete within a single transaction:
    1. `UPDATE suppliers SET latest_audit_id = NULL WHERE id = %s` (clear circular FK)
    2. `DELETE FROM products WHERE supplier_id = %s` (removes products; product_images, product_tags, portfolio_items CASCADE automatically; quotation_items SET NULL automatically)
    3. `DELETE FROM suppliers WHERE id = %s RETURNING id` (supplier_audits CASCADE automatically)
    4. Commit transaction
  - Return a dict with deletion counts: `{"deleted": True, "products_deleted": int, "audits_deleted": int}` or `None` if supplier not found
  - Add a `get_delete_preview()` method that returns counts of associated records that would be deleted (products count, audits count) for the confirmation dialog

### Step 2: Update SupplierService — Hard delete logic
- In `apps/Server/app/services/supplier_service.py`:
  - Update `delete_supplier()` method:
    - Remove the active products check that blocks deletion
    - Call the updated repository `delete()` method
    - Return deletion result with counts
  - Add `get_delete_preview()` method that returns counts of what would be deleted (for the frontend confirmation dialog)

### Step 3: Update API routes — Hard delete endpoint and preview endpoint
- In `apps/Server/app/api/supplier_routes.py`:
  - Update the `DELETE /suppliers/{supplier_id}` endpoint:
    - Change docstring to reflect hard delete
    - Return enhanced response with deletion counts: `{"message": "...", "products_deleted": N, "audits_deleted": N}`
  - Add a new `GET /suppliers/{supplier_id}/delete-preview` endpoint:
    - Returns counts of associated records that would be deleted
    - Used by frontend to show in the confirmation dialog
    - Requires admin/manager role

### Step 4: Update DTOs if needed
- In `apps/Server/app/models/kompass_dto.py`:
  - Add `SupplierDeletePreviewDTO` with fields: `supplier_name`, `products_count`, `audits_count`
  - Add `SupplierDeleteResponseDTO` with fields: `message`, `products_deleted`, `audits_deleted`

### Step 5: Update Frontend — Enhanced delete confirmation dialog
- In `apps/Client/src/services/kompassService.ts`:
  - Add `getDeletePreview(id: string)` method to fetch the delete preview
  - Update `delete()` method to return the response data (products_deleted, audits_deleted)
- In `apps/Client/src/types/kompass.ts`:
  - Add `SupplierDeletePreview` interface with `supplier_name`, `products_count`, `audits_count`
- In `apps/Client/src/pages/kompass/SuppliersPage.tsx`:
  - Update `handleDeleteClick` to first fetch the delete preview
  - Update the confirmation dialog to show a warning about permanent deletion
  - Display counts of associated records that will be deleted (e.g., "This will permanently delete: X products, Y audit reports")
  - Add a red warning icon or text to emphasize the irreversible nature
  - Show a success snackbar after deletion with counts of what was deleted

### Step 6: Update unit tests for service layer
- In `apps/Server/tests/services/test_supplier_service.py`:
  - Update `TestDeleteSupplier` class:
    - Update `test_delete_supplier_success` to verify hard delete behavior and returned counts
    - Remove or update `test_delete_supplier_with_active_products_fails` since active products no longer block deletion
    - Add `test_delete_supplier_cascades_products` to verify products are included in deletion
    - Add `test_delete_preview` to verify preview returns correct counts

### Step 7: Update unit tests for API routes
- In `apps/Server/tests/api/test_supplier_routes.py`:
  - Update `TestDeleteSupplier` class:
    - Update `test_delete_supplier_success` to verify enhanced response with counts
    - Remove `test_delete_supplier_with_active_products` (no longer blocked)
    - Add `test_delete_preview_endpoint` tests
    - Keep `test_delete_supplier_not_found` and `test_delete_supplier_forbidden_for_regular_user`

### Step 8: Create E2E test file for hard delete
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` to understand the E2E test pattern
- Create `.claude/commands/e2e/test_delete_supplier_hard.md` with test steps:
  1. Navigate to Suppliers page
  2. Create a test supplier
  3. Click delete on the test supplier
  4. Verify confirmation dialog shows permanent deletion warning with counts
  5. Confirm deletion
  6. Verify supplier is removed from the list
  7. Verify supplier no longer appears in search results

### Step 9: Run validation commands
- Run all validation commands listed below to ensure zero regressions

## Testing Strategy
### Unit Tests
- **Service layer**: Test that `delete_supplier()` calls the repository hard delete, returns counts, and handles not-found cases
- **Service layer**: Test that `get_delete_preview()` returns correct counts
- **API routes**: Test DELETE endpoint returns enhanced response with counts
- **API routes**: Test delete-preview endpoint returns correct preview data
- **API routes**: Test RBAC enforcement (only admin/manager can delete)

### Edge Cases
- Deleting a supplier with no products and no audits (counts should be 0)
- Deleting a supplier with products that are in portfolio_items (CASCADE should handle)
- Deleting a supplier with products referenced in quotation_items (SET NULL should handle)
- Deleting a supplier with a latest_audit_id set (circular FK must be cleared first)
- Deleting a non-existent supplier (404 response)
- Regular user attempting to delete (403 response)
- Concurrent deletion attempts (idempotency)

## Acceptance Criteria
- Admin/manager users can permanently delete a supplier from the Suppliers page
- All associated data is deleted: supplier_audits, products, product_images, product_tags, portfolio_items references
- Quotation items referencing deleted products have their product_id set to NULL (preserving quotation history)
- The confirmation dialog clearly warns that deletion is permanent and shows counts of what will be deleted
- After deletion, the supplier no longer appears in any list, search, or pipeline view
- Regular users and viewers cannot delete suppliers (403 error)
- All existing unit tests pass with updated behavior
- Frontend build succeeds with no TypeScript errors

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_delete_supplier_hard.md` test file to validate this functionality works.

- `cd apps/Server && source .venv/bin/activate && python -m pytest tests/ -v --tb=short` - Run Server tests to validate the feature works with zero regressions
- `cd apps/Client && npx tsc --noEmit` - Run Client type check to validate the feature works with zero regressions
- `cd apps/Client && npm run build` - Run Client build to validate the feature works with zero regressions

## Notes
- The database schema already has `ON DELETE CASCADE` on `supplier_audits.supplier_id`, so deleting the supplier will automatically remove all audits. However, `products.supplier_id` has `ON DELETE RESTRICT`, which means we must explicitly delete products first before deleting the supplier.
- The circular FK between `suppliers.latest_audit_id → supplier_audits.id` must be cleared (SET NULL) before attempting to delete audits/supplier to avoid FK constraint violations.
- Product deletion will CASCADE to `product_images`, `product_tags`, and `portfolio_items` due to their `ON DELETE CASCADE` constraints.
- `quotation_items.product_id` has `ON DELETE SET NULL`, so quotation history is preserved even after product deletion — the quotation item keeps its `product_name`, `sku`, and pricing data but loses the FK reference.
- No new libraries are needed for this implementation.
