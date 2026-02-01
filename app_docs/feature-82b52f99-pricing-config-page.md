# Pricing Configuration Page

**ADW ID:** 82b52f99
**Date:** 2026-02-01
**Specification:** specs/issue-29-adw-82b52f99-pricing-config-page.md

## Overview

A comprehensive Pricing Configuration page for the Kompass Portfolio & Quotation system that enables administrators and managers to manage three key pricing components through a tabbed interface: HS codes with tariff rates, freight rates with validity tracking, and global pricing settings.

## What Was Built

- **PricingConfigPage**: Main page with three tabs (HS Codes, Freight Rates, Settings)
- **HSCodeTable/HSCodeForm**: Searchable table and CRUD dialog for HS codes
- **FreightRateTable/FreightRateForm**: Filterable table with expired rate highlighting and CRUD dialog for freight rates
- **PricingSettingsForm**: Form for global pricing settings with validation and save confirmation
- **E2E Test Specification**: Playwright test file for pricing configuration page

## Technical Implementation

### Files Modified

- `apps/Client/src/App.tsx`: Added `/pricing` route with PricingConfigPage component
- `apps/Client/src/components/layout/Sidebar.tsx`: Added "Pricing" navigation item with AttachMoneyIcon
- `apps/Client/package.json`: Added `@mui/x-date-pickers` dependency for date selection
- `playwright-mcp-config.json`: Updated config for E2E tests

### Files Created

- `apps/Client/src/pages/kompass/PricingConfigPage.tsx`: Main page component with tabbed interface, state management for HS codes and freight rates, CRUD handlers, delete confirmation dialogs
- `apps/Client/src/components/kompass/HSCodeTable.tsx`: Table component with search functionality, edit/delete actions
- `apps/Client/src/components/kompass/HSCodeForm.tsx`: Dialog form using react-hook-form for creating/editing HS codes
- `apps/Client/src/components/kompass/FreightRateTable.tsx`: Table with origin/destination filtering and expired rate highlighting (yellow background)
- `apps/Client/src/components/kompass/FreightRateForm.tsx`: Dialog form with date pickers for validity dates and incoterm selection
- `apps/Client/src/components/kompass/PricingSettingsForm.tsx`: Form with validated number inputs for margin, costs, and exchange rates
- `.claude/commands/e2e/test_pricing_config.md`: E2E test specification for the page

### Key Changes

- **Tabbed Interface**: Uses Material-UI Tabs with TabPanel helper component for switching between HS Codes, Freight Rates, and Settings tabs
- **HS Code Management**: Searchable by code or description, CRUD operations with validation (code required, duty_rate 0-100%)
- **Freight Rate Management**: Filterable by origin/destination, expired rates highlighted with warning color, validity date tracking with date pickers
- **Settings Form**: Uses react-hook-form with InputAdornment for unit display (%, USD, COP), confirmation dialog before saving
- **Delete Protection**: Handles 409 Conflict errors when trying to delete HS codes or freight rates that are in use

## How to Use

1. Navigate to the Pricing page via the sidebar (click "Pricing" under the navigation items)
2. **HS Codes Tab**:
   - Use the search box to filter HS codes by code or description
   - Click "Add HS Code" to create a new entry
   - Click the edit icon to modify an existing HS code
   - Click the delete icon to remove an HS code (if not in use)
3. **Freight Rates Tab**:
   - Use the origin/destination filters to narrow down rates
   - Expired rates are highlighted with a yellow background
   - Click "Add Freight Rate" to create a new entry
   - Edit or delete rates using the action icons
4. **Settings Tab**:
   - Modify pricing settings (margin %, inspection cost, insurance %, etc.)
   - Click "Save Settings" to update (confirmation dialog will appear)

## Configuration

The page uses the existing `pricingService` from `kompassService.ts` with these settings:

- `default_margin_percentage`: Default profit margin for quotations (0-100%)
- `inspection_cost_usd`: Standard inspection cost in USD
- `insurance_percentage`: Insurance percentage for shipments (0-100%)
- `nationalization_cost_cop`: Customs nationalization cost in COP
- `exchange_rate_usd_cop`: USD to COP exchange rate

## Testing

Run the E2E tests for this feature:
```bash
# Read and execute the E2E test specification
cat .claude/commands/e2e/test_pricing_config.md
```

Test scenarios covered:
- Navigate to /pricing and verify tabs
- HS Codes: search, create, edit, delete operations
- Freight Rates: filter, create, edit, delete, expired rate highlighting
- Settings: view, update, save with confirmation

## Notes

- The page requires authentication and appropriate role permissions
- HS codes cannot be deleted if they are assigned to products (returns 409 error)
- Freight rates with `valid_until` date before today are considered expired and highlighted
- Settings changes affect all future quotation calculations
- All forms include data-testid attributes for E2E testing
