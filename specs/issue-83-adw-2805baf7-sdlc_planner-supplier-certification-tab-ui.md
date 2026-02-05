# Feature: Supplier Certification Tab with Audit Management UI

## Metadata
issue_number: `83`
adw_id: `2805baf7`
issue_json: `{"number":83,"title":"feat: Add supplier certification tab with audit management UI","body":"..."}`

## Feature Description
This feature creates the frontend UI components for the Supplier Certification tab, enabling users to manage factory audits through a visual interface. The system allows users to upload PDF audit documents via drag-and-drop, view AI-extracted data summaries, see A/B/C supplier classifications with color-coded badges, and override classifications when needed. The certification tab integrates into the existing SupplierForm dialog as a new tab, providing a comprehensive view of factory audit information without needing to read 70+ page PDF documents.

## User Story
As a sourcing manager
I want to upload factory audits and view extracted summaries with AI-generated classifications
So that I can make faster supplier qualification decisions without manually reviewing lengthy PDF documents

## Problem Statement
Factory audits are 70+ page PDF documents (~21MB) that require significant manual review time. There is no centralized way to quickly view key supplier certification data or track audit classification status. Users need a visual interface to upload audits, see extracted summaries, and manage supplier classifications efficiently.

## Solution Statement
Create a suite of React components that integrate into the SupplierForm as a "Certification" tab. The solution includes:
1. **AuditUploader** - Drag-and-drop PDF upload with progress indicator
2. **AuditSummaryCard** - Visual display of extracted audit data
3. **ClassificationBadge** - Color-coded A/B/C classification indicator
4. **ClassificationOverrideDialog** - Modal for manual classification override
5. **MarketsServedChart** - Horizontal bar chart of market percentages
6. **SupplierCertificationTab** - Container component integrating all pieces

## Relevant Files
Use these files to implement the feature:

**Existing Components to Modify:**
- `apps/Client/src/components/kompass/SupplierForm.tsx` - Add Certification tab to the supplier dialog; currently a simple form dialog, will need to evolve to tabbed interface

**Service Layer:**
- `apps/Client/src/services/kompassService.ts` - Add audit-related service methods (uploadAudit, getAudits, classifyAudit, overrideClassification, reprocessAudit)

**Type Definitions:**
- `apps/Client/src/types/kompass.ts` - Add TypeScript interfaces for audit DTOs (SupplierAuditResponse, AuditExtractionData, ClassificationGrade, etc.)

**Reference Files (Patterns):**
- `apps/Client/src/pages/kompass/SuppliersPage.tsx` - Reference for MUI patterns, state management, loading states
- `apps/Client/src/pages/DashboardPage.tsx` - Reference for chart implementation using recharts
- `apps/Client/src/components/kompass/KPICard.tsx` - Reference for card component patterns with loading states
- `apps/Client/src/components/kompass/ClientForm.tsx` - Reference for tabbed dialog form pattern (if exists)

**Backend API Reference (Already Implemented in Issue #82):**
- `apps/Server/app/api/audit_routes.py` - Backend endpoints for audit operations
- `apps/Server/app/models/kompass_dto.py` - Backend DTOs (lines 458-545) to match frontend types

**E2E Test Reference:**
- `.claude/commands/test_e2e.md` - E2E test runner documentation
- `.claude/commands/e2e/test_suppliers_page.md` - Reference for suppliers E2E test structure

### New Files

**Components:**
- `apps/Client/src/components/kompass/AuditUploader.tsx` - Drag-and-drop PDF upload component
- `apps/Client/src/components/kompass/AuditSummaryCard.tsx` - Extracted audit data display card
- `apps/Client/src/components/kompass/ClassificationBadge.tsx` - A/B/C classification badge with tooltip
- `apps/Client/src/components/kompass/ClassificationOverrideDialog.tsx` - Override classification modal
- `apps/Client/src/components/kompass/MarketsServedChart.tsx` - Horizontal bar chart for markets
- `apps/Client/src/components/kompass/SupplierCertificationTab.tsx` - Main certification tab container

**E2E Test:**
- `.claude/commands/e2e/test_supplier_certification_tab.md` - E2E test for certification tab functionality

## Implementation Plan

### Phase 1: Foundation
Establish TypeScript types and service layer integration to connect frontend with existing backend API.

1. Add TypeScript interfaces in `kompass.ts` that match the backend DTOs
2. Add audit service methods to `kompassService.ts` for API communication
3. These foundational pieces enable all subsequent component development

### Phase 2: Core Implementation
Build the individual UI components following existing codebase patterns.

1. Create ClassificationBadge - Simple visual component with color coding
2. Create MarketsServedChart - Bar chart using recharts library
3. Create AuditUploader - Drag-and-drop file upload with progress
4. Create AuditSummaryCard - Display extracted data with actions
5. Create ClassificationOverrideDialog - Modal for manual override

### Phase 3: Integration
Integrate components into the supplier workflow.

1. Create SupplierCertificationTab - Container orchestrating all components
2. Modify SupplierForm - Convert to tabbed interface with Certification tab
3. Ensure proper data flow between components

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create E2E Test File
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_suppliers_page.md` to understand E2E test patterns
- Create `.claude/commands/e2e/test_supplier_certification_tab.md` with test steps covering:
  - Navigate to Suppliers page and open a supplier
  - Switch to Certification tab
  - Upload an audit PDF file via drag-drop
  - Verify upload progress indicator displays
  - Verify extraction summary displays after processing
  - Verify markets chart renders with correct data
  - Verify positive/negative points display
  - Verify classification badge shows with correct color
  - Open override dialog and change classification with notes
  - Verify classification updates
  - Test View Full PDF button
  - Test Reprocess button for failed extractions
  - Verify responsive design on smaller viewport

### Step 2: Add TypeScript Interfaces
- Open `apps/Client/src/types/kompass.ts`
- Add the following interfaces after the existing Supplier DTOs section:

```typescript
// =============================================================================
// SUPPLIER AUDIT DTOs
// =============================================================================

export type AuditType = 'factory_audit' | 'container_inspection';
export type SupplierType = 'manufacturer' | 'trader' | 'unknown';
export type ExtractionStatus = 'pending' | 'processing' | 'completed' | 'failed';
export type ClassificationGrade = 'A' | 'B' | 'C';

export interface MarketsServed {
  south_america?: number;
  north_america?: number;
  europe?: number;
  asia?: number;
  other?: number;
}

export interface SupplierAuditCreate {
  supplier_id: string;
  audit_type?: AuditType;
  document_url: string;
  document_name?: string | null;
  file_size_bytes?: number | null;
  audit_date?: string | null;
  inspector_name?: string | null;
}

export interface SupplierAuditResponse {
  id: string;
  supplier_id: string;
  audit_type: AuditType;
  document_url: string;
  document_name: string | null;
  file_size_bytes: number | null;

  // Extracted data
  supplier_type: SupplierType | null;
  employee_count: number | null;
  factory_area_sqm: number | null;
  production_lines_count: number | null;
  markets_served: MarketsServed | null;
  certifications: string[] | null;
  has_machinery_photos: boolean;
  positive_points: string[] | null;
  negative_points: string[] | null;
  products_verified: string[] | null;

  // Audit metadata
  audit_date: string | null;
  inspector_name: string | null;

  // Processing
  extraction_status: ExtractionStatus;
  extraction_raw_response: Record<string, unknown> | null;
  extracted_at: string | null;

  // Classification
  ai_classification: ClassificationGrade | null;
  ai_classification_reason: string | null;
  manual_classification: ClassificationGrade | null;
  classification_notes: string | null;

  // Timestamps
  created_at: string;
  updated_at: string;
}

export interface SupplierAuditListResponse {
  items: SupplierAuditResponse[];
  pagination: Pagination;
}

export interface ClassificationOverride {
  classification: ClassificationGrade;
  notes: string;
}
```

### Step 3: Add Audit Service Methods
- Open `apps/Client/src/services/kompassService.ts`
- Add new `auditService` object with the following methods:

```typescript
export const auditService = {
  async upload(
    supplierId: string,
    file: File,
    auditType: AuditType = 'factory_audit',
    onProgress?: (percent: number) => void
  ): Promise<SupplierAuditResponse>

  async list(supplierId: string, page?: number, limit?: number): Promise<SupplierAuditListResponse>

  async get(supplierId: string, auditId: string): Promise<SupplierAuditResponse>

  async reprocess(supplierId: string, auditId: string): Promise<SupplierAuditResponse>

  async classify(supplierId: string, auditId: string): Promise<SupplierAuditResponse>

  async overrideClassification(
    supplierId: string,
    auditId: string,
    data: ClassificationOverride
  ): Promise<SupplierAuditResponse>

  async delete(supplierId: string, auditId: string): Promise<void>
}
```

- Use `FormData` for file upload with `Content-Type: multipart/form-data`
- Implement `onProgress` callback using XMLHttpRequest or axios progress events
- Follow existing logging pattern: `console.log('INFO [auditService]: ...')`

### Step 4: Create ClassificationBadge Component
- Create `apps/Client/src/components/kompass/ClassificationBadge.tsx`
- Props interface:
  ```typescript
  interface ClassificationBadgeProps {
    grade: ClassificationGrade | null;
    aiReason?: string | null;
    isManualOverride?: boolean;
    size?: 'small' | 'medium' | 'large';
  }
  ```
- Display behavior:
  - Grade 'A': Green background (#4caf50), white text
  - Grade 'B': Orange background (#ff9800), white text
  - Grade 'C': Red background (#f44336), white text
  - No grade (null): Gray background, "Pending" text
- Include MUI Tooltip showing reasoning when available
- If `isManualOverride` is true, show small "Manual" indicator

### Step 5: Create MarketsServedChart Component
- Create `apps/Client/src/components/kompass/MarketsServedChart.tsx`
- Props interface:
  ```typescript
  interface MarketsServedChartProps {
    markets: MarketsServed | null;
    height?: number;
  }
  ```
- Use `recharts` library (already a project dependency - verify in package.json)
- Implement horizontal bar chart with:
  - ResponsiveContainer wrapper
  - BarChart with `layout="vertical"`
  - XAxis with percentage domain [0, 100]
  - YAxis with market names as categories
  - Color-coded bars (South America, North America, Europe, Asia, Other)
  - Show percentage labels on bars
- Handle null/empty markets gracefully with "No market data available" message
- Reference `DashboardPage.tsx` for chart patterns

### Step 6: Create AuditUploader Component
- Create `apps/Client/src/components/kompass/AuditUploader.tsx`
- Props interface:
  ```typescript
  interface AuditUploaderProps {
    supplierId: string;
    onUploadComplete: (audit: SupplierAuditResponse) => void;
    onError?: (error: string) => void;
    disabled?: boolean;
  }
  ```
- Implement drag-and-drop zone using native HTML5 drag events (onDragOver, onDragLeave, onDrop)
- Styling: Dashed border, highlight on drag over
- File input for click-to-browse fallback
- Validation:
  - Accept only `.pdf` files (MIME type: application/pdf)
  - Max file size: 25MB (show error if exceeded)
- Display:
  - Upload progress bar (LinearProgress from MUI)
  - Processing status after upload ("Processing...", "Extraction complete", "Extraction failed")
- Use the `auditService.upload()` method with progress callback
- Show visual feedback during different states: idle, dragging, uploading, processing, complete, error

### Step 7: Create AuditSummaryCard Component
- Create `apps/Client/src/components/kompass/AuditSummaryCard.tsx`
- Props interface:
  ```typescript
  interface AuditSummaryCardProps {
    audit: SupplierAuditResponse;
    onReprocess?: (auditId: string) => void;
    onViewPdf?: (documentUrl: string) => void;
    onOverrideClick?: () => void;
    showClassification?: boolean;
  }
  ```
- Layout (using MUI Grid):
  - Top row: Quick Summary (left) + Classification (right)
  - Quick Summary section:
    - Supplier type with checkmark icon (manufacturer) or X icon (trader)
    - Employee count
    - Factory size (sqm)
    - Production lines count
    - List of certifications as Chips
  - Classification section:
    - ClassificationBadge component
    - "Override" button if `onOverrideClick` provided
- Middle row: MarketsServedChart component
- Bottom row: Two columns
  - Positive Points (green checkmark icon, bullet list)
  - Negative Points (warning icon, bullet list)
- Footer: "View Full PDF" and "Reprocess" buttons
- Handle extraction_status:
  - 'pending' or 'processing': Show Skeleton loaders
  - 'failed': Show error message with Reprocess button
  - 'completed': Show full summary
- Use MUI Card, CardContent, Typography, Chip, IconButton components

### Step 8: Create ClassificationOverrideDialog Component
- Create `apps/Client/src/components/kompass/ClassificationOverrideDialog.tsx`
- Props interface:
  ```typescript
  interface ClassificationOverrideDialogProps {
    open: boolean;
    onClose: () => void;
    onConfirm: (data: ClassificationOverride) => Promise<void>;
    currentClassification: ClassificationGrade | null;
    supplierName: string;
  }
  ```
- Dialog content:
  - Title: "Override Classification"
  - Subtitle showing current classification and supplier name
  - TextField (select) for new classification (A, B, C options)
  - TextField (multiline, required) for notes explaining override reason
  - Minimum 10 characters for notes
- Actions:
  - Cancel button
  - Confirm button (disabled if notes too short)
  - Loading state during submission
- Use react-hook-form for form management (matching project patterns)
- Show Alert on error

### Step 9: Create SupplierCertificationTab Component
- Create `apps/Client/src/components/kompass/SupplierCertificationTab.tsx`
- Props interface:
  ```typescript
  interface SupplierCertificationTabProps {
    supplierId: string;
    supplierName: string;
  }
  ```
- State management:
  - `audits: SupplierAuditResponse[]`
  - `loading: boolean`
  - `error: string | null`
  - `overrideDialogOpen: boolean`
  - `selectedAudit: SupplierAuditResponse | null`
- On mount: Fetch audits using `auditService.list(supplierId)`
- Layout:
  - AuditUploader at top
  - If audits exist:
    - Latest audit AuditSummaryCard (prominent display)
    - "Audit History" section with table of past audits (date, type, status, classification)
  - If no audits:
    - Empty state message: "No audits uploaded. Upload a factory audit to get started."
- Handle override flow:
  - When override button clicked, open ClassificationOverrideDialog
  - On confirm, call `auditService.overrideClassification()`
  - Refresh audit data on success
- Handle reprocess flow:
  - Call `auditService.reprocess()`
  - Poll for completion or show processing state
- Handle view PDF:
  - Open document_url in new browser tab

### Step 10: Modify SupplierForm to Add Tabbed Interface
- Open `apps/Client/src/components/kompass/SupplierForm.tsx`
- Convert from simple form to tabbed Dialog:
  - Import MUI Tabs, Tab, TabPanel components
  - Create custom TabPanel component for tab content visibility
  - Tab 0: "General" - existing form fields
  - Tab 1: "Certification" - SupplierCertificationTab component
- State additions:
  - `activeTab: number` (default 0)
- Conditional rendering:
  - Only show Certification tab when in edit mode (supplier exists)
  - In create mode, show only General tab
- Pass supplier.id and supplier.name to SupplierCertificationTab
- Ensure form submission only affects General tab data
- Update DialogTitle to include tab name context

### Step 11: Export New Components
- Update `apps/Client/src/components/kompass/index.ts` (if exists) to export new components
- Or ensure components are exported directly from their files

### Step 12: Run Validation Commands
Execute all validation commands to ensure zero regressions.

## Testing Strategy

### Unit Tests
- ClassificationBadge: Test color mappings for each grade, pending state, tooltip display
- MarketsServedChart: Test chart rendering with valid data, empty data handling
- AuditUploader: Test file validation (type, size), drag-and-drop states, progress updates
- AuditSummaryCard: Test rendering for each extraction_status, action button callbacks
- ClassificationOverrideDialog: Test form validation, submit flow, error handling
- SupplierCertificationTab: Test audit list fetching, empty state, override flow

### Edge Cases
- Upload a file larger than 25MB - should show error
- Upload a non-PDF file - should show error
- View audit with extraction_status='failed' - should show reprocess option
- Override classification without notes - should prevent submission
- View audit with null/empty markets_served - should show fallback message
- Handle network errors during upload - should show error and allow retry
- Handle API errors during classification override - should show error in dialog

## Acceptance Criteria
- [ ] Can upload audit PDF via drag-drop or file picker
- [ ] Shows upload progress during file upload
- [ ] Displays extraction summary after processing completes
- [ ] Markets chart renders correctly with percentage values
- [ ] Positive/negative points displayed in two columns with icons
- [ ] Classification badge shows correct color (A=green, B=orange, C=red)
- [ ] "Pending" badge shown when classification not yet available
- [ ] Can override classification with required notes
- [ ] Override updates classification and shows "Manual" indicator
- [ ] Can view full PDF document in new tab
- [ ] Can reprocess failed extractions
- [ ] Responsive design works on tablet/mobile viewports
- [ ] Loading and error states handled gracefully
- [ ] All TypeScript types compile without errors
- [ ] All existing tests continue to pass

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npm run typecheck` - Run TypeScript check to validate types
- `cd apps/Client && npm run lint` - Run ESLint to check code quality
- `cd apps/Client && npm run build` - Run production build to verify compilation
- `cd apps/Server && source .venv/bin/activate && python -m pytest tests/ -v --tb=short` - Run Server tests
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_supplier_certification_tab.md` to validate the certification tab functionality end-to-end

## Notes
- The backend API endpoints are already implemented in Issue #82, so this is purely frontend work
- File upload currently uses a temporary file:// URL in development; production will use cloud storage
- The recharts library should already be available (used in DashboardPage) - verify in package.json
- Consider adding polling mechanism to check extraction_status when it's 'pending' or 'processing'
- The classification override requires admin/manager role on the backend - ensure frontend handles 403 gracefully
- For large audits, extraction may take 30-60 seconds; provide appropriate user feedback
- The certification tab should be read-only for users with 'viewer' role
