# Business Card AI Data Extraction

**ADW ID:** 418c50b0
**Date:** 2026-03-09
**Specification:** specs/issue-141-adw-418c50b0-business-card-ai-extraction.md

## Overview

Adds AI vision-based extraction to process uploaded business card photos, extracting structured contact fields (name, phone, email, company, address, website, WeChat) from potentially bilingual Chinese/English cards. Uses existing Anthropic Claude or OpenAI GPT-4o vision providers already configured in the ExtractionService. Results display on the CardCapturePage with per-field confidence score badges.

## What Was Built

- **Business card AI extraction prompt** — specialized prompt template for contact data extraction with bilingual support and confidence scoring
- **Extraction service methods** — `extract_business_card_data()` using Anthropic Claude or OpenAI GPT-4o vision APIs
- **Extraction orchestration** — `BusinessCardService.extract_card()` handling status transitions (pending → processing → extracted/failed)
- **REST endpoint** — `POST /api/extract/business-cards/{capture_id}/extract` to trigger extraction manually
- **Auto-extract on upload** — `auto_extract=true` parameter on the upload endpoint triggers extraction immediately after capture
- **Frontend extraction UI** — confidence badges (green/yellow/red), extract/retry buttons, spinner during processing
- **DTO** — `BusinessCardExtractionResultDTO` for the extraction result schema
- **E2E test** — test script for the business card extraction feature

## Technical Implementation

### Files Modified

- `apps/Server/app/services/extraction_service.py`: Added `_build_business_card_prompt()`, `extract_business_card_data()`, `_extract_business_card_with_anthropic()`, `_extract_business_card_with_openai()`, `_parse_business_card_response()` — 154 new lines
- `apps/Server/app/services/business_card_service.py`: Added `extract_card()`, `_get_image_data()`, `_to_json()` — 95 new lines
- `apps/Server/app/api/extraction_routes.py`: Added `POST /business-cards/{capture_id}/extract` endpoint and `auto_extract` param on upload — 78 new lines
- `apps/Server/app/models/kompass_dto.py`: Added `BusinessCardExtractionResultDTO` with confidence_scores dict — 15 new lines
- `apps/Client/src/pages/kompass/CardCapturePage.tsx`: Added `ConfidenceBadge`, `ExtractedField` components, `handleExtract()`, extraction UI with status-aware rendering — 237 lines (major rewrite of card list)
- `apps/Client/src/services/kompassService.ts`: Added `triggerExtraction()` to `businessCardService` — 8 new lines
- `.claude/commands/e2e/test_business_card_extraction.md`: New E2E test file — 88 lines

### Key Changes

- **AI Prompt**: Specialized prompt handles bilingual cards (Chinese/English, prefers English), extracts 8 contact fields, detects QR codes, and returns per-field confidence scores (0.0–1.0)
- **Provider Pattern**: Reuses existing `_get_preferred_ai_provider()` to select Anthropic or OpenAI; each has dedicated vision methods for business cards
- **Status Machine**: Captures follow `pending → processing → extracted` (success) or `pending → processing → failed` (error) flow; retry allowed from `failed` status
- **Auto-Extract**: Upload endpoint triggers extraction by default (`auto_extract=True`); failures are caught silently so the upload itself always succeeds
- **Image Retrieval**: Handles both base64 data URIs (dev mode) and HTTP URLs (production with Supabase Storage)

## How to Use

1. Navigate to **Captura Tarjetas** in the sidebar
2. Upload a business card photo — extraction runs automatically
3. View extracted data (company, contact, phone, email, address) with color-coded confidence badges:
   - **Green** (≥80%): High confidence
   - **Yellow** (≥50%): Medium confidence
   - **Red** (<50%): Low confidence
4. If extraction fails, click **Reintentar** to retry
5. For pending cards (auto-extract disabled), click **Extraer** to trigger manually

## Configuration

No new environment variables required. Uses existing AI provider configuration:

- `ANTHROPIC_API_KEY` — for Claude vision extraction
- `OPENAI_API_KEY` — for GPT-4o vision extraction
- `EXTRACTION_AI_PROVIDER` — selects preferred provider (in `apps/Server/app/config/settings.py`)

## Testing

- **Backend**: `cd apps/Server && python -m pytest tests/ -v --tb=short`
- **Frontend type check**: `cd apps/Client && npx tsc --noEmit`
- **Frontend build**: `cd apps/Client && npm run build`
- **Linting**: `cd apps/Client && npm run lint` and `cd apps/Server && python -m ruff check .`
- **E2E**: Run `.claude/commands/e2e/test_business_card_extraction.md`

## Notes

- Extraction is synchronous (~2-5 seconds) since it processes a single image; can be moved to background tasks if latency becomes an issue
- `province` and `qr_code_detected` fields are stored in `extraction_raw_response` (JSONB) since the DB schema has no dedicated columns
- All UI text is in Spanish (Colombian)
- Extraction on already-extracted cards is rejected (only `pending` or `failed` status allowed)
