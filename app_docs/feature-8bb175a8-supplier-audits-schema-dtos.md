# Supplier Audits Schema and DTOs

**ADW ID:** 8bb175a8
**Date:** 2026-02-04
**Specification:** specs/issue-79-adw-8bb175a8-supplier-audits-schema-dtos.md

## Overview

This feature adds the foundational database schema and Pydantic DTOs for the Supplier Certification system. It creates a new `supplier_audits` table to store factory audit documents and AI-extracted data, adds certification and pipeline status columns to the existing `suppliers` table, and defines comprehensive DTOs for data validation and API responses.

## What Was Built

- New `supplier_audits` table for storing factory audit documents and extracted data
- Certification and pipeline status columns added to `suppliers` table
- Five new enums: `AuditType`, `ExtractionStatus`, `CertificationStatus`, `SupplierPipelineStatus`, `SupplierType`
- Six new DTOs for supplier audit operations
- Idempotent migration script for existing databases
- Updated main schema.sql for fresh installations

## Technical Implementation

### Files Modified

- `apps/Server/database/schema.sql`: Added `supplier_audits` table, certification columns to `suppliers`, indexes, and triggers
- `apps/Server/app/models/kompass_dto.py`: Added 5 enums and 6 DTOs, updated existing Supplier DTOs with certification fields
- `apps/Server/database/migrations/001_supplier_audits.sql`: New migration script for existing databases

### Key Changes

- **New Table**: `supplier_audits` stores audit documents, AI-extracted factory data (employee count, factory area, certifications, etc.), and classification grades (A/B/C)
- **Suppliers Enhancement**: Added `certification_status`, `pipeline_status`, `latest_audit_id`, and `certified_at` columns
- **Enums**: Define valid values for audit types, extraction status, certification levels, and pipeline stages
- **DTOs**: Full CRUD support with `SupplierAuditCreateDTO`, `SupplierAuditExtractionDTO`, `SupplierAuditClassificationDTO`, `SupplierAuditResponseDTO`, and `SupplierAuditListResponseDTO`
- **Indexes**: Optimized queries on `supplier_id`, `certification_status`, `pipeline_status`, `extraction_status`, and classification fields

### Database Schema

**supplier_audits table fields:**
- Document metadata: `audit_type`, `document_url`, `document_name`, `file_size_bytes`
- Extracted data: `supplier_type`, `employee_count`, `factory_area_sqm`, `production_lines_count`, `markets_served`, `certifications`, `has_machinery_photos`, `positive_points`, `negative_points`, `products_verified`
- Audit metadata: `audit_date`, `inspector_name`
- Processing: `extraction_status`, `extraction_raw_response`, `extracted_at`
- Classification: `ai_classification`, `ai_classification_reason`, `manual_classification`, `classification_notes`

**suppliers table new columns:**
- `certification_status`: `uncertified` | `pending_review` | `certified_a` | `certified_b` | `certified_c`
- `pipeline_status`: `contacted` | `potential` | `quoted` | `certified` | `active` | `inactive`
- `latest_audit_id`: FK to `supplier_audits`
- `certified_at`: Timestamp

## How to Use

1. **Apply migration to existing database:**
   ```bash
   psql $DATABASE_URL -f apps/Server/database/migrations/001_supplier_audits.sql
   ```

2. **For fresh installations:** The schema.sql file already includes the new table and columns.

3. **Import DTOs in Python code:**
   ```python
   from app.models.kompass_dto import (
       AuditType,
       ExtractionStatus,
       CertificationStatus,
       SupplierPipelineStatus,
       SupplierType,
       SupplierAuditCreateDTO,
       SupplierAuditExtractionDTO,
       SupplierAuditClassificationDTO,
       SupplierAuditResponseDTO,
       SupplierAuditListResponseDTO,
   )
   ```

4. **Create a supplier audit:**
   ```python
   audit = SupplierAuditCreateDTO(
       supplier_id=uuid,
       audit_type=AuditType.FACTORY_AUDIT,
       document_url="https://storage.example.com/audits/doc.pdf",
       document_name="Factory_Audit_2026.pdf",
       audit_date=date(2026, 2, 1),
   )
   ```

5. **Update supplier certification status:**
   ```python
   update = SupplierUpdateDTO(
       certification_status=CertificationStatus.CERTIFIED_A,
       pipeline_status=SupplierPipelineStatus.CERTIFIED,
   )
   ```

## Configuration

No additional configuration required. The schema uses existing database patterns:
- UUID primary keys with `gen_random_uuid()`
- Automatic `updated_at` trigger
- `ON DELETE CASCADE` for supplier foreign key
- `ON DELETE SET NULL` for latest_audit_id reference

## Testing

1. **Verify DTOs import:**
   ```bash
   cd apps/Server && python -c "from app.models.kompass_dto import *; print('DTOs import successfully')"
   ```

2. **Run linter:**
   ```bash
   cd apps/Server && .venv/bin/ruff check app/models/kompass_dto.py
   ```

3. **Run existing tests:**
   ```bash
   cd apps/Server && .venv/bin/pytest tests/ -v --tb=short
   ```

## Notes

- This is Phase 1 (data layer only) of the Supplier Certification system
- Future phases will add: API endpoints, AI extraction service, classification logic, and frontend UI
- The migration script is idempotent using `IF NOT EXISTS` patterns
- `suppliers.status` (operational) is separate from `suppliers.pipeline_status` (onboarding workflow)
- Classification grades (A, B, C) can be set by AI (`ai_classification`) or manually (`manual_classification`)
