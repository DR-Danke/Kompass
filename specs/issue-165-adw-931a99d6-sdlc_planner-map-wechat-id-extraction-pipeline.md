# Feature: Map AI-Extracted WeChat ID to Supplier wechat_id Field

## Metadata
issue_number: `165`
adw_id: `931a99d6`
issue_json: ``

## Feature Description
This feature ensures the AI-extracted `contact_wechat` field flows correctly through the entire business card pipeline: extraction → card review display → card capture display → supplier creation mapping. The extraction prompt is enhanced with WeChat-specific recognition guidance for better accuracy, and both the Card Review and Card Capture pages are updated to display the WeChat ID field with confidence badges. The supplier creation from card already maps `contact_wechat` to `wechat_id` — this feature verifies and completes the end-to-end pipeline.

## User Story
As a Kompass sourcing agent at a Chinese trade fair
I want the WeChat ID extracted from business cards to be visible during review and correctly saved to the supplier record
So that I can contact suppliers via WeChat after the fair without manual data entry

## Problem Statement
The AI extraction prompt already captures `contact_wechat` from business card images, and the backend already maps it to the supplier's `wechat_id` field during creation. However, the extraction prompt lacks specific WeChat ID recognition guidance (labels, format hints, QR code handling), and the frontend does not display the WeChat ID field on the Card Review or Card Capture pages — making it invisible to users during the review workflow.

## Solution Statement
1. Enhance the AI extraction prompt in `extraction_service.py` with WeChat-specific guidance: common labels (WeChat, 微信, Wechat ID, 微信号), format description (alphanumeric, 6-20 chars, starts with letter), and QR code handling notes.
2. Add a WeChat ID column to the Card Review table with an editable cell and confidence badge.
3. Add WeChat ID to the extracted fields display on the Card Capture page.
4. Verify that all existing backend mappings (repository, service, supplier creation) are complete (they are — no changes needed).

## Relevant Files
Use these files to implement the feature:

**Backend — Extraction Prompt Enhancement:**
- `apps/Server/app/services/extraction_service.py` — Contains `_build_business_card_prompt()` method. Enhance the prompt with WeChat-specific recognition instructions. Lines 240-272.

**Backend — Verification Only (no changes expected):**
- `apps/Server/app/services/supplier_service.py` — `create_supplier_from_card()` already maps `contact_wechat` to `wechat_id` (line 560, 607). Verify only.
- `apps/Server/app/repository/business_card_repository.py` — Already includes `contact_wechat` in `_COLUMNS` and `_row_to_dict`. Verify only.
- `apps/Server/app/services/business_card_service.py` — Already maps `contact_wechat` from extraction results (line 227). Verify only.
- `apps/Server/app/repository/kompass_repository.py` — Already includes `wechat_id` in all supplier queries. Verify only.

**Frontend — UI Changes:**
- `apps/Client/src/pages/kompass/CardReviewPage.tsx` — Add WeChat ID column to the review table with editable cell and confidence badge.
- `apps/Client/src/pages/kompass/CardCapturePage.tsx` — Add WeChat ID to extracted fields display alongside phone and email.
- `apps/Client/src/types/kompass.ts` — Already has `contact_wechat: string | null` on `BusinessCardCapture` interface. Verify only.

**E2E Test Reference:**
- `.claude/commands/test_e2e.md` — Read to understand E2E test runner format.
- `.claude/commands/e2e/test_business_card_extraction.md` — Reference for card extraction E2E test structure.
- `.claude/commands/e2e/test_supplier_wechat_id.md` — Reference for WeChat ID supplier E2E test structure.

### New Files
- `.claude/commands/e2e/test_wechat_id_extraction_pipeline.md` — E2E test validating WeChat ID visibility on Card Review and Card Capture pages.

## Implementation Plan
### Phase 1: Foundation
Verify that all backend data plumbing is already in place:
- `contact_wechat` in business card repository columns and row mapping
- `contact_wechat` extraction in business card service
- `contact_wechat` → `wechat_id` mapping in supplier creation from card
- `wechat_id` in supplier repository queries
- `contact_wechat` in frontend TypeScript types

### Phase 2: Core Implementation
1. Enhance the extraction prompt with WeChat-specific guidance
2. Add WeChat ID column to Card Review table
3. Add WeChat ID field to Card Capture extracted fields display

### Phase 3: Integration
- Create E2E test to validate the full pipeline visibility
- Run static analysis and build to verify zero regressions

## Step by Step Tasks

### Step 1: Create E2E Test File
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_business_card_extraction.md` to understand E2E test format
- Create `.claude/commands/e2e/test_wechat_id_extraction_pipeline.md` with test steps that:
  1. Navigate to Card Review page and verify WeChat ID column header exists
  2. Navigate to Card Capture page and verify WeChat ID field appears for extracted cards
  3. Validate confidence badge appears for WeChat ID when confidence data is present
- Follow existing E2E test patterns for screenshots and verification steps

### Step 2: Enhance Extraction Prompt with WeChat-Specific Guidance
- Open `apps/Server/app/services/extraction_service.py`
- In `_build_business_card_prompt()` (line 240), enhance the prompt instructions:
  - Add a "WeChat ID recognition" section to the prompt rules
  - Include guidance to look for labels: "WeChat", "微信", "Wechat ID", "微信号"
  - Note that WeChat IDs are alphanumeric strings, typically 6-20 characters, often starting with a letter
  - If a QR code is visible and labeled as WeChat, note `qr_code_detected: true` and attempt to read any adjacent text that might be the WeChat ID
  - Ensure existing fields are not degraded by the prompt changes

### Step 3: Add WeChat ID Column to Card Review Page
- Open `apps/Client/src/pages/kompass/CardReviewPage.tsx`
- Add a new `<TableCell>WeChat ID</TableCell>` header after the "Teléfono" column (after line 346)
- Add a corresponding `<TableCell>` in the table body with an `<EditableCell>` component:
  - `value={capture.contact_wechat}`
  - `fieldName="contact_wechat"`
  - `captureId={capture.id}`
  - `confidenceScore={scores.contact_wechat}`
  - `onSave={updateField}`
  - `disabled={!editable}`
- This follows the exact same pattern as the existing phone, email, and company name cells

### Step 4: Add WeChat ID to Card Capture Extracted Fields
- Open `apps/Client/src/pages/kompass/CardCapturePage.tsx`
- In the extracted fields section (after the email `ExtractedField` around line 393), add a WeChat ID `ExtractedField`:
  - Import `ChatIcon` from `@mui/icons-material/Chat` (a suitable icon for messaging/WeChat)
  - Add: `<ExtractedField icon={<ChatIcon sx={{ fontSize: 14, color: 'text.secondary' }} />} value={capture.contact_wechat} confidence={scores.contact_wechat} />`
  - Place it after the email field and before the address field, alongside other contact fields

### Step 5: Verify TypeScript Types
- Open `apps/Client/src/types/kompass.ts` and confirm `BusinessCardCapture` interface includes `contact_wechat: string | null` (it does at line 1062)
- No changes needed — verification only

### Step 6: Verify Backend Pipeline Completeness
- Open `apps/Server/app/repository/business_card_repository.py` and confirm `contact_wechat` is in `_COLUMNS` (line 15) and `_row_to_dict` (line 235). No changes needed.
- Open `apps/Server/app/services/business_card_service.py` and confirm `contact_wechat` is mapped in `extract_card()` updates dict (line 227). No changes needed.
- Open `apps/Server/app/services/supplier_service.py` and confirm `create_supplier_from_card()` maps `contact_wechat` to `wechat_id` param (lines 560, 607). No changes needed.
- Open `apps/Server/app/repository/kompass_repository.py` and confirm `wechat_id` is in supplier INSERT and SELECT queries. No changes needed.

### Step 7: Run Validation Commands
- Execute all validation commands to confirm zero regressions.

## Testing Strategy
### Unit Tests
- The extraction prompt change is a string-only change to `_build_business_card_prompt()` — existing tests for `ExtractionService` cover the parsing and response handling. No new unit tests required for prompt text changes.
- The frontend changes are display-only additions to existing components — covered by build and typecheck validation.

### Edge Cases
- Business card with no WeChat ID: `contact_wechat` will be `null`, and the `ExtractedField` component on CardCapturePage already handles `null` (returns `null`, not rendered). The `EditableCell` on CardReviewPage shows "—" for null values.
- WeChat ID with low confidence (< 0.5): The confidence badge will render in red, visually flagging it for manual review.
- WeChat ID extracted from QR code context: The prompt enhancement guides the AI to look for text near WeChat QR codes.
- Cards without any QR code: `qr_code_detected` defaults to `false`, no impact on other fields.

## Acceptance Criteria
- The extraction prompt in `_build_business_card_prompt()` includes WeChat-specific recognition guidance (labels, format, QR code handling)
- The Card Review page table shows a "WeChat ID" column with editable cells and confidence badges
- The Card Capture page shows WeChat ID in the extracted fields display when present
- The `contact_wechat` field confidence below 0.5 renders with a red badge (already handled by existing `getConfidenceColor` function)
- Existing extraction fields (name, email, phone, company, province) are not degraded by prompt changes
- TypeScript build and lint pass with zero errors
- Backend tests pass with zero regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run Client TypeScript check to validate types
- `cd apps/Client && npm run build` — Run Client production build to validate zero regressions
- `cd apps/Client && npm run lint` — Run Client ESLint to validate code quality
- `cd apps/Server && python -m pytest tests/ -v --tb=short` — Run Server tests to validate zero regressions
- `cd apps/Server && python -m ruff check .` — Run Server linting to validate code quality
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_wechat_id_extraction_pipeline.md` E2E test to validate the feature works end-to-end

## Notes
- No new libraries required. All changes use existing MUI components and patterns.
- The backend data plumbing is already 100% complete from TF-001. This issue primarily enhances the extraction prompt and adds frontend visibility.
- The `ChatIcon` from `@mui/icons-material` is used as a WeChat proxy icon since MUI does not include a dedicated WeChat icon. This is consistent with using generic icons for messaging platforms.
- UI language is Spanish (Colombian) but "WeChat ID" remains as-is since it is a proper noun.
- The `ExtractedField` component on CardCapturePage already returns `null` for empty values, so no special handling is needed for cards without WeChat IDs.
