# E2E Test: Supplier Outreach Follow-Up Messages

## Test Name
Supplier Outreach Follow-Up Messages

## User Story
As a back-office team member (admin, manager, or user)
I want to send configurable follow-up messages to suppliers via email and/or WeChat from the supplier detail view
So that I can efficiently request product catalogs and pricing information after trade fair meetings

## Prerequisites
- Application is running and accessible
- User is authenticated with valid credentials
- At least one supplier exists in the database (preferably with contact_email)

## Test Steps

### Step 1: Navigate to Suppliers Page
1. Log in to the application with valid credentials
2. Navigate to the Suppliers page via sidebar or URL `/suppliers`
3. **Verify**: Page loads with title "Suppliers"
4. **Verify**: Supplier list table is visible with rows
5. **Screenshot**: `01_suppliers_page.png`

### Step 2: Verify Outreach Status Column
1. Look at the table headers
2. **Verify**: A "Seguimiento" column header is visible in the table
3. **Verify**: Suppliers with outreach_status other than 'none' display a colored chip
4. **Screenshot**: `02_outreach_column.png`

### Step 3: Open Quick Actions Menu
1. Find a supplier row with a contact email (or any supplier)
2. Click the three-dot menu (MoreVert icon) on that supplier's row
3. **Verify**: Quick actions menu opens with menu items
4. **Verify**: "Enviar Seguimiento" menu item is visible
5. **Verify**: "Enviar Seguimiento" has a send icon
6. **Screenshot**: `03_quick_actions_menu.png`

### Step 4: Open Outreach Dialog
1. Click "Enviar Seguimiento" menu item
2. **Verify**: Outreach dialog opens with title "Enviar Seguimiento — [Supplier Name]"
3. **Verify**: Template dropdown (Plantilla) is visible with options
4. **Verify**: Channel checkboxes (Email, WeChat) are visible
5. **Verify**: Email checkbox is enabled if supplier has contact_email, disabled otherwise
6. **Verify**: Message preview section (Vista previa) shows template subject and body preview
7. **Verify**: Custom message text field is visible with label "Mensaje personalizado (opcional)"
8. **Verify**: "Enviar" and "Cancelar" buttons are visible
9. **Screenshot**: `04_outreach_dialog.png`

### Step 5: Select Template
1. Open the template dropdown (Plantilla)
2. **Verify**: At least 3 templates are available: "Presentación inicial", "Solicitud de catálogo", "Solicitud de precios"
3. Select "Solicitud de catálogo" template
4. **Verify**: Message preview updates to show the catalog request template content
5. **Screenshot**: `05_template_selected.png`

### Step 6: Verify Channel Controls
1. **Verify**: Email checkbox state matches whether supplier has contact_email
2. **Verify**: WeChat checkbox state matches whether supplier has contact_phone/wechat_id
3. If both are available, check both checkboxes
4. **Screenshot**: `06_channels.png`

### Step 7: Send Outreach Message
1. Ensure at least one channel checkbox is checked
2. Click "Enviar" button
3. **Verify**: Loading indicator appears on the button
4. **Verify**: After sending, a success or error Alert is displayed in the dialog
5. **Verify**: If successful, the Alert shows a success message
6. **Screenshot**: `07_send_result.png`

### Step 8: Verify Status Update
1. Close the outreach dialog by clicking "Cancelar"
2. **Verify**: The supplier's outreach status chip in the table has updated
3. **Verify**: If message was sent successfully, chip shows "Contactado" (blue)
4. **Screenshot**: `08_status_updated.png`

### Step 9: Verify Spanish Labels
1. **Verify**: All dialog labels are in Spanish: "Enviar Seguimiento", "Plantilla", "Canales", "Vista previa", "Mensaje personalizado", "Enviar", "Cancelar"
2. **Verify**: Outreach status chips use Spanish labels: "Sin contactar", "Contactado", "Respondió", etc.
3. **Screenshot**: `09_spanish_labels.png`

## Success Criteria
- [x] Suppliers page loads with "Seguimiento" column visible
- [x] "Enviar Seguimiento" action appears in supplier quick actions menu
- [x] "Enviar Seguimiento" is disabled when supplier has no contact_email AND no contact_phone
- [x] Outreach dialog opens with template dropdown, channel checkboxes, message preview, send button
- [x] Template dropdown shows at least 3 templates with Spanish names
- [x] Email checkbox is disabled when supplier has no contact_email
- [x] WeChat checkbox is disabled when supplier has no contact_phone
- [x] Message preview renders template subject and body preview
- [x] "Enviar" button triggers outreach send and shows result feedback
- [x] Success/error Alert displays after sending
- [x] Outreach status chip updates on supplier row after successful send
- [x] All UI text is in Spanish (Colombian)

## Output Format
```json
{
  "test_name": "Supplier Outreach Follow-Up Messages",
  "status": "passed|failed",
  "screenshots": [
    "01_suppliers_page.png",
    "02_outreach_column.png",
    "03_quick_actions_menu.png",
    "04_outreach_dialog.png",
    "05_template_selected.png",
    "06_channels.png",
    "07_send_result.png",
    "08_status_updated.png",
    "09_spanish_labels.png"
  ],
  "error": null
}
```
