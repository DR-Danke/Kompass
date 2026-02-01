# Feature: Products Catalog Page (Biblia General)

## Metadata
issue_number: `22`
adw_id: `e17d0e09`
issue_json: `{"number":22,"title":"[Kompass] Phase 9B: Products Catalog Page (Biblia General)","body":"..."}`

## Feature Description
Create the main products catalog page with grid and table views for the Kompass application. This page will serve as the central hub for managing the "Biblia General" - the master product database. Users will be able to browse, search, filter, and manage products with support for both visual grid view (product cards) and detailed table view. The page will include comprehensive filtering options (supplier, category, price range, MOQ, tags, status, image presence), full-text search, pagination, sorting, and CRUD operations through a multi-step product form.

## User Story
As a Kompass user (admin, manager, or regular user)
I want to browse, search, filter, and manage products in a catalog interface
So that I can efficiently find, view, and maintain product information in the Biblia General

## Problem Statement
The current ProductsPage is a placeholder showing "Coming Soon". Users need a fully functional products catalog page to manage the master product database with multiple view options, comprehensive filtering, search capabilities, and forms for creating/editing products.

## Solution Statement
Implement a complete products catalog page with:
1. **Dual view modes**: Grid view with product cards and table view with sortable columns
2. **Advanced filtering**: Filter panel with supplier dropdown, category tree selector, price range slider, MOQ range, tags multi-select, status dropdown, and has-images checkbox
3. **Search and sort**: Full-text search bar and sortable column headers
4. **Pagination**: Page navigation with configurable page size
5. **CRUD operations**: Add Product button, edit functionality, bulk actions, and delete with confirmation
6. **Product cards**: Display image with fallback, name, SKU, price, status badge, supplier link, and quick actions
7. **Multi-step product form**: Form with steps for Basic Info, Pricing, Details, Images, and Tags

## Relevant Files
Use these files to implement the feature:

- `apps/Client/src/pages/kompass/ProductsPage.tsx` - **Main file to modify** - Currently placeholder, will become the products catalog page
- `apps/Client/src/services/kompassService.ts` - Contains `productService` with all API methods (list, get, create, update, delete, search, bulkCreate, addImage, removeImage, setPrimaryImage, addTag, removeTag)
- `apps/Client/src/types/kompass.ts` - Contains all TypeScript types: `ProductResponse`, `ProductCreate`, `ProductUpdate`, `ProductFilter`, `ProductListResponse`, `ProductStatus`, `ProductImageCreate`, `TagResponse`, `SupplierResponse`, `CategoryTreeNode`, etc.
- `apps/Client/src/pages/LoginPage.tsx` - Reference for react-hook-form patterns with Material-UI
- `apps/Client/src/pages/DashboardPage.tsx` - Reference for page layout patterns
- `apps/Client/src/components/layout/MainLayout.tsx` - Reference for layout context
- `apps/Client/src/hooks/useAuth.ts` - Authentication hook pattern
- `apps/Client/src/api/clients/index.ts` - API client with axios interceptors
- `apps/Server/app/api/product_routes.py` - Backend API endpoints for reference (filtering, pagination, sorting parameters)
- `app_docs/feature-0081e866-product-service-biblia-general.md` - Backend product service documentation
- `app_docs/feature-e7062de8-product-api-routes.md` - Backend API routes documentation
- `app_docs/feature-af7568d5-frontend-types-api-service.md` - Frontend types and service documentation
- `.claude/commands/test_e2e.md` - E2E test runner instructions
- `.claude/commands/e2e/test_basic_query.md` - E2E test example template (if exists)

### New Files
The following files need to be created:
- `apps/Client/src/components/kompass/ProductCard.tsx` - Product card component for grid view
- `apps/Client/src/components/kompass/ProductForm.tsx` - Multi-step product create/edit form
- `apps/Client/src/components/kompass/ProductTable.tsx` - Data table component for table view
- `apps/Client/src/components/kompass/ProductFilters.tsx` - Filter panel component
- `apps/Client/src/components/kompass/ProductStatusBadge.tsx` - Status badge component
- `apps/Client/src/hooks/kompass/useProducts.ts` - Custom hook for products data management
- `.claude/commands/e2e/test_products_catalog.md` - E2E test file for the products catalog feature

## Implementation Plan
### Phase 1: Foundation
1. Create the `useProducts` custom hook to manage product data fetching, filtering, pagination, and state
2. Create the `ProductStatusBadge` component for consistent status display
3. Set up the basic page structure with view toggle, search bar, and action buttons

### Phase 2: Core Implementation
1. Implement `ProductFilters` component with all filter controls
2. Implement `ProductCard` component with image, details, status, and quick actions
3. Implement `ProductTable` component with sortable columns and row actions
4. Implement `ProductForm` as a multi-step dialog/modal for create/edit operations
5. Update `ProductsPage` to integrate all components

### Phase 3: Integration
1. Wire up all filters to the API through the useProducts hook
2. Implement pagination controls with page size selector
3. Add bulk action functionality
4. Implement create/edit/delete operations with proper feedback
5. Add loading states and error handling
6. Create E2E test file for validation

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create E2E Test Specification File
- Read `.claude/commands/test_e2e.md` to understand E2E test format
- Create `.claude/commands/e2e/test_products_catalog.md` with test steps for:
  - Loading the products page
  - Switching between grid and table views
  - Using search functionality
  - Applying filters (at least supplier and status filters)
  - Creating a new product via the form
  - Editing an existing product
  - Verifying pagination works

### Step 2: Create useProducts Custom Hook
- Create `apps/Client/src/hooks/kompass/useProducts.ts`
- Implement state management for:
  - Products list with pagination
  - Loading and error states
  - Filter state (supplier_id, category_id, status, price range, MOQ range, tag_ids, has_images, search)
  - Sort state (sort_by, sort_order)
  - View mode (grid/table)
  - Page and page size
- Implement functions:
  - `fetchProducts()` - Fetch products with current filters
  - `setFilter(key, value)` - Update a filter value
  - `clearFilters()` - Reset all filters
  - `setPage(page)` - Change page
  - `setPageSize(size)` - Change page size
  - `setSort(field, order)` - Change sorting
  - `toggleViewMode()` - Switch between grid/table
- Use `productService` from kompassService.ts

### Step 3: Create ProductStatusBadge Component
- Create `apps/Client/src/components/kompass/ProductStatusBadge.tsx`
- Accept `status: ProductStatus` prop
- Use Material-UI Chip component with appropriate colors:
  - active: success (green)
  - inactive: default (grey)
  - draft: warning (yellow)
  - discontinued: error (red)

### Step 4: Create ProductFilters Component
- Create `apps/Client/src/components/kompass/ProductFilters.tsx`
- Implement collapsible filter panel using Material-UI Accordion or Drawer
- Include filter controls:
  - Supplier dropdown (async load from supplierService.list)
  - Category tree selector (async load from categoryService.getTree)
  - Price range slider (min/max with TextField inputs)
  - MOQ range (min/max TextFields)
  - Tags multi-select (async load from tagService.list with Autocomplete)
  - Status dropdown (ProductStatus options)
  - Has images checkbox
- Accept `filters` state and `onFilterChange` callback props
- Include "Clear Filters" button

### Step 5: Create ProductCard Component
- Create `apps/Client/src/components/kompass/ProductCard.tsx`
- Accept `product: ProductResponse` prop and action callbacks
- Display:
  - Product image with fallback placeholder (use Box with background or img tag)
  - Product name (Typography h6)
  - SKU (Typography caption)
  - Price with currency formatting
  - ProductStatusBadge
  - Supplier name as link/chip
  - Tags as chips (limited display, e.g., first 3)
- Include quick actions (IconButton):
  - View/Edit (EditIcon)
  - Delete (DeleteIcon)
- Use Material-UI Card with CardMedia, CardContent, CardActions

### Step 6: Create ProductTable Component
- Create `apps/Client/src/components/kompass/ProductTable.tsx`
- Use Material-UI Table, TableHead, TableBody, TableRow, TableCell
- Implement sortable column headers with TableSortLabel
- Columns: Image (thumbnail), Name, SKU, Supplier, Category, Price, MOQ, Status, Actions
- Accept `products`, `sort`, `onSortChange`, and action callbacks as props
- Include row actions (IconButton): Edit, Delete
- Show product image as small thumbnail

### Step 7: Create ProductForm Component (Multi-Step)
- Create `apps/Client/src/components/kompass/ProductForm.tsx`
- Use Material-UI Dialog, Stepper, Step, StepLabel
- Use react-hook-form for form management
- Implement steps:
  1. **Basic Info**: name (required), sku (optional), description, supplier_id (required dropdown), category_id (tree select), status
  2. **Pricing**: unit_cost, unit_price, currency (default USD), unit_of_measure
  3. **Details**: minimum_order_qty, lead_time_days, weight_kg, dimensions, origin_country, hs_code_id
  4. **Images**: List current images, add new image URL input, set primary, remove
  5. **Tags**: Multi-select for existing tags, add new tag
- Accept `open`, `onClose`, `product` (optional for edit mode), `onSave` props
- Include validation for required fields
- Show loading state during save

### Step 8: Update ProductsPage - Main Integration
- Rewrite `apps/Client/src/pages/kompass/ProductsPage.tsx`
- Import and use useProducts hook
- Implement page layout:
  - Page header with title "Biblia General" and "Add Product" button
  - Search bar (TextField with search icon)
  - View toggle buttons (Grid/Table icons using ToggleButtonGroup)
  - ProductFilters component (collapsible on left or as drawer)
  - Main content area:
    - Grid view: Use MUI Grid to display ProductCard components
    - Table view: ProductTable component
  - Pagination controls at bottom (TablePagination or custom)
- Handle states:
  - Loading: Show CircularProgress or Skeleton
  - Empty: Show "No products found" message
  - Error: Show Alert with error message
- Implement handlers:
  - onSearch - debounced search input handler
  - onFilterChange - filter updates
  - onSortChange - sort updates
  - onPageChange, onPageSizeChange - pagination
  - onAddProduct - open form in create mode
  - onEditProduct - open form in edit mode with product data
  - onDeleteProduct - show confirmation dialog, then delete
- Include ProductForm dialog for create/edit

### Step 9: Add Bulk Actions Support
- Add checkbox selection to ProductCard and ProductTable
- Add bulk action toolbar that appears when items are selected
- Implement bulk actions:
  - Bulk delete (with confirmation)
  - Bulk status change dropdown
- Update useProducts hook with selection state

### Step 10: Add Loading and Error States
- Add Skeleton components for loading states in grid/table views
- Add proper error boundaries
- Add toast/snackbar notifications for success/error feedback
- Use MUI Alert for inline error messages

### Step 11: Run Validation Commands
- Run `cd apps/Client && npm run typecheck` to validate TypeScript
- Run `cd apps/Client && npm run lint` to check linting
- Run `cd apps/Client && npm run build` to verify production build
- Run `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` to ensure backend tests pass
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_products_catalog.md` to validate the feature end-to-end

## Testing Strategy
### Unit Tests
- Test useProducts hook with mock API responses
- Test ProductStatusBadge renders correct colors for each status
- Test ProductFilters correctly calls onFilterChange with filter values
- Test ProductCard displays all product information correctly
- Test ProductTable sorts correctly when headers clicked
- Test ProductForm validation for required fields

### Edge Cases
- Empty products list displays appropriate message
- Very long product names are truncated with ellipsis
- Products without images show fallback placeholder
- Products without tags display gracefully
- Filter with no results shows "No products match filters" message
- Network errors during fetch show error state with retry option
- Form submission with invalid data shows validation errors
- Delete last product on page navigates to previous page

## Acceptance Criteria
- [ ] Grid view renders product cards with image, name, SKU, price, supplier, status badge
- [ ] Table view renders with sortable columns (name, price, MOQ, created_at)
- [ ] View toggle switches between grid and table views
- [ ] All filters work correctly: supplier, category, price range, MOQ, tags, status, has_images
- [ ] Full-text search filters products by name, SKU, description
- [ ] Pagination displays correct page info and navigates pages
- [ ] Page size selector changes items per page
- [ ] "Add Product" button opens create form
- [ ] Product form has 5 steps: Basic Info, Pricing, Details, Images, Tags
- [ ] Edit product pre-fills form with existing data
- [ ] Delete product shows confirmation and removes product
- [ ] Image upload/management works in product form
- [ ] Tag management works in product form
- [ ] Loading states display while fetching data
- [ ] Error states display appropriate messages with retry options

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Navigate to Client directory and run type check
cd apps/Client && npm run typecheck

# Run linting
cd apps/Client && npm run lint

# Run production build
cd apps/Client && npm run build

# Run backend tests to ensure no regressions
cd apps/Server && .venv/bin/pytest tests/ -v --tb=short

# Run ruff check on backend
cd apps/Server && .venv/bin/ruff check .
```

E2E Validation:
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_products_catalog.md` to validate the products catalog functionality works end-to-end.

## Notes
- The backend API already supports all required functionality (filtering, pagination, sorting, CRUD, images, tags) via `apps/Server/app/api/product_routes.py`
- The frontend service layer is complete in `apps/Client/src/services/kompassService.ts` with `productService`
- All TypeScript types are defined in `apps/Client/src/types/kompass.ts`
- Follow existing patterns: use `@/` path alias, Material-UI components, react-hook-form for forms
- Use logging pattern: `console.log('INFO [ComponentName]: message')`
- Consider debouncing search input to avoid excessive API calls
- Image URLs are stored as strings; actual file upload is handled externally (URLs provided)
- The category tree selector should use CategoryTreeNode[] from categoryService.getTree()
- Price range slider should accept decimal values for precise filtering
- Consider using React Query or SWR for data fetching in the future, but for now follow existing patterns with useState/useEffect
