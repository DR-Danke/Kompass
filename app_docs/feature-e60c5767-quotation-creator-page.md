# Quotation Creator Page

**ADW ID:** e60c5767
**Date:** 2026-02-01
**Specification:** specs/issue-28-adw-e60c5767-quotation-creator-page.md

## Overview

Implements a comprehensive quotation creator page with multi-step workflow including client selection, product browsing from the Biblia General catalog, editable line items table with live pricing calculation, and a pricing panel showing full cost breakdown in COP. Also includes a quotations list page with filtering, pagination, and CRUD operations.

## What Was Built

- **QuotationCreatorPage** - Multi-section quotation builder with client selection, product selection, line items, and pricing sidebar
- **QuotationsListPage** - Data table showing all quotations with filtering, pagination, and actions (view, edit, clone, delete)
- **useQuotationCreator Hook** - State management for quotation creation including client, items, settings, and pricing calculations
- **useQuotations Hook** - List management with filtering, pagination, and CRUD operations
- **ClientSelector Component** - Client search autocomplete with inline creation capability
- **ProductSelector Component** - Dual-mode product selection (catalog browse or portfolio selection)
- **QuotationLineItemsTable Component** - Line items table with inline editing for quantity and price overrides
- **QuotationPricingPanel Component** - Live pricing breakdown sidebar with cost components in USD and COP
- **QuotationActions Component** - Action buttons for Save Draft, Calculate, PDF export, Email, and Share Link
- **QuotationStatusBadge Component** - Color-coded status badges for quotation statuses

## Technical Implementation

### Files Modified

- `apps/Client/src/App.tsx`: Added routes for `/quotations` (list), `/quotations/new` (create), and `/quotations/:id` (edit)
- `apps/Client/src/pages/kompass/QuotationsPage.tsx`: Removed (replaced with QuotationsListPage)

### New Files Created

- `apps/Client/src/pages/kompass/QuotationCreatorPage.tsx` (314 lines): Main quotation creator page with multi-column layout
- `apps/Client/src/pages/kompass/QuotationsListPage.tsx` (452 lines): Quotations data table with filtering and actions
- `apps/Client/src/hooks/kompass/useQuotationCreator.ts` (484 lines): State management hook for quotation creation
- `apps/Client/src/hooks/kompass/useQuotations.ts` (201 lines): List management hook for quotations
- `apps/Client/src/components/kompass/ClientSelector.tsx` (272 lines): Client search and selection component
- `apps/Client/src/components/kompass/ProductSelector.tsx` (344 lines): Product browser with catalog and portfolio modes
- `apps/Client/src/components/kompass/QuotationLineItemsTable.tsx` (219 lines): Editable line items table
- `apps/Client/src/components/kompass/QuotationPricingPanel.tsx` (253 lines): Pricing breakdown sidebar
- `apps/Client/src/components/kompass/QuotationActions.tsx` (339 lines): Action buttons with dialogs
- `apps/Client/src/components/kompass/QuotationStatusBadge.tsx` (45 lines): Status badge component
- `.claude/commands/e2e/test_quotation_creator.md` (185 lines): E2E test specification

### Key Changes

- Two-column layout with main content (left) and sticky pricing panel (right sidebar)
- Client selection with async search autocomplete and inline "Create New Client" option
- Product selection with tabbed interface: Browse Biblia General catalog or select from existing portfolios
- Line items table with editable quantity fields, price override capability, and calculated line totals
- Pricing panel shows complete cost breakdown: Subtotal FOB USD, Tariffs, International Freight, Inspection, Insurance, National Freight (COP), Nationalization (COP), Margin %, and highlighted Total COP
- Actions: Save Draft, Calculate (triggers backend pricing), PDF export, Send Email (dialog), Copy Share Link
- Edit mode loads existing quotation by ID with pre-populated data
- Unsaved changes warning with browser beforeunload event

## How to Use

1. Navigate to `/quotations` to see the list of all quotations
2. Click "New Quotation" to create a new quotation
3. Select a client by searching or creating a new one inline
4. Add products from the catalog tab or select from existing portfolios
5. Adjust quantities in the line items table (price overrides are supported)
6. Configure quote details: Incoterm, Currency, Discount %, Validity days, Notes, Terms & Conditions
7. Click "Save Draft" to persist the quotation
8. Click "Calculate" to get full pricing breakdown from the backend
9. Use PDF, Email, or Share actions to distribute the quotation

## Configuration

The quotation creator uses the following default settings:

- Default Incoterm: FOB
- Default Currency: USD
- Default Validity: 30 days
- Default Margin: 15%

Pricing calculation is performed by the backend quotation service which considers:
- FOB prices from line items
- HS code tariffs
- Freight rates (international and national)
- Insurance and inspection costs
- Exchange rates (USD to COP)
- Configurable margin percentage

## Testing

### E2E Test File
See `.claude/commands/e2e/test_quotation_creator.md` for the complete E2E test specification.

### Manual Testing
1. Navigate to quotations list, verify data table displays correctly
2. Apply filters (status, client, date range) and verify filtering works
3. Create a new quotation with all sections filled
4. Verify live pricing updates when quantities change
5. Save draft and verify persistence
6. Edit an existing quotation and verify data loads correctly
7. Test PDF export, email sending, and share link copy functionality

## Notes

- The backend quotation service and API routes were already implemented (KP-017 and KP-019)
- PDF generation uses reportlab on the backend - frontend just calls the export endpoint
- Email sending supports mock mode via EMAIL_MOCK_MODE environment variable
- Share tokens are JWT-based with 30-day expiration
- The pricing formula: Total COP = (FOB + Tariffs + Int'l Freight + Inspection + Insurance) × Exchange Rate + National Freight + Nationalization + Margin
- Status workflow: draft → sent → viewed → negotiating → accepted/rejected/expired
- Debouncing is recommended on quantity/price inputs to avoid excessive API calls (not yet implemented)
- Pricing panel shows "Calculating..." while waiting for backend response
