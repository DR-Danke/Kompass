# Feature: Business Card Photo Ingestion (TradeFair Wave 1)

## Metadata
issue_number: `140`
adw_id: `b15648cb`
issue_json: ``

## Feature Description
Build the foundational upload infrastructure for the Trade Fair Supplier Capture system. This enables users to photograph or upload supplier business card images at trade fairs, stores them via Supabase Storage, creates tracking records in a new `business_card_captures` database table, and adds trade fair metadata columns to the existing `suppliers` table. The page must be mobile-responsive as it will primarily be used on phones at trade fairs. This is Wave 1 of 5 — subsequent waves will add AI extraction (TF-002), supplier creation, and automated outreach.

## User Story
As a Kompass sourcing agent attending a trade fair
I want to quickly photograph supplier business cards from my phone and upload them to the system
So that I can capture supplier contact information efficiently and process it later with AI extraction

## Problem Statement
At trade fairs, sourcing agents collect large numbers of supplier business cards. Currently there is no digital capture pipeline — cards must be manually transcribed later, leading to data loss, delays, and missed follow-ups. The system needs a fast, mobile-friendly way to photograph and upload business cards for subsequent automated processing.

## Solution Statement
Create a full-stack business card photo upload pipeline:
1. A new `business_card_captures` PostgreSQL table to track uploaded cards and their processing status
2. New columns on the `suppliers` table for trade fair metadata (source, fair_name, capture_date, outreach_status, wechat_id)
3. Backend API endpoints under `/api/extract/` for uploading images, listing captures, and retrieving individual capture details
4. A new `BusinessCardCaptureService` for business logic
5. A mobile-responsive frontend page (`CardCapturePage`) with camera/file upload, progress indicators, and a list of recent captures
6. Image storage via Supabase Storage (with base64 fallback for development)

## Relevant Files
Use these files to implement the feature:

### Existing Files to Modify
- `apps/Server/database/schema.sql` — Add `business_card_captures` table and new `suppliers` columns. Follow existing table patterns (UUIDs, timestamps, CHECK constraints, indexes, triggers).
- `apps/Server/app/models/kompass_dto.py` — Add DTOs for business card capture (create, response, list). Follow existing DTO patterns (Pydantic BaseModel, Optional fields, model_config).
- `apps/Server/app/repository/kompass_repository.py` — Add `BusinessCardCaptureRepository` class following existing repository patterns (get_database_connection, try/except/finally, cursor-based queries).
- `apps/Server/app/api/extraction_routes.py` — Add 3 new endpoints for business card upload, list, and get. Follow existing upload patterns from audit_routes.py.
- `apps/Server/main.py` — No changes needed; extraction_routes already registered at `/api/extract`.
- `apps/Client/src/types/kompass.ts` — Add `BusinessCardCapture` interface matching backend DTOs.
- `apps/Client/src/services/kompassService.ts` — Add `businessCardService` with upload (FormData + progress), list, and get methods following the `auditService` pattern.
- `apps/Client/src/App.tsx` — Add route for `/card-capture` → `CardCapturePage`.
- `apps/Client/src/components/layout/Sidebar.tsx` — Add nav item for "Captura Tarjetas" with appropriate icon.

### Reference Files (read-only patterns)
- `apps/Server/app/api/audit_routes.py` — Reference for file upload pattern with Supabase Storage + validation.
- `apps/Server/app/services/audit_service.py` — Reference for service layer pattern.
- `apps/Server/app/services/storage_service.py` — Supabase Storage upload service (use this for image storage).
- `apps/Server/app/repository/audit_repository.py` — Reference for repository pattern with separate file.
- `apps/Client/src/pages/kompass/NichesPage.tsx` — Reference for page component patterns.
- `.claude/commands/test_e2e.md` — Read to understand how E2E tests are executed.
- `.claude/commands/e2e/test_niches_page.md` — Reference for E2E test format.

### New Files
- `apps/Server/database/migration_add_business_card_capture.sql` — Migration script for the new table and supplier columns.
- `apps/Server/app/services/business_card_service.py` — Business logic service for card capture operations.
- `apps/Server/app/repository/business_card_repository.py` — Data access layer for business_card_captures table.
- `apps/Client/src/pages/kompass/CardCapturePage.tsx` — Mobile-responsive card capture page.
- `.claude/commands/e2e/test_card_capture_page.md` — E2E test specification for the card capture page.

## Implementation Plan
### Phase 1: Foundation
- Create the database migration script with the `business_card_captures` table and supplier columns
- Update the master schema.sql to include the new table definition, indexes, and triggers
- Add backend DTOs for business card capture operations

### Phase 2: Core Implementation
- Create the business card capture repository with CRUD methods
- Create the business card capture service for business logic
- Add API endpoints to extraction_routes.py for upload (POST), list (GET), and get-by-id (GET)
- The upload endpoint stores images via Supabase Storage (using existing `storage_service`) and falls back to base64 data URL for development

### Phase 3: Integration
- Add TypeScript interfaces to kompass.ts
- Add API service methods to kompassService.ts using FormData for file upload
- Create the CardCapturePage component with mobile-responsive design
- Register the route in App.tsx and add sidebar navigation entry
- Create E2E test specification

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Task 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_niches_page.md` to understand the E2E test format
- Create `.claude/commands/e2e/test_card_capture_page.md` with the following test steps:
  1. Navigate to Card Capture page via sidebar "Captura Tarjetas" or `/card-capture`
  2. Verify page title "Captura de Tarjetas" is visible
  3. Verify upload area/button is visible
  4. Enter a fair name (e.g., "Canton Fair 2026")
  5. Upload a test image file (.jpg or .png) using the file input
  6. Verify upload progress/success indicator appears
  7. Verify the uploaded card appears in the recent captures list with "pending" status
  8. Verify the capture card shows the image thumbnail and fair name
  9. Screenshot key states: page loaded, upload in progress, capture listed

### Task 2: Create Database Migration
- Create `apps/Server/database/migration_add_business_card_capture.sql` with:
  - `business_card_captures` table with all columns as specified in the issue (id, image_url, status with CHECK constraint, extracted fields, metadata, timestamps)
  - Indexes on status, supplier_id, and created_at
  - ALTER TABLE statements to add columns to `suppliers`: source, fair_name, capture_date, outreach_status (with CHECK constraint), wechat_id

### Task 3: Update Master Schema
- Update `apps/Server/database/schema.sql`:
  - Add the `business_card_captures` table definition after the `supplier_audits` section (before products)
  - Add new columns to the existing `suppliers` CREATE TABLE statement: source, fair_name, capture_date, outreach_status, wechat_id
  - Add indexes for the new table
  - Add auto-update trigger for `business_card_captures`

### Task 4: Add Backend DTOs
- Add to `apps/Server/app/models/kompass_dto.py`:
  - `BusinessCardCaptureStatus` enum: pending, processing, extracted, confirmed, rejected, failed
  - `BusinessCardCaptureCreateDTO(BaseModel)`: fair_name (Optional[str]), notes (Optional[str])
  - `BusinessCardCaptureResponseDTO(BaseModel)`: all fields from the table (id as UUID, image_url, status, contact fields, metadata, timestamps) with `model_config = {"from_attributes": True}`
  - `BusinessCardCaptureListResponseDTO(BaseModel)`: captures (List[BusinessCardCaptureResponseDTO]), total (int)

### Task 5: Create Backend Repository
- Create `apps/Server/app/repository/business_card_repository.py` following existing repository patterns:
  - `BusinessCardCaptureRepository` class with:
    - `create(image_url, fair_name, notes, captured_by)` — INSERT RETURNING all columns
    - `get_by_id(capture_id)` — SELECT by UUID
    - `list_captures(status_filter, limit, offset)` — SELECT with optional WHERE status filter, ORDER BY created_at DESC, with total count
    - `update(capture_id, updates: dict)` — Dynamic UPDATE for provided fields
  - Use `get_database_connection()` / `close_database_connection(conn)` pattern
  - Singleton instance: `business_card_repository = BusinessCardCaptureRepository()`

### Task 6: Create Backend Service
- Create `apps/Server/app/services/business_card_service.py`:
  - `BusinessCardService` class with:
    - `create_capture(image_url, fair_name, notes, captured_by)` — calls repository.create, returns dict
    - `get_capture(capture_id)` — calls repository.get_by_id, raises if not found
    - `list_captures(status_filter, limit, offset)` — calls repository.list_captures, returns list + total
    - `update_capture(capture_id, updates)` — calls repository.update
  - Logging with `print(f"INFO [BusinessCardService]: ...")`
  - Singleton instance: `business_card_service = BusinessCardService()`

### Task 7: Add Backend API Endpoints
- Modify `apps/Server/app/api/extraction_routes.py` to add:
  - `POST /business-card` endpoint:
    - Accepts `UploadFile` (file) + optional `Form` fields (fair_name, notes)
    - Validates file extension (.png, .jpg, .jpeg only) and size (max 10MB)
    - Uploads to Supabase Storage via `storage_service.upload_file()` with folder `business-cards` and content_type based on extension
    - Falls back to base64 data URL if storage not configured (for development)
    - Creates a `business_card_captures` record via service with status "pending"
    - Returns `BusinessCardCaptureResponseDTO`
    - Requires auth: `require_roles(["admin", "manager", "user"])`
  - `GET /business-cards` endpoint:
    - Optional query param: `status` (string filter)
    - Optional query params: `limit` (int, default 50), `offset` (int, default 0)
    - Returns `BusinessCardCaptureListResponseDTO`
    - Requires auth
  - `GET /business-cards/{capture_id}` endpoint:
    - Path param: `capture_id` (UUID)
    - Returns `BusinessCardCaptureResponseDTO`
    - Requires auth
  - Import `storage_service` from `app.services.storage_service`
  - Import `business_card_service` from `app.services.business_card_service`
  - Import new DTOs from `app.models.kompass_dto`
  - Add `Form` import from `fastapi`

### Task 8: Add Frontend Types
- Add to `apps/Client/src/types/kompass.ts`:
  - `BusinessCardCaptureStatus` type: `'pending' | 'processing' | 'extracted' | 'confirmed' | 'rejected' | 'failed'`
  - `BusinessCardCapture` interface with all fields matching the response DTO

### Task 9: Add Frontend API Service
- Add to `apps/Client/src/services/kompassService.ts`:
  - `businessCardService` object with:
    - `uploadCard(file: File, fairName?: string, notes?: string, onProgress?: (percent: number) => void): Promise<BusinessCardCapture>` — use XMLHttpRequest for progress tracking (same pattern as `auditService.upload`), send FormData with file + optional fair_name + notes fields, POST to `/extract/business-card`
    - `listCaptures(status?: string, limit?: number, offset?: number): Promise<{captures: BusinessCardCapture[], total: number}>` — GET `/extract/business-cards` with query params
    - `getCapture(id: string): Promise<BusinessCardCapture>` — GET `/extract/business-cards/${id}`

### Task 10: Create Card Capture Page
- Create `apps/Client/src/pages/kompass/CardCapturePage.tsx`:
  - **UI Language:** Spanish (Colombian) for all labels, messages, and placeholders
  - **Mobile-responsive design** — optimized for phone viewport at trade fairs
  - **Layout:**
    - Page title: "Captura de Tarjetas"
    - Optional `fair_name` text field at the top (persisted in component state across uploads within the session, label: "Nombre de la Feria")
    - Large, prominent upload button/area with camera icon (large touch target, min 60px height)
    - Accept attribute: `.png,.jpg,.jpeg`; max 10MB validation with error snackbar
    - Upload progress bar shown during upload
    - List of recently captured cards below, ordered by most recent first
  - **Card list items show:**
    - Thumbnail of the uploaded image
    - Status chip (color-coded: pending=orange, processing=blue, extracted=green, confirmed=teal, rejected=red, failed=red)
    - Fair name (if set)
    - Timestamp (relative or formatted)
    - Company name (if extracted, from TF-002 — show placeholder for now)
  - **State management:**
    - `captures` state loaded on mount via `businessCardService.listCaptures()`
    - `uploading` boolean state for upload-in-progress UI
    - `uploadProgress` number state for progress bar
    - `fairName` string state persisted across uploads
    - `error` / `success` snackbar states
  - **Upload flow:**
    1. User selects file (via input or camera)
    2. Validate file type and size client-side
    3. Show progress bar during upload
    4. On success: prepend new capture to list, show success snackbar
    5. On error: show error snackbar
  - Use Material-UI components: Box, Typography, Button, TextField, Card, CardMedia, Chip, LinearProgress, Snackbar, Alert, IconButton
  - Use `useCallback` and `useEffect` for data fetching
  - Follow logging convention: `console.log('INFO [CardCapturePage]: ...')`

### Task 11: Register Route and Navigation
- In `apps/Client/src/App.tsx`:
  - Import `CardCapturePage` from `./pages/kompass/CardCapturePage`
  - Add route: `<Route path="card-capture" element={<CardCapturePage />} />`
- In `apps/Client/src/components/layout/Sidebar.tsx`:
  - Import `CameraAltIcon` from `@mui/icons-material/CameraAlt`
  - Add nav item to `navItems` array after "Import Wizard": `{ title: 'Captura Tarjetas', icon: <CameraAltIcon />, path: '/card-capture' }`

### Task 12: Run Validation Commands
- Run all validation commands listed below to confirm zero regressions

## Testing Strategy
### Unit Tests
- Backend repository methods: verify SQL queries execute correctly (tested implicitly via API integration tests)
- Backend service methods: verify business logic delegation to repository
- Backend API endpoints: test upload with valid/invalid files, list with/without filters, get by ID
- Frontend: TypeScript type checking ensures DTO alignment

### Edge Cases
- Upload file exceeding 10MB limit — should return 400 error
- Upload file with unsupported extension (.gif, .bmp, .pdf) — should return 400 error
- Upload when Supabase Storage is not configured — should fallback to base64 data URL
- List captures with no results — should return empty array with total 0
- Get capture with non-existent ID — should return 404
- Upload with empty file — should return 400 error
- Very long fair_name or notes values — constrained by DB column lengths
- Concurrent uploads from the same user — should create separate records

## Acceptance Criteria
- [ ] `business_card_captures` table exists with all specified columns, constraints, and indexes
- [ ] `suppliers` table has new columns: source, fair_name, capture_date, outreach_status, wechat_id
- [ ] POST `/api/extract/business-card` accepts image uploads (.png, .jpg, .jpeg ≤ 10MB) and stores them
- [ ] GET `/api/extract/business-cards` returns paginated list with optional status filter
- [ ] GET `/api/extract/business-cards/{id}` returns single capture details
- [ ] CardCapturePage is accessible at `/card-capture` and listed in sidebar as "Captura Tarjetas"
- [ ] Page is mobile-responsive with large upload button suitable for phone use
- [ ] Fair name field persists across multiple uploads in the same session
- [ ] Upload progress is displayed during file upload
- [ ] Recently captured cards are shown in a list with status indicators
- [ ] All UI text is in Spanish (Colombian)
- [ ] TypeScript compiles with no errors
- [ ] Frontend builds successfully
- [ ] Backend tests pass with no regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/ -v --tb=short` — Run Server tests to validate the feature works with zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate the feature works with zero regressions
- `cd apps/Client && npm run build` — Run Client build to validate the feature works with zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_card_capture_page.md` E2E test to validate this functionality works

## Notes
- **Image Storage Strategy:** Use Supabase Storage via the existing `storage_service` (folder: `business-cards`). For local development without Supabase configured, fall back to storing a base64 data URL in the `image_url` column. This matches the pattern used by audit_routes.py.
- **No new dependencies needed:** The implementation uses existing libraries (FastAPI UploadFile, Supabase Storage client, Material-UI, Axios).
- **Future waves:** TF-002 will add AI vision extraction to process uploaded images. The `status` field and extracted contact fields are prepared for that. TF-003+ will handle supplier creation and outreach.
- **The `business_card_captures` table is intentionally separate from `supplier_audits`** — different purpose (contact extraction vs. factory qualification), different workflow, different extracted fields.
- **File validation is enforced both client-side and server-side** for defense in depth.
