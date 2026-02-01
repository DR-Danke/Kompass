import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  TextField,
  MenuItem,
  InputAdornment,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Paper,
  IconButton,
  Tooltip,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  CircularProgress,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SearchIcon from '@mui/icons-material/Search';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ClearIcon from '@mui/icons-material/Clear';
import { useQuotations } from '@/hooks/kompass/useQuotations';
import { clientService } from '@/services/kompassService';
import QuotationStatusBadge from '@/components/kompass/QuotationStatusBadge';
import type { QuotationResponse, QuotationStatus, ClientResponse } from '@/types/kompass';

const STATUS_OPTIONS: { value: QuotationStatus | ''; label: string }[] = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'sent', label: 'Sent' },
  { value: 'viewed', label: 'Viewed' },
  { value: 'negotiating', label: 'Negotiating' },
  { value: 'accepted', label: 'Accepted' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'expired', label: 'Expired' },
];

const QuotationsListPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    quotations,
    pagination,
    filters,
    isLoading,
    error,
    setFilter,
    clearFilters,
    setPage,
    setPageSize,
    deleteQuotation,
    cloneQuotation,
  } = useQuotations();

  // Local state
  const [clients, setClients] = useState<ClientResponse[]>([]);
  const [searchInput, setSearchInput] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [quotationToDelete, setQuotationToDelete] = useState<QuotationResponse | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isCloning, setIsCloning] = useState(false);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  }>({
    open: false,
    message: '',
    severity: 'success',
  });

  // Fetch clients for filter dropdown
  useEffect(() => {
    const fetchClients = async () => {
      try {
        const response = await clientService.list(1, 100);
        setClients(response.items);
      } catch (err) {
        console.error('ERROR [QuotationsListPage]: Failed to fetch clients:', err);
      }
    };
    fetchClients();
  }, []);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      setFilter('search', searchInput || null);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchInput, setFilter]);

  const handleNewQuotation = () => {
    navigate('/quotations/new');
  };

  const handleViewQuotation = (id: string) => {
    navigate(`/quotations/${id}`);
  };

  const handleEditQuotation = (id: string) => {
    navigate(`/quotations/${id}`);
  };

  const handleDeleteClick = (quotation: QuotationResponse) => {
    setQuotationToDelete(quotation);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!quotationToDelete) return;

    setIsDeleting(true);
    try {
      await deleteQuotation(quotationToDelete.id);
      setDeleteDialogOpen(false);
      setQuotationToDelete(null);
      setSnackbar({
        open: true,
        message: 'Quotation deleted successfully',
        severity: 'success',
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: err instanceof Error ? err.message : 'Failed to delete quotation',
        severity: 'error',
      });
    } finally {
      setIsDeleting(false);
    }
  };

  const handleClone = async (id: string) => {
    setIsCloning(true);
    try {
      const cloned = await cloneQuotation(id);
      setSnackbar({
        open: true,
        message: `Quotation cloned: ${cloned.quotation_number}`,
        severity: 'success',
      });
      navigate(`/quotations/${cloned.id}`);
    } catch (err) {
      setSnackbar({
        open: true,
        message: err instanceof Error ? err.message : 'Failed to clone quotation',
        severity: 'error',
      });
    } finally {
      setIsCloning(false);
    }
  };

  const handlePageChange = (_event: unknown, newPage: number) => {
    setPage(newPage + 1);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPageSize(parseInt(event.target.value, 10));
  };

  const handleClearFilters = () => {
    setSearchInput('');
    clearFilters();
  };

  const formatCurrency = (value: number | string, currency = 'COP'): string => {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    if (currency === 'COP') {
      return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(num);
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(num);
  };

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString();
  };

  const hasActiveFilters = useCallback(() => {
    return !!(filters.status || filters.client_id || filters.date_from || filters.date_to || filters.search);
  }, [filters]);

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Quotations</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleNewQuotation}>
          New Quotation
        </Button>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
        <Box display="flex" gap={2} alignItems="center" flexWrap="wrap">
          {/* Search */}
          <TextField
            placeholder="Search by quote # or client..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            size="small"
            sx={{ width: 250 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />

          {/* Status Filter */}
          <TextField
            select
            label="Status"
            value={filters.status || ''}
            onChange={(e) => setFilter('status', (e.target.value as QuotationStatus) || null)}
            size="small"
            sx={{ width: 150 }}
          >
            {STATUS_OPTIONS.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </TextField>

          {/* Client Filter */}
          <TextField
            select
            label="Client"
            value={filters.client_id || ''}
            onChange={(e) => setFilter('client_id', e.target.value || null)}
            size="small"
            sx={{ width: 200 }}
          >
            <MenuItem value="">All Clients</MenuItem>
            {clients.map((client) => (
              <MenuItem key={client.id} value={client.id}>
                {client.company_name}
              </MenuItem>
            ))}
          </TextField>

          {/* Date Range */}
          <TextField
            type="date"
            label="From Date"
            value={filters.date_from || ''}
            onChange={(e) => setFilter('date_from', e.target.value || null)}
            size="small"
            InputLabelProps={{ shrink: true }}
            sx={{ width: 150 }}
          />
          <TextField
            type="date"
            label="To Date"
            value={filters.date_to || ''}
            onChange={(e) => setFilter('date_to', e.target.value || null)}
            size="small"
            InputLabelProps={{ shrink: true }}
            sx={{ width: 150 }}
          />

          <Box flex={1} />

          {/* Clear Filters */}
          {hasActiveFilters() && (
            <Button startIcon={<ClearIcon />} onClick={handleClearFilters} size="small">
              Clear Filters
            </Button>
          )}
        </Box>
      </Paper>

      {/* Table */}
      <TableContainer component={Paper} variant="outlined">
        <Table>
          <TableHead>
            <TableRow sx={{ bgcolor: 'grey.50' }}>
              <TableCell>Quote #</TableCell>
              <TableCell>Client</TableCell>
              <TableCell align="right">Total</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Valid Until</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : quotations.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                  <Typography color="text.secondary">
                    {hasActiveFilters()
                      ? 'No quotations found matching your filters'
                      : 'No quotations yet. Create your first quotation!'}
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              quotations.map((quotation) => (
                <TableRow key={quotation.id} hover>
                  <TableCell>
                    <Typography
                      variant="body2"
                      fontWeight="medium"
                      sx={{ cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
                      onClick={() => handleViewQuotation(quotation.id)}
                    >
                      {quotation.quotation_number}
                    </Typography>
                  </TableCell>
                  <TableCell>{quotation.client_name || '-'}</TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="medium">
                      {formatCurrency(quotation.grand_total)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <QuotationStatusBadge status={quotation.status} />
                  </TableCell>
                  <TableCell>{formatDate(quotation.created_at)}</TableCell>
                  <TableCell>{formatDate(quotation.valid_until)}</TableCell>
                  <TableCell align="center">
                    <Tooltip title="View">
                      <IconButton size="small" onClick={() => handleViewQuotation(quotation.id)}>
                        <VisibilityIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit">
                      <IconButton size="small" onClick={() => handleEditQuotation(quotation.id)}>
                        <EditIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Clone">
                      <IconButton
                        size="small"
                        onClick={() => handleClone(quotation.id)}
                        disabled={isCloning}
                      >
                        <ContentCopyIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteClick(quotation)}
                        color="error"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>

        <TablePagination
          component="div"
          count={pagination.total}
          page={pagination.page - 1}
          rowsPerPage={pagination.limit}
          onPageChange={handlePageChange}
          onRowsPerPageChange={handleRowsPerPageChange}
          rowsPerPageOptions={[10, 20, 50]}
        />
      </TableContainer>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Quotation</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete quotation "{quotationToDelete?.quotation_number}"?
            This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)} disabled={isDeleting}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
            disabled={isDeleting}
          >
            {isDeleting ? <CircularProgress size={20} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          variant="filled"
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default QuotationsListPage;
