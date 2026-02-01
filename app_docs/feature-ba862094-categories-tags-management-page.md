# Categories and Tags Management Page

**ADW ID:** ba862094
**Date:** 2026-02-01
**Specification:** specs/issue-24-adw-ba862094-categories-tags-management-page.md

## Overview

A comprehensive management page for product categories and tags in the Kompass Portfolio & Quotation System. The page provides a unified interface for managing the hierarchical category structure with drag-and-drop reparenting capabilities, and a flexible tag management system with color-coded chips and search functionality.

## What Was Built

- **CategoriesPage**: Main management page with split-view layout for categories and tags
- **CategoryTree**: Recursive tree component with expand/collapse and HTML5 drag-and-drop
- **TagChip**: Colored chip component with automatic contrast text color
- **CategoryDialog**: Modal dialog for category CRUD with parent selection
- **TagDialog**: Modal dialog for tag CRUD with color picker
- **useCategories**: Custom hook for category state management and API operations
- **useTags**: Custom hook for tag state management with search/filter

## Technical Implementation

### Files Modified

- `apps/Client/src/App.tsx`: Added `/categories` route for CategoriesPage
- `apps/Client/src/components/layout/Sidebar.tsx`: Added "Categories" navigation item
- `apps/Client/.eslintrc.cjs`: Added ESLint rule exceptions for accessibility on interactive elements

### Files Created

- `apps/Client/src/pages/kompass/CategoriesPage.tsx`: Main page component (484 lines)
- `apps/Client/src/components/kompass/CategoryTree.tsx`: Recursive tree with drag-and-drop (378 lines)
- `apps/Client/src/components/kompass/TagChip.tsx`: Colored chip component (107 lines)
- `apps/Client/src/components/kompass/CategoryDialog.tsx`: Category create/edit dialog (191 lines)
- `apps/Client/src/components/kompass/TagDialog.tsx`: Tag create/edit dialog (170 lines)
- `apps/Client/src/hooks/useCategories.ts`: Category state management hook (134 lines)
- `apps/Client/src/hooks/useTags.ts`: Tag state management hook (128 lines)
- `.claude/commands/e2e/test_categories_tags_management.md`: E2E test specification

### Key Changes

- **HTML5 Drag and Drop**: Implemented native drag-and-drop for category reparenting without external dependencies (no react-dnd)
- **Automatic Contrast Colors**: TagChip calculates text color based on background luminance for optimal readability
- **Tree Structure**: Recursive tree rendering with expand/collapse state management and visual depth indicators
- **Root Drop Zone**: Special drop target at bottom of tree for moving categories to root level
- **Search/Filter**: Client-side tag filtering by name using memoized filtering

## How to Use

1. Navigate to the Categories & Tags page via the sidebar "Categories" link or `/categories` route
2. **Category Management**:
   - Click "Add Root Category" to create a top-level category
   - Hover over a category to reveal action buttons (Add Child, Edit, Delete)
   - Click the expand/collapse icon to toggle child visibility
   - Drag a category and drop it on another to make it a child
   - Drag to the "Drop here to move to root level" zone to move to root
3. **Tag Management**:
   - Click "Add Tag" to create a new tag with name and color
   - Use the search field to filter tags by name
   - Hover over a tag to reveal edit and delete buttons
   - Tags display product count when available

## Configuration

No additional configuration required. The feature uses:
- Existing `categoryService` and `tagService` from `kompassService.ts`
- Standard Material-UI theming
- Native HTML5 Drag and Drop API (no external dependencies)

## Testing

Run the E2E tests using the test specification:
```bash
# Execute E2E test for categories and tags management
/test_e2e .claude/commands/e2e/test_categories_tags_management.md
```

Manual testing checklist:
- [ ] Category tree renders with hierarchical structure
- [ ] Categories expand/collapse correctly
- [ ] New root category can be created
- [ ] Child categories can be added
- [ ] Categories can be edited
- [ ] Categories can be deleted (fails if has children)
- [ ] Drag-and-drop reparenting works
- [ ] Tag grid displays all tags with colors
- [ ] Tag search filters correctly
- [ ] New tags can be created with color picker
- [ ] Tags can be edited and deleted

## Notes

### Architecture Decisions
- Used HTML5 Drag and Drop API instead of react-dnd to avoid adding dependencies
- Used native HTML5 `<input type="color">` for color picker instead of external library
- Implemented recursive TreeNode component for unlimited category nesting depth
- Used MUI `Collapse` component for smooth expand/collapse animations

### API Dependencies
- `categoryService.getTree()`: Fetches nested category tree structure
- `categoryService.move(id, parentId)`: Handles reparenting with backend validation
- `tagService.list()`: Fetches paginated tag list
- Backend prevents category cycles and validates parent relationships

### Future Enhancements
- Category icon selection
- Tag grouping/categories
- Bulk operations (multi-select delete)
- Import/export functionality
