# Feature: Frontend Types and API Service Layer for Kompass

## Metadata
issue_number: `20`
adw_id: `af7568d5`
issue_json: `{"number":20,"title":"[Kompass] Phase 8: Frontend Types and API Service","body":"## Context\n**Current Phase:** Phase 8 of 13 - Frontend Foundation\n**Current Issue:** KP-020 (Issue 20 of 33)\n**Parallel Execution:** NO - Must complete before Phase 9-12 frontend work.\n\n---\n\n## Description\nCreate TypeScript types and API service layer for Kompass frontend.\n\n## Requirements\n\n### File: apps/Client/src/types/kompass.ts\n\n```typescript\n// Enums\nexport type SupplierStatus = 'active' | 'inactive';\nexport type ProductStatus = 'draft' | 'active' | 'discontinued';\nexport type ClientStatus = 'lead' | 'qualified' | 'quoting' | 'negotiating' | 'won' | 'lost';\nexport type QuotationStatus = 'draft' | 'sent' | 'viewed' | 'negotiating' | 'accepted' | 'rejected' | 'expired';\nexport type Incoterm = 'FOB' | 'CIF' | 'DDP';\n\n// Interfaces for Supplier, Product, Category, Tag, Portfolio, Client, Quotation, etc.\n```\n\n### File: apps/Client/src/services/kompassService.ts\nService methods for all API endpoints.\n\n### Update: apps/Client/src/components/layout/Sidebar.tsx\n- Add Kompass menu section with icons:\n  - Dashboard, Suppliers, Products (Biblia General), Portfolios, Clients, Quotations, Settings\n\n### Update: apps/Client/src/App.tsx\n- Add routes for all Kompass pages\n\n## Acceptance Criteria\n- [ ] All types defined matching backend DTOs\n- [ ] Service methods for all endpoints\n- [ ] Sidebar navigation added\n- [ ] Routes configured\n- [ ] TypeScript strict mode passing\n\nInclude workflow: adw_plan_build_iso"}`

## Feature Description
Create the TypeScript type definitions and API service layer for the Kompass Portfolio & Quotation system frontend. This phase establishes the foundation for all subsequent frontend development (Phases 9-12) by defining:

1. **TypeScript types** matching all backend DTOs for type-safe API interactions
2. **API service layer** with methods for all Kompass endpoints (suppliers, products, categories, tags, portfolios, clients, quotations, pricing)
3. **Sidebar navigation** with Kompass menu items
4. **Route configuration** for all Kompass pages (placeholder components)

This is a critical foundation phase that must complete before any UI component development can begin.

## User Story
As a **frontend developer**
I want to **have strongly-typed API services and navigation configured**
So that **I can build Kompass UI components with type safety and proper routing**

## Problem Statement
The frontend currently lacks the TypeScript type definitions that match the backend DTOs and has no service layer for communicating with the Kompass API endpoints. Additionally, the navigation sidebar and routing don't include the Kompass modules. Without these foundations, frontend component development cannot proceed.

## Solution Statement
Create a comprehensive TypeScript types file (`kompass.ts`) that mirrors all backend DTOs, a service layer (`kompassService.ts`) with methods for all CRUD operations across all Kompass entities, update the Sidebar with navigation items for all Kompass modules, and configure App.tsx routes to placeholder pages that will be implemented in subsequent phases.

## Relevant Files
Use these files to implement the feature:

- `apps/Client/src/types/auth.ts` - Reference for TypeScript type patterns (interfaces, union types, naming conventions)
- `apps/Client/src/services/authService.ts` - Reference for API service patterns (object-based exports, apiClient usage, logging)
- `apps/Client/src/api/clients/index.ts` - The Axios apiClient used for all API calls
- `apps/Client/src/components/layout/Sidebar.tsx` - Sidebar to update with Kompass navigation items
- `apps/Client/src/App.tsx` - Route configuration to add Kompass pages
- `apps/Server/app/models/kompass_dto.py` - Backend DTOs that frontend types must match exactly
- `apps/Server/main.py` - API route prefixes to build service endpoint URLs

### New Files
- `apps/Client/src/types/kompass.ts` - All Kompass TypeScript type definitions
- `apps/Client/src/services/kompassService.ts` - Comprehensive API service for all Kompass endpoints
- `apps/Client/src/pages/kompass/SuppliersPage.tsx` - Placeholder page for suppliers
- `apps/Client/src/pages/kompass/ProductsPage.tsx` - Placeholder page for products (Biblia General)
- `apps/Client/src/pages/kompass/PortfoliosPage.tsx` - Placeholder page for portfolios
- `apps/Client/src/pages/kompass/ClientsPage.tsx` - Placeholder page for clients
- `apps/Client/src/pages/kompass/QuotationsPage.tsx` - Placeholder page for quotations
- `apps/Client/src/pages/kompass/SettingsPage.tsx` - Placeholder page for Kompass settings

## Implementation Plan
### Phase 1: Foundation - TypeScript Types
Define all TypeScript types in `kompass.ts` that exactly match the backend DTOs:
- Status/Enum union types (SupplierStatus, ProductStatus, ClientStatus, etc.)
- Pagination interface
- Request DTOs (Create, Update, Filter)
- Response DTOs (single, list with pagination)
- Specialized DTOs (TreeNode, WithCount, etc.)

### Phase 2: Core Implementation - API Service Layer
Create `kompassService.ts` with service objects for each entity:
- `supplierService` - CRUD + search
- `productService` - CRUD + search + image/tag management
- `categoryService` - CRUD + tree operations
- `tagService` - CRUD + search
- `portfolioService` - CRUD + item management + share token + export
- `clientService` - CRUD + status management + pipeline
- `quotationService` - CRUD + pricing + status transitions + clone + share + email
- `pricingService` - HS codes, freight rates, pricing settings
- `nicheService` - CRUD for client niches

### Phase 3: Integration - Navigation and Routing
- Update Sidebar.tsx with Kompass menu items
- Add placeholder pages for all modules
- Configure routes in App.tsx

## Step by Step Tasks

### Step 1: Create TypeScript Types File
- Create `apps/Client/src/types/kompass.ts`
- Define all status/enum union types matching backend enums:
  - `SupplierStatus`: 'active' | 'inactive' | 'pending_review'
  - `ProductStatus`: 'active' | 'inactive' | 'draft' | 'discontinued'
  - `ClientStatus`: 'active' | 'inactive' | 'prospect'
  - `ClientSource`: 'website' | 'referral' | 'cold_call' | 'trade_show' | 'linkedin' | 'other'
  - `QuotationStatus`: 'draft' | 'sent' | 'viewed' | 'negotiating' | 'accepted' | 'rejected' | 'expired'
  - `Incoterm`: 'FOB' | 'CIF' | 'EXW' | 'DDP' | 'DAP' | 'CFR' | 'CPT' | 'CIP' | 'DAT' | 'FCA' | 'FAS'
- Define `Pagination` interface
- Define Niche interfaces (Create, Update, Response, ListResponse, WithClientCount)
- Define Category interfaces (Create, Update, Response, ListResponse, TreeNode)
- Define Tag interfaces (Create, Update, Response, ListResponse, WithCount)
- Define HSCode interfaces (Create, Update, Response, ListResponse)
- Define Supplier interfaces (Create, Update, Response, ListResponse)
- Define ProductImage interfaces (Create, Response)
- Define Product interfaces (Create, Update, Response, ListResponse, Filter)
- Define PortfolioItem interfaces (Create, Response)
- Define Portfolio interfaces (Create, Update, Response, ListResponse, Filter, ShareToken, PublicResponse, AddItem, Reorder, Duplicate, FromFilters)
- Define Client interfaces (Create, Update, Response, ListResponse, StatusChange, StatusHistory, WithQuotations, Pipeline, TimingFeasibility, QuotationSummary)
- Define FreightRate interfaces (Create, Update, Response, ListResponse)
- Define PricingSetting interfaces (Create, Update, Response, SettingsResponse)
- Define QuotationItem interfaces (Create, Update, Response)
- Define Quotation interfaces (Create, Update, Response, ListResponse, Filter, Pricing, StatusTransition, Clone, ShareToken, PublicResponse, PublicItem, SendEmailRequest, SendEmailResponse)
- Define BulkCreate interfaces (Error, Response)

### Step 2: Create Kompass API Service
- Create `apps/Client/src/services/kompassService.ts`
- Import apiClient from `@/api/clients`
- Import all types from `@/types/kompass`

**Niche Service Methods:**
- `listNiches(page?, limit?)` - GET /api/niches
- `getNiche(id)` - GET /api/niches/:id
- `createNiche(data)` - POST /api/niches
- `updateNiche(id, data)` - PUT /api/niches/:id
- `deleteNiche(id)` - DELETE /api/niches/:id

**Supplier Service Methods:**
- `listSuppliers(page?, limit?, filters?)` - GET /api/suppliers
- `getSupplier(id)` - GET /api/suppliers/:id
- `createSupplier(data)` - POST /api/suppliers
- `updateSupplier(id, data)` - PUT /api/suppliers/:id
- `deleteSupplier(id)` - DELETE /api/suppliers/:id
- `searchSuppliers(query)` - GET /api/suppliers/search

**Product Service Methods:**
- `listProducts(page?, limit?, filters?)` - GET /api/products
- `getProduct(id)` - GET /api/products/:id
- `createProduct(data)` - POST /api/products
- `updateProduct(id, data)` - PUT /api/products/:id
- `deleteProduct(id)` - DELETE /api/products/:id
- `searchProducts(query)` - GET /api/products/search
- `bulkCreateProducts(products)` - POST /api/products/bulk
- `addProductImage(productId, image)` - POST /api/products/:id/images
- `removeProductImage(productId, imageId)` - DELETE /api/products/:id/images/:imageId
- `setProductPrimaryImage(productId, imageId)` - PUT /api/products/:id/images/:imageId/primary
- `addProductTag(productId, tagId)` - POST /api/products/:id/tags/:tagId
- `removeProductTag(productId, tagId)` - DELETE /api/products/:id/tags/:tagId

**Category Service Methods:**
- `listCategories(page?, limit?)` - GET /api/categories
- `getCategoryTree()` - GET /api/categories/tree
- `getCategory(id)` - GET /api/categories/:id
- `createCategory(data)` - POST /api/categories
- `updateCategory(id, data)` - PUT /api/categories/:id
- `deleteCategory(id)` - DELETE /api/categories/:id
- `moveCategory(id, parentId)` - PUT /api/categories/:id/move

**Tag Service Methods:**
- `listTags(page?, limit?)` - GET /api/tags
- `getTag(id)` - GET /api/tags/:id
- `createTag(data)` - POST /api/tags
- `updateTag(id, data)` - PUT /api/tags/:id
- `deleteTag(id)` - DELETE /api/tags/:id
- `searchTags(query)` - GET /api/tags/search

**Portfolio Service Methods:**
- `listPortfolios(page?, limit?, filters?)` - GET /api/portfolios
- `getPortfolio(id)` - GET /api/portfolios/:id
- `createPortfolio(data)` - POST /api/portfolios
- `updatePortfolio(id, data)` - PUT /api/portfolios/:id
- `deletePortfolio(id)` - DELETE /api/portfolios/:id
- `addPortfolioItem(portfolioId, data)` - POST /api/portfolios/:id/items
- `removePortfolioItem(portfolioId, itemId)` - DELETE /api/portfolios/:id/items/:itemId
- `reorderPortfolioItems(portfolioId, productIds)` - PUT /api/portfolios/:id/reorder
- `duplicatePortfolio(portfolioId, newName)` - POST /api/portfolios/:id/duplicate
- `getPortfolioShareToken(portfolioId)` - POST /api/portfolios/:id/share
- `getPortfolioByShareToken(token)` - GET /api/portfolios/share/:token
- `exportPortfolioPdf(portfolioId)` - GET /api/portfolios/:id/export/pdf
- `createPortfolioFromFilters(data)` - POST /api/portfolios/from-filters

**Client Service Methods:**
- `listClients(page?, limit?, filters?)` - GET /api/clients
- `getClient(id)` - GET /api/clients/:id
- `createClient(data)` - POST /api/clients
- `updateClient(id, data)` - PUT /api/clients/:id
- `deleteClient(id)` - DELETE /api/clients/:id
- `searchClients(query)` - GET /api/clients/search
- `updateClientStatus(id, statusChange)` - PUT /api/clients/:id/status
- `getClientStatusHistory(id)` - GET /api/clients/:id/status-history
- `getPipelineView()` - GET /api/clients/pipeline
- `checkTimingFeasibility(clientId)` - GET /api/clients/:id/timing-feasibility

**Quotation Service Methods:**
- `listQuotations(page?, limit?, filters?)` - GET /api/quotations
- `getQuotation(id)` - GET /api/quotations/:id
- `createQuotation(data)` - POST /api/quotations
- `updateQuotation(id, data)` - PUT /api/quotations/:id
- `deleteQuotation(id)` - DELETE /api/quotations/:id
- `calculateQuotation(id)` - POST /api/quotations/:id/calculate
- `updateQuotationStatus(id, statusTransition)` - PUT /api/quotations/:id/status
- `cloneQuotation(id, notes?)` - POST /api/quotations/:id/clone
- `getQuotationShareToken(id)` - POST /api/quotations/:id/share
- `getQuotationByShareToken(token)` - GET /api/quotations/share/:token
- `exportQuotationPdf(id)` - GET /api/quotations/:id/export/pdf
- `sendQuotationEmail(id, emailRequest)` - POST /api/quotations/:id/send
- `addQuotationItem(quotationId, item)` - POST /api/quotations/:id/items
- `updateQuotationItem(quotationId, itemId, item)` - PUT /api/quotations/:id/items/:itemId
- `deleteQuotationItem(quotationId, itemId)` - DELETE /api/quotations/:id/items/:itemId

**Pricing Service Methods:**
- `listHsCodes(page?, limit?)` - GET /api/pricing/hs-codes
- `getHsCode(id)` - GET /api/pricing/hs-codes/:id
- `createHsCode(data)` - POST /api/pricing/hs-codes
- `updateHsCode(id, data)` - PUT /api/pricing/hs-codes/:id
- `deleteHsCode(id)` - DELETE /api/pricing/hs-codes/:id
- `searchHsCodes(query)` - GET /api/pricing/hs-codes/search
- `listFreightRates(page?, limit?)` - GET /api/pricing/freight-rates
- `getFreightRate(id)` - GET /api/pricing/freight-rates/:id
- `createFreightRate(data)` - POST /api/pricing/freight-rates
- `updateFreightRate(id, data)` - PUT /api/pricing/freight-rates/:id
- `deleteFreightRate(id)` - DELETE /api/pricing/freight-rates/:id
- `getActiveFreightRate(origin, destination, incoterm)` - GET /api/pricing/freight-rates/active
- `getPricingSettings()` - GET /api/pricing/settings
- `updatePricingSetting(key, data)` - PUT /api/pricing/settings/:key

### Step 3: Create Placeholder Pages
Create minimal placeholder page components that will be implemented in later phases:

- Create `apps/Client/src/pages/kompass/SuppliersPage.tsx` - Display "Suppliers Page - Coming Soon"
- Create `apps/Client/src/pages/kompass/ProductsPage.tsx` - Display "Products (Biblia General) - Coming Soon"
- Create `apps/Client/src/pages/kompass/PortfoliosPage.tsx` - Display "Portfolios Page - Coming Soon"
- Create `apps/Client/src/pages/kompass/ClientsPage.tsx` - Display "Clients Page - Coming Soon"
- Create `apps/Client/src/pages/kompass/QuotationsPage.tsx` - Display "Quotations Page - Coming Soon"
- Create `apps/Client/src/pages/kompass/SettingsPage.tsx` - Display "Kompass Settings - Coming Soon"

Each placeholder should:
- Use Material-UI Box and Typography components
- Display a centered message indicating the page is under development
- Be a valid React component that can be routed to

### Step 4: Update Sidebar Navigation
- Edit `apps/Client/src/components/layout/Sidebar.tsx`
- Add Material-UI icons import:
  - FactoryIcon (Suppliers)
  - InventoryIcon (Products/Biblia General)
  - CollectionsIcon (Portfolios)
  - PeopleIcon (Clients)
  - DescriptionIcon (Quotations)
  - SettingsIcon (already imported)
- Add Kompass navigation items to navItems array:
  ```typescript
  { title: 'Suppliers', icon: <FactoryIcon />, path: '/suppliers' },
  { title: 'Biblia General', icon: <InventoryIcon />, path: '/products' },
  { title: 'Portfolios', icon: <CollectionsIcon />, path: '/portfolios' },
  { title: 'Clients', icon: <PeopleIcon />, path: '/clients' },
  { title: 'Quotations', icon: <DescriptionIcon />, path: '/quotations' },
  ```
- Keep Settings at the end of the list

### Step 5: Update App.tsx Routes
- Edit `apps/Client/src/App.tsx`
- Import all new placeholder pages
- Add routes inside the protected route section:
  ```typescript
  <Route path="suppliers" element={<SuppliersPage />} />
  <Route path="products" element={<ProductsPage />} />
  <Route path="portfolios" element={<PortfoliosPage />} />
  <Route path="clients" element={<ClientsPage />} />
  <Route path="quotations" element={<QuotationsPage />} />
  <Route path="settings" element={<SettingsPage />} />
  ```

### Step 6: Run Validation Commands
Execute all validation commands to ensure the implementation is correct with zero regressions.

## Testing Strategy
### Unit Tests
This feature focuses on type definitions and service layer setup. Unit tests are not required for:
- TypeScript type definitions (validated by TypeScript compiler)
- Service layer methods (will be tested through integration tests in later phases)

The TypeScript compiler serves as the primary validation mechanism for this phase.

### Edge Cases
- Ensure all optional fields are properly typed with `?` or `| null`
- Ensure all date fields are typed as `string` (ISO format from backend)
- Ensure UUID fields are typed as `string`
- Ensure Decimal fields from backend are typed as `number | string` for flexibility
- Ensure enum/union types exactly match backend enum values

## Acceptance Criteria
- [ ] All TypeScript types defined in `kompass.ts` matching backend DTOs exactly
- [ ] All service methods implemented in `kompassService.ts` for every API endpoint
- [ ] Sidebar shows Kompass navigation items (Suppliers, Biblia General, Portfolios, Clients, Quotations, Settings)
- [ ] Routes configured for all Kompass pages in App.tsx
- [ ] TypeScript compilation passes with zero errors (`npm run typecheck`)
- [ ] Frontend build succeeds (`npm run build`)
- [ ] No console errors when navigating between Kompass pages

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/af7568d5/apps/Client && npm run typecheck` - Run TypeScript type checking to validate all types are correct
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/af7568d5/apps/Client && npm run lint` - Run ESLint to check for code quality issues
- `cd /mnt/c/Users/user/danke_apps/Kompass/trees/af7568d5/apps/Client && npm run build` - Build the frontend to ensure no compilation errors

## Notes
- The backend already has all API endpoints implemented (see main.py for router registrations)
- Backend DTOs are defined in `apps/Server/app/models/kompass_dto.py` - types must match exactly
- This phase creates placeholder pages only - full UI implementation happens in Phases 9-12
- The service layer follows the existing pattern from `authService.ts`
- All monetary values should be typed as `number | string` to handle both JavaScript numbers and stringified decimals from the backend
- Date fields should be typed as `string` (ISO format) since backend returns datetime as strings
- UUID fields should be typed as `string` since JavaScript doesn't have a native UUID type
