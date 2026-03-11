# Clickable Recent Captures Navigation

**ADW ID:** a973c501
**Date:** 2026-03-10
**Specification:** specs/issue-170-adw-a973c501-sdlc_planner-clickable-recent-captures-navigation.md

## Overview

Makes the recent captures cards on the CardCapturePage clickable, allowing users to navigate directly to the CardReviewPage with the corresponding capture highlighted. This builds on the existing `highlightCaptureId` mechanism introduced in issue #169 (auto-navigate after capture), extending it to manual click-based navigation.

## What Was Built

- Clickable capture cards with `onClick` handler navigating to `/card-review` with capture ID in router state
- Visual hover feedback: `cursor: pointer` and elevated box shadow on hover with smooth transition
- `stopPropagation` on all action buttons (Extraer, Reintentar, Crear Proveedor) to prevent card navigation when clicking buttons
- E2E test specification for validating clickable captures navigation

## Technical Implementation

### Files Modified

- `apps/Client/src/pages/kompass/CardCapturePage.tsx`: Added click handler, hover styles, and `stopPropagation` on action buttons (+17 lines, -5 lines)
- `.claude/commands/e2e/test_clickable_recent_captures.md`: New E2E test specification for the feature
- `playwright-mcp-config.json`: Minor config update

### Key Changes

- Each `<Card>` in the recent captures list now has `onClick={() => navigate('/card-review', { state: { highlightCaptureId: capture.id } })}` to navigate with the capture ID
- Cards show `cursor: pointer` and `boxShadow: 3` on hover via MUI `sx` prop with `transition: 'box-shadow 0.2s ease-in-out'`
- Three action buttons (Extraer, Reintentar, Crear Proveedor) use `e.stopPropagation()` to prevent their clicks from bubbling up to the card-level click handler
- No changes needed on CardReviewPage — it already supports `highlightCaptureId` in `location.state` with scroll-to and pulse animation

## How to Use

1. Navigate to the **Captura de Tarjetas** page (`/card-capture`)
2. View the **Capturas Recientes** section showing previously captured business cards
3. Hover over any capture card to see the elevated shadow feedback
4. Click on a capture card to navigate to the **Revisión de Tarjetas** page (`/card-review`)
5. The corresponding capture row will be highlighted with a pulse animation and scrolled into view
6. Action buttons (Extraer, Reintentar, Crear Proveedor) continue to work independently without triggering navigation

## Configuration

No additional configuration required. The feature uses React Router's `state` parameter for navigation, consistent with the auto-navigate pattern.

## Testing

- Run `cd apps/Client && npx tsc --noEmit` to verify no TypeScript errors
- Run `cd apps/Client && npm run build` to verify production build succeeds
- Run `cd apps/Client && npm run lint` to verify no linting issues
- Execute the E2E test via `/e2e:test_clickable_recent_captures` to validate end-to-end behavior

## Notes

- Leverages the existing `highlightCaptureId` mechanism on CardReviewPage built in issue #169
- Navigation uses React Router `state` (does not change URL) — consistent with auto-navigate pattern
- Only one source file modified (`CardCapturePage.tsx`), no new dependencies
- Cards in all statuses (pending, processing, extracted, confirmed, rejected, failed) are clickable
