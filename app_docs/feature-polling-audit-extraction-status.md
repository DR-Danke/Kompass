# Polling for Audit Extraction Status

**Date:** 2026-02-05
**Type:** Bug Fix / Enhancement

## Overview

Fixed an issue where the Supplier Certification Tab would show "Processing..." indefinitely after uploading a factory audit PDF. The UI now polls the backend to detect when AI extraction completes and automatically updates to display the extracted audit summary.

## Problem

When uploading a factory audit PDF:
1. Backend creates an audit record with `pending` status
2. AI extraction runs asynchronously via FastAPI BackgroundTasks
3. Frontend receives the `pending` status and shows a "Processing..." skeleton
4. **Bug:** Frontend never checked back with the server to detect completion
5. User was stuck seeing "Processing..." forever, even after extraction finished

## Solution

Added automatic polling to `SupplierCertificationTab.tsx`:

1. **Detect pending audits** - Component checks if any audit has `pending` or `processing` status
2. **Start polling** - When pending audits exist, polls the backend every 5 seconds
3. **Silent refresh** - Polling doesn't show loading spinner to avoid UI flicker
4. **Auto-stop** - Polling stops automatically when all audits reach `completed` or `failed` status
5. **Cleanup** - Interval is cleared on component unmount to prevent memory leaks

## Technical Implementation

### Files Modified

- `apps/Client/src/components/kompass/SupplierCertificationTab.tsx`

### Key Changes

```typescript
// Poll for status updates when there are pending/processing audits
useEffect(() => {
  const hasPendingAudits = audits.some(
    (audit) => audit.extraction_status === 'pending' || audit.extraction_status === 'processing'
  );

  if (!hasPendingAudits) return;

  console.log('INFO [SupplierCertificationTab]: Starting polling for pending audits');
  const pollInterval = setInterval(() => {
    fetchAudits(false); // Silent refresh (no loading spinner)
  }, 5000); // Poll every 5 seconds

  return () => {
    console.log('INFO [SupplierCertificationTab]: Stopping polling');
    clearInterval(pollInterval);
  };
}, [audits, fetchAudits]);
```

### Data Flow

```
User uploads PDF
       │
       ▼
Backend creates audit (status: pending)
       │
       ▼
Frontend adds to list, shows "Processing..."
       │
       ▼
Polling starts (every 5 seconds)
       │
       ▼
Backend completes extraction (status: completed)
       │
       ▼
Next poll detects completed status
       │
       ▼
UI updates to show AuditSummaryCard with extracted data
       │
       ▼
Polling stops (no more pending audits)
```

## How to Use

1. Navigate to **Kompass > Suppliers**
2. Click edit on any supplier
3. Switch to the **Certification** tab
4. Upload a factory audit PDF file
5. Observe "Processing..." skeleton appears
6. Wait 5-30 seconds (depending on PDF complexity)
7. UI automatically updates to show extracted summary with:
   - Supplier type (Manufacturer/Trader)
   - Employee count, factory area, production lines
   - Certifications list
   - Markets served chart
   - Positive/negative points
   - A/B/C classification badge

## Configuration

- **Poll interval:** 5 seconds (hardcoded, can be adjusted if needed)
- **Backend extraction timeout:** Varies based on PDF size and AI processing

## Testing

1. Upload a valid PDF and verify the UI updates automatically
2. Upload multiple PDFs and verify all are tracked
3. Close and reopen the dialog - pending audits should resume polling
4. Verify polling stops after all audits complete
5. Check browser console for polling start/stop log messages

## Notes

- Polling only occurs when the Certification tab is visible
- If extraction fails, the UI shows an error state with a "Reprocess" button
- Backend logs extraction progress in the server terminal
- For production, consider WebSocket notifications instead of polling for real-time updates
