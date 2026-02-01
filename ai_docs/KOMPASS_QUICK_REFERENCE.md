# Kompass Quick Reference Card

A quick reference for common tasks in the Kompass Portfolio & Quotation System.

---

## Navigation Quick Links

| Module | Sidebar Icon | Keyboard | Purpose |
|--------|--------------|----------|---------|
| Dashboard | Home | - | KPIs, charts, activity |
| Suppliers | Factory | - | Chinese vendor registry |
| Products | Inventory | - | Biblia General catalog |
| Import | Upload | - | AI bulk import |
| Categories | Folder | - | Product hierarchy + tags |
| Portfolios | Collections | - | Curated collections |
| Clients | People | - | CRM pipeline |
| Quotations | Document | - | Create/manage quotes |
| Niches | Label | - | Client segments |
| Pricing | Money | - | HS codes, freight, settings |

---

## Common Tasks Cheat Sheet

### Products

| Task | Steps |
|------|-------|
| Add product | Products > + Add Product > Fill form > Save |
| Search products | Products > Type in search bar (searches name, SKU, description) |
| Filter by category | Products > Category dropdown > Select |
| Filter by tags | Products > Tags dropdown > Select multiple |
| Add image | Product detail > Images tab > Add Image |
| Assign tag | Product detail > Tags section > Add Tag |
| Bulk import | Import Wizard > Upload file > Review > Confirm |

### Quotations

| Task | Steps |
|------|-------|
| New quotation | Quotations > + New Quotation > Select client |
| Add products | Quotation editor > Add Products > Search > Click + |
| Set quantity | Click quantity field > Enter number |
| Custom price | Click unit price field > Enter price |
| Generate PDF | Quotation > Generate PDF button |
| Share link | Quotation > Share > Copy link |
| Clone quotation | Quotation > Clone > Edit as needed |
| Send email | Quotation > Send Email > Enter recipient |

### Portfolios

| Task | Steps |
|------|-------|
| Create portfolio | Portfolios > + Create Portfolio > Name it |
| Add products | Portfolio builder > + Add Products > Search > Add |
| Reorder | Drag and drop products in the builder |
| Add notes | Click product > Enter curator notes |
| Share | Portfolio > Share > Copy link |
| Export PDF | Portfolio > Export PDF |
| Duplicate | Portfolio > Duplicate > Enter new name |

### Clients

| Task | Steps |
|------|-------|
| Add client | Clients > + Add Client > Fill form |
| Move in pipeline | Drag card to new column (Kanban view) |
| View quotations | Click client > Quotations tab |
| Check timing | Client with deadline > Check Timing button |
| View history | Click client > History tab |
| Switch views | Toggle Kanban/List view button |

### Pricing Configuration

| Task | Steps |
|------|-------|
| Add HS code | Pricing > HS Codes > + Add > Enter code + rate |
| Add freight rate | Pricing > Freight Rates > + Add > Enter route |
| Update exchange rate | Pricing > Settings > exchange_rate_usd_cop > Edit |
| Change margin | Pricing > Settings > default_margin_percentage > Edit |

---

## Status Reference

### Quotation Status Flow

```
DRAFT ──► SENT ──► VIEWED ──► NEGOTIATING ──► ACCEPTED
                      │            │
                      └────────────┴──► REJECTED
                                       EXPIRED
```

| Status | Meaning | Next Steps |
|--------|---------|------------|
| Draft | Work in progress | Edit, then Send |
| Sent | Delivered to client | Wait for response |
| Viewed | Client opened it | Follow up |
| Negotiating | In discussion | Adjust terms |
| Accepted | Deal won! | Fulfill order |
| Rejected | Deal lost | Learn, move on |
| Expired | Past valid date | Clone if needed |

### Client Pipeline Stages

```
LEAD ──► QUALIFIED ──► QUOTING ──► NEGOTIATING ──► WON
                                                    │
                                                    └──► LOST
```

| Stage | Meaning | Action |
|-------|---------|--------|
| Lead | New prospect | Qualify their needs |
| Qualified | Confirmed interest | Prepare quotation |
| Quoting | Quote being prepared | Send quotation |
| Negotiating | Quote sent, discussing | Close the deal |
| Won | Deal closed | Celebrate! |
| Lost | Didn't close | Analyze why |

### Product Status

| Status | Meaning | Visibility |
|--------|---------|------------|
| Draft | Not ready | Hidden from quotations |
| Active | Available | Shown in quotations |
| Inactive | Temporarily unavailable | Hidden |
| Discontinued | No longer available | Hidden |

### Supplier Status

| Status | Meaning |
|--------|---------|
| Active | Current approved vendor |
| Inactive | No longer ordering |
| Pending Review | Under evaluation |

---

## Pricing Formula Quick Reference

```
Total COP = [
  (FOB Price x Qty)           <-- Product prices
  + Tariff                    <-- HS code duty rate %
  + International Freight     <-- Freight rates table
  + Inspection ($150)         <-- Fixed per shipment
  + Insurance (1.5%)          <-- % of (FOB + Freight)
] x Exchange Rate (4200)      <-- USD to COP
+ National Freight            <-- Domestic shipping
+ Nationalization (200K COP)  <-- Customs fee
+ Margin (20%)                <-- Profit markup
```

### Default Settings

| Setting | Default | Purpose |
|---------|---------|---------|
| Exchange Rate | 4,200 COP/USD | Currency conversion |
| Margin | 20% | Profit markup |
| Insurance | 1.5% | Cargo insurance |
| Inspection | $150 USD | Per-shipment QC |
| Nationalization | 200,000 COP | Customs processing |

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + K` | Quick search |
| `Esc` | Close modal/dialog |
| `Enter` | Confirm action |
| `Tab` | Move to next field |

---

## Data Entry Tips

### Product SKU Format
Recommended: `SUP-CAT-NNNN`
- SUP = Supplier code (3 chars)
- CAT = Category code (3 chars)
- NNNN = Sequential number

Example: `LMC-LED-0042`

### Quotation Number Format
Auto-generated: `QUO-YYYYMMDD-NNNN`

Example: `QUO-20260201-0015`

### Required Fields

| Entity | Required Fields |
|--------|-----------------|
| Supplier | Name |
| Product | Name, Supplier, Unit Cost |
| Client | Company Name |
| Quotation | Client |
| Portfolio | Name |
| Category | Name |
| Tag | Name |
| HS Code | Code, Description |
| Freight Rate | Origin, Destination |

---

## File Formats for Import

| Format | Extension | Best For |
|--------|-----------|----------|
| PDF | .pdf | Supplier catalogs |
| Excel | .xlsx, .xls | Price lists |
| Images | .jpg, .png | Product photos with text |

**Max file size**: 20 MB

---

## Share Links

### Portfolio Share Link
```
https://your-app.com/share/portfolio/{token}
```
- Valid for 30 days
- No login required
- Read-only access

### Quotation Share Link
```
https://your-app.com/share/quotation/{token}
```
- Valid for 30 days
- No login required
- Read-only access

---

## Common Filter Combinations

### Find products to quote
- Status: Active
- Category: (select relevant)
- Price range: (set min/max)

### Find urgent clients
- Pipeline: Quoting or Negotiating
- Sort by: Deadline

### Find quotations needing follow-up
- Status: Sent (no response yet)
- Date: Last 7 days

---

## Role Quick Access

### Diana (Design Director)
Primary modules: **Import Wizard**, **Products**, **Portfolios**, **Categories**

### Alejandro (Commercial Manager)
Primary modules: **Quotations**, **Pricing**, **Clients**

### Ruben (CEO)
Primary modules: **Dashboard**, **Clients** (pipeline view)

---

## Troubleshooting Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Can't find product | Check status filter (might be Draft/Inactive) |
| Price looks wrong | Check HS code assignment and freight rates |
| Share link doesn't work | Generate new token (may have expired) |
| Import failed | Check file format and size (max 20MB) |
| Client not in pipeline | Check client status (must be in CRM stages) |

---

## Getting Help

1. **User Guide**: `ai_docs/KOMPASS_USER_GUIDE.md`
2. **Technical Guide**: `ai_docs/KOMPASS_MODULE_GUIDE.md`
3. **System Admin**: Contact your administrator
