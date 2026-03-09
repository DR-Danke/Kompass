# Patch: Fix business_card_captures table schema mismatch in migration

## Metadata
adw_id: `b15648cb`
review_change_request: `Database schema mismatch: The existing business_card_captures table has different columns than what the repository code expects. Code references columns (contact_wechat, website, extraction_raw_response) that don't exist in the table, and the table has columns (province, qr_code_detected, confidence_scores, source) not in the code. The INSERT RETURNING query in BusinessCardCaptureRepository.create() fails, causing POST /business-card to return 500 'Failed to create business card capture record'. The migration uses CREATE TABLE IF NOT EXISTS which won't fix an existing table with a different schema. Resolution: Either drop and recreate the business_card_captures table to match the migration schema, or update the migration to handle the case where the table exists with a different schema (use DROP TABLE IF EXISTS before CREATE, or use ALTER statements to reconcile columns). Severity: blocker`

## Issue Summary
**Original Spec:** `specs/issue-140-adw-b15648cb-sdlc_planner-business-card-photo-ingestion.md`
**Issue:** The migration file `migration_add_business_card_capture.sql` uses `CREATE TABLE IF NOT EXISTS` for `business_card_captures`. If the table already exists with a different schema (e.g., from a previous iteration with columns `province`, `qr_code_detected`, `confidence_scores`, `source`), the migration silently succeeds but leaves the old schema in place. The repository code then fails because it references columns (`contact_wechat`, `website`, `extraction_raw_response`) that don't exist in the stale table.
**Solution:** Change the migration to use `DROP TABLE IF EXISTS business_card_captures CASCADE` before `CREATE TABLE`, ensuring the table is always recreated with the correct schema. This is safe because business_card_captures is a new table with no production data to preserve.

## Files to Modify
Use these files to implement the patch:

- `apps/Server/database/migration_add_business_card_capture.sql` — Add `DROP TABLE IF EXISTS` before `CREATE TABLE`

## Implementation Steps
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add DROP TABLE before CREATE TABLE in migration
- In `apps/Server/database/migration_add_business_card_capture.sql`, add `DROP TABLE IF EXISTS business_card_captures CASCADE;` immediately before the `CREATE TABLE IF NOT EXISTS business_card_captures` statement
- This ensures that if the table exists with a stale/mismatched schema, it is dropped and recreated with the correct columns

### Step 2: Verify schema.sql consistency
- Confirm that `apps/Server/database/schema.sql` already has the correct `business_card_captures` table definition matching the repository code (columns: `contact_wechat`, `website`, `extraction_raw_response`, etc.)
- No changes needed to schema.sql — it already matches the code

## Validation
Execute every command to validate the patch is complete with zero regressions.

1. `cd apps/Server && .venv/bin/python -m py_compile main.py` — Verify no syntax errors
2. `cd apps/Server && .venv/bin/ruff check .` — Verify linting passes
3. `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` — Run all backend tests
4. `cd apps/Client && npx tsc --noEmit` — Run Client type check
5. `cd apps/Client && npm run build` — Run Client build

## Patch Scope
**Lines of code to change:** ~2 lines (add DROP TABLE statement)
**Risk level:** low
**Testing required:** Backend syntax check, linting, unit tests, and frontend build to confirm no regressions
