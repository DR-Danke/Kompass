# Kompass Team Onboarding Guide

Welcome to Kompass! This guide will get you up and running quickly.

---

## What is Kompass?

Kompass is our **Portfolio & Quotation Automation System** for the China sourcing business. It helps us:

- **Manage our product catalog** (Biblia General) - all products from Chinese suppliers
- **Create portfolios** - curated collections for different client types
- **Generate quotations** - professional quotes with automated pricing
- **Track clients** - CRM pipeline from lead to closed deal
- **Import products faster** - AI extracts data from supplier catalogs

### Before Kompass vs. After

| Task | Before | After |
|------|--------|-------|
| Import 100 products from catalog | 8 hours | 30 minutes |
| Create a quotation | 1 day | 15 minutes |
| Quotations per week | 1-2 | 10-15 |

---

## Getting Started (15 minutes)

### Step 1: Log In

1. Open your browser (Chrome recommended)
2. Go to the Kompass URL (provided by your admin)
3. Enter your email and password
4. Click **Login**

### Step 2: Explore the Dashboard

After login, you'll see the Dashboard:

- **KPI Cards** - Key metrics at a glance
- **Charts** - Quotation status, trends, top products
- **Activity Feeds** - Recent products, quotes, clients

### Step 3: Navigate with the Sidebar

The left sidebar provides access to all modules:

| Icon | Module | What It Does |
|------|--------|--------------|
| Home | Dashboard | Business overview |
| Factory | Suppliers | Chinese vendors |
| Box | Biblia General | Product catalog |
| Upload | Import Wizard | AI product import |
| Folder | Categories | Product organization |
| Grid | Portfolios | Product collections |
| People | Clients | CRM & pipeline |
| Doc | Quotations | Create quotes |
| Tag | Niches | Client segments |
| Dollar | Pricing | Costs & margins |

Click the hamburger menu (three lines) to collapse/expand the sidebar.

---

## Your First Tasks by Role

### If You're Diana (Design/Products)

**Day 1 Goals**:
1. Browse the product catalog (**Biblia General**)
2. Understand the category structure (**Categories**)
3. View an existing portfolio (**Portfolios**)

**First Week Goals**:
1. Import a small catalog via **Import Wizard**
2. Create a sample portfolio
3. Add tags to 10 products

**Go-to Guide**: [Diana's Workflows](KOMPASS_ROLE_WORKFLOWS.md#diana---design-director)

### If You're Alejandro (Commercial/Sales)

**Day 1 Goals**:
1. View the client pipeline (**Clients** - Kanban view)
2. Open an existing quotation (**Quotations**)
3. Check pricing settings (**Pricing**)

**First Week Goals**:
1. Create a quotation for a test client
2. Generate and review a PDF
3. Configure one freight rate

**Go-to Guide**: [Alejandro's Workflows](KOMPASS_ROLE_WORKFLOWS.md#alejandro---commercial-manager)

### If You're Ruben (Executive)

**Day 1 Goals**:
1. Review the Dashboard KPIs
2. Understand the pipeline stages (**Clients**)
3. Check quotation status chart

**Weekly Routine**:
1. Daily: Check Dashboard (5 min)
2. Weekly: Pipeline review meeting
3. Monthly: Trend analysis

**Go-to Guide**: [Ruben's Workflows](KOMPASS_ROLE_WORKFLOWS.md#ruben---ceofounder)

---

## Key Concepts to Understand

### Products & Organization

```
Products belong to → Categories (hierarchical)
Products have → Tags (flexible labels)
Products come from → Suppliers
Products have → HS Codes (for tariffs)
```

### Portfolios

- A **portfolio** is a curated collection of products
- Targeted at specific **niches** (client types)
- Can be shared with clients via link or PDF
- Think of it as a custom catalog for a specific audience

### Quotations

- A **quotation** is a formal price quote to a client
- Contains **line items** (products with quantities)
- **Pricing is automated** based on configured rates
- Can be shared via link, email, or PDF

### Client Pipeline

```
Lead → Qualified → Quoting → Negotiating → Won
                                           ↓
                                          Lost
```

- Drag clients between stages to track progress
- All movements are logged in history

### Pricing Components

Kompass calculates the full cost from China to Colombia:

```
FOB Price (product cost)
+ Tariff (HS code duty rate)
+ International Freight
+ Inspection ($150)
+ Insurance (1.5%)
× Exchange Rate (USD→COP)
+ National Freight
+ Nationalization (customs)
+ Margin (20%)
= Final Price to Client
```

---

## Quick Reference Card

### Creating Things

| To Create | Go To | Click |
|-----------|-------|-------|
| Supplier | Suppliers | + Add Supplier |
| Product | Biblia General | + Add Product |
| Category | Categories | + Add Category |
| Tag | Categories > Tags | + Add Tag |
| Portfolio | Portfolios | + Create Portfolio |
| Client | Clients | + Add Client |
| Quotation | Quotations | + New Quotation |
| HS Code | Pricing > HS Codes | + Add |
| Freight Rate | Pricing > Freight | + Add |

### Sharing Things

| To Share | Open It | Click |
|----------|---------|-------|
| Portfolio | Portfolio detail | Share icon |
| Quotation | Quotation detail | Share icon |
| PDF | Portfolio or Quotation | Export PDF |

### Finding Things

| To Find | Where | How |
|---------|-------|-----|
| Product | Biblia General | Search bar + filters |
| Client | Clients | Search bar |
| Quotation | Quotations | Search by quote # or client |
| Any | Anywhere | Ctrl/Cmd + K (quick search) |

---

## Common Workflows

### Workflow 1: Quick Quote (15 min)

1. **Quotations** > **+ New Quotation**
2. Select client
3. **Add Products** > Search > Add items
4. Set quantities
5. Review pricing panel
6. **Save** (draft)
7. **Generate PDF** or **Share**

### Workflow 2: Import Products (30 min)

1. **Import Wizard** > Upload PDF/Excel
2. Select supplier
3. Wait for AI extraction
4. Review & correct data
5. **Confirm Import**
6. Edit products to add images/tags

### Workflow 3: Build Portfolio (20 min)

1. **Portfolios** > **+ Create Portfolio**
2. Name it, select niche
3. **Add Products** from catalog
4. Reorder as needed
5. Add curator notes
6. Toggle **Published**
7. **Share** or **Export PDF**

---

## Do's and Don'ts

### Do

- Keep the exchange rate updated (weekly)
- Assign HS codes to products (affects pricing)
- Add images to products (helps clients)
- Use descriptive portfolio names
- Add notes when moving clients in pipeline
- Clone quotations instead of editing old ones

### Don't

- Create duplicate suppliers (search first)
- Leave products in Draft status forever
- Ignore the pricing panel warnings
- Share links for unpublished portfolios
- Delete quotations that have been sent

---

## Keyboard Shortcuts

| Keys | Action |
|------|--------|
| `Ctrl/Cmd + K` | Quick search |
| `Esc` | Close dialog |
| `Enter` | Confirm |
| `Tab` | Next field |

---

## Where to Get Help

| Need | Resource |
|------|----------|
| Step-by-step instructions | [User Guide](KOMPASS_USER_GUIDE.md) |
| Quick answers | [Quick Reference](KOMPASS_QUICK_REFERENCE.md) |
| Role-specific workflows | [Role Workflows](KOMPASS_ROLE_WORKFLOWS.md) |
| Problem solving | [Troubleshooting FAQ](KOMPASS_TROUBLESHOOTING_FAQ.md) |
| Technical details | [Module Guide](KOMPASS_MODULE_GUIDE.md) |
| Human help | Your system administrator |

---

## Your Onboarding Checklist

### Day 1

- [ ] Log in successfully
- [ ] Explore Dashboard
- [ ] Navigate all sidebar modules
- [ ] Open and view a product
- [ ] Open and view a quotation
- [ ] Open and view the client pipeline

### Week 1

- [ ] Complete your role-specific first week goals
- [ ] Create at least one item (product, quote, or portfolio)
- [ ] Understand the pricing formula
- [ ] Read the relevant sections of the User Guide
- [ ] Ask questions about anything unclear

### Month 1

- [ ] Feel comfortable with daily tasks
- [ ] Know where to find help
- [ ] Suggest one improvement (we love feedback!)

---

## Quick Glossary

| Term | Meaning |
|------|---------|
| **Biblia General** | Master product catalog |
| **FOB** | Free On Board - price at Chinese port |
| **CIF** | Cost, Insurance, Freight included |
| **HS Code** | Harmonized System tariff code |
| **Niche** | Client market segment |
| **Pipeline** | Sales stages from lead to won |
| **Portfolio** | Curated product collection |
| **SKU** | Stock Keeping Unit - product ID |

---

Welcome to the team! You've got this.
