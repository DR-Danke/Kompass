# Kompass User Guide

This guide explains how to use the Kompass Portfolio & Quotation Automation System for managing your China sourcing business.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Supplier Management](#supplier-management)
4. [Product Catalog (Biblia General)](#product-catalog-biblia-general)
5. [Import Wizard](#import-wizard)
6. [Categories & Tags](#categories--tags)
7. [Portfolio Creation](#portfolio-creation)
8. [Client Management](#client-management)
9. [Quotation Workflow](#quotation-workflow)
10. [Pricing Configuration](#pricing-configuration)

---

## Getting Started

### Logging In

1. Navigate to your Kompass application URL
2. Enter your email and password
3. Click **Login**

After logging in, you'll be redirected to the Dashboard.

### Navigation

The sidebar on the left provides access to all modules:

| Icon | Module | Description |
|------|--------|-------------|
| Dashboard | Dashboard | KPIs, charts, and recent activity |
| Factory | Suppliers | Manage Chinese vendors |
| Inventory | Biblia General | Product catalog |
| Upload | Import Wizard | Bulk import products |
| Category | Categories | Product categorization |
| Collections | Portfolios | Curated product collections |
| People | Clients | CRM and pipeline |
| Document | Quotations | Create and manage quotations |
| Label | Niches | Client market segments |
| Money | Pricing | Pricing configuration |
| Settings | Settings | Application settings |

Click the menu icon at the top to collapse or expand the sidebar.

---

## Dashboard Overview

The Dashboard provides a snapshot of your business:

### KPI Cards

- **Total Products**: Number of products in your Biblia General
- **Products Added This Month**: New products added in the current month
- **Active Suppliers**: Number of active supplier relationships
- **Quotations Sent This Week**: Quotations sent in the past 7 days
- **Pipeline Value**: Total value of quotations in active pipeline

### Charts

- **Quotations by Status**: Donut chart showing distribution (draft, sent, accepted, etc.)
- **Quotation Trend**: Line chart showing sent vs. accepted quotations over time
- **Top Quoted Products**: Bar chart of most frequently quoted products

### Activity Feeds

- **Recent Products**: Latest products added to the catalog
- **Recent Quotations**: Latest quotation activity
- **Recent Clients**: Newly added clients

---

## Supplier Management

### Viewing Suppliers

1. Click **Suppliers** in the sidebar
2. View the supplier list with search and filters
3. Use the search bar to find suppliers by name or code

### Adding a New Supplier

1. Click the **+ Add Supplier** button
2. Fill in the required fields:
   - **Name**: Supplier company name (required)
   - **Code**: Unique supplier code (optional, auto-generated if blank)
   - **Status**: Active, Inactive, or Pending Review
3. Add contact information:
   - Contact Name
   - Email
   - Phone
   - WeChat ID
4. Add location details:
   - Address
   - City
   - Country (defaults to China)
   - Website
5. Add any notes
6. Click **Save**

### Editing a Supplier

1. Click on a supplier row to open the detail view
2. Click **Edit**
3. Make your changes
4. Click **Save**

### Managing Supplier Status

Supplier statuses help track vendor relationships:

| Status | Description |
|--------|-------------|
| **Active** | Current, approved supplier |
| **Inactive** | No longer ordering from this supplier |
| **Pending Review** | New supplier being evaluated |

### Viewing Supplier Products

From the supplier detail view, click the **Products** tab to see all products from that supplier.

---

## Product Catalog (Biblia General)

The Biblia General is your master product database containing all products from your suppliers.

### Browsing Products

1. Click **Biblia General** in the sidebar
2. Toggle between **Grid View** and **Table View** using the view buttons
3. Use filters to narrow results:
   - **Category**: Filter by product category
   - **Supplier**: Filter by supplier
   - **Status**: Draft, Active, Inactive, Discontinued
   - **Price Range**: Min and max price
   - **Tags**: Filter by assigned tags

### Searching Products

Use the search bar to find products by:
- Product name
- SKU
- Description

The search performs full-text matching across these fields.

### Creating a Product

1. Click **+ Add Product**
2. Fill in basic information:
   - **Name**: Product name (required)
   - **SKU**: Unique identifier (auto-generated if blank)
   - **Supplier**: Select from dropdown (required)
   - **Description**: Product details
3. Set categorization:
   - **Category**: Select from category tree
   - **Tags**: Add relevant tags
4. Configure pricing:
   - **Unit Cost**: Your cost from supplier (FOB)
   - **Unit Price**: Your selling price
   - **Currency**: Default USD
5. Add specifications:
   - Unit of Measure
   - Minimum Order Quantity
   - Lead Time (days)
   - Weight (kg)
   - Dimensions
6. Set product status:
   - **Draft**: Not yet ready for quotations
   - **Active**: Available for quotations
   - **Inactive**: Temporarily unavailable
   - **Discontinued**: No longer available
7. Click **Save**

### Managing Product Images

1. Open the product detail view
2. Click the **Images** tab
3. Click **Add Image** to upload
4. Set one image as **Primary** (shown in lists)
5. Drag images to reorder
6. Click the trash icon to remove images

### Assigning Tags

1. Open the product detail view
2. Click the **Tags** section
3. Click **Add Tag** and select from available tags
4. Or create a new tag on the fly

---

## Import Wizard

The Import Wizard uses AI to extract product data from supplier catalogs.

### Supported Formats

- **PDF**: Supplier catalogs and price lists
- **Excel**: Spreadsheets with product data (.xlsx, .xls)
- **Images**: Product photos with text (.jpg, .png)

### Import Process

#### Step 1: Upload File

1. Click **Import Wizard** in the sidebar
2. Drag and drop your file or click to browse
3. Select the file to upload
4. Wait for the upload to complete

#### Step 2: Configure Extraction

1. Select the **Supplier** for these products
2. Choose the **Default Category** (optional)
3. Set **Default Status** for imported products
4. Click **Start Extraction**

#### Step 3: Review Extracted Products

1. The AI will extract product information
2. Review each product in the list:
   - Check product names
   - Verify prices
   - Review descriptions
3. Make corrections as needed:
   - Click on any field to edit
   - Remove products you don't want to import
4. Assign categories and tags if needed

#### Step 4: Confirm Import

1. Review the summary showing:
   - Total products to import
   - Products with warnings
   - Products ready for import
2. Click **Confirm Import**
3. Products are added to your Biblia General

### Tips for Better Extraction

- Use clear, high-quality PDFs
- Structured catalogs work better than free-form layouts
- Tables are extracted more accurately
- Provide price lists in consistent formats

---

## Categories & Tags

### Managing Categories

Categories provide hierarchical organization for products.

#### Creating a Category

1. Click **Categories** in the sidebar
2. Click **+ Add Category**
3. Enter category details:
   - **Name**: Category name
   - **Description**: Optional description
   - **Parent**: Select parent for subcategories
   - **Sort Order**: Display order (lower = first)
4. Click **Save**

#### Creating Subcategories

1. When creating/editing a category
2. Select a **Parent** category
3. The new category becomes a child of the parent
4. Categories can be nested multiple levels deep

#### Category Tree View

- Click **Tree View** to see the full hierarchy
- Expand/collapse branches using the arrow icons
- Drag categories to reorganize (if enabled)

### Managing Tags

Tags provide flexible, cross-cutting organization.

#### Creating a Tag

1. Click **Categories** (Tags tab) in the sidebar
2. Click **+ Add Tag**
3. Enter tag details:
   - **Name**: Tag name
   - **Color**: Pick a color for visual identification
4. Click **Save**

#### Using Tags

- Tags can be assigned to multiple products
- Products can have multiple tags
- Filter products by tags in the catalog
- Tags appear as colored chips on product cards

---

## Portfolio Creation

Portfolios are curated product collections tailored for specific client niches.

### Creating a Portfolio

1. Click **Portfolios** in the sidebar
2. Click **+ Create Portfolio**
3. Enter portfolio details:
   - **Name**: Portfolio name
   - **Description**: What this collection is for
   - **Niche**: Target client segment
4. Click **Create**

### Adding Products to a Portfolio

#### From the Portfolio Builder

1. Open the portfolio
2. Click **+ Add Products**
3. Browse or search for products
4. Click the **+** icon to add products
5. Products are added to the portfolio

#### From the Product Catalog

1. In the Biblia General, select products
2. Click **Add to Portfolio**
3. Select the target portfolio
4. Confirm the addition

### Managing Portfolio Items

#### Reordering Products

1. Open the Portfolio Builder
2. Drag and drop products to reorder
3. Changes save automatically

#### Adding Curator Notes

1. Click on a product in the portfolio
2. Add notes in the **Notes** field
3. Notes appear when viewing the portfolio

#### Removing Products

1. Hover over a product in the portfolio
2. Click the **X** icon to remove

### Duplicating a Portfolio

1. Open the portfolio
2. Click **Duplicate**
3. Enter a new name
4. The portfolio is copied with all items

### Sharing a Portfolio

#### Generate Share Link

1. Open the portfolio
2. Click **Share**
3. Copy the generated link
4. Share with clients (no login required)

The share link expires after 30 days.

#### Export to PDF

1. Open the portfolio
2. Click **Export PDF**
3. A professional PDF is generated with:
   - Portfolio name and description
   - Product images and details
   - Contact information
4. Download or print the PDF

---

## Client Management

### Adding a Client

1. Click **Clients** in the sidebar
2. Click **+ Add Client**
3. Enter client information:
   - **Company Name**: Client company (required)
   - **Contact Name**: Primary contact
   - **Email**: Contact email
   - **Phone**: Phone number
   - **WhatsApp**: WhatsApp number
4. Add address details
5. Select **Niche**: Client's market segment
6. Set **Source**: How you found this client
7. Add **Project Details**:
   - Project Name
   - Project Deadline
   - Preferred Incoterm
8. Click **Save**

### Pipeline View (Kanban)

The pipeline view shows clients organized by sales stage:

| Stage | Description |
|-------|-------------|
| **Lead** | New prospect, not yet qualified |
| **Qualified** | Confirmed budget and interest |
| **Quoting** | Actively preparing quotation |
| **Negotiating** | Quotation sent, in discussion |
| **Won** | Deal closed successfully |
| **Lost** | Deal did not close |

#### Moving Clients

1. Drag client cards between columns
2. Drop to change their pipeline stage
3. Add notes when prompted (optional)

#### Status History

All stage changes are tracked. View history by:
1. Opening a client
2. Clicking the **History** tab

### Client Detail View

- **Overview**: Contact information and status
- **Quotations**: All quotations for this client
- **History**: Status change timeline
- **Notes**: Internal notes

### Timing Feasibility

Check if a project deadline is achievable:

1. Open the client with a project deadline
2. Click **Check Timing**
3. View the feasibility analysis:
   - Production lead time
   - Shipping transit time
   - Total days required
   - Buffer days available

---

## Quotation Workflow

### Creating a Quotation

1. Click **Quotations** in the sidebar
2. Click **+ New Quotation**
3. Select the **Client**
4. Configure quotation settings:
   - **Incoterm**: FOB, CIF, DDP, etc.
   - **Currency**: USD, COP, etc.
   - **Valid From/Until**: Validity period

### Adding Products

#### From Search

1. In the Quotation Creator, click **Add Products**
2. Search for products
3. Click **+** to add to the quotation
4. Set quantity for each item

#### From Portfolio

1. Click **Add from Portfolio**
2. Select a portfolio
3. Choose products to add
4. Confirm selection

### Managing Line Items

#### Editing Quantities

1. Click on the quantity field
2. Enter the new quantity
3. Line total updates automatically

#### Adjusting Prices

1. Click on the unit price field
2. Enter custom price (overrides catalog price)
3. Changes apply to this quotation only

#### Removing Items

1. Click the trash icon next to an item
2. Confirm removal

### Understanding the Pricing Panel

The pricing panel shows the complete cost breakdown:

| Component | Description |
|-----------|-------------|
| **Subtotal FOB** | Sum of line items |
| **Tariff Total** | Import duties (based on HS codes) |
| **Int'l Freight** | Shipping from China |
| **Inspection** | Pre-shipment inspection fee |
| **Insurance** | Cargo insurance |
| **Subtotal USD** | All USD costs combined |
| **National Freight** | Domestic shipping in Colombia |
| **Nationalization** | Customs processing fee |
| **Subtotal COP** | All costs in COP |
| **Margin** | Profit margin |
| **Total COP** | Final price to client |

### Saving and Status

#### Draft Status

- New quotations start as **Draft**
- Edit freely while in draft
- Not visible to client

#### Sending a Quotation

1. Review the quotation
2. Click **Send**
3. Status changes to **Sent**
4. Options to:
   - Send via email (with PDF)
   - Generate share link
   - Download PDF

### Quotation Status Flow

```
Draft → Sent → Viewed → Negotiating → Accepted
                  ↓          ↓
              Rejected   Rejected
                  ↓          ↓
              Expired    Expired
```

### Generating PDF

1. Open the quotation
2. Click **Generate PDF**
3. The PDF includes:
   - Company header
   - Client information
   - Quotation details
   - Product table
   - Pricing breakdown
   - Terms and conditions
   - Page numbers

### Sharing via Link

1. Open the quotation
2. Click **Share**
3. Copy the link
4. Client can view without login
5. Link expires after 30 days

### Sending via Email

1. Open the quotation
2. Click **Send Email**
3. Enter:
   - Recipient email
   - Subject line
   - Custom message
4. Choose to attach PDF
5. Click **Send**

### Cloning a Quotation

Create a new version based on an existing quotation:

1. Open the quotation
2. Click **Clone**
3. A new draft is created with:
   - Same client
   - Same line items
   - New quotation number
   - Reference to original

---

## Pricing Configuration

### Managing HS Codes

HS (Harmonized System) codes determine import tariff rates.

#### Adding an HS Code

1. Go to **Pricing** > **HS Codes**
2. Click **+ Add HS Code**
3. Enter:
   - **Code**: The HS code (e.g., "8544.42")
   - **Description**: What products this covers
   - **Duty Rate**: Tariff percentage
   - **Notes**: Additional information
4. Click **Save**

#### Assigning HS Codes to Products

1. Edit a product
2. Select the **HS Code** from the dropdown
3. The tariff rate applies automatically in quotations

### Managing Freight Rates

Configure shipping rates for different routes.

#### Adding a Freight Rate

1. Go to **Pricing** > **Freight Rates**
2. Click **+ Add Rate**
3. Enter:
   - **Origin**: Starting port (e.g., "Shanghai")
   - **Destination**: Arrival port (e.g., "Buenaventura")
   - **Incoterm**: FOB, CIF, etc.
   - **Rate per kg**: Cost per kilogram
   - **Rate per CBM**: Cost per cubic meter
   - **Minimum Charge**: Minimum shipping cost
   - **Transit Days**: Expected transit time
4. Set validity period (optional)
5. Click **Save**

### Global Pricing Settings

Adjust system-wide pricing parameters.

#### Accessing Settings

1. Go to **Pricing** > **Settings**
2. View all pricing parameters

#### Available Settings

| Setting | Description | Example |
|---------|-------------|---------|
| Exchange Rate | USD to COP conversion | 4200.00 |
| Margin % | Default profit margin | 20.00 |
| Insurance % | Insurance rate | 1.50 |
| Inspection Cost | Per-shipment inspection | $150.00 |
| Nationalization | Customs processing | 200,000 COP |

#### Updating a Setting

1. Click on the setting row
2. Enter the new value
3. Click **Save**
4. All future quotation calculations use the new value

---

## Managing Niches

Niches categorize your clients by market segment.

### Creating a Niche

1. Click **Niches** in the sidebar
2. Click **+ Add Niche**
3. Enter:
   - **Name**: Niche name (e.g., "Hotels", "Retailers", "Architects")
   - **Description**: What this segment represents
4. Click **Save**

### Using Niches

- Assign niches to clients to segment your CRM
- Create portfolios targeted at specific niches
- Filter clients and portfolios by niche

---

## Tips and Best Practices

### Product Organization

1. **Use Categories for Structure**: Create a logical hierarchy (e.g., Lighting > LED > Strips)
2. **Use Tags for Attributes**: Tag products with characteristics (e.g., "Best Seller", "New Arrival")
3. **Keep SKUs Consistent**: Use a consistent SKU format for easy searching

### Quotation Efficiency

1. **Create Niche Portfolios**: Pre-build portfolios for common client types
2. **Use Templates**: Clone successful quotations as starting points
3. **Set HS Codes Early**: Assign HS codes to products for automatic tariff calculation

### Client Management

1. **Track Sources**: Record where leads come from for marketing insights
2. **Set Deadlines**: Enter project deadlines to prioritize urgent clients
3. **Use Notes**: Add context to client records for team communication

### Pricing Accuracy

1. **Update Exchange Rates**: Keep the USD/COP rate current
2. **Review Freight Rates**: Update rates as shipping costs change
3. **Verify HS Codes**: Ensure products have correct tariff classifications

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + K` | Quick search |
| `Esc` | Close modal/dialog |
| `Enter` | Confirm action |

---

## Getting Help

If you need assistance:

1. Contact your system administrator
2. Review this user guide
3. Check the technical documentation in `ai_docs/KOMPASS_MODULE_GUIDE.md`
