# Feature: Add Create Supplier to Card Review Page

## Metadata
issue_number: `185`
adw_id: `d3b666c5`
issue_json: `{"number":185,"title":"Add create supplier to the <Revisión Tarjetas> page","body":"When the user takes the picture, the app sends the user to the <Revisión Tarjetas> screen. Here, the user can adjust the extracted data. After adjusting, the user has to go back to the <Captura Tarjetas> screen to create the supplier. To improve the UX, the user should also be able to create the supplier from the <Revisión Tarjetas> screen."}`

## Feature Description
Add an explicit "Crear Proveedor" (Create Supplier) button to the Card Review page (`Revisión Tarjetas`) so users can create a supplier directly after reviewing and editing extracted business card data, without having to navigate back to the Card Capture page.

Currently, the Card Review page has an "Aprobar" (Approve) button that internally creates a supplier, but the UX does not make this clear. The Card Capture page has an explicit "Crear Proveedor" button with loading states and inline result feedback. This feature brings the same explicit supplier-creation UX to the Card Review page by adding a dedicated "Crear Proveedor" button with proper loading states, result feedback, and a "Proveedor vinculado" (Linked Supplier) chip for confirmed cards.

## User Story
As a trade fair attendee using Kompass
I want to create a supplier directly from the Card Review page after editing the extracted data
So that I don't have to navigate back to the Card Capture page to complete the supplier creation workflow

## Problem Statement
After capturing a business card photo, the app navigates the user to the Card Review page where they can edit the extracted data. However, to create a supplier from the card, the user must navigate back to the Card Capture page and find the card there to click "Crear Proveedor". This extra navigation step is a UX friction point, especially during busy trade fairs where speed matters.

## Solution Statement
Add a dedicated "Crear Proveedor" button to the Card Review page's actions column for each card with status `extracted` and no linked supplier. The button will:
1. Call the existing `POST /api/extract/business-cards/{id}/create-supplier` API endpoint
2. Show a loading spinner with "Creando..." text while the request is in progress
3. Display result feedback via snackbar (success, duplicate, email status)
4. Update the card's local state to `confirmed` with the supplier_id on success
5. Show a "Proveedor vinculado" chip for confirmed cards with a linked supplier

No backend changes are needed — the API endpoint and service logic already exist.

## Relevant Files
Use these files to implement the feature:

- `apps/Client/src/pages/kompass/CardReviewPage.tsx` — The Card Review page component. Add the "Crear Proveedor" button in the actions column, loading states, and result feedback. Reference the existing "Crear Proveedor" pattern from CardCapturePage.
- `apps/Client/src/hooks/kompass/useCardReview.ts` — The Card Review hook. Add a `createSupplierFromCard` method that calls `businessCardService.createSupplierFromCard()` and manages loading/result state.
- `apps/Client/src/pages/kompass/CardCapturePage.tsx` — Reference file. Contains the existing "Crear Proveedor" button pattern with loading states (`creatingSupplierIds`), result tracking (`supplierResults`), and inline feedback. Use this as the pattern to follow.
- `apps/Client/src/services/kompassService.ts` — Contains `businessCardService.createSupplierFromCard()` (line ~1289). Already exists — no changes needed, just reference for the API call signature.
- `apps/Client/src/types/kompass.ts` — Contains `SupplierFromCardResult` and `BusinessCardCapture` types (lines 1052-1085). Already exists — no changes needed.
- `.claude/commands/test_e2e.md` — Read to understand how to create and run E2E tests.
- `.claude/commands/e2e/test_basic_query.md` — Read as an example E2E test file format.
- `.claude/commands/e2e/test_auto_create_supplier_from_card.md` — Read as reference for supplier creation E2E test patterns.
- `.claude/commands/e2e/test_card_review_page.md` — Read as reference for Card Review page E2E test patterns.

### New Files
- `.claude/commands/e2e/test_create_supplier_card_review.md` — New E2E test file to validate the "Crear Proveedor" button works on the Card Review page.

## Implementation Plan
### Phase 1: Foundation
Add the `createSupplierFromCard` method and associated state to the `useCardReview` hook. This includes tracking which card IDs are currently being processed (loading state) and storing supplier creation results.

### Phase 2: Core Implementation
Add the "Crear Proveedor" button to the CardReviewPage actions column. The button appears for cards with status `extracted` and no `supplier_id`. It shows a loading spinner while creating, and displays result feedback via snackbar. Also add a "Proveedor vinculado" chip for confirmed cards that already have a linked supplier.

### Phase 3: Integration
Create an E2E test to validate the full workflow: navigate to Card Review, verify the "Crear Proveedor" button appears for extracted cards, verify loading state, verify result feedback, and verify the card status updates after supplier creation. Run all validation commands to ensure zero regressions.

## Step by Step Tasks

### Step 1: Create E2E test file
- Read `.claude/commands/test_e2e.md` to understand the E2E test format
- Read `.claude/commands/e2e/test_basic_query.md` for the E2E test template
- Read `.claude/commands/e2e/test_auto_create_supplier_from_card.md` for supplier creation test patterns
- Read `.claude/commands/e2e/test_card_review_page.md` for Card Review page test patterns
- Create `.claude/commands/e2e/test_create_supplier_card_review.md` with these test steps:
  1. Navigate to `/card-review` and verify the page loads with the table
  2. Filter by "Extraídas" status to show only extracted cards
  3. Verify a "Crear Proveedor" button appears in the actions column for extracted cards without a linked supplier
  4. Verify that confirmed cards show a "Proveedor vinculado" chip instead of the button
  5. Click "Crear Proveedor" on an extracted card and verify the button shows loading state ("Creando..." with spinner)
  6. Verify a success snackbar appears with the supplier name after creation
  7. Verify the card status changes to "Confirmado" and the "Proveedor vinculado" chip appears
  8. Take screenshots at each step for validation

### Step 2: Add `createSupplierFromCard` method to useCardReview hook
- Open `apps/Client/src/hooks/kompass/useCardReview.ts`
- Add state for tracking creating supplier IDs: `creatingSupplierIds` as a `Set<string>`
- Add `createSupplierFromCard` method to the hook that:
  - Adds the captureId to `creatingSupplierIds` set
  - Calls `businessCardService.createSupplierFromCard(captureId)`
  - On success: updates the capture's status to `confirmed` and sets `supplier_id` in local state
  - On duplicate: updates the capture's status to `rejected` in local state
  - Removes the captureId from `creatingSupplierIds` in the `finally` block
  - Returns the `SupplierFromCardResult` for the page to handle snackbar messaging
- Add `createSupplierFromCard` and `creatingSupplierIds` to the `UseCardReviewReturn` interface and the hook's return object

### Step 3: Add "Crear Proveedor" button to CardReviewPage
- Open `apps/Client/src/pages/kompass/CardReviewPage.tsx`
- Import `PersonAddIcon` from `@mui/icons-material/PersonAdd` (used for the button icon, matching CardCapturePage pattern)
- Destructure `createSupplierFromCard` and `creatingSupplierIds` from `useCardReview()`
- Add a `handleCreateSupplier` async function (similar to `handleApprove`) that:
  - Calls `createSupplierFromCard(captureId)`
  - On success: shows snackbar with supplier name and email status (same messaging as `handleApprove`)
  - On duplicate: shows error snackbar with duplicate supplier name
  - On error: shows error snackbar
- In the actions column (`<TableCell>` at line ~570), add the "Crear Proveedor" button:
  - Visible when: `capture.status === 'extracted' && !capture.supplier_id`
  - Button text: "Crear Proveedor" (or "Creando..." when loading)
  - Icon: `PersonAddIcon` (or `CircularProgress` spinner when loading)
  - Color: `primary`, variant: `contained`, size: `small`
  - Disabled when: `creatingSupplierIds.has(capture.id)` or `isProcessing`
  - onClick: calls `handleCreateSupplier(capture.id)`
- Add a "Proveedor vinculado" chip for cards with `status === 'confirmed' && supplier_id`:
  - Uses `CheckCircleIcon` as the chip icon
  - Color: `primary`, size: `small`, variant: `outlined`
  - Label: "Proveedor vinculado"
- Keep the existing "Aprobar" button as-is (it provides batch-compatible approval workflow)
- Place "Crear Proveedor" button BEFORE the "Aprobar" button in the actions to give it visual priority as the primary action

### Step 4: Run validation commands
- Run `cd apps/Server && python -m pytest tests/ -v --tb=short` to validate no backend regressions
- Run `cd apps/Client && npx tsc --noEmit` to validate TypeScript compiles with no errors
- Run `cd apps/Client && npm run build` to validate the production build succeeds
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_create_supplier_card_review.md` to validate the feature works end-to-end

## Testing Strategy
### Unit Tests
No new unit tests are needed. The backend API endpoint and service logic are already tested. The frontend changes are UI-only (adding a button that calls an existing service method) and will be validated by the E2E test and TypeScript compilation.

### Edge Cases
- Card with status `extracted` but already has a `supplier_id` (shouldn't show button — handled by condition check)
- Duplicate supplier detection — button should show error snackbar and update status to `rejected`
- Card with status `confirmed` — should show "Proveedor vinculado" chip, not the button
- Card with status `pending`, `processing`, or `failed` — should not show "Crear Proveedor" button
- Multiple rapid clicks on "Crear Proveedor" — button is disabled while loading, preventing double submission
- Network error during supplier creation — should show error snackbar and not change card status
- Email send failure — should show warning snackbar (supplier created but email failed)
- No email address on card — should show warning snackbar (manual follow-up needed)

## Acceptance Criteria
- A "Crear Proveedor" button appears in the Card Review page actions column for cards with status `extracted` and no linked supplier
- Clicking "Crear Proveedor" shows a loading state (spinner + "Creando..." text)
- On successful supplier creation, a success snackbar shows the supplier name
- On successful creation, the card status updates to "Confirmado" in the table
- After creation, a "Proveedor vinculado" chip appears instead of the button
- Duplicate suppliers are detected and shown as error snackbar
- Email status (sent, failed, no email) is communicated via appropriate snackbar severity
- The button is disabled during processing to prevent double-clicks
- TypeScript compiles with zero errors
- Production build succeeds
- No regressions in existing tests

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/ -v --tb=short` — Run Server tests to validate the feature works with zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate the feature works with zero regressions
- `cd apps/Client && npm run build` — Run Client build to validate the feature works with zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_create_supplier_card_review.md` E2E test file to validate this functionality works

## Notes
- No backend changes are required. The `POST /api/extract/business-cards/{id}/create-supplier` endpoint already exists and handles supplier creation, duplicate detection, email sending, and status updates.
- The existing "Aprobar" button is kept alongside "Crear Proveedor" because "Aprobar" supports the batch workflow (batch approve selected cards). The "Crear Proveedor" button provides explicit, individual supplier creation UX.
- The `businessCardService.createSupplierFromCard()` method in `kompassService.ts` already exists (line ~1289) and is the same method used on the CardCapturePage.
- The pattern for loading states follows the CardCapturePage approach: tracking IDs in a `Set<string>` for per-row loading indicators.
