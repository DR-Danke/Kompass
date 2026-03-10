# Feature: Review & Confirm Extracted Suppliers

## Metadata
issue_number: `144`
adw_id: `ba9f1399`
issue_json: ``

## Feature Description
Create a dedicated review interface for business card extractions where the back-office team can view, edit, approve, or reject extracted supplier data before it is finalized. This page acts as a quality-control step between AI extraction (TF-002) and automatic supplier creation (TF-003). Team members can correct AI extraction errors, view confidence scores, approve cards to trigger supplier creation + outreach email, or reject cards with a reason. Batch actions allow processing multiple cards at once.

## User Story
As a back-office team member reviewing trade fair captures
I want to see all extracted business cards, correct any AI mistakes, and approve or reject supplier creation
So that only accurate supplier records enter our database and outreach emails go to the right contacts

## Problem Statement
Currently, the CardCapturePage combines upload, extraction, and supplier creation into a single workflow on the same page. There is no way to:
- Edit extracted fields to correct AI mistakes before creating a supplier
- Reject a card with a reason (only duplicate detection auto-rejects)
- Batch approve/reject multiple cards at once
- Have a dedicated review interface for team members who weren't at the fair

## Solution Statement
Add a new CardReviewPage at `/card-review` with a table/list view of business card captures filtered by status. Each row shows the card image thumbnail alongside editable extracted fields with confidence indicators. Approve triggers supplier creation + email outreach. Reject requires confirmation with an optional reason. Batch actions allow processing multiple cards simultaneously. Backend endpoints support updating fields, approving, and rejecting captures.

## Relevant Files
Use these files to implement the feature:

**Backend - Routes & API:**
- `apps/Server/app/api/extraction_routes.py` — Add PUT update, POST approve, POST reject endpoints for business cards. Existing endpoints at lines 309-508 handle list/get/extract/create-supplier.
- `apps/Server/main.py` — No changes needed; extraction router already mounted.

**Backend - Services:**
- `apps/Server/app/services/business_card_service.py` — Already has `update_capture()` (line 99). Add `approve_card()` and `reject_card()` methods.
- `apps/Server/app/services/supplier_service.py` — Contains `create_supplier_from_card()` (line 526). Called by approve flow.

**Backend - DTOs:**
- `apps/Server/app/models/kompass_dto.py` — Add `BusinessCardUpdateDTO` and `BusinessCardRejectDTO`. Existing business card DTOs at lines 631-667.

**Backend - Repository:**
- `apps/Server/app/repository/business_card_repository.py` — Already has `update()` method (line 163). No changes needed.

**Backend - Tests:**
- `apps/Server/tests/test_extraction_routes.py` — Add tests for new PUT, POST approve, POST reject endpoints.

**Frontend - Types:**
- `apps/Client/src/types/kompass.ts` — `BusinessCardCapture` (line 1048) and `SupplierFromCardResult` (line 1068) already defined. No changes needed.

**Frontend - API Service:**
- `apps/Client/src/services/kompassService.ts` — Add `updateBusinessCardCapture()`, `approveBusinessCard()`, `rejectBusinessCard()` to `businessCardService` object (line 1156).

**Frontend - Hook:**
- `apps/Client/src/hooks/kompass/useCardReview.ts` — **New file.** Custom hook for review page state management.

**Frontend - Page:**
- `apps/Client/src/pages/kompass/CardReviewPage.tsx` — **New file.** Review & confirm page component.

**Frontend - Router:**
- `apps/Client/src/App.tsx` — Add import and route for CardReviewPage.

**Frontend - Navigation:**
- `apps/Client/src/components/layout/Sidebar.tsx` — Add nav item for card review page.

**Frontend - Reference:**
- `apps/Client/src/pages/kompass/CardCapturePage.tsx` — Reference for status colors, confidence display, and UI patterns.
- `apps/Client/src/hooks/kompass/useClients.ts` — Reference for hook pattern (state interface, return interface, useCallback, useEffect).

**E2E Test:**
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_card_capture_page.md` to understand how to create an E2E test file.

### New Files
- `apps/Client/src/pages/kompass/CardReviewPage.tsx` — Review & confirm page
- `apps/Client/src/hooks/kompass/useCardReview.ts` — Custom hook for review page
- `.claude/commands/e2e/test_card_review_page.md` — E2E test for the review page

## Implementation Plan
### Phase 1: Foundation
Add backend DTOs for update and reject operations. Add backend service methods for approve and reject flows. Add backend API endpoints.

### Phase 2: Core Implementation
Create the frontend API service methods, custom hook, and CardReviewPage component with editable fields, confidence indicators, approve/reject actions, and batch operations.

### Phase 3: Integration
Register the route in App.tsx, add navigation entry in Sidebar.tsx, create E2E test, and validate everything works end-to-end.

## Step by Step Tasks

### Step 1: Add Backend DTOs
- Open `apps/Server/app/models/kompass_dto.py`
- Add `BusinessCardUpdateDTO` (Pydantic BaseModel) with optional fields: `contact_name`, `contact_phone`, `contact_email`, `company_name`, `address`, `province`, `fair_name`, `notes`
- Add `BusinessCardRejectDTO` (Pydantic BaseModel) with optional field: `reason: Optional[str] = None`
- Place these near the existing `BusinessCardCaptureResponseDTO` (around line 630)

### Step 2: Add Backend Service Methods
- Open `apps/Server/app/services/business_card_service.py`
- Add `approve_card(self, capture_id: UUID) -> Dict[str, Any]` method:
  - Get capture, validate status is "extracted"
  - Call `supplier_service.create_supplier_from_card(capture_id)` — this already handles setting status to "confirmed", linking supplier_id, duplicate detection (sets "rejected"), and sending email
  - Return the `SupplierFromCardResultDTO` from supplier_service
- Add `reject_card(self, capture_id: UUID, reason: Optional[str] = None) -> Dict[str, Any]` method:
  - Get capture, validate status is "extracted" or "pending" or "failed"
  - Update capture status to "rejected"
  - If reason provided, store in the `notes` field (append to existing notes if any)
  - Return updated capture dict

### Step 3: Add Backend API Endpoints
- Open `apps/Server/app/api/extraction_routes.py`
- Import `BusinessCardUpdateDTO` and `BusinessCardRejectDTO` from kompass_dto
- Add `PUT /business-cards/{capture_id}` endpoint:
  - Requires roles: admin, manager, user
  - Accepts `BusinessCardUpdateDTO` body
  - Calls `business_card_service.update_capture(capture_id, updates.model_dump(exclude_unset=True))`
  - Returns `BusinessCardCaptureResponseDTO`
- Add `POST /business-cards/{capture_id}/approve` endpoint:
  - Requires roles: admin, manager, user
  - Calls `business_card_service.approve_card(capture_id)`
  - Returns `SupplierFromCardResultDTO`
- Add `POST /business-cards/{capture_id}/reject` endpoint:
  - Requires roles: admin, manager, user
  - Accepts optional `BusinessCardRejectDTO` body
  - Calls `business_card_service.reject_card(capture_id, body.reason)`
  - Returns `BusinessCardCaptureResponseDTO`
- Place these endpoints between the existing `get_business_card` (line 361) and `extract_business_card` (line 406) endpoints, or after `create_supplier_from_card` (line 508) — but BEFORE the `/{job_id}` catch-all route (line 511)

### Step 4: Add Backend Tests
- Open `apps/Server/tests/test_extraction_routes.py`
- Add test class or test functions for the three new endpoints:
  - `test_update_business_card_success` — mock service, verify 200 with updated fields
  - `test_update_business_card_not_found` — mock ValueError, verify 404
  - `test_approve_business_card_success` — mock approve_card returning SupplierFromCardResultDTO, verify 200
  - `test_approve_business_card_invalid_status` — mock ValueError, verify 400
  - `test_reject_business_card_success` — mock reject_card, verify 200
  - `test_reject_business_card_with_reason` — verify reason is passed through
  - `test_viewer_cannot_approve` — verify viewer role gets 403
  - `test_viewer_cannot_reject` — verify viewer role gets 403

### Step 5: Create E2E Test File
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_card_capture_page.md` for format reference
- Create `.claude/commands/e2e/test_card_review_page.md` with:
  - User story: As a back-office team member, I want to review extracted business cards and approve/reject them
  - Step 1: Navigate to `/card-review`, verify page title "Revisión de Tarjetas" is visible
  - Step 2: Verify status filter tabs/buttons (Todos, Extraídas, Confirmadas, Rechazadas) are visible
  - Step 3: Verify the captures table/list shows columns: image, company, contact, email, phone, status, actions
  - Step 4: If extracted cards exist, verify editable fields can be clicked/edited
  - Step 5: Verify confidence score color indicators are visible on extracted cards
  - Step 6: Verify "Aprobar" and "Rechazar" buttons are visible on extracted cards
  - Step 7: Click "Rechazar" on a card, verify confirmation dialog appears with reason field
  - Step 8: Verify batch selection checkboxes and batch action buttons
  - Screenshots at each step
  - Success criteria covering all UI elements and interactions

### Step 6: Add Frontend API Service Methods
- Open `apps/Client/src/services/kompassService.ts`
- Add to the `businessCardService` object (after `createSupplierFromCard` at line 1249):
  - `updateBusinessCardCapture(captureId: string, updates: Partial<BusinessCardCapture>)` — PUT to `/extract/business-cards/${captureId}`, returns `BusinessCardCapture`
  - `approveBusinessCard(captureId: string)` — POST to `/extract/business-cards/${captureId}/approve`, returns `SupplierFromCardResult`
  - `rejectBusinessCard(captureId: string, reason?: string)` — POST to `/extract/business-cards/${captureId}/reject` with `{ reason }` body, returns `BusinessCardCapture`

### Step 7: Create useCardReview Hook
- Create `apps/Client/src/hooks/kompass/useCardReview.ts`
- Follow pattern from `useClients.ts`: state interface, return interface, useState, useCallback, useEffect
- State: `captures: BusinessCardCapture[]`, `total: number`, `statusFilter: BusinessCardCaptureStatus | null`, `selectedIds: Set<string>`, `isLoading: boolean`, `isProcessing: boolean`, `error: string | null`
- Methods:
  - `fetchCaptures(statusFilter?)` — calls `businessCardService.listCaptures()`
  - `updateField(captureId, fieldName, value)` — calls `businessCardService.updateBusinessCardCapture()` with optimistic update
  - `approveCard(captureId)` — calls `businessCardService.approveBusinessCard()`, updates local state based on result (confirmed or rejected for duplicates)
  - `rejectCard(captureId, reason?)` — calls `businessCardService.rejectBusinessCard()`, updates local state
  - `batchApprove(captureIds)` — loop through IDs calling approveCard sequentially
  - `batchReject(captureIds, reason?)` — loop through IDs calling rejectCard sequentially
  - `toggleSelection(captureId)` and `toggleSelectAll()`
  - `setStatusFilter(status)` — updates filter and re-fetches
  - `clearError()`
- useEffect to fetch captures on mount and when statusFilter changes

### Step 8: Create CardReviewPage Component
- Create `apps/Client/src/pages/kompass/CardReviewPage.tsx`
- All UI text in Spanish (Colombian)
- Page title: "Revisión de Tarjetas"
- Status filter tabs using MUI Tabs or ToggleButtonGroup: Todos, Pendientes, Extraídas, Confirmadas, Rechazadas
- Table/list view of captures using MUI Table or Card list:
  - Checkbox column for batch selection
  - Image thumbnail (80x80 px) — use the `image_url` from capture
  - Extracted fields displayed as editable TextFields (inline edit): company_name, contact_name, contact_email, contact_phone, address, province
  - Confidence score indicators per field: green chip (≥0.8), yellow chip (≥0.5), red chip (<0.5) — extract from `extraction_raw_response.confidence_scores`
  - Status chip with colors matching existing STATUS_COLORS pattern from CardCapturePage
  - Fair name display
  - Timestamps (created_at)
  - Actions column:
    - "Aprobar" button (green, CheckCircle icon) — visible only for "extracted" status
    - "Rechazar" button (red, Cancel icon) — visible only for "extracted", "pending", "failed" status
- Batch action bar (appears when items selected):
  - "Aprobar Seleccionados" button
  - "Rechazar Seleccionados" button
- Reject confirmation dialog (MUI Dialog):
  - Title: "Rechazar Tarjeta"
  - Optional TextField for reason: "Motivo del rechazo (opcional)"
  - Cancel and Confirm buttons
- Snackbar for success/error feedback
- Loading skeleton/spinner while fetching
- Empty state message when no captures match filter
- Use the `useCardReview` hook for all state management

### Step 9: Register Route and Navigation
- Open `apps/Client/src/App.tsx`:
  - Add import: `import CardReviewPage from './pages/kompass/CardReviewPage';`
  - Add route after `card-capture`: `<Route path="card-review" element={<CardReviewPage />} />`
- Open `apps/Client/src/components/layout/Sidebar.tsx`:
  - Import `RateReviewIcon` from `@mui/icons-material/RateReview`
  - Add nav item after "Captura Tarjetas" entry: `{ title: 'Revisión Tarjetas', icon: <RateReviewIcon />, path: '/card-review' }`

### Step 10: Run Validation Commands
- Run all validation commands listed below to verify zero regressions

## Testing Strategy
### Unit Tests
- Backend: Test new PUT, POST approve, POST reject endpoints with mocked services
- Backend: Test service methods approve_card and reject_card with mocked repository
- Backend: Test role-based access (viewer denied, user/manager/admin allowed)
- Frontend: TypeScript type checking validates all API contracts

### Edge Cases
- Approving a card that is not in "extracted" status → should return 400
- Approving a card that has already been linked to a supplier → should return 400
- Rejecting an already-rejected card → should return 400
- Updating fields on a confirmed card → should be allowed (no status restriction on field edits)
- Batch approve where some cards fail (duplicate) and some succeed → each should be handled individually
- Empty reason on reject → should be allowed (reason is optional)
- Confidence scores not present in extraction_raw_response → should show no indicators gracefully

## Acceptance Criteria
- [ ] PUT `/api/extract/business-cards/{id}` updates editable fields and returns updated capture
- [ ] POST `/api/extract/business-cards/{id}/approve` triggers supplier creation + email, returns SupplierFromCardResultDTO
- [ ] POST `/api/extract/business-cards/{id}/reject` sets status to "rejected", optionally stores reason
- [ ] CardReviewPage loads at `/card-review` with title "Revisión de Tarjetas"
- [ ] Status filter tabs work (Todos, Pendientes, Extraídas, Confirmadas, Rechazadas)
- [ ] Extracted fields are editable inline with save on blur/enter
- [ ] Confidence scores are color-coded (green ≥0.8, yellow ≥0.5, red <0.5)
- [ ] "Aprobar" button creates supplier and updates card status to confirmed
- [ ] "Rechazar" button shows confirmation dialog, then rejects card
- [ ] Batch approve/reject works for multiple selected cards
- [ ] Sidebar navigation includes "Revisión Tarjetas" entry
- [ ] All UI text is in Spanish (Colombian)
- [ ] Viewer role cannot approve or reject (backend enforced)
- [ ] All existing tests pass with zero regressions
- [ ] Frontend builds without TypeScript errors

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/ -v --tb=short` — Run all backend tests including new review endpoint tests
- `cd apps/Client && npx tsc --noEmit` — Run TypeScript type check to validate no type errors
- `cd apps/Client && npm run build` — Run production build to validate no build errors
- `cd apps/Client && npm run lint` — Run ESLint to validate no lint errors
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_card_review_page.md` E2E test to validate the review page works

## Notes
- The approve endpoint reuses the existing `supplier_service.create_supplier_from_card()` method which already handles duplicate detection, email sending, and status updates. The new `approve_card` method in business_card_service is a thin wrapper.
- The `province` field is mentioned in the issue but does not exist in the database schema. The implementation should store province in the `address` field or the `extraction_raw_response` JSONB, or add it as a new column. Recommendation: use the existing `address` field and let users include province information there.
- The `BusinessCardReviewActionDTO` from the issue spec is split into two separate DTOs (`BusinessCardUpdateDTO` and `BusinessCardRejectDTO`) for cleaner API design — each endpoint gets its own DTO rather than a generic action DTO.
- No new Python libraries required.
- No new npm packages required.
