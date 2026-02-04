# Feature: Add supplier audits database schema and DTOs

## Metadata
issue_number: `79`
adw_id: `8bb175a8`
issue_json: `{"number":79,"title":"feat: Add supplier audits database schema and DTOs","body":"## Summary\nAdd database schema and Pydantic DTOs for the new Supplier Certification system.\n\n## Context\nFrom PRD: `ai_docs/PRD-Supplier-Certification-System.md`\n\nThe Supplier Certification system requires storing factory audit documents and their extracted data for supplier qualification.\n\n## Requirements\n\n### Database Schema\nCreate new `supplier_audits` table with fields:\n- `id`, `supplier_id` (FK to suppliers)\n- `audit_type` ('factory_audit', 'container_inspection')\n- `document_url`, `document_name`, `file_size_bytes`\n- Extracted data fields: `supplier_type`, `employee_count`, `factory_area_sqm`, `production_lines_count`, `markets_served` (JSONB), `certifications` (TEXT[]), `has_machinery_photos`, `positive_points` (TEXT[]), `negative_points` (TEXT[]), `products_verified` (TEXT[])\n- Audit metadata: `audit_date`, `inspector_name`\n- Processing fields: `extraction_status`, `extraction_raw_response`, `extracted_at`\n- Classification: `ai_classification`, `ai_classification_reason`, `manual_classification`, `classification_notes`\n\n### Alter suppliers table\nAdd columns:\n- `certification_status` ('uncertified', 'pending_review', 'certified_a', 'certified_b', 'certified_c')\n- `pipeline_status` ('contacted', 'potential', 'quoted', 'certified', 'active', 'inactive')\n- `latest_audit_id` (FK to supplier_audits)\n- `certified_at`\n\n### Pydantic DTOs\nCreate in `app/models/kompass_dto.py`:\n- `SupplierAuditCreate`\n- `SupplierAuditResponse`\n- `SupplierAuditExtraction`\n- `SupplierClassification`\n- Update `SupplierResponse` with new fields\n\n## Acceptance Criteria\n- [ ] Migration script creates `supplier_audits` table\n- [ ] Suppliers table has new certification columns\n- [ ] DTOs defined with proper validation\n- [ ] Indexes created for efficient queries\n\n## Labels\nfeature, backend, database, phase-1"}`

## Feature Description
This feature adds the foundational database schema and Pydantic DTOs for the Supplier Certification system. The system enables Kompass Trading to store factory audit documents, extract key data points using AI, and track supplier certification status through a defined pipeline workflow. This is Phase 1 of the Supplier Certification feature, focusing solely on the data layer without implementing API endpoints or UI components.

## User Story
As a sourcing manager
I want supplier audit data to be stored in a structured database schema
So that the system can track certification status, store extracted audit data, and enable future features like AI classification and pipeline workflows

## Problem Statement
Currently, supplier qualification information is tracked manually with no structured storage for factory audit data. The existing suppliers table lacks fields for certification status and pipeline tracking. Without a proper data model, the Supplier Certification system cannot be built.

## Solution Statement
Create a new `supplier_audits` table to store factory audit documents and their extracted data. Add certification and pipeline status columns to the existing `suppliers` table. Define comprehensive Pydantic DTOs for audit data validation and API responses. This provides the data foundation for future phases that will add audit upload, AI extraction, and classification features.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/database/schema.sql` - Main database schema file where the new `supplier_audits` table and `suppliers` table alterations will be added. Follow existing table patterns with UUID primary keys, timestamps, and appropriate indexes.

- `apps/Server/app/models/kompass_dto.py` - Pydantic DTOs file where new audit-related DTOs will be added. Follow existing patterns for Create/Update/Response DTOs, use proper Field validators, and maintain consistent naming conventions.

- `ai_docs/PRD-Supplier-Certification-System.md` - PRD containing the complete requirements and schema design for the Supplier Certification system. Use Section 3.1 for exact schema specifications.

### New Files

- `apps/Server/database/migrations/001_supplier_audits.sql` - Migration script for adding the `supplier_audits` table and altering the `suppliers` table. This will be a standalone migration file that can be run against existing databases.

## Implementation Plan

### Phase 1: Foundation
1. Review existing schema patterns in `schema.sql` for table structure, naming conventions, indexes, and triggers
2. Review existing DTO patterns in `kompass_dto.py` for enum definitions, Create/Update/Response patterns, and validation approach
3. Study the PRD schema requirements in detail to ensure all fields are captured correctly

### Phase 2: Core Implementation
1. Create the migration directory structure if not exists
2. Write the migration SQL script with:
   - New `supplier_audits` table with all required fields
   - ALTER statements for `suppliers` table
   - Indexes for efficient queries
   - Auto-update trigger for `updated_at`
3. Add new enums to DTOs: `AuditType`, `ExtractionStatus`, `CertificationStatus`, `SupplierPipelineStatus`
4. Create audit-related DTOs following existing patterns
5. Update `SupplierResponseDTO` and related DTOs with new certification fields

### Phase 3: Integration
1. Update the main `schema.sql` to include the new table (for fresh installations)
2. Ensure foreign key relationships are correct
3. Verify enum values match between SQL CHECK constraints and Pydantic enums
4. Test DTO validation with sample data

## Step by Step Tasks

### Step 1: Create migration directory structure
- Create `apps/Server/database/migrations/` directory if it doesn't exist
- This follows standard database migration patterns for incremental schema changes

### Step 2: Create the supplier_audits migration script
- Create `apps/Server/database/migrations/001_supplier_audits.sql`
- Add `supplier_audits` table with all fields from requirements:
  - `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`
  - `supplier_id UUID NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE`
  - `audit_type VARCHAR(50) NOT NULL DEFAULT 'factory_audit' CHECK (audit_type IN ('factory_audit', 'container_inspection'))`
  - `document_url VARCHAR(1000) NOT NULL`
  - `document_name VARCHAR(255)`
  - `file_size_bytes BIGINT`
  - Extracted data fields: `supplier_type`, `employee_count`, `factory_area_sqm`, `production_lines_count`, `markets_served` (JSONB), `certifications` (TEXT[]), `has_machinery_photos`, `positive_points` (TEXT[]), `negative_points` (TEXT[]), `products_verified` (TEXT[])
  - Audit metadata: `audit_date DATE`, `inspector_name VARCHAR(255)`
  - Processing fields: `extraction_status VARCHAR(50) DEFAULT 'pending' CHECK (...)`, `extraction_raw_response JSONB`, `extracted_at TIMESTAMP WITH TIME ZONE`
  - Classification: `ai_classification VARCHAR(10)`, `ai_classification_reason TEXT`, `manual_classification VARCHAR(10)`, `classification_notes TEXT`
  - Standard timestamps: `created_at`, `updated_at`
- Add indexes for `supplier_id` and other frequently queried fields
- Add auto-update trigger for `updated_at`

### Step 3: Add ALTER statements for suppliers table
- In the same migration script, add:
  - `ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS certification_status VARCHAR(50) DEFAULT 'uncertified' CHECK (...)`
  - `ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS pipeline_status VARCHAR(50) DEFAULT 'contacted' CHECK (...)`
  - `ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS latest_audit_id UUID REFERENCES supplier_audits(id)`
  - `ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS certified_at TIMESTAMP WITH TIME ZONE`
- Add indexes for new columns

### Step 4: Add new enums to kompass_dto.py
- Add `AuditType` enum with values: `FACTORY_AUDIT`, `CONTAINER_INSPECTION`
- Add `ExtractionStatus` enum with values: `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`
- Add `CertificationStatus` enum with values: `UNCERTIFIED`, `PENDING_REVIEW`, `CERTIFIED_A`, `CERTIFIED_B`, `CERTIFIED_C`
- Add `SupplierPipelineStatus` enum with values: `CONTACTED`, `POTENTIAL`, `QUOTED`, `CERTIFIED`, `ACTIVE`, `INACTIVE`
- Place these after existing enum definitions following the same pattern

### Step 5: Create SupplierAudit DTOs
- Create `SupplierAuditCreateDTO` with fields:
  - `supplier_id: UUID`
  - `audit_type: AuditType = AuditType.FACTORY_AUDIT`
  - `document_url: str = Field(min_length=1, max_length=1000)`
  - `document_name: Optional[str] = Field(default=None, max_length=255)`
  - `file_size_bytes: Optional[int] = Field(default=None, ge=0)`
  - `audit_date: Optional[date] = None`
  - `inspector_name: Optional[str] = Field(default=None, max_length=255)`

- Create `SupplierAuditExtractionDTO` for AI-extracted data:
  - `supplier_type: Optional[str] = Field(default=None, max_length=50)` (values: 'manufacturer', 'trader', 'unknown')
  - `employee_count: Optional[int] = Field(default=None, ge=0)`
  - `factory_area_sqm: Optional[int] = Field(default=None, ge=0)`
  - `production_lines_count: Optional[int] = Field(default=None, ge=0)`
  - `markets_served: Optional[dict] = None` (JSONB)
  - `certifications: Optional[List[str]] = None`
  - `has_machinery_photos: bool = False`
  - `positive_points: Optional[List[str]] = None`
  - `negative_points: Optional[List[str]] = None`
  - `products_verified: Optional[List[str]] = None`

- Create `SupplierAuditClassificationDTO` for classification operations:
  - `classification: str = Field(pattern=r'^[ABC]$')` (A, B, or C)
  - `notes: Optional[str] = None`

- Create `SupplierAuditResponseDTO` with all fields:
  - All fields from create DTO
  - All fields from extraction DTO
  - `extraction_status: ExtractionStatus`
  - `extraction_raw_response: Optional[dict] = None`
  - `extracted_at: Optional[datetime] = None`
  - `ai_classification: Optional[str] = None`
  - `ai_classification_reason: Optional[str] = None`
  - `manual_classification: Optional[str] = None`
  - `classification_notes: Optional[str] = None`
  - `created_at: datetime`
  - `updated_at: datetime`

- Create `SupplierAuditListResponseDTO` with pagination pattern

### Step 6: Update existing Supplier DTOs
- Update `SupplierCreateDTO`:
  - Add `certification_status: CertificationStatus = CertificationStatus.UNCERTIFIED`
  - Add `pipeline_status: SupplierPipelineStatus = SupplierPipelineStatus.CONTACTED`

- Update `SupplierUpdateDTO`:
  - Add `certification_status: Optional[CertificationStatus] = None`
  - Add `pipeline_status: Optional[SupplierPipelineStatus] = None`

- Update `SupplierResponseDTO`:
  - Add `certification_status: CertificationStatus`
  - Add `pipeline_status: SupplierPipelineStatus`
  - Add `latest_audit_id: Optional[UUID] = None`
  - Add `certified_at: Optional[datetime] = None`

### Step 7: Update main schema.sql for fresh installations
- Add the `supplier_audits` table definition to `apps/Server/database/schema.sql`
- Add the new columns to the `suppliers` table definition
- Add appropriate indexes and triggers
- Ensure table is created AFTER suppliers table due to foreign key dependency

### Step 8: Run validation commands
- Run ruff linter to check Python code quality
- Run pytest to ensure existing tests still pass
- Verify DTO imports work correctly

## Testing Strategy

### Unit Tests
- Test that all new DTOs can be instantiated with valid data
- Test validation constraints (Field validators, patterns, min/max values)
- Test enum value serialization/deserialization
- Test that existing SupplierResponseDTO still works with new optional fields

### Edge Cases
- Test DTO creation with missing optional fields
- Test enum value case sensitivity
- Test JSONB field serialization for `markets_served`
- Test array field handling for `certifications`, `positive_points`, `negative_points`
- Test classification pattern validation (only A, B, or C allowed)

## Acceptance Criteria
- [ ] Migration script `001_supplier_audits.sql` creates `supplier_audits` table with all required fields
- [ ] Migration script adds certification columns to `suppliers` table
- [ ] Proper indexes created on `supplier_id`, `certification_status`, `pipeline_status`, `extraction_status`
- [ ] New enums defined: `AuditType`, `ExtractionStatus`, `CertificationStatus`, `SupplierPipelineStatus`
- [ ] `SupplierAuditCreateDTO` defined with proper validation
- [ ] `SupplierAuditExtractionDTO` defined for AI extraction data
- [ ] `SupplierAuditClassificationDTO` defined for classification operations
- [ ] `SupplierAuditResponseDTO` defined with all fields
- [ ] `SupplierAuditListResponseDTO` defined with pagination
- [ ] Existing Supplier DTOs updated with new certification fields
- [ ] Main `schema.sql` updated for fresh installations
- [ ] All Python files pass ruff linting
- [ ] Existing tests continue to pass

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `mkdir -p apps/Server/database/migrations` - Create migrations directory if needed
- `cd apps/Server && .venv/bin/ruff check .` - Run ruff linter to check Python code quality
- `cd apps/Server && .venv/bin/ruff check app/models/kompass_dto.py` - Specifically validate the DTOs file
- `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` - Run Server tests to validate zero regressions
- `cd apps/Server && python -c "from app.models.kompass_dto import *; print('DTOs import successfully')"` - Verify all DTOs can be imported

## Notes
- This feature is Phase 1 (data layer only) of the Supplier Certification system. Future phases will add:
  - Phase 2: API endpoints for audit upload and retrieval
  - Phase 3: AI extraction service integration
  - Phase 4: Classification logic and pipeline workflow
  - Phase 5: Frontend UI components
- The migration script uses `IF NOT EXISTS` and `ADD COLUMN IF NOT EXISTS` patterns for idempotent execution
- Foreign key from `suppliers.latest_audit_id` to `supplier_audits.id` creates a circular reference that requires careful ordering in migrations
- The `suppliers` table already has `status` column with values `active`, `inactive`, `pending_review` - the new `pipeline_status` is separate and tracks the supplier onboarding workflow
- Consider adding a comment to differentiate `status` (operational status) from `pipeline_status` (onboarding workflow) in future documentation
