# Frontend Types and API Service Layer for Kompass

**ADW ID:** af7568d5
**Date:** 2026-02-01
**Specification:** specs/issue-20-adw-af7568d5-frontend-types-api-service.md

## Overview

This feature establishes the frontend foundation for the Kompass Portfolio & Quotation system by implementing comprehensive TypeScript type definitions that match backend DTOs, a complete API service layer for all Kompass endpoints, sidebar navigation integration, and route configuration for all Kompass modules. This is a critical Phase 8 deliverable that enables subsequent frontend UI development (Phases 9-12).

## What Was Built

- **TypeScript Types File** (`kompass.ts`) - 876 lines of comprehensive type definitions
- **API Service Layer** (`kompassService.ts`) - 749 lines of service methods for all Kompass endpoints
- **Sidebar Navigation** - Kompass menu items added to the application sidebar
- **Route Configuration** - All Kompass routes configured in App.tsx
- **Placeholder Pages** - Six placeholder pages for future UI implementation

## Technical Implementation

### Files Modified

- `apps/Client/src/types/kompass.ts`: New file with all TypeScript type definitions matching backend DTOs
- `apps/Client/src/services/kompassService.ts`: New file with comprehensive API service layer
- `apps/Client/src/components/layout/Sidebar.tsx`: Added Kompass navigation items with icons
- `apps/Client/src/App.tsx`: Added routes for all Kompass pages
- `apps/Client/src/pages/kompass/SuppliersPage.tsx`: Placeholder page for suppliers
- `apps/Client/src/pages/kompass/ProductsPage.tsx`: Placeholder page for products (Biblia General)
- `apps/Client/src/pages/kompass/PortfoliosPage.tsx`: Placeholder page for portfolios
- `apps/Client/src/pages/kompass/ClientsPage.tsx`: Placeholder page for clients
- `apps/Client/src/pages/kompass/QuotationsPage.tsx`: Placeholder page for quotations
- `apps/Client/src/pages/kompass/SettingsPage.tsx`: Placeholder page for Kompass settings

### Key Changes

- **Status/Enum Types**: Defined union types for SupplierStatus, ProductStatus, ClientStatus, ClientSource, QuotationStatus, and Incoterm matching backend enums exactly
- **Entity DTOs**: Complete type definitions for all Kompass entities including Niche, Category, Tag, HSCode, Supplier, Product, Portfolio, Client, Quotation, FreightRate, and PricingSetting
- **Request/Response Types**: Separate Create, Update, Response, and ListResponse interfaces for each entity following backend DTO patterns
- **Service Objects**: Nine service objects (nicheService, supplierService, productService, categoryService, tagService, portfolioService, clientService, quotationService, pricingService) with full CRUD and specialized operations
- **Navigation Integration**: Added five new navigation items (Suppliers, Biblia General, Portfolios, Clients, Quotations) using Material-UI icons

## How to Use

### TypeScript Types

Import types from the kompass types file:

```typescript
import type {
  SupplierResponse,
  ProductCreate,
  QuotationStatus,
} from '@/types/kompass';
```

### API Services

Import and use service objects for API operations:

```typescript
import { supplierService, productService } from '@/services/kompassService';

// List suppliers with pagination
const suppliers = await supplierService.list(1, 20);

// Create a new product
const product = await productService.create({
  name: 'New Product',
  supplier_id: 'uuid-here',
});

// Search products
const results = await productService.search('keyword');
```

### Navigation

The sidebar automatically shows Kompass navigation items:
- Suppliers (`/suppliers`)
- Biblia General (`/products`)
- Portfolios (`/portfolios`)
- Clients (`/clients`)
- Quotations (`/quotations`)
- Settings (`/settings`)

## Configuration

No additional configuration required. The service layer uses the existing `apiClient` from `@/api/clients` which handles authentication and base URL configuration.

## Testing

1. **TypeScript Validation**: Run `npm run typecheck` to verify all types compile correctly
2. **Lint Check**: Run `npm run lint` to ensure code quality
3. **Build Verification**: Run `npm run build` to confirm the frontend builds successfully
4. **Navigation Test**: Log in and verify all Kompass menu items appear in the sidebar and navigate to placeholder pages

## Notes

- All monetary values are typed as `number | string` to handle both JavaScript numbers and stringified decimals from the backend
- Date fields are typed as `string` (ISO format) since the backend returns datetime as strings
- UUID fields are typed as `string` since JavaScript doesn't have a native UUID type
- The placeholder pages display "Coming Soon" messages and will be fully implemented in Phases 9-12
- Service methods include console.log statements for debugging following the project's logging pattern
