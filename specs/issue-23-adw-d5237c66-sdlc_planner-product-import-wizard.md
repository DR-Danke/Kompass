# Feature: Product Import Wizard

## Metadata
issue_number: `23`
adw_id: `d5237c66`
issue_json: `{"number":23,"title":"[Kompass] Phase 9C: Product Import Wizard","body":"..."}`

## Feature Description
Create a comprehensive multi-step import wizard for AI-powered product catalog extraction from supplier documents. The wizard guides users through uploading PDF, Excel, or image files, monitoring AI extraction progress in real-time, reviewing and editing extracted product data with validation feedback, and confirming import to the product database with supplier selection and duplicate warnings.

This feature integrates with the existing ExtractionService backend (Phase 2D) and extraction API routes (Phase 3D) to provide a complete end-to-end import workflow for populating the Kompass product catalog (Biblia General) from supplier catalogs.

## User Story
As a **Kompass user (admin, manager, or user role)**
I want to **upload supplier catalogs and extract product data using AI**
So that **I can quickly populate my product database without manual data entry**

## Problem Statement
Currently, users must manually enter product data into the Kompass system, which is time-consuming and error-prone. The AI data extraction service exists on the backend but has no frontend interface to leverage its capabilities. Users need a guided workflow to:
- Upload various file formats (PDF, Excel, images)
- Monitor extraction progress
- Review and correct AI-extracted data before import
- Select which products to import with validation

## Solution Statement
Build a multi-step wizard component (ImportWizardPage) with four distinct steps:
1. **Upload Step**: Drag-and-drop file upload with preview
2. **Processing Step**: Real-time progress tracking via polling
3. **Review Step**: Editable table with inline validation (ExtractedProductTable component)
4. **Confirm Step**: Supplier selection, duplicate detection, and final import

The wizard will use Material-UI's Stepper component for navigation, react-hook-form for form state management, and integrate with the existing extraction API endpoints.

## Relevant Files
Use these files to implement the feature:

**Backend (Already Exists - Read Only):**
- `apps/Server/app/api/extraction_routes.py` - Extraction API endpoints (POST /upload, GET /{job_id}, GET /{job_id}/results, POST /{job_id}/confirm)
- `apps/Server/app/models/extraction_dto.py` - ExtractedProduct, ExtractionResult DTOs
- `apps/Server/app/models/extraction_job_dto.py` - ExtractionJobDTO, ExtractionJobStatus, ConfirmImportRequestDTO
- `apps/Server/app/services/extraction_service.py` - AI extraction service (PDF, Excel, images)

**Frontend (To Modify/Create):**
- `apps/Client/src/App.tsx` - Add route for /import-wizard
- `apps/Client/src/components/layout/Sidebar.tsx` - Add navigation item for Import Wizard
- `apps/Client/src/types/kompass.ts` - Add extraction-related TypeScript types
- `apps/Client/src/services/kompassService.ts` - Add extractionService API methods

**Documentation:**
- `app_docs/feature-dc759ae8-ai-data-extraction-service.md` - Backend extraction service details
- `app_docs/feature-1ee9c0ae-data-extraction-api-routes.md` - API routes documentation
- `app_docs/feature-af7568d5-frontend-types-api-service.md` - Frontend types and services patterns

**E2E Testing (Read for patterns):**
- `.claude/commands/test_e2e.md` - E2E test runner instructions

### New Files
- `apps/Client/src/pages/kompass/ImportWizardPage.tsx` - Main wizard page component with step navigation
- `apps/Client/src/components/kompass/ExtractedProductTable.tsx` - Editable table for reviewing extracted products
- `apps/Client/src/hooks/useExtractionJob.ts` - Custom hook for job polling and state management
- `.claude/commands/e2e/test_import_wizard.md` - E2E test specification for import wizard

## Implementation Plan
### Phase 1: Foundation
1. Add TypeScript types for extraction APIs to `apps/Client/src/types/kompass.ts`
2. Add extraction service methods to `apps/Client/src/services/kompassService.ts`
3. Create the `useExtractionJob` custom hook for managing job state and polling

### Phase 2: Core Implementation
1. Build the ImportWizardPage component with Material-UI Stepper
2. Implement Step 1 (Upload): File drop zone, file list preview, validation
3. Implement Step 2 (Processing): Progress bar, status display, real-time polling
4. Build ExtractedProductTable component with editable cells
5. Implement Step 3 (Review): Display table, inline validation, product selection
6. Implement Step 4 (Confirm): Supplier dropdown, summary, import action

### Phase 3: Integration
1. Add route to App.tsx for /import-wizard
2. Add navigation item to Sidebar with upload icon
3. Wire up form submission and confirmation flow
4. Add cancel/save draft functionality
5. Create E2E test specification

## Step by Step Tasks

### Step 1: Add Extraction TypeScript Types
- Add `ExtractionJobStatus` enum to types/kompass.ts
- Add `ExtractedProduct` interface matching backend DTO
- Add `ExtractionJobDTO` interface for job state
- Add `UploadResponseDTO` interface
- Add `ConfirmImportRequestDTO` and `ConfirmImportResponseDTO` interfaces

### Step 2: Add Extraction Service Methods
- Add `extractionService` object to kompassService.ts
- Implement `uploadFiles(files: FileList): Promise<UploadResponseDTO>` using FormData
- Implement `getJobStatus(jobId: string): Promise<ExtractionJobDTO>`
- Implement `getJobResults(jobId: string): Promise<ExtractionJobDTO>`
- Implement `confirmImport(request: ConfirmImportRequestDTO): Promise<ConfirmImportResponseDTO>`

### Step 3: Create useExtractionJob Hook
- Create new file `apps/Client/src/hooks/useExtractionJob.ts`
- Implement state: jobId, status, progress, extractedProducts, errors
- Implement `startJob(files: FileList)` function
- Implement polling logic with setInterval for job status (poll every 2 seconds)
- Implement cleanup on unmount
- Return: jobId, status, progress, products, errors, isProcessing, startJob, resetJob

### Step 4: Create ImportWizardPage Component - Structure
- Create new file `apps/Client/src/pages/kompass/ImportWizardPage.tsx`
- Set up React component with Material-UI imports
- Add state for activeStep (0-3)
- Add Stepper component with 4 steps: Upload, Processing, Review, Confirm
- Implement step navigation (handleNext, handleBack)
- Add cancel confirmation dialog

### Step 5: Implement Upload Step (Step 0)
- Create file drop zone using Box with drag-and-drop handlers
- Use `onDragOver`, `onDragLeave`, `onDrop` events
- Display visual feedback for drag state
- Support file input with hidden input element and label trigger
- Show file list preview with file name, size, type
- Add remove file button for each file
- Validate file types (.pdf, .xlsx, .xls, .png, .jpg, .jpeg)
- Validate file size (max 20MB)
- Display validation errors inline
- Enable Next button only when valid files are present

### Step 6: Implement Processing Step (Step 1)
- Display LinearProgress with progress percentage
- Show status text (pending, processing, completed, failed)
- Display processed files count: "Processing file X of Y"
- Use useExtractionJob hook for polling
- Auto-advance to Review step when completed
- Show error message if extraction fails with retry option

### Step 7: Create ExtractedProductTable Component
- Create new file `apps/Client/src/components/kompass/ExtractedProductTable.tsx`
- Accept props: products, onProductChange, onProductSelect, validationErrors
- Use MUI Table with sticky header
- Columns: Checkbox, SKU, Name, Description, Price, MOQ, Confidence, Actions
- Make SKU, Name, Description, Price, MOQ editable with inline TextField
- Show confidence score with color-coded chip (green >0.8, yellow >0.5, red <0.5)
- Highlight rows with validation errors (red border)
- Show validation error tooltips on affected cells
- Implement row checkbox for selection
- Add image preview column with thumbnail if image_urls present
- Support select all checkbox in header

### Step 8: Implement Review Step (Step 2)
- Display ExtractedProductTable with extracted products
- Track selected products in local state
- Validate products before enabling Next:
  - Name is required
  - Price must be >= 0 if present
  - MOQ must be >= 1 if present
- Show validation error count summary
- Allow editing inline to fix validation errors
- Enable Next only when at least one valid product is selected

### Step 9: Implement Confirm Step (Step 3)
- Display summary card: "X products selected for import"
- Add Supplier selection dropdown using supplierService.list()
- Fetch and display existing products to check for duplicates (by SKU)
- Show duplicate warnings with yellow alert
- Display list of products to import with key fields
- Add Import button with loading state
- Handle import via confirmImport API
- Show success/error result dialog

### Step 10: Add Save Draft and Cancel Functionality
- Implement save draft using localStorage
- Store: files metadata, extracted products, selected indices, supplier
- Add "Save Draft" button in wizard header
- Add "Load Draft" option if draft exists on page load
- Implement cancel with confirmation dialog
- Clear draft on successful import

### Step 11: Add Route and Navigation
- Add import to App.tsx: `import ImportWizardPage from './pages/kompass/ImportWizardPage'`
- Add Route: `<Route path="import-wizard" element={<ImportWizardPage />} />`
- Add nav item to Sidebar.tsx with CloudUploadIcon at appropriate position (after Products)
- Set path to '/import-wizard' and title to 'Import Wizard'

### Step 12: Create E2E Test Specification
- Create new file `.claude/commands/e2e/test_import_wizard.md`
- Define test scenarios:
  1. Navigate to Import Wizard page
  2. Upload a test file (mock or real PDF)
  3. Verify processing step shows progress
  4. Verify review step shows extracted products
  5. Select products and verify selection
  6. Choose supplier and confirm import
  7. Verify success message
- Include screenshot capture points
- Define success criteria

### Step 13: Run Validation Commands
- Run TypeScript type check
- Run ESLint
- Run Client build
- Read and execute E2E test if applicable

## Testing Strategy
### Unit Tests
- Test useExtractionJob hook with mocked API responses
- Test ExtractedProductTable renders correctly with various product data
- Test inline validation logic for required fields
- Test file type and size validation in Upload step

### Edge Cases
- Empty file list handling
- All products have validation errors
- Extraction job fails mid-processing
- Network error during polling
- Large number of products (100+) performance
- Duplicate SKU detection with existing products
- File upload cancelled before completion
- Draft restore with changed supplier list

## Acceptance Criteria
- [ ] File upload working with drag-and-drop and click-to-browse
- [ ] File type validation (.pdf, .xlsx, .xls, .png, .jpg, .jpeg only)
- [ ] File size validation (max 20MB per file)
- [ ] Processing progress displayed with percentage and file count
- [ ] Real-time status updates via polling
- [ ] Review table displays all extracted products
- [ ] Inline editing for SKU, Name, Description, Price, MOQ
- [ ] Validation errors shown inline with red highlighting
- [ ] Confidence score indicator (color-coded chip)
- [ ] Product selection via checkboxes
- [ ] Select all functionality
- [ ] Supplier selection required before import
- [ ] Duplicate SKU warnings displayed
- [ ] Import completing successfully with success message
- [ ] Cancel with confirmation dialog
- [ ] Back/Next navigation working correctly
- [ ] Stepper shows current step visually

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Run TypeScript type check
cd apps/Client && npm run typecheck

# Run ESLint
cd apps/Client && npm run lint

# Run Client build
cd apps/Client && npm run build

# Run Server tests to ensure backend still works
cd apps/Server && source .venv/bin/activate && python -m pytest tests/test_extraction_routes.py -v --tb=short

# Run Server ruff check
cd apps/Server && source .venv/bin/activate && ruff check .
```

After implementation, read `.claude/commands/test_e2e.md` and execute `.claude/commands/e2e/test_import_wizard.md` to validate the end-to-end functionality.

## Notes
- The wizard uses polling (every 2 seconds) instead of WebSockets for simplicity and compatibility with the existing backend architecture
- Draft saving uses localStorage which is cleared on successful import
- The ExtractedProductTable component is designed to be reusable for other table editing scenarios
- Confidence score thresholds (0.8 high, 0.5 medium) match backend extraction service behavior
- File validation on frontend matches backend limits (20MB max, same extensions)
- The wizard does not persist state to backend - only localStorage drafts for user convenience
- Duplicate detection compares SKUs with existing products fetched via productService
- The import uses bulk_create_products which handles partial failures gracefully
