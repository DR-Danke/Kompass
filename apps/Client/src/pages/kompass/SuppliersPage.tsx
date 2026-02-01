import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Paper,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  InputAdornment,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import SearchIcon from '@mui/icons-material/Search';
import type { SupplierResponse, SupplierStatus } from '@/types/kompass';
import { supplierService } from '@/services/kompassService';
import SupplierForm from '@/components/kompass/SupplierForm';

type StatusFilter = SupplierStatus | 'all';

const statusOptions: { value: StatusFilter; label: string }[] = [
  { value: 'all', label: 'All Statuses' },
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'pending_review', label: 'Pending Review' },
];

const getStatusChipColor = (status: SupplierStatus): 'success' | 'default' | 'warning' => {
  switch (status) {
    case 'active':
      return 'success';
    case 'inactive':
      return 'default';
    case 'pending_review':
      return 'warning';
    default:
      return 'default';
  }
};

const getStatusLabel = (status: SupplierStatus): string => {
  switch (status) {
    case 'active':
      return 'Active';
    case 'inactive':
      return 'Inactive';
    case 'pending_review':
      return 'Pending Review';
    default:
      return status;
  }
};

const SuppliersPage: React.FC = () => {
  // Data state
  const [suppliers, setSuppliers] = useState<SupplierResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Pagination state
  const [page, setPage] = useState(0);
  const [limit, setLimit] = useState(10);
  const [total, setTotal] = useState(0);

  // Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');

  // Dialog state
  const [formOpen, setFormOpen] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState<SupplierResponse | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [supplierToDelete, setSupplierToDelete] = useState<SupplierResponse | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setPage(0); // Reset to first page when search changes
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Fetch suppliers
  const fetchSuppliers = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      console.log('INFO [SuppliersPage]: Fetching suppliers');
      const filters: { status?: string; search?: string } = {};
      if (statusFilter !== 'all') {
        filters.status = statusFilter;
      }
      if (debouncedSearch) {
        filters.search = debouncedSearch;
      }

      const response = await supplierService.list(page + 1, limit, filters);
      setSuppliers(response.items);
      setTotal(response.pagination.total);
      console.log(`INFO [SuppliersPage]: Fetched ${response.items.length} suppliers`);
    } catch (err) {
      console.log('ERROR [SuppliersPage]: Failed to fetch suppliers', err);
      setError(err instanceof Error ? err.message : 'Failed to load suppliers');
    } finally {
      setLoading(false);
    }
  }, [page, limit, statusFilter, debouncedSearch]);

  useEffect(() => {
    fetchSuppliers();
  }, [fetchSuppliers]);

  // Handle pagination
  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setLimit(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Handle status filter change
  const handleStatusFilterChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setStatusFilter(event.target.value as StatusFilter);
    setPage(0);
  };

  // Handle add/edit
  const handleAddClick = () => {
    setSelectedSupplier(null);
    setFormOpen(true);
  };

  const handleEditClick = (supplier: SupplierResponse) => {
    setSelectedSupplier(supplier);
    setFormOpen(true);
  };

  const handleFormClose = () => {
    setFormOpen(false);
    setSelectedSupplier(null);
  };

  const handleFormSuccess = () => {
    fetchSuppliers();
  };

  // Handle delete
  const handleDeleteClick = (supplier: SupplierResponse) => {
    setSupplierToDelete(supplier);
    setDeleteDialogOpen(true);
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setSupplierToDelete(null);
  };

  const handleDeleteConfirm = async () => {
    if (!supplierToDelete) return;

    setDeleteLoading(true);
    try {
      console.log(`INFO [SuppliersPage]: Deleting supplier ${supplierToDelete.id}`);
      await supplierService.delete(supplierToDelete.id);
      setDeleteDialogOpen(false);
      setSupplierToDelete(null);
      fetchSuppliers();
    } catch (err) {
      console.log('ERROR [SuppliersPage]: Failed to delete supplier', err);
      setError(err instanceof Error ? err.message : 'Failed to delete supplier');
    } finally {
      setDeleteLoading(false);
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Suppliers</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddClick}
        >
          Add Supplier
        </Button>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Box display="flex" gap={2} mb={2}>
        <TextField
          placeholder="Search suppliers..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          size="small"
          sx={{ width: 300 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
        <TextField
          select
          label="Status"
          value={statusFilter}
          onChange={handleStatusFilterChange}
          size="small"
          sx={{ width: 180 }}
        >
          {statusOptions.map((option) => (
            <MenuItem key={option.value} value={option.value}>
              {option.label}
            </MenuItem>
          ))}
        </TextField>
      </Box>

      {/* Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Country</TableCell>
              <TableCell>Contact Email</TableCell>
              <TableCell>Contact Phone</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : suppliers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                  <Typography color="text.secondary">
                    {debouncedSearch || statusFilter !== 'all'
                      ? 'No suppliers match your filters'
                      : 'No suppliers found. Click "Add Supplier" to create one.'}
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              suppliers.map((supplier) => (
                <TableRow key={supplier.id} hover>
                  <TableCell>
                    <Typography
                      sx={{
                        maxWidth: 250,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {supplier.name}
                    </Typography>
                  </TableCell>
                  <TableCell>{supplier.country}</TableCell>
                  <TableCell>{supplier.contact_email || '-'}</TableCell>
                  <TableCell>{supplier.contact_phone || '-'}</TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusLabel(supplier.status)}
                      color={getStatusChipColor(supplier.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => handleEditClick(supplier)}
                      aria-label="edit"
                    >
                      <EditIcon fontSize="small" />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteClick(supplier)}
                      aria-label="delete"
                      color="error"
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={total}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={limit}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={[5, 10, 25, 50]}
        />
      </TableContainer>

      {/* Supplier Form Dialog */}
      <SupplierForm
        open={formOpen}
        onClose={handleFormClose}
        onSuccess={handleFormSuccess}
        supplier={selectedSupplier}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleDeleteCancel}>
        <DialogTitle>Delete Supplier</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the supplier "{supplierToDelete?.name}"? This action
            cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} disabled={deleteLoading}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
            disabled={deleteLoading}
          >
            {deleteLoading ? <CircularProgress size={20} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SuppliersPage;
