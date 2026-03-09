# E2E Test: Card Capture Page (Business Card Photo Ingestion)

## User Story

As a Kompass sourcing agent attending a trade fair
I want to quickly photograph supplier business cards from my phone and upload them to the system
So that I can capture supplier contact information efficiently and process it later with AI extraction

## Test Steps

### Step 1: Navigate to Card Capture Page
1. Open the application at the base URL
2. Login with test credentials (if required)
3. Navigate to `/card-capture` page using the sidebar navigation item "Captura Tarjetas" or direct URL
4. **Verify** page title "Captura de Tarjetas" is visible
5. **Verify** upload button/area is visible with camera icon
6. **Verify** fair name text field ("Nombre de la Feria") is visible
7. **Screenshot**: `01_card_capture_page_loaded.png`

### Step 2: Verify Page Structure
1. **Verify** the upload area has a large touch target (prominent button)
2. **Verify** the file input accepts image files (.png, .jpg, .jpeg)
3. **Verify** the recent captures list area is visible (may show empty state)
4. **Screenshot**: `02_page_structure.png`

### Step 3: Enter Fair Name
1. Find the "Nombre de la Feria" text field
2. Enter "Canton Fair 2026"
3. **Verify** the text field contains "Canton Fair 2026"
4. **Screenshot**: `03_fair_name_entered.png`

### Step 4: Upload a Test Image
1. Create a test image file (1x1 pixel PNG or use any small .jpg/.png file)
2. Upload the test image using the file input
3. **Verify** upload progress indicator appears (progress bar)
4. **Verify** upload completes successfully (success snackbar or indicator)
5. **Screenshot**: `04_upload_in_progress.png`

### Step 5: Verify Uploaded Card in List
1. **Verify** the uploaded card appears in the recent captures list
2. **Verify** the capture card shows:
   - Image thumbnail
   - Status chip with "pending" status (orange color)
   - Fair name "Canton Fair 2026"
   - Timestamp
3. **Screenshot**: `05_capture_listed.png`

### Step 6: Upload Second Image (Fair Name Persistence)
1. **Verify** the fair name field still contains "Canton Fair 2026" (persisted across uploads)
2. Upload another test image
3. **Verify** upload completes successfully
4. **Verify** the new capture appears at the top of the list (most recent first)
5. **Verify** both captures are visible in the list
6. **Screenshot**: `06_second_capture_listed.png`

### Step 7: File Validation
1. Attempt to select a file with an unsupported extension (if possible via the UI)
2. **Verify** error message appears for invalid file type or the file input only accepts valid extensions
3. **Screenshot**: `07_file_validation.png`

### Step 8: Verify Status Chip Colors
1. **Verify** captures with "pending" status show an orange-colored chip
2. **Screenshot**: `08_status_chips.png`

## Success Criteria

- [ ] Card Capture page loads at `/card-capture` with title "Captura de Tarjetas"
- [ ] Page is accessible via sidebar navigation item "Captura Tarjetas"
- [ ] Upload button/area is visible and prominent (large touch target)
- [ ] Fair name text field ("Nombre de la Feria") is visible and functional
- [ ] File input accepts .png, .jpg, .jpeg images
- [ ] Upload progress indicator is displayed during upload
- [ ] Success feedback is shown after upload completes
- [ ] Uploaded card appears in recent captures list with thumbnail, status, and fair name
- [ ] Status chip shows "pending" with orange color
- [ ] Fair name persists across multiple uploads in the same session
- [ ] Most recent captures appear first in the list
- [ ] All UI text is in Spanish (Colombian)
- [ ] No console errors during test execution

## Notes

- The test creates business card captures which will persist in the database
- The page is designed to be mobile-responsive for use at trade fairs
- Upload uses XMLHttpRequest for progress tracking
- Images are stored via Supabase Storage (or base64 fallback in development)
- Status values: pending, processing, extracted, confirmed, rejected, failed
