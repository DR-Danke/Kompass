# Audit Service with AI Extraction for Factory Audits

**ADW ID:** e8bfdee4
**Date:** 2026-02-04
**Specification:** specs/issue-80-adw-e8bfdee4-audit-service-ai-extraction.md

## Overview

This feature implements a complete audit service for handling supplier factory audit PDF documents. The service uses Claude AI's vision capabilities to automatically extract key supplier qualification data from 70+ page audit PDFs, enabling faster supplier qualification decisions without manual document review.

## What Was Built

- Complete audit repository for `supplier_audits` table CRUD operations
- Audit service with AI-powered PDF extraction using Claude or OpenAI vision APIs
- REST API endpoints for audit upload, retrieval, reprocessing, and deletion
- Background task processing for large PDF documents
- Extraction status tracking (pending -> processing -> completed/failed)
- Comprehensive unit tests with mocked AI clients

## Technical Implementation

### Files Modified

- `apps/Server/main.py`: Added audit router registration
- `apps/Server/app/services/audit_service.py`: New service implementing AI extraction logic
- `apps/Server/app/repository/audit_repository.py`: New repository for database operations
- `apps/Server/app/api/audit_routes.py`: New API routes for audit endpoints
- `apps/Server/tests/test_audit_service.py`: Unit tests for the audit service

### Key Changes

- **AI Extraction**: Uses Claude (claude-sonnet-4-20250514) or OpenAI (gpt-4o) vision APIs to analyze PDF pages converted to images
- **PDF Processing**: Converts PDF pages to JPEG images using pdf2image library, limited to first 20 pages at 150 DPI
- **Background Processing**: File upload returns immediately while AI extraction runs asynchronously via FastAPI BackgroundTasks
- **Status Tracking**: Audits transition through `pending -> processing -> completed/failed` states
- **Data Extracted**: supplier_type, employee_count, factory_area_sqm, production_lines_count, markets_served, certifications, positive_points, negative_points, products_verified, audit_date, inspector_name

## How to Use

1. **Upload an audit PDF**
   ```bash
   POST /api/suppliers/{supplier_id}/audits
   Content-Type: multipart/form-data
   file: <pdf_file>
   audit_type: factory_audit | container_inspection
   ```

2. **Check extraction status**
   ```bash
   GET /api/suppliers/{supplier_id}/audits/{audit_id}
   ```
   Response includes `extraction_status`: pending, processing, completed, or failed

3. **List all audits for a supplier**
   ```bash
   GET /api/suppliers/{supplier_id}/audits?page=1&limit=20
   ```

4. **Reprocess a failed extraction**
   ```bash
   POST /api/suppliers/{supplier_id}/audits/{audit_id}/reprocess
   ```
   Requires admin or manager role

5. **Delete an audit**
   ```bash
   DELETE /api/suppliers/{supplier_id}/audits/{audit_id}
   ```
   Requires admin or manager role

## Configuration

The audit service uses existing AI configuration from `app/config/settings.py`:

- `ANTHROPIC_API_KEY`: API key for Claude (preferred)
- `OPENAI_API_KEY`: API key for OpenAI (fallback)
- `EXTRACTION_AI_PROVIDER`: Preferred provider ("anthropic" or "openai")

File constraints:
- Maximum file size: 25MB
- Allowed extensions: PDF only
- Maximum pages processed: 20 pages per PDF

## Testing

Run the audit service tests:
```bash
cd apps/Server
.venv/bin/pytest tests/test_audit_service.py -v
```

Verify imports:
```bash
cd apps/Server
python -c "from app.services.audit_service import audit_service; print('OK')"
python -c "from app.repository.audit_repository import audit_repository; print('OK')"
python -c "from app.api.audit_routes import router; print('OK')"
```

## Notes

- **Dependencies**: Requires `pdf2image` library which depends on `poppler-utils` system package
- **File Storage**: Current implementation uses local temp files with `file://` URLs. Production deployments should use cloud storage (S3/R2/Supabase Storage)
- **Large PDFs**: Only first 20 pages are processed to balance extraction quality with API costs
- **Future Work**: Issue #81 will add AI classification logic (Type A/B/C) based on extracted data
