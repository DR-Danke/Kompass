# Feature: Category and Tag Management Service

## Metadata
issue_number: `4`
adw_id: `0a08fee5`
issue_json: `{"number":4,"title":"[Kompass] Phase 2C: Category and Tag Management Service","body":"..."}`

## Feature Description
Implement the service layer for managing product categories (hierarchical) and tags in the Kompass Portfolio & Quotation System. This includes CRUD operations for both entities, hierarchical tree operations for categories (building nested trees, calculating depth and paths, getting descendants), and tag operations with product count tracking.

The category service must support:
- CRUD operations with optional parent category for hierarchy
- Building nested tree structures from flat database records
- Calculating depth and path for each category node
- Getting all descendants of a category
- Moving categories to new parents (reparenting)
- Validation to prevent deletion of categories with products or children

The tag service must support:
- CRUD operations with color support (hex codes)
- Getting tags with product counts
- Search functionality for autocomplete
- Cascade deletion that removes product associations

## User Story
As a system administrator or product manager
I want to manage hierarchical product categories and flexible tags
So that I can organize products in a structured taxonomy and enable rich filtering/discovery

## Problem Statement
The Kompass system needs a robust way to organize products into hierarchical categories and flexible tags. Phase 1 (KP-001) established the database schema and repository layer for categories and tags, but the business logic layer (service) is missing. Without the service layer, the API routes (Phase 3) cannot be implemented with proper validation, tree operations, and business rules.

## Solution Statement
Implement two service classes (`CategoryService` and `TagService`) that provide business logic on top of the existing repository layer. The category service will handle hierarchical tree operations and validation, while the tag service will handle product count aggregation and search. Both services will follow the singleton pattern established by `AuthService`.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/app/services/auth_service.py` - Reference pattern for service class structure, docstrings, and singleton instantiation
- `apps/Server/app/models/kompass_dto.py` (lines 124-207) - Contains existing `CategoryCreateDTO`, `CategoryUpdateDTO`, `CategoryResponseDTO`, `CategoryListResponseDTO`, `TagCreateDTO`, `TagUpdateDTO`, `TagResponseDTO`, `TagListResponseDTO`
- `apps/Server/app/repository/kompass_repository.py` (lines 238-657) - Contains existing `CategoryRepository` and `TagRepository` with full CRUD operations
- `apps/Server/app/config/database.py` - Database connection utilities used by repositories
- `app_docs/feature-9ce5e2ee-database-schema-core-dtos.md` - Documentation for Phase 1 (database schema and DTOs)

### New Files
- `apps/Server/app/services/category_service.py` - Category service with CRUD and tree operations
- `apps/Server/app/services/tag_service.py` - Tag service with CRUD, product counts, and search
- `apps/Server/tests/services/test_category_service.py` - Unit tests for category service
- `apps/Server/tests/services/test_tag_service.py` - Unit tests for tag service

## Implementation Plan

### Phase 1: Foundation
1. Understand the existing repository patterns and DTOs from Phase 1
2. Review the database schema for categories (hierarchical with `parent_id`) and tags (flat with `product_tags` junction)
3. Identify new DTOs needed for tree operations (e.g., `CategoryTreeNode` for nested tree response)

### Phase 2: Core Implementation
1. **Category Service**
   - Implement CRUD methods wrapping repository calls with DTO conversion
   - Implement hierarchical tree building from flat records using recursive algorithm
   - Implement depth/path calculation for tree nodes
   - Implement descendant retrieval for a given category
   - Implement category reparenting with validation
   - Implement delete validation (check for children and products)

2. **Tag Service**
   - Implement CRUD methods wrapping repository calls
   - Implement product count aggregation using SQL COUNT query on `product_tags` table
   - Implement search functionality with ILIKE pattern matching
   - Implement cascade delete that handles product associations (via database FK CASCADE)

### Phase 3: Integration
1. Add new DTOs to `kompass_dto.py` for tree operations (`CategoryTreeNode`, `TagWithCountDTO`)
2. Wire up services with repository singletons
3. Export service singletons for use in API routes (Phase 3)

## Step by Step Tasks

### Step 1: Add New DTOs for Tree Operations
- Read `apps/Server/app/models/kompass_dto.py` to understand existing DTO patterns
- Add `CategoryTreeNode` DTO with fields: `id`, `name`, `description`, `parent_id`, `sort_order`, `is_active`, `depth`, `path`, `children` (recursive)
- Add `TagWithCountDTO` DTO extending `TagResponseDTO` with `product_count` field
- Ensure all DTOs have proper type hints and `model_config = {"from_attributes": True}`

### Step 2: Implement Category Service
- Create `apps/Server/app/services/category_service.py`
- Implement `CategoryService` class with docstrings following `auth_service.py` pattern
- Implement `create_category(request: CategoryCreateDTO) -> CategoryResponseDTO`:
  - Validate parent exists if `parent_id` is provided
  - Call `category_repository.create()` and convert result to DTO
- Implement `get_category(category_id: UUID) -> Optional[CategoryResponseDTO]`:
  - Call `category_repository.get_by_id()` and convert to DTO
  - Return None if not found
- Implement `list_categories() -> List[CategoryTreeNode]`:
  - Fetch all categories from repository (use large limit)
  - Build nested tree structure using `_build_tree()` helper
- Implement `update_category(category_id: UUID, request: CategoryUpdateDTO) -> Optional[CategoryResponseDTO]`:
  - Validate new parent exists if changing `parent_id`
  - Prevent setting parent to self or descendant (cycle detection)
  - Call `category_repository.update()` and convert to DTO
- Implement `delete_category(category_id: UUID) -> bool`:
  - Check if category has children (fail if yes)
  - Check if category has products associated (fail if yes - requires product check)
  - Call `category_repository.delete()` (soft delete via `is_active=False`)
- Implement `move_category(category_id: UUID, new_parent_id: Optional[UUID]) -> Optional[CategoryResponseDTO]`:
  - Validate no cycle would be created
  - Update `parent_id` via repository
- Implement `get_descendants(category_id: UUID) -> List[CategoryResponseDTO]`:
  - Recursive retrieval of all children at all levels
- Implement private helper `_build_tree(categories: List[Dict], parent_id: Optional[UUID] = None, depth: int = 0, path: str = "") -> List[CategoryTreeNode]`:
  - Recursive algorithm to build nested tree with depth and path calculation
- Create singleton: `category_service = CategoryService()`

### Step 3: Implement Tag Service
- Create `apps/Server/app/services/tag_service.py`
- Implement `TagService` class with docstrings
- Implement `create_tag(request: TagCreateDTO) -> TagResponseDTO`:
  - Call `tag_repository.create()` and convert to DTO
- Implement `get_tag(tag_id: UUID) -> Optional[TagWithCountDTO]`:
  - Call `tag_repository.get_by_id()`
  - Query `product_tags` table for count
  - Return `TagWithCountDTO` with product count
- Implement `list_tags() -> List[TagWithCountDTO]`:
  - Fetch all tags from repository
  - Aggregate product counts using SQL GROUP BY on `product_tags`
  - Return list with counts
- Implement `update_tag(tag_id: UUID, request: TagUpdateDTO) -> Optional[TagResponseDTO]`:
  - Call `tag_repository.update()` and convert to DTO
- Implement `delete_tag(tag_id: UUID) -> bool`:
  - Call `tag_repository.delete()` (hard delete, FK CASCADE handles associations)
- Implement `search_tags(query: str) -> List[TagResponseDTO]`:
  - Use SQL ILIKE for case-insensitive search on `name` field
  - Limit results (e.g., 20) for autocomplete performance
- Implement private helper `_get_product_count(tag_id: UUID) -> int`:
  - SQL COUNT on `product_tags WHERE tag_id = %s`
- Implement private helper `_get_all_product_counts() -> Dict[UUID, int]`:
  - Single SQL query with GROUP BY for efficiency
- Create singleton: `tag_service = TagService()`

### Step 4: Add Repository Methods for Service Needs
- Read `apps/Server/app/repository/kompass_repository.py` to check if additional methods are needed
- Add `CategoryRepository.get_children(category_id: UUID) -> List[Dict]` if not exists
- Add `CategoryRepository.has_products(category_id: UUID) -> bool` method to check if category has associated products
- Add `TagRepository.search(query: str, limit: int = 20) -> List[Dict]` method for ILIKE search
- Add `TagRepository.get_product_count(tag_id: UUID) -> int` method
- Add `TagRepository.get_all_with_counts() -> List[Dict]` method for efficient bulk count retrieval

### Step 5: Write Unit Tests for Category Service
- Create `apps/Server/tests/services/__init__.py` if not exists
- Create `apps/Server/tests/services/test_category_service.py`
- Test `create_category` with and without parent
- Test `create_category` with invalid parent (should fail)
- Test `get_category` for existing and non-existing category
- Test `list_categories` returns proper tree structure
- Test `update_category` with valid data
- Test `update_category` preventing cycle (parent cannot be descendant)
- Test `delete_category` fails when has children
- Test `delete_category` succeeds for leaf category
- Test `move_category` reparenting works correctly
- Test `get_descendants` returns all levels of children
- Use pytest fixtures and mocking for database isolation

### Step 6: Write Unit Tests for Tag Service
- Create `apps/Server/tests/services/test_tag_service.py`
- Test `create_tag` with valid color
- Test `get_tag` returns product count
- Test `list_tags` returns all tags with counts
- Test `update_tag` with new name and color
- Test `delete_tag` cascade removes associations
- Test `search_tags` returns matching results with ILIKE
- Test `search_tags` with empty query returns empty list
- Use pytest fixtures and mocking for database isolation

### Step 7: Run Validation Commands
- Execute all validation commands to ensure zero regressions
- Fix any linting errors or test failures
- Verify imports work correctly

## Testing Strategy

### Unit Tests
- **Category Service Tests**:
  - CRUD operations (create, read, update, delete)
  - Tree building with multiple levels of hierarchy
  - Cycle prevention in update/move operations
  - Delete validation (children check, products check)
  - Descendant retrieval at multiple levels

- **Tag Service Tests**:
  - CRUD operations (create, read, update, delete)
  - Product count aggregation
  - Search functionality with various query patterns
  - Cascade delete behavior

### Edge Cases
- Category with no parent (root level)
- Category with deeply nested children (3+ levels)
- Moving category to root level (parent_id = None)
- Attempting to move category to its own descendant (cycle)
- Tag with zero products
- Tag search with special characters
- Tag search with empty string
- Deleting tag that has many product associations
- Creating category with non-existent parent_id
- Updating category to have self as parent

## Acceptance Criteria
- [ ] Category CRUD working - create, read, update, soft-delete operations functional
- [ ] Hierarchical tree building correctly - `list_categories()` returns properly nested tree with depth/path
- [ ] Tag CRUD working - create, read, update, hard-delete operations functional
- [ ] Product counts accurate - `get_tag()` and `list_tags()` return correct product association counts
- [ ] Delete validations working - categories with children or products cannot be deleted
- [ ] Unit tests passing - all tests in `test_category_service.py` and `test_tag_service.py` pass
- [ ] No linting errors - ruff check passes with zero errors
- [ ] Services follow singleton pattern - `category_service` and `tag_service` exported as singletons

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Verify DTO imports work
cd apps/Server && source .venv/bin/activate && python -c "from app.models.kompass_dto import CategoryTreeNode, TagWithCountDTO; print('New DTOs imported successfully')"

# Verify service imports work
cd apps/Server && source .venv/bin/activate && python -c "from app.services.category_service import category_service; from app.services.tag_service import tag_service; print('Services imported successfully')"

# Run linting
cd apps/Server && .venv/bin/ruff check .

# Run all Server tests
cd apps/Server && .venv/bin/pytest tests/ -v --tb=short

# Run specific service tests
cd apps/Server && .venv/bin/pytest tests/services/test_category_service.py tests/services/test_tag_service.py -v --tb=short

# Run type checking (if mypy configured)
cd apps/Server && .venv/bin/python -m py_compile app/services/category_service.py app/services/tag_service.py
```

## Notes

### Parallel Execution Context
This is Phase 2C (Issue 4 of 33) running in parallel with:
- KP-002: Supplier and Niche Management Service
- KP-003: Product Management Service
- KP-005: Client and Quotation Management Service

All Phase 2 services are being developed in separate worktrees. This service can be developed independently since it only depends on Phase 1 (database schema and DTOs) which is already complete.

### Tree Building Algorithm
The `_build_tree()` method should use a dictionary-based approach for O(n) performance:
```python
def _build_tree(self, categories: List[Dict], parent_id: Optional[UUID] = None, depth: int = 0, path: str = "") -> List[CategoryTreeNode]:
    result = []
    for cat in categories:
        if cat.get("parent_id") == parent_id:
            node_path = f"{path}/{cat['name']}" if path else cat['name']
            children = self._build_tree(categories, cat['id'], depth + 1, node_path)
            result.append(CategoryTreeNode(
                id=cat['id'],
                name=cat['name'],
                description=cat.get('description'),
                parent_id=cat.get('parent_id'),
                sort_order=cat.get('sort_order', 0),
                is_active=cat.get('is_active', True),
                depth=depth,
                path=node_path,
                children=children
            ))
    return sorted(result, key=lambda x: (x.sort_order, x.name))
```

### Product Count Query
For efficient product counting across all tags:
```sql
SELECT tag_id, COUNT(*) as product_count
FROM product_tags
GROUP BY tag_id
```

### Delete Validation for Categories
Before deleting a category, check:
1. `SELECT COUNT(*) FROM categories WHERE parent_id = %s` (children check)
2. `SELECT COUNT(*) FROM products WHERE category_id = %s` (products check)

If either returns > 0, raise HTTPException with appropriate message.

### No New Dependencies Required
This feature uses only existing dependencies (Pydantic, psycopg2) from the project.
