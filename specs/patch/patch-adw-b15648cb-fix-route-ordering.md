# Patch: Fix route ordering conflict for business card GET endpoints

## Metadata
adw_id: `b15648cb`
review_change_request: `Route ordering conflict in extraction_routes.py: GET /{job_id} (line 302) is defined before GET /business-cards (line 635) and GET /business-cards/{capture_id} (line 687). FastAPI matches routes in definition order, so 'business-cards' gets matched by /{job_id} and fails UUID validation. The list and detail endpoints are completely unreachable, returning 422 errors.`

## Issue Summary
**Original Spec:** N/A
**Issue:** In `extraction_routes.py`, the `GET /{job_id}` route (line 302) is defined before the `GET /business-cards` and `GET /business-cards/{capture_id}` routes (lines 635, 687). FastAPI evaluates routes in definition order, so requests to `/business-cards` are intercepted by `/{job_id}`, which tries to parse "business-cards" as a UUID, resulting in a 422 validation error.
**Solution:** Move the entire business card GET endpoints section (`GET /business-cards` and `GET /business-cards/{capture_id}`) above the `GET /{job_id}` route definition. This ensures static path segments are matched before the dynamic `{job_id}` parameter.

## Files to Modify
Use these files to implement the patch:

- `apps/Server/app/api/extraction_routes.py` — Reorder route definitions

## Implementation Steps
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Move `GET /business-cards` and `GET /business-cards/{capture_id}` before `GET /{job_id}`
- Cut the two GET endpoint functions (`list_business_cards` at line 635 and `get_business_card` at line 687) along with the section comment header (lines 520-523)
- Paste them immediately before the `GET /{job_id}` route definition (currently at line 302)
- Keep the `POST /business-card` endpoint where it currently is (line 525) since POST routes don't conflict with `GET /{job_id}`
- Preserve all existing code, docstrings, and decorators exactly as-is

### Step 2: Verify route order correctness
- After the move, the route order should be:
  1. `POST /upload`
  2. `GET /business-cards` (list — static path, must come before `{job_id}`)
  3. `GET /business-cards/{capture_id}` (static prefix, must come before `{job_id}`)
  4. `GET /{job_id}` (dynamic catch-all)
  5. `GET /{job_id}/results`
  6. `POST /{job_id}/confirm`
  7. `POST /image/process`
  8. `POST /hs-code/suggest`
  9. `POST /business-card`

## Validation
Execute every command to validate the patch is complete with zero regressions.

1. `cd apps/Server && .venv/bin/python -m py_compile main.py` — Verify no syntax errors
2. `cd apps/Server && .venv/bin/ruff check app/api/extraction_routes.py` — Verify linting passes
3. `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` — Run all backend tests
4. `cd apps/Client && npm run build` — Verify frontend build (no regression)

## Patch Scope
**Lines of code to change:** ~100 lines (move, no new code)
**Risk level:** low
**Testing required:** Backend syntax check, linting, and unit tests to confirm no regressions
