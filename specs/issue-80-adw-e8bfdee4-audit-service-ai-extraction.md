# Feature: Add audit service with AI extraction for factory audits

## Metadata
issue_number: `80`
adw_id: `e8bfdee4`
issue_json: `{"number":80,"title":"feat: Add audit service with AI extraction for factory audits","body":"## Summary\nCreate a new `audit_service.py` that handles factory audit PDF uploads and uses AI to extract key supplier data.\n\n## Context\nFrom PRD: `ai_docs/PRD-Supplier-Certification-System.md`\n\nFactory audits are 70+ page PDFs (~21MB) containing critical supplier qualification information. The system needs to automatically extract ~10 key data points using AI vision capabilities.\n\n## Requirements\n\n### New Service: `app/services/audit_service.py`\n\n**Methods:**\n1. `upload_audit(supplier_id, file, audit_type)` - Upload and queue for processing\n2. `process_audit(audit_id)` - Extract data from PDF using AI\n3. `get_supplier_audits(supplier_id)` - List all audits for a supplier\n4. `get_audit(audit_id)` - Get single audit details\n5. `reprocess_audit(audit_id)` - Re-run extraction\n\n### AI Extraction\nLeverage existing `extraction_service.py` patterns. Create prompt template to extract:\n- `supplier_type` (manufacturer/trader) - CRITICAL\n- `employee_count`\n- `factory_area_sqm`\n- `production_lines_count`\n- `markets_served` (JSON with percentages by region)\n- `certifications` (array)\n- `has_machinery_photos`\n- `positive_points` (array)\n- `negative_points` (array)\n- `products_verified` (array)\n- `audit_date`, `inspector_name`\n\n### File Storage\n- Store uploaded PDFs to cloud storage (use existing patterns if available)\n- Support files up to 25MB\n- Store URL reference in database\n\n## Technical Notes\n- Use background tasks for large PDF processing\n- Set appropriate timeout (audits are large)\n- Return extraction_status for async tracking\n- Log extraction results for debugging\n\n## Acceptance Criteria\n- [ ] Can upload PDF audit documents\n- [ ] AI extracts all required fields from audit PDF\n- [ ] Extraction runs as background job\n- [ ] Can track extraction status\n- [ ] Can reprocess failed extractions\n- [ ] Handles various audit PDF formats gracefully\n\n## Dependencies\n- Issue #79 (database schema) must be completed first\n\n## Labels\nfeature, backend, ai, phase-1"}`

## Feature Description
This feature implements the `audit_service.py` that handles factory audit PDF uploads and uses AI to extract key supplier qualification data. The service leverages existing `extraction_service.py` patterns to process large PDF documents (up to 25MB) containing 70+ pages of factory audit information. Key data points like supplier type (manufacturer vs trader), employee count, factory area, certifications, and positive/negative points are automatically extracted using Claude's vision capabilities. The extracted data is stored in the `supplier_audits` table (created in Issue #79) and can be used for supplier classification and certification workflows.

## User Story
As a sourcing manager
I want to upload factory audit PDF documents and have the system automatically extract key supplier information
So that I can make faster supplier qualification decisions without manually reading 70+ page documents

## Problem Statement
Factory audits are lengthy (70+ pages, ~21MB) PDF documents that require manual review to extract key supplier qualification data. This is time-consuming and inconsistent, leading to delays in supplier qualification decisions. The existing `extraction_service.py` handles product catalog extraction but does not support the specialized extraction of factory audit documents with their unique structure and data points.

## Solution Statement
Create a new `audit_service.py` that:
1. Accepts PDF uploads for factory audits and container inspections
2. Stores uploaded files with URL references in the database
3. Uses Claude AI's vision capabilities to extract ~10 key data points from audit PDFs
4. Processes large PDFs asynchronously using FastAPI background tasks
5. Tracks extraction status (pending → processing → completed/failed)
6. Supports reprocessing failed extractions
7. Integrates with the existing repository pattern for database operations

## Relevant Files
Use these files to implement the feature:

- `apps/Server/app/services/extraction_service.py` - Reference for AI extraction patterns, Claude/OpenAI client initialization, prompt building, JSON response parsing, and error handling. Follow the same patterns for lazy client initialization and AI provider selection.

- `apps/Server/app/models/kompass_dto.py` - Contains the DTOs for supplier audits created in Issue #79: `SupplierAuditCreateDTO`, `SupplierAuditResponseDTO`, `SupplierAuditExtractionDTO`, `SupplierAuditClassificationDTO`, `AuditType`, `ExtractionStatus`. Use these for request/response validation.

- `apps/Server/app/repository/kompass_repository.py` - Reference for repository pattern implementation. Follow the same patterns for database operations, connection management, and error handling.

- `apps/Server/app/api/extraction_routes.py` - Reference for file upload handling, background task scheduling, job status tracking, and file validation. Follow similar patterns for the audit routes.

- `apps/Server/app/config/settings.py` - Settings for AI API keys and timeout configuration. Use existing settings for AI providers.

- `apps/Server/database/schema.sql` - Contains the `supplier_audits` table schema from Issue #79. Reference for understanding the database structure.

- `ai_docs/PRD-Supplier-Certification-System.md` - Contains the extraction prompt template (Section 3.2) and field requirements for audit data extraction.

- `apps/Server/main.py` - Register the new audit routes.

### New Files

- `apps/Server/app/services/audit_service.py` - New service implementing audit upload, AI extraction, and processing logic.

- `apps/Server/app/repository/audit_repository.py` - Repository for `supplier_audits` table CRUD operations.

- `apps/Server/app/api/audit_routes.py` - API routes for audit upload, retrieval, reprocessing, and status tracking.

- `apps/Server/tests/test_audit_service.py` - Unit tests for the audit service.

## Implementation Plan

### Phase 1: Foundation
1. Create the audit repository with CRUD operations for the `supplier_audits` table
2. Implement database operations following existing repository patterns
3. Set up proper connection management and error handling

### Phase 2: Core Implementation
1. Create the audit service with core methods:
   - `upload_audit()` - Save file reference and create audit record
   - `process_audit()` - AI extraction from PDF
   - `get_audit()` and `get_supplier_audits()` - Retrieval methods
   - `reprocess_audit()` - Re-run extraction
2. Implement the AI extraction prompt template for factory audits
3. Add PDF processing using PyPDF2 and Claude vision
4. Implement background task processing for large files

### Phase 3: Integration
1. Create API routes for audit operations
2. Register routes in main.py
3. Add file validation and size limits (25MB)
4. Implement status tracking and progress reporting
5. Add unit tests for the service

## Step by Step Tasks

### Step 1: Create the audit repository
- Create `apps/Server/app/repository/audit_repository.py`
- Implement `create()` method to insert new audit records
- Implement `get_by_id()` method to retrieve single audit
- Implement `get_by_supplier_id()` method to list audits for a supplier with pagination
- Implement `update()` method to update extraction results and status
- Implement `update_extraction_status()` method for status transitions
- Implement `update_extraction_results()` method to store extracted data
- Implement `delete()` method for audit removal
- Create singleton instance `audit_repository`
- Follow existing patterns from `kompass_repository.py` for connection management

### Step 2: Create the audit service
- Create `apps/Server/app/services/audit_service.py`
- Add imports for DTOs, repository, settings, and AI clients
- Create `AuditService` class following singleton pattern
- Implement `_get_anthropic_client()` and `_get_openai_client()` methods (reference `extraction_service.py`)
- Implement `_is_ai_available()` and `_get_preferred_ai_provider()` methods
- Implement the audit extraction prompt template as `_build_audit_extraction_prompt()`:
  ```python
  """
  Analyze this factory audit document and extract the following information in JSON format:
  {
      "supplier_type": "manufacturer" or "trader" or "unknown",
      "employee_count": <number or null>,
      "factory_area_sqm": <number or null>,
      "production_lines_count": <number or null>,
      "markets_served": {"south_america": <pct>, "north_america": <pct>, "europe": <pct>, "asia": <pct>, "other": <pct>},
      "certifications": ["list", "of", "certifications"],
      "has_machinery_photos": true/false,
      "positive_points": ["strength 1", "strength 2", ...],
      "negative_points": ["concern 1", "concern 2", ...],
      "products_verified": ["product 1", "product 2", ...],
      "audit_date": "YYYY-MM-DD" or null,
      "inspector_name": "name" or null
  }
  Focus on: 1. Whether this is a true manufacturer or trader/middleman, 2. Production capacity indicators, 3. Quality certifications, 4. Export market experience, 5. Red flags or concerns, 6. Positive highlights
  If information is not found, use null.
  """
  ```
- Implement `_parse_audit_extraction_response()` to parse JSON from AI response
- Implement `_extract_with_anthropic()` for Claude-based extraction
- Implement `_extract_with_openai()` for OpenAI-based extraction
- Create singleton instance `audit_service`

### Step 3: Implement upload_audit method
- Implement `upload_audit(supplier_id: UUID, document_url: str, document_name: str, file_size_bytes: int, audit_type: AuditType) -> SupplierAuditResponseDTO`
- Validate supplier exists (check with supplier_repository)
- Create audit record with status='pending' via repository
- Return the created audit response DTO
- Log upload action with `print(f"INFO [AuditService]: ...")`

### Step 4: Implement process_audit method
- Implement `process_audit(audit_id: UUID) -> SupplierAuditResponseDTO`
- Retrieve audit record from repository
- Raise ValueError if audit not found
- Update status to 'processing'
- Fetch PDF content from document_url using httpx
- Convert PDF pages to images for vision processing (use pdf2image library)
- Call AI extraction method with images
- Parse response and update audit record with extracted data
- Update status to 'completed' and set `extracted_at` timestamp
- Handle errors gracefully: update status to 'failed', store error in `extraction_raw_response`
- Return updated audit response DTO

### Step 5: Implement retrieval methods
- Implement `get_audit(audit_id: UUID) -> Optional[SupplierAuditResponseDTO]`
  - Get audit by ID from repository
  - Return DTO or None if not found
- Implement `get_supplier_audits(supplier_id: UUID, page: int, limit: int) -> SupplierAuditListResponseDTO`
  - Get audits by supplier ID with pagination
  - Return list response DTO with pagination metadata

### Step 6: Implement reprocess_audit method
- Implement `reprocess_audit(audit_id: UUID) -> SupplierAuditResponseDTO`
- Retrieve audit record
- Raise ValueError if not found
- Reset extraction fields (clear old results)
- Update status to 'pending'
- Call `process_audit()` to re-run extraction
- Return updated audit response DTO

### Step 7: Implement update_supplier_latest_audit method
- Implement `update_supplier_latest_audit(supplier_id: UUID, audit_id: UUID) -> bool`
- Update the supplier's `latest_audit_id` field to point to the most recent audit
- Use supplier_repository to perform the update

### Step 8: Create API routes file
- Create `apps/Server/app/api/audit_routes.py`
- Create APIRouter with tags=["Supplier Audits"]
- Add file size limit constant: `MAX_AUDIT_FILE_SIZE_BYTES = 25 * 1024 * 1024`  # 25MB
- Add allowed extensions: `ALLOWED_EXTENSIONS = {".pdf"}`

### Step 9: Implement upload endpoint
- Implement `POST /suppliers/{supplier_id}/audits`
- Accept `UploadFile` for file and query params for `audit_type`
- Validate file extension is PDF
- Validate file size <= 25MB
- Save file temporarily (for now, use temp storage with data URI or local path)
- Call `audit_service.upload_audit()`
- Schedule background task for `audit_service.process_audit()`
- Return `SupplierAuditResponseDTO` with 201 status
- Require authentication with `require_roles(["admin", "manager", "user"])`

### Step 10: Implement retrieval endpoints
- Implement `GET /suppliers/{supplier_id}/audits` - List supplier audits
  - Accept pagination params (page, limit)
  - Call `audit_service.get_supplier_audits()`
  - Return `SupplierAuditListResponseDTO`
- Implement `GET /suppliers/{supplier_id}/audits/{audit_id}` - Get single audit
  - Validate audit belongs to supplier
  - Call `audit_service.get_audit()`
  - Return `SupplierAuditResponseDTO` or 404

### Step 11: Implement reprocess endpoint
- Implement `POST /suppliers/{supplier_id}/audits/{audit_id}/reprocess`
- Validate audit belongs to supplier
- Call `audit_service.reprocess_audit()` as background task
- Return `SupplierAuditResponseDTO` with updated status

### Step 12: Implement delete endpoint
- Implement `DELETE /suppliers/{supplier_id}/audits/{audit_id}`
- Validate audit belongs to supplier
- Require `require_roles(["admin", "manager"])`
- Call repository delete method
- Return 204 No Content

### Step 13: Register routes in main.py
- Import `router as audit_router` from `app.api.audit_routes`
- Add `app.include_router(audit_router, prefix="/api/suppliers")` (nested under suppliers)
- Note: Routes will be `/api/suppliers/{supplier_id}/audits/...`

### Step 14: Create unit tests for audit service
- Create `apps/Server/tests/test_audit_service.py`
- Test `upload_audit()` creates audit record with pending status
- Test `process_audit()` updates status and extracts data (mock AI client)
- Test `get_audit()` returns correct audit or None
- Test `get_supplier_audits()` returns paginated results
- Test `reprocess_audit()` resets and re-extracts
- Test error handling when AI extraction fails

### Step 15: Run validation commands
- Run ruff linter to check Python code quality
- Run pytest to ensure all tests pass
- Verify imports work correctly
- Test API endpoints manually with sample PDF

## Testing Strategy

### Unit Tests
- Test audit repository CRUD operations with mocked database connections
- Test audit service methods with mocked repository and AI clients
- Test extraction prompt parsing with sample AI responses
- Test status transitions (pending → processing → completed/failed)
- Test error handling when AI service unavailable

### Edge Cases
- Test upload of files at exactly 25MB limit
- Test upload of non-PDF files (should reject)
- Test extraction of corrupt or encrypted PDFs
- Test extraction when AI returns incomplete/malformed JSON
- Test reprocessing already-completed audits
- Test getting audits for non-existent supplier
- Test concurrent extraction requests for same audit

## Acceptance Criteria
- [ ] Can upload PDF audit documents up to 25MB
- [ ] Audit record created with 'pending' status on upload
- [ ] AI extraction runs as background task
- [ ] AI extracts all 12 required fields from audit PDF
- [ ] Extraction status transitions: pending → processing → completed/failed
- [ ] Can track extraction status via GET endpoint
- [ ] Can reprocess failed extractions
- [ ] Can list all audits for a supplier with pagination
- [ ] Can delete audit documents (admin/manager only)
- [ ] Handles various audit PDF formats gracefully (null for missing fields)
- [ ] All Python files pass ruff linting
- [ ] All unit tests pass

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && .venv/bin/ruff check .` - Run ruff linter to check Python code quality
- `cd apps/Server && .venv/bin/ruff check app/services/audit_service.py app/repository/audit_repository.py app/api/audit_routes.py` - Specifically validate the new files
- `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` - Run Server tests to validate zero regressions
- `cd apps/Server && python -c "from app.services.audit_service import audit_service; print('AuditService imports successfully')"` - Verify service can be imported
- `cd apps/Server && python -c "from app.repository.audit_repository import audit_repository; print('AuditRepository imports successfully')"` - Verify repository can be imported
- `cd apps/Server && python -c "from app.api.audit_routes import router; print('Audit routes import successfully')"` - Verify routes can be imported

## Notes

- **File Storage Strategy**: For V1, store the document URL as provided (assumes external storage like S3/R2/Supabase Storage). The `upload_audit` method accepts a `document_url` parameter rather than handling file storage directly. File upload to cloud storage should be handled by the API layer or a separate storage service.

- **PDF Processing**: The service uses Claude's vision capabilities to process PDF pages. For very large PDFs (70+ pages), consider:
  - Processing only the first 10-20 pages where key information is typically found
  - Implementing chunked processing if needed in future iterations
  - Using the `pdf2image` library to convert PDF pages to images

- **AI Timeout**: Set appropriate timeouts for large document processing. The existing `EXTRACTION_TIMEOUT_SECONDS` setting (default 60s) may need to be increased for audit documents.

- **Background Processing**: Use FastAPI's `BackgroundTasks` for async processing. The upload endpoint returns immediately with the audit record, and extraction runs in the background.

- **Dependencies**: This feature depends on Issue #79 (database schema and DTOs) being completed first. The `supplier_audits` table and related DTOs must exist.

- **Future Enhancements** (out of scope for this issue):
  - AI classification logic (Type A/B/C) - Issue #81
  - Manual classification override - Issue #81
  - Frontend UI for audit upload and display - Future issues
  - Direct file upload to cloud storage - Can be added later

- **Library Requirements**: The `pdf2image` library requires `poppler-utils` to be installed on the system. Add a note in requirements.txt or deployment docs.
