# Patch: Add wechat_id to _row_to_dict_extended and all extended SELECT queries

## Metadata
adw_id: `9167a7c8`
review_change_request: `The _row_to_dict_extended() method in kompass_repository.py does not include wechat_id in its column mapping. All extended SELECT queries omit wechat_id, causing GET /api/suppliers (list) to return wechat_id: null even when values exist in the database. The edit form uses list data, so existing WeChat IDs are never pre-filled.`

## Issue Summary
**Original Spec:** `specs/issue-163-adw-9167a7c8-sdlc_planner-add-supplier-wechat-id-field.md`
**Issue:** The spec incorrectly stated `_row_to_dict_extended()` did NOT need changes (line 208). In reality, `get_all_with_filters()` uses `_row_to_dict_extended()` and its SELECT omits `wechat_id`, so the supplier list API returns `wechat_id: null` for all suppliers. Since the SupplierForm uses list data directly (no fresh GET by ID), the edit form never pre-fills WeChat IDs.
**Solution:** Add `wechat_id` to ALL extended SELECT/RETURNING queries and update `_row_to_dict_extended()` to map the new column. Insert `wechat_id` after `notes` (consistent with `_row_to_dict()`) and shift all subsequent indices by +1. Also fix `get_all_with_audit_data()` which is missing `outreach_status` (pre-existing bug that becomes critical after index shift).

## Files to Modify

- `apps/Server/app/repository/kompass_repository.py` — Update `_row_to_dict_extended()` and all 11 SELECT/RETURNING queries that feed into it

## Implementation Steps

### Step 1: Update `_row_to_dict_extended()` mapping (line 2217-2246)

Replace the entire mapping dict with the new column order (20 columns, was 19):

```python
def _row_to_dict_extended(self, row: tuple) -> Dict[str, Any]:
    """Convert an extended database row to a dictionary (includes certification fields)."""
    return {
        "id": row[0],
        "name": row[1],
        "code": row[2],
        "status": row[3],
        "contact_name": row[4],
        "contact_email": row[5],
        "contact_phone": row[6],
        "address": row[7],
        "city": row[8],
        "country": row[9],
        "website": row[10],
        "notes": row[11],
        "wechat_id": row[12],
        "certification_status": row[13],
        "pipeline_status": row[14],
        "latest_audit_id": row[15],
        "certified_at": row[16],
        "outreach_status": row[17],
        "created_at": row[18],
        "updated_at": row[19],
    }
```

### Step 2: Update all 11 extended SELECT/RETURNING queries to include `wechat_id` after `notes`

Each query must follow the canonical column order:
```sql
id, name, code, status, contact_name, contact_email,
contact_phone, address, city, country, website, notes,
wechat_id, certification_status, pipeline_status, latest_audit_id,
certified_at, outreach_status, created_at, updated_at
```

**Queries to update (by method name and approximate line):**

1. **`create_with_trade_fair_metadata()`** RETURNING clause (~line 1385-1388):
   - Add `wechat_id,` after `notes,` in RETURNING

2. **`find_duplicate_supplier()`** SELECT (~line 1756-1759):
   - Add `wechat_id,` after `notes,` in SELECT

3. **`get_all_with_filters()`** SELECT (~line 1953-1956):
   - Add `s.wechat_id,` after `s.notes,` in SELECT

4. **`get_all_with_audit_data()`** SELECT (~line 2066-2069):
   - Add `s.wechat_id,` after `s.notes,` in SELECT
   - Add `s.outreach_status,` after `s.certified_at,` (missing — pre-existing bug)
   - Change `row[:18]` → `row[:20]` on line ~2093
   - Shift ALL audit column indices by +2 (row[18]→row[20], row[19]→row[21], ... row[34]→row[36]) on lines ~2094-2111

5. **`update_certification_status()`** RETURNING (~line 2197-2200):
   - Add `wechat_id,` after `notes,` in RETURNING

6. **`get_by_certification_status()`** SELECT (~line 2307-2310):
   - Add `wechat_id,` after `notes,` in SELECT

7. **`get_by_pipeline_status()`** SELECT (~line 2362-2365):
   - Add `wechat_id,` after `notes,` in SELECT

8. **`update_pipeline_status()`** RETURNING (~line 2409-2412):
   - Add `wechat_id,` after `notes,` in RETURNING

9. **`update_outreach_status()`** RETURNING (~line 2455-2458):
   - Add `wechat_id,` after `notes,` in RETURNING

10. **`get_by_id_extended()`** SELECT (~line 2556-2559):
    - Add `wechat_id,` after `notes,` in SELECT

11. **`get_all_grouped_by_pipeline()`** SELECT (~line 2635-2638):
    - Add `s.wechat_id,` after `s.notes,` in SELECT
    - Change `row[:19]` → `row[:20]` on line ~2658
    - Change `row[19]` → `row[20]` for product_count on line ~2659
    - Change `row[13]` → `row[14]` for pipeline_status on line ~2660

### Step 3: Verify no other callers reference raw row indices from extended queries

Search for any other hardcoded row index references that depend on the extended column order and update them.

## Validation
Execute every command to validate the patch is complete with zero regressions.

1. `cd apps/Server && .venv/bin/python -m py_compile main.py` — Verify Python syntax
2. `cd apps/Server && .venv/bin/ruff check .` — Verify code quality
3. `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` — Run all backend tests
4. `cd apps/Client && npx tsc --noEmit` — TypeScript type check (no frontend changes, but verify)
5. `cd apps/Client && npm run build` — Frontend build check (no frontend changes, but verify)

## Patch Scope
**Lines of code to change:** ~60
**Risk level:** medium (index shifts across 11 queries require careful alignment; one incorrect index causes silent data mislabeling)
**Testing required:** Backend unit tests + manual verification that GET /api/suppliers list response includes correct wechat_id values; verify edit form pre-fills WeChat ID
