# Bug Fix: Extraction Company Name Misidentification

**ADW ID:** 09516803
**Date:** 2026-03-10
**Specification:** specs/issue-167-adw-09516803-sdlc_planner-fix-extraction-company-name-misidentification.md

## Overview

Fixed a bug where the AI business card extraction frequently misidentified company names — either leaving the field blank or populating it with the contact person's name. The fix enhances the AI prompt with explicit company vs. person name distinction, adds post-extraction validation in the response parser, and flags cards with missing company names for manual review.

## What Was Built

- Enhanced AI extraction prompt with explicit company_name vs. contact_name distinction and visual cue guidance
- Post-extraction validation logic to catch misidentification (company equals contact, empty strings, person-name heuristic)
- Manual review flagging in the business card service when company_name is null
- 8 unit tests covering all validation scenarios

## Technical Implementation

### Files Modified

- `apps/Server/app/services/extraction_service.py`: Enhanced `_build_business_card_prompt()` with a CRITICAL DISTINCTION section; added validation logic in `_parse_business_card_response()` for empty normalization, company==contact detection, and person-name heuristic
- `apps/Server/app/services/business_card_service.py`: Added manual review note flagging in `extract_card()` when company_name is null after extraction
- `apps/Server/tests/test_extraction_service.py`: Added `TestParseBusinessCardResponse` class with 8 test cases

### Key Changes

- **Prompt enhancement**: Added a `CRITICAL DISTINCTION` section to the business card prompt that instructs the AI to use visual cues (font size, logos, corporate suffixes like Inc., LLC, GmbH, Co. Ltd., S.A., etc.) to distinguish company from person names, and to return null rather than guess
- **Empty normalization**: Empty strings and whitespace-only company_name values are normalized to `None`
- **Misidentification detection**: If company_name equals contact_name (case-insensitive), company_name is set to `None` and its confidence score to `0.0`
- **Person-name heuristic**: If company_name is 2-3 words with no corporate suffix, confidence is capped at `0.4` (safety net, not nullification)
- **Manual review flagging**: When company_name is null post-extraction, a note "Company name could not be determined — manual review required" is appended to the card's notes field

## How to Use

1. Upload a business card via the Card Capture page as usual
2. The AI extraction now applies stricter company name identification rules
3. If the company name cannot be determined, the card moves to `extracted` status with a review note visible on the Card Review page
4. Users can manually edit the company name on the Card Review page before approving the card

## Configuration

No new configuration required. The corporate suffixes list and validation thresholds are hardcoded in the extraction service.

## Testing

Run the extraction service tests:
```bash
cd apps/Server && python -m pytest tests/test_extraction_service.py::TestParseBusinessCardResponse -v --tb=short
```

Test cases cover:
- Valid business card with distinct company/contact names
- Company name equals contact name (case-insensitive)
- Empty and whitespace-only company name normalization
- Person-name-like company name confidence capping
- Valid company with corporate suffix (confidence preserved)
- Null company name passthrough
- Field regression (all other fields preserved)

## Notes

- This is a backend-only change — no frontend modifications were needed
- The corporate suffixes list covers international formats: Chinese (Co., Ltd.), Latin American (S.A., S.A.S., Ltda., S.R.L.), European (GmbH, S.L.), and US (Inc., LLC, Corp.)
- The person-name heuristic is intentionally conservative — it caps confidence rather than nullifying, since legitimate companies can have short names (e.g., "Golden Star")
- The prompt improvement is the primary fix; parser validation serves as a safety net
