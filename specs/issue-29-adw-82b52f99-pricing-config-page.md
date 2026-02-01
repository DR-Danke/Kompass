# Feature: Pricing Configuration Page

## Metadata
issue_number: `29`
adw_id: `82b52f99`
issue_json: `{"number":29,"title":"[Kompass] Phase 11B: Pricing Configuration Page","body":"## Context\n**Current Phase:** Phase 11 of 13 - Frontend Quotation\n**Current Issue:** KP-029 (Issue 29 of 33)\n**Parallel Execution:** YES - Runs IN PARALLEL with KP-028.\n\n---\n\n## Description\nCreate pricing configuration page for HS codes, freight rates, and settings.\n\n## Requirements\n\n### File: apps/Client/src/pages/kompass/PricingConfigPage.tsx\n\n#### Tabs\n1. **HS Codes:** Searchable table, create/edit dialog, columns: Code, Description, Tariff %\n2. **Freight Rates:** Table with origin, destination, container type, rate, validity\n3. **Settings:** Form with default margin, inspection cost, insurance %, etc.\n\n#### HS Code Search\n- Instant search by code or description\n- Add new code button\n\n#### Freight Rate Management\n- Filter by origin/destination\n- Highlight expired rates\n- Add new rate button\n\n#### Settings Form\n- Number inputs with validation\n- Exchange rate (USD to COP)\n- Save button with confirmation\n\n## Acceptance Criteria\n- [ ] HS codes management working\n- [ ] Freight rates management working\n- [ ] Settings save working\n- [ ] Expired rate warnings shown"}`

## Feature Description
Create a comprehensive Pricing Configuration page for the Kompass Portfolio & Quotation system that enables administrators and managers to manage three key pricing components: HS codes (Harmonized System codes with tariff rates), freight rates (origin/destination routes with validity tracking), and global pricing settings (default margins, exchange rates, etc.). The page will use a tabbed interface for easy navigation between these three configuration areas.

## User Story
As a Kompass admin or manager
I want to configure pricing parameters through a dedicated page with HS codes, freight rates, and settings tabs
So that I can maintain accurate pricing data for quotation calculations and ensure tariffs, freight costs, and margins are up-to-date

## Problem Statement
The quotation system needs configurable pricing data including HS code tariff rates, freight costs by route, and global settings like margins and exchange rates. Currently, there's no UI to manage these pricing configurations, requiring direct database access. This creates friction in maintaining accurate pricing data and increases the risk of outdated or incorrect quotations.

## Solution Statement
Implement a tabbed Pricing Configuration page at `/pricing` with three tabs:
1. **HS Codes Tab**: Searchable table with CRUD operations for HS codes including code, description, and duty rate
2. **Freight Rates Tab**: Table with filtering by origin/destination, CRUD operations, validity date tracking, and visual warnings for expired rates
3. **Settings Tab**: Form-based interface for global pricing settings with validation and save confirmation

The implementation will follow existing patterns from NichesPage and other Kompass pages, using Material-UI components, react-hook-form for forms, and the existing pricingService from kompassService.ts.

## Relevant Files
Use these files to implement the feature:

- **apps/Client/src/pages/kompass/NichesPage.tsx**: Reference implementation for CRUD page pattern with dialogs
- **apps/Client/src/components/kompass/NicheForm.tsx**: Reference for dialog form pattern using react-hook-form
- **apps/Client/src/services/kompassService.ts**: Contains pricingService with all required API methods (lines 667-762)
- **apps/Client/src/types/kompass.ts**: Contains HSCodeCreate/Response, FreightRateCreate/Response, PricingSettingResponse types (lines 148-654)
- **apps/Client/src/App.tsx**: Route configuration for adding /pricing route
- **apps/Client/src/components/layout/Sidebar.tsx**: Sidebar navigation for adding Pricing menu item
- **apps/Server/app/api/pricing_routes.py**: Backend API endpoints for pricing configuration
- **apps/Server/app/services/pricing_service.py**: Backend pricing service with business logic
- **app_docs/feature-b6ca4629-pricing-config-api-routes.md**: Documentation for pricing API endpoints
- **app_docs/feature-d2c2988b-pricing-config-service.md**: Documentation for pricing service layer
- **.claude/commands/test_e2e.md**: E2E test runner instructions
- **.claude/commands/e2e/test_niches_page.md**: Example E2E test file pattern

### New Files
- **apps/Client/src/pages/kompass/PricingConfigPage.tsx**: Main pricing configuration page with tabbed interface
- **apps/Client/src/components/kompass/HSCodeForm.tsx**: Dialog form for creating/editing HS codes
- **apps/Client/src/components/kompass/FreightRateForm.tsx**: Dialog form for creating/editing freight rates
- **apps/Client/src/components/kompass/HSCodeTable.tsx**: Table component for HS codes with search
- **apps/Client/src/components/kompass/FreightRateTable.tsx**: Table component for freight rates with filtering and expired highlighting
- **apps/Client/src/components/kompass/PricingSettingsForm.tsx**: Form component for pricing settings
- **.claude/commands/e2e/test_pricing_config.md**: E2E test file for the pricing configuration page

## Implementation Plan
### Phase 1: Foundation
- Add the `/pricing` route to App.tsx
- Add "Pricing" navigation item to Sidebar.tsx with appropriate icon (AttachMoney or PriceCheck)
- Create the base PricingConfigPage.tsx with tabbed interface using Material-UI Tabs

### Phase 2: Core Implementation
- Implement HSCodeTable component with DataGrid/table, search functionality, and CRUD buttons
- Implement HSCodeForm dialog for create/edit operations with react-hook-form validation
- Implement FreightRateTable component with table, origin/destination filtering, expired rate highlighting
- Implement FreightRateForm dialog for create/edit operations with date picker for validity dates
- Implement PricingSettingsForm component with validated number inputs and save confirmation

### Phase 3: Integration
- Wire up all components in PricingConfigPage with proper state management
- Connect to pricingService API methods
- Add loading states, error handling, and success notifications
- Implement tab state persistence (optional - via URL query param or localStorage)

## Step by Step Tasks

### Step 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` for E2E test runner instructions
- Read `.claude/commands/e2e/test_niches_page.md` for example E2E test pattern
- Create `.claude/commands/e2e/test_pricing_config.md` with test steps for:
  - Navigate to /pricing page and verify tabs are displayed
  - HS Codes tab: search, create, edit, delete operations
  - Freight Rates tab: filter, create, edit, delete, verify expired rate highlighting
  - Settings tab: view settings, update values, save with confirmation

### Step 2: Add Route and Navigation
- Edit `apps/Client/src/App.tsx`:
  - Import PricingConfigPage
  - Add route: `<Route path="pricing" element={<PricingConfigPage />} />`
- Edit `apps/Client/src/components/layout/Sidebar.tsx`:
  - Import AttachMoneyIcon (or PriceCheckIcon)
  - Add navItem: `{ title: 'Pricing', icon: <AttachMoneyIcon />, path: '/pricing' }`
  - Position after "Niches" and before "Settings"

### Step 3: Create Base PricingConfigPage
- Create `apps/Client/src/pages/kompass/PricingConfigPage.tsx`:
  - Import Material-UI components (Box, Typography, Tabs, Tab)
  - Implement TabPanel helper component
  - Set up three tabs: "HS Codes", "Freight Rates", "Settings"
  - Add tab state management with useState
  - Style with consistent header layout (title + optional actions)

### Step 4: Create HSCodeTable Component
- Create `apps/Client/src/components/kompass/HSCodeTable.tsx`:
  - Import HSCodeResponse type from kompass.ts
  - Add props: hsCodes, loading, onEdit, onDelete, searchQuery, onSearchChange
  - Implement search TextField with instant filtering
  - Implement table with columns: Code, Description, Duty Rate (%), Actions
  - Add edit (pencil) and delete (trash) IconButtons
  - Add "Add HS Code" button
  - Implement empty state when no HS codes found
  - Include data-testid attributes for E2E testing

### Step 5: Create HSCodeForm Component
- Create `apps/Client/src/components/kompass/HSCodeForm.tsx`:
  - Follow pattern from NicheForm.tsx
  - Use react-hook-form for form state
  - Fields: code (required), description (required), duty_rate (required, number 0-100)
  - Validation: code format, duty_rate range validation
  - Handle both create and edit modes
  - Connect to pricingService.createHsCode / pricingService.updateHsCode
  - Include loading state and error handling

### Step 6: Create FreightRateTable Component
- Create `apps/Client/src/components/kompass/FreightRateTable.tsx`:
  - Import FreightRateResponse type from kompass.ts
  - Add props: freightRates, loading, onEdit, onDelete, filters, onFilterChange
  - Add filter TextFields for origin and destination
  - Implement table with columns: Origin, Destination, Incoterm, Rate/kg, Rate/cbm, Min Charge, Transit Days, Valid From, Valid Until, Status, Actions
  - Highlight expired rates with warning color (row background or chip)
  - Calculate expired status: valid_until < today's date
  - Add "Add Freight Rate" button
  - Include data-testid attributes for E2E testing

### Step 7: Create FreightRateForm Component
- Create `apps/Client/src/components/kompass/FreightRateForm.tsx`:
  - Follow pattern from NicheForm.tsx
  - Use react-hook-form for form state
  - Fields: origin (required), destination (required), incoterm (select), rate_per_kg, rate_per_cbm, minimum_charge, transit_days, valid_from (date picker), valid_until (date picker), notes
  - Incoterm options from Incoterm type in kompass.ts
  - Date validation: valid_until must be after valid_from
  - Handle both create and edit modes
  - Connect to pricingService.createFreightRate / pricingService.updateFreightRate

### Step 8: Create PricingSettingsForm Component
- Create `apps/Client/src/components/kompass/PricingSettingsForm.tsx`:
  - Import PricingSettingResponse type from kompass.ts
  - Fetch settings using pricingService.getSettings()
  - Display settings in a form layout:
    - Default Margin % (number input)
    - Inspection Cost USD (number input)
    - Insurance % (number input)
    - Nationalization Cost COP (number input)
    - Exchange Rate USD/COP (number input)
  - Use react-hook-form for form state
  - Add validation for numeric values (positive numbers, reasonable ranges)
  - Implement Save button with confirmation dialog
  - Connect to pricingService.updateSetting for each changed setting
  - Show success/error notifications
  - Include data-testid attributes for E2E testing

### Step 9: Integrate Components in PricingConfigPage
- Update `apps/Client/src/pages/kompass/PricingConfigPage.tsx`:
  - Import all created components
  - Add state for HS codes list, freight rates list, loading, errors
  - Add state for HSCodeForm dialog (open, selectedHsCode)
  - Add state for FreightRateForm dialog (open, selectedFreightRate)
  - Add state for delete confirmation dialogs
  - Implement fetch functions for HS codes and freight rates
  - Implement CRUD handlers for HS codes (create, edit, delete)
  - Implement CRUD handlers for freight rates (create, edit, delete)
  - Wire up all components with proper props
  - Add useEffect to fetch data on mount

### Step 10: Add Delete Confirmation Dialogs
- In PricingConfigPage.tsx add:
  - Delete confirmation dialog for HS codes
  - Delete confirmation dialog for freight rates
  - Handle delete errors (e.g., HS code in use)
  - Show success notifications on delete

### Step 11: Run Validation Commands
Execute every command to validate the feature works correctly with zero regressions:
- Run TypeScript check: `cd apps/Client && npm run typecheck`
- Run ESLint: `cd apps/Client && npm run lint`
- Run build: `cd apps/Client && npm run build`
- Run backend tests: `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short`
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_pricing_config.md` to validate this functionality works

## Testing Strategy
### Unit Tests
- HSCodeForm: test validation rules (required fields, duty_rate range)
- FreightRateForm: test date validation (valid_until > valid_from)
- FreightRateTable: test expired rate detection logic
- PricingSettingsForm: test numeric validation

### Edge Cases
- Empty HS codes list (empty state)
- Empty freight rates list (empty state)
- Freight rate with null valid_until (perpetually valid)
- Freight rate that expires today (edge case for expired detection)
- Settings with missing values (handle gracefully)
- Long HS code descriptions (truncation)
- API errors during save operations

## Acceptance Criteria
- [ ] HS codes tab displays searchable table with code, description, and duty rate
- [ ] HS code create dialog allows adding new codes with validation
- [ ] HS code edit dialog pre-fills existing data and updates on save
- [ ] HS code delete shows confirmation and removes from list
- [ ] HS code search filters table by code or description instantly
- [ ] Freight rates tab displays table with all rate details
- [ ] Freight rates filter by origin and destination works
- [ ] Expired freight rates are visually highlighted (background color or badge)
- [ ] Freight rate create/edit dialog works with date pickers
- [ ] Freight rate delete shows confirmation and removes from list
- [ ] Settings tab displays all pricing settings with current values
- [ ] Settings form validates numeric inputs
- [ ] Settings save button shows confirmation dialog
- [ ] Settings save updates backend and shows success message
- [ ] Navigation item "Pricing" appears in sidebar
- [ ] Route /pricing loads the page correctly
- [ ] No TypeScript errors
- [ ] No ESLint errors
- [ ] Build completes successfully

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npm run typecheck` - Run Client type check to validate TypeScript compiles
- `cd apps/Client && npm run lint` - Run ESLint to validate code quality
- `cd apps/Client && npm run build` - Run Client build to validate production build works
- `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` - Run Server tests to validate backend still works
- `cd apps/Server && .venv/bin/ruff check .` - Run ruff linter on backend

Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_pricing_config.md` to validate this functionality works.

## Notes
- The pricingService already exists in kompassService.ts with all required API methods
- HSCode, FreightRate, and PricingSetting types already defined in kompass.ts
- Backend API routes already implemented at /api/pricing/* endpoints
- Follow NichesPage.tsx pattern for page structure and CRUD dialog patterns
- Use Material-UI Tabs for the tabbed interface
- Consider using MUI X DataGrid for tables if project already uses it, otherwise use basic Table component
- Expired rate detection: compare valid_until date with new Date() - highlight if valid_until < today
- Default pricing settings per documentation: default_margin_percentage, inspection_cost_usd, insurance_percentage, nationalization_cost_cop, exchange_rate_usd_cop
- Add data-testid attributes to key interactive elements for E2E testing
