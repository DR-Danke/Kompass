# Portfolio Builder Page with Interactive Product Selection

**ADW ID:** 2287ac8d
**Date:** 2026-02-01
**Specification:** specs/issue-25-adw-2287ac8d-portfolio-builder-page.md

## Overview

This feature implements a complete portfolio management system for the Kompass application, allowing sales representatives to create, manage, and share curated product collections for clients. It includes a portfolios list page with card grid view and a two-column interactive builder with drag-and-drop product reordering using @dnd-kit.

## What Was Built

- **PortfoliosPage** - Grid-based portfolio list with search, filters, pagination, and quick actions
- **PortfolioBuilderPage** - Two-column builder interface for creating/editing portfolios
- **ProductCatalogMini** - Compact product browser for selecting products to add to portfolios
- **PortfolioBuilder** - Drag-and-drop sortable product list using @dnd-kit
- **PortfolioCard** - Card component displaying portfolio preview with actions
- **PortfolioItemCard** - Draggable portfolio item with curator notes support
- **PortfolioStatusBadge** - Status indicator chip (Published/Draft)
- **usePortfolios** - Hook for portfolio list management and CRUD operations
- **usePortfolioBuilder** - Hook for builder state management with optimistic updates
- **E2E Test Specification** - Playwright test file for portfolio builder functionality

## Technical Implementation

### Files Modified

- `apps/Client/src/App.tsx`: Added route for `/portfolios/:id` to PortfolioBuilderPage
- `apps/Client/package.json`: Added @dnd-kit/core, @dnd-kit/sortable, @dnd-kit/utilities dependencies
- `playwright-mcp-config.json`: Updated test file path

### New Files Created

- `apps/Client/src/pages/kompass/PortfolioBuilderPage.tsx`: Main builder page with two-column layout
- `apps/Client/src/pages/kompass/PortfoliosPage.tsx`: Full portfolio list page (replaced placeholder)
- `apps/Client/src/components/kompass/PortfolioBuilder.tsx`: Drag-drop sortable container
- `apps/Client/src/components/kompass/PortfolioCard.tsx`: Portfolio preview card
- `apps/Client/src/components/kompass/PortfolioItemCard.tsx`: Draggable item with notes
- `apps/Client/src/components/kompass/PortfolioStatusBadge.tsx`: Status badge component
- `apps/Client/src/components/kompass/ProductCatalogMini.tsx`: Mini catalog browser
- `apps/Client/src/hooks/kompass/usePortfolios.ts`: List management hook
- `apps/Client/src/hooks/kompass/usePortfolioBuilder.ts`: Builder state hook
- `.claude/commands/e2e/test_portfolio_builder.md`: E2E test specification

### Key Changes

- **Drag-and-Drop**: Implemented using @dnd-kit library for React 19 compatibility, with PointerSensor and KeyboardSensor support
- **Optimistic Updates**: Builder hook manages local state optimistically and syncs with backend on save
- **Two-Column Layout**: 40% left panel for product catalog, 60% right panel for portfolio builder
- **Product Details Loading**: Portfolio builder fetches product details on-demand when items are added
- **Infinite Scroll**: ProductCatalogMini supports lazy loading with scroll-based pagination
- **Share Token Generation**: Integration with portfolioService.getShareToken() for JWT-based share links

## How to Use

### Viewing Portfolios

1. Navigate to `/portfolios` from the sidebar
2. Browse the grid of portfolio cards
3. Use search box to filter by portfolio name
4. Use niche dropdown to filter by client niche
5. Use status dropdown to filter by Published/Draft
6. Click "Create Portfolio" to start a new portfolio

### Building a Portfolio

1. Click "Create Portfolio" or open an existing portfolio
2. **Left Panel**: Browse products by search or category filter
3. Click a product in the left panel to add it to your portfolio
4. **Right Panel**: View and arrange portfolio items
5. Drag items to reorder them
6. Click the X button on an item to remove it
7. Add curator notes to each item using the text field

### Managing Portfolio Metadata

1. Edit the portfolio name using the text field in the top bar
2. Select a niche from the dropdown
3. Toggle Published/Draft status with the switch
4. Click "Save" to persist changes

### Sharing and Exporting

1. Click the link icon to copy a shareable URL to clipboard
2. Click the PDF icon to download a PDF export
3. Share links are JWT-based and expire after 30 days

## Configuration

No additional configuration required. The feature uses existing environment variables:
- `VITE_API_URL` - Backend API URL for portfolio service calls

## Testing

Run the E2E tests using the test specification:

```bash
# Execute the portfolio builder E2E test
/test_e2e e2e:test_portfolio_builder
```

Manual testing checklist:
- Create a new portfolio and add products
- Reorder products using drag-and-drop
- Save and verify persistence
- Test search and filtering in both list and builder views
- Verify share link generation and PDF export

## Notes

- Products already in the portfolio show an "Added" chip and cannot be added again
- The builder tracks dirty state and only enables Save when changes exist
- For new portfolios, items are stored locally until first save
- PDF export opens in a new tab to preserve builder state
- Cover image for portfolio cards uses the first product's primary image
