# Product Requirements Document (PRD)
# Kompass Portfolio & Quotation Automation System

**Version:** 1.0
**Date:** January 31, 2026
**Author:** AI Development Team
**Status:** Draft

---

## 1. Executive Summary

### 1.1 Problem Statement

Kompass is a trading company that sources furniture, decorations, and construction finishes from China for Colombian clients (constructors, architects, hotels, retailers). Currently, the team spends:

- **25% of time** on manual data entry (populating the "Biblia General" product database)
- **50% of time** on quotation preparation (complex pricing with tariffs, freight, margins)
- **25% of time** on actual sales activities

This distribution is unsustainable. The goal is to flip it to **10% data entry, 15% quotation, 75% sales**.

### 1.2 Solution Overview

Build an integrated web application that:
1. **Automates data extraction** from supplier catalogs (PDF, Excel, images)
2. **Centralizes product management** in a structured database (Biblia General)
3. **Enables portfolio curation** by client niche with filtering and tagging
4. **Automates quotation generation** with pre-configured pricing formulas
5. **Tracks clients** through the sales lifecycle

### 1.3 Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Time to extract 100 products from catalog | 8 hours | 30 minutes |
| Time to generate a quotation | 1 day | 15 minutes |
| Quotations per week | 1-2 | 10-15 |
| Data entry accuracy | Variable | 95%+ |

---

## 2. User Personas

### 2.1 Diana - Design Director
- **Pain:** Spends hours extracting product data from PDFs and images
- **Need:** Automated data extraction, image processing, product categorization
- **Goal:** Focus on curation and client relationships, not data entry

### 2.2 Alejandro - Commercial Manager
- **Pain:** Complex Excel formulas for quotations, manual PDF generation
- **Need:** Automated quotation system with pricing formulas
- **Goal:** Send more quotations faster, close more deals

### 2.3 Ruben - CEO/Founder
- **Pain:** No visibility into pipeline, manual processes during trade fairs
- **Need:** Dashboard with metrics, mobile-friendly data capture
- **Goal:** Scale the business without adding headcount

---

## 3. Functional Requirements

### 3.1 Module: Suppliers Management

#### 3.1.1 Supplier Registry
- **FR-SUP-001:** System shall allow CRUD operations on suppliers
- **FR-SUP-002:** Supplier fields: name, country, WeChat ID, email, website, contact person, phone, trade fair origin, notes, status (active/inactive), created/updated timestamps
- **FR-SUP-003:** System shall support linking multiple catalogs (files) to a supplier
- **FR-SUP-004:** System shall track communication history with suppliers

#### 3.1.2 Supplier List & Search
- **FR-SUP-005:** System shall display suppliers in a searchable, sortable table
- **FR-SUP-006:** System shall support filtering by: country, status, date added, has products
- **FR-SUP-007:** System shall show product count per supplier

---

### 3.2 Module: Products (Biblia General)

#### 3.2.1 Product Registry
- **FR-PRD-001:** System shall allow CRUD operations on products
- **FR-PRD-002:** Product fields:
  - `sku` (alphanumeric reference from supplier)
  - `name` / `description`
  - `supplier_id` (FK)
  - `category_id` (FK)
  - `price_fob_usd` (supplier price)
  - `moq` (minimum order quantity)
  - `hs_code` (tariff classification)
  - `images[]` (array of image URLs)
  - `material`
  - `dimensions`
  - `weight_kg`
  - `is_customizable` (boolean)
  - `lead_time_days`
  - `tags[]` (for filtering)
  - `status` (draft/active/discontinued)
  - `created_at`, `updated_at`

#### 3.2.2 Data Extraction (AI-Assisted)
- **FR-PRD-003:** System shall accept file uploads: PDF, Excel (.xlsx/.xls), Word (.docx), images (PNG/JPG)
- **FR-PRD-004:** System shall extract product data from uploaded catalogs using OCR/AI
- **FR-PRD-005:** Extracted data shall be presented for human review before saving
- **FR-PRD-006:** System shall support batch import with validation report
- **FR-PRD-007:** System shall auto-detect and suggest HS codes based on product description

#### 3.2.3 Image Processing
- **FR-PRD-008:** System shall automatically remove backgrounds from product images
- **FR-PRD-009:** System shall resize images to standard dimensions (800x800, 400x400 thumbnails)
- **FR-PRD-010:** System shall support manual image upload and URL linking
- **FR-PRD-011:** System shall use reverse image search to find higher quality versions

#### 3.2.4 Product Catalog View
- **FR-PRD-012:** System shall display products in grid (visual) and table (data) views
- **FR-PRD-013:** System shall support filtering by: category, supplier, price range, MOQ, tags, status
- **FR-PRD-014:** System shall support full-text search across name, description, SKU
- **FR-PRD-015:** System shall show total product count and filter results count

---

### 3.3 Module: Categories & Tags

#### 3.3.1 Category Management
- **FR-CAT-001:** System shall support hierarchical categories (e.g., Furniture > Seating > Chairs)
- **FR-CAT-002:** Categories shall have: name, description, parent_category_id, icon, sort_order
- **FR-CAT-003:** System shall prevent deletion of categories with associated products

#### 3.3.2 Tag Management
- **FR-TAG-001:** System shall allow creating custom tags for flexible product classification
- **FR-TAG-002:** Tags can be used for: style (modern, classic), material (wood, metal), niche (hospitality, VIS)
- **FR-TAG-003:** System shall suggest existing tags during product editing (autocomplete)

---

### 3.4 Module: Portfolios (Curated Catalogs)

#### 3.4.1 Portfolio Management
- **FR-PRT-001:** System shall allow creating named portfolios (e.g., "Hospitality 2026", "VIS Básico")
- **FR-PRT-002:** Portfolio fields: name, description, target_niche_id, cover_image, status (draft/published), created_by
- **FR-PRT-003:** System shall allow adding/removing products to portfolios
- **FR-PRT-004:** Portfolio products shall have: sort_order, notes (curator comments)

#### 3.4.2 Portfolio Generation
- **FR-PRT-005:** System shall support creating portfolios from product filters (e.g., "all products tagged 'hospitality' under $50 FOB")
- **FR-PRT-006:** System shall generate PDF portfolio exports with customizable templates
- **FR-PRT-007:** PDF shall include: cover page, product images, descriptions, and QR code to digital version
- **FR-PRT-008:** System shall generate shareable web links for portfolios (read-only client view)

#### 3.4.3 Client-Specific Portfolios
- **FR-PRT-009:** System shall allow cloning a portfolio for a specific client
- **FR-PRT-010:** Client portfolios shall track which products the client has viewed/selected

---

### 3.5 Module: Clients (CRM)

#### 3.5.1 Client Registry
- **FR-CLI-001:** System shall allow CRUD operations on clients
- **FR-CLI-002:** Client fields:
  - `company_name`
  - `contact_name`
  - `email`, `phone`, `whatsapp`
  - `niche_id` (FK to niches: constructor, architect, hotel, retailer, etc.)
  - `project_name` (optional)
  - `project_deadline` (for timing validation)
  - `incoterm_preference` (FOB/CIF/DDP)
  - `status` (lead/qualified/quoting/negotiating/won/lost)
  - `source` (referral, fair, website, etc.)
  - `notes`
  - `assigned_to` (user_id)

#### 3.5.2 Client Pipeline
- **FR-CLI-003:** System shall display clients in a Kanban board by status
- **FR-CLI-004:** System shall support drag-and-drop status changes
- **FR-CLI-005:** System shall track status change history with timestamps

#### 3.5.3 Client Niches
- **FR-CLI-006:** System shall maintain a list of client niches: Constructoras, Estudios de Arquitectura, Desarrolladores, Hoteles, Operadores Rentas Cortas, Retailers
- **FR-CLI-007:** Niches shall be linked to recommended portfolios

---

### 3.6 Module: Quotations

#### 3.6.1 Quotation Creation
- **FR-QUO-001:** System shall allow creating quotations linked to a client
- **FR-QUO-002:** Quotation shall validate project timing (production + shipping vs. deadline)
- **FR-QUO-003:** User shall select products from Biblia General or a Portfolio
- **FR-QUO-004:** Each quotation line item shall have: product_id, quantity, unit_price_fob, notes

#### 3.6.2 Pricing Engine
- **FR-QUO-005:** System shall automatically calculate pricing based on formula:

```
Price COP = (
  (Price FOB USD × Quantity)
  + Tariff (based on HS Code %)
  + International Freight (configurable per route)
  + National Freight (configurable per destination)
  + Pre-shipment Inspection (configurable)
  + Cargo Insurance (% of value)
  + Nationalization Costs (configurable)
  + Commercial Margin (%)
) × Exchange Rate USD/COP
```

- **FR-QUO-006:** System shall maintain configurable pricing parameters:
  - Tariff rates by HS code
  - Freight rates by origin port / destination city
  - Default margin percentage
  - Exchange rate (manual or API-fed)

- **FR-QUO-007:** User shall be able to override calculated values manually
- **FR-QUO-008:** System shall show cost breakdown (FOB, tariffs, freight, margin, total)

#### 3.6.3 Quotation Workflow
- **FR-QUO-009:** Quotation statuses: draft, sent, viewed, negotiating, accepted, rejected, expired
- **FR-QUO-010:** System shall track quotation versions (v1, v2, etc.)
- **FR-QUO-011:** System shall support cloning quotations for revisions

#### 3.6.4 Quotation Output
- **FR-QUO-012:** System shall generate PDF proforma invoice with company branding
- **FR-QUO-013:** PDF shall include: client info, product list with images, pricing breakdown, payment terms, validity period
- **FR-QUO-014:** System shall send quotation via email directly from the system
- **FR-QUO-015:** System shall generate shareable web link for quotation (client can view online)

---

### 3.7 Module: Pricing Configuration

#### 3.7.1 HS Codes & Tariffs
- **FR-PRC-001:** System shall maintain a database of HS codes with tariff percentages
- **FR-PRC-002:** Admin shall be able to add/edit HS codes and rates
- **FR-PRC-003:** System shall support searching HS codes by description

#### 3.7.2 Freight Rates
- **FR-PRC-004:** System shall maintain freight rates by: origin_port, destination_city, container_type
- **FR-PRC-005:** Rates shall have effective dates (valid_from, valid_to)
- **FR-PRC-006:** System shall alert when using expired rates

#### 3.7.3 General Settings
- **FR-PRC-007:** System shall store default values for: inspection cost, insurance %, nationalization costs, commercial margin %
- **FR-PRC-008:** Exchange rate shall be configurable (manual entry or future API integration)

---

### 3.8 Module: Dashboard & Analytics

#### 3.8.1 KPI Dashboard
- **FR-DAS-001:** Dashboard shall show:
  - Total products in Biblia General
  - Products added this month
  - Active suppliers count
  - Quotations sent (this week/month)
  - Quotation conversion rate
  - Pipeline value by status
  - Top products quoted

#### 3.8.2 Activity Feed
- **FR-DAS-002:** Dashboard shall show recent activity (new products, quotations sent, clients added)

---

## 4. Non-Functional Requirements

### 4.1 Performance
- **NFR-001:** Page load time < 2 seconds for lists up to 1000 items
- **NFR-002:** PDF generation < 10 seconds for quotations up to 50 line items
- **NFR-003:** File upload (catalog extraction) < 30 seconds for files up to 20MB

### 4.2 Security
- **NFR-004:** All API endpoints require JWT authentication (existing system)
- **NFR-005:** Role-based access control (admin, manager, user, viewer)
- **NFR-006:** File uploads validated for type and scanned for malware
- **NFR-007:** Sensitive data (pricing formulas) accessible only to authorized roles

### 4.3 Scalability
- **NFR-008:** System shall support up to 50,000 products
- **NFR-009:** System shall support up to 1,000 suppliers
- **NFR-010:** System shall support up to 10 concurrent users

### 4.4 Availability
- **NFR-011:** Target uptime: 99.5%
- **NFR-012:** Deployment on Vercel (frontend) and Render (backend) with Supabase (database)

### 4.5 Usability
- **NFR-013:** Responsive design for desktop and tablet
- **NFR-014:** Spanish language UI (primary), English optional
- **NFR-015:** Consistent with Material-UI design patterns (existing)

---

## 5. Technical Architecture

### 5.1 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  React 19 + TypeScript + Material-UI + React Router + Axios     │
│  Hosted on: Vercel                                               │
├─────────────────────────────────────────────────────────────────┤
│                         BACKEND                                  │
│  FastAPI + Pydantic + psycopg2 + python-jose                    │
│  Hosted on: Render                                               │
├─────────────────────────────────────────────────────────────────┤
│                        DATABASE                                  │
│  PostgreSQL (Supabase)                                          │
│  + File Storage (Supabase Storage or S3)                        │
├─────────────────────────────────────────────────────────────────┤
│                     EXTERNAL SERVICES                            │
│  - OCR/AI: OpenAI Vision API or Anthropic Claude                │
│  - Image Processing: remove.bg API or rembg library             │
│  - PDF Generation: WeasyPrint or ReportLab                      │
│  - Email: SendGrid or AWS SES                                    │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Database Schema (New Tables)

```sql
-- Niches (client types)
CREATE TABLE niches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Categories (product categories, hierarchical)
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES categories(id),
    icon VARCHAR(50),
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Suppliers
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100) DEFAULT 'China',
    wechat_id VARCHAR(100),
    email VARCHAR(255),
    website VARCHAR(500),
    contact_person VARCHAR(200),
    phone VARCHAR(50),
    trade_fair_origin VARCHAR(200),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Products (Biblia General)
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    supplier_id UUID NOT NULL REFERENCES suppliers(id),
    category_id UUID REFERENCES categories(id),
    price_fob_usd DECIMAL(12,2),
    moq INT,
    hs_code VARCHAR(20),
    material VARCHAR(200),
    dimensions VARCHAR(200),
    weight_kg DECIMAL(8,2),
    is_customizable BOOLEAN DEFAULT false,
    lead_time_days INT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(supplier_id, sku)
);

-- Product Images
CREATE TABLE product_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    url VARCHAR(1000) NOT NULL,
    is_primary BOOLEAN DEFAULT false,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tags
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    color VARCHAR(7) DEFAULT '#1e3a5f',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Product Tags (many-to-many)
CREATE TABLE product_tags (
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, tag_id)
);

-- Portfolios
CREATE TABLE portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    niche_id UUID REFERENCES niches(id),
    cover_image_url VARCHAR(1000),
    status VARCHAR(20) DEFAULT 'draft',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Portfolio Items
CREATE TABLE portfolio_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    sort_order INT DEFAULT 0,
    curator_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(portfolio_id, product_id)
);

-- Clients
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(200),
    email VARCHAR(255),
    phone VARCHAR(50),
    whatsapp VARCHAR(50),
    niche_id UUID REFERENCES niches(id),
    project_name VARCHAR(255),
    project_deadline DATE,
    incoterm_preference VARCHAR(10) DEFAULT 'FOB',
    status VARCHAR(30) DEFAULT 'lead',
    source VARCHAR(100),
    notes TEXT,
    assigned_to UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- HS Codes with tariff rates
CREATE TABLE hs_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    tariff_percentage DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Freight Rates
CREATE TABLE freight_rates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    origin_port VARCHAR(100) NOT NULL,
    destination_city VARCHAR(100) NOT NULL,
    container_type VARCHAR(20) NOT NULL,
    rate_usd DECIMAL(12,2) NOT NULL,
    valid_from DATE NOT NULL,
    valid_to DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Pricing Settings
CREATE TABLE pricing_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(100) NOT NULL UNIQUE,
    value DECIMAL(12,4) NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by UUID REFERENCES users(id)
);

-- Quotations
CREATE TABLE quotations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quote_number VARCHAR(50) NOT NULL UNIQUE,
    client_id UUID NOT NULL REFERENCES clients(id),
    version INT DEFAULT 1,
    incoterm VARCHAR(10) NOT NULL,
    exchange_rate DECIMAL(10,2) NOT NULL,
    subtotal_fob_usd DECIMAL(14,2) NOT NULL,
    total_tariffs_cop DECIMAL(14,2) NOT NULL,
    total_freight_intl_usd DECIMAL(14,2) NOT NULL,
    total_freight_national_cop DECIMAL(14,2) NOT NULL,
    inspection_cost_usd DECIMAL(10,2) DEFAULT 0,
    insurance_cop DECIMAL(12,2) DEFAULT 0,
    nationalization_cop DECIMAL(12,2) DEFAULT 0,
    margin_percentage DECIMAL(5,2) NOT NULL,
    margin_cop DECIMAL(14,2) NOT NULL,
    total_cop DECIMAL(16,2) NOT NULL,
    status VARCHAR(30) DEFAULT 'draft',
    valid_until DATE,
    notes TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Quotation Line Items
CREATE TABLE quotation_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quotation_id UUID NOT NULL REFERENCES quotations(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id),
    quantity INT NOT NULL,
    unit_price_fob_usd DECIMAL(12,2) NOT NULL,
    line_total_fob_usd DECIMAL(14,2) NOT NULL,
    hs_code VARCHAR(20),
    tariff_percentage DECIMAL(5,2),
    notes TEXT,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_products_supplier ON products(supplier_id);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_status ON products(status);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_clients_status ON clients(status);
CREATE INDEX idx_clients_niche ON clients(niche_id);
CREATE INDEX idx_quotations_client ON quotations(client_id);
CREATE INDEX idx_quotations_status ON quotations(status);
CREATE INDEX idx_portfolio_items_portfolio ON portfolio_items(portfolio_id);
```

### 5.3 API Endpoints (New)

#### Suppliers
- `GET /api/suppliers` - List suppliers (paginated, filterable)
- `GET /api/suppliers/{id}` - Get supplier detail
- `POST /api/suppliers` - Create supplier
- `PUT /api/suppliers/{id}` - Update supplier
- `DELETE /api/suppliers/{id}` - Soft delete supplier

#### Products
- `GET /api/products` - List products (paginated, filterable)
- `GET /api/products/{id}` - Get product detail
- `POST /api/products` - Create product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Soft delete product
- `POST /api/products/extract` - Extract products from uploaded file (AI)
- `POST /api/products/{id}/images` - Upload product image
- `DELETE /api/products/{id}/images/{image_id}` - Delete product image

#### Categories
- `GET /api/categories` - List categories (tree structure)
- `POST /api/categories` - Create category
- `PUT /api/categories/{id}` - Update category
- `DELETE /api/categories/{id}` - Delete category

#### Tags
- `GET /api/tags` - List tags
- `POST /api/tags` - Create tag
- `PUT /api/tags/{id}` - Update tag
- `DELETE /api/tags/{id}` - Delete tag

#### Portfolios
- `GET /api/portfolios` - List portfolios
- `GET /api/portfolios/{id}` - Get portfolio with products
- `POST /api/portfolios` - Create portfolio
- `PUT /api/portfolios/{id}` - Update portfolio
- `DELETE /api/portfolios/{id}` - Delete portfolio
- `POST /api/portfolios/{id}/items` - Add products to portfolio
- `DELETE /api/portfolios/{id}/items/{item_id}` - Remove product from portfolio
- `GET /api/portfolios/{id}/export/pdf` - Generate PDF export
- `GET /api/portfolios/share/{share_token}` - Public portfolio view

#### Clients
- `GET /api/clients` - List clients (paginated, filterable)
- `GET /api/clients/{id}` - Get client detail
- `POST /api/clients` - Create client
- `PUT /api/clients/{id}` - Update client
- `DELETE /api/clients/{id}` - Soft delete client
- `GET /api/clients/pipeline` - Get clients grouped by status (Kanban)

#### Quotations
- `GET /api/quotations` - List quotations
- `GET /api/quotations/{id}` - Get quotation detail
- `POST /api/quotations` - Create quotation
- `PUT /api/quotations/{id}` - Update quotation
- `POST /api/quotations/{id}/calculate` - Recalculate pricing
- `POST /api/quotations/{id}/clone` - Clone quotation (new version)
- `GET /api/quotations/{id}/export/pdf` - Generate PDF proforma
- `POST /api/quotations/{id}/send` - Send quotation via email
- `GET /api/quotations/share/{share_token}` - Public quotation view

#### Pricing Configuration
- `GET /api/pricing/hs-codes` - List HS codes
- `POST /api/pricing/hs-codes` - Create HS code
- `PUT /api/pricing/hs-codes/{id}` - Update HS code
- `GET /api/pricing/freight-rates` - List freight rates
- `POST /api/pricing/freight-rates` - Create freight rate
- `PUT /api/pricing/freight-rates/{id}` - Update freight rate
- `GET /api/pricing/settings` - Get pricing settings
- `PUT /api/pricing/settings` - Update pricing settings

#### Dashboard
- `GET /api/dashboard/stats` - Get KPI statistics
- `GET /api/dashboard/activity` - Get recent activity feed

#### Niches
- `GET /api/niches` - List niches
- `POST /api/niches` - Create niche
- `PUT /api/niches/{id}` - Update niche

---

## 6. User Interface Specifications

### 6.1 Navigation Structure

```
Sidebar Menu:
├── Dashboard
├── Suppliers
│   ├── List
│   └── Add New
├── Products (Biblia General)
│   ├── Catalog View
│   ├── Add New
│   └── Import from File
├── Portfolios
│   ├── All Portfolios
│   └── Create Portfolio
├── Clients
│   ├── Pipeline (Kanban)
│   └── List View
├── Quotations
│   ├── All Quotations
│   └── Create Quotation
├── Settings
│   ├── Categories & Tags
│   ├── HS Codes & Tariffs
│   ├── Freight Rates
│   └── Pricing Settings
└── Users (Admin only)
```

### 6.2 Key Screens

#### 6.2.1 Product Catalog (Biblia General)
- **Grid View:** Card layout with product image, name, SKU, price, supplier
- **Table View:** Sortable columns, bulk actions
- **Filter Panel:** Category tree, supplier dropdown, price range slider, tags multi-select, status
- **Search Bar:** Full-text search with instant results
- **Import Button:** Opens file upload modal for AI extraction

#### 6.2.2 Product Import Wizard
1. **Upload Step:** Drag-and-drop area for PDF/Excel/images
2. **Processing Step:** Progress indicator, AI extraction status
3. **Review Step:** Editable table of extracted products, validation errors highlighted
4. **Confirmation Step:** Summary of products to import, duplicates warning

#### 6.2.3 Portfolio Builder
- **Left Panel:** Product search/filter (mini catalog view)
- **Right Panel:** Current portfolio with drag-to-reorder
- **Top Bar:** Portfolio name, niche selector, status toggle
- **Actions:** Preview PDF, Copy share link, Export

#### 6.2.4 Quotation Creator
1. **Client Selection:** Search existing or create new client
2. **Product Selection:** Browse Biblia or select from Portfolio
3. **Line Items Table:** Product, quantity (editable), unit price, line total
4. **Pricing Panel:** Live calculation with all cost components
5. **Summary:** Grand total in COP, payment terms, validity
6. **Actions:** Save Draft, Generate PDF, Send via Email

#### 6.2.5 Client Pipeline (Kanban)
- **Columns:** Lead → Qualified → Quoting → Negotiating → Won / Lost
- **Cards:** Company name, contact, niche badge, last activity date
- **Drag-and-Drop:** Move between columns with confirmation

---

## 7. Implementation Phases

### Phase 1: Foundation (Weeks 1-3)
**Goal:** Core data management for Suppliers and Products

- Database schema migration
- Suppliers CRUD (backend + frontend)
- Products CRUD (backend + frontend)
- Categories and Tags management
- Product catalog UI (grid/table views, filtering)
- Basic image upload to Supabase Storage

**Deliverables:**
- Suppliers list and detail pages
- Products catalog with filters
- Manual product creation flow

---

### Phase 2: Data Extraction (Weeks 4-5)
**Goal:** AI-assisted catalog import

- File upload infrastructure
- Integration with AI service (Claude/OpenAI) for OCR
- Extraction review UI
- Background image processing (remove.bg or rembg)
- Batch import workflow

**Deliverables:**
- Import wizard for PDF/Excel/images
- Extracted data review and edit screen
- Automated image background removal

---

### Phase 3: Portfolios (Weeks 6-7)
**Goal:** Curated portfolio management

- Portfolio CRUD
- Portfolio builder UI
- PDF generation with WeasyPrint
- Shareable portfolio links (public routes)
- Portfolio duplication for clients

**Deliverables:**
- Portfolio builder interface
- PDF export with branding
- Public portfolio view page

---

### Phase 4: Clients & CRM (Week 8)
**Goal:** Client management and pipeline tracking

- Clients CRUD
- Niches configuration
- Kanban pipeline view
- Status change tracking
- Client detail page with history

**Deliverables:**
- Client list and Kanban views
- Client creation/edit forms
- Activity timeline per client

---

### Phase 5: Quotations (Weeks 9-11)
**Goal:** Automated quotation system

- HS codes and tariff management
- Freight rates management
- Pricing settings configuration
- Quotation creator with live pricing
- PDF proforma generation
- Email sending integration
- Quotation versioning

**Deliverables:**
- Full quotation workflow
- PDF proforma with branding
- Email delivery from system

---

### Phase 6: Dashboard & Polish (Week 12)
**Goal:** Analytics and refinement

- Dashboard with KPIs
- Activity feed
- Performance optimization
- Bug fixes and UI polish
- User acceptance testing

**Deliverables:**
- Analytics dashboard
- Production-ready application

---

## 8. Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| AI extraction accuracy | High | Medium | Human review step before saving; continuous model tuning |
| Complex pricing formula errors | High | Medium | Extensive testing; manual override capability; audit logs |
| Performance with large catalogs | Medium | Low | Pagination; database indexing; caching |
| User adoption resistance | Medium | Medium | Training sessions; intuitive UI; gradual rollout |
| External API costs (OCR, image processing) | Medium | Medium | Usage limits; batch processing; alternative providers |

---

## 9. Glossary

| Term | Definition |
|------|------------|
| **Biblia General** | Master database containing all products from all suppliers |
| **Portfolio** | Curated subset of products filtered for a specific client niche |
| **FOB** | Free On Board - price at Chinese port, excluding freight |
| **CIF** | Cost, Insurance, Freight - price including shipping to destination port |
| **DDP** | Delivered Duty Paid - price including all costs to client's door |
| **HS Code** | Harmonized System code for tariff classification |
| **MOQ** | Minimum Order Quantity required by supplier |
| **Incoterm** | International Commercial Terms defining buyer/seller responsibilities |
| **Proforma** | Preliminary invoice/quotation sent before formal purchase order |

---

## 10. Appendix

### A. Sample Pricing Calculation

**Scenario:** Client in Bogotá wants 100 chairs

| Component | Value | Notes |
|-----------|-------|-------|
| Unit Price FOB | $25 USD | From supplier |
| Quantity | 100 | |
| Subtotal FOB | $2,500 USD | |
| HS Code | 9401.61 | Upholstered seats |
| Tariff Rate | 15% | Based on HS code |
| Tariff Amount | $375 USD | |
| Int'l Freight | $800 USD | Shanghai → Buenaventura |
| Nat'l Freight | $500,000 COP | Buenaventura → Bogotá |
| Inspection | $150 USD | Pre-shipment |
| Insurance | 1.5% of CIF | $55 USD |
| Nationalization | $200,000 COP | Customs broker |
| Subtotal Costs | $3,880 USD + 700,000 COP | |
| Exchange Rate | 4,200 COP/USD | |
| Subtotal COP | $16,996,000 COP | |
| Margin | 20% | |
| Margin Amount | $3,399,200 COP | |
| **Total Quote** | **$20,395,200 COP** | |

### B. File Formats Supported for Import

| Format | Extension | Extraction Method |
|--------|-----------|-------------------|
| PDF Catalog | .pdf | OCR + Vision AI |
| Excel Spreadsheet | .xlsx, .xls | Direct parsing |
| Word Document | .docx | Text extraction |
| Images | .jpg, .png | Vision AI |
| WeChat Export | .txt | Text parsing |

---

*End of PRD*
