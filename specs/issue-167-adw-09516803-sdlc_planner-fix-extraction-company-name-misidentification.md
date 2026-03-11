# Bug: Fix AI extraction company name misidentification

## Metadata
issue_number: `167`
adw_id: `09516803`
issue_json: ``

## Bug Description
The AI extraction for business cards frequently fails to correctly identify the company/organization name. Two failure modes exist:
1. **Company field left blank** — the AI does not extract the company name even when it is clearly visible on the card (near logos, in large/bold text, with corporate suffixes).
2. **Company field populated with contact person's name** — the AI confuses the person's name with the company name, resulting in incorrect supplier records downstream.

**Expected behavior:** `company_name` should contain only the organization name (e.g., "Guangzhou Trading Co., Ltd."), and `contact_name` should contain the person's name (e.g., "Zhang Wei"). When the company name cannot be determined, `company_name` should be `null` with a manual review note.

**Actual behavior:** `company_name` is either empty or incorrectly set to the contact person's name, producing bad supplier records.

## Problem Statement
The business card AI extraction prompt (`_build_business_card_prompt`) does not explicitly instruct the model to distinguish between company names and personal names. The response parser (`_parse_business_card_response`) performs no validation to catch cases where the company name equals the contact name or looks like a person's name. There is also no flagging mechanism when company_name is null after extraction.

## Solution Statement
1. Enhance the AI prompt with explicit instructions to distinguish company_name from contact_name, including visual cues (font size, logos, corporate suffixes) and a directive to return null rather than guess.
2. Add post-extraction validation in the response parser to catch misidentification (company_name == contact_name, or company_name looks like a person's name).
3. Add flagging logic in the business card service to append a manual review note when company_name is null after extraction.

## Steps to Reproduce
1. Upload a business card image via the Card Capture page
2. The system runs AI extraction via `extract_card()` → `extract_business_card_data()`
3. Observe that `company_name` in the extraction result is either blank or contains the contact person's name
4. The card moves to `extracted` status with incorrect company data
5. If approved, a supplier record is created with wrong/missing company name

## Root Cause Analysis
Three contributing factors:

1. **Insufficient prompt guidance** (`extraction_service.py:240-273`): The `_build_business_card_prompt()` method describes `company_name` simply as "company or factory name" without explicit instructions to distinguish it from the contact person's name. The AI model lacks guidance on visual cues (font size, logos, corporate suffixes like Inc., S.A., GmbH) that differentiate company names from personal names.

2. **No response validation** (`extraction_service.py:370-393`): The `_parse_business_card_response()` method parses the JSON and ensures `confidence_scores` exists and `qr_code_detected` is boolean, but performs zero validation on the relationship between `company_name` and `contact_name`. It does not check for equality, does not normalize empty strings to null, and does not flag suspicious company names that look like person names.

3. **No manual review flagging** (`business_card_service.py:188-250`): The `extract_card()` method maps fields directly from the extraction result to the database without checking if `company_name` is null. When company_name is missing, the card silently moves to `extracted` status without any note alerting the user to review.

## Relevant Files
Use these files to fix the bug:

- `apps/Server/app/services/extraction_service.py` — Contains `_build_business_card_prompt()` (line 240) and `_parse_business_card_response()` (line 370). Both methods need enhancement.
- `apps/Server/app/services/business_card_service.py` — Contains `extract_card()` (line 188). Needs flagging logic when company_name is null.
- `apps/Server/tests/test_extraction_service.py` — Existing extraction service tests. Need to add business card parsing tests.
- `apps/Server/database/schema.sql` — Reference for `business_card_captures` table schema (company_name VARCHAR(255), notes TEXT).
- `apps/Server/app/repository/business_card_repository.py` — Reference for understanding how updates are persisted.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Enhance the business card extraction prompt
**File:** `apps/Server/app/services/extraction_service.py` — method `_build_business_card_prompt()` (line 240)

Update the prompt to add explicit company vs. contact name distinction:

- Add a `CRITICAL DISTINCTION` section after the JSON schema that explicitly defines:
  - `company_name`: The name of the company or organization (NOT the person). Visual cues: largest/boldest text, text near logos, text with corporate suffixes (Inc., LLC, S.A., S.A.S., Ltda., GmbH, Co., Ltd., Corp., S.R.L., S.L.).
  - `contact_name`: The individual person's full name. Visual cues: text near job titles, text in normal/smaller font.
- Add the instruction: "If you cannot clearly identify a company name, set company_name to null — do NOT use the person's name as the company name."
- Add a `confidence_scores.company_name` instruction: set it below 0.5 if the company name is uncertain.

### Step 2: Add validation logic to the business card response parser
**File:** `apps/Server/app/services/extraction_service.py` — method `_parse_business_card_response()` (line 370)

Add post-parse validation after the existing JSON parsing and before the return statement:

- **Normalize empty strings to null:** If `company_name` is an empty string or whitespace-only, set it to `None`.
- **Strip whitespace:** If `company_name` is a string, strip leading/trailing whitespace.
- **Detect company_name == contact_name:** If `company_name` and `contact_name` are both present and equal (case-insensitive comparison after stripping), set `company_name` to `None` and set `confidence_scores.company_name` to `0.0`. Log a warning.
- **Detect person-name-like company_name:** Create a helper check — if `company_name` is 2-3 words and contains no corporate suffix (check against a tuple of common suffixes: "inc", "llc", "s.a.", "s.a.s", "ltda", "gmbh", "co.", "ltd", "corp", "s.r.l.", "s.l.", "company", "group", "trading", "industrial", "factory", "manufacture"), set `confidence_scores.company_name` to a value capped at `0.4` (low confidence). Log a warning.

### Step 3: Add manual review flagging for null company_name
**File:** `apps/Server/app/services/business_card_service.py` — method `extract_card()` (line 188)

After building the `updates` dict (line 221-231) and before calling `business_card_repository.update()`:

- Check if `updates["company_name"]` is `None`.
- If null, append a note to the existing `notes` field: `"Company name could not be determined — manual review required"`.
  - Retrieve existing notes from `capture.get("notes") or ""`.
  - If existing notes are non-empty, concatenate with a newline separator.
  - Set `updates["notes"]` to the combined value.
- Keep status as `"extracted"` (not `"failed"`) — the card should still be reviewable.
- Log: `print(f"INFO [BusinessCardService]: Company name null for {capture_id}, flagged for manual review")`

### Step 4: Add unit tests for business card parsing validation
**File:** `apps/Server/tests/test_extraction_service.py`

Add a new test class `TestParseBusinessCardResponse` with the following test cases:

- **test_parse_valid_business_card**: Valid JSON with distinct company_name and contact_name — both should be preserved.
- **test_parse_company_equals_contact_name**: When company_name equals contact_name (case-insensitive), company_name should be set to None and confidence_scores.company_name to 0.0.
- **test_parse_empty_company_name**: Empty string company_name should be normalized to None.
- **test_parse_whitespace_company_name**: Whitespace-only company_name should be normalized to None.
- **test_parse_person_name_as_company**: A 2-word company_name without corporate suffixes should have confidence capped at 0.4.
- **test_parse_valid_company_with_suffix**: A company_name with "Co., Ltd." suffix should retain normal confidence.
- **test_parse_null_company_name**: Explicit null company_name should remain None.
- **test_existing_fields_not_regressed**: Ensure contact_name, contact_email, contact_phone, website, address, contact_wechat are all preserved correctly when company_name validation fires.

### Step 5: Run validation commands
Execute all validation commands listed below to confirm the fix works with zero regressions.

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `cd apps/Server && python -m pytest tests/test_extraction_service.py -v --tb=short` — Run extraction service tests including new business card parsing tests
- `cd apps/Server && python -m pytest tests/ -v --tb=short` — Run all Server tests for zero regressions
- `cd apps/Server && python -m ruff check app/services/extraction_service.py app/services/business_card_service.py` — Lint the modified service files
- `cd apps/Client && npx tsc --noEmit` — Run Client type check (no client changes expected, but verify nothing broke)
- `cd apps/Client && npm run build` — Run Client build to validate no regressions

## Notes
- This is a **backend-only** change. No frontend modifications are needed — the CardReviewPage already supports manual editing of all extracted fields including company_name.
- The corporate suffixes list should cover international formats common in the sourcing/trading context: Chinese (Co., Ltd.), Latin American (S.A., S.A.S., Ltda., S.R.L.), European (GmbH, S.L.), and US (Inc., LLC, Corp.).
- The person-name heuristic (2-3 words, no corporate suffix) is intentionally conservative — it only flags low confidence rather than nullifying, since some legitimate company names could be short (e.g., "Golden Star"). The prompt improvement is the primary fix; the parser validation is a safety net.
- No new libraries are required.
- The `notes` field concatenation in Step 3 follows the same pattern already used in `reject_card()` (line 177-179 of business_card_service.py).
