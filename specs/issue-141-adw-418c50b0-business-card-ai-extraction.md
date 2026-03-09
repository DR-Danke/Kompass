# Feature: Business Card AI Data Extraction

## Metadata
issue_number: `141`
adw_id: `418c50b0`
issue_json: ``

## Feature Description
Add AI vision-based extraction to process uploaded business card photos. This extends the existing extraction pipeline (used for product catalogs) with a new prompt template optimized for business cards, extracting structured contact fields (name, phone, email, company, address, province) from potentially bilingual Chinese/English cards. The extraction uses the existing Anthropic/OpenAI AI providers already configured in the ExtractionService. Results are stored in the `business_card_captures` table and displayed in the frontend CardCapturePage with confidence score indicators.

## User Story
As a Kompass sourcing agent at a trade fair
I want uploaded business card photos to be automatically processed by AI to extract contact information
So that I can quickly digitize supplier details without manual data entry

## Problem Statement
Business card photos are uploaded to the system (TF-001) but remain in "pending" status with no extracted data. Users must manually read cards and enter contact information. This is slow and error-prone, especially with bilingual Chinese/English cards.

## Solution Statement
Add an AI extraction method to `ExtractionService` that sends business card images to the configured AI vision API (Anthropic Claude or OpenAI GPT-4o) with a specialized prompt for contact data extraction. Add a trigger endpoint to initiate extraction, and update the frontend to display extraction results with confidence scores and a retry option for failures.

## Relevant Files
Use these files to implement the feature:

**Backend — Core:**
- `apps/Server/app/services/extraction_service.py` — Add `extract_business_card()` method using existing AI provider pattern (`_extract_with_anthropic`, `_extract_with_openai`). This is the main service with the AI integration.
- `apps/Server/app/services/business_card_service.py` — Add `extract_card()` method that orchestrates the extraction flow: validate status, set to processing, call extraction service, update record.
- `apps/Server/app/repository/business_card_repository.py` — Already has `update()` method for updating extracted fields. No changes needed.
- `apps/Server/app/api/extraction_routes.py` — Add `POST /api/extract/business-cards/{capture_id}/extract` endpoint and add `auto_extract=true` support to the upload endpoint.
- `apps/Server/app/models/kompass_dto.py` — Contains `BusinessCardCaptureResponseDTO` and `BusinessCardCaptureStatus`. Add `BusinessCardExtractionResultDTO` for the extraction result shape.

**Backend — Config:**
- `apps/Server/app/config/settings.py` — Settings with `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `EXTRACTION_AI_PROVIDER`. No changes needed.
- `apps/Server/database/schema.sql` — `business_card_captures` table with all needed columns (company_name, contact_name, contact_email, contact_phone, contact_wechat, website, address, extraction_raw_response JSONB). No schema changes needed — province can be included in address field or stored in extraction_raw_response.

**Frontend:**
- `apps/Client/src/pages/kompass/CardCapturePage.tsx` — Update to show extraction status, display extracted fields with confidence badges, add extract/retry buttons.
- `apps/Client/src/services/kompassService.ts` — Add `triggerExtraction()` method to `businessCardService`.
- `apps/Client/src/types/kompass.ts` — `BusinessCardCapture` type already has all needed fields including `extraction_raw_response` for confidence scores.

**E2E Testing:**
- `.claude/commands/test_e2e.md` — Read for E2E test runner format
- `.claude/commands/e2e/test_card_capture_page.md` — Existing E2E test for card capture page (reference)

### New Files
- `.claude/commands/e2e/test_business_card_extraction.md` — E2E test for AI extraction feature

## Implementation Plan
### Phase 1: Foundation
Add the extraction result DTO and the business card extraction prompt template to the extraction service. This establishes the data contract and AI prompt before wiring up endpoints.

### Phase 2: Core Implementation
Implement the `extract_business_card()` method in `ExtractionService` using the existing AI provider pattern. Add orchestration in `BusinessCardService`. Wire up the extraction trigger endpoint and auto-extract support in the upload endpoint.

### Phase 3: Integration
Update the frontend CardCapturePage to display extraction results with confidence indicators, add extract/retry buttons, and implement polling for status updates during extraction.

## Step by Step Tasks

### Step 1: Add BusinessCardExtractionResultDTO to DTOs
- Open `apps/Server/app/models/kompass_dto.py`
- Add a new `BusinessCardExtractionResultDTO` class after `BusinessCardCaptureListResponseDTO`:
  ```python
  class BusinessCardExtractionResultDTO(BaseModel):
      """Result of AI extraction from a business card image."""
      contact_name: Optional[str] = None
      contact_phone: Optional[str] = None
      contact_email: Optional[str] = None
      company_name: Optional[str] = None
      address: Optional[str] = None
      province: Optional[str] = None
      website: Optional[str] = None
      contact_wechat: Optional[str] = None
      qr_code_detected: bool = False
      confidence_scores: dict = {}
  ```

### Step 2: Add Business Card Extraction to ExtractionService
- Open `apps/Server/app/services/extraction_service.py`
- Add a new method `_build_business_card_prompt()` that returns the specialized prompt for business card extraction:
  - Extract: contact_name, contact_phone (with international prefix like +86), contact_email, company_name (factory name), address, province/city, website, wechat_id
  - Detect QR code presence (boolean)
  - Handle bilingual Chinese/English — prefer English, fallback to Chinese
  - Return confidence scores (0.0–1.0) per field
  - Return null for missing fields
  - Output as structured JSON
- Add method `extract_business_card_data(image_data: bytes) -> dict` that:
  1. Uses `_get_preferred_ai_provider()` to select AI provider
  2. Calls `_extract_with_anthropic()` or `_extract_with_openai()` with vision mode, using the business card prompt
  3. Parses the JSON response
  4. Returns a dict with extracted fields and confidence_scores
  5. Falls back to empty result with zero confidence if AI unavailable or fails

### Step 3: Add Extraction Orchestration to BusinessCardService
- Open `apps/Server/app/services/business_card_service.py`
- Import `extraction_service` from `app.services.extraction_service`
- Add method `extract_card(capture_id: UUID) -> Dict[str, Any]` that:
  1. Gets the capture record via `get_capture(capture_id)`
  2. Validates status is `pending` or `failed` (allows retry)
  3. Updates status to `processing` via `business_card_repository.update()`
  4. Retrieves image data: if image_url is a base64 data URL, decode it; if an HTTP URL, download it with `httpx`
  5. Calls `extraction_service.extract_business_card_data(image_data)`
  6. On success: update capture record with extracted fields (company_name, contact_name, contact_email, contact_phone, contact_wechat, website, address) and set `extraction_raw_response` to the full result dict (including confidence_scores and province), set status to `extracted`
  7. On failure: set status to `failed`, store error in `extraction_raw_response`
  8. Returns the updated capture record

### Step 4: Add Extraction Trigger Endpoint
- Open `apps/Server/app/api/extraction_routes.py`
- Add new endpoint after the existing business card GET endpoints (before the `/{job_id}` catch-all):
  ```python
  @router.post("/business-cards/{capture_id}/extract", response_model=BusinessCardCaptureResponseDTO)
  async def extract_business_card(
      capture_id: UUID,
      current_user: Dict[str, Any] = Depends(require_roles(["admin", "manager", "user"])),
  ) -> BusinessCardCaptureResponseDTO:
  ```
  - Calls `business_card_service.extract_card(capture_id)`
  - Returns the updated capture record as `BusinessCardCaptureResponseDTO`
  - Handles `ValueError` → 404, generic exceptions → 500
- Import `BusinessCardExtractionResultDTO` if needed

### Step 5: Add Auto-Extract to Upload Endpoint
- In `apps/Server/app/api/extraction_routes.py`, modify `upload_business_card()`:
  - Add `auto_extract: bool = Form(default=True)` parameter
  - After successful capture creation, if `auto_extract` is True, call `business_card_service.extract_card(capture["id"])` wrapped in try/except (extraction failure should not fail the upload)
  - Return the capture record (with extracted data if auto-extract succeeded)

### Step 6: Add triggerExtraction to Frontend Service
- Open `apps/Client/src/services/kompassService.ts`
- Add method to `businessCardService`:
  ```typescript
  async triggerExtraction(captureId: string): Promise<BusinessCardCapture> {
    console.log(`INFO [businessCardService]: Triggering extraction for ${captureId}`);
    const response = await apiClient.post<BusinessCardCapture>(
      `/extract/business-cards/${captureId}/extract`
    );
    return response.data;
  },
  ```

### Step 7: Update CardCapturePage with Extraction UI
- Open `apps/Client/src/pages/kompass/CardCapturePage.tsx`
- Add imports: `CircularProgress`, `Button`, `Tooltip`, `IconButton` from MUI, `AutoFixHighIcon` or `SmartToyIcon` from MUI icons
- Add `extractingIds` state (`Set<string>`) to track which cards are being extracted
- Add `handleExtract(captureId: string)` function that:
  1. Adds captureId to extractingIds
  2. Calls `businessCardService.triggerExtraction(captureId)`
  3. On success: update the capture in the captures list, show success snackbar
  4. On failure: show error snackbar
  5. Removes captureId from extractingIds
- Update the capture card rendering to show:
  - When status is `processing` or captureId is in extractingIds: show `CircularProgress` spinner
  - When status is `extracted`: show extracted fields (company_name, contact_name, contact_phone, contact_email, address) with confidence badges from `extraction_raw_response.confidence_scores`
  - Confidence badge colors: >= 0.8 green, >= 0.5 yellow/orange, < 0.5 red
  - When status is `failed`: show error message with "Reintentar" (retry) button
  - When status is `pending`: show "Extraer" (extract) button (for manual trigger if auto-extract was off)
- All UI text in Spanish (Colombian)

### Step 8: Create E2E Test File
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_card_capture_page.md` to understand the E2E test format
- Create `.claude/commands/e2e/test_business_card_extraction.md` with test steps:
  1. Navigate to Card Capture page
  2. Upload a test business card image
  3. Verify extraction triggers automatically (auto-extract)
  4. Verify extraction results appear with confidence badges
  5. Verify extracted fields are displayed (company name, contact info)
  6. Verify status changes from pending → processing → extracted
  7. Test manual extract/retry button for failed captures
  8. Screenshots at each step

### Step 9: Run Validation Commands
- Execute all validation commands to ensure zero regressions

## Testing Strategy
### Unit Tests
- Test `extract_business_card_data()` with mocked AI responses (valid JSON, malformed JSON, empty response)
- Test `extract_card()` orchestration: verify status transitions (pending→processing→extracted, pending→processing→failed)
- Test auto-extract in upload flow: verify extraction runs when auto_extract=True
- Test extraction trigger endpoint with valid/invalid capture IDs
- Test retry: verify extraction can be re-triggered on `failed` status

### Edge Cases
- AI service unavailable (no API keys configured) — should gracefully fail, set status to `failed`
- Malformed AI response (non-JSON output) — should handle gracefully, store raw response
- Base64 data URL image (development mode) — must decode correctly
- HTTP URL image (production with Supabase Storage) — must download correctly
- Very large images — handled by existing 10MB upload limit
- Cards with only Chinese text — should extract Chinese values
- Cards with both Chinese and English — should prefer English
- Cards with missing fields (no email, no phone) — should return null for missing fields
- Concurrent extraction requests for same capture — status check prevents double-processing
- Extraction on already-extracted card — should reject (status not pending/failed)

## Acceptance Criteria
- `POST /api/extract/business-cards/{id}/extract` endpoint returns extracted contact data
- Extraction sets status to `processing` then `extracted` on success or `failed` on error
- Business card prompt extracts: contact_name, contact_phone, contact_email, company_name, address, province, website, wechat
- QR code detection returns a boolean
- Confidence scores (0.0–1.0) are returned per field and stored in `extraction_raw_response`
- Bilingual cards prefer English values when both languages present
- Auto-extract triggers on upload by default
- Frontend displays extracted fields with green/yellow/red confidence badges
- Frontend shows retry button for failed extractions
- Frontend shows spinner during extraction processing
- All UI text is in Spanish (Colombian)
- No regressions in existing extraction pipeline or business card upload

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/ -v --tb=short` — Run Server tests to validate the feature works with zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate the feature works with zero regressions
- `cd apps/Client && npm run build` — Run Client build to validate the feature works with zero regressions
- `cd apps/Client && npm run lint` — Run Client linting to catch any code quality issues
- `cd apps/Server && python -m ruff check .` — Run Server linting to catch any code quality issues
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_business_card_extraction.md` E2E test to validate this functionality works

## Notes
- The extraction uses the **existing** Anthropic/OpenAI providers already configured in `ExtractionService`. No new AI provider (LandingAI) is needed — the issue mentions LandingAI but the codebase already has Anthropic Claude and OpenAI GPT-4o vision capabilities fully implemented.
- The `province` field from the extraction result will be stored inside `extraction_raw_response` (JSONB) since the DB schema doesn't have a separate `province` column. The address field can include province/city info.
- The `qr_code_detected` boolean is also stored in `extraction_raw_response` since there's no dedicated DB column.
- The extraction is synchronous (not background task) since business card AI extraction is fast (single image, ~2-5 seconds). If latency becomes an issue in the future, it can be moved to a background task.
- Auto-extract on upload means the upload endpoint takes slightly longer but the user gets results immediately instead of needing a second action.
