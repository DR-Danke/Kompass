# Smart Excel Header Detection, AI Fallback & Confirm Import Fix

**ADW ID:** 5694333e
**Date:** 2026-02-12
**Specification:** specs/issue-121-adw-5694333e-sdlc_planner-smart-excel-header-ai-fallback.md

## Overview

Enhances the Excel extraction pipeline to handle real-world supplier catalog formats from diverse Chinese suppliers. Adds multi-row header scanning (first 10 rows), Spanish/variant column name matching via substring logic, unit-of-measure detection from price headers, AI fallback for unrecognized sheets, and fixes lost fields (material, category_id, unit_of_measure) during the confirm import step.

## What Was Built

- **Multi-row header scanning**: Scans first 10 rows of each Excel sheet, scoring each row by column category matches (SKU, Name, Price, MOQ, Description, Material, Dimensions) to find the best header row
- **Expanded column name matching**: Added Spanish terms (REFERENCIA, PRODUCTO, PRECIO, CANTIDAD, etc.) and format variants (FOB U/P, Unit Price(USD), Price (USD/m2)) with substring/contains matching
- **Unit-of-measure detection**: Parses price column header text for unit hints (m2, pcs, set, kg, etc.) and populates `unit_of_measure` on extracted products
- **AI fallback**: When fewer than 2 column categories match, serializes the first 50 data rows and sends to AI (Anthropic/OpenAI) for structured extraction
- **DTO additions**: `unit_of_measure` field on `ExtractedProduct`, `category_id` field on `ConfirmImportRequestDTO`
- **Confirm import fix**: Maps `unit_of_measure`, appends `material` to description, and passes `category_id` through during product creation

## Technical Implementation

### Files Modified

- `apps/Server/app/services/extraction_service.py`: Core changes — refactored `process_excel()` with new `_find_column()` (substring matching), `_find_best_header_row()` (multi-row scanning), `_detect_unit_of_measure()`, and `_extract_excel_with_ai()` methods. Expanded column candidate lists as class-level constants with Spanish and format variants. (+287 lines)
- `apps/Server/app/models/extraction_dto.py`: Added `unit_of_measure: Optional[str] = Field(default=None, max_length=50)` to `ExtractedProduct`
- `apps/Server/app/models/extraction_job_dto.py`: Added `category_id: Optional[UUID] = None` to `ConfirmImportRequestDTO`
- `apps/Server/app/api/extraction_routes.py`: Updated confirm import endpoint to map `unit_of_measure`, append material to description, and pass `category_id` to `ProductCreateDTO`
- `apps/Server/tests/test_extraction_service.py`: Added `TestSmartHeaderDetection` (10 tests) and `TestExcelAIFallback` (3 tests) classes (+327 lines)
- `apps/Server/tests/test_extraction_routes.py`: Added `TestConfirmImportFieldMapping` class with 4 tests (+142 lines)

### Key Changes

- **Header detection algorithm**: `_find_best_header_row()` iterates rows 0–9, running `_find_column()` for all 7 column categories per row, tracking claimed columns to avoid duplicates. The highest-scoring row becomes the header row; data rows start at `header_row_index + 1`.
- **Substring matching**: `_find_column()` performs two passes — first exact match (lowercased), then substring match where any candidate is contained in the header text. This allows matching headers like `"FOB U/P (USD)"` against candidate `"fob u/p"`.
- **AI fallback threshold**: Activates when the best header row scores < 2 column matches. Checks `_is_ai_available()` first and logs a WARN when triggered. Uses `max_tokens=4096` for table extraction.
- **Unit mapping**: Static dictionary maps keywords in price headers (m2, sqm, pcs, pc, set, pair, kg, ton, meter) to normalized unit values.
- **Backward compatibility**: All existing Excel extraction tests continue to pass. The column matching changes are additive — exact matching still takes priority over substring matching.

## How to Use

1. **Standard Excel import** (no changes needed): Upload Excel files through the Import Wizard as before. Files with headers in row 0 continue to work identically.
2. **Multi-row headers**: Excel files with metadata rows before headers (e.g., company name, dates in rows 0-6, headers in row 7) are now automatically detected.
3. **Spanish catalogs**: Upload supplier catalogs with Spanish column names (REFERENCIA, PRODUCTO, PRECIO, CANTIDAD, etc.) — they are recognized automatically.
4. **Variant formats**: Headers like "FOB U/P (USD)", "Unit Price(USD)", "Price (USD/m2)" are now matched via substring detection.
5. **Unit of measure**: When a price header contains unit hints (e.g., "Price (USD/m2)"), the detected unit is automatically assigned to all products from that sheet.
6. **AI fallback**: For Excel files with completely unrecognizable headers, the system falls back to AI extraction if an AI provider is configured. No user action needed — this is transparent.
7. **Confirm import with category**: When confirming an import, you can now optionally pass a `category_id` to assign all imported products to a specific category.

## Configuration

- **AI provider**: The AI fallback uses the same provider configuration already in place for PDF/image extraction (`ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in environment variables).
- **No new dependencies**: Uses existing `openpyxl` for Excel processing and existing Anthropic/OpenAI clients.
- **No frontend changes required**: The `unit_of_measure` DTO addition is backward-compatible (Optional with default None). The Import Wizard will display the new field if extended.

## Testing

- **Unit tests**: 17 new tests added across two test files
  - `TestSmartHeaderDetection` (10 tests): Header detection at rows 0/3/7, Spanish columns, mixed language, substring matching (FOB U/P, Unit Price(USD)), unit-of-measure detection (m2, pcs, None)
  - `TestExcelAIFallback` (3 tests): AI fallback triggers on low match, skipped when unavailable, not triggered when columns match
  - `TestConfirmImportFieldMapping` (4 tests): unit_of_measure mapping, material-to-description append, category_id passthrough, None material handling
- Run: `cd apps/Server && python -m pytest tests/test_extraction_service.py tests/test_extraction_routes.py -v --tb=short`

## Notes

- **AI model**: Reuses the same models already configured (`claude-sonnet-4-20250514` for Anthropic, `gpt-4o` for OpenAI) with increased `max_tokens=4096` for table extraction
- **Column priority**: Categories are matched in a specific order (SKU, Price, MOQ, Description, Material, Dimensions, Name) to prevent generic candidates like "item" from stealing columns meant for more specific categories
- **Data row limit**: AI fallback only sends the first 50 rows to avoid token limits
- **No frontend impact**: All changes are backend-only. The Import Wizard frontend will automatically benefit from improved extraction without modifications
