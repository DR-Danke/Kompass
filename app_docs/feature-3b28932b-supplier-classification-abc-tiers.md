# Supplier Classification ABC Tiers

**ADW ID:** 3b28932b
**Date:** 2026-02-04
**Specification:** specs/issue-81-adw-3b28932b-supplier-classification-abc-tiers.md

## Overview

This feature adds an AI-driven supplier classification system that analyzes extracted audit data and recommends A/B/C tier ratings. The system uses a transparent scoring algorithm to generate classifications with human-readable reasoning, allows manual overrides with required notes, and automatically updates supplier certification status when classifications are finalized.

## What Was Built

- Score-based classification algorithm analyzing 6 audit data factors
- Human-readable reasoning generation explaining classification decisions
- Manual override capability with required notes for audit trail
- Automatic supplier certification status synchronization
- Two new API endpoints for classification and override operations
- Comprehensive unit tests covering all classification scenarios

## Technical Implementation

### Files Modified

- `apps/Server/app/services/audit_service.py`: Added `classify_supplier()`, `override_classification()`, and `_update_supplier_certification()` methods
- `apps/Server/app/repository/audit_repository.py`: Added `update_classification()` and `update_manual_classification()` repository methods
- `apps/Server/app/repository/kompass_repository.py`: Added `update_certification_status()` method to SupplierRepository
- `apps/Server/app/api/audit_routes.py`: Added POST `/classify` and PUT `/classification` endpoints

### New Files

- `apps/Server/tests/test_classification.py`: Dedicated unit tests for classification logic (573 lines)

### Key Changes

- **Scoring Algorithm**: 6-factor scoring system with clear point values:
  - Supplier type: manufacturer (+3), trader (+1), unknown (0)
  - Certifications: 3+ (+2), 1-2 (+1), 0 (0)
  - Production lines: 3+ (+1), 1-2 (+0.5), 0 (0)
  - Negative points: 0 (+1), 1-2 (0), 3+ (-1)
  - Positive points: 3+ (+1), 1-2 (+0.5), 0 (0)
  - South America market experience: >0% (+0.5)

- **Classification Thresholds**:
  - Type A (Preferred): score >= 6
  - Type B (Acceptable): score >= 3 and < 6
  - Type C (Requires verification): score < 3

- **Cascading Updates**: Classification changes automatically update the supplier's `certification_status`, `certified_at`, and `latest_audit_id` fields

## How to Use

### Classify a Supplier Audit

1. Ensure the audit has `extraction_status = 'completed'`
2. Call the classify endpoint:
   ```
   POST /api/suppliers/{supplier_id}/audits/{audit_id}/classify
   ```
3. The response includes the AI classification and reasoning

### Override a Classification

1. Call the override endpoint with classification and required notes:
   ```
   PUT /api/suppliers/{supplier_id}/audits/{audit_id}/classification
   Content-Type: application/json

   {
     "classification": "A",
     "notes": "Upgraded to A due to strong performance history and client recommendation from Hijin"
   }
   ```
2. Notes are mandatory and provide audit trail for business decisions

### API Response

Both endpoints return `SupplierAuditResponseDTO` with classification fields:
- `ai_classification`: The algorithm-generated classification (A/B/C)
- `ai_classification_reason`: Human-readable explanation
- `manual_classification`: Override classification if set (takes precedence)
- `classification_notes`: Notes explaining manual override

## Configuration

No additional configuration required. The scoring weights and thresholds are defined in `audit_service.py` and can be adjusted if business requirements change.

## Testing

Run classification tests:
```bash
cd apps/Server && .venv/bin/pytest tests/test_classification.py -v --tb=short
```

Test scenarios covered:
- Type A classification (manufacturer, 3+ certs, minimal negatives)
- Type B classification (moderate scores)
- Type C classification (trader, no certs, many negatives)
- Reasoning generation validation
- Override with valid/invalid inputs
- Supplier certification status synchronization
- Error handling for incomplete/missing audits

## Notes

- Classification is a recommendation tool; human judgment is always required
- Manual overrides take precedence over AI classification for certification status
- The scoring algorithm is designed to be transparent and adjustable
- South America market experience bonus reflects regional business priorities
- All classification changes are logged for audit trail purposes
