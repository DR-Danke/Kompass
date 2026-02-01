# Feature: Enhanced PDF Generation Service

## Metadata
issue_number: `31`
adw_id: `5d18ddf7`
issue_json: `{"number":31,"title":"[Kompass] Phase 12B: PDF Generation Service","body":"## Context\n**Current Phase:** Phase 12 of 13 - Dashboard & Export\n**Current Issue:** KP-031 (Issue 31 of 33)\n**Parallel Execution:** YES - Runs IN PARALLEL with KP-030.\n\n---\n\n## Description\nImplement PDF generation for portfolios and quotations.\n\n## Requirements\n\n### File: apps/Server/app/services/pdf_service.py\n\n#### Portfolio PDF\n- Cover page with portfolio name, niche, Kompass branding\n- Product pages with image, name, SKU, description\n- QR code linking to digital version\n- Page numbers\n\n#### Quotation PDF (Proforma Invoice)\n- Company header with logo\n- Client information\n- Quotation number, date, validity\n- Product table with images, quantities, prices\n- Pricing breakdown\n- Payment terms\n- Footer with contact info\n\n### Templates\n- Use WeasyPrint or ReportLab\n- HTML/CSS templates for layouts\n- Company branding assets\n\n### File: apps/Server/app/api/pdf_routes.py\n- GET /api/portfolios/{id}/pdf - Generate portfolio PDF\n- GET /api/quotations/{id}/pdf - Generate proforma PDF\n\n## Acceptance Criteria\n- [ ] Portfolio PDF generating correctly\n- [ ] Quotation PDF generating correctly\n- [ ] Branding applied\n- [ ] QR codes working\n- [ ] Performance acceptable (<10 seconds)"}`

## Feature Description
Enhance the existing PDF generation functionality for portfolios and quotations with professional-grade features including cover pages, branding, product images, QR codes, and page numbers. The current implementation in `portfolio_service.py` and `quotation_service.py` uses ReportLab for basic PDF generation. This feature will create a dedicated `pdf_service.py` module with enhanced templates and functionality.

## User Story
As a Kompass user (admin, manager, or sales representative)
I want to generate professional PDF documents for portfolios and quotations with branding, images, and QR codes
So that I can share polished, branded documents with clients that include all relevant product and pricing information

## Problem Statement
The current PDF generation implementation provides basic table-based outputs without professional branding, cover pages, product images, QR codes, or page numbers. This limits the usefulness of exported documents for client-facing presentations and formal quotations.

## Solution Statement
Create a dedicated `pdf_service.py` module that enhances PDF generation with:
1. **Portfolio PDFs**: Cover page with Kompass branding, product pages with images, QR codes linking to digital versions, page numbers
2. **Quotation PDFs (Proforma Invoice)**: Professional header with logo, client information, product table with images, pricing breakdown, payment terms, footer with contact info

The solution will leverage ReportLab (already installed) for PDF generation and add the `qrcode` library for QR code generation. The existing routes (`/api/portfolios/{id}/export/pdf` and `/api/quotations/{id}/export/pdf`) will be updated to use the new enhanced service.

## Relevant Files
Use these files to implement the feature:

### Existing Files to Modify
- `apps/Server/app/services/portfolio_service.py` - Contains existing `generate_pdf()` method (lines 711-855) that will be refactored to use the new pdf_service
- `apps/Server/app/services/quotation_service.py` - Contains existing `generate_pdf()` method (lines 1013-1246) that will be refactored to use the new pdf_service
- `apps/Server/requirements.txt` - Add `qrcode[pil]` dependency for QR code generation

### Existing Files for Reference (patterns and DTOs)
- `apps/Server/app/api/portfolio_routes.py` - Contains the `/export/pdf` endpoint (lines 511-553)
- `apps/Server/app/api/quotation_routes.py` - Contains the `/export/pdf` endpoint (lines 427-469)
- `apps/Server/app/models/kompass_dto.py` - DTOs for portfolios and quotations
- `apps/Server/app/repository/kompass_repository.py` - Repository for fetching data

### Test Files for Reference
- `apps/Server/tests/api/test_portfolio_routes.py` - Existing PDF export tests (lines 613-656)
- `apps/Server/tests/services/test_portfolio_service.py` - Service tests
- `apps/Server/tests/services/test_quotation_service.py` - Service tests

### Documentation Files
- `.claude/commands/test_e2e.md` - E2E test runner instructions
- `.claude/commands/e2e/test_portfolio_builder.md` - Existing portfolio E2E tests (includes PDF preview step)
- `.claude/commands/e2e/test_quotation_creator.md` - Existing quotation E2E tests (includes PDF preview step)

### New Files

- `apps/Server/app/services/pdf_service.py` - New dedicated PDF generation service with enhanced features
- `apps/Server/tests/services/test_pdf_service.py` - Unit tests for the new PDF service

## Implementation Plan

### Phase 1: Foundation
1. Add `qrcode[pil]` dependency to requirements.txt
2. Create the `pdf_service.py` module with base classes and utility functions
3. Implement color schemes, fonts, and branding constants

### Phase 2: Core Implementation
1. Implement enhanced Portfolio PDF generation:
   - Cover page with portfolio name, niche, and Kompass branding
   - Product listing pages with optional product images
   - QR code linking to the portfolio share URL
   - Page numbers on all pages
2. Implement enhanced Quotation PDF generation (Proforma Invoice):
   - Professional header with company logo placeholder
   - Client information section
   - Quotation metadata (number, date, validity)
   - Product table with quantities and prices
   - Pricing breakdown section (subtotal, freight, insurance, total)
   - Payment terms section
   - Footer with contact information

### Phase 3: Integration
1. Refactor `portfolio_service.py` to use the new `pdf_service`
2. Refactor `quotation_service.py` to use the new `pdf_service`
3. Ensure existing API routes continue to work seamlessly
4. Add unit tests for the new PDF service

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add QR Code Dependency
- Add `qrcode[pil]>=7.4.0` to `apps/Server/requirements.txt`
- Install the new dependency

### Step 2: Create PDF Service Module
- Create `apps/Server/app/services/pdf_service.py`
- Define branding constants (colors, fonts, margins)
- Create utility functions:
  - `_create_qr_code(url: str) -> bytes` - Generate QR code image
  - `_add_page_number(canvas, doc, page_num, total_pages)` - Page number footer
  - `_create_header(elements, title, subtitle)` - Reusable header component
  - `_create_footer(elements, contact_info)` - Reusable footer component

### Step 3: Implement Portfolio PDF Generation
- Create `PortfolioPDFGenerator` class in `pdf_service.py`
- Implement `generate_cover_page()`:
  - Portfolio name as main title
  - Niche name as subtitle
  - Kompass branding (logo placeholder, colors)
  - Generation date
- Implement `generate_product_pages()`:
  - Product listing with name, SKU, description
  - Optional product image placeholders
  - Sort order preserved
- Implement `generate_qr_code_section()`:
  - QR code linking to share URL (constructed from portfolio ID)
  - Caption text
- Implement `generate()` method combining all sections with page numbers

### Step 4: Implement Quotation PDF Generation (Proforma Invoice)
- Create `QuotationPDFGenerator` class in `pdf_service.py`
- Implement `generate_header()`:
  - Company logo placeholder
  - Document title "PROFORMA INVOICE"
  - Quotation number and date
- Implement `generate_client_section()`:
  - Client name and contact details
  - Billing information placeholder
- Implement `generate_items_table()`:
  - Product name, SKU, quantity, unit, unit price, line total
  - Alternating row colors
  - Table styling
- Implement `generate_pricing_breakdown()`:
  - Subtotal, freight, insurance, other costs
  - Discount (if applicable)
  - Grand total (highlighted)
- Implement `generate_terms_section()`:
  - Payment terms
  - Terms and conditions
  - Validity period
- Implement `generate_footer()`:
  - Contact information
  - Generation timestamp
- Implement `generate()` method combining all sections with page numbers

### Step 5: Integrate PDF Service with Portfolio Service
- Import `pdf_service` in `portfolio_service.py`
- Refactor `generate_pdf()` method to use `PortfolioPDFGenerator`
- Construct share URL for QR code (use settings for base URL)
- Maintain backward compatibility with existing API

### Step 6: Integrate PDF Service with Quotation Service
- Import `pdf_service` in `quotation_service.py`
- Refactor `generate_pdf()` method to use `QuotationPDFGenerator`
- Maintain backward compatibility with existing API

### Step 7: Create Unit Tests for PDF Service
- Create `apps/Server/tests/services/test_pdf_service.py`
- Test `PortfolioPDFGenerator`:
  - Test PDF generation with sample data
  - Test cover page contains portfolio name
  - Test QR code generation
  - Test page numbers are present
- Test `QuotationPDFGenerator`:
  - Test PDF generation with sample quotation
  - Test header contains quotation number
  - Test items table formatting
  - Test pricing breakdown
  - Test footer content
- Test utility functions:
  - QR code generation
  - Page numbering

### Step 8: Run Validation Commands
- Execute all validation commands to ensure zero regressions

## Testing Strategy

### Unit Tests
- `test_pdf_service.py`:
  - `test_portfolio_pdf_generation_returns_bytes` - Verify PDF bytes are returned
  - `test_portfolio_pdf_contains_portfolio_name` - Check portfolio name in PDF
  - `test_portfolio_pdf_has_qr_code` - Verify QR code is generated
  - `test_quotation_pdf_generation_returns_bytes` - Verify PDF bytes are returned
  - `test_quotation_pdf_contains_quotation_number` - Check quotation number
  - `test_quotation_pdf_has_items_table` - Verify items table is present
  - `test_quotation_pdf_has_pricing_breakdown` - Check pricing section
  - `test_qr_code_generation` - Test QR code utility function

### Edge Cases
- Empty portfolio (no items) - Should still generate valid PDF with empty table message
- Quotation with no line items - Should generate PDF with empty items note
- Very long product names - Should truncate or wrap appropriately
- Missing optional fields (description, notes) - Should handle None values gracefully
- Large number of items (50+) - Should handle pagination across multiple pages
- Special characters in text - Should escape properly for PDF
- Missing client information - Should show placeholder or "N/A"

## Acceptance Criteria
- [ ] Portfolio PDF includes cover page with portfolio name, niche, and Kompass branding
- [ ] Portfolio PDF includes product pages with name, SKU, and description for each item
- [ ] Portfolio PDF includes QR code linking to digital version (share URL)
- [ ] Portfolio PDF includes page numbers on all pages
- [ ] Quotation PDF includes company header with document title
- [ ] Quotation PDF includes client information section
- [ ] Quotation PDF includes quotation number, date, and validity period
- [ ] Quotation PDF includes product table with quantities and prices
- [ ] Quotation PDF includes pricing breakdown (subtotal, freight, insurance, total)
- [ ] Quotation PDF includes terms and conditions section
- [ ] Quotation PDF includes footer with contact information and timestamp
- [ ] PDF generation completes in under 10 seconds for typical documents
- [ ] All existing API routes continue to work without changes
- [ ] All existing tests pass without modification
- [ ] New unit tests provide adequate coverage for the PDF service

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Install dependencies (if not already done)
cd apps/Server && pip install -r requirements.txt

# Run all Server tests including new PDF service tests
cd apps/Server && .venv/bin/pytest tests/ -v --tb=short

# Run specific PDF service tests
cd apps/Server && .venv/bin/pytest tests/services/test_pdf_service.py -v --tb=short

# Run portfolio route tests (includes PDF export tests)
cd apps/Server && .venv/bin/pytest tests/api/test_portfolio_routes.py -v --tb=short

# Run quotation route tests
cd apps/Server && .venv/bin/pytest tests/api/test_quotation_routes.py -v --tb=short

# Run ruff linting
cd apps/Server && .venv/bin/ruff check .

# Run Client type check
cd apps/Client && npm run typecheck

# Run Client build
cd apps/Client && npm run build
```

## Notes

### Library Choice
- **ReportLab**: Already installed and used in current implementation. Provides robust PDF generation capabilities.
- **qrcode[pil]**: Standard Python library for QR code generation. The `[pil]` extra provides Pillow-based rendering which integrates well with ReportLab.

### Branding Considerations
- Logo is a placeholder until actual Kompass branding assets are available
- Color scheme uses Material Design blue (`#1976d2`) as primary color to match frontend
- Font defaults to Helvetica (built into ReportLab) for cross-platform compatibility

### Performance
- PDF generation should complete in <10 seconds as per acceptance criteria
- For large documents, consider streaming response if needed
- QR codes are generated in-memory without file I/O

### Share URL Construction
- Portfolio share URL format: `{FRONTEND_URL}/portfolios/share/{token}`
- Token is generated via existing `get_share_token()` method
- If no share token exists, generate one during PDF creation

### Future Enhancements (Out of Scope)
- Actual company logo integration (requires asset upload feature)
- Product image embedding (requires image storage infrastructure)
- Custom PDF templates per client/niche
- Multiple language support for PDF content
