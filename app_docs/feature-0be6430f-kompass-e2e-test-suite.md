# Kompass E2E Test Suite

**ADW ID:** 0be6430f
**Date:** 2026-02-01
**Specification:** specs/issue-32-adw-0be6430f-kompass-e2e-test-suite.md

## Overview

Comprehensive end-to-end test suite for the Kompass module that validates all critical user flows. The suite covers suppliers, products, portfolios, quotations, and pricing configurations through API integration tests and service-level E2E tests using pytest with mocked repositories.

## What Was Built

- Complete test infrastructure in `apps/Server/tests/test_kompass/` directory
- Shared fixtures for authentication, sample data factories, and test utilities
- Supplier workflow E2E tests (CRUD, validation, filtering, search)
- Product workflow E2E tests (CRUD, images, tags, bulk import, filtering)
- Portfolio workflow E2E tests (CRUD, items, duplication, share tokens, PDF)
- Quotation workflow E2E tests (CRUD, items, cloning, pricing, status workflow, PDF, email)
- Pricing configuration E2E tests (HS codes, freight rates, settings)
- Cross-service API integration tests (authentication, RBAC, delete constraints, pagination)

## Technical Implementation

### Files Modified

- `apps/Server/tests/test_kompass/__init__.py`: Package initialization with module docstring
- `apps/Server/tests/test_kompass/conftest.py`: 502 lines of shared fixtures including:
  - Authentication fixtures (`mock_auth_user`, `mock_admin_user`, `mock_manager_user`, `mock_viewer_user`)
  - Sample data factories (`create_sample_supplier`, `create_sample_product`, `create_sample_portfolio`, `create_sample_quotation`, `create_sample_hs_code`, `create_sample_freight_rate`)
  - Pagination and mock repository fixtures
  - Custom pytest markers (`slow`, `integration`, `e2e`)
- `apps/Server/tests/test_kompass/test_supplier_e2e.py`: 508 lines testing supplier workflows
- `apps/Server/tests/test_kompass/test_product_e2e.py`: 799 lines testing product workflows
- `apps/Server/tests/test_kompass/test_portfolio_e2e.py`: 571 lines testing portfolio workflows
- `apps/Server/tests/test_kompass/test_quotation_e2e.py`: 769 lines testing quotation workflows
- `apps/Server/tests/test_kompass/test_pricing_e2e.py`: 690 lines testing pricing configuration
- `apps/Server/tests/test_kompass/test_api_integration.py`: 568 lines testing API authentication, RBAC, and cross-service integration

### Key Changes

- **Factory Pattern**: All test data is generated via factory functions (`create_sample_*`) that produce consistent, configurable test data
- **Repository Mocking**: Tests use `@patch` decorators to mock repository layer, enabling isolated service-level testing
- **FastAPI TestClient**: API integration tests use FastAPI's `TestClient` with dependency overrides for authentication
- **Comprehensive Coverage**: Tests cover CRUD workflows, validation, filtering, search, cross-service constraints, and edge cases
- **Custom Markers**: Pytest markers allow selective test execution (`slow`, `integration`, `e2e`)

## How to Use

1. Navigate to the Server directory:
   ```bash
   cd apps/Server
   ```

2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

3. Run all Kompass E2E tests:
   ```bash
   .venv/bin/pytest tests/test_kompass/ -v --tb=short
   ```

4. Run a specific test file:
   ```bash
   .venv/bin/pytest tests/test_kompass/test_supplier_e2e.py -v
   ```

5. Run tests with custom markers:
   ```bash
   .venv/bin/pytest tests/test_kompass/ -v -m "not slow"
   ```

6. Run with coverage reporting:
   ```bash
   .venv/bin/pytest tests/test_kompass/ -v --cov=app --cov-report=term-missing
   ```

## Configuration

No additional configuration required. Tests use mocked repositories and don't require database connections.

### Pytest Markers

- `@pytest.mark.slow`: Mark tests as slow-running
- `@pytest.mark.integration`: Mark tests as integration tests
- `@pytest.mark.e2e`: Mark tests as end-to-end tests

## Testing

### Test Structure

Each test file follows the pattern:
```
tests/test_kompass/
├── __init__.py          # Package initialization
├── conftest.py          # Shared fixtures
├── test_supplier_e2e.py # Supplier workflow tests
├── test_product_e2e.py  # Product workflow tests
├── test_portfolio_e2e.py # Portfolio workflow tests
├── test_quotation_e2e.py # Quotation workflow tests
├── test_pricing_e2e.py  # Pricing config tests
└── test_api_integration.py # API integration tests
```

### Test Classes

Each domain has organized test classes:
- **TestSupplierCRUDWorkflow**: Create → Read → Update → Delete flow
- **TestSupplierValidation**: Email validation, required fields, duplicate handling
- **TestSupplierFiltering**: Status, country, has_products filters
- **TestProductWithImages**: Add, remove, set primary image
- **TestProductWithTags**: Tag management operations
- **TestBulkImport**: Bulk create with partial failure handling
- **TestPortfolioDuplication**: Duplicate portfolio with items
- **TestQuotationPricing**: Pricing formula validation
- **TestQuotationStatusWorkflow**: Draft → Sent → Accepted/Rejected transitions
- **TestAuthenticatedEndpoints**: Authentication requirement validation
- **TestRBACEnforcement**: Admin-only operation validation

### Running the Full Suite

```bash
# Run all tests with verbose output
.venv/bin/pytest tests/ -v --tb=short

# Run with time reporting (ensure < 5 minutes)
.venv/bin/pytest tests/ -v --tb=short --durations=10

# Run linter on test files
.venv/bin/ruff check tests/test_kompass/
```

## Notes

### Mocking Strategy

- Repository layer is mocked for all service tests
- External services (email, PDF) are always mocked
- FastAPI dependency injection used for authentication mocking in API tests

### Edge Cases Covered

- Empty states (no items, zero values)
- Boundary conditions (pagination limits, max items)
- Invalid data (malformed requests, invalid UUIDs)
- Authorization failures (wrong role, missing token)
- Cascade effects (delete with dependencies)
- Calculation edge cases (zero quantities, currency precision)

### Future Enhancements

- Add `pytest-benchmark` for performance regression testing
- Add `hypothesis` for property-based testing
- Consider contract tests for API response validation
- Add browser-based Playwright tests for UI flows
