# Feature: Data Extraction API Routes

## Metadata
issue_number: `9`
adw_id: `1ee9c0ae`
issue_json: `{"number":9,"title":"[Kompass] Phase 3D: Data Extraction API Routes","body":"Implement FastAPI routes for AI-powered data extraction."}`

## Feature Description
Implement FastAPI routes for AI-powered data extraction functionality. These routes expose the existing ExtractionService (built in Phase 2D, KP-005) to allow clients to upload files (PDF, Excel, images) for automatic product data extraction, track asynchronous extraction jobs, retrieve results, and confirm imports into the product database. Additionally, provide endpoints for single image processing (background removal) and HS code suggestions.

The routes implement an asynchronous job-based pattern where file uploads create extraction jobs that process in the background, allowing clients to poll for progress and results.

## User Story
As a product manager or importer
I want to upload supplier catalogs and price lists for automatic data extraction
So that I can quickly import product data without manual data entry

## Problem Statement
The ExtractionService (Phase 2D) provides powerful AI-powered extraction capabilities, but there's no way for frontend applications to access these features. Users need HTTP endpoints to upload files, monitor extraction progress, review extracted products, and confirm imports into the system.

## Solution Statement
Create a comprehensive set of FastAPI routes at `/api/extract/*` that:
1. Accept file uploads via multipart/form-data and create extraction jobs
2. Track job status and progress using an in-memory job store (with UUID-based job IDs)
3. Return extracted products once processing completes
4. Allow users to confirm and import extracted products into the product database
5. Provide single-endpoint access to image processing (background removal) and HS code suggestion

## Relevant Files
Use these files to implement the feature:

**Core Dependencies:**
- `apps/Server/app/services/extraction_service.py` - The ExtractionService singleton that provides all extraction logic (AI extraction, PDF/Excel/Image processing, HS code suggestion, background removal)
- `apps/Server/app/models/extraction_dto.py` - Existing DTOs (ExtractedProduct, ExtractionResult, HsCodeSuggestion, ImageProcessingResult, ImageOperation)
- `apps/Server/app/services/product_service.py` - ProductService for importing confirmed products
- `apps/Server/app/models/kompass_dto.py` - ProductCreateDTO and related DTOs for product import

**API Pattern References:**
- `apps/Server/app/api/auth_routes.py` - Reference for route structure, error handling, and response patterns
- `apps/Server/app/api/dependencies.py` - Authentication dependency (get_current_user)
- `apps/Server/app/api/rbac_dependencies.py` - Role-based access control (require_roles)

**Application Entry:**
- `apps/Server/main.py` - Route registration

### New Files
- `apps/Server/app/api/extraction_routes.py` - New extraction API routes
- `apps/Server/app/models/extraction_job_dto.py` - New DTOs for extraction jobs (job status, upload request/response, confirm request)
- `apps/Server/tests/test_extraction_routes.py` - Unit tests for the extraction routes

## Implementation Plan

### Phase 1: Foundation
Create the data models and DTOs needed for the extraction job workflow:
- ExtractionJobStatus enum (pending, processing, completed, failed)
- ExtractionJob DTO with job_id, status, progress, file info, results, and errors
- Upload response DTO with job_id
- Confirm import request/response DTOs
- In-memory job store with basic CRUD operations

### Phase 2: Core Implementation
Implement the six API endpoints:
1. POST `/api/extract/upload` - File upload with job creation
2. GET `/api/extract/{job_id}` - Job status polling
3. GET `/api/extract/{job_id}/results` - Get extracted products
4. POST `/api/extract/{job_id}/confirm` - Confirm and import products
5. POST `/api/extract/image/process` - Single image background removal
6. POST `/api/extract/hs-code/suggest` - HS code suggestion

### Phase 3: Integration
- Register routes in main.py
- Add authentication and RBAC
- Add comprehensive error handling
- Add file validation (type, size)

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Task 1: Create Extraction Job DTOs
- Create `apps/Server/app/models/extraction_job_dto.py`
- Define `ExtractionJobStatus` enum with values: pending, processing, completed, failed
- Define `ExtractionJobDTO` with fields:
  - job_id: UUID
  - status: ExtractionJobStatus
  - progress: int (0-100)
  - total_files: int
  - processed_files: int
  - extracted_products: List[ExtractedProduct]
  - errors: List[str]
  - created_at: datetime
  - updated_at: datetime
- Define `UploadResponseDTO` with job_id: UUID
- Define `ConfirmImportRequestDTO` with:
  - job_id: UUID
  - product_indices: Optional[List[int]] (if None, import all)
  - supplier_id: UUID (required for product import)
- Define `ConfirmImportResponseDTO` with:
  - imported_count: int
  - failed_count: int
  - errors: List[str]
- Define `HsCodeSuggestRequestDTO` with description: str
- Define `ImageProcessRequestDTO` with image_url: str

### Task 2: Create In-Memory Job Store
- Add job store dictionary to extraction_routes.py (or a separate module if preferred)
- Store jobs keyed by UUID string
- Include helper functions:
  - create_job(total_files: int) -> ExtractionJobDTO
  - get_job(job_id: str) -> Optional[ExtractionJobDTO]
  - update_job_progress(job_id: str, processed: int, products: List, errors: List)
  - complete_job(job_id: str, products: List, errors: List)
  - fail_job(job_id: str, error: str)

### Task 3: Implement Upload Endpoint
- Create `apps/Server/app/api/extraction_routes.py`
- Create router with prefix `/extract` and tags=["Extraction"]
- Implement POST `/upload`:
  - Accept List[UploadFile] via multipart/form-data
  - Validate file types: .pdf, .xlsx, .xls, .docx, .png, .jpg, .jpeg
  - Validate file size: max 20MB per file
  - Create extraction job in "pending" status
  - Save uploaded files to temp directory
  - Use BackgroundTasks to process files asynchronously
  - Return UploadResponseDTO with job_id immediately
- Implement background processing function:
  - Update job status to "processing"
  - Call extraction_service.process_batch() with file paths
  - Update progress during processing
  - Complete job with results when done
  - Clean up temp files

### Task 4: Implement Job Status Endpoint
- Implement GET `/{job_id}`:
  - Validate job_id format (UUID)
  - Return 404 if job not found
  - Return ExtractionJobDTO with current status
  - Include progress percentage, processed/total files

### Task 5: Implement Results Endpoint
- Implement GET `/{job_id}/results`:
  - Validate job_id exists
  - Return 400 if job not completed
  - Return ExtractionJobDTO (or just the extracted_products list)
  - Include all extracted products with confidence scores

### Task 6: Implement Confirm Import Endpoint
- Implement POST `/{job_id}/confirm`:
  - Accept ConfirmImportRequestDTO body
  - Validate job exists and is completed
  - Filter products by product_indices if provided (else import all)
  - For each product, create ProductCreateDTO:
    - Map ExtractedProduct fields to ProductCreateDTO
    - Use supplier_id from request
    - Auto-generate SKU via ProductService
    - Set status to "draft"
  - Call product_service.bulk_create_products()
  - Return ConfirmImportResponseDTO with counts and errors
  - Optionally mark job as "imported" or delete it

### Task 7: Implement Image Process Endpoint
- Implement POST `/image/process`:
  - Accept ImageProcessRequestDTO with image_url
  - Call extraction_service.remove_background(image_url)
  - Return ImageProcessingResult directly

### Task 8: Implement HS Code Suggest Endpoint
- Implement POST `/hs-code/suggest`:
  - Accept HsCodeSuggestRequestDTO with description
  - Validate description is not empty
  - Call extraction_service.suggest_hs_code(description)
  - Return HsCodeSuggestion directly

### Task 9: Add Authentication and RBAC
- Add authentication to all endpoints via Depends(get_current_user)
- Upload, confirm: require_roles(['admin', 'manager', 'user'])
- Status, results: require_roles(['admin', 'manager', 'user'])
- Image process, HS code: require_roles(['admin', 'manager', 'user'])
- Viewer role should NOT have access to upload or confirm

### Task 10: Register Routes in main.py
- Import extraction_routes router
- Add `app.include_router(extraction_router, prefix="/api/extract")`
- Verify routes appear in /docs

### Task 11: Write Unit Tests
- Create `apps/Server/tests/test_extraction_routes.py`
- Test upload endpoint:
  - Valid file upload creates job
  - Invalid file type returns 400
  - Oversized file returns 400
- Test job status endpoint:
  - Valid job_id returns job
  - Invalid job_id returns 404
- Test results endpoint:
  - Completed job returns products
  - Non-completed job returns 400
- Test confirm endpoint:
  - Successful import creates products
  - Partial selection works
  - Non-completed job returns 400
- Test image process endpoint:
  - Returns processed URL
- Test HS code suggest endpoint:
  - Returns suggestion with code and confidence
- Mock extraction_service and product_service for isolation

### Task 12: Run Validation Commands
- Run all validation commands to ensure zero regressions

## Testing Strategy

### Unit Tests
- Test each endpoint in isolation with mocked services
- Test authentication and authorization (401/403 responses)
- Test file validation (type, size limits)
- Test job state transitions (pending -> processing -> completed/failed)
- Test partial product selection in confirm import
- Test error handling for various failure scenarios

### Edge Cases
- Upload with mixed valid/invalid file types
- Job polling during processing (progress updates)
- Confirm import with empty product list
- Confirm import with invalid product indices
- HS code suggestion with empty/very long description
- Image process with invalid URL
- Concurrent job creation and processing
- Job cleanup/expiration (out of scope for MVP but document for future)

## Acceptance Criteria
- [ ] File upload working with .pdf, .xlsx, .xls, .docx, .png, .jpg, .jpeg
- [ ] File size limit (20MB) enforced
- [ ] Async job tracking functional with status updates
- [ ] Extraction results returned with extracted_products array
- [ ] Import confirmation working with product_service integration
- [ ] Partial product selection (by indices) working
- [ ] HS code suggestion working with AI service
- [ ] Image background removal working
- [ ] All endpoints require authentication
- [ ] All tests pass
- [ ] Routes appear in /docs (OpenAPI)

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Run backend tests
cd apps/Server && source .venv/bin/activate && python -m pytest tests/ -v --tb=short

# Run linting
cd apps/Server && source .venv/bin/activate && python -m ruff check .

# Run type checking (if configured)
cd apps/Server && source .venv/bin/activate && python -m mypy app/ --ignore-missing-imports || true

# Verify server starts without errors
cd apps/Server && source .venv/bin/activate && timeout 10 python -m uvicorn main:app --host 0.0.0.0 --port 8000 || true

# Run client type check
cd apps/Client && npm run typecheck

# Run client build
cd apps/Client && npm run build
```

## Notes

### In-Memory Job Store Limitations
The current implementation uses an in-memory dictionary for job storage. This has limitations:
- Jobs are lost on server restart
- Does not scale to multiple server instances
- No automatic job expiration/cleanup

**Future Enhancement:** For production, consider:
- Redis-based job storage
- Database-backed jobs with status tracking
- Celery/RQ for distributed task processing
- Job expiration policy (e.g., delete after 24 hours)

### File Storage
Uploaded files are temporarily stored on the filesystem during processing and deleted after extraction completes. For cloud deployments, consider:
- AWS S3 or GCS for file storage
- Signed upload URLs for direct client uploads
- Async file processing with cloud functions

### Rate Limiting
Consider adding rate limiting for:
- File uploads (prevent abuse)
- AI endpoints (expensive API calls)
- Job creation (prevent DoS)

### Progress Tracking
The current implementation updates progress after each file. For more granular progress:
- Could track per-page progress for PDFs
- Could track per-row progress for Excel
- WebSocket support for real-time updates (future enhancement)
