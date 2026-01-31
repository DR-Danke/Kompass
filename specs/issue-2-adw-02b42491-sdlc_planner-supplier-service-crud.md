# Feature: Supplier Service - CRUD & Management

## Metadata
issue_number: `2`
adw_id: `02b42491`
issue_json: `{"number":2,"title":"[Kompass] Phase 2A: Supplier Service - CRUD & Management","body":"..."}`

## Feature Description
Implement a comprehensive supplier service for managing Chinese supplier information in the Kompass Portfolio & Quotation Automation System. This service provides the business logic layer between the API routes (Phase 3) and the repository layer (Phase 1), handling CRUD operations, filtering, search, and business rule enforcement for suppliers.

This is Phase 2A of 13 (Backend Core Services) and runs IN PARALLEL with KP-003, KP-004, and KP-005. The service depends on Phase 1's database schema and DTOs/repository being complete.

## User Story
As a system administrator or sales team member
I want to manage Chinese supplier information with validation and business rules
So that I can maintain accurate supplier data, search for suppliers, and ensure data integrity when products reference suppliers

## Problem Statement
The Kompass system needs a service layer to:
- Create suppliers with proper validation (email format, WeChat normalization)
- Retrieve suppliers with product counts for informed decision-making
- List and filter suppliers by status, country, and product association
- Search suppliers by name, email, or WeChat ID
- Soft-delete suppliers while protecting referential integrity (no deletion if active products exist)
- Enforce business rules consistently across all supplier operations

Without this service layer, the API routes cannot properly orchestrate supplier management with validation and business logic.

## Solution Statement
Create a `SupplierService` class in `apps/Server/app/services/supplier_service.py` that:
- Wraps the existing `SupplierRepository` with business logic
- Adds validation for email format and WeChat ID normalization
- Implements product count enrichment on supplier retrieval
- Provides filtering by status, country, and has_products flag
- Implements search across name, email, and WeChat fields
- Enforces the "no delete with active products" business rule
- Follows the singleton pattern consistent with existing services

## Relevant Files
Use these files to implement the feature:

- `apps/Server/app/models/kompass_dto.py` - Contains `SupplierCreateDTO`, `SupplierUpdateDTO`, `SupplierResponseDTO`, `SupplierListResponseDTO`, `PaginationDTO`, and `SupplierStatus` enum. These are the input/output types for the service.
- `apps/Server/app/repository/kompass_repository.py` - Contains `SupplierRepository` class and singleton `supplier_repository` instance with CRUD methods. Also contains `ProductRepository` for checking active products.
- `apps/Server/app/services/auth_service.py` - Reference for service layer patterns (class structure, singleton instance, logging format `print(f"INFO/WARN/ERROR [ServiceName]: ...")`).
- `apps/Server/app/config/database.py` - Database connection utilities if needed for complex queries.
- `app_docs/feature-9ce5e2ee-database-schema-core-dtos.md` - Documentation of Phase 1 implementation with schema and DTO details.

### New Files
- `apps/Server/app/services/supplier_service.py` - Main supplier service with all business logic
- `apps/Server/tests/services/test_supplier_service.py` - Unit tests for the supplier service

## Implementation Plan

### Phase 1: Foundation
1. Create the service file structure following existing patterns
2. Import necessary DTOs, repository instances, and utilities
3. Define the `SupplierService` class with proper docstrings
4. Add helper methods for validation (email format, WeChat normalization)

### Phase 2: Core Implementation
1. Implement `create_supplier()` with validation and WeChat normalization
2. Implement `get_supplier()` with product count enrichment
3. Implement `list_suppliers()` with filtering and pagination
4. Implement `update_supplier()` with validation
5. Implement `delete_supplier()` with active products check
6. Implement `search_suppliers()` with multi-field search

### Phase 3: Integration
1. Create comprehensive unit tests for all service methods
2. Test edge cases (invalid email, empty results, active products blocking delete)
3. Verify integration with repository layer

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create Service File Structure
Create `apps/Server/app/services/supplier_service.py` with:
- Module docstring describing the service purpose
- Imports: `re` for email validation, `math` for pagination, `UUID` from uuid
- Import DTOs from `app.models.kompass_dto`
- Import repositories from `app.repository.kompass_repository`
- Class `SupplierService` with docstring

### Step 2: Implement Email Validation Helper
Add private method `_validate_email(email: str) -> bool`:
- Use regex pattern to validate email format
- Return True if valid, False otherwise
- This is used to validate `contact_email` field

### Step 3: Implement WeChat Normalization Helper
Add private method `_normalize_wechat_id(wechat_id: str) -> str`:
- Convert to lowercase
- Strip whitespace
- Return normalized ID
- Note: The current schema has `contact_phone` but the issue mentions WeChat. We'll add a `wechat_id` field handling if needed, or apply normalization to existing fields.

### Step 4: Implement Create Supplier Method
Add method `create_supplier(request: SupplierCreateDTO) -> SupplierResponseDTO`:
- Validate email format if provided (contact_email field)
- Normalize WeChat ID if applicable
- Call `supplier_repository.create()` with validated data
- Return `SupplierResponseDTO` from result
- Raise `ValueError` for validation failures
- Log INFO on success, ERROR on failure

### Step 5: Implement Get Supplier with Product Count
Add method `get_supplier(supplier_id: UUID) -> Optional[SupplierResponseDTO]`:
- Call `supplier_repository.get_by_id()`
- If found, query product count using `product_repository.get_all(supplier_id=supplier_id)`
- Add `product_count` to response (extend DTO if needed or return as dict)
- Return None if not found
- Log INFO on access

### Step 6: Implement List Suppliers with Filters
Add method `list_suppliers(status: Optional[str], country: Optional[str], has_products: Optional[bool], sort_by: str, page: int, limit: int) -> SupplierListResponseDTO`:
- Build filter conditions for repository query
- For `has_products` filter, need to join with products or use subquery
- Call repository's `get_all()` with filters
- Calculate pagination metadata
- Return `SupplierListResponseDTO` with items and pagination

### Step 7: Implement Update Supplier Method
Add method `update_supplier(supplier_id: UUID, request: SupplierUpdateDTO) -> Optional[SupplierResponseDTO]`:
- Validate email format if provided and changed
- Normalize WeChat ID if provided
- Call `supplier_repository.update()` with validated data
- Return updated `SupplierResponseDTO`
- Return None if supplier not found
- Raise `ValueError` for validation failures

### Step 8: Implement Delete Supplier (Soft Delete)
Add method `delete_supplier(supplier_id: UUID) -> bool`:
- First check if supplier exists
- Check for active products: query `product_repository.get_all(supplier_id=supplier_id, status='active')`
- If active products exist, raise `ValueError("Cannot delete supplier with active products")`
- Call `supplier_repository.delete()` (sets status to inactive)
- Return True on success, False if supplier not found
- Log WARN when blocking due to active products

### Step 9: Implement Search Suppliers Method
Add method `search_suppliers(query: str) -> List[SupplierResponseDTO]`:
- Search across name, contact_email, and contact_phone (for WeChat) fields
- Use ILIKE pattern matching in repository or filter in-memory
- Return list of matching `SupplierResponseDTO`
- Limit results to reasonable number (e.g., 50)
- Return empty list if query is empty or too short

### Step 10: Add SupplierFilters DTO if Needed
Check if `kompass_dto.py` needs a `SupplierFiltersDTO` class:
- Fields: status (Optional), country (Optional), has_products (Optional[bool])
- This enables typed filter passing to `list_suppliers()`

### Step 11: Create Singleton Instance
At the bottom of `supplier_service.py`:
- Create singleton: `supplier_service = SupplierService()`
- Export for use by API routes

### Step 12: Extend Repository for Product Count Query
If the repository doesn't support counting products by supplier efficiently:
- Add method `count_products_by_supplier(supplier_id: UUID) -> int` to `ProductRepository` in `kompass_repository.py`
- Use `SELECT COUNT(*) FROM products WHERE supplier_id = %s` query

### Step 13: Extend Repository for Has-Products Filter
If the repository doesn't support filtering suppliers by has_products:
- Add method `get_all_with_product_filter()` to `SupplierRepository` or extend `get_all()`
- Use a subquery or LEFT JOIN to count products per supplier

### Step 14: Create Test Directory Structure
Create `apps/Server/tests/services/__init__.py` if it doesn't exist

### Step 15: Create Unit Tests for Supplier Service
Create `apps/Server/tests/services/test_supplier_service.py`:
- Test `create_supplier` with valid data
- Test `create_supplier` with invalid email (should raise ValueError)
- Test `get_supplier` with existing ID
- Test `get_supplier` with non-existent ID (should return None)
- Test `list_suppliers` with various filter combinations
- Test `update_supplier` with valid data
- Test `delete_supplier` with no products (should succeed)
- Test `delete_supplier` with active products (should raise ValueError)
- Test `search_suppliers` with matching query
- Test `search_suppliers` with no matches (should return empty list)

### Step 16: Run Validation Commands
Execute all validation commands to ensure the implementation is correct with zero regressions.

## Testing Strategy

### Unit Tests
- Mock the repository layer to isolate service logic
- Test each service method with valid and invalid inputs
- Verify proper exception handling (ValueError for validation failures)
- Test edge cases: empty strings, None values, boundary conditions

### Edge Cases
- Creating supplier with empty name (should fail at DTO validation)
- Updating supplier with invalid email format
- Deleting supplier that doesn't exist
- Searching with empty query string
- Filtering with no matches
- Pagination at boundaries (page 0, negative limit)
- Supplier with 0 products vs supplier with active products

## Acceptance Criteria
- [ ] All CRUD operations (create, read, update, delete) working correctly
- [ ] Filtering by status, country, and has_products functional
- [ ] Pagination returns correct metadata (page, limit, total, pages)
- [ ] Soft delete sets status to 'inactive' instead of hard delete
- [ ] Cannot delete supplier with active products (ValueError raised)
- [ ] Search returns relevant results for name, email, wechat
- [ ] Email validation rejects malformed addresses
- [ ] WeChat ID normalized to lowercase
- [ ] Unit tests cover all methods and edge cases
- [ ] All tests passing with zero regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && source .venv/bin/activate && python -c "from app.services.supplier_service import supplier_service; print('SupplierService imported successfully')"` - Verify service can be imported
- `cd apps/Server && .venv/bin/ruff check app/services/supplier_service.py` - Lint the new service file
- `cd apps/Server && .venv/bin/ruff check .` - Run full Server linting to check for regressions
- `cd apps/Server && .venv/bin/pytest tests/services/test_supplier_service.py -v --tb=short` - Run supplier service unit tests
- `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` - Run all Server tests to ensure no regressions

## Notes

### Schema Considerations
The current schema has `contact_phone` but the issue mentions WeChat ID. Options:
1. Use `contact_phone` field for WeChat (common practice since WeChat IDs are often phone numbers)
2. Add a `wechat_id` column to the suppliers table (requires migration)

For this implementation, we'll normalize the existing fields and document that `contact_phone` can store WeChat IDs.

### Parallel Execution
This issue runs in parallel with:
- KP-003: Product Service
- KP-004: Portfolio Service
- KP-005: Client Service

Each service is independent but shares the same repository layer from Phase 1.

### Future Integration
The Supplier Service will be consumed by:
- Phase 3 API Routes: `/api/suppliers/*` endpoints
- Product Service: validating supplier references when creating products
- Quotation Service: looking up supplier info for quotation items

### Logging Convention
Follow existing pattern from CLAUDE.md:
```python
print(f"INFO [SupplierService]: Created supplier {supplier_id}")
print(f"WARN [SupplierService]: Blocked deletion of supplier {supplier_id} - has active products")
print(f"ERROR [SupplierService]: Failed to create supplier: {error}")
```
