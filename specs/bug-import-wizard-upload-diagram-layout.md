# Bug: Import Wizard Upload Diagram Layout Issue

## Metadata
issue_number: ``
adw_id: ``
issue_json: ``

## Bug Description
The Import Wizard page displays the file upload area incorrectly. The dashed box with the cloud upload icon and text ("Drag and drop files here" / "or click to browse") is not rendering with proper layout. The visual appearance shows the content appearing compressed or misaligned, with the dashed border box not having adequate height to properly display the upload icon and accompanying text.

**Symptoms:**
- Upload area dashed box appears collapsed or too small
- Content inside the upload area may be cut off or misaligned
- The cloud upload icon and text are not properly centered or visible

**Expected Behavior:**
- The upload area should have a clearly visible dashed border box
- The cloud upload icon should be prominently displayed and centered
- Text labels ("Drag and drop files here", "or click to browse", and supported formats info) should be clearly visible and properly spaced
- The entire upload area should have adequate height (minimum 200-250px) to display all content comfortably

**Actual Behavior:**
- The upload area appears compressed with insufficient height
- Layout does not provide adequate visual spacing for the upload interface elements

## Problem Statement
The file upload drag-and-drop area in the Import Wizard's Upload step (Step 1) does not have proper minimum height or padding constraints, causing the upload interface to display improperly with insufficient vertical space for the cloud icon and text content.

## Solution Statement
Add explicit `minHeight` styling to the drag-and-drop upload Box component in `ImportWizardPage.tsx` to ensure the upload area always renders with adequate vertical space. Additionally, ensure proper vertical padding and spacing for all child elements (icon, title, subtitle, caption) to create a visually balanced and user-friendly upload interface.

## Steps to Reproduce
1. Start the frontend server: `cd apps/Client && npm run dev`
2. Log in to the application with valid credentials
3. Navigate to "Import Wizard" from the sidebar
4. Observe the upload area on Step 1 (Upload Files)
5. **Bug**: The dashed box with the cloud icon appears collapsed or improperly sized
6. Compare with expected design: should show a spacious upload area with centered icon and text

## Root Cause Analysis
The `renderUploadStep()` function in `apps/Client/src/pages/kompass/ImportWizardPage.tsx` (lines 396-465) defines the upload area Box component with border, padding, and drag-and-drop handlers, but lacks explicit `minHeight` styling.

**Root Cause:**
- The Box component at line 398 has `p: 4` (padding) but no `minHeight` property
- Without a minimum height constraint, the Box collapses to fit only its immediate content
- Material-UI's default flex/box behavior does not guarantee adequate vertical space
- The icon (CloudUploadIcon at line 422) and Typography components (lines 423-429) stack vertically but don't force minimum container height

**Why it fails:**
When the Box renders, Material-UI calculates the minimum required height based on content, but with default line-height and icon size, this results in a compressed appearance. The padding (`p: 4` = 32px) is insufficient to create the expected spacious upload area.

**Solution:**
Adding `minHeight: 250` (or similar value) to the Box `sx` prop will ensure the container always maintains adequate vertical space regardless of content, creating the expected visual design.

## Relevant Files
Use these files to fix the bug:

- `apps/Client/src/pages/kompass/ImportWizardPage.tsx` - Main Import Wizard component containing the upload step rendering logic. The `renderUploadStep()` function (lines 396-465) specifically needs modification to add `minHeight` to the upload Box component (lines 398-414).

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Fix Upload Area Layout
- Open `apps/Client/src/pages/kompass/ImportWizardPage.tsx`
- Locate the `renderUploadStep()` function (line 396)
- Find the Box component with drag-and-drop handlers (line 398)
- Add `minHeight: 250` to the Box component's `sx` prop object
- Optionally adjust vertical padding or spacing for icon and text elements if needed for better visual balance
- Save the file

### 2. Validate Fix Visually
- Start the frontend development server if not running: `cd apps/Client && npm run dev`
- Navigate to Import Wizard page in browser
- Verify the upload area now displays with adequate height
- Verify the cloud icon is centered and prominent
- Verify all text labels are visible and properly spaced
- Take a screenshot to confirm the fix

### 3. Run Validation Commands
- Execute all validation commands listed below to ensure zero regressions
- Verify TypeScript compilation succeeds
- Verify frontend build succeeds
- Optionally run E2E test to validate full Import Wizard workflow

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

Before fix:
- Navigate to Import Wizard page and observe the compressed upload area

After fix:
- Navigate to Import Wizard page and verify upload area displays with proper height and spacing
- Verify all UI elements (cloud icon, text, supported formats) are visible and centered

TypeScript and Build Validation:
- `cd apps/Client && npm run typecheck` - Run TypeScript check to validate no type errors
- `cd apps/Client && npm run build` - Run Client build to validate the fix compiles successfully

## Notes
- The fix is minimal and surgical - only adding a `minHeight` style property
- No new dependencies or libraries required
- The change affects only visual presentation, no functional logic changes
- Consider testing across different screen sizes to ensure responsive behavior
- The `minHeight: 250` value may be adjusted based on design preferences (range 200-300px is reasonable)
- This is a CSS/styling fix with zero impact on business logic or data processing
