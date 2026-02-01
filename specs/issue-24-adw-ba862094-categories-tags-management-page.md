# Feature: Categories and Tags Management Page

## Metadata
issue_number: `24`
adw_id: `ba862094`
issue_json: `{"number":24,"title":"[Kompass] Phase 9D: Categories and Tags Management Page","body":"## Context\n**Current Phase:** Phase 9 of 13 - Frontend Core Pages\n**Current Issue:** KP-024 (Issue 24 of 33)\n**Parallel Execution:** YES - Runs IN PARALLEL with KP-021, KP-022, KP-023.\n\n---\n\n## Description\nCreate management page for product categories and tags.\n\n## Requirements\n\n### File: apps/Client/src/pages/kompass/CategoriesPage.tsx\n\n#### Category Section\n- Tree view with expand/collapse\n- Drag-and-drop to reparent\n- Add child button on each node\n- Edit/delete actions\n- Product count per category\n\n#### Tag Section\n- Tag chips with color\n- Search/filter\n- Create tag dialog (name, color picker)\n- Edit/delete actions\n- Product count per tag\n\n### File: apps/Client/src/components/kompass/CategoryTree.tsx\n- Recursive tree component\n- Expand/collapse icons\n- Drag-and-drop support with react-dnd\n\n### File: apps/Client/src/components/kompass/TagChip.tsx\n- Colored chip with name\n- Delete icon on hover"}`

## Feature Description
Create a comprehensive management page for product categories and tags in the Kompass Portfolio & Quotation System. This page will provide a unified interface for managing the hierarchical category structure with drag-and-drop reparenting capabilities, and a flexible tag management system with color-coded chips. The page enables admins and managers to organize products through intuitive tree navigation and tagging.

## User Story
As a product manager or admin
I want to manage product categories in a visual tree structure and organize tags with colors
So that I can effectively categorize and tag products for easy discovery and portfolio creation

## Problem Statement
The Kompass system requires a user-friendly interface to manage the hierarchical category taxonomy and product tags. Without proper tooling, organizing products becomes cumbersome and error-prone. Users need to visualize the category tree, reparent categories via drag-and-drop, and manage color-coded tags with product counts - all from a single, intuitive page.

## Solution Statement
Implement a dedicated CategoriesPage with two main sections:
1. **Category Management**: A recursive tree component with expand/collapse, drag-and-drop reparenting via HTML5 Drag and Drop API (avoiding react-dnd to keep dependencies minimal), inline add-child buttons, edit/delete actions, and product counts
2. **Tag Management**: A grid of colored chips with search/filter, create/edit dialogs with color pickers, delete capability with confirmation, and product counts per tag

The solution uses Material-UI components for consistent styling, leverages the existing `categoryService` and `tagService` from `kompassService.ts`, and follows established patterns from other Kompass pages.

## Relevant Files
Use these files to implement the feature:

- `apps/Client/src/types/kompass.ts` - Contains TypeScript types for Category and Tag entities (CategoryTreeNode, TagResponse, TagWithCount, CategoryCreate, CategoryUpdate, TagCreate, TagUpdate)
- `apps/Client/src/services/kompassService.ts` - Contains categoryService (getTree, create, update, delete, move) and tagService (list, create, update, delete, search) API methods
- `apps/Client/src/pages/kompass/SuppliersPage.tsx` - Reference for page structure and patterns
- `apps/Client/src/pages/kompass/ProductsPage.tsx` - Reference for placeholder page pattern
- `apps/Client/src/components/layout/Sidebar.tsx` - Navigation structure, may need to add Categories/Tags route
- `apps/Client/src/App.tsx` - Route configuration, may need to add /categories route
- `apps/Client/package.json` - Check dependencies (Note: react-dnd is NOT installed, will use HTML5 drag-drop instead)
- `app_docs/feature-0a08fee5-category-tag-management-service.md` - Backend service documentation
- `app_docs/feature-c58228ec-category-tag-api-routes.md` - Backend API routes documentation
- `app_docs/feature-af7568d5-frontend-types-api-service.md` - Frontend types and service layer documentation
- `.claude/commands/test_e2e.md` - E2E test runner documentation for creating the E2E test file

### New Files
- `apps/Client/src/pages/kompass/CategoriesPage.tsx` - Main categories and tags management page
- `apps/Client/src/components/kompass/CategoryTree.tsx` - Recursive tree component with drag-and-drop
- `apps/Client/src/components/kompass/TagChip.tsx` - Colored tag chip component with delete
- `apps/Client/src/components/kompass/CategoryDialog.tsx` - Dialog for create/edit category
- `apps/Client/src/components/kompass/TagDialog.tsx` - Dialog for create/edit tag with color picker
- `apps/Client/src/hooks/useCategories.ts` - Custom hook for category state management
- `apps/Client/src/hooks/useTags.ts` - Custom hook for tag state management
- `.claude/commands/e2e/test_categories_tags_management.md` - E2E test specification file

## Implementation Plan

### Phase 1: Foundation
1. Create custom hooks `useCategories.ts` and `useTags.ts` for state management and API calls
2. Add navigation item for Categories/Tags to the Sidebar
3. Add route configuration for `/categories` in App.tsx

### Phase 2: Core Components
1. Create `CategoryTree.tsx` - Recursive tree component with:
   - Expand/collapse functionality using MUI TreeView or custom implementation
   - HTML5 Drag and Drop for reparenting (not react-dnd to avoid new dependency)
   - Add child button on each node
   - Edit/delete action buttons
   - Product count display
2. Create `TagChip.tsx` - Colored chip component with:
   - Dynamic background color from tag.color
   - Name display with contrasting text color
   - Delete icon on hover
   - Product count badge
3. Create `CategoryDialog.tsx` - Modal dialog for category CRUD
4. Create `TagDialog.tsx` - Modal dialog for tag CRUD with color picker

### Phase 3: Integration
1. Implement `CategoriesPage.tsx` combining both sections:
   - Category section with tree view
   - Tag section with chip grid
   - Search/filter for tags
   - Loading states and error handling
2. Wire up all components with hooks and services
3. Handle success/error notifications via MUI Snackbar

## Step by Step Tasks

### Step 1: Add Navigation and Route Configuration
- Add "Categories" navigation item to `apps/Client/src/components/layout/Sidebar.tsx` with CategoryIcon
- Add `/categories` route to `apps/Client/src/App.tsx` pointing to CategoriesPage

### Step 2: Create Custom Hooks
- Create `apps/Client/src/hooks/useCategories.ts`:
  - State for categories tree (CategoryTreeNode[])
  - Loading and error states
  - fetchCategories() using categoryService.getTree()
  - createCategory(data) using categoryService.create()
  - updateCategory(id, data) using categoryService.update()
  - deleteCategory(id) using categoryService.delete()
  - moveCategory(id, newParentId) using categoryService.move()
- Create `apps/Client/src/hooks/useTags.ts`:
  - State for tags list (TagWithCount[])
  - Loading and error states
  - Filter/search state
  - fetchTags() using tagService.list()
  - createTag(data) using tagService.create()
  - updateTag(id, data) using tagService.update()
  - deleteTag(id) using tagService.delete()
  - searchTags(query) using tagService.search()

### Step 3: Create TagChip Component
- Create `apps/Client/src/components/kompass/TagChip.tsx`:
  - Props: tag (TagResponse or TagWithCount), onEdit?, onDelete?, showCount?
  - Display MUI Chip with tag.name, styled with tag.color as background
  - Calculate contrasting text color (light/dark) based on background
  - Show delete icon on hover (if onDelete provided)
  - Show product count badge (if showCount and product_count exists)

### Step 4: Create TagDialog Component
- Create `apps/Client/src/components/kompass/TagDialog.tsx`:
  - Props: open, onClose, onSave, tag? (for edit mode)
  - Form fields: name (TextField), color (MUI color input or custom picker)
  - Use react-hook-form for form state
  - Submit calls onSave with TagCreate or TagUpdate data

### Step 5: Create CategoryDialog Component
- Create `apps/Client/src/components/kompass/CategoryDialog.tsx`:
  - Props: open, onClose, onSave, category?, parentId? (for add child)
  - Form fields: name, description, parent_id (select), sort_order, is_active
  - Use react-hook-form for form state
  - Submit calls onSave with CategoryCreate or CategoryUpdate data

### Step 6: Create CategoryTree Component
- Create `apps/Client/src/components/kompass/CategoryTree.tsx`:
  - Props: categories (CategoryTreeNode[]), onAddChild, onEdit, onDelete, onMove
  - Recursive rendering of tree nodes using MUI List/ListItem or custom
  - Expand/collapse state using React useState
  - HTML5 Drag and Drop:
    - draggable="true" on nodes
    - onDragStart: store dragged category ID
    - onDragOver: visual feedback on drop targets
    - onDrop: call onMove(draggedId, targetParentId)
  - Action buttons: Add Child (on folder icon click), Edit (pencil), Delete (trash)
  - Display product_count if available (from backend tree endpoint)

### Step 7: Create CategoriesPage
- Create `apps/Client/src/pages/kompass/CategoriesPage.tsx`:
  - Two-column layout (or tabs) for Categories and Tags sections
  - Category Section:
    - Header with "Categories" title and "Add Root Category" button
    - CategoryTree component with all handlers connected
    - CategoryDialog for create/edit
    - Delete confirmation dialog
  - Tag Section:
    - Header with "Tags" title and "Add Tag" button
    - Search/filter TextField
    - Grid of TagChip components (filtered by search)
    - TagDialog for create/edit
    - Delete confirmation dialog
  - Loading skeletons during fetch
  - Error state with retry button
  - Success/error snackbar notifications

### Step 8: Create E2E Test Specification
- Create `.claude/commands/e2e/test_categories_tags_management.md`:
  - Test navigation to /categories page
  - Test category tree rendering and expand/collapse
  - Test add root category flow
  - Test add child category flow
  - Test edit category
  - Test delete category (with confirmation)
  - Test drag-and-drop reparenting
  - Test tag grid rendering
  - Test tag search/filter
  - Test add tag with color picker
  - Test edit tag
  - Test delete tag (with confirmation)
  - Define success criteria and screenshot requirements

### Step 9: Run Validation Commands
- Run TypeScript type check: `cd apps/Client && npm run typecheck`
- Run ESLint: `cd apps/Client && npm run lint`
- Run build: `cd apps/Client && npm run build`
- Run backend tests: `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short`

## Testing Strategy

### Unit Tests
- Test useCategories hook fetch, create, update, delete, move operations
- Test useTags hook fetch, create, update, delete, search operations
- Test CategoryTree expand/collapse behavior
- Test TagChip color contrast calculation
- Test CategoryDialog form validation
- Test TagDialog form validation

### Edge Cases
- Empty categories tree (no root categories)
- Empty tags list
- Category with many nested children (deep nesting)
- Category delete with children (should show error from API)
- Category drag-and-drop to itself or descendant (prevent via API validation)
- Tag with very long name (truncation)
- Tag search with no results
- Network errors during CRUD operations
- Concurrent updates (optimistic UI vs server state)

## Acceptance Criteria
- [ ] Category tree renders with hierarchical structure showing all categories
- [ ] Categories can be expanded/collapsed to show/hide children
- [ ] New root category can be created via dialog
- [ ] Child category can be added to existing category via dialog
- [ ] Category can be edited via dialog
- [ ] Category can be deleted with confirmation (fails if has children/products)
- [ ] Category can be reparented via drag-and-drop
- [ ] Product count displays per category (if endpoint supports it)
- [ ] Tag grid renders all tags as colored chips
- [ ] Tags can be filtered by search query
- [ ] New tag can be created via dialog with color picker
- [ ] Tag can be edited via dialog
- [ ] Tag can be deleted with confirmation
- [ ] Product count displays per tag
- [ ] Loading states show during API operations
- [ ] Error states show with retry option on failures
- [ ] Success/error notifications appear for CRUD operations
- [ ] Page is accessible via navigation sidebar
- [ ] TypeScript builds without errors
- [ ] ESLint passes without warnings
- [ ] Production build succeeds

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Run TypeScript type check
cd apps/Client && npm run typecheck

# Run ESLint
cd apps/Client && npm run lint

# Run production build
cd apps/Client && npm run build

# Run backend tests to ensure API compatibility
cd apps/Server && .venv/bin/pytest tests/ -v --tb=short
```

After completing implementation:
- Read `.claude/commands/test_e2e.md` for E2E test execution instructions
- Execute the E2E test: `.claude/commands/e2e/test_categories_tags_management.md`

## Notes

### Dependencies
- No new npm dependencies required. Using HTML5 Drag and Drop API instead of react-dnd to avoid adding new dependencies
- Color picker can be implemented using native HTML5 `<input type="color">` or MUI's TextField with type="color"

### API Considerations
- `categoryService.getTree()` returns `CategoryTreeNode[]` with nested children
- `categoryService.move(id, parentId)` handles reparenting
- The backend prevents cycles (moving category to its own descendant)
- `tagService.list()` returns `TagWithCount[]` with product_count

### Future Enhancements
- Consider adding category icon selection
- Consider adding tag grouping/categories
- Consider adding bulk operations (multi-select delete)
- Consider adding import/export functionality
