import React, { useState, useCallback, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  InputAdornment,
  ToggleButton,
  ToggleButtonGroup,
  TablePagination,
  Grid,
  CircularProgress,
  Alert,
  IconButton,
  Toolbar,
  Paper,
  Checkbox,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Skeleton,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import GridViewIcon from '@mui/icons-material/GridView';
import TableRowsIcon from '@mui/icons-material/TableRows';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useProducts } from '@/hooks/kompass/useProducts';
import ProductFilters from '@/components/kompass/ProductFilters';
import ProductCard from '@/components/kompass/ProductCard';
import ProductTable from '@/components/kompass/ProductTable';
import ProductForm from '@/components/kompass/ProductForm';
import type { ProductResponse } from '@/types/kompass';
import type { ViewMode } from '@/hooks/kompass/useProducts';

const ProductsPage: React.FC = () => {
  const {
    products,
    pagination,
    filters,
    sortBy,
    sortOrder,
    viewMode,
    isLoading,
    error,
    selectedIds,
    setFilter,
    clearFilters,
    setPage,
    setPageSize,
    setSort,
    setViewMode,
    toggleSelection,
    selectAll,
    clearSelection,
    deleteProduct,
    bulkDelete,
    refreshProducts,
  } = useProducts(12);

  const [searchValue, setSearchValue] = useState('');
  const [searchTimeout, setSearchTimeoutState] = useState<ReturnType<typeof setTimeout> | null>(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<ProductResponse | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deletingProduct, setDeletingProduct] = useState<ProductResponse | null>(null);
  const [bulkDeleteDialogOpen, setBulkDeleteDialogOpen] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    setSearchValue(filters.search || '');
  }, []);

  const handleSearchChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const value = event.target.value;
      setSearchValue(value);

      if (searchTimeout) {
        clearTimeout(searchTimeout);
      }

      const timeout = setTimeout(() => {
        setFilter('search', value || null);
      }, 300);

      setSearchTimeoutState(timeout);
    },
    [searchTimeout, setFilter]
  );

  const handleViewModeChange = (
    _event: React.MouseEvent<HTMLElement>,
    newMode: ViewMode | null
  ) => {
    if (newMode) {
      setViewMode(newMode);
    }
  };

  const handlePageChange = (_event: unknown, newPage: number) => {
    setPage(newPage + 1);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPageSize(parseInt(event.target.value, 10));
  };

  const handleAddProduct = () => {
    setEditingProduct(null);
    setFormOpen(true);
  };

  const handleEditProduct = (product: ProductResponse) => {
    setEditingProduct(product);
    setFormOpen(true);
  };

  const handleFormClose = () => {
    setFormOpen(false);
    setEditingProduct(null);
  };

  const handleFormSave = async () => {
    await refreshProducts();
    setSnackbar({
      open: true,
      message: editingProduct ? 'Product updated successfully' : 'Product created successfully',
      severity: 'success',
    });
  };

  const handleDeleteClick = (product: ProductResponse) => {
    setDeletingProduct(product);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingProduct) return;

    setIsDeleting(true);
    try {
      await deleteProduct(deletingProduct.id);
      setSnackbar({
        open: true,
        message: 'Product deleted successfully',
        severity: 'success',
      });
    } catch (err) {
      console.error('ERROR [ProductsPage]: Failed to delete product:', err);
      setSnackbar({
        open: true,
        message: 'Failed to delete product',
        severity: 'error',
      });
    } finally {
      setIsDeleting(false);
      setDeleteDialogOpen(false);
      setDeletingProduct(null);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setDeletingProduct(null);
  };

  const handleBulkDeleteClick = () => {
    setBulkDeleteDialogOpen(true);
  };

  const handleBulkDeleteConfirm = async () => {
    setIsDeleting(true);
    try {
      await bulkDelete(selectedIds);
      setSnackbar({
        open: true,
        message: `${selectedIds.length} product(s) deleted successfully`,
        severity: 'success',
      });
    } catch (err) {
      console.error('ERROR [ProductsPage]: Failed to bulk delete products:', err);
      setSnackbar({
        open: true,
        message: 'Failed to delete products',
        severity: 'error',
      });
    } finally {
      setIsDeleting(false);
      setBulkDeleteDialogOpen(false);
    }
  };

  const handleBulkDeleteCancel = () => {
    setBulkDeleteDialogOpen(false);
  };

  const handleSelectAll = () => {
    if (selectedIds.length === products.length) {
      clearSelection();
    } else {
      selectAll();
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  const renderContent = () => {
    if (isLoading && products.length === 0) {
      return viewMode === 'grid' ? (
        <Grid container spacing={2}>
          {[...Array(8)].map((_, i) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={i}>
              <Skeleton variant="rectangular" height={300} sx={{ borderRadius: 1 }} />
            </Grid>
          ))}
        </Grid>
      ) : (
        <Box sx={{ p: 2 }}>
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} variant="rectangular" height={52} sx={{ mb: 1, borderRadius: 1 }} />
          ))}
        </Box>
      );
    }

    if (error) {
      return (
        <Alert
          severity="error"
          action={
            <Button color="inherit" size="small" onClick={refreshProducts}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      );
    }

    if (products.length === 0) {
      return (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            py: 8,
          }}
        >
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No products found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {filters.search || Object.values(filters).some((v) => v !== null)
              ? 'Try adjusting your search or filters'
              : 'Get started by adding your first product'}
          </Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleAddProduct}>
            Add Product
          </Button>
        </Box>
      );
    }

    if (viewMode === 'grid') {
      return (
        <Grid container spacing={2}>
          {products.map((product) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={product.id}>
              <ProductCard
                product={product}
                selected={selectedIds.includes(product.id)}
                onSelect={toggleSelection}
                onEdit={handleEditProduct}
                onDelete={handleDeleteClick}
              />
            </Grid>
          ))}
        </Grid>
      );
    }

    return (
      <ProductTable
        products={products}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSortChange={setSort}
        selectedIds={selectedIds}
        onSelect={toggleSelection}
        onSelectAll={handleSelectAll}
        onEdit={handleEditProduct}
        onDelete={handleDeleteClick}
      />
    );
  };

  return (
    <Box>
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 3,
        }}
      >
        <Typography variant="h4" component="h1">
          Biblia General
        </Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleAddProduct}>
          Add Product
        </Button>
      </Box>

      {/* Search and View Controls */}
      <Box
        sx={{
          display: 'flex',
          gap: 2,
          mb: 2,
          flexWrap: 'wrap',
        }}
      >
        <TextField
          placeholder="Search products..."
          value={searchValue}
          onChange={handleSearchChange}
          size="small"
          sx={{ minWidth: 300, flex: 1 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />

        <ToggleButtonGroup
          value={viewMode}
          exclusive
          onChange={handleViewModeChange}
          size="small"
        >
          <ToggleButton value="grid" aria-label="grid view">
            <GridViewIcon />
          </ToggleButton>
          <ToggleButton value="table" aria-label="table view">
            <TableRowsIcon />
          </ToggleButton>
        </ToggleButtonGroup>

        <IconButton onClick={refreshProducts} disabled={isLoading}>
          <RefreshIcon />
        </IconButton>
      </Box>

      {/* Bulk Actions Toolbar */}
      {selectedIds.length > 0 && (
        <Paper sx={{ mb: 2, p: 1 }}>
          <Toolbar variant="dense" sx={{ minHeight: 40, pl: 1, pr: 1 }}>
            <Checkbox
              indeterminate={selectedIds.length > 0 && selectedIds.length < products.length}
              checked={products.length > 0 && selectedIds.length === products.length}
              onChange={handleSelectAll}
            />
            <Typography sx={{ flex: 1 }} color="inherit" variant="subtitle1">
              {selectedIds.length} selected
            </Typography>
            <Button
              variant="outlined"
              color="error"
              size="small"
              startIcon={<DeleteIcon />}
              onClick={handleBulkDeleteClick}
            >
              Delete Selected
            </Button>
          </Toolbar>
        </Paper>
      )}

      {/* Main Content with Filters */}
      <Box sx={{ display: 'flex', gap: 2 }}>
        {/* Filters Sidebar */}
        <Box sx={{ width: 280, flexShrink: 0 }}>
          <ProductFilters
            filters={filters}
            onFilterChange={setFilter}
            onClearFilters={clearFilters}
          />
        </Box>

        {/* Products Content */}
        <Box sx={{ flex: 1, position: 'relative' }}>
          {isLoading && products.length > 0 && (
            <Box
              sx={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'rgba(255, 255, 255, 0.7)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1,
              }}
            >
              <CircularProgress />
            </Box>
          )}

          {renderContent()}

          {/* Pagination */}
          {products.length > 0 && (
            <TablePagination
              component="div"
              count={pagination.total}
              page={pagination.page - 1}
              onPageChange={handlePageChange}
              rowsPerPage={pagination.limit}
              onRowsPerPageChange={handleRowsPerPageChange}
              rowsPerPageOptions={[12, 24, 48, 96]}
              sx={{ mt: 2 }}
            />
          )}
        </Box>
      </Box>

      {/* Product Form Dialog */}
      <ProductForm
        open={formOpen}
        onClose={handleFormClose}
        product={editingProduct}
        onSave={handleFormSave}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleDeleteCancel}>
        <DialogTitle>Delete Product</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete "{deletingProduct?.name}"? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} disabled={isDeleting}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            disabled={isDeleting}
            startIcon={isDeleting ? <CircularProgress size={16} /> : undefined}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Bulk Delete Confirmation Dialog */}
      <Dialog open={bulkDeleteDialogOpen} onClose={handleBulkDeleteCancel}>
        <DialogTitle>Delete Products</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete {selectedIds.length} product(s)? This action cannot be
            undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleBulkDeleteCancel} disabled={isDeleting}>
            Cancel
          </Button>
          <Button
            onClick={handleBulkDeleteConfirm}
            color="error"
            disabled={isDeleting}
            startIcon={isDeleting ? <CircularProgress size={16} /> : undefined}
          >
            Delete All
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ProductsPage;
