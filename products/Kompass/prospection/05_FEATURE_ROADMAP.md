# Feature Roadmap — Kompass

## Current State (v1.0) — Available Now

### Supplier Management
- [x] Supplier directory with contact info (name, email, phone, WeChat ID)
- [x] Pipeline status tracking (contacted → potential → quoted → certified → active)
- [x] Certification tiers (A/B/C classification)
- [x] Trade fair metadata capture (fair name, capture date, source)
- [x] Outreach status management
- [x] Product count per supplier
- [x] Kanban board visualization for supplier pipeline
- [x] Excel export with certification data

### AI Business Card Capture (Trade Fair)
- [x] Mobile-responsive photo capture from camera or file upload
- [x] AI extraction: company name, contact name, email, phone, WeChat ID, website, address
- [x] Bilingual support (Chinese/English)
- [x] Per-field confidence scoring with visual badges (green/yellow/red)
- [x] QR code detection for WeChat ID extraction
- [x] Auto-create supplier from extracted card data
- [x] Status workflow: pending → processing → extracted → confirmed → rejected
- [x] Manual retry capability
- [x] Recent captures list

### AI Factory Audit Analysis
- [x] PDF upload for factory audit documents (up to 25MB)
- [x] AI extraction of 12+ data points (supplier type, employees, certifications, markets, factory area)
- [x] A/B/C certification recommendation with reasoning
- [x] Manual classification override
- [x] Audit summary cards with key metrics
- [x] Markets served visualization

### Product Catalog (Biblia General)
- [x] Full product database with SKU, name, description, unit cost (FOB USD)
- [x] Minimum order quantity (MOQ), lead time, weight, dimensions
- [x] HS code association for tariff classification
- [x] Status management: draft, active, inactive, discontinued
- [x] Hierarchical category system with sub-categories
- [x] Flexible tagging with color coding
- [x] Multiple product images (primary + gallery) via Supabase Storage
- [x] Supplier association per product
- [x] Grid view (visual) and table view (data)
- [x] Full-text search with multi-filter (category, supplier, price range, MOQ, tags, status)

### AI Product Import Wizard
- [x] File format support: PDF catalogs, Excel spreadsheets, Word documents, images
- [x] AI extraction: SKU, name, description, price, MOQ, dimensions, material, category suggestions
- [x] Multi-provider AI (Anthropic Claude + OpenAI GPT-4o with fallback)
- [x] Review extracted products before import
- [x] Validation report (success/error counts)
- [x] Batch import with atomicity

### Portfolios (Curated Collections)
- [x] Named collections targeting specific client niches
- [x] Add/remove products with sort order and curator notes
- [x] Portfolio status: draft, published
- [x] PDF export with customizable templates
- [x] Shareable public web links with time-limited share tokens (30-day expiration)
- [x] Read-only client view
- [x] QR code in PDF linking to digital version
- [x] Portfolio duplication

### Client CRM & Pipeline
- [x] Client registry with contact info, WhatsApp, assigned sales rep
- [x] Lead source tracking (website, referral, cold call, trade show, LinkedIn)
- [x] Pipeline status: lead → qualified → quoting → negotiating → won/lost
- [x] Status change history with timestamps (audit trail)
- [x] Kanban board with drag-and-drop
- [x] List view toggle
- [x] Project deadline and niche classification

### Quotation System
- [x] Unique quotation numbers with multiple line items
- [x] Automated pricing engine:
  - FOB + tariffs (from HS codes) + freight + inspection + insurance × exchange rate + national freight + nationalization + margin
- [x] Per-line-item tariff calculation
- [x] Freight allocation per line item
- [x] Discount support (percentage and absolute)
- [x] Quotation lifecycle: draft → sent → viewed → negotiating → accepted/rejected/expired
- [x] Professional PDF proforma generation with branding
- [x] Email delivery to clients (SMTP with mock mode fallback)
- [x] Shareable tracking links with share tokens
- [x] All major incoterms supported (FOB, CIF, EXW, DDP, DAP, CFR, CPT, CIP, DAT, FCA, FAS)

### Pricing Configuration
- [x] HS code library with duty rates
- [x] Freight rates by route (origin/destination, rate/kg or CBM, minimum charge, validity)
- [x] Global pricing settings: margin %, inspection cost, insurance %, nationalization cost, exchange rate

### WeChat Integration
- [x] Official Account webhook receiver (verify + receive messages)
- [x] Send introduction and custom messages to suppliers
- [x] Auto-route business card photos from WeChat to extraction pipeline
- [x] Access token management with auto-refresh
- [x] Mock mode for development

### Communication & Outreach
- [x] SMTP email service (real + mock modes)
- [x] Editable outreach templates with variable substitution
- [x] Introduction, catalog request, and pricing inquiry templates
- [x] Auto-send follow-up emails after business card capture

### Dashboard & Analytics
- [x] KPI cards: total products, monthly additions, active suppliers, weekly quotations, pipeline value
- [x] Charts: quotations by status, quotation trend, top quoted products
- [x] Activity feeds: recent products, quotations, clients, trade fair captures

### Categories, Tags & Niches
- [x] Hierarchical categories with tree view
- [x] Color-coded tags with autocomplete
- [x] Market niche definitions for client segmentation

---

## Near-Term Roadmap (v1.1-1.3)

### Enhanced AI Extraction
- [ ] Multi-page PDF catalog extraction with page-by-page processing
- [ ] Image-based product recognition (photograph a product, extract specs)
- [ ] Supplier website scraping (extract product catalog from website URL)
- [ ] AI-suggested HS codes based on product description
- [ ] Business card extraction accuracy improvement via training feedback

### Quotation Workflow
- [ ] Client counter-offer workflow (digital negotiation)
- [ ] Quotation versioning (v1, v2, v3 with change tracking)
- [ ] Auto-expiration with follow-up email reminders
- [ ] Quotation cloning for repeat orders
- [ ] Multi-currency quotations (COP, USD, EUR)

### Portfolio Enhancements
- [ ] Interactive digital catalog with filtering (not just PDF)
- [ ] Client-side product inquiry from portfolio (request pricing on specific items)
- [ ] Portfolio analytics (which products get the most views)
- [ ] Custom PDF templates per client niche

### Communication
- [ ] WhatsApp Business API integration (send quotations via WhatsApp)
- [ ] Automated email sequences (follow-up after 3 days, 7 days, 14 days)
- [ ] Supplier email inbox monitoring (detect price list updates)
- [ ] SMS notifications for quotation views/acceptance

### Dashboard & Analytics
- [ ] Sales rep performance leaderboard (quotations sent, deals closed)
- [ ] Product popularity analytics (most quoted, most ordered)
- [ ] Supplier reliability scoring (lead time accuracy, quality)
- [ ] Revenue by product category/niche breakdown
- [ ] Trade fair ROI analytics (cards captured → deals closed)

---

## Mid-Term Roadmap (v2.0)

### Order Management
- [ ] Convert accepted quotation to purchase order
- [ ] Purchase order tracking (placed → confirmed → shipped → delivered)
- [ ] Supplier payment tracking
- [ ] Shipment tracking integration (container/tracking number)
- [ ] Automatic cost comparison (quoted vs. actual)

### Multi-Currency & International
- [ ] Multi-currency pricing engine (auto-convert based on incoterm)
- [ ] Country-specific import cost calculation (not just Colombia — Mexico, Peru, Chile, Ecuador)
- [ ] Regional HS code databases
- [ ] Multi-language quotation templates

### Advanced Supplier Management
- [ ] Supplier performance dashboard (quality, delivery, pricing trend)
- [ ] Automatic re-quote reminders when supplier prices change
- [ ] Supplier comparison by product (who has the best price for widget X?)
- [ ] Supplier development tracking (certifications, improvements)

### Client Intelligence
- [ ] Client purchase history analytics
- [ ] Reorder prediction (suggest replenishment timing)
- [ ] Client-specific pricing rules (VIP discounts, volume tiers)
- [ ] Client satisfaction tracking

### Integrations
- [ ] Accounting software sync (Siigo, QuickBooks — push invoices from accepted quotes)
- [ ] Shipping forwarder integration (auto-request freight quotes)
- [ ] Google Sheets export for legacy reporting
- [ ] Webhook API for custom workflows
- [ ] Zapier/Make integration for automation

### Mobile App
- [ ] Native mobile app for trade fair usage (card capture, quick product photos)
- [ ] Offline mode for trade fair floors (sync when connectivity returns)
- [ ] Push notifications for quotation views and client responses
- [ ] Quick-quote from mobile (select products, set margin, send)

---

## Long-Term Vision (v3.0+)

### AI-Powered Sales
- [ ] AI quotation assistant ("Quote this client on bathroom faucets under $10 FOB")
- [ ] AI product recommendations based on client history and niche
- [ ] AI-generated portfolio curation based on market trends
- [ ] Demand prediction per product/category
- [ ] Automated competitive pricing (adjust based on market intelligence)

### Marketplace Features
- [ ] Buyer portal (clients browse and self-serve quotation requests)
- [ ] Supplier discovery integration (find new suppliers for requested products)
- [ ] Product trend analytics (what's hot in the market)
- [ ] Cross-company product benchmarking (anonymous pricing data)

### Supply Chain Intelligence
- [ ] End-to-end cost tracking (FOB → landed cost → margin → profit)
- [ ] Currency hedging recommendations
- [ ] Tariff change alerts (HS code duty rate modifications)
- [ ] Trade regulation updates per country
- [ ] Carbon footprint estimation per shipment

### Platform Evolution
- [ ] White-label for sourcing agencies
- [ ] Multi-team support (separate catalogs per product vertical)
- [ ] API marketplace for third-party data providers
- [ ] Self-service onboarding (no launch package needed)
- [ ] Franchise model for local Kompass distributors in each LATAM country
