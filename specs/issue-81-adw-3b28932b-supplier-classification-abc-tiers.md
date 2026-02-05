# Feature: Supplier Classification System (A/B/C Tiers)

## Metadata
issue_number: `81`
adw_id: `3b28932b`
issue_json: `{}`

## Feature Description
Implement an AI-driven supplier classification system that suggests A/B/C tier ratings based on extracted audit data. The system analyzes factory audit extraction results (supplier type, certifications, production capacity, negative/positive points, export market experience) and generates a classification recommendation with human-readable reasoning. Users can override AI classifications with required notes, and classification history is tracked. When a classification is finalized, the associated supplier's certification_status is automatically updated.

## User Story
As a sourcing manager
I want the system to analyze audit data and suggest an A/B/C supplier classification with clear reasoning
So that I can make faster and more informed supplier qualification decisions while retaining the ability to override based on business context

## Problem Statement
After AI extraction of factory audit documents (Issue #80), the extracted data exists but there is no automated way to classify suppliers into certification tiers. Sourcing managers must manually review all extracted data points to determine supplier quality ratings, which is time-consuming and inconsistent.

## Solution Statement
Add two new service methods to `audit_service.py`:
1. `classify_supplier(audit_id)` - Analyzes extracted audit data, applies classification logic, generates human-readable reasoning, stores the AI classification, and updates the supplier's certification status
2. `override_classification(audit_id, classification, notes, user_id)` - Allows manual override of AI classification with required notes, tracks who made the override, and updates supplier certification_status

Add corresponding API endpoints and repository methods to support these operations. Classification updates cascade to the supplier record (certification_status, certified_at, latest_audit_id).

## Relevant Files
Use these files to implement the feature:

### Existing Files to Modify

- `apps/Server/app/services/audit_service.py` - Main file to add `classify_supplier()` and `override_classification()` methods. Already has AI client setup and extraction logic that can be leveraged.
- `apps/Server/app/repository/audit_repository.py` - Add `update_classification()` method to store AI classification and `update_manual_classification()` for overrides.
- `apps/Server/app/api/audit_routes.py` - Add new API endpoints for classification and override.
- `apps/Server/app/models/kompass_dto.py` - Add DTOs for classification request/response if needed. Already has `SupplierAuditClassificationDTO` that can be used.
- `apps/Server/app/repository/kompass_repository.py` - Modify `SupplierRepository` to add method for updating certification status and linking latest_audit_id.
- `apps/Server/tests/test_audit_service.py` - Add unit tests for new classification methods.

### Reference Files (Read-Only)

- `apps/Server/database/schema.sql` - Schema already includes classification fields: `ai_classification`, `ai_classification_reason`, `manual_classification`, `classification_notes` in `supplier_audits` table, and `certification_status`, `certified_at`, `latest_audit_id` in `suppliers` table.
- `ai_docs/PRD-Supplier-Certification-System.md` - Contains classification tier criteria and business rules.
- `apps/Server/app/models/kompass_dto.py` - Existing enums: `CertificationStatus` (uncertified, pending_review, certified_a, certified_b, certified_c).

### New Files
- `apps/Server/tests/test_classification.py` - Dedicated unit tests for classification logic.

## Implementation Plan

### Phase 1: Foundation - Repository Layer
Add repository methods to update classification fields in `supplier_audits` table and certification fields in `suppliers` table.

### Phase 2: Core Implementation - Service Layer
Implement classification logic in `audit_service.py`:
1. `classify_supplier()` - Score-based classification with AI reasoning
2. `override_classification()` - Manual override with required notes and user tracking
3. Helper method `_update_supplier_certification()` to cascade changes to supplier record

### Phase 3: Integration - API Routes
Add REST endpoints for triggering classification and handling overrides. Wire up the service methods and ensure proper authorization.

## Step by Step Tasks

### Step 1: Add Classification Repository Methods
- Read `apps/Server/app/repository/audit_repository.py`
- Add `update_classification(audit_id, classification, reason)` method to update `ai_classification` and `ai_classification_reason` fields
- Add `update_manual_classification(audit_id, classification, notes)` method to update `manual_classification` and `classification_notes` fields
- Both methods should set `updated_at = NOW()`

### Step 2: Add Supplier Certification Update Method
- Read `apps/Server/app/repository/kompass_repository.py` and find `SupplierRepository`
- Add `update_certification_status(supplier_id, certification_status, audit_id)` method
- This method updates `suppliers.certification_status`, `suppliers.certified_at = NOW()`, and `suppliers.latest_audit_id`
- Map classification 'A'/'B'/'C' to CertificationStatus enum values (certified_a, certified_b, certified_c)

### Step 3: Implement Classification Logic in Audit Service
- Read `apps/Server/app/services/audit_service.py`
- Add `classify_supplier(audit_id: UUID) -> SupplierAuditResponseDTO` method:
  - Get audit by ID (must have extraction_status = 'completed')
  - Apply classification algorithm based on:
    - supplier_type: manufacturer = +3, trader = +1, unknown = 0
    - certifications count: 3+ = +2, 1-2 = +1, 0 = 0
    - production_lines_count: 3+ = +1, 1-2 = +0.5, 0 = 0
    - negative_points count: 0 = +1, 1-2 = 0, 3+ = -1
    - positive_points count: 3+ = +1, 1-2 = +0.5, 0 = 0
    - markets_served.south_america > 0 = +0.5 (bonus for SA experience)
  - Calculate total score: Type A >= 6, Type B >= 3, Type C < 3
  - Generate human-readable reasoning explaining the classification
  - Store classification via repository
  - Update supplier certification status via repository
  - Return updated audit DTO

### Step 4: Implement Override Classification Method
- Add `override_classification(audit_id: UUID, classification: str, notes: str, user_id: UUID) -> SupplierAuditResponseDTO` method:
  - Validate classification is 'A', 'B', or 'C'
  - Validate notes is not empty (required for overrides)
  - Get audit by ID
  - Update manual_classification and classification_notes via repository
  - Update supplier certification_status (manual takes precedence)
  - Return updated audit DTO

### Step 5: Add Classification API Endpoints
- Read `apps/Server/app/api/audit_routes.py`
- Add `POST /{supplier_id}/audits/{audit_id}/classify` endpoint:
  - Calls `audit_service.classify_supplier(audit_id)`
  - Requires admin/manager/user roles
  - Returns SupplierAuditResponseDTO
- Add `PUT /{supplier_id}/audits/{audit_id}/classification` endpoint:
  - Accepts `SupplierAuditClassificationDTO` with classification and notes
  - Calls `audit_service.override_classification()`
  - Requires admin/manager roles only (override is more sensitive)
  - Returns SupplierAuditResponseDTO

### Step 6: Add Unit Tests for Classification Logic
- Create `apps/Server/tests/test_classification.py`
- Test `classify_supplier()`:
  - Test Type A classification (manufacturer, 3+ certs, many positives, minimal negatives)
  - Test Type B classification (moderate scores)
  - Test Type C classification (trader, no certs, many negatives)
  - Test reasoning generation is human-readable
  - Test supplier certification_status is updated
  - Test error when audit not completed
- Test `override_classification()`:
  - Test successful override with notes
  - Test error when notes are empty
  - Test supplier status reflects override
  - Test invalid classification value rejected

### Step 7: Update Existing Tests
- Read `apps/Server/tests/test_audit_service.py`
- Add tests for classification integration with existing audit flow
- Ensure mock data includes classification fields

### Step 8: Run Validation Commands
- Run all validation commands to ensure zero regressions

## Testing Strategy

### Unit Tests
- Test `classify_supplier()` with various extracted data scenarios (manufacturer vs trader, different cert counts, positive/negative points)
- Test scoring algorithm produces correct tier for edge cases
- Test reasoning generation includes key factors
- Test `override_classification()` with valid and invalid inputs
- Test supplier certification status updates correctly
- Test error handling for missing/incomplete audits

### Edge Cases
- Audit with extraction_status != 'completed' - should fail classification
- Audit with no extracted data (all nulls) - should classify as Type C
- Override without notes - should fail validation
- Override with empty notes - should fail validation
- Classification of already-classified audit - should allow reclassification
- Multiple overrides - latest should take precedence

## Acceptance Criteria
- [ ] `classify_supplier(audit_id)` generates A/B/C classification based on extracted audit data
- [ ] Classification reasoning is human-readable and explains key factors
- [ ] `override_classification(audit_id, classification, notes)` allows manual override with required notes
- [ ] Override requires notes (cannot be empty)
- [ ] Supplier `certification_status` updates automatically when audit is classified (certified_a, certified_b, or certified_c)
- [ ] Supplier `certified_at` timestamp updates when classification is set
- [ ] Supplier `latest_audit_id` links to the classified audit
- [ ] API endpoints for classify and override are protected with appropriate roles
- [ ] All new code has unit test coverage
- [ ] Validation commands pass with zero regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && .venv/bin/pytest tests/test_audit_service.py tests/test_classification.py -v --tb=short` - Run audit service and classification tests
- `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` - Run all Server tests
- `cd apps/Server && .venv/bin/ruff check .` - Run linting on Server code
- `cd apps/Client && npm run typecheck` - Run Client type check (no frontend changes but verify no breaks)
- `cd apps/Client && npm run build` - Run Client build (verify no breaks)

## Notes

### Classification Scoring Algorithm
The scoring system is designed to be transparent and adjustable:
- **Manufacturer status** is weighted heavily (3 points) as it's the most critical factor for Type A
- **Certifications** provide quality assurance confidence (2 points for 3+)
- **Production capacity** (lines) indicates scale (1 point for 3+)
- **Negative points** act as penalties (-1 for 3+ concerns)
- **Positive points** provide confidence boost (1 point for 3+)
- **South America experience** is a bonus for regional fit (+0.5)

**Score thresholds:**
- Type A: Score >= 6 (typically manufacturer + good certs + minimal negatives)
- Type B: Score >= 3 and < 6 (mixed signals, requires human review)
- Type C: Score < 3 (significant concerns, limited documentation, or trader without verification)

### Human Override Philosophy
Per the PRD: "Classification is a recommendation tool, not a final decision. Human judgment is always required based on product requirements, client needs, and input from the China-based agent (Hijin)."

The override feature exists because:
1. Business context may warrant different classifications
2. Some factors aren't captured in extracted data
3. Relationships and history matter
4. Notes provide audit trail for future reference

### Future Enhancements (Out of Scope)
- Classification history tracking table (for viewing previous classifications)
- Bulk classification of multiple audits
- UI components for classification display and override (separate frontend issue)
- Email notifications on classification changes
