# Feature: AI Data Extraction Service

## Metadata
issue_number: `5`
adw_id: `dc759ae8`
issue_json: `{"number":5,"title":"[Kompass] Phase 2D: AI Data Extraction Service","body":"..."}`

## Feature Description
Implement an AI-powered data extraction service that automatically extracts product information from supplier catalogs in various formats (PDF, Excel, images). The service leverages Claude or OpenAI Vision APIs to intelligently parse product data including SKU, name, description, pricing, MOQ, dimensions, material, and suggested categories. It also provides image processing capabilities (background removal, resizing) and HS code suggestions for tariff classification.

This is Phase 2D of the Kompass Portfolio & Quotation Automation System and runs in parallel with KP-002, KP-003, and KP-004 backend services.

## User Story
As a sourcing operations manager
I want to upload supplier catalogs (PDF, Excel, images) and have product data automatically extracted
So that I can quickly populate the Biblia General (master product database) without manual data entry

## Problem Statement
Manually entering product data from supplier catalogs is time-consuming and error-prone. Suppliers provide catalogs in various formats (PDF brochures, Excel price lists, individual product images), and extracting structured data from these documents requires significant manual effort. Additionally, determining appropriate HS codes for tariff classification requires specialized knowledge.

## Solution Statement
Build an extraction service that:
1. Processes PDF catalogs using PDF parsing + AI vision for text/image extraction
2. Parses Excel spreadsheets using openpyxl for structured data extraction
3. Extracts product data from images using Claude/OpenAI Vision APIs
4. Provides image processing utilities (background removal via RemoveBG API, resizing)
5. Suggests HS codes using AI based on product descriptions
6. Handles batch processing with error tracking and graceful fallbacks when AI services are unavailable

## Relevant Files
Use these files to implement the feature:

- `apps/Server/app/config/settings.py` - Add new environment variables for AI API keys (ANTHROPIC_API_KEY, OPENAI_API_KEY, REMOVEBG_API_KEY)
- `apps/Server/app/models/kompass_dto.py` - Contains existing DTOs and patterns; will add extraction-specific DTOs
- `apps/Server/app/services/auth_service.py` - Example of service class pattern with singleton instance
- `apps/Server/app/repository/kompass_repository.py` - Reference for repository patterns if needed
- `apps/Server/requirements.txt` - Add new dependencies (anthropic, openai, pypdf2, openpyxl, pillow, httpx)
- `apps/Server/main.py` - Reference for application structure (no changes needed for this service)

### New Files
- `apps/Server/app/services/extraction_service.py` - Main extraction service with all AI-powered extraction functionality
- `apps/Server/app/models/extraction_dto.py` - DTOs for extracted products, extraction results, HS code suggestions
- `apps/Server/tests/test_extraction_service.py` - Unit tests with mocked AI responses

## Implementation Plan
### Phase 1: Foundation
1. Add required dependencies to requirements.txt (anthropic, openai, pypdf2, openpyxl, pillow)
2. Add environment variables to settings.py for API keys
3. Create extraction DTOs (ExtractedProduct, ExtractionResult, HsCodeSuggestion)

### Phase 2: Core Implementation
1. Implement PDF processing with text extraction and page-by-page image extraction
2. Implement Excel parsing with flexible column mapping
3. Implement AI extraction using Claude API with vision capabilities
4. Implement image processing utilities (background removal, resize)
5. Implement HS code suggestion using AI
6. Implement batch processing with error tracking

### Phase 3: Integration
1. Add graceful fallbacks when AI services are unavailable
2. Implement confidence scoring for extracted data
3. Add comprehensive error handling and logging
4. Write unit tests with mocked AI responses

## Step by Step Tasks

### Step 1: Add Dependencies to requirements.txt
- Add `anthropic>=0.7.0` for Claude API integration
- Add `openai>=1.3.0` for OpenAI Vision API (fallback)
- Add `pypdf2>=3.0.0` for PDF text extraction
- Add `openpyxl>=3.1.0` for Excel file parsing
- Add `pillow>=10.0.0` for image processing and resizing
- Note: `httpx>=0.25.0` already exists for HTTP requests (used for RemoveBG API)

### Step 2: Add Environment Variables to Settings
- Add `ANTHROPIC_API_KEY: Optional[str] = None` for Claude API access
- Add `OPENAI_API_KEY: Optional[str] = None` for OpenAI fallback
- Add `REMOVEBG_API_KEY: Optional[str] = None` for background removal service
- Add `EXTRACTION_AI_PROVIDER: str = "anthropic"` to configure preferred AI provider
- Add `EXTRACTION_MAX_RETRIES: int = 3` for API retry configuration
- Add `EXTRACTION_TIMEOUT_SECONDS: int = 60` for API timeout

### Step 3: Create Extraction DTOs
Create `apps/Server/app/models/extraction_dto.py` with:
- `ExtractedProduct` DTO with fields: sku, name, description, price_fob_usd (Optional[Decimal]), moq (Optional[int]), dimensions (Optional[str]), material (Optional[str]), suggested_category (Optional[str]), image_urls (List[str]), confidence_score (float 0-1), raw_text (Optional[str]), source_page (Optional[int])
- `ExtractionResult` DTO with fields: products (List[ExtractedProduct]), total_extracted (int), errors (List[str]), warnings (List[str]), processing_time_seconds (float)
- `HsCodeSuggestion` DTO with fields: code (str), description (str), confidence_score (float), reasoning (Optional[str])
- `ImageProcessingResult` DTO with fields: original_url (str), processed_url (str), operation (str - "remove_bg" | "resize")

### Step 4: Implement Extraction Service Foundation
Create `apps/Server/app/services/extraction_service.py` with:
- `ExtractionService` class following singleton pattern from auth_service.py
- Constructor that initializes AI clients based on available API keys
- Helper method `_get_ai_client()` to return configured Claude or OpenAI client
- Helper method `_is_ai_available()` to check if any AI service is configured

### Step 5: Implement PDF Processing
Add to extraction_service.py:
- `process_pdf(file_path: str) -> List[ExtractedProduct]` method
- Use PyPDF2 to extract text from each page
- For pages with minimal text, convert to image and use AI vision
- Aggregate extracted products from all pages
- Handle encrypted PDFs gracefully (return error)

### Step 6: Implement Excel Processing
Add to extraction_service.py:
- `process_excel(file_path: str) -> List[ExtractedProduct]` method
- Use openpyxl to read worksheets
- Implement flexible column mapping (detect columns by header names)
- Map common header variations: "SKU"/"Reference"/"Code", "Name"/"Product"/"Item", "Price"/"FOB", "MOQ"/"Minimum"
- Skip empty rows and validate required fields

### Step 7: Implement AI Product Data Extraction
Add to extraction_service.py:
- `extract_product_data(image_or_text: str, is_image: bool = False) -> ExtractedProduct` method
- Build structured prompt for Claude/OpenAI to extract product fields
- For images: encode to base64 and use vision capabilities
- For text: use text completion with structured extraction prompt
- Parse AI response into ExtractedProduct DTO
- Calculate confidence score based on number of fields successfully extracted

### Step 8: Implement Image Processing Utilities
Add to extraction_service.py:
- `remove_background(image_url: str) -> str` method
  - Call RemoveBG API if REMOVEBG_API_KEY is configured
  - Return processed image URL or data URI
  - Graceful fallback: return original URL if API unavailable
- `resize_image(image_url: str, width: int, height: int) -> str` method
  - Use Pillow to resize image
  - Maintain aspect ratio
  - Return resized image as data URI or save to temp path
- `find_higher_quality_image(image_url: str) -> Optional[str]` method
  - Placeholder implementation returning None (reverse image search is complex)
  - Add TODO comment for future Google/TinEye integration

### Step 9: Implement HS Code Suggestion
Add to extraction_service.py:
- `suggest_hs_code(product_description: str) -> HsCodeSuggestion` method
- Build prompt with product description and request HS code classification
- Include context about common HS code categories for China imports
- Parse AI response into HsCodeSuggestion DTO
- Fallback: return generic code "9999.99.99" with low confidence if AI unavailable

### Step 10: Implement Batch Processing
Add to extraction_service.py:
- `process_batch(file_paths: List[str]) -> ExtractionResult` method
- Detect file type by extension (.pdf, .xlsx, .xls, .jpg, .jpeg, .png)
- Route to appropriate processor (process_pdf, process_excel, process_image)
- Aggregate results into single ExtractionResult
- Track errors per file, continue processing on failure
- Calculate total processing time

### Step 11: Implement Single Image Processing
Add to extraction_service.py:
- `process_image(file_path: str) -> ExtractedProduct` method
- Read image file and encode to base64
- Call extract_product_data with is_image=True
- Return single ExtractedProduct

### Step 12: Add Graceful Fallbacks
Ensure all methods handle AI unavailability:
- Check `_is_ai_available()` before AI calls
- Return partial results with warnings when AI unavailable
- For PDF/Excel: return raw text extraction without AI enrichment
- Log all fallback scenarios with INFO level

### Step 13: Write Unit Tests
Create `apps/Server/tests/test_extraction_service.py` with:
- Test `process_excel` with sample Excel file (mock file read)
- Test `extract_product_data` with mocked Claude API response
- Test `suggest_hs_code` with mocked AI response
- Test `process_batch` with mixed file types
- Test graceful fallback when AI unavailable (mock API key as None)
- Test `remove_background` with mocked RemoveBG API
- Test error handling for invalid file paths
- Use pytest fixtures and mocking (unittest.mock.patch)

### Step 14: Run Validation Commands
Execute all validation commands to ensure zero regressions.

## Testing Strategy
### Unit Tests
- Mock AI API responses to test extraction logic without real API calls
- Test Excel parsing with various column formats and edge cases
- Test PDF processing with text-heavy and image-heavy documents
- Test batch processing with mixed file types
- Test error handling for missing files, corrupted files, API failures
- Test confidence score calculation

### Edge Cases
- Empty Excel files or PDFs
- PDFs with only images (no extractable text)
- Excel files with non-standard column names
- Very large files (implement size limits)
- Network timeouts when calling AI/RemoveBG APIs
- Invalid image formats
- Unicode characters in product names/descriptions
- Missing optional API keys (partial functionality)

## Acceptance Criteria
- [ ] PDF extraction working: Can extract product data from PDF catalogs with text and/or images
- [ ] Excel parsing working: Can parse Excel files with flexible column mapping
- [ ] Image extraction working: Can extract product data from single product images
- [ ] Background removal functional: Returns processed image URL when API key is configured, graceful fallback otherwise
- [ ] HS code suggestions returning relevant codes: AI-powered suggestions with confidence scores
- [ ] Graceful fallback when AI unavailable: Service returns partial results with warnings instead of errors
- [ ] Unit tests with mocked AI responses: All tests pass with mocked external services

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && source .venv/bin/activate && pip install -r requirements.txt` - Install new dependencies
- `cd apps/Server && source .venv/bin/activate && python -c "from app.models.extraction_dto import *; print('Extraction DTOs imported successfully')"` - Verify DTOs import
- `cd apps/Server && source .venv/bin/activate && python -c "from app.services.extraction_service import extraction_service; print('Extraction service imported successfully')"` - Verify service import
- `cd apps/Server && .venv/bin/ruff check .` - Run linting to verify code quality
- `cd apps/Server && .venv/bin/pytest tests/test_extraction_service.py -v --tb=short` - Run extraction service unit tests
- `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` - Run all Server tests to validate zero regressions

## Notes
- **New Dependencies**: This feature requires adding `anthropic`, `openai`, `pypdf2`, `openpyxl`, and `pillow` to requirements.txt
- **API Keys Optional**: The service should work in degraded mode without AI API keys, returning raw extraction without AI enrichment
- **RemoveBG API**: Free tier allows 50 API calls/month; consider implementing a local fallback using rembg library for high-volume scenarios
- **Parallel Execution**: This issue runs in parallel with KP-002, KP-003, and KP-004. No cross-dependencies within Phase 2.
- **No UI/Frontend**: This is a backend-only service. Frontend integration will be added in later phases.
- **Claude Vision**: Prefer Claude's vision capabilities over OpenAI for consistency with other Anthropic integrations
- **File Size Limits**: Consider implementing file size limits (e.g., 50MB for PDFs, 10MB for images) to prevent memory issues
- **Temporary Files**: When processing uploaded files, use Python's tempfile module for secure temporary storage
