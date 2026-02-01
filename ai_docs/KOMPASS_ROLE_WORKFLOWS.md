# Kompass Role-Based Workflow Guide

This guide provides step-by-step workflows tailored for each team role.

---

## Table of Contents

1. [Diana - Design Director](#diana---design-director)
2. [Alejandro - Commercial Manager](#alejandro---commercial-manager)
3. [Ruben - CEO/Founder](#ruben---ceofounder)
4. [Cross-Team Workflows](#cross-team-workflows)

---

# Diana - Design Director

**Primary Focus**: Product catalog management, portfolio curation, visual presentation

**Key Modules**: Import Wizard, Products, Portfolios, Categories & Tags

---

## Daily Workflow

### Morning: Check New Products

1. **Dashboard** - Review "Products Added This Month" KPI
2. **Products** - Sort by "Created At" (descending) to see newest
3. Verify recently imported products have:
   - Correct categories assigned
   - Appropriate tags
   - Good quality images
   - Accurate descriptions

### Throughout Day: Manage Product Requests

When the sales team requests specific products:

1. Check if product exists in **Products** catalog
2. If not found, coordinate with supplier for catalog
3. Import using **Import Wizard** (see workflow below)

---

## Workflow: Import Products from Supplier Catalog

**Scenario**: You received a new PDF catalog from a supplier with 50+ products.

### Step 1: Prepare

1. Verify supplier exists in **Suppliers** module
2. If new supplier, create them first:
   - Click **+ Add Supplier**
   - Enter name, contact info, country
   - Set status to "Pending Review" until verified
   - Save

### Step 2: Upload Catalog

1. Go to **Import Wizard**
2. Drag and drop the PDF file (or click to browse)
3. Wait for upload to complete

### Step 3: Configure Extraction

1. Select the **Supplier** from dropdown
2. Choose **Default Category** (optional, can assign later)
3. Set **Default Status** to "Draft" (review before activating)
4. Click **Start Extraction**

### Step 4: Review Extracted Products

The AI will extract product information. Review each:

| Check | Action if Wrong |
|-------|-----------------|
| Product name | Click to edit |
| Price (FOB USD) | Click to correct |
| Description | Click to enhance |
| MOQ | Verify minimum order |
| Unit of measure | Correct if needed |

**Tips**:
- Remove duplicates by clicking the X icon
- Skip products you don't want to import
- Add missing information now (faster than editing later)

### Step 5: Assign Categories

For each product (or bulk if supported):
1. Click the category dropdown
2. Select appropriate category from tree
3. Products without categories are harder to find later

### Step 6: Confirm Import

1. Review the summary:
   - Total products to import
   - Products with warnings (missing data)
   - Products ready for import
2. Click **Confirm Import**
3. Products are added to Biblia General as "Draft"

### Step 7: Finalize Products

1. Go to **Products** > Filter by Status: Draft
2. For each imported product:
   - Add/improve images
   - Assign tags
   - Assign HS code (for pricing)
   - Review description
   - When ready, change status to "Active"

---

## Workflow: Create a Niche Portfolio

**Scenario**: Create a portfolio for hotel clients featuring bathroom fixtures.

### Step 1: Create Portfolio

1. Go to **Portfolios**
2. Click **+ Create Portfolio**
3. Enter details:
   - **Name**: "Hotel Bathrooms 2026"
   - **Description**: "Curated bathroom fixtures for hospitality projects"
   - **Niche**: Select "Hotels" (create niche first if needed)
4. Click **Create**

### Step 2: Add Products

You're now in the Portfolio Builder.

**Method A: Search and Add**
1. Use the search bar in the left panel
2. Search for relevant products: "faucet", "mirror", "towel"
3. Click **+** on products to add them

**Method B: Browse by Category**
1. Use category filter in left panel
2. Select "Bathroom" or relevant category
3. Browse and add products

### Step 3: Curate the Collection

1. **Reorder**: Drag products to arrange in best presentation order
   - Put hero products at the top
   - Group similar items together

2. **Add Notes**: Click each product to add curator notes
   - "Best seller for 5-star hotels"
   - "Available in brushed nickel"
   - "Pairs well with mirror SKU-XXX"

3. **Remove**: Click X on products that don't fit

### Step 4: Quality Check

Review the portfolio:
- Are images high quality?
- Is pricing competitive?
- Are descriptions compelling?
- Does the collection tell a story?

### Step 5: Publish

1. Toggle **Published** switch to "On"
2. The portfolio is now active and shareable

### Step 6: Share with Team/Clients

**Share Link**:
1. Click **Share** icon
2. Copy the link
3. Send to client (no login required)

**Export PDF**:
1. Click **Export PDF**
2. Download the professional PDF
3. Email or print as needed

---

## Workflow: Organize Products with Categories & Tags

### Categories: Hierarchical Structure

**Example category tree**:
```
Lighting
├── LED
│   ├── Strips
│   ├── Bulbs
│   └── Panels
├── Decorative
│   ├── Chandeliers
│   └── Pendants
└── Outdoor
    ├── Floodlights
    └── Path Lights
```

**Creating Categories**:
1. Go to **Categories**
2. Click **+ Add Category**
3. Enter name: "LED Strips"
4. Select parent: "LED"
5. Save

**Best Practices**:
- Max 3-4 levels deep
- Specific enough to be useful
- General enough to have multiple products

### Tags: Flexible Attributes

**Example tags**:
- Best Seller (green)
- New Arrival (blue)
- Clearance (red)
- Eco-Friendly (green)
- Premium (gold)
- Budget (gray)

**Creating Tags**:
1. Go to **Categories** > **Tags** tab
2. Click **+ Add Tag**
3. Enter name: "Best Seller"
4. Choose color: Green
5. Save

**Using Tags**:
- Assign multiple tags per product
- Use for cross-cutting attributes
- Filter products by tags in catalog

---

## Weekly Tasks Checklist

| Task | Frequency | Notes |
|------|-----------|-------|
| Review draft products | Daily | Activate ready products |
| Update product images | Weekly | Replace low-quality images |
| Check expired portfolios | Weekly | Update or archive old collections |
| Organize new categories | As needed | Keep hierarchy clean |
| Tag review | Monthly | Remove unused tags |

---

# Alejandro - Commercial Manager

**Primary Focus**: Client relationships, quotations, pricing accuracy

**Key Modules**: Clients, Quotations, Pricing Configuration

---

## Daily Workflow

### Morning: Pipeline Review

1. **Dashboard** - Check KPIs:
   - Quotations Sent This Week
   - Pipeline Value
   - Quotations by Status chart

2. **Clients** (Kanban view) - Review pipeline:
   - Any new leads to qualify?
   - Any stuck in "Quoting" too long?
   - Follow up on "Negotiating" clients

### Throughout Day: Respond to Quote Requests

Process incoming quotation requests efficiently using the workflow below.

---

## Workflow: Create a New Quotation

**Scenario**: A hotel client requests a quotation for bathroom fixtures.

### Step 1: Verify Client Exists

1. Go to **Clients**
2. Search for the client
3. If not found, create new client:
   - Click **+ Add Client**
   - Enter company name, contact info
   - Select **Niche**: "Hotels"
   - Set **Source**: How you found them
   - Add project deadline if known
   - Save

### Step 2: Start Quotation

1. Go to **Quotations**
2. Click **+ New Quotation**
3. Select the **Client** from dropdown
4. You'll see client info and any previous quotations

### Step 3: Configure Settings

In the quotation header:

| Setting | What to Choose |
|---------|---------------|
| **Incoterm** | FOB (default), CIF, DDP, etc. |
| **Currency** | USD (default) or COP |
| **Valid From** | Today's date |
| **Valid Until** | 30 days out (typical) |

### Step 4: Add Products

**From Search**:
1. Click **Add Products**
2. Search for products: "faucet", "mirror"
3. Click **+** to add to quotation
4. Set **Quantity** for each item

**From Portfolio** (faster for repeat requests):
1. Click **Add from Portfolio**
2. Select portfolio: "Hotel Bathrooms 2026"
3. Check products to include
4. Click **Add Selected**

### Step 5: Customize Line Items

For each line item:

| Field | Action |
|-------|--------|
| **Quantity** | Set client's order quantity |
| **Unit Price** | Adjust if giving special pricing |
| **Notes** | Add line-specific notes |

**Reorder**: Drag items to arrange logically

### Step 6: Review Pricing Panel

The right panel shows automated calculations:

```
Subtotal FOB:     $5,000 USD
+ Tariffs:        $750 USD (15% avg)
+ Int'l Freight:  $450 USD
+ Inspection:     $150 USD
+ Insurance:      $82 USD
─────────────────────────────
Subtotal USD:     $6,432 USD
× Exchange Rate:  × 4,200
─────────────────────────────
Subtotal COP:     $27,014,400 COP
+ Nat'l Freight:  $500,000 COP
+ Nationalization: $200,000 COP
+ Margin (20%):   $5,542,880 COP
─────────────────────────────
TOTAL COP:        $33,257,280 COP
```

### Step 7: Verify Pricing Accuracy

Check that:
- [ ] HS codes assigned to all products (affects tariffs)
- [ ] Freight rates are current
- [ ] Exchange rate is recent
- [ ] Margin is appropriate for this client

If pricing looks wrong, go to **Pricing** to check settings.

### Step 8: Save Draft

1. Click **Save**
2. Status is "Draft"
3. Review everything one more time

### Step 9: Send to Client

**Option A: Email directly**
1. Click **Send Email**
2. Enter client's email
3. Write a personalized message
4. Attach PDF (recommended)
5. Click **Send**

**Option B: Share link**
1. Click **Share**
2. Copy the link
3. Send via WhatsApp/email manually

**Option C: PDF only**
1. Click **Generate PDF**
2. Download
3. Send as email attachment

### Step 10: Update Status

After sending:
1. Click **Send** button to change status
2. Status becomes "Sent"
3. Quotation is now tracked

---

## Workflow: Follow Up on Quotations

### Step 1: Find Pending Quotations

1. Go to **Quotations**
2. Filter by Status: **Sent**
3. Sort by date (oldest first)

### Step 2: Review Each

For each quotation past follow-up date:

| Days Since Sent | Action |
|-----------------|--------|
| 2-3 days | Send gentle reminder |
| 5-7 days | Call to discuss |
| 10+ days | Final follow-up, then move on |

### Step 3: Update Status

Based on client response:

| Client Said | New Status |
|-------------|------------|
| "Let me review" | Viewed |
| "Can you adjust X?" | Negotiating |
| "We accept!" | Accepted |
| "Not interested" | Rejected |
| No response past valid date | Expired |

To change status:
1. Open quotation
2. Click current status badge
3. Select new status
4. Add notes (optional)

---

## Workflow: Clone a Quotation

**Scenario**: Client wants a revised quotation with different quantities.

1. Open the original quotation
2. Click **Clone**
3. A new draft is created with:
   - Same client
   - Same products
   - New quotation number
   - Reference to original
4. Adjust quantities/prices as needed
5. Save and send

---

## Workflow: Configure Pricing

### Update Exchange Rate

When USD/COP rate changes significantly:

1. Go to **Pricing** > **Settings**
2. Find `exchange_rate_usd_cop`
3. Click to edit
4. Enter new rate (e.g., 4350)
5. Save
6. All future quotations use new rate

### Add HS Code

When importing new product categories:

1. Go to **Pricing** > **HS Codes**
2. Click **+ Add HS Code**
3. Enter:
   - **Code**: "8544.42" (from customs documentation)
   - **Description**: "Electric conductors with connectors"
   - **Duty Rate**: 15.00%
4. Save
5. Assign to products in catalog

### Add Freight Rate

When getting new shipping routes:

1. Go to **Pricing** > **Freight Rates**
2. Click **+ Add Rate**
3. Enter:
   - **Origin**: "Shenzhen"
   - **Destination**: "Cartagena"
   - **Incoterm**: "FOB"
   - **Rate per kg**: $2.80
   - **Rate per CBM**: $480.00
   - **Transit Days**: 32
4. Set validity period
5. Save

---

## Weekly Tasks Checklist

| Task | Frequency | Notes |
|------|-----------|-------|
| Update exchange rate | Weekly | Check current USD/COP |
| Follow up on Sent quotes | Daily | Don't let them go cold |
| Review expired quotes | Weekly | Clone and resend if relevant |
| Pipeline review | Daily | Keep deals moving |
| Pricing audit | Monthly | Verify rates are current |

---

# Ruben - CEO/Founder

**Primary Focus**: Business overview, pipeline health, team performance

**Key Modules**: Dashboard, Clients (pipeline view)

---

## Daily Workflow

### Morning: Business Health Check

1. Open **Dashboard**
2. Review KPI cards:

| KPI | What It Tells You |
|-----|-------------------|
| **Pipeline Value** | Total opportunity in negotiation |
| **Quotations Sent This Week** | Team activity level |
| **Products Added** | Catalog growth |
| **Active Suppliers** | Supply chain breadth |

3. Check **Quotations by Status** chart:
   - Healthy: Mostly "Sent" and "Negotiating"
   - Warning: Too many "Draft" (bottleneck)
   - Good: "Accepted" growing

4. Review **Quotation Trend**:
   - Compare Sent vs Accepted
   - Look for conversion patterns
   - Identify good/bad weeks

---

## Workflow: Pipeline Review

### Step 1: Open Pipeline

1. Go to **Clients**
2. Ensure you're in **Kanban View**
3. You see the full pipeline:

```
LEAD | QUALIFIED | QUOTING | NEGOTIATING | WON | LOST
```

### Step 2: Review Each Stage

| Stage | Questions to Ask |
|-------|------------------|
| **Lead** | How old are these? Should they be qualified or discarded? |
| **Qualified** | Why haven't we sent quotes? Any blockers? |
| **Quoting** | Is the team preparing quotes? Any delays? |
| **Negotiating** | What's the status? Close dates? |
| **Won** | Celebrate! Any patterns to replicate? |
| **Lost** | Why did we lose? Lessons learned? |

### Step 3: Identify Stuck Deals

Click on any client card to see:
- When they entered this stage
- Status history
- Notes from team

**Action items**:
- Deals stuck 2+ weeks in Quoting → Check with Alejandro
- Deals stuck 3+ weeks in Negotiating → May need executive involvement

### Step 4: Check High-Value Opportunities

1. Look at cards in "Negotiating"
2. Click to see quotation totals
3. Prioritize follow-up on largest deals

---

## Weekly Executive Review

### What to Review

| Metric | Where | Benchmark |
|--------|-------|-----------|
| Quotations/week | Dashboard | 10-15 target |
| Conversion rate | Accepted/Sent | 30-40% healthy |
| Avg deal size | Quotation totals | Track trend |
| Pipeline velocity | Days in each stage | Shorter = better |
| New products/month | Products Added | Catalog growth |

### Questions to Discuss

1. Are we quoting enough? (Volume)
2. Are we winning deals? (Conversion)
3. Are our prices competitive? (Win/loss analysis)
4. Is the catalog growing? (Product additions)
5. Are suppliers performing? (Quality, delivery)

---

## Monthly Strategic View

### Pipeline Health Assessment

1. **Dashboard** > **Quotation Trend** (30 days)
2. Compare to previous months
3. Identify:
   - Seasonal patterns
   - Growth trajectory
   - Problem areas

### Team Performance

Review quotation activity:
- Who's creating the most quotations?
- What's the conversion by sales person?
- Where are deals getting stuck?

### Product Performance

1. **Dashboard** > **Top Quoted Products**
2. Ensure popular items are:
   - In stock with suppliers
   - Priced competitively
   - Featured in portfolios

---

## Quick Actions for Executives

| Need | Action |
|------|--------|
| See total pipeline value | Dashboard > Pipeline Value KPI |
| Check this week's activity | Dashboard > Quotations Sent This Week |
| Find stuck deals | Clients > Kanban > Look for old cards |
| Export data for board | Dashboard > Export (if available) |
| Review a specific quotation | Quotations > Search > Click to view |

---

# Cross-Team Workflows

## Workflow: End-to-End New Project

**Scenario**: A new hotel project from lead to won deal.

### Phase 1: Lead Generation (Ruben/Sales)

1. Identify opportunity (trade show, referral)
2. Create client in **Clients** module
3. Status: Lead

### Phase 2: Qualification (Alejandro)

1. Contact client, understand needs
2. Move to **Qualified**
3. Identify product requirements

### Phase 3: Product Curation (Diana)

1. Review existing portfolios
2. Create custom portfolio if needed
3. Import any missing products

### Phase 4: Quotation (Alejandro)

1. Create quotation from portfolio
2. Configure pricing
3. Review with team
4. Send to client
5. Move client to **Quoting** then **Negotiating**

### Phase 5: Close (Alejandro + Ruben)

1. Handle negotiations
2. Adjust quotation if needed
3. Get final acceptance
4. Move to **Won**

---

## Workflow: Monthly Catalog Refresh

**Participants**: Diana (lead), Alejandro (input)

### Week 1: Gather Inputs

1. Alejandro provides:
   - Frequently requested products we don't have
   - Competitor products clients mention
   - Price feedback from lost deals

2. Diana identifies:
   - New supplier catalogs to import
   - Categories needing expansion
   - Outdated products to discontinue

### Week 2: Import & Organize

1. Import new products via **Import Wizard**
2. Organize into categories
3. Apply appropriate tags
4. Add to relevant portfolios

### Week 3: Quality & Pricing

1. Alejandro reviews new products:
   - Assigns HS codes
   - Verifies pricing is competitive
   - Flags any concerns

2. Diana finalizes:
   - Improves images/descriptions
   - Activates products

### Week 4: Launch

1. Update portfolios with new products
2. Communicate additions to team
3. Feature in client outreach

---

## Communication Handoffs

| From | To | Handoff | How |
|------|----|---------|-----|
| Diana | Alejandro | "Products ready for quoting" | Set status to Active |
| Alejandro | Diana | "Need this product" | Create request in notes |
| Alejandro | Ruben | "Deal needs exec support" | Move to Negotiating + note |
| Ruben | Alejandro | "Prioritize this client" | Add note to client |

---

## Daily Standup Topics

| Person | Reports On |
|--------|------------|
| Diana | Products imported, portfolios updated |
| Alejandro | Quotes sent, deals progressing |
| Ruben | Pipeline observations, priorities |

---

## End of Guide

For detailed instructions on specific features, refer to:
- **User Guide**: `ai_docs/KOMPASS_USER_GUIDE.md`
- **Quick Reference**: `ai_docs/KOMPASS_QUICK_REFERENCE.md`
- **Technical Guide**: `ai_docs/KOMPASS_MODULE_GUIDE.md`
