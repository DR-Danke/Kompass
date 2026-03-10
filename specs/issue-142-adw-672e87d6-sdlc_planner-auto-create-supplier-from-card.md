# Feature: Auto-Create Supplier from Extracted Business Card Data

## Metadata
issue_number: `142`
adw_id: `672e87d6`
issue_json: ``

## Feature Description
Implement auto-creation of supplier records from AI-extracted business card data, with duplicate detection by email/phone. When a business card has been captured and its data extracted via AI (TF-002), this feature enables creating a supplier record with all available fields populated, pipeline status "contacted", trade fair metadata (source, fair_name, capture_date), and linking the capture to the new supplier. Duplicate detection prevents accidental creation of duplicate suppliers by checking existing email and phone matches.

## User Story
As a Kompass sourcing agent at a trade fair
I want to automatically create a supplier from an extracted business card
So that I can quickly build my supplier database without manual data entry and avoid duplicate records

## Problem Statement
After AI extraction of business card data (TF-002), users must manually create supplier records by copy-pasting extracted fields. This is slow and error-prone, especially at busy trade fairs. There is also no mechanism to detect if a supplier already exists in the system, risking duplicate entries.

## Solution Statement
Add a "Create Supplier" action to extracted business cards that:
1. Maps extracted fields to supplier record fields automatically
2. Checks for duplicate suppliers by email (case-insensitive) and phone before creation
3. If a duplicate is found, flags the capture and returns the existing supplier info
4. If no duplicate, creates the supplier with trade fair metadata and links it to the capture
5. Updates the capture status to `confirmed` upon successful creation

## Relevant Files
Use these files to implement the feature:

**Backend — Core Implementation:**
- `apps/Server/app/services/supplier_service.py` — Add `create_supplier_from_card()` method. Contains existing `create_supplier()`, `_validate_email()`, and `_normalize_wechat_id()` patterns to follow.
- `apps/Server/app/services/business_card_service.py` — Contains `get_capture()` and `update_capture()` methods used to retrieve and update capture records.
- `apps/Server/app/repository/kompass_repository.py` — Add `find_duplicate_supplier()` and `create_with_trade_fair_metadata()` methods to `SupplierRepository`. Note: existing `create()` (line 1267) does NOT include trade fair fields (`source`, `fair_name`, `capture_date`, `wechat_id`). The `_row_to_dict()` (line 1615) returns 14 basic fields; `_row_to_dict_extended()` (line 2066) returns 18 fields with certification data.
- `apps/Server/app/repository/business_card_repository.py` — Has `get_by_id()`, `update()`, and `_row_to_dict()` methods. The `update()` method accepts a dict of field names to values, including `supplier_id` and `status`.
- `apps/Server/app/models/kompass_dto.py` — Add `SupplierFromCardResultDTO`. Contains existing `SupplierCreateDTO` (line 373), `SupplierResponseDTO` (line 411), `BusinessCardCaptureResponseDTO`, and enum definitions.
- `apps/Server/app/api/extraction_routes.py` — Add `POST /business-cards/{id}/create-supplier` endpoint. Contains existing business card endpoints using `require_roles()` auth pattern.
- `apps/Server/app/api/supplier_routes.py` — Add `source` query parameter to `list_suppliers()` endpoint (line 38). Currently supports `status`, `country`, `has_products`, `certification_status`, `pipeline_status`, `search` filters.

**Frontend — UI Integration:**
- `apps/Client/src/pages/kompass/CardCapturePage.tsx` — Add "Crear Proveedor" button for extracted cards, duplicate warning display, and success confirmation. Currently 428 lines with upload, extract, and display functionality.
- `apps/Client/src/services/kompassService.ts` — Add `createSupplierFromCard()` method to `businessCardService`. Contains existing `uploadCard()`, `listCaptures()`, `getCapture()`, `triggerExtraction()` methods.
- `apps/Client/src/types/kompass.ts` — Add `SupplierFromCardResult` interface. Contains existing `BusinessCardCapture` (line 1048) and `SupplierResponse` (line 260) types.

**Database Schema Reference:**
- `apps/Server/database/schema.sql` — Suppliers table (line 111) has trade fair columns: `source VARCHAR(50)`, `fair_name VARCHAR(255)`, `capture_date TIMESTAMP WITH TIME ZONE`, `outreach_status VARCHAR(20)`, `wechat_id VARCHAR(100)`. Business card captures table (line 209) has `supplier_id UUID REFERENCES suppliers(id)` and `status` CHECK constraint including `confirmed`.

**Testing:**
- `apps/Server/tests/services/test_supplier_service.py` — Add tests for `create_supplier_from_card()` method.
- `apps/Server/tests/test_extraction_routes.py` — Add tests for the new endpoint.

**E2E Test Reference:**
- Read `.claude/commands/test_e2e.md` to understand E2E test execution pattern
- Read `.claude/commands/e2e/test_basic_query.md` to understand E2E test file format
- Read `.claude/commands/e2e/test_business_card_extraction.md` — Existing extraction test for pattern reference

### New Files
- `.claude/commands/e2e/test_auto_create_supplier_from_card.md` — E2E test spec for auto-create supplier from card feature

## Implementation Plan
### Phase 1: Foundation
1. Add `SupplierFromCardResultDTO` to DTOs
2. Add `find_duplicate_supplier()` method to `SupplierRepository`
3. Add `create_with_trade_fair_metadata()` method to `SupplierRepository` (extends existing `create()` with `source`, `fair_name`, `capture_date`, `wechat_id` fields)

### Phase 2: Core Implementation
1. Add `create_supplier_from_card()` method to `SupplierService` that orchestrates: capture retrieval, duplicate detection, supplier creation with trade fair metadata, capture linking, and status update
2. Add `POST /business-cards/{id}/create-supplier` API endpoint
3. Add `source` filter parameter to `list_suppliers()` route and `get_all_with_filters()` repository method

### Phase 3: Integration
1. Add `SupplierFromCardResult` TypeScript interface
2. Add `createSupplierFromCard()` to frontend `businessCardService`
3. Add "Crear Proveedor" button to `CardCapturePage.tsx` for extracted cards
4. Add duplicate warning and success confirmation UI
5. Create E2E test spec and validate

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add SupplierFromCardResultDTO to Backend DTOs
- Open `apps/Server/app/models/kompass_dto.py`
- Add `SupplierFromCardResultDTO` class near the other supplier DTOs (after `SupplierPipelineStatusUpdateDTO` around line 448):
  ```python
  class SupplierFromCardResultDTO(BaseModel):
      """Result of creating a supplier from a business card capture."""
      success: bool
      supplier_id: Optional[UUID] = None
      supplier_name: Optional[str] = None
      is_duplicate: bool = False
      duplicate_supplier_id: Optional[UUID] = None
      duplicate_supplier_name: Optional[str] = None
      message: str
  ```

### Step 2: Add Duplicate Detection to Supplier Repository
- Open `apps/Server/app/repository/kompass_repository.py`
- Add method `find_duplicate_supplier(email: Optional[str], phone: Optional[str]) -> Optional[Dict[str, Any]]` to `SupplierRepository` class:
  - Query: `SELECT ... FROM suppliers WHERE LOWER(contact_email) = LOWER(%s) OR contact_phone = %s LIMIT 1`
  - Only include conditions for non-None/non-empty parameters
  - If both email and phone are None/empty, return None immediately
  - Use the existing `_row_to_dict_extended()` for the returned row (SELECT 18 fields to match)
  - Follow existing error handling pattern with try/except, logging, and `close_database_connection(conn)` in finally

### Step 3: Add Trade Fair Metadata Supplier Creation to Repository
- Open `apps/Server/app/repository/kompass_repository.py`
- Add method `create_with_trade_fair_metadata()` to `SupplierRepository` class that extends the existing `create()` method:
  - Parameters: same as `create()` plus `source: Optional[str] = None`, `fair_name: Optional[str] = None`, `capture_date: Optional[datetime] = None`, `wechat_id: Optional[str] = None`
  - INSERT should include `source`, `fair_name`, `capture_date`, `wechat_id` columns
  - RETURNING should include all 18 extended fields (matching `_row_to_dict_extended()` format): `id, name, code, status, contact_name, contact_email, contact_phone, address, city, country, website, notes, certification_status, pipeline_status, latest_audit_id, certified_at, created_at, updated_at`
  - Use `_row_to_dict_extended()` for the returned row
  - Follow existing `create()` error handling pattern

### Step 4: Add Source Filter to Repository's get_all_with_filters
- Open `apps/Server/app/repository/kompass_repository.py`
- In `get_all_with_filters()` method (line 1689), add `source: Optional[str] = None` parameter
- Add condition: `if source: conditions.append("s.source = %s"); params.append(source)`
- Place it after the existing `pipeline_status` filter block

### Step 5: Add Source Filter to Supplier Service
- Open `apps/Server/app/services/supplier_service.py`
- Add `source: Optional[str] = None` parameter to `list_suppliers()` method (line 155)
- Pass `source=source` to `supplier_repository.get_all_with_filters()` call

### Step 6: Add Source Filter to Supplier Routes
- Open `apps/Server/app/api/supplier_routes.py`
- Add `source: Optional[str] = Query(None, description="Filter by source (e.g., trade_fair)")` parameter to `list_suppliers()` route (line 38)
- Pass `source=source` to `supplier_service.list_suppliers()` call

### Step 7: Implement create_supplier_from_card in Supplier Service
- Open `apps/Server/app/services/supplier_service.py`
- Add imports: `from app.services.business_card_service import business_card_service` and `from app.models.kompass_dto import SupplierFromCardResultDTO`
- Add method `create_supplier_from_card(self, capture_id: UUID) -> SupplierFromCardResultDTO`:
  1. Retrieve capture via `business_card_service.get_capture(capture_id)` — raises ValueError if not found
  2. Validate capture status is `extracted` — raise ValueError if not
  3. Extract fields: `company_name`, `contact_name`, `contact_email`, `contact_phone`, `contact_wechat`, `address`, `website`, `fair_name` from capture dict
  4. Determine supplier name: use `company_name` if available, otherwise `contact_name`, otherwise raise ValueError("No company or contact name extracted")
  5. Call `supplier_repository.find_duplicate_supplier(email=contact_email, phone=contact_phone)`
  6. If duplicate found:
     - Update capture status to `duplicate_detected` via `business_card_service.update_capture(capture_id, {"status": "rejected"})` (using `rejected` since `duplicate_detected` is not in the CHECK constraint)
     - Return `SupplierFromCardResultDTO(success=False, is_duplicate=True, duplicate_supplier_id=dup["id"], duplicate_supplier_name=dup["name"], message="Proveedor duplicado detectado")`
  7. If no duplicate:
     - Validate email if present using `self._validate_email()`
     - Normalize phone using `self._normalize_wechat_id()`
     - Call `supplier_repository.create_with_trade_fair_metadata(name=supplier_name, contact_name=contact_name, contact_email=contact_email, contact_phone=normalized_phone, address=address, country="China", website=website, pipeline_status="contacted", source="trade_fair", fair_name=fair_name, capture_date=capture["created_at"], wechat_id=contact_wechat)`
     - If creation fails, raise ValueError
     - Link capture to supplier: `business_card_service.update_capture(capture_id, {"supplier_id": str(result["id"]), "status": "confirmed"})`
     - Return `SupplierFromCardResultDTO(success=True, supplier_id=result["id"], supplier_name=result["name"], message="Proveedor creado exitosamente")`

### Step 8: Add API Endpoint for Create Supplier from Card
- Open `apps/Server/app/api/extraction_routes.py`
- Add import for `SupplierFromCardResultDTO` from `app.models.kompass_dto`
- Add import for `supplier_service` from `app.services.supplier_service`
- Add endpoint after the existing `extract_business_card` endpoint (after line 462):
  ```python
  @router.post(
      "/business-cards/{capture_id}/create-supplier",
      response_model=SupplierFromCardResultDTO,
  )
  async def create_supplier_from_card(
      capture_id: UUID,
      current_user: Dict[str, Any] = Depends(
          require_roles(["admin", "manager", "user"])
      ),
  ) -> SupplierFromCardResultDTO:
  ```
  - Log request info
  - Call `supplier_service.create_supplier_from_card(capture_id)`
  - Handle ValueError (404 for "not found", 400 for other validation errors)
  - Handle generic Exception as 500

### Step 9: Add Frontend TypeScript Interface
- Open `apps/Client/src/types/kompass.ts`
- Add `SupplierFromCardResult` interface after the `BusinessCardCapture` interface (around line 1070):
  ```typescript
  export interface SupplierFromCardResult {
    success: boolean;
    supplier_id?: string;
    supplier_name?: string;
    is_duplicate: boolean;
    duplicate_supplier_id?: string;
    duplicate_supplier_name?: string;
    message: string;
  }
  ```

### Step 10: Add Frontend Service Method
- Open `apps/Client/src/services/kompassService.ts`
- Add `createSupplierFromCard` method to the `businessCardService` object:
  ```typescript
  async createSupplierFromCard(captureId: string): Promise<SupplierFromCardResult> {
    console.log(`INFO [businessCardService]: Creating supplier from card ${captureId}`);
    const response = await apiClient.post<SupplierFromCardResult>(
      `/extract/business-cards/${captureId}/create-supplier`
    );
    return response.data;
  },
  ```
- Add import for `SupplierFromCardResult` type in the import block from `@/types/kompass`

### Step 11: Add Create Supplier UI to CardCapturePage
- Open `apps/Client/src/pages/kompass/CardCapturePage.tsx`
- Add imports: `PersonAddIcon` from `@mui/icons-material/PersonAdd`, `CheckCircleIcon` from `@mui/icons-material/CheckCircle`, `WarningIcon` from `@mui/icons-material/Warning`, `LinkIcon` from `@mui/icons-material/Link`
- Add import for `SupplierFromCardResult` type
- Add state: `const [creatingSupplierIds, setCreatingSupplierIds] = useState<Set<string>>(new Set());`
- Add state: `const [supplierResults, setSupplierResults] = useState<Record<string, SupplierFromCardResult>>({});`
- Add handler `handleCreateSupplier(captureId: string)`:
  1. Add captureId to `creatingSupplierIds` set
  2. Call `businessCardService.createSupplierFromCard(captureId)`
  3. Store result in `supplierResults`
  4. If `result.success`, update the capture in local state: set status to `confirmed` and supplier_id to result.supplier_id
  5. Show success/duplicate snackbar message
  6. On error, show error snackbar
  7. Remove captureId from `creatingSupplierIds` in finally
- In the capture card rendering, add after the existing action buttons `Box` (around line 372):
  - Show "Crear Proveedor" button when `capture.status === 'extracted' && !capture.supplier_id`:
    - Button with `PersonAddIcon` startIcon, size="small", variant="contained", color="primary"
    - Disabled when `creatingSupplierIds.has(capture.id)`, show CircularProgress when creating
    - Text: "Crear Proveedor" (or "Creando..." when in progress)
  - Show duplicate warning when `supplierResults[capture.id]?.is_duplicate`:
    - Alert with severity="warning" and text including duplicate supplier name
    - Link to existing supplier page: `/suppliers` (or show supplier name)
  - Show success confirmation when `supplierResults[capture.id]?.success`:
    - Alert with severity="success" and text "Proveedor creado: {name}"
  - Show "Proveedor vinculado" chip when `capture.status === 'confirmed' && capture.supplier_id`:
    - Chip with CheckCircleIcon, color="primary", label "Proveedor vinculado"

### Step 12: Create E2E Test Spec
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` for pattern reference
- Create `.claude/commands/e2e/test_auto_create_supplier_from_card.md` with test steps:
  1. Navigate to Card Capture page, verify page loads
  2. Upload a test business card image with fair name "Canton Fair 2026"
  3. Verify the card appears and extraction completes (or is in `extracted` status)
  4. Verify "Crear Proveedor" button is visible on extracted card
  5. Click "Crear Proveedor" button
  6. Verify success message appears (or duplicate warning if supplier already exists)
  7. Verify capture status updates to "Confirmado" (confirmed)
  8. Verify "Proveedor vinculado" indicator appears
  9. Upload same card again, extract, attempt to create supplier again
  10. Verify duplicate detection warning appears
  11. Take screenshots at each step
  - Success criteria checklist covering all scenarios
  - All UI text in Spanish

### Step 13: Add Backend Unit Tests
- Open `apps/Server/tests/services/test_supplier_service.py`
- Add test cases for `create_supplier_from_card()`:
  - Test successful supplier creation from extracted card
  - Test duplicate detection by email
  - Test duplicate detection by phone
  - Test rejection when capture status is not `extracted`
  - Test rejection when capture has no company_name or contact_name
  - Test capture is linked to created supplier (supplier_id updated)
  - Test capture status updated to `confirmed` on success
  - Mock `business_card_service.get_capture()` and `supplier_repository` methods

### Step 14: Run Validation Commands
- Run all validation commands to ensure zero regressions:
  - `cd apps/Server && python -m pytest tests/ -v --tb=short`
  - `cd apps/Client && npx tsc --noEmit`
  - `cd apps/Client && npm run build`
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_auto_create_supplier_from_card.md` E2E test

## Testing Strategy
### Unit Tests
- **SupplierService.create_supplier_from_card()**: Mock `business_card_service.get_capture()` returning extracted capture dict, mock `supplier_repository.find_duplicate_supplier()` returning None, mock `supplier_repository.create_with_trade_fair_metadata()` returning supplier dict, verify result is `SupplierFromCardResultDTO(success=True, ...)`
- **Duplicate detection path**: Mock `find_duplicate_supplier()` returning existing supplier dict, verify result is `SupplierFromCardResultDTO(success=False, is_duplicate=True, ...)`
- **Status validation**: Mock capture with status `pending`, verify ValueError raised
- **API endpoint tests**: Mock supplier_service, test 201 success, 400 validation error, 404 not found

### Edge Cases
- Card with only `contact_name` (no `company_name`) — should use contact_name as supplier name
- Card with neither `company_name` nor `contact_name` — should return error
- Card with no email and no phone — should skip duplicate check and create directly
- Card with email that doesn't match regex — should create but without email (or validate and reject)
- Card already linked to a supplier (`supplier_id` is not null) — should reject to prevent double-creation
- Card in `confirmed` status — should reject since already processed
- Concurrent creation requests for same card — the second should detect the supplier_id was set

## Acceptance Criteria
- `POST /api/extract/business-cards/{id}/create-supplier` endpoint works and returns `SupplierFromCardResultDTO`
- Supplier is created with correct field mapping from extracted card data
- Trade fair metadata (`source="trade_fair"`, `fair_name`, `capture_date`, `wechat_id`) is stored on the supplier
- `pipeline_status` is set to `"contacted"` for new trade fair suppliers
- Duplicate detection by email (case-insensitive) prevents creation and returns existing supplier info
- Duplicate detection by phone prevents creation and returns existing supplier info
- Capture `supplier_id` is linked to the new supplier after creation
- Capture status is updated to `confirmed` after successful supplier creation
- "Crear Proveedor" button appears only for extracted cards without a linked supplier
- Duplicate warning shows with existing supplier info when duplicate detected
- Success confirmation shows with new supplier name
- `GET /api/suppliers?source=trade_fair` filter works to list only trade fair suppliers
- All UI text is in Spanish (Colombian)
- All existing tests pass with zero regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/ -v --tb=short` — Run Server tests to validate the feature works with zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate the feature works with zero regressions
- `cd apps/Client && npm run build` — Run Client build to validate the feature works with zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_auto_create_supplier_from_card.md` E2E test to validate this functionality works

## Notes
- The `suppliers` table already has trade fair columns (`source`, `fair_name`, `capture_date`, `outreach_status`, `wechat_id`) — no schema migration needed
- The `business_card_captures.status` CHECK constraint includes `confirmed` — no schema change needed
- The existing `SupplierRepository.create()` method does NOT include trade fair fields in its INSERT/RETURNING — a new `create_with_trade_fair_metadata()` method is needed rather than modifying the existing one, to avoid breaking existing supplier creation flows
- The `_row_to_dict()` (14 fields) vs `_row_to_dict_extended()` (18 fields) distinction matters — the new method should use `_row_to_dict_extended()` since `SupplierResponseDTO` includes `certification_status`, `pipeline_status`, `latest_audit_id`, and `certified_at`
- This feature runs IN PARALLEL with TF-004 (Email Service) in a separate worktree — no merge conflicts expected since they touch different files
- The `duplicate_detected` status is NOT in the `business_card_captures.status` CHECK constraint (`pending`, `processing`, `extracted`, `confirmed`, `rejected`, `failed`). Use `rejected` status instead and include the reason in the API response
- The `suppliers.source` column has no CHECK constraint so `trade_fair` can be stored as a free text value
