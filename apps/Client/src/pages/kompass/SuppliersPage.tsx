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
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import SearchIcon from '@mui/icons-material/Search';
import ViewListIcon from '@mui/icons-material/ViewList';
import ViewKanbanIcon from '@mui/icons-material/ViewKanban';
import type { SupplierResponse, SupplierStatus, SupplierPipelineStatus, SupplierWithProductCount } from '@/types/kompass';
import { supplierService } from '@/services/kompassService';
import SupplierForm from '@/components/kompass/SupplierForm';
import PipelineStatusBadge from '@/components/kompass/PipelineStatusBadge';
import SupplierPipelineKanban from '@/components/kompass/SupplierPipelineKanban';
import { useSupplierPipeline, ViewMode } from '@/hooks/kompass/useSupplierPipeline';

type StatusFilter = SupplierStatus | 'all';
type PipelineFilter = SupplierPipelineStatus | 'all';

const statusOptions: { value: StatusFilter; label: string }[] = [
  { value: 'all', label: 'All Statuses' },
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'pending_review', label: 'Pending Review' },
];

const pipelineOptions: { value: PipelineFilter; label: string }[] = [
  { value: 'all', label: 'All Pipeline' },
  { value: 'contacted', label: 'Contacted' },
  { value: 'potential', label: 'Potential' },
  { value: 'quoted', label: 'Quoted' },
  { value: 'certified', label: 'Certified' },
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
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
  // View mode state
  const [viewMode, setViewMode] = useState<ViewMode>('list');

  // Kanban hook
  const {
    pipeline,
    isLoading: kanbanLoading,
    isUpdating,
    error: kanbanError,
    fetchPipeline,
    updatePipelineStatus,
    getFilteredPipeline,
    setSearchQuery: setKanbanSearchQuery,
    clearError: clearKanbanError,
  } = useSupplierPipeline();

  // List view state
  const [suppliers, setSuppliers] = useState<SupplierResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Pagination state
  const [page, setPage] = useState(0);
  const [limit, setLimit] = useState(10);
  const [total, setTotal] = useState(0);

  // Filter state for list view
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [pipelineFilter, setPipelineFilter] = useState<PipelineFilter>('all');

  // Dialog state
  const [formOpen, setFormOpen] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState<SupplierResponse | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [supplierToDelete, setSupplierToDelete] = useState<SupplierResponse | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  // Debounce search query for list view
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setPage(0);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Debounce search query for kanban view
  useEffect(() => {
    const timer = setTimeout(() => {
      setKanbanSearchQuery(searchQuery);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery, setKanbanSearchQuery]);

  // Fetch suppliers for list view
  const fetchSuppliers = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      console.log('INFO [SuppliersPage]: Fetching suppliers');
      const filters: { status?: string; search?: string; pipeline_status?: string } = {};
      if (statusFilter !== 'all') {
        filters.status = statusFilter;
      }
      if (pipelineFilter !== 'all') {
        filters.pipeline_status = pipelineFilter;
      }
      if (debouncedSearch) {
        filters.search = debouncedSearch;
      }

      const response = await supplierService.list(page + 1, limit, filters);
      const items = response.items || [];
      setSuppliers(items);
      setTotal(response.pagination?.total || 0);
      console.log(`INFO [SuppliersPage]: Fetched ${items.length} suppliers`);
    } catch (err) {
      console.log('ERROR [SuppliersPage]: Failed to fetch suppliers', err);
      setError(err instanceof Error ? err.message : 'Failed to load suppliers');
    } finally {
      setLoading(false);
    }
  }, [page, limit, statusFilter, pipelineFilter, debouncedSearch]);

  useEffect(() => {
    if (viewMode === 'list') {
      fetchSuppliers();
    }
  }, [fetchSuppliers, viewMode]);

  // Fetch pipeline when switching to kanban view
  useEffect(() => {
    if (viewMode === 'kanban' && !pipeline) {
      fetchPipeline();
    }
  }, [viewMode, pipeline, fetchPipeline]);

  // Handle view mode toggle
  const handleViewModeChange = (_event: React.MouseEvent<HTMLElement>, newMode: ViewMode | null) => {
    if (newMode) {
      setViewMode(newMode);
    }
  };

  // Handle pagination
  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setLimit(parseInt(event.target.value, 10));
    setPage(0);
  };

  // Handle filter changes
  const handleStatusFilterChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setStatusFilter(event.target.value as StatusFilter);
    setPage(0);
  };

  const handlePipelineFilterChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPipelineFilter(event.target.value as PipelineFilter);
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

  const handleSupplierClick = (supplier: SupplierWithProductCount) => {
    // Convert SupplierWithProductCount to SupplierResponse for editing
    const supplierResponse: SupplierResponse = {
      ...supplier,
    };
    setSelectedSupplier(supplierResponse);
    setFormOpen(true);
  };

  const handleFormClose = () => {
    setFormOpen(false);
    setSelectedSupplier(null);
  };

  const handleFormSuccess = () => {
    if (viewMode === 'list') {
      fetchSuppliers();
    } else {
      fetchPipeline();
    }
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
      if (viewMode === 'list') {
        fetchSuppliers();
      } else {
        fetchPipeline();
      }
    } catch (err) {
      console.log('ERROR [SuppliersPage]: Failed to delete supplier', err);
      setError(err instanceof Error ? err.message : 'Failed to delete supplier');
    } finally {
      setDeleteLoading(false);
    }
  };

  // Handle status change from Kanban drag-and-drop
  const handleStatusChange = async (supplierId: string, newStatus: SupplierPipelineStatus) => {
    await updatePipelineStatus(supplierId, newStatus);
  };

  const currentError = viewMode === 'kanban' ? kanbanError : error;
  const clearError = () => {
    if (viewMode === 'kanban') {
      clearKanbanError();
    } else {
      setError(null);
    }
  };

  const filteredPipeline = getFilteredPipeline();

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Suppliers</Typography>
        <Box display="flex" gap={2} alignItems="center">
          <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={handleViewModeChange}
            size="small"
          >
            <ToggleButton value="list" aria-label="list view">
              <ViewListIcon />
            </ToggleButton>
            <ToggleButton value="kanban" aria-label="kanban view">
              <ViewKanbanIcon />
            </ToggleButton>
          </ToggleButtonGroup>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAddClick}
          >
            Add Supplier
          </Button>
        </Box>
      </Box>

      {/* Error Alert */}
      {currentError && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={clearError}>
          {currentError}
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
        {viewMode === 'list' && (
          <>
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
            <TextField
              select
              label="Pipeline"
              value={pipelineFilter}
              onChange={handlePipelineFilterChange}
              size="small"
              sx={{ width: 180 }}
            >
              {pipelineOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </>
        )}
      </Box>

      {/* Kanban View */}
      {viewMode === 'kanban' && (
        kanbanLoading ? (
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        ) : filteredPipeline ? (
          <SupplierPipelineKanban
            pipeline={filteredPipeline}
            onSupplierClick={handleSupplierClick}
            onStatusChange={handleStatusChange}
            isUpdating={isUpdating}
          />
        ) : null
      )}

      {/* List View */}
      {viewMode === 'list' && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Country</TableCell>
                <TableCell>Contact Email</TableCell>
                <TableCell>Contact Phone</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Pipeline</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : suppliers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">
                      {debouncedSearch || statusFilter !== 'all' || pipelineFilter !== 'all'
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
                    <TableCell>
                      <PipelineStatusBadge status={supplier.pipeline_status} />
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
      )}

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
