# E2E Test: Editable Outreach Email Templates

## Test Name
Editable Outreach Email Templates

## User Story
As an admin or manager
I want to edit outreach email templates (subject lines, body text, and names) directly from the application UI
So that I can customize follow-up email content without requiring code changes or developer intervention

## Prerequisites
- Application is running and accessible
- User is authenticated with admin or manager role
- Outreach templates have been seeded in the database (3 default templates)

## Test Steps

### Step 1: Navigate to Settings Page
1. Log in to the application with valid credentials (admin or manager role)
2. Navigate to the Settings page via sidebar or URL `/settings`
3. **Verify**: Page loads with title "Configuración"
4. **Verify**: "Plantillas de Seguimiento" section is visible
5. **Screenshot**: `01_settings_page.png`

### Step 2: Verify Template List
1. Look at the "Plantillas de Seguimiento" section
2. **Verify**: 3 templates are listed: "Presentación inicial", "Solicitud de catálogo", "Solicitud de precios"
3. **Verify**: Each template row shows: name, key identifier, subject (truncated), and an active toggle switch
4. **Verify**: All 3 templates have their active toggle set to ON by default
5. **Screenshot**: `02_template_list.png`

### Step 3: Open Edit Dialog
1. Click on the "Presentación inicial" template row
2. **Verify**: Edit dialog opens with title "Editar Plantilla"
3. **Verify**: "Nombre" text field shows "Presentación inicial"
4. **Verify**: "Asunto" text field shows the template subject
5. **Verify**: "Cuerpo del Mensaje" multiline text field shows the full template body
6. **Screenshot**: `03_edit_dialog.png`

### Step 4: Verify Placeholder Chips
1. In the edit dialog, look for the "Variables Disponibles" section
2. **Verify**: 4 clickable chips are shown: `{contact_name}`, `{company_name}`, `{fair_name}`, `{sender_name}`
3. Click a placeholder chip (e.g., `{contact_name}`)
4. **Verify**: The placeholder text is inserted into the body field at cursor position
5. **Screenshot**: `04_placeholder_chips.png`

### Step 5: Verify Live Preview
1. In the edit dialog, look for the "Vista Previa" panel
2. **Verify**: Preview panel shows the template rendered with sample data
3. **Verify**: `{contact_name}` is replaced with "Juan Pérez"
4. **Verify**: `{company_name}` is replaced with "Empresa ABC"
5. **Verify**: `{fair_name}` is replaced with "Canton Fair 2026"
6. **Verify**: `{sender_name}` is replaced with "Kompass"
7. **Screenshot**: `05_live_preview.png`

### Step 6: Edit Template and Save
1. Change the "Nombre" field to "Presentación inicial modificada"
2. **Verify**: The preview updates to reflect changes
3. Click "Guardar" button
4. **Verify**: Success snackbar appears with message "Plantilla actualizada exitosamente"
5. **Verify**: Dialog closes
6. **Verify**: Template list shows updated name "Presentación inicial modificada"
7. **Screenshot**: `06_template_saved.png`

### Step 7: Verify Persistence After Reload
1. Reload the Settings page (navigate away and back, or refresh)
2. **Verify**: The modified template still shows "Presentación inicial modificada"
3. **Screenshot**: `07_persistence_check.png`

### Step 8: Reset Template to Default
1. Click on the modified "Presentación inicial modificada" template row
2. Click "Restaurar Original" button
3. **Verify**: Confirmation dialog appears asking to confirm reset
4. Confirm the reset action
5. **Verify**: Template fields are restored to original values
6. **Verify**: Name shows "Presentación inicial" again
7. **Verify**: Success snackbar appears
8. **Screenshot**: `08_template_reset.png`

### Step 9: Toggle Template Inactive
1. Find the "Solicitud de precios" template in the list
2. Toggle its active switch to OFF
3. **Verify**: Switch changes to OFF state
4. **Verify**: Success snackbar appears
5. Navigate to the Suppliers page (`/suppliers`)
6. Open the outreach dialog for any supplier (via quick actions menu → "Enviar Seguimiento")
7. Open the template dropdown
8. **Verify**: "Solicitud de precios" template does NOT appear in the dropdown
9. **Verify**: Only 2 templates appear (the active ones)
10. **Screenshot**: `09_template_inactive.png`

### Step 10: Toggle Template Back Active
1. Navigate back to the Settings page
2. Toggle the "Solicitud de precios" template active switch back to ON
3. Navigate to the Suppliers page
4. Open the outreach dialog again
5. **Verify**: "Solicitud de precios" template now appears in the dropdown
6. **Verify**: 3 templates are available again
7. **Screenshot**: `10_template_reactivated.png`

### Step 11: Verify Spanish Labels
1. Navigate back to Settings page
2. **Verify**: All labels are in Spanish: "Configuración", "Plantillas de Seguimiento", "Editar Plantilla", "Nombre", "Asunto", "Cuerpo del Mensaje", "Variables Disponibles", "Vista Previa", "Guardar", "Cancelar", "Restaurar Original"
3. **Screenshot**: `11_spanish_labels.png`

## Success Criteria
- [x] Settings page loads with "Plantillas de Seguimiento" section
- [x] 3 templates listed with name, key, subject, and active toggle
- [x] Edit dialog opens with editable Name, Subject, Body fields
- [x] Placeholder chips are shown and clickable (insert at cursor position)
- [x] Live preview panel renders template with sample data
- [x] Editing a template and saving persists changes
- [x] Changes persist after page reload
- [x] "Restaurar Original" resets template to default content with confirmation
- [x] Toggling template inactive hides it from Suppliers page outreach dropdown
- [x] Toggling template back active makes it reappear in outreach dropdown
- [x] All UI text is in Spanish (Colombian)

## Output Format
```json
{
  "test_name": "Editable Outreach Email Templates",
  "status": "passed|failed",
  "screenshots": [
    "01_settings_page.png",
    "02_template_list.png",
    "03_edit_dialog.png",
    "04_placeholder_chips.png",
    "05_live_preview.png",
    "06_template_saved.png",
    "07_persistence_check.png",
    "08_template_reset.png",
    "09_template_inactive.png",
    "10_template_reactivated.png",
    "11_spanish_labels.png"
  ],
  "error": null
}
```
