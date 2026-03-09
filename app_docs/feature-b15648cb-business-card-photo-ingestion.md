# Business Card Photo Ingestion (Trade Fair Wave 1)

**ADW ID:** b15648cb
**Date:** 2026-03-09
**Specification:** specs/issue-140-adw-b15648cb-sdlc_planner-business-card-photo-ingestion.md

## Overview

Full-stack feature enabling sourcing agents to photograph and upload supplier business cards at trade fairs from their mobile devices. Uploaded images are stored via Supabase Storage (with base64 fallback for development), tracked in a new `business_card_captures` database table, and displayed in a mobile-responsive capture list. This is Wave 1 of the Trade Fair Supplier Capture system — future waves will add AI extraction, supplier creation, and automated outreach.

## What Was Built

- **Database layer:** New `business_card_captures` table with status workflow and extracted contact fields; new trade fair metadata columns on `suppliers` table
- **Backend API:** Three new endpoints under `/api/extract/` for uploading business card images, listing captures, and retrieving individual captures
- **Backend service/repository:** `BusinessCardService` and `BusinessCardCaptureRepository` following existing clean architecture patterns
- **Frontend page:** Mobile-responsive `CardCapturePage` at `/card-capture` with camera/file upload, progress tracking, and recent captures list
- **Frontend service:** `businessCardService` with XHR-based upload (for progress tracking), list, and get methods
- **Navigation:** Sidebar entry "Captura Tarjetas" with camera icon
- **E2E test spec:** `.claude/commands/e2e/test_card_capture_page.md`

## Technical Implementation

### Files Modified

- `apps/Server/database/schema.sql`: Added `business_card_captures` table definition, indexes, trigger, and trade fair columns to `suppliers`
- `apps/Server/database/migration_add_business_card_capture.sql`: Migration script for the new table and supplier column alterations
- `apps/Server/app/models/kompass_dto.py`: Added `BusinessCardCaptureStatus` enum, `BusinessCardCaptureCreateDTO`, `BusinessCardCaptureResponseDTO`, `BusinessCardCaptureListResponseDTO`
- `apps/Server/app/repository/business_card_repository.py`: New repository with `create`, `get_by_id`, `list_captures`, `update` methods
- `apps/Server/app/services/business_card_service.py`: New service layer delegating to repository with logging
- `apps/Server/app/api/extraction_routes.py`: Added `POST /business-card`, `GET /business-cards`, `GET /business-cards/{capture_id}` endpoints with auth and file validation
- `apps/Client/src/types/kompass.ts`: Added `BusinessCardCaptureStatus` type and `BusinessCardCapture` interface
- `apps/Client/src/services/kompassService.ts`: Added `businessCardService` with `uploadCard` (XHR + progress), `listCaptures`, `getCapture`
- `apps/Client/src/pages/kompass/CardCapturePage.tsx`: New mobile-responsive page with upload area, progress bar, and captures list
- `apps/Client/src/App.tsx`: Added `/card-capture` route
- `apps/Client/src/components/layout/Sidebar.tsx`: Added "Captura Tarjetas" nav item with `CameraAltIcon`

### Key Changes

- **Image upload** uses `UploadFile` on backend with validation for `.png/.jpg/.jpeg` and max 10MB; stores via `storage_service` (Supabase Storage) with base64 data URL fallback
- **Upload progress tracking** implemented via `XMLHttpRequest` on frontend (same pattern as audit upload) rather than Axios, to support `onProgress` callbacks
- **Status workflow:** `pending → processing → extracted → confirmed → rejected → failed` — Wave 1 creates captures in `pending` status; AI extraction (Wave 2) will transition through subsequent states
- **Trade fair metadata** on `suppliers` table includes `source`, `fair_name`, `capture_date`, `outreach_status` (with CHECK constraint), and `wechat_id` — prepared for Wave 3 supplier creation
- **All UI text** is in Spanish (Colombian) as required for the target user base

### Database Schema

```sql
-- New table
business_card_captures (
  id UUID PK, image_url, status, company_name, contact_name,
  contact_email, contact_phone, contact_wechat, website, address,
  supplier_id FK, fair_name, notes, captured_by FK, extraction_raw_response JSONB,
  created_at, updated_at
)

-- New supplier columns
suppliers + (source, fair_name, capture_date, outreach_status, wechat_id)
```

### API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/extract/business-card` | Upload business card image | admin, manager, user |
| GET | `/api/extract/business-cards` | List captures (with optional status filter, pagination) | admin, manager, user |
| GET | `/api/extract/business-cards/{id}` | Get single capture details | admin, manager, user |

## How to Use

1. Navigate to **Captura Tarjetas** in the sidebar (or go to `/card-capture`)
2. Optionally enter the trade fair name in the "Nombre de la Feria" field — this persists across uploads in the same session
3. Tap the upload button or camera area to select/photograph a business card image (.png, .jpg, .jpeg, max 10MB)
4. Watch the progress bar during upload
5. On success, the new capture appears at the top of the recent captures list with a "pending" status chip
6. Repeat for additional cards — the fair name carries over automatically

## Configuration

- **Supabase Storage:** Images stored in `business-cards` folder. If Supabase Storage is not configured (local dev), falls back to base64 data URLs in the database
- **No new environment variables** required — uses existing `DATABASE_URL` and Supabase Storage configuration

## Testing

- **Backend tests:** `cd apps/Server && python -m pytest tests/ -v --tb=short`
- **TypeScript:** `cd apps/Client && npx tsc --noEmit`
- **Build:** `cd apps/Client && npm run build`
- **E2E:** Run `/test_e2e` with `.claude/commands/e2e/test_card_capture_page.md`

## Notes

- **Wave 1 only:** This feature provides the upload infrastructure. Captured cards remain in `pending` status until Wave 2 (TF-002) adds AI vision extraction
- **Extracted contact fields** (`company_name`, `contact_email`, etc.) are present in the schema but will be populated by future AI extraction
- **The `business_card_captures` table is separate from `supplier_audits`** — different purpose (contact extraction vs. factory qualification), different workflow
- **File validation** is enforced both client-side and server-side for defense in depth
- **Mobile-responsive design** with large touch targets (min 60px) optimized for phone use at trade fairs
