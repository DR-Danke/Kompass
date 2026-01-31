# Supplier Service - CRUD & Management

**ADW ID:** 02b42491
**Date:** 2026-01-31
**Specification:** specs/issue-2-adw-02b42491-sdlc_planner-supplier-service-crud.md

## Overview

Implemented a comprehensive supplier service for managing Chinese supplier information in the Kompass Portfolio & Quotation Automation System. This service provides the business logic layer between API routes and the repository layer, handling CRUD operations, filtering, search, and business rule enforcement for suppliers.

## What Was Built

- `SupplierService` class with full CRUD operations (create, read, update, delete)
- Email validation and WeChat ID normalization helpers
- Product count enrichment for supplier retrieval
- Advanced filtering by status, country, and has_products flag
- Multi-field search across name, email, contact phone, and supplier code
- Soft-delete with active products protection (business rule enforcement)
- Extended repository methods for filtering and searching

## Technical Implementation

### Files Modified

- `apps/Server/app/services/supplier_service.py`: New supplier service with all business logic (324 lines)
- `apps/Server/app/repository/kompass_repository.py`: Extended with `count_products_by_supplier()`, `get_all_with_filters()`, and `search()` methods (154 lines added)
- `apps/Server/tests/services/__init__.py`: New test directory init file
- `apps/Server/tests/services/test_supplier_service.py`: Comprehensive unit tests (386 lines)

### Key Changes

- **Email Validation**: Regex-based email format validation using `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$` pattern. Empty emails are allowed as the field is optional.
- **WeChat Normalization**: Contact phone field (used for WeChat IDs) is normalized to lowercase with whitespace stripped.
- **Product Count Enrichment**: `get_supplier_with_product_count()` method joins supplier data with product count from the products table.
- **Has-Products Filter**: Uses SQL `EXISTS`/`NOT EXISTS` subqueries for efficient filtering of suppliers with or without products.
- **Delete Protection**: Before soft-deleting, checks for active products using `product_repository.get_all()` and raises `ValueError` if any exist.
- **Singleton Pattern**: Exports `supplier_service` instance for use by API routes, following existing service patterns.

## How to Use

1. **Import the service**:
   ```python
   from app.services.supplier_service import supplier_service
   ```

2. **Create a supplier**:
   ```python
   from app.models.kompass_dto import SupplierCreateDTO

   request = SupplierCreateDTO(
       name="Shanghai Trading Co.",
       code="STC001",
       contact_email="contact@shanghai-trading.com",
       contact_phone="wechat_id_123",
       country="China"
   )
   supplier = supplier_service.create_supplier(request)
   ```

3. **Get a supplier with product count**:
   ```python
   supplier_dict = supplier_service.get_supplier_with_product_count(supplier_id)
   # Returns dict with 'product_count' field
   ```

4. **List suppliers with filters**:
   ```python
   from app.models.kompass_dto import SupplierStatus

   result = supplier_service.list_suppliers(
       status=SupplierStatus.active,
       country="China",
       has_products=True,
       page=1,
       limit=20
   )
   # Returns SupplierListResponseDTO with items and pagination
   ```

5. **Search suppliers**:
   ```python
   results = supplier_service.search_suppliers("shanghai")
   # Searches name, email, contact_phone, and code fields
   ```

6. **Delete a supplier** (soft delete):
   ```python
   success = supplier_service.delete_supplier(supplier_id)
   # Raises ValueError if supplier has active products
   ```

## Configuration

No additional configuration required. The service uses existing database connection settings from `app.config.database`.

## Testing

Run unit tests for the supplier service:

```bash
cd apps/Server && .venv/bin/pytest tests/services/test_supplier_service.py -v --tb=short
```

Test coverage includes:
- Email validation (valid, invalid, empty)
- WeChat ID normalization (lowercase, whitespace stripping)
- Create supplier (success, validation failure, repository failure)
- Get supplier (found, not found)
- Get supplier with product count
- List suppliers with various filter combinations
- Update supplier (success, validation, not found)
- Delete supplier (success, not found, blocked by active products)
- Search suppliers (matching, no matches, empty query)

## Notes

- **WeChat ID Storage**: The `contact_phone` field can store WeChat IDs. WeChat IDs are normalized to lowercase during create/update operations.
- **Soft Delete**: Delete operations set the supplier status to 'inactive' rather than hard deleting records.
- **Business Rule**: Cannot delete a supplier that has active products. This protects referential integrity.
- **Logging**: Uses the project's logging convention: `print(f"INFO/WARN/ERROR [SupplierService]: ...")`
- **Future Integration**: This service will be consumed by Phase 3 API Routes (`/api/suppliers/*` endpoints).
