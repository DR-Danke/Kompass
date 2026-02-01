# Product Import Wizard

**ADW ID:** d5237c66
**Date:** 2026-02-01
**Specification:** specs/issue-23-adw-d5237c66-sdlc_planner-product-import-wizard.md

## Overview

A comprehensive multi-step wizard for AI-powered product catalog extraction from supplier documents. The wizard guides users through uploading PDF, Excel, or image files, monitoring AI extraction progress in real-time, reviewing and editing extracted product data with validation feedback, and confirming import to the product database with supplier selection and duplicate warnings.

## What Was Built

- **ImportWizardPage**: Main wizard component with 4-step Material-UI Stepper navigation
- **ExtractedProductTable**: Editable table component for reviewing extracted products with inline validation
- **useExtractionJob hook**: Custom hook for managing extraction job state and API polling
- **Extraction service methods**: Frontend API integration for upload, status polling, and import confirmation
- **TypeScript types**: Complete type definitions for extraction DTOs
- **E2E test specification**: Test commands for validating the import wizard workflow

## Technical Implementation

### Files Modified

- `apps/Client/src/App.tsx`: Added route `/import-wizard` for ImportWizardPage
- `apps/Client/src/components/layout/Sidebar.tsx`: Added "Import Wizard" navigation item with CloudUploadIcon
- `apps/Client/src/types/kompass.ts`: Added extraction-related TypeScript types (ExtractionJobStatus, ExtractedProduct, ExtractionJobDTO, UploadResponseDTO, ConfirmImportRequestDTO, ConfirmImportResponseDTO)
- `apps/Client/src/services/kompassService.ts`: Added extractionService with uploadFiles, getJobStatus, getJobResults, confirmImport methods

### New Files Created

- `apps/Client/src/pages/kompass/ImportWizardPage.tsx` (772 lines): Main wizard page with all 4 steps
- `apps/Client/src/components/kompass/ExtractedProductTable.tsx` (211 lines): Editable product review table
- `apps/Client/src/hooks/useExtractionJob.ts` (127 lines): Extraction job state management hook
- `.claude/commands/e2e/test_import_wizard.md`: E2E test specification

### Key Changes

- **4-Step Wizard Flow**: Upload > Processing > Review > Confirm, with Material-UI Stepper for visual progress
- **File Validation**: Client-side validation for allowed file types (.pdf, .xlsx, .xls, .png, .jpg, .jpeg) and max size (20MB)
- **Real-time Progress Polling**: useExtractionJob hook polls backend every 2 seconds during processing
- **Inline Product Editing**: ExtractedProductTable supports inline editing of SKU, name, description, price, MOQ with validation
- **Confidence Score Display**: Color-coded chips (green >80%, yellow >50%, red <50%) for extraction confidence
- **Draft Persistence**: localStorage-based draft saving to resume incomplete imports
- **Duplicate Detection**: Compares selected product SKUs against existing products before import

## How to Use

1. Navigate to "Import Wizard" from the sidebar (under Kompass section)
2. **Upload Step**: Drag and drop files or click to browse. Supported formats: PDF, Excel (.xlsx, .xls), Images (.png, .jpg, .jpeg). Max 20MB per file
3. **Processing Step**: Wait for AI extraction to complete. Progress bar shows percentage and file count
4. **Review Step**: Review extracted products in the editable table. Edit fields inline, toggle product selection via checkboxes. Fix any validation errors (red highlighted rows)
5. **Confirm Step**: Select a supplier from the dropdown. Review duplicate SKU warnings. Click "Import Products" to finalize

## Configuration

The wizard uses these backend API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/extract/upload` | POST | Upload files for extraction |
| `/api/extract/{job_id}` | GET | Get job status and progress |
| `/api/extract/{job_id}/results` | GET | Get extraction results |
| `/api/extract/{job_id}/confirm` | POST | Confirm import with selected products |

### Constants

```typescript
const ALLOWED_EXTENSIONS = ['.pdf', '.xlsx', '.xls', '.png', '.jpg', '.jpeg'];
const MAX_FILE_SIZE_MB = 20;
const POLL_INTERVAL_MS = 2000;
const DRAFT_STORAGE_KEY = 'kompass_import_wizard_draft';
```

## Testing

Run the E2E test specification:

```bash
# Execute the import wizard E2E test
claude -p "Read and execute .claude/commands/e2e/test_import_wizard.md"
```

Manual testing steps:
1. Upload a sample PDF or Excel file with product data
2. Verify processing shows progress percentage
3. Verify extracted products appear in review table
4. Edit a product field and verify validation
5. Select products and choose a supplier
6. Complete import and verify success dialog

## Notes

- The wizard uses polling (every 2 seconds) instead of WebSockets for backend compatibility
- Draft data persists in localStorage and is automatically cleared on successful import
- Confidence score thresholds (0.8 high, 0.5 medium) match backend extraction service behavior
- The ExtractedProductTable component is designed to be reusable for other table editing scenarios
- Duplicate SKU detection compares against all existing products (fetched on confirm step load)
- The import uses the bulk_create_products endpoint which handles partial failures gracefully
