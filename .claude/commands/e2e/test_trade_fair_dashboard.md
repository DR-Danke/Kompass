# E2E Test: Trade Fair Dashboard Activity Feed

## Test Name
Trade Fair Dashboard Activity Feed

## User Story
As a back-office team member (any role: admin, manager, user, or viewer)
I want to see a Trade Fair Activity section on my dashboard showing recently captured suppliers, their processing status, and outreach progress
So that I can monitor trade fair capture activity in near-real-time and ensure organized data within one day of capture

## Prerequisites
- Application is running and accessible
- User is authenticated with valid credentials
- Database may or may not have business_card_captures records

## Test Steps

### Step 1: Navigate to Dashboard
1. Log in to the application with valid credentials
2. Navigate to the Dashboard page via sidebar or URL `/`
3. **Verify**: Page loads with title "Dashboard"
4. **Screenshot**: `01_dashboard_page.png`

### Step 2: Verify Trade Fair Activity Section Visibility
1. Look for the Trade Fair Activity section with `data-testid="trade-fair-activity"`
2. **Verify**: If captures exist in the database, the section is visible with title "Actividad Feria Comercial"
3. **Verify**: If no captures exist, the section is NOT rendered (hidden)
4. **Screenshot**: `02_trade_fair_section.png`

### Step 3: Verify KPI Cards
1. If the Trade Fair Activity section is visible, locate the KPI cards row
2. **Verify**: "Capturas Totales" card is visible with a numeric value
3. **Verify**: "Proveedores Creados" card is visible with a numeric value
4. **Verify**: "Emails Enviados" card is visible with a numeric value
5. **Verify**: "Respuestas" card is visible with a numeric value
6. **Screenshot**: `03_kpi_cards.png`

### Step 4: Verify Status Breakdown
1. If the Trade Fair Activity section is visible, locate the status breakdown area
2. **Verify**: Status badges/chips are rendered with correct colors (pending=orange, processing=blue, extracted=purple, confirmed=green, rejected=red, failed=grey)
3. **Verify**: Each status badge shows a count
4. **Screenshot**: `04_status_breakdown.png`

### Step 5: Verify Recent Captures List
1. If the Trade Fair Activity section is visible, locate the recent captures list
2. **Verify**: "Capturas Recientes" heading is visible
3. **Verify**: Each capture entry shows company name (or "—" if null)
4. **Verify**: Each capture entry shows contact name
5. **Verify**: Each capture entry shows a status chip
6. **Verify**: Each capture entry shows an outreach status chip (if applicable)
7. **Verify**: Each capture entry shows relative time (e.g., "hace 2 horas")
8. **Screenshot**: `05_recent_captures.png`

### Step 6: Test Refresh Button
1. Locate the refresh button (RefreshIcon) in the Trade Fair Activity section
2. Click the refresh button
3. **Verify**: Data reloads (loading state may appear briefly)
4. **Screenshot**: `06_after_refresh.png`

### Step 7: Verify Spanish Labels
1. **Verify**: All UI text is in Spanish: "Actividad Feria Comercial", "Capturas Totales", "Proveedores Creados", "Emails Enviados", "Respuestas", "Capturas Recientes", "Actualizar"
2. **Screenshot**: `07_spanish_labels.png`

## Success Criteria
- [x] Dashboard page loads without errors
- [x] Trade Fair Activity section renders when captures exist
- [x] Trade Fair Activity section is hidden when no captures exist
- [x] KPI cards display: total captures, suppliers created, emails sent, responses
- [x] Status breakdown shows colored badges for each capture status with counts
- [x] Recent captures list shows company name, contact name, status chip, outreach status, time ago
- [x] Refresh button triggers data reload
- [x] All UI text is in Spanish (Colombian)

## Output Format
```json
{
  "test_name": "Trade Fair Dashboard Activity Feed",
  "status": "passed|failed",
  "screenshots": [
    "01_dashboard_page.png",
    "02_trade_fair_section.png",
    "03_kpi_cards.png",
    "04_status_breakdown.png",
    "05_recent_captures.png",
    "06_after_refresh.png",
    "07_spanish_labels.png"
  ],
  "error": null
}
```
