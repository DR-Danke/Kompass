# E2E Test: Categories and Tags Management Page

## Test Name
Categories and Tags Management

## User Story
As a product manager or admin, I want to manage product categories in a visual tree structure and organize tags with colors so that I can effectively categorize and tag products for easy discovery and portfolio creation.

## Prerequisites
- Application running at configured URL
- User authenticated with admin or manager role
- Backend API available at /api

## Test Steps

### Step 1: Navigate to Categories Page
1. Open the application
2. Login with admin credentials if required
3. Click on "Categories" in the sidebar navigation
4. **Verify** the Categories & Tags page loads with two sections: Categories and Tags

### Step 2: Test Empty State
1. **Verify** if categories are empty, the message "No categories yet" is displayed
2. **Verify** if tags are empty, the message "No tags yet" is displayed
3. **Screenshot**: Capture the initial empty state or populated state

### Step 3: Create Root Category
1. Click "Add Root Category" button
2. **Verify** the category dialog opens with title "Create Root Category"
3. Enter "Electronics" in the Category Name field
4. Enter "Electronic products and devices" in the Description field
5. **Verify** the Active toggle is enabled by default
6. Click "Create" button
7. **Verify** success snackbar appears with "Category created successfully"
8. **Verify** "Electronics" category appears in the tree
9. **Screenshot**: Capture after creating root category

### Step 4: Create Child Category
1. Hover over the "Electronics" category row
2. Click the "Add child category" (+ icon) button
3. **Verify** the dialog opens with title 'Add Child to "Electronics"'
4. Enter "Smartphones" in the Category Name field
5. Click "Create" button
6. **Verify** success snackbar appears
7. Click the expand icon on "Electronics" to show children
8. **Verify** "Smartphones" appears as a child of "Electronics"
9. **Screenshot**: Capture the expanded tree with child category

### Step 5: Edit Category
1. Hover over "Smartphones" category
2. Click the "Edit category" (pencil icon) button
3. **Verify** the dialog opens with title "Edit Category"
4. **Verify** the name field is pre-filled with "Smartphones"
5. Update the name to "Mobile Phones"
6. Click "Update" button
7. **Verify** success snackbar appears with "Category updated successfully"
8. **Verify** the category name updates to "Mobile Phones"
9. **Screenshot**: Capture after editing category

### Step 6: Create Additional Categories for Drag-Drop Test
1. Click "Add Root Category" button
2. Enter "Accessories" and click "Create"
3. **Verify** "Accessories" root category appears

### Step 7: Test Drag and Drop Reparenting
1. Drag "Mobile Phones" category
2. Drop it on the "Drop here to move to root level" area
3. **Verify** success snackbar appears with "Category moved successfully"
4. **Verify** "Mobile Phones" is now at root level
5. **Screenshot**: Capture after drag-drop move

### Step 8: Create Tag with Color
1. In the Tags section, click "Add Tag" button
2. **Verify** the tag dialog opens with title "Create Tag"
3. Enter "Best Seller" in the Tag Name field
4. Select a gold/yellow color (#FFD700) using the color picker
5. Click "Create" button
6. **Verify** success snackbar appears with "Tag created successfully"
7. **Verify** "Best Seller" tag chip appears with the selected color
8. **Screenshot**: Capture after creating tag

### Step 9: Create Multiple Tags
1. Click "Add Tag" button
2. Enter "New Arrival" with blue color (#2196F3)
3. Click "Create"
4. Click "Add Tag" button
5. Enter "Sale" with red color (#F44336)
6. Click "Create"
7. **Verify** all three tags are visible as colored chips
8. **Screenshot**: Capture all tags

### Step 10: Test Tag Search
1. Type "Best" in the search field
2. **Verify** only "Best Seller" tag is visible
3. **Verify** "New Arrival" and "Sale" tags are hidden
4. Clear the search field
5. **Verify** all tags are visible again
6. **Screenshot**: Capture search filter in action

### Step 11: Edit Tag
1. Hover over "Sale" tag
2. Click the edit (pencil) icon
3. **Verify** the dialog opens with title "Edit Tag"
4. **Verify** the name field is pre-filled with "Sale"
5. Update the name to "On Sale"
6. Change the color to orange (#FF9800)
7. Click "Update" button
8. **Verify** success snackbar appears with "Tag updated successfully"
9. **Verify** the tag updates with new name and color
10. **Screenshot**: Capture after editing tag

### Step 12: Delete Tag
1. Hover over "On Sale" tag
2. Click the delete (trash) icon
3. **Verify** a confirmation dialog appears
4. Click "Delete" button
5. **Verify** success snackbar appears with "Tag deleted successfully"
6. **Verify** "On Sale" tag is removed from the list
7. **Screenshot**: Capture after deleting tag

### Step 13: Delete Category
1. Hover over "Mobile Phones" category (which should now be at root level)
2. Click the delete (trash) icon
3. **Verify** a confirmation dialog appears
4. Click "Delete" button
5. **Verify** success snackbar appears with "Category deleted successfully"
6. **Verify** "Mobile Phones" category is removed
7. **Screenshot**: Capture final state

### Step 14: Test Refresh Functionality
1. Click the refresh icon in the Categories section header
2. **Verify** the categories list refreshes without errors
3. Click the refresh icon in the Tags section header
4. **Verify** the tags list refreshes without errors

## Success Criteria

- [ ] Categories page loads with proper two-column layout
- [ ] Category tree renders hierarchically
- [ ] Categories can be expanded/collapsed
- [ ] Root categories can be created
- [ ] Child categories can be added to existing categories
- [ ] Categories can be edited
- [ ] Categories can be deleted
- [ ] Categories can be reparented via drag-and-drop
- [ ] Tags render as colored chips
- [ ] Tag search/filter works correctly
- [ ] Tags can be created with custom colors
- [ ] Tags can be edited
- [ ] Tags can be deleted
- [ ] Success/error notifications display properly
- [ ] Loading states show during operations
- [ ] Error states show with retry option on failures

## Screenshots Required
1. Initial page state
2. After creating root category
3. Expanded tree with child category
4. After editing category
5. After drag-drop reparenting
6. After creating first tag
7. All tags created
8. Search filter in action
9. After editing tag
10. After deleting tag
11. Final state after cleanup

## Output Format

```json
{
  "test_name": "Categories and Tags Management",
  "status": "passed|failed",
  "steps_completed": 14,
  "steps_failed": [],
  "screenshots": [
    "01_initial_page_state.png",
    "02_root_category_created.png",
    "03_child_category_expanded.png",
    "04_category_edited.png",
    "05_category_reparented.png",
    "06_first_tag_created.png",
    "07_all_tags_created.png",
    "08_tag_search_filter.png",
    "09_tag_edited.png",
    "10_tag_deleted.png",
    "11_final_state.png"
  ],
  "error": null
}
```
