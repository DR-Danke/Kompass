# Kompass Troubleshooting & FAQ

Solutions to common issues and frequently asked questions.

---

## Table of Contents

1. [Login & Access Issues](#login--access-issues)
2. [Product Catalog Issues](#product-catalog-issues)
3. [Import Wizard Issues](#import-wizard-issues)
4. [Quotation Issues](#quotation-issues)
5. [Pricing Issues](#pricing-issues)
6. [Portfolio Issues](#portfolio-issues)
7. [Client/CRM Issues](#clientcrm-issues)
8. [Share & Export Issues](#share--export-issues)
9. [Performance Issues](#performance-issues)
10. [Frequently Asked Questions](#frequently-asked-questions)

---

# Login & Access Issues

## "Invalid credentials" error

**Symptoms**: Can't log in, "Invalid email or password" message

**Solutions**:
1. Verify email is typed correctly (check for typos)
2. Check caps lock is off (passwords are case-sensitive)
3. Try resetting your password (contact admin)
4. Clear browser cache and try again

## Session expired / logged out unexpectedly

**Symptoms**: Redirected to login page while working

**Cause**: JWT tokens expire after 24 hours

**Solutions**:
1. Log in again
2. If happens frequently, check your browser settings:
   - Ensure cookies are enabled
   - Ensure localStorage is not being cleared

## "Access denied" error

**Symptoms**: Can see a page but can't perform an action

**Cause**: Your role doesn't have permission for that action

**Role permissions**:
| Role | Can Do |
|------|--------|
| Viewer | Read-only access |
| User | Most operations |
| Manager | All business operations |
| Admin | Everything + user management |

**Solution**: Contact admin if you need elevated permissions

---

# Product Catalog Issues

## Can't find a product I know exists

**Symptoms**: Search returns no results for a product

**Checklist**:
1. Check the **Status** filter - is it set to "All" or just "Active"?
2. Product might be in "Draft" status (not visible by default)
3. Try searching by:
   - SKU
   - Part of the product name
   - Description keywords
4. Check spelling

**Solution**: Reset all filters and search again

## Product shows wrong price in quotation

**Symptoms**: Price in quotation differs from catalog price

**Causes**:
1. You manually edited the price in the quotation (intentional)
2. The catalog price was updated after creating the quotation
3. Currency mismatch

**Solution**:
1. Check the product in **Products** for current price
2. In quotation, click the price field to update
3. Or remove and re-add the product

## Images not displaying

**Symptoms**: Product images show as broken/missing

**Causes**:
1. Image URL is invalid or expired
2. Image was deleted from source
3. CORS issues with external URLs

**Solutions**:
1. Edit product > Images tab
2. Remove broken image
3. Upload new image from local file
4. Use a reliable image hosting URL

## Product tags not saving

**Symptoms**: Add a tag, but it doesn't appear after refresh

**Cause**: Tag assignment failed silently

**Solutions**:
1. Check if the tag exists in **Categories > Tags**
2. Create the tag first if it doesn't exist
3. Try assigning from the Tags tab (not inline)
4. Refresh the page and try again

---

# Import Wizard Issues

## Upload fails with error

**Symptoms**: File upload shows error message

**Common causes and fixes**:

| Error | Cause | Fix |
|-------|-------|-----|
| "File too large" | File exceeds 20MB limit | Compress or split the file |
| "Invalid file type" | Not PDF/Excel/Image | Convert to supported format |
| "Upload failed" | Network error | Check connection, retry |

## Extraction produces garbage data

**Symptoms**: Extracted products have wrong names, prices, or missing data

**Causes**:
1. PDF is image-based (scanned), not text-based
2. Complex catalog layout
3. Non-standard formatting

**Solutions**:
1. For scanned PDFs: Try a clearer scan or OCR first
2. For complex layouts: Use Excel export from supplier
3. Import fewer pages at a time
4. Manually correct extracted data before confirming

## "No products extracted" message

**Symptoms**: Extraction completes but returns zero products

**Causes**:
1. File is password-protected
2. File contains only images with no text
3. AI couldn't identify product table structure

**Solutions**:
1. Remove password protection from PDF
2. Use Excel/CSV format instead
3. Request price list in tabular format from supplier

## Products imported with missing data

**Symptoms**: Products created but fields like price or description are empty

**Solution**:
1. During review step, fill in missing data
2. After import, edit products individually
3. Bulk edit if available

---

# Quotation Issues

## Quotation total shows $0 or wrong amount

**Symptoms**: Grand total is incorrect

**Checklist**:
1. Are line item quantities > 0?
2. Are unit prices > 0?
3. Is the pricing panel visible?
4. Click **Recalculate** if available

**Common causes**:
| Issue | Fix |
|-------|-----|
| No products added | Add products first |
| Quantities are 0 | Set quantities for each item |
| Prices are 0 | Check catalog prices |

## Tariff/duty not calculating

**Symptoms**: Tariff line shows $0 even though products have value

**Cause**: Products don't have HS codes assigned

**Solution**:
1. Note which products are in the quotation
2. Go to **Products** > Edit each product
3. Assign appropriate **HS Code**
4. Return to quotation > Recalculate

## Can't add products to quotation

**Symptoms**: Search shows products but can't add them

**Causes**:
1. Product status is "Draft" or "Inactive"
2. Product is already in quotation

**Solutions**:
1. Activate the product first
2. Check if already added (look in line items)

## Quotation PDF is blank or missing data

**Symptoms**: Generated PDF doesn't show all information

**Causes**:
1. Quotation has no line items
2. Browser blocking download
3. PDF generation timeout

**Solutions**:
1. Ensure quotation has products
2. Check browser download settings
3. Try generating again
4. Contact admin if persists

## Can't change quotation status

**Symptoms**: Status dropdown doesn't allow certain transitions

**Cause**: Not all status transitions are allowed

**Valid transitions**:
- Draft → Sent
- Sent → Viewed, Accepted, Rejected, Expired
- Viewed → Negotiating, Accepted, Rejected
- Negotiating → Accepted, Rejected

**Note**: You can't go backwards (e.g., Sent → Draft)

## Share link doesn't work for client

**Symptoms**: Client reports "link expired" or "not found"

**Causes**:
1. Link expired (30-day limit)
2. Link copied incorrectly
3. Quotation was deleted

**Solutions**:
1. Generate a new share token
2. Verify link is complete when copying
3. Check quotation still exists

---

# Pricing Issues

## Exchange rate is outdated

**Symptoms**: COP totals don't match current exchange rate

**Solution**:
1. Go to **Pricing** > **Settings**
2. Find `exchange_rate_usd_cop`
3. Update to current rate
4. Save
5. Recalculate existing quotations

## Freight cost seems wrong

**Symptoms**: International freight is too high or too low

**Checklist**:
1. Is the correct freight rate configured?
2. Does the route match (origin/destination)?
3. Is the rate still valid (check dates)?

**Solution**:
1. Go to **Pricing** > **Freight Rates**
2. Verify or add the correct route
3. Update rates as needed

## HS code not appearing in dropdown

**Symptoms**: Product edit shows no HS code options

**Cause**: No HS codes configured in system

**Solution**:
1. Go to **Pricing** > **HS Codes**
2. Add required HS codes
3. Include code, description, and duty rate

## Margin percentage not applying

**Symptoms**: Grand total doesn't include expected margin

**Checklist**:
1. Check `default_margin_percentage` in Pricing Settings
2. Ensure it's a number (e.g., 20 not "20%")
3. Recalculate the quotation

---

# Portfolio Issues

## Can't add product to portfolio

**Symptoms**: Product search works but add button disabled

**Causes**:
1. Product already in portfolio
2. Product status is not Active

**Solutions**:
1. Check if product already added
2. Activate the product first

## Portfolio order won't save

**Symptoms**: Drag-and-drop products but order resets

**Cause**: Browser not saving changes, or network error

**Solutions**:
1. Try explicit save if available
2. Refresh and try again
3. Check network connection

## Duplicate portfolio fails

**Symptoms**: Click duplicate but nothing happens

**Causes**:
1. Name already exists
2. Network error

**Solution**: Try a different name for the copy

---

# Client/CRM Issues

## Client not showing in pipeline

**Symptoms**: Added client but don't see them in Kanban

**Causes**:
1. Client status isn't a pipeline status
2. You're in List view not Kanban
3. Filters are hiding the client

**Solutions**:
1. Check client status (should be Lead, Qualified, etc.)
2. Toggle to Kanban view
3. Clear any active filters

## Can't drag client to new column

**Symptoms**: Drag doesn't work in Kanban

**Causes**:
1. Browser compatibility
2. Invalid status transition

**Solutions**:
1. Try a different browser
2. Use the status dropdown instead

## Status history not showing

**Symptoms**: History tab is empty

**Cause**: No status changes recorded yet

**Note**: History only tracks changes, not initial status

## Timing feasibility not calculating

**Symptoms**: "Check Timing" shows no results

**Cause**: Project deadline not set on client

**Solution**: Edit client and add project deadline

---

# Share & Export Issues

## Share link expired

**Symptoms**: Client can't access shared portfolio/quotation

**Cause**: Links expire after 30 days

**Solution**: Generate a new share token

## PDF won't download

**Symptoms**: Click Generate PDF but nothing happens

**Causes**:
1. Browser blocking popups/downloads
2. PDF generation failed

**Solutions**:
1. Allow popups for the site
2. Check downloads folder
3. Try a different browser
4. Reduce quotation size (fewer items)

## PDF missing images

**Symptoms**: PDF generates but product images are missing

**Cause**: Image URLs not accessible during PDF generation

**Solution**: Use direct image URLs, not temporary or authenticated ones

---

# Performance Issues

## Pages loading slowly

**Symptoms**: Takes long time to load product list or quotations

**Causes**:
1. Large data sets
2. Network latency
3. Server performance

**Solutions**:
1. Use filters to reduce result sets
2. Reduce page size in pagination
3. Clear browser cache
4. Check network connection

## Search is slow

**Symptoms**: Typing in search takes long to show results

**Cause**: Searching large dataset

**Solution**: Wait for debounce (300ms) before results appear

## Browser freezing

**Symptoms**: Page becomes unresponsive

**Causes**:
1. Too many items displayed
2. Memory issues

**Solutions**:
1. Reduce items per page
2. Close other tabs
3. Restart browser

---

# Frequently Asked Questions

## General

### Q: How do I change my password?
A: Contact your system administrator. Self-service password reset is not currently available.

### Q: Can I work offline?
A: No, Kompass requires an internet connection. Data is not cached locally.

### Q: Is my data backed up?
A: Yes, the database is backed up automatically by Supabase.

## Products

### Q: How many products can I have in the catalog?
A: There's no hard limit. Performance may degrade with 10,000+ products.

### Q: Can I bulk edit products?
A: Currently, products must be edited individually. Bulk import is available for new products.

### Q: How do I delete a product?
A: Edit the product and set status to "Discontinued" or delete from product detail view. Note: Products used in quotations cannot be fully deleted.

### Q: What image formats are supported?
A: JPG, PNG, GIF, WebP. Recommended: JPG or PNG under 2MB.

## Import

### Q: What file formats can I import?
A: PDF, Excel (.xlsx, .xls), and images (JPG, PNG).

### Q: How big can import files be?
A: Maximum 20MB per file.

### Q: Can I import from multiple files at once?
A: Upload one file at a time, but you can queue multiple imports.

### Q: How accurate is the AI extraction?
A: Varies by document quality. Expect 80-95% accuracy for clean, structured documents.

## Quotations

### Q: Can I edit a quotation after sending?
A: Yes, but consider cloning and sending a new version instead for audit trail.

### Q: How long are share links valid?
A: 30 days from generation.

### Q: Can clients edit a shared quotation?
A: No, share links are read-only.

### Q: Can I send a quotation to multiple recipients?
A: Send email separately to each, or share a link they can forward.

### Q: What happens when a quotation expires?
A: It remains in the system with "Expired" status. Clone it to create a new one.

## Pricing

### Q: How often should I update the exchange rate?
A: Weekly, or when it changes significantly (>2%).

### Q: Where do I find HS codes for products?
A: Consult Colombian customs tariff schedules or your customs broker.

### Q: Can I have different margins for different clients?
A: Adjust unit prices manually in quotations. The default margin applies to calculations.

## Portfolios

### Q: How many products can be in a portfolio?
A: No hard limit, but 20-50 is typical for good presentation.

### Q: Can I share a portfolio that's not published?
A: You can generate a share link, but recipients may see incomplete data.

### Q: Can multiple people edit a portfolio simultaneously?
A: No, avoid concurrent edits to prevent conflicts.

## Clients

### Q: Can I import clients from a spreadsheet?
A: Not currently. Clients must be added manually.

### Q: What's the difference between Kanban and List view?
A: Kanban shows pipeline stages as columns. List shows all clients with filters and sorting.

### Q: Can I customize pipeline stages?
A: The six stages are fixed (Lead, Qualified, Quoting, Negotiating, Won, Lost).

## Technical

### Q: Which browsers are supported?
A: Chrome, Firefox, Safari, Edge (latest versions). Chrome recommended.

### Q: Can I use Kompass on mobile?
A: The interface is responsive but optimized for desktop. Some features may be limited on mobile.

### Q: How do I report a bug?
A: Contact your system administrator with:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots if possible

### Q: Is there an API I can use?
A: Yes, see `ai_docs/KOMPASS_MODULE_GUIDE.md` for API documentation.

---

## Still Need Help?

If your issue isn't covered here:

1. Check the detailed **User Guide**: `ai_docs/KOMPASS_USER_GUIDE.md`
2. Review the **Technical Guide**: `ai_docs/KOMPASS_MODULE_GUIDE.md`
3. Contact your system administrator
4. For developers: Check browser console for error messages

---

## Error Code Reference

| Error | Meaning | Fix |
|-------|---------|-----|
| 400 | Bad request / Invalid data | Check required fields |
| 401 | Not authenticated | Log in again |
| 403 | Not authorized | Check your role/permissions |
| 404 | Not found | Resource doesn't exist |
| 409 | Conflict | Duplicate or constraint violation |
| 422 | Validation error | Check field formats |
| 500 | Server error | Contact admin |
