import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  TextField,
  InputAdornment,
  Grid,
  CircularProgress,
  Alert,
  IconButton,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Skeleton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TablePagination,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import AddIcon from '@mui/icons-material/Add';
import RefreshIcon from '@mui/icons-material/Refresh';
import ClearIcon from '@mui/icons-material/Clear';
import { usePortfolios } from '@/hooks/kompass/usePortfolios';
import { nicheService } from '@/services/kompassService';
import PortfolioCard from '@/components/kompass/PortfolioCard';
import type { PortfolioResponse, NicheResponse } from '@/types/kompass';

const PortfoliosPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    portfolios,
    pagination,
    filters,
    isLoading,
    error,
    setFilter,
    clearFilters,
    setPage,
    setPageSize,
    deletePortfolio,
    duplicatePortfolio,
    getShareToken,
    refreshPortfolios,
  } = usePortfolios(12);

  const [searchValue, setSearchValue] = useState('');
  const [searchTimeout, setSearchTimeoutState] = useState<ReturnType<typeof setTimeout> | null>(null);
  const [niches, setNiches] = useState<NicheResponse[]>([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deletingPortfolio, setDeletingPortfolio] = useState<PortfolioResponse | null>(null);
  const [duplicateDialogOpen, setDuplicateDialogOpen] = useState(false);
  const [duplicatingPortfolio, setDuplicatingPortfolio] = useState<PortfolioResponse | null>(null);
  const [duplicateName, setDuplicateName] = useState('');
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });
  const [isDeleting, setIsDeleting] = useState(false);
  const [isDuplicating, setIsDuplicating] = useState(false);

  useEffect(() => {
    setSearchValue(filters.search || '');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const fetchNiches = async () => {
      try {
        const response = await nicheService.list(1, 100);
        setNiches(response.items);
      } catch (err) {
        console.error('ERROR [PortfoliosPage]: Failed to fetch niches:', err);
      }
    };
    fetchNiches();
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

  const handleNicheFilterChange = (event: { target: { value: string } }) => {
    const value = event.target.value;
    setFilter('niche_id', value || null);
  };

  const handleStatusFilterChange = (event: { target: { value: string } }) => {
    const value = event.target.value;
    if (value === '') {
      setFilter('is_active', null);
    } else {
      setFilter('is_active', value === 'active');
    }
  };

  const handleClearFilters = () => {
    setSearchValue('');
    clearFilters();
  };

  const handlePageChange = (_event: unknown, newPage: number) => {
    setPage(newPage + 1);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPageSize(parseInt(event.target.value, 10));
  };

  const handleCreatePortfolio = () => {
    navigate('/portfolios/new');
  };

  const handleOpenPortfolio = (portfolio: PortfolioResponse) => {
    navigate(`/portfolios/${portfolio.id}`);
  };

  const handleDeleteClick = (portfolio: PortfolioResponse) => {
    setDeletingPortfolio(portfolio);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingPortfolio) return;

    setIsDeleting(true);
    try {
      await deletePortfolio(deletingPortfolio.id);
      setSnackbar({
        open: true,
        message: 'Portfolio deleted successfully',
        severity: 'success',
      });
    } catch (err) {
      console.error('ERROR [PortfoliosPage]: Failed to delete portfolio:', err);
      setSnackbar({
        open: true,
        message: 'Failed to delete portfolio',
        severity: 'error',
      });
    } finally {
      setIsDeleting(false);
      setDeleteDialogOpen(false);
      setDeletingPortfolio(null);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setDeletingPortfolio(null);
  };

  const handleDuplicateClick = (portfolio: PortfolioResponse) => {
    setDuplicatingPortfolio(portfolio);
    setDuplicateName(`${portfolio.name} (Copy)`);
    setDuplicateDialogOpen(true);
  };

  const handleDuplicateConfirm = async () => {
    if (!duplicatingPortfolio || !duplicateName.trim()) return;

    setIsDuplicating(true);
    try {
      await duplicatePortfolio(duplicatingPortfolio.id, duplicateName.trim());
      setSnackbar({
        open: true,
        message: 'Portfolio duplicated successfully',
        severity: 'success',
      });
    } catch (err) {
      console.error('ERROR [PortfoliosPage]: Failed to duplicate portfolio:', err);
      setSnackbar({
        open: true,
        message: 'Failed to duplicate portfolio',
        severity: 'error',
      });
    } finally {
      setIsDuplicating(false);
      setDuplicateDialogOpen(false);
      setDuplicatingPortfolio(null);
      setDuplicateName('');
    }
  };

  const handleDuplicateCancel = () => {
    setDuplicateDialogOpen(false);
    setDuplicatingPortfolio(null);
    setDuplicateName('');
  };

  const handleCopyShareLink = async (portfolio: PortfolioResponse) => {
    try {
      const token = await getShareToken(portfolio.id);
      const shareUrl = `${window.location.origin}/share/portfolio/${token}`;
      await navigator.clipboard.writeText(shareUrl);
      setSnackbar({
        open: true,
        message: 'Share link copied to clipboard',
        severity: 'success',
      });
    } catch (err) {
      console.error('ERROR [PortfoliosPage]: Failed to copy share link:', err);
      setSnackbar({
        open: true,
        message: 'Failed to copy share link',
        severity: 'error',
      });
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  const hasActiveFilters = filters.search || filters.niche_id || filters.is_active !== null;

  const renderContent = () => {
    if (isLoading && portfolios.length === 0) {
      return (
        <Grid container spacing={2}>
          {[...Array(8)].map((_, i) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={i}>
              <Skeleton variant="rectangular" height={280} sx={{ borderRadius: 1 }} />
            </Grid>
          ))}
        </Grid>
      );
    }

    if (error) {
      return (
        <Alert
          severity="error"
          action={
            <Button color="inherit" size="small" onClick={refreshPortfolios}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      );
    }

    if (portfolios.length === 0) {
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
            No portfolios found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {hasActiveFilters
              ? 'Try adjusting your search or filters'
              : 'Get started by creating your first portfolio'}
          </Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleCreatePortfolio}>
            Create Portfolio
          </Button>
        </Box>
      );
    }

    return (
      <Grid container spacing={2}>
        {portfolios.map((portfolio) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={portfolio.id}>
            <PortfolioCard
              portfolio={portfolio}
              onOpen={handleOpenPortfolio}
              onDuplicate={handleDuplicateClick}
              onDelete={handleDeleteClick}
              onCopyShareLink={handleCopyShareLink}
            />
          </Grid>
        ))}
      </Grid>
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
          Portfolios
        </Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleCreatePortfolio}>
          Create Portfolio
        </Button>
      </Box>

      {/* Search and Filters */}
      <Box
        sx={{
          display: 'flex',
          gap: 2,
          mb: 3,
          flexWrap: 'wrap',
          alignItems: 'center',
        }}
      >
        <TextField
          placeholder="Search portfolios..."
          value={searchValue}
          onChange={handleSearchChange}
          size="small"
          sx={{ minWidth: 250, flex: 1, maxWidth: 400 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />

        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Niche</InputLabel>
          <Select
            value={filters.niche_id || ''}
            label="Niche"
            onChange={handleNicheFilterChange}
          >
            <MenuItem value="">All Niches</MenuItem>
            {niches.map((niche) => (
              <MenuItem key={niche.id} value={niche.id}>
                {niche.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Status</InputLabel>
          <Select
            value={filters.is_active === null ? '' : filters.is_active ? 'active' : 'inactive'}
            label="Status"
            onChange={handleStatusFilterChange}
          >
            <MenuItem value="">All</MenuItem>
            <MenuItem value="active">Published</MenuItem>
            <MenuItem value="inactive">Draft</MenuItem>
          </Select>
        </FormControl>

        {hasActiveFilters && (
          <Button
            variant="outlined"
            size="small"
            startIcon={<ClearIcon />}
            onClick={handleClearFilters}
          >
            Clear Filters
          </Button>
        )}

        <IconButton onClick={refreshPortfolios} disabled={isLoading}>
          <RefreshIcon />
        </IconButton>
      </Box>

      {/* Main Content */}
      <Box sx={{ position: 'relative' }}>
        {isLoading && portfolios.length > 0 && (
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
        {portfolios.length > 0 && (
          <TablePagination
            component="div"
            count={pagination.total}
            page={pagination.page - 1}
            onPageChange={handlePageChange}
            rowsPerPage={pagination.limit}
            onRowsPerPageChange={handleRowsPerPageChange}
            rowsPerPageOptions={[12, 24, 48]}
            sx={{ mt: 2 }}
          />
        )}
      </Box>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleDeleteCancel}>
        <DialogTitle>Delete Portfolio</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete "{deletingPortfolio?.name}"? This action cannot be undone.
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

      {/* Duplicate Dialog */}
      <Dialog open={duplicateDialogOpen} onClose={handleDuplicateCancel}>
        <DialogTitle>Duplicate Portfolio</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Enter a name for the duplicated portfolio:
          </DialogContentText>
          <TextField
            autoFocus
            fullWidth
            label="Portfolio Name"
            value={duplicateName}
            onChange={(e) => setDuplicateName(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDuplicateCancel} disabled={isDuplicating}>
            Cancel
          </Button>
          <Button
            onClick={handleDuplicateConfirm}
            color="primary"
            disabled={isDuplicating || !duplicateName.trim()}
            startIcon={isDuplicating ? <CircularProgress size={16} /> : undefined}
          >
            Duplicate
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

export default PortfoliosPage;
