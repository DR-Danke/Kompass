# Niches Configuration Page

**ADW ID:** e37ee810
**Date:** 2026-02-01
**Specification:** specs/issue-27-adw-e37ee810-niches-configuration-page.md

## Overview

This feature implements a Niches Configuration Page for the Kompass Portfolio & Quotation system. Niches are client type classifications (e.g., Constructoras, Hoteles, Retailers) that help categorize clients for targeted portfolio management. The page provides a card-based UI to list, create, edit, and delete niches while enforcing business rules such as preventing deletion of niches with associated clients.

## What Was Built

- **NichesPage component**: Main page displaying niches in a responsive card grid with name, description, and client count
- **NicheForm component**: Dialog form for creating and editing niches using react-hook-form
- **Route and navigation**: `/niches` route added to the application with sidebar navigation using LabelIcon
- **Delete protection**: Handles 409 Conflict when attempting to delete niches with associated clients
- **E2E test specification**: Test coverage for all CRUD operations and delete validation

## Technical Implementation

### Files Modified

- `apps/Client/src/App.tsx`: Added NichesPage import and `/niches` route
- `apps/Client/src/components/layout/Sidebar.tsx`: Added "Niches" navigation item with LabelIcon

### Files Created

- `apps/Client/src/pages/kompass/NichesPage.tsx`: Main page component (271 lines)
- `apps/Client/src/components/kompass/NicheForm.tsx`: Form dialog component (155 lines)
- `.claude/commands/e2e/test_niches_page.md`: E2E test specification

### Key Changes

- **Card-based layout**: Uses Material-UI Grid with Card components to display niches in a responsive 3-column (md), 2-column (sm), 1-column (xs) layout
- **Client count badge**: Each card shows a Chip with PeopleIcon displaying the number of clients assigned to the niche
- **Form validation**: Name field is required; description is optional with multiline input
- **Delete confirmation**: Two-step delete process with confirmation dialog
- **409 error handling**: Catches axios 409 Conflict response and displays user-friendly message when niche has clients
- **Loading states**: Shows CircularProgress during data fetching and form submission
- **Empty state**: Displays helpful message when no niches exist

## How to Use

1. Navigate to the Niches page via the sidebar (click "Niches" link)
2. View existing niches displayed as cards showing name, description, and client count
3. Click "Add Niche" button to create a new niche
4. Fill in the name (required) and optional description in the form dialog
5. Click "Create" to save the new niche
6. To edit, click the pencil icon on any niche card
7. To delete, click the trash icon and confirm in the dialog
8. If a niche has clients, deletion will be blocked with an error message

## Configuration

No additional configuration required. The page uses the existing:
- `nicheService` from `@/services/kompassService` for API calls
- JWT authentication via existing auth context
- Material-UI theme for styling

## Testing

Run the E2E tests using the test specification:
```bash
# Read and execute the E2E test
# .claude/commands/e2e/test_niches_page.md
```

Test coverage includes:
- Navigate to Niches page
- Verify page structure (title, add button, cards/list)
- Create new niche
- Edit existing niche
- Delete niche (success case)
- Delete blocked validation (attempt to delete niche with clients)

## Notes

- The backend returns `NicheWithClientCount` which includes the `client_count` field for each niche
- The backend returns 409 Conflict when attempting to delete a niche that has associated clients
- Default niches (seeded): Constructoras, Estudios de Arquitectura, Desarrolladores, Hoteles, Operadores Rentas Cortas, Retailers
- The implementation follows patterns established in SuppliersPage.tsx and SupplierForm.tsx
- Card descriptions are truncated to 3 lines with ellipsis overflow
- Niche names are truncated with ellipsis when exceeding available width
