# WeChat ID Extraction Pipeline

**ADW ID:** 931a99d6
**Date:** 2026-03-10
**Specification:** specs/issue-165-adw-931a99d6-sdlc_planner-map-wechat-id-extraction-pipeline.md

## Overview

This feature completes the WeChat ID extraction pipeline by enhancing the AI extraction prompt with WeChat-specific recognition guidance and adding WeChat ID visibility to both the Card Review and Card Capture pages. The backend data plumbing was already in place; this feature closes the gap in the frontend UI and improves extraction accuracy.

## What Was Built

- Enhanced AI extraction prompt with WeChat-specific recognition instructions (labels, format, QR code handling)
- WeChat ID column on the Card Review page with editable cells and confidence badges
- WeChat ID extracted field on the Card Capture page with chat icon and confidence badge
- E2E test specification for validating WeChat ID visibility across both pages

## Technical Implementation

### Files Modified

- `apps/Server/app/services/extraction_service.py`: Added WeChat-specific recognition guidance to `_build_business_card_prompt()` — instructs the AI to look for labels ("WeChat", "微信", "Wechat ID", "微信号"), recognize alphanumeric 6-20 char format, and handle QR code context.
- `apps/Client/src/pages/kompass/CardReviewPage.tsx`: Added "WeChat ID" table column header and an `EditableCell` in each row for `contact_wechat`, with confidence badge and edit support.
- `apps/Client/src/pages/kompass/CardCapturePage.tsx`: Added `ChatIcon` import and an `ExtractedField` for `contact_wechat` between email and address fields, with confidence badge.
- `.claude/commands/e2e/test_wechat_id_extraction_pipeline.md`: New E2E test spec with 6 test steps covering column visibility, editability, extracted field display, and confidence badge colors.

### Key Changes

- The extraction prompt now includes a dedicated WeChat ID recognition rule covering common Chinese/English labels, expected alphanumeric format (6-20 chars, letter-first), and QR code proximity hints.
- Card Review page table gained a new column after "Teléfono" using the same `EditableCell` pattern as phone and email, enabling inline editing with confidence scoring.
- Card Capture page displays WeChat ID using the `ExtractedField` component with `ChatIcon` — returns null for empty values, so only appears when a WeChat ID is extracted.
- No backend data layer changes were needed — `contact_wechat` already flows through the repository, business card service, and supplier creation mapping.

## How to Use

1. **Capture a business card** via the Card Capture page (`/card-capture`) — the AI extraction now includes WeChat-specific recognition guidance for better accuracy.
2. **Review extracted data** on the Card Review page (`/card-review`) — the WeChat ID column shows the extracted value with a confidence badge. Click the cell to edit if needed.
3. **Verify on Card Capture page** — extracted cards show the WeChat ID alongside phone and email in the extracted fields section.
4. **Create supplier** — when creating a supplier from a reviewed card, the `contact_wechat` value maps automatically to the supplier's `wechat_id` field.

## Configuration

No new configuration required. The feature uses existing extraction service configuration and MUI components.

## Testing

- **Static analysis**: `cd apps/Client && npm run lint && npm run typecheck && npm run build`
- **Backend tests**: `cd apps/Server && python -m pytest tests/ -v --tb=short`
- **E2E test**: Run `/test_e2e` with `test_wechat_id_extraction_pipeline` to validate WeChat ID visibility on Card Review and Card Capture pages

## Notes

- No new libraries added — `ChatIcon` from `@mui/icons-material` is used as a messaging proxy icon since MUI has no dedicated WeChat icon.
- UI language remains Spanish (Colombian), but "WeChat ID" is kept as-is since it is a proper noun.
- Cards without a WeChat ID gracefully handle null: `ExtractedField` returns null (not rendered), `EditableCell` shows "—".
- Confidence badges follow existing color coding: green (>=80%), yellow (>=50%), red (<50%).
