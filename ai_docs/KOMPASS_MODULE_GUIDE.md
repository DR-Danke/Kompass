# Kompass Module Technical Guide

This document provides comprehensive technical documentation for the Kompass Portfolio & Quotation Automation System.

## Table of Contents

1. [Module Overview](#module-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Database Schema](#database-schema)
4. [API Endpoint Reference](#api-endpoint-reference)
5. [Pricing Formula Explanation](#pricing-formula-explanation)
6. [Configuration Options](#configuration-options)
7. [Deployment Notes](#deployment-notes)

---

## Module Overview

### Purpose

Kompass is a Portfolio & Quotation Automation System designed for China sourcing businesses. It provides:

- **Centralized Product Database (Biblia General)**: Master catalog of products from Chinese suppliers
- **Portfolio Curation**: Create targeted product collections for different client niches
- **Automated Quotations**: Generate professional quotations with automated pricing calculations
- **Client CRM**: Track clients through a sales pipeline with Kanban visualization
- **AI Data Extraction**: Import products from supplier catalogs via PDF, Excel, or images

### Problem Solved

| Challenge | Before Kompass | After Kompass |
|-----------|----------------|---------------|
| Extract 100 products from catalog | 8 hours | 30 minutes |
| Generate a quotation | 1 day | 15 minutes |
| Quotations per week | 1-2 | 10-15 |

### Key Metrics

- **Data Entry Reduction**: 75% less time spent on manual data entry
- **Quotation Prep Reduction**: 50% faster quotation preparation
- **Sales Capacity**: 5-10x increase in quotation output

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           FRONTEND                                   │
│                    React 19 + TypeScript + MUI                       │
│                         (Vercel)                                     │
├─────────────────────────────────────────────────────────────────────┤
│   Dashboard │ Suppliers │ Products │ Import │ Categories │ Portfolios │
│   Clients   │ Quotations │ Niches │ Pricing │ Settings                │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ HTTPS (REST API)
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           BACKEND                                    │
│                    FastAPI + Python 3.11.9                           │
│                         (Render)                                     │
├─────────────────────────────────────────────────────────────────────┤
│  API Routes:                                                         │
│  /api/suppliers  /api/products   /api/categories  /api/tags         │
│  /api/portfolios /api/clients    /api/quotations  /api/pricing      │
│  /api/niches     /api/extract    /api/dashboard                     │
├─────────────────────────────────────────────────────────────────────┤
│  Services:                                                           │
│  SupplierService  ProductService   CategoryService  TagService      │
│  PortfolioService ClientService    QuotationService PricingService  │
│  NicheService     ExtractionService DashboardService PDFService     │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ psycopg2 (Direct Connection)
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          DATABASE                                    │
│                    PostgreSQL (Supabase)                             │
├─────────────────────────────────────────────────────────────────────┤
│  Reference: niches, categories, tags, hs_codes                      │
│  Products:  suppliers, products, product_images, product_tags       │
│  Portfolios: portfolios, portfolio_items                            │
│  CRM:       clients, client_status_history                          │
│  Pricing:   freight_rates, pricing_settings                         │
│  Quotations: quotations, quotation_items                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### Overview

The Kompass module uses 16 PostgreSQL tables organized into logical groups:

| Group | Tables | Purpose |
|-------|--------|---------|
| Reference | niches, categories, tags, hs_codes | Classification and configuration data |
| Products | suppliers, products, product_images, product_tags | Product catalog |
| Portfolios | portfolios, portfolio_items | Curated product collections |
| CRM | clients, client_status_history | Client management and pipeline |
| Pricing | freight_rates, pricing_settings | Pricing configuration |
| Quotations | quotations, quotation_items | Quotation documents |

### Entity Relationship

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   niches     │     │  categories  │     │    tags      │
│              │     │  (self-ref)  │     │              │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   clients    │◄────│   products   │────►│ product_tags │
│              │     │              │     │  (junction)  │
└──────┬───────┘     └──────┬───────┘     └──────────────┘
       │                    │
       │                    ├──────────────┐
       │                    │              │
       ▼                    ▼              ▼
┌──────────────┐     ┌──────────────┐┌──────────────┐
│  quotations  │     │   suppliers  ││product_images│
│              │     │              │└──────────────┘
└──────┬───────┘     └──────────────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│quotation_items│     │  portfolios  │────►│portfolio_items│
└──────────────┘     └──────────────┘     └──────────────┘
```

### Table Definitions

#### Reference Tables

**niches** - Client types/market segments
```sql
CREATE TABLE niches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**categories** - Hierarchical product categories (self-referencing)
```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**tags** - Flexible product tagging
```sql
CREATE TABLE tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    color VARCHAR(7) DEFAULT '#000000',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**hs_codes** - Harmonized System tariff codes
```sql
CREATE TABLE hs_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    duty_rate DECIMAL(5,2) DEFAULT 0.00,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Product Tables

**suppliers** - Chinese vendor registry
```sql
CREATE TABLE suppliers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE,
    status VARCHAR(20) DEFAULT 'active' NOT NULL
        CHECK (status IN ('active', 'inactive', 'pending_review')),
    contact_name VARCHAR(200),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100) DEFAULT 'China',
    website VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**products** - Master product database (Biblia General)
```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    supplier_id UUID NOT NULL REFERENCES suppliers(id) ON DELETE RESTRICT,
    category_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    hs_code_id UUID REFERENCES hs_codes(id) ON DELETE SET NULL,
    status VARCHAR(20) DEFAULT 'draft' NOT NULL
        CHECK (status IN ('active', 'inactive', 'draft', 'discontinued')),
    unit_cost DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    unit_price DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'USD',
    unit_of_measure VARCHAR(50) DEFAULT 'piece',
    minimum_order_qty INTEGER DEFAULT 1,
    lead_time_days INTEGER,
    weight_kg DECIMAL(10,3),
    dimensions VARCHAR(100),
    origin_country VARCHAR(100) DEFAULT 'China',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**product_images** - Product image gallery
```sql
CREATE TABLE product_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    url VARCHAR(1000) NOT NULL,
    alt_text VARCHAR(500),
    sort_order INTEGER DEFAULT 0,
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**product_tags** - Many-to-many junction table
```sql
CREATE TABLE product_tags (
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (product_id, tag_id)
);
```

#### Portfolio Tables

**portfolios** - Curated product collections
```sql
CREATE TABLE portfolios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    niche_id UUID REFERENCES niches(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**portfolio_items** - Products within portfolios
```sql
CREATE TABLE portfolio_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    sort_order INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (portfolio_id, product_id)
);
```

#### CRM Tables

**clients** - Client/prospect registry
```sql
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(200),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    niche_id UUID REFERENCES niches(id) ON DELETE SET NULL,
    status VARCHAR(20) DEFAULT 'prospect' NOT NULL
        CHECK (status IN ('active', 'inactive', 'prospect')),
    notes TEXT,
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    source VARCHAR(50) CHECK (source IN ('website', 'referral', 'cold_call',
        'trade_show', 'linkedin', 'other')),
    project_deadline DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**client_status_history** - CRM audit trail
```sql
CREATE TABLE client_status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    notes TEXT,
    changed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Pricing Tables

**freight_rates** - Shipping rates by route
```sql
CREATE TABLE freight_rates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    origin VARCHAR(200) NOT NULL,
    destination VARCHAR(200) NOT NULL,
    incoterm VARCHAR(10) DEFAULT 'FOB' NOT NULL
        CHECK (incoterm IN ('FOB', 'CIF', 'EXW', 'DDP', 'DAP', 'CFR', 'CPT', 'CIP', 'DAT', 'FCA', 'FAS')),
    rate_per_kg DECIMAL(10,4),
    rate_per_cbm DECIMAL(10,2),
    minimum_charge DECIMAL(12,2) DEFAULT 0.00,
    transit_days INTEGER,
    is_active BOOLEAN DEFAULT true NOT NULL,
    valid_from DATE,
    valid_until DATE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**pricing_settings** - Global pricing parameters
```sql
CREATE TABLE pricing_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value DECIMAL(12,4) NOT NULL,
    description TEXT,
    is_percentage BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Quotation Tables

**quotations** - Client quotations
```sql
CREATE TABLE quotations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quotation_number VARCHAR(50) NOT NULL UNIQUE,
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE RESTRICT,
    status VARCHAR(20) DEFAULT 'draft' NOT NULL
        CHECK (status IN ('draft', 'sent', 'accepted', 'rejected', 'expired')),
    incoterm VARCHAR(10) DEFAULT 'FOB' NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    subtotal DECIMAL(14,2) DEFAULT 0.00,
    freight_cost DECIMAL(14,2) DEFAULT 0.00,
    insurance_cost DECIMAL(14,2) DEFAULT 0.00,
    other_costs DECIMAL(14,2) DEFAULT 0.00,
    total DECIMAL(14,2) DEFAULT 0.00,
    discount_percent DECIMAL(5,2) DEFAULT 0.00,
    discount_amount DECIMAL(14,2) DEFAULT 0.00,
    grand_total DECIMAL(14,2) DEFAULT 0.00,
    notes TEXT,
    terms_and_conditions TEXT,
    valid_from DATE,
    valid_until DATE,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**quotation_items** - Line items in quotations
```sql
CREATE TABLE quotation_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quotation_id UUID NOT NULL REFERENCES quotations(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    sku VARCHAR(100),
    product_name VARCHAR(500) NOT NULL,
    description TEXT,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_of_measure VARCHAR(50) DEFAULT 'piece',
    unit_cost DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    unit_price DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    markup_percent DECIMAL(5,2) DEFAULT 0.00,
    tariff_percent DECIMAL(5,2) DEFAULT 0.00,
    tariff_amount DECIMAL(12,2) DEFAULT 0.00,
    freight_amount DECIMAL(12,2) DEFAULT 0.00,
    line_total DECIMAL(14,2) NOT NULL DEFAULT 0.00,
    sort_order INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Key Indexes

All tables include indexes for:
- Primary key lookups (UUID)
- Foreign key relationships
- Status and active flags for filtering
- Name/code fields for search operations
- Timestamp fields for sorting

---

## API Endpoint Reference

### Suppliers API (`/api/suppliers`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/suppliers` | List suppliers (paginated, filterable) |
| GET | `/api/suppliers/{id}` | Get supplier by ID |
| POST | `/api/suppliers` | Create new supplier |
| PUT | `/api/suppliers/{id}` | Update supplier |
| DELETE | `/api/suppliers/{id}` | Delete supplier |

### Products API (`/api/products`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | List products with filters |
| GET | `/api/products/{id}` | Get product by ID |
| POST | `/api/products` | Create product |
| PUT | `/api/products/{id}` | Update product |
| DELETE | `/api/products/{id}` | Delete product |
| POST | `/api/products/{id}/images` | Add product image |
| DELETE | `/api/products/{id}/images/{image_id}` | Remove product image |
| POST | `/api/products/{id}/tags` | Add tag to product |
| DELETE | `/api/products/{id}/tags/{tag_id}` | Remove tag from product |
| POST | `/api/products/bulk` | Bulk create products |

### Categories API (`/api/categories`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories` | List categories |
| GET | `/api/categories/tree` | Get hierarchical tree |
| GET | `/api/categories/{id}` | Get category by ID |
| POST | `/api/categories` | Create category |
| PUT | `/api/categories/{id}` | Update category |
| DELETE | `/api/categories/{id}` | Delete category |

### Tags API (`/api/tags`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tags` | List all tags |
| GET | `/api/tags/{id}` | Get tag by ID |
| POST | `/api/tags` | Create tag |
| PUT | `/api/tags/{id}` | Update tag |
| DELETE | `/api/tags/{id}` | Delete tag |

### Portfolios API (`/api/portfolios`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/portfolios` | List portfolios |
| GET | `/api/portfolios/{id}` | Get portfolio with items |
| POST | `/api/portfolios` | Create portfolio |
| PUT | `/api/portfolios/{id}` | Update portfolio |
| DELETE | `/api/portfolios/{id}` | Delete portfolio |
| POST | `/api/portfolios/{id}/items` | Add product to portfolio |
| DELETE | `/api/portfolios/{id}/items/{item_id}` | Remove item |
| PUT | `/api/portfolios/{id}/reorder` | Reorder items |
| POST | `/api/portfolios/{id}/duplicate` | Duplicate portfolio |
| GET | `/api/portfolios/{id}/share-token` | Get share token |
| GET | `/api/portfolios/public/{token}` | Get by share token (public) |
| GET | `/api/portfolios/{id}/pdf` | Export to PDF |

### Clients API (`/api/clients`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/clients` | List clients |
| GET | `/api/clients/pipeline` | Get Kanban pipeline view |
| GET | `/api/clients/{id}` | Get client by ID |
| GET | `/api/clients/{id}/quotations` | Get client with quotation history |
| POST | `/api/clients` | Create client |
| PUT | `/api/clients/{id}` | Update client |
| DELETE | `/api/clients/{id}` | Delete client |
| POST | `/api/clients/{id}/status` | Change status (with history) |
| GET | `/api/clients/{id}/history` | Get status history |
| GET | `/api/clients/{id}/timing` | Check project timing feasibility |

### Quotations API (`/api/quotations`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/quotations` | List quotations |
| GET | `/api/quotations/{id}` | Get quotation by ID |
| POST | `/api/quotations` | Create quotation |
| PUT | `/api/quotations/{id}` | Update quotation |
| DELETE | `/api/quotations/{id}` | Delete quotation |
| POST | `/api/quotations/{id}/items` | Add line item |
| PUT | `/api/quotations/{id}/items/{item_id}` | Update line item |
| DELETE | `/api/quotations/{id}/items/{item_id}` | Remove line item |
| POST | `/api/quotations/{id}/status` | Change status |
| POST | `/api/quotations/{id}/clone` | Clone quotation |
| GET | `/api/quotations/{id}/pricing` | Calculate pricing |
| POST | `/api/quotations/{id}/recalculate` | Recalculate and persist |
| GET | `/api/quotations/{id}/pdf` | Generate PDF |
| GET | `/api/quotations/{id}/share-token` | Get share token |
| GET | `/api/quotations/public/{token}` | Get by share token (public) |
| POST | `/api/quotations/{id}/send-email` | Send via email |

### Pricing API (`/api/pricing`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/pricing/hs-codes` | List HS codes |
| GET | `/api/pricing/hs-codes/{id}` | Get HS code |
| POST | `/api/pricing/hs-codes` | Create HS code |
| PUT | `/api/pricing/hs-codes/{id}` | Update HS code |
| GET | `/api/pricing/freight-rates` | List freight rates |
| POST | `/api/pricing/freight-rates` | Create freight rate |
| PUT | `/api/pricing/freight-rates/{id}` | Update freight rate |
| GET | `/api/pricing/settings` | Get all settings |
| PUT | `/api/pricing/settings/{key}` | Update setting |

### Niches API (`/api/niches`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/niches` | List niches |
| GET | `/api/niches/{id}` | Get niche by ID |
| POST | `/api/niches` | Create niche |
| PUT | `/api/niches/{id}` | Update niche |
| DELETE | `/api/niches/{id}` | Delete niche |

### Extraction API (`/api/extract`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/extract/upload` | Upload file for extraction |
| GET | `/api/extract/jobs/{job_id}` | Get extraction job status |
| POST | `/api/extract/jobs/{job_id}/confirm` | Confirm and import products |

### Dashboard API (`/api/dashboard`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | Get KPIs and statistics |
| GET | `/api/dashboard/quotations-by-status` | Get quotation status chart data |
| GET | `/api/dashboard/quotation-trend` | Get quotation trend data |
| GET | `/api/dashboard/top-products` | Get top quoted products |

---

## Pricing Formula Explanation

### Complete Formula

The pricing engine calculates the total cost in Colombian Pesos (COP) using:

```
Total COP = (
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

### Component Breakdown

| Component | Source | Description |
|-----------|--------|-------------|
| **FOB Price** | Product unit_price × quantity | Base product cost in USD |
| **Tariff** | HS Code duty_rate % × FOB | Import duties based on product classification |
| **Int'l Freight** | freight_rates table or quotation.freight_cost | Shipping from China to Colombia |
| **Inspection** | pricing_settings.inspection_cost_usd | Pre-shipment quality inspection |
| **Insurance** | pricing_settings.insurance_percentage % × (FOB + Freight) | Cargo insurance |
| **Exchange Rate** | pricing_settings.exchange_rate_usd_cop | USD to COP conversion |
| **National Freight** | quotation.other_costs | Domestic shipping in Colombia |
| **Nationalization** | pricing_settings.nationalization_cost_cop | Customs clearance costs |
| **Margin** | pricing_settings.default_margin_percentage % | Commercial profit margin |

### Default Settings

| Setting Key | Default Value | Description |
|-------------|---------------|-------------|
| `exchange_rate_usd_cop` | 4200.0 | USD to COP exchange rate |
| `default_margin_percentage` | 20.0% | Profit margin |
| `insurance_percentage` | 1.5% | Insurance rate |
| `inspection_cost_usd` | $150 | Inspection cost per shipment |
| `nationalization_cost_cop` | 200,000 COP | Customs processing fee |

### Pricing Calculation Flow

```python
# 1. Calculate line items subtotal
subtotal_fob_usd = sum(item.unit_price * item.quantity for item in items)

# 2. Calculate tariffs
tariff_total_usd = sum(
    (item.unit_price * item.quantity) * (item.tariff_percent / 100)
    for item in items
)

# 3. Get freight and insurance
freight_intl_usd = quotation.freight_cost
insurance_usd = (subtotal_fob_usd + freight_intl_usd) * insurance_percentage / 100

# 4. Convert to COP
subtotal_cop = (
    subtotal_fob_usd + tariff_total_usd + freight_intl_usd +
    inspection_usd + insurance_usd
) * exchange_rate

# 5. Add local costs
total_before_margin = subtotal_cop + national_freight_cop + nationalization_cop

# 6. Apply margin
margin_cop = total_before_margin * margin_percentage / 100
total_cop = total_before_margin + margin_cop
```

---

## Configuration Options

### Environment Variables

#### Backend Required

```bash
# Database
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres

# Authentication
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# CORS (JSON array format)
CORS_ORIGINS=["http://localhost:5173","https://your-app.vercel.app"]

# Python version (critical for Render)
PYTHON_VERSION=3.11.9
```

#### Backend Optional

```bash
# Email (mock mode if not configured)
EMAIL_MOCK_MODE=true
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-email
SMTP_PASSWORD=your-password

# AI Extraction (for Import Wizard)
OPENAI_API_KEY=sk-...
```

#### Frontend Required

```bash
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Kompass
```

### Pricing Settings

Managed via `/api/pricing/settings` endpoint or database directly:

| Key | Type | Default | Purpose |
|-----|------|---------|---------|
| `exchange_rate_usd_cop` | Decimal | 4200.0 | Currency conversion |
| `default_margin_percentage` | Percentage | 20.0 | Profit margin |
| `insurance_percentage` | Percentage | 1.5 | Insurance calculation |
| `inspection_cost_usd` | Decimal | 150.0 | Fixed inspection fee |
| `nationalization_cost_cop` | Decimal | 200000.0 | Customs processing |

### HS Codes Configuration

HS codes determine tariff rates. Configure via `/api/pricing/hs-codes`:

```json
{
  "code": "8544.42",
  "description": "Electric conductors with connectors",
  "duty_rate": 15.00,
  "notes": "Common for LED lighting cables"
}
```

### Freight Rates Configuration

Configure shipping routes via `/api/pricing/freight-rates`:

```json
{
  "origin": "Shanghai",
  "destination": "Buenaventura",
  "incoterm": "FOB",
  "rate_per_kg": 2.50,
  "rate_per_cbm": 450.00,
  "minimum_charge": 150.00,
  "transit_days": 35,
  "is_active": true,
  "valid_from": "2024-01-01",
  "valid_until": "2024-12-31"
}
```

---

## Deployment Notes

### Backend (Render)

**Configuration:**
- Root Directory: `apps/Server`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Critical Settings:**
- Set `PYTHON_VERSION=3.11.9` in environment variables
- Ensure `DATABASE_URL` points to Supabase connection string
- Configure `CORS_ORIGINS` as JSON array with production frontend URL

### Frontend (Vercel)

**Configuration:**
- Root Directory: `apps/Client`
- Build Command: `npm run build`
- Output Directory: `dist`
- Framework Preset: Vite

**Environment Variables:**
- `VITE_API_URL`: Backend API URL (e.g., `https://your-api.onrender.com/api`)

### Database (Supabase)

**Setup:**
1. Create new Supabase project
2. Get connection string from Settings > Database
3. Run `database/schema.sql` to initialize tables
4. Configure RLS policies if needed (optional for this app)

**Connection String Format:**
```
postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
```

### Status Workflows

#### Quotation Status Transitions

```
draft ─────► sent
              │
              ├──► viewed ──┬──► negotiating ──┬──► accepted
              │             │                  │
              │             │                  └──► rejected
              │             │
              │             └──► accepted
              │             └──► rejected
              │             └──► expired
              │
              ├──► accepted
              ├──► rejected
              └──► expired
```

Valid transitions:
- `draft` → `sent`
- `sent` → `viewed`, `accepted`, `rejected`, `expired`
- `viewed` → `negotiating`, `accepted`, `rejected`, `expired`
- `negotiating` → `accepted`, `rejected`, `expired`

#### Client Pipeline Status

```
lead ──► qualified ──► quoting ──► negotiating ──┬──► won
                                                 │
                                                 └──► lost
```

### Share Token Pattern

Both portfolios and quotations support public sharing via JWT tokens:

1. Generate token: `GET /api/{resource}/{id}/share-token`
2. Access publicly: `GET /api/{resource}/public/{token}`

Tokens expire after 30 days and include:
- Resource ID in payload
- Token type for validation
- Expiration timestamp

---

## File Structure

```
├── apps/
│   ├── Client/
│   │   └── src/
│   │       ├── pages/kompass/           # 12 Kompass pages
│   │       │   ├── CategoriesPage.tsx
│   │       │   ├── ClientsPage.tsx
│   │       │   ├── ImportWizardPage.tsx
│   │       │   ├── NichesPage.tsx
│   │       │   ├── PortfolioBuilderPage.tsx
│   │       │   ├── PortfoliosPage.tsx
│   │       │   ├── PricingConfigPage.tsx
│   │       │   ├── ProductsPage.tsx
│   │       │   ├── QuotationCreatorPage.tsx
│   │       │   ├── QuotationsListPage.tsx
│   │       │   ├── SettingsPage.tsx
│   │       │   └── SuppliersPage.tsx
│   │       ├── components/kompass/      # Reusable components
│   │       ├── hooks/kompass/           # Custom hooks
│   │       ├── types/kompass.ts         # TypeScript definitions
│   │       └── services/kompassService.ts
│   └── Server/
│       └── app/
│           ├── api/                     # Route handlers
│           │   ├── supplier_routes.py
│           │   ├── product_routes.py
│           │   ├── category_routes.py
│           │   ├── tag_routes.py
│           │   ├── portfolio_routes.py
│           │   ├── client_routes.py
│           │   ├── quotation_routes.py
│           │   ├── pricing_routes.py
│           │   ├── niche_routes.py
│           │   ├── extraction_routes.py
│           │   └── dashboard_routes.py
│           ├── services/                # Business logic
│           │   ├── supplier_service.py
│           │   ├── product_service.py
│           │   ├── category_service.py
│           │   ├── tag_service.py
│           │   ├── portfolio_service.py
│           │   ├── client_service.py
│           │   ├── quotation_service.py
│           │   ├── pricing_service.py
│           │   ├── niche_service.py
│           │   ├── extraction_service.py
│           │   ├── dashboard_service.py
│           │   └── pdf_service.py
│           ├── models/kompass_dto.py    # Pydantic DTOs
│           └── repository/kompass_repository.py
├── ai_docs/
│   ├── KOMPASS_MODULE_GUIDE.md          # This file
│   ├── KOMPASS_USER_GUIDE.md            # End-user documentation
│   └── PRD-Kompass-Portfolio-Quotation-System.md
└── app_docs/                            # Feature documentation
```
