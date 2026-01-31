# Data Extraction API Routes

**ADW ID:** 1ee9c0ae
**Date:** 2026-01-31
**Specification:** specs/issue-9-adw-1ee9c0ae-sdlc_planner-data-extraction-api-routes.md

## Overview

This feature exposes the existing ExtractionService (built in Phase 2D) via FastAPI routes, enabling clients to upload files (PDF, Excel, images) for AI-powered product data extraction, track asynchronous extraction jobs, retrieve results, and confirm imports into the product database. Additional endpoints support single-image background removal and HS code suggestions.

## What Was Built

- File upload endpoint with async job creation and background processing
- Job status polling endpoint for tracking extraction progress
- Results endpoint for retrieving extracted products from completed jobs
- Confirm import endpoint for importing selected products into the database
- Single-image background removal endpoint
- HS code suggestion endpoint
- In-memory job store with CRUD helper functions
- Comprehensive unit tests with mocked services

## Technical Implementation

### Files Modified

- `apps/Server/app/api/extraction_routes.py`: New extraction API routes (491 lines) with 6 endpoints, file validation, background processing, and in-memory job store
- `apps/Server/app/models/extraction_job_dto.py`: New DTOs (70 lines) for job management including ExtractionJobStatus enum, ExtractionJobDTO, request/response DTOs
- `apps/Server/main.py`: Route registration - added extraction_router at `/api/extract` prefix
- `apps/Server/requirements.txt`: Added python-multipart dependency for file uploads
- `apps/Server/tests/test_extraction_routes.py`: Comprehensive unit tests (517 lines) with mocked services

### Key Changes

- Implemented async job-based pattern where file uploads create extraction jobs that process in the background via FastAPI `BackgroundTasks`
- Added file validation for extensions (.pdf, .xlsx, .xls, .docx, .png, .jpg, .jpeg) and size (max 20MB)
- Created in-memory job store with UUID-based job IDs and helper functions for state management
- Integrated with ExtractionService for AI-powered extraction and ProductService for bulk product imports
- Applied RBAC with `require_roles(['admin', 'manager', 'user'])` on all endpoints - viewer role excluded

## How to Use

1. **Upload files for extraction:**
   ```bash
   POST /api/extract/upload
   Content-Type: multipart/form-data
   Authorization: Bearer <token>

   files: <file1>, <file2>, ...
   ```
   Returns: `{"job_id": "<uuid>"}`

2. **Check job status:**
   ```bash
   GET /api/extract/{job_id}
   Authorization: Bearer <token>
   ```
   Returns job with status (pending/processing/completed/failed), progress (0-100), processed/total file counts

3. **Get extraction results (completed jobs only):**
   ```bash
   GET /api/extract/{job_id}/results
   Authorization: Bearer <token>
   ```
   Returns job with extracted_products array containing product data with confidence scores

4. **Confirm and import products:**
   ```bash
   POST /api/extract/{job_id}/confirm
   Authorization: Bearer <token>
   Content-Type: application/json

   {
     "job_id": "<uuid>",
     "supplier_id": "<supplier-uuid>",
     "product_indices": [0, 2, 5]  // optional, imports all if null
   }
   ```
   Returns: `{"imported_count": 3, "failed_count": 0, "errors": []}`

5. **Remove image background:**
   ```bash
   POST /api/extract/image/process
   Authorization: Bearer <token>
   Content-Type: application/json

   {"image_url": "https://example.com/image.png"}
   ```

6. **Get HS code suggestion:**
   ```bash
   POST /api/extract/hs-code/suggest
   Authorization: Bearer <token>
   Content-Type: application/json

   {"description": "Electric water heater 1500W"}
   ```

## Configuration

No additional environment variables required. The routes use existing configuration:
- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` - for AI extraction (via ExtractionService)
- `REMOVEBG_API_KEY` - for background removal (via ExtractionService)

## Testing

Run the extraction routes tests:
```bash
cd apps/Server
source .venv/bin/activate
python -m pytest tests/test_extraction_routes.py -v --tb=short
```

Tests cover:
- File upload with valid/invalid file types
- File size validation
- Job status retrieval (found/not found)
- Results endpoint (completed/non-completed jobs)
- Confirm import with full/partial product selection
- Image processing and HS code suggestion endpoints
- Authentication and authorization requirements

## Notes

### In-Memory Job Store Limitations
The current implementation uses an in-memory dictionary for job storage:
- Jobs are lost on server restart
- Does not scale to multiple server instances
- No automatic job expiration/cleanup

**Future Enhancement:** Consider Redis-based storage, database-backed jobs with Celery/RQ for distributed processing, or job expiration policies.

### File Storage
Uploaded files are temporarily stored on the filesystem during processing and deleted after extraction completes. For cloud deployments, consider S3/GCS with signed upload URLs.

### API Documentation
Routes appear in the OpenAPI docs at `/docs` under the "Extraction" tag.
