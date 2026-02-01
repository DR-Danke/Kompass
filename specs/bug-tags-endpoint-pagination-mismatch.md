# Bug: Tags Endpoint Returns Array Instead of Paginated Response

## Metadata
issue_number: ``
adw_id: ``
issue_json: ``

## Bug Description
When navigating to http://localhost:5176/products, the page displays a loading spinner on the tags filter field and then crashes with a TypeError: "Cannot read properties of undefined (reading 'length')". The error occurs in the MUI Autocomplete component in the ProductFilters component. The API successfully returns a 200 response from `/tags`, but the frontend crashes when trying to render the tags filter.

## Problem Statement
The backend `/tags` endpoint returns a direct array `List[TagWithCountDTO]` but the frontend `tagService.list()` expects a paginated response object with `{ items: TagResponse[], pagination: Pagination }` structure. When the response doesn't match the expected format, `response.data.items` is `undefined`, causing the MUI Autocomplete to crash when it tries to read the `length` property of `undefined`.

## Solution Statement
Update the backend `/tags` endpoint to return a paginated response that matches the expected frontend format, consistent with other list endpoints like suppliers, products, portfolios, etc. This will require modifying the tag routes to accept pagination parameters and return a standardized paginated response.

## Steps to Reproduce
1. Start the backend server on port 8000
2. Start the frontend server on port 5176
3. Navigate to http://localhost:5176/products
4. Observe the tags filter field shows a loading spinner
5. After API call completes, observe the page crashes with "Cannot read properties of undefined (reading 'length')" error in browser console
6. Check network tab - `/tags` returns 200 with a direct array, not a paginated object

## Root Cause Analysis
The root cause is a mismatch between backend API response format and frontend expectations:

**Backend (apps/Server/app/api/tag_routes.py:21-31):**
```python
@router.get("/", response_model=List[TagWithCountDTO])
async def list_tags(
    current_user: dict = Depends(get_current_user),
) -> List[TagWithCountDTO]:
    return tag_service.list_tags()
```
Returns: `[{id: "...", name: "...", color: "...", product_count: 0}, ...]`

**Frontend (apps/Client/src/services/kompassService.ts:327-334):**
```typescript
async list(page = 1, limit = 20): Promise<TagListResponse> {
    const response = await apiClient.get<TagListResponse>('/tags', {
      params: { page, limit },
    });
    return response.data;
  }
```
Expects: `{ items: [...], pagination: {...} }`

**Frontend (apps/Client/src/components/kompass/ProductFilters.tsx:99-100):**
```typescript
const response = await tagService.list(1, 100);
setTags(response.items);
```
Tries to access `response.items`, which is `undefined` because the API returns an array directly.

The MUI Autocomplete receives `undefined` for its `options` prop (line 281), and when it tries to check the length property, it crashes.

## Relevant Files
Use these files to fix the bug:

- `apps/Server/app/api/tag_routes.py` - Backend tag routes that need to be updated to return paginated responses
- `apps/Server/app/services/tag_service.py` - Tag service that needs pagination support
- `apps/Server/app/models/kompass_dto.py` - Check if PaginatedResponse DTO exists for tags
- `apps/Client/src/components/kompass/ProductFilters.tsx` - Frontend component that calls tagService.list() and expects paginated response
- `apps/Client/src/hooks/useTags.ts` - Hook that also calls tagService.list() and expects paginated response
- `apps/Client/src/services/kompassService.ts` - Frontend service with tagService.list() implementation
- `apps/Client/src/types/kompass.ts` - Type definitions including TagListResponse

### Reference Files
- `apps/Server/app/api/supplier_routes.py` - Reference for correct paginated endpoint pattern
- `apps/Server/app/api/product_routes.py` - Reference for correct paginated endpoint pattern

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Review existing paginated endpoints for pattern reference
- Read `apps/Server/app/api/supplier_routes.py` to understand the pagination pattern
- Read `apps/Server/app/api/product_routes.py` to understand the pagination pattern
- Note how they accept `page` and `limit` query parameters and return paginated responses

### 2. Update backend tag service to support pagination
- Read `apps/Server/app/services/tag_service.py`
- Modify `list_tags()` method to accept `page` and `limit` parameters
- Update the SQL query to use LIMIT and OFFSET for pagination
- Calculate total count of tags
- Return a dictionary/object with `items` array and `pagination` metadata

### 3. Update backend tag routes to accept pagination parameters
- Update `apps/Server/app/api/tag_routes.py` GET "/" endpoint
- Add `page` and `limit` query parameters with proper defaults and validation
- Change response model from `List[TagWithCountDTO]` to a paginated response model
- Check `apps/Server/app/models/kompass_dto.py` for existing PaginatedResponse model or create if needed
- Update the endpoint to call updated `tag_service.list_tags(page, limit)`

### 4. Run validation commands
- Execute all validation commands below to ensure the bug is fixed with zero regressions

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

### Manual testing to reproduce and verify fix:
1. Start backend: `cd apps/Server && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`
2. Start frontend: `cd apps/Client && npm run dev`
3. Navigate to http://localhost:5176/products
4. Verify tags filter loads without errors
5. Verify tags filter shows available tags in dropdown
6. Verify selecting tags filters products correctly
7. Check browser console for no errors
8. Check network tab that `/tags?page=1&limit=100` returns `{items: [...], pagination: {...}}`

### Automated validation:
- `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` - Run Server tests to validate the bug is fixed with zero regressions
- `cd apps/Client && npm run tsc --noEmit` - Run Client type check to validate the bug is fixed with zero regressions
- `cd apps/Client && npm run build` - Run Client build to validate the bug is fixed with zero regressions

## Notes
- This is a backend API contract breaking change, but since the frontend already expects pagination, it aligns the backend with existing frontend expectations
- The fix follows the established pattern used by other list endpoints in the codebase (suppliers, products, portfolios, clients, etc.)
- The pagination parameters sent by the frontend (`page=1&limit=100`) are currently being ignored by the backend
- After this fix, tags filtering will work consistently with other filter components in the application
