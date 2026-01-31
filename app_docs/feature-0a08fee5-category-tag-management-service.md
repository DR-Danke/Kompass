# Category and Tag Management Service

**ADW ID:** 0a08fee5
**Date:** 2026-01-31
**Specification:** specs/issue-4-adw-0a08fee5-sdlc_planner-category-tag-management-service.md

## Overview

Implements the service layer for managing hierarchical product categories and flexible tags in the Kompass Portfolio & Quotation System. This includes CRUD operations for both entities, hierarchical tree operations for categories (building nested trees, calculating depth and paths, getting descendants), and tag operations with product count tracking.

## What Was Built

- **CategoryService**: Full CRUD with hierarchical tree building, cycle prevention, and delete validation
- **TagService**: CRUD with product count aggregation and search functionality
- **New DTOs**: `CategoryTreeNode` for nested tree representation, `TagWithCountDTO` for tags with product counts
- **Repository Extensions**: New methods for children retrieval, product checking, parent setting, search, and count aggregation
- **Comprehensive Unit Tests**: Full test coverage for both services with mocked repositories

## Technical Implementation

### Files Modified

- `apps/Server/app/models/kompass_dto.py`: Added `CategoryTreeNode` and `TagWithCountDTO` DTOs
- `apps/Server/app/repository/kompass_repository.py`: Added `get_children`, `has_products`, `has_children`, `set_parent` for categories; `search`, `get_product_count`, `get_all_with_counts` for tags

### Files Created

- `apps/Server/app/services/category_service.py`: CategoryService class with 246 lines
- `apps/Server/app/services/tag_service.py`: TagService class with 137 lines
- `apps/Server/tests/services/__init__.py`: Package initialization
- `apps/Server/tests/services/test_category_service.py`: 414 lines of unit tests
- `apps/Server/tests/services/test_tag_service.py`: 346 lines of unit tests

### Key Changes

- **Hierarchical Tree Building**: Recursive `_build_tree()` method converts flat category records into nested `CategoryTreeNode` structures with depth and path calculation
- **Cycle Prevention**: `_is_descendant()` method prevents moving a category to one of its own descendants
- **Delete Validation**: Categories cannot be deleted if they have children or associated products
- **Product Count Aggregation**: Tags include product counts via LEFT JOIN with `product_tags` table
- **Search Functionality**: Case-insensitive ILIKE search for tag autocomplete

## How to Use

### Category Service

```python
from app.services.category_service import category_service

# Create category
category = category_service.create_category(CategoryCreateDTO(
    name="Electronics",
    description="Electronic products",
    parent_id=None,  # Root category
    sort_order=1,
    is_active=True
))

# Get category tree
tree = category_service.list_categories()  # Returns List[CategoryTreeNode]

# Update category
updated = category_service.update_category(category_id, CategoryUpdateDTO(
    name="Consumer Electronics"
))

# Move category to new parent
moved = category_service.move_category(category_id, new_parent_id)

# Get all descendants
descendants = category_service.get_descendants(category_id)

# Delete category (fails if has children or products)
success = category_service.delete_category(category_id)
```

### Tag Service

```python
from app.services.tag_service import tag_service

# Create tag
tag = tag_service.create_tag(TagCreateDTO(
    name="Featured",
    color="#FF5733"
))

# Get tag with product count
tag_with_count = tag_service.get_tag(tag_id)  # Returns TagWithCountDTO

# List all tags with counts
all_tags = tag_service.list_tags()  # Returns List[TagWithCountDTO]

# Search tags for autocomplete
matches = tag_service.search_tags("feat", limit=20)

# Update tag
updated = tag_service.update_tag(tag_id, TagUpdateDTO(
    name="Featured Products",
    color="#FF0000"
))

# Delete tag (hard delete, FK cascade removes associations)
success = tag_service.delete_tag(tag_id)
```

## Configuration

No new environment variables or configuration required. Services use existing database connection utilities from `app.config.database`.

## Testing

Run service tests:

```bash
cd apps/Server && .venv/bin/pytest tests/services/test_category_service.py tests/services/test_tag_service.py -v --tb=short
```

Verify imports:

```bash
cd apps/Server && source .venv/bin/activate && python -c "from app.services.category_service import category_service; from app.services.tag_service import tag_service; print('Services imported successfully')"
```

## Notes

- **Singleton Pattern**: Both services export singleton instances (`category_service`, `tag_service`) for use in API routes
- **Soft Delete for Categories**: Categories use `is_active=False` for soft deletion
- **Hard Delete for Tags**: Tags are permanently deleted with FK cascade handling product associations
- **Tree Performance**: The `_build_tree()` method uses O(n) algorithm with dictionary-based lookup
- **Part of Phase 2C**: This service layer builds on Phase 1 (database schema and DTOs) and will be consumed by Phase 3 (API routes)
