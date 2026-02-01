# Chore: Kompass Documentation and CLAUDE.md Update

## Metadata
issue_number: `33`
adw_id: `09679466`
issue_json: `{"number":33,"title":"[Kompass] Phase 13B: Documentation and CLAUDE.md Update","body":"## Context\n**Current Phase:** Phase 13 of 13 - Testing & Documentation (FINAL PHASE)\n**Current Issue:** KP-033 (Issue 33 of 33 - FINAL ISSUE)\n**Parallel Execution:** YES - Runs IN PARALLEL with KP-032.\n\n---\n\n## Description\nCreate documentation and update CLAUDE.md with Kompass module information.\n\n## Requirements\n\n### File: ai_docs/KOMPASS_MODULE_GUIDE.md\n1. Module overview\n2. Architecture diagram\n3. API endpoint reference\n4. Database schema\n5. Pricing formula explanation\n6. Configuration options\n7. Deployment notes\n\n### File: ai_docs/KOMPASS_USER_GUIDE.md\n1. Supplier management guide\n2. Product catalog (Biblia General) guide\n3. Portfolio creation guide\n4. Quotation workflow guide\n5. Pricing configuration guide\n\n### Update: CLAUDE.md\n- Add Kompass module section\n- Document new routes and services\n- Add new slash commands if applicable\n- Update project structure\n\n### UI Polish Checklist\n- Consistent spacing\n- Loading skeletons\n- Empty states\n- Error messages\n- Mobile responsiveness\n\n## Acceptance Criteria\n- [ ] Technical documentation complete\n- [ ] User guide complete\n- [ ] CLAUDE.md updated\n- [ ] UI consistent and polished"}`

## Chore Description

This is the final issue (KP-033) of the Kompass Portfolio & Quotation Automation System implementation. The chore involves creating comprehensive documentation for the Kompass module:

1. **Technical Module Guide** (`ai_docs/KOMPASS_MODULE_GUIDE.md`) - Developer-focused documentation covering architecture, API endpoints, database schema, and pricing formulas
2. **User Guide** (`ai_docs/KOMPASS_USER_GUIDE.md`) - End-user documentation explaining how to use each feature
3. **CLAUDE.md Update** - Add Kompass module section to help Claude Code understand the module structure

The documentation task does NOT include actual UI polish work (that's a separate concern for the E2E tests in KP-032).

## Relevant Files

Use these files to resolve the chore:

### Files to Read for Context
- `CLAUDE.md` - Current Claude Code guidance file that needs updating with Kompass module information
- `ai_docs/PRD-Kompass-Portfolio-Quotation-System.md` - Product Requirements Document with complete feature specifications
- `ai_docs/KOMPASS_ADW_IMPLEMENTATION_PROMPTS.md` - Implementation reference with all 33 issues and architecture overview
- `apps/Server/database/schema.sql` - Database schema with all 15 Kompass tables
- `apps/Server/app/models/kompass_dto.py` - All DTOs and enums for the Kompass module
- `apps/Server/main.py` - Router registration showing all API route prefixes
- `apps/Client/src/App.tsx` - Frontend routing configuration
- `apps/Client/src/components/layout/Sidebar.tsx` - Navigation structure

### Backend Service Files (for API documentation)
- `apps/Server/app/services/supplier_service.py` - Supplier management service
- `apps/Server/app/services/product_service.py` - Product (Biblia General) service
- `apps/Server/app/services/category_service.py` - Hierarchical category service
- `apps/Server/app/services/tag_service.py` - Product tagging service
- `apps/Server/app/services/portfolio_service.py` - Portfolio curation service
- `apps/Server/app/services/client_service.py` - Client CRM service
- `apps/Server/app/services/quotation_service.py` - Quotation and pricing engine service
- `apps/Server/app/services/pricing_service.py` - Pricing configuration service
- `apps/Server/app/services/pdf_service.py` - PDF generation service
- `apps/Server/app/services/extraction_service.py` - AI data extraction service
- `apps/Server/app/services/niche_service.py` - Client niche service
- `apps/Server/app/services/dashboard_service.py` - Dashboard KPI service

### API Route Files (for endpoint documentation)
- `apps/Server/app/api/supplier_routes.py` - `/api/suppliers` endpoints
- `apps/Server/app/api/product_routes.py` - `/api/products` endpoints
- `apps/Server/app/api/category_routes.py` - `/api/categories` endpoints
- `apps/Server/app/api/tag_routes.py` - `/api/tags` endpoints
- `apps/Server/app/api/portfolio_routes.py` - `/api/portfolios` endpoints
- `apps/Server/app/api/client_routes.py` - `/api/clients` endpoints
- `apps/Server/app/api/quotation_routes.py` - `/api/quotations` endpoints
- `apps/Server/app/api/pricing_routes.py` - `/api/pricing` endpoints
- `apps/Server/app/api/extraction_routes.py` - `/api/extract` endpoints
- `apps/Server/app/api/niche_routes.py` - `/api/niches` endpoints
- `apps/Server/app/api/dashboard_routes.py` - `/api/dashboard` endpoints

### Frontend Files (for user guide documentation)
- `apps/Client/src/types/kompass.ts` - TypeScript types (1,007 lines)
- `apps/Client/src/services/kompassService.ts` - API service methods (910 lines)
- `apps/Client/src/pages/kompass/*.tsx` - All 12 Kompass pages

### Existing Feature Documentation (for reference)
- `app_docs/feature-*.md` - 31 feature documentation files created during development

### New Files

- `ai_docs/KOMPASS_MODULE_GUIDE.md` - Technical developer documentation
- `ai_docs/KOMPASS_USER_GUIDE.md` - End-user guide

## Step by Step Tasks

IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create Technical Module Guide (ai_docs/KOMPASS_MODULE_GUIDE.md)

Create the comprehensive technical documentation file with the following sections:

**1.1 Module Overview**
- Purpose: Portfolio & Quotation Automation System for China sourcing business
- Problem: Reduce time spent on data entry (25%) and quotation prep (50%) to enable more sales
- Solution: Automated data extraction, centralized product database, portfolio curation, automated quotations

**1.2 Architecture Diagram**
- Create ASCII diagram showing:
  - Frontend (React 19 + TypeScript + MUI) → Vercel
  - Backend (FastAPI + Python 3.11) → Render
  - Database (PostgreSQL) → Supabase
  - External Services: AI extraction, PDF generation

**1.3 Database Schema**
- Document all 15 tables with their relationships:
  - Reference tables: niches, categories, tags, hs_codes
  - Core entities: suppliers, products, product_images, product_tags
  - Portfolio: portfolios, portfolio_items
  - CRM: clients, client_status_history
  - Pricing: freight_rates, pricing_settings
  - Quotations: quotations, quotation_items
- Include key indexes and constraints

**1.4 API Endpoint Reference**
- Document all endpoints grouped by module:
  - Suppliers: GET/POST/PUT/DELETE /api/suppliers
  - Products: GET/POST/PUT/DELETE /api/products (with images, tags)
  - Categories: GET/POST/PUT/DELETE /api/categories (tree structure)
  - Tags: GET/POST/PUT/DELETE /api/tags
  - Portfolios: GET/POST/PUT/DELETE /api/portfolios (with share tokens, PDF)
  - Clients: GET/POST/PUT/DELETE /api/clients (pipeline, status history)
  - Quotations: GET/POST/PUT/DELETE /api/quotations (pricing, email, PDF)
  - Pricing: /api/pricing (hs-codes, freight-rates, settings)
  - Dashboard: /api/dashboard (stats)
  - Extraction: /api/extract (upload, job status, confirm)

**1.5 Pricing Formula Explanation**
- Document the complete pricing engine formula:
  ```
  Total COP = (FOB USD + Tariffs + Int'l Freight + Inspection + Insurance) × Exchange Rate
              + National Freight COP + Nationalization COP + Margin
  ```
- Explain each component and how it's configured
- Document pricing settings and their defaults

**1.6 Configuration Options**
- Environment variables required
- Pricing settings (exchange rate, margin, inspection, insurance, etc.)
- HS codes and tariff rates
- Freight rates configuration

**1.7 Deployment Notes**
- Backend on Render (Python 3.11.9 critical)
- Frontend on Vercel
- Database on Supabase
- CORS configuration

### Step 2: Create User Guide (ai_docs/KOMPASS_USER_GUIDE.md)

Create end-user documentation with the following sections:

**2.1 Getting Started**
- Logging in and navigating the dashboard
- Understanding the sidebar navigation
- Overview of available modules

**2.2 Supplier Management Guide**
- Adding new suppliers (name, country, WeChat, email, contact info)
- Editing supplier information
- Filtering and searching suppliers
- Managing supplier status (active/inactive)
- Viewing supplier products

**2.3 Product Catalog (Biblia General) Guide**
- Browsing products (grid view vs table view)
- Using filters (category, supplier, price range, tags, status)
- Full-text search functionality
- Creating products manually
- Adding product images (primary image, gallery)
- Assigning categories and tags
- Understanding product statuses (draft, active, discontinued)

**2.4 Import Wizard Guide**
- Supported file formats (PDF, Excel, images)
- Upload process
- Reviewing extracted products
- Editing before import
- Confirming bulk import

**2.5 Categories & Tags Guide**
- Creating hierarchical categories
- Managing the category tree
- Creating and assigning tags
- Using tags for product organization

**2.6 Portfolio Creation Guide**
- Creating new portfolios
- Adding products to portfolios
- Reordering products
- Adding curator notes
- Duplicating portfolios
- Exporting to PDF
- Sharing portfolios via public link

**2.7 Client Management Guide**
- Adding new clients (company, contact info, niche)
- Using the Kanban pipeline view
- Drag-and-drop status changes
- Viewing client details and quotation history
- Managing niches

**2.8 Quotation Workflow Guide**
- Creating a new quotation
- Selecting a client
- Adding products to the quotation
- Understanding the pricing panel
- Reviewing cost breakdown
- Saving drafts
- Generating PDF proforma
- Sending via email
- Sharing via public link
- Cloning quotations for revisions
- Status workflow (draft → sent → viewed → negotiating → accepted/rejected)

**2.9 Pricing Configuration Guide**
- Managing HS codes and tariff rates
- Configuring freight rates by route
- Setting global pricing parameters
- Understanding the pricing formula

### Step 3: Update CLAUDE.md with Kompass Module Section

Add a new section to CLAUDE.md after the "Architecture" section:

**3.1 Add Kompass Module Overview**
```markdown
## Kompass Module

Portfolio & Quotation Automation System for managing suppliers, products, portfolios, clients, and quotations with automated pricing.

### Module Architecture
- **11 Backend Services**: supplier, product, category, tag, portfolio, client, quotation, pricing, niche, extraction, dashboard
- **12 API Route Groups**: /api/suppliers, /api/products, /api/categories, /api/tags, /api/portfolios, /api/clients, /api/quotations, /api/pricing, /api/niches, /api/extract, /api/dashboard
- **15 Database Tables**: See database/schema.sql
- **12 Frontend Pages**: Dashboard, Suppliers, Products, Import Wizard, Categories, Portfolios, Portfolio Builder, Clients, Quotations, Quotation Creator, Niches, Pricing Config
```

**3.2 Document Key Services**
- Pricing Engine in quotation_service.py
- PDF generation in pdf_service.py
- Share token pattern for public access
- Status workflow for quotations

**3.3 Update Project Structure**
Add Kompass-specific files to the structure section:
```
├── apps/
│   ├── Client/
│   │   └── src/
│   │       ├── pages/kompass/     # 12 Kompass pages
│   │       ├── components/kompass/ # 37 Kompass components
│   │       ├── hooks/kompass/     # 7 custom hooks
│   │       ├── types/kompass.ts   # Type definitions
│   │       └── services/kompassService.ts
│   └── Server/
│       └── app/
│           ├── services/          # 11 Kompass services
│           ├── api/               # 12 route files
│           ├── models/kompass_dto.py
│           └── repository/kompass_repository.py
├── ai_docs/
│   ├── KOMPASS_MODULE_GUIDE.md    # Technical docs
│   ├── KOMPASS_USER_GUIDE.md      # User guide
│   └── PRD-Kompass-Portfolio-Quotation-System.md
└── app_docs/                      # 31 feature docs
```

**3.4 Add New Slash Commands (if applicable)**
Review current slash commands and add any Kompass-specific ones (likely none new needed as existing `/test`, `/test_e2e` already cover Kompass).

### Step 4: Run Validation Commands

Execute all validation commands to ensure documentation is correct and nothing is broken.

## Validation Commands

Execute every command to validate the chore is complete with zero regressions.

- `cd apps/Client && npm run typecheck` - Verify frontend TypeScript compiles without errors
- `cd apps/Client && npm run lint` - Verify frontend code follows ESLint rules
- `cd apps/Client && npm run build` - Verify frontend builds successfully
- `cd apps/Server && .venv/bin/ruff check .` - Verify backend code follows ruff linting rules
- `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` - Run backend tests to ensure no regressions

## Notes

### Documentation Guidelines
- Use consistent formatting with headers, code blocks, and tables
- Include examples where helpful
- Keep technical docs separate from user guides
- Reference existing PRD and implementation docs for accuracy

### Key Metrics from PRD
| Metric | Current | Target |
|--------|---------|--------|
| Time to extract 100 products from catalog | 8 hours | 30 minutes |
| Time to generate a quotation | 1 day | 15 minutes |
| Quotations per week | 1-2 | 10-15 |

### Pricing Formula Reference
```
Price COP = (
  (Price FOB USD × Quantity)
  + Tariff (based on HS Code %)
  + International Freight
  + Pre-shipment Inspection
  + Cargo Insurance
) × Exchange Rate USD/COP
+ National Freight COP
+ Nationalization COP
+ Commercial Margin (%)
```

### Status Workflows
**Quotation Status Transitions:**
- draft → sent
- sent → viewed, accepted, rejected, expired
- viewed → negotiating, accepted, rejected, expired
- negotiating → accepted, rejected, expired

**Client Status Pipeline:**
- lead → qualified → quoting → negotiating → won | lost

### Database Tables (15 total)
1. niches
2. categories
3. tags
4. hs_codes
5. suppliers
6. products
7. product_images
8. product_tags
9. portfolios
10. portfolio_items
11. clients
12. client_status_history
13. freight_rates
14. pricing_settings
15. quotations
16. quotation_items

### API Route Prefixes
| Prefix | Router |
|--------|--------|
| /api/suppliers | supplier_routes |
| /api/products | product_routes |
| /api/categories | category_routes |
| /api/tags | tag_routes |
| /api/niches | niche_routes |
| /api/extract | extraction_routes |
| /api/portfolios | portfolio_routes |
| /api/clients | client_routes |
| /api/quotations | quotation_routes |
| /api/pricing | pricing_routes |
| /api/dashboard | dashboard_routes |
