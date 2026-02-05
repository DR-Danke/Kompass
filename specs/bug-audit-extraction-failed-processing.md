# Bug: Audit Extraction Failed - PDF Processing Error

## Metadata
issue_number: ``
adw_id: ``
issue_json: ``

## Bug Description
When uploading a PDF file for the supplier audit process, the system shows "Processing..." but then displays the error: "Extraction failed. The audit document could not be processed." The file uploads successfully, but the AI extraction step fails silently in the background, causing the audit to remain stuck with a `failed` extraction status.

**Expected behavior:** After uploading a factory audit PDF, the system should extract key data (supplier type, employee count, certifications, etc.) and display the audit summary.

**Actual behavior:** Upload succeeds but extraction fails, leaving the user with an error message and no extracted data.

## Problem Statement
The audit extraction process fails because:
1. **Missing dependency**: `pdf2image` package is used in the code but not listed in `requirements.txt`
2. **Invalid URL scheme**: Documents are stored with `file://` URLs, but `httpx` cannot fetch local file URLs
3. **Missing system dependency**: `pdf2image` requires `poppler-utils` to be installed on the system

## Solution Statement
Fix the extraction pipeline by:
1. Adding `pdf2image` to `requirements.txt`
2. Modifying `process_audit()` to read local files directly instead of using httpx for `file://` URLs
3. Adding proper error handling with informative messages
4. Documenting the `poppler-utils` system dependency requirement

## Steps to Reproduce
1. Start the application (`/start`)
2. Navigate to Kompass > Suppliers
3. Click edit on any supplier
4. Go to the "Certification" tab
5. Upload a factory audit PDF file (any valid PDF)
6. Observe "Processing..." appears briefly
7. After ~5-10 seconds, the error message appears: "Extraction failed. The audit document could not be processed."

## Root Cause Analysis
Looking at `apps/Server/app/services/audit_service.py`:

1. **Line 245-286**: `_convert_pdf_to_images()` uses `from pdf2image import convert_from_bytes` but `pdf2image` is not in `requirements.txt`

2. **Line 350-360**: `process_audit()` tries to fetch the document using httpx:
```python
document_url = audit_data["document_url"]  # "file:///tmp/audit_xxx.pdf"
with httpx.Client(timeout=120.0) as client:
    response = client.get(document_url)  # FAILS - httpx doesn't support file:// URLs
```

3. **Line 419-431**: When extraction fails, it catches the exception and sets status to `failed`, but the error is not user-friendly

4. In `audit_routes.py` line 127, the URL is created as:
```python
document_url = f"file://{temp_path}"  # e.g., "file:///tmp/audit_xyz.pdf"
```

## Relevant Files
Use these files to fix the bug:

- `apps/Server/app/services/audit_service.py` - Contains `process_audit()` method that fails when fetching file:// URLs and uses pdf2image
- `apps/Server/app/api/audit_routes.py` - Creates the file:// URL when uploading documents
- `apps/Server/requirements.txt` - Missing `pdf2image` dependency
- `apps/Server/app/config/settings.py` - Contains AI provider configuration (ANTHROPIC_API_KEY, OPENAI_API_KEY)
- `README.md` - May need to document poppler-utils requirement
- `ai_docs/PRD-Supplier-Certification-System.md` - Reference for understanding the feature
- `.claude/commands/test_e2e.md` - Reference for E2E test format
- `.claude/commands/e2e/test_supplier_certification_workflow.md` - Existing E2E test to reference

### New Files
- `.claude/commands/e2e/test_audit_extraction_fix.md` - E2E test to validate the bug fix

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add missing pdf2image dependency
- Open `apps/Server/requirements.txt`
- Add `pdf2image>=2.16.0` to the AI & Data Extraction section
- This package is required for converting PDF pages to images for AI vision processing

### Step 2: Fix file:// URL handling in audit_service.py
- Open `apps/Server/app/services/audit_service.py`
- Locate the `process_audit()` method (around line 328)
- Modify the document fetching logic to handle `file://` URLs by reading the local file directly:
```python
# Before the httpx fetch, check if it's a local file
document_url = audit_data["document_url"]
if document_url.startswith("file://"):
    # Read local file directly
    local_path = document_url[7:]  # Remove "file://" prefix
    with open(local_path, "rb") as f:
        pdf_content = f.read()
else:
    # Fetch from remote URL
    with httpx.Client(timeout=120.0) as client:
        response = client.get(document_url)
        response.raise_for_status()
        pdf_content = response.content
```

### Step 3: Add better error handling and logging
- In `audit_service.py`, enhance the error handling in `process_audit()`:
  - Add specific error message when pdf2image import fails
  - Add specific error message when AI API keys are not configured
  - Add specific error message when poppler is not installed
  - Log the actual exception details for debugging

### Step 4: Update README with system dependency documentation
- Open `README.md` or create `apps/Server/README.md` if needed
- Add a note about the `poppler-utils` system dependency requirement:
  - Ubuntu/Debian: `sudo apt-get install poppler-utils`
  - macOS: `brew install poppler`
  - Windows: Download from poppler releases and add to PATH

### Step 5: Install dependencies and verify fix
- Run `cd apps/Server && pip install pdf2image`
- Ensure `poppler-utils` is installed on the system
- Verify ANTHROPIC_API_KEY or OPENAI_API_KEY is set in `.env`
- Test by uploading a PDF and confirming extraction works

### Step 6: Create E2E test for the fix
- Read `.claude/commands/e2e/test_basic_query.md` and `.claude/commands/e2e/test_supplier_certification_workflow.md`
- Create `.claude/commands/e2e/test_audit_extraction_fix.md` with steps to:
  1. Navigate to Suppliers page
  2. Open a supplier for editing
  3. Go to Certification tab
  4. Upload a test PDF file
  5. Wait for processing to complete (use polling)
  6. Verify extraction summary appears (not the error message)
  7. Verify key fields are populated (supplier type, employee count, etc.)
  8. Take screenshots at each step

### Step 7: Run validation commands
- Execute all validation commands to ensure the fix works and there are no regressions

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

```bash
# Check pdf2image is in requirements
grep -q "pdf2image" apps/Server/requirements.txt && echo "pdf2image found" || echo "pdf2image MISSING"

# Install dependencies
cd apps/Server && pip install -r requirements.txt

# Verify poppler is installed (required by pdf2image)
which pdftoppm || echo "WARNING: poppler-utils not installed"

# Run Server tests to validate no regressions
cd apps/Server && .venv/bin/pytest tests/ -v --tb=short

# Run specific audit service tests
cd apps/Server && .venv/bin/pytest tests/test_audit_service.py -v --tb=short

# Run audit route tests
cd apps/Server && .venv/bin/pytest tests/api/test_audit_routes.py -v --tb=short

# Run Client type check
cd apps/Client && npm run typecheck

# Run Client build
cd apps/Client && npm run build
```

Read `.claude/commands/test_e2e.md`, then read and execute the new E2E test `.claude/commands/e2e/test_audit_extraction_fix.md` to validate the extraction works end-to-end.

## Notes

1. **System dependency**: `pdf2image` requires `poppler-utils` to be installed on the system. This is a system-level dependency that cannot be installed via pip.

2. **AI API Keys**: The extraction requires either `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` to be set in the `.env` file. Without these, extraction will mark as "completed" but with empty data.

3. **File storage**: In production, the document should be uploaded to cloud storage (S3/R2/Supabase Storage) and use a proper HTTP URL. The current `file://` URL approach is only for local development.

4. **New package**: Add `pdf2image>=2.16.0` to requirements.txt

5. **Testing**: When running E2E tests, ensure you have a test PDF file available. The extraction quality depends on the PDF content and AI provider performance.
