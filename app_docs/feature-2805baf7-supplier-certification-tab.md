# Supplier Certification Tab

**ADW ID:** 2805baf7
**Date:** 2026-02-04
**Specification:** specs/issue-83-adw-2805baf7-sdlc_planner-supplier-certification-tab-ui.md

## Overview

This feature adds a comprehensive Certification tab to the Supplier dialog, enabling users to upload factory audit PDF documents, view AI-extracted summaries, see A/B/C supplier classifications with color-coded badges, and manually override classifications when needed. The feature eliminates the need to manually review 70+ page audit documents by displaying key metrics and findings in a visual, digestible format.

## What Was Built

- **AuditUploader** - Drag-and-drop PDF upload component with progress indicator and file validation
- **AuditSummaryCard** - Visual display of extracted audit data including supplier type, employee count, factory area, certifications, and positive/negative points
- **ClassificationBadge** - Color-coded A/B/C classification indicator with tooltip support
- **ClassificationOverrideDialog** - Modal for manual classification override with required notes
- **MarketsServedChart** - Horizontal bar chart showing market percentage distribution using recharts
- **SupplierCertificationTab** - Container component orchestrating all pieces with audit history table
- **Tabbed SupplierForm** - Converted supplier dialog from simple form to tabbed interface (General + Certification tabs)

## Technical Implementation

### Files Modified

- `apps/Client/src/components/kompass/SupplierForm.tsx`: Converted to tabbed dialog interface with General and Certification tabs; Certification tab only shown in edit mode

### Files Added

- `apps/Client/src/components/kompass/AuditUploader.tsx`: Drag-and-drop PDF upload with 25MB limit, progress tracking, and state management
- `apps/Client/src/components/kompass/AuditSummaryCard.tsx`: Card component displaying extracted audit data with skeleton loading states
- `apps/Client/src/components/kompass/ClassificationBadge.tsx`: Badge component with A (green), B (orange), C (red) color coding
- `apps/Client/src/components/kompass/ClassificationOverrideDialog.tsx`: Form dialog using react-hook-form for classification override
- `apps/Client/src/components/kompass/MarketsServedChart.tsx`: Horizontal bar chart using recharts ResponsiveContainer
- `apps/Client/src/components/kompass/SupplierCertificationTab.tsx`: Main container with audit list, history table, and state management
- `apps/Client/src/services/kompassService.ts`: Added `auditService` with upload, list, get, reprocess, classify, overrideClassification, and delete methods
- `apps/Client/src/types/kompass.ts`: Added TypeScript interfaces for audit DTOs (AuditType, SupplierType, ExtractionStatus, ClassificationGrade, MarketsServed, SupplierAuditResponse, etc.)

### Key Changes

- Upload uses XMLHttpRequest for progress tracking with `onProgress` callback
- Audit list fetched on tab mount with automatic state updates after upload/override
- Processing states (pending, processing, completed, failed) render different UI variants
- Classification badge shows "Manual" indicator when override is applied
- View PDF opens document in new browser tab via `window.open()`

## How to Use

1. Navigate to the Suppliers page
2. Click on an existing supplier to open the edit dialog
3. Click the "Certification" tab (only visible in edit mode)
4. Drag and drop a factory audit PDF (max 25MB) or click to browse
5. Wait for upload progress and extraction processing
6. View the audit summary showing supplier type, employee count, factory area, production lines, certifications, and market distribution
7. Review positive points and areas of concern extracted from the audit
8. View the A/B/C classification badge with AI reasoning tooltip
9. Click "Override" to manually change the classification (requires notes)
10. Use "View Full PDF" to open the original document
11. Use "Reprocess" if extraction failed or needs re-extraction
12. View audit history in the table below the latest audit

## Configuration

No additional configuration required. The feature uses existing backend API endpoints from Issue #82:
- `POST /api/suppliers/{id}/audits` - Upload audit
- `GET /api/suppliers/{id}/audits` - List audits
- `POST /api/suppliers/{id}/audits/{auditId}/reprocess` - Reprocess extraction
- `POST /api/suppliers/{id}/audits/{auditId}/classify` - Run classification
- `PUT /api/suppliers/{id}/audits/{auditId}/override` - Override classification

## Testing

Run the E2E test suite for the certification tab:
```bash
# Follow instructions in .claude/commands/e2e/test_supplier_certification_tab.md
```

Key test scenarios:
- Upload valid/invalid PDF files
- Verify file size limit (25MB)
- Check extraction status transitions
- Test classification override with notes validation
- Verify audit history table updates
- Test View PDF and Reprocess buttons

## Notes

- The Certification tab only appears when editing an existing supplier (not in create mode)
- File upload currently uses temporary file:// URLs in development; production uses cloud storage
- Extraction may take 30-60 seconds for large audits; UI shows processing indicator
- Classification override requires admin/manager role on the backend
- The recharts library is used for the markets served chart (already a project dependency)
