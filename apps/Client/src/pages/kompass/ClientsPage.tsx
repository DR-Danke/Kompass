import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  ToggleButton,
  ToggleButtonGroup,
  InputAdornment,
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
import ViewKanbanIcon from '@mui/icons-material/ViewKanban';
import ViewListIcon from '@mui/icons-material/ViewList';
import SearchIcon from '@mui/icons-material/Search';
import type { ClientResponse, ClientStatus, PipelineResponse } from '@/types/kompass';
import { useClients, ViewMode } from '@/hooks/kompass/useClients';
import ClientKanbanBoard from '@/components/kompass/ClientKanbanBoard';
import ClientListView from '@/components/kompass/ClientListView';
import ClientDetailDrawer from '@/components/kompass/ClientDetailDrawer';
import ClientForm from '@/components/kompass/ClientForm';

const INITIAL_PIPELINE: PipelineResponse = {
  lead: [],
  qualified: [],
  quoting: [],
  negotiating: [],
  won: [],
  lost: [],
};

const ClientsPage: React.FC = () => {
  const {
    pipeline,
    clients,
    selectedClient,
    clientWithQuotations,
    statusHistory,
    viewMode,
    isLoading,
    isUpdating,
    error,
    searchQuery,
    fetchClients,
    setSelectedClient,
    fetchClientWithQuotations,
    fetchStatusHistory,
    updateClientStatus,
    createClient,
    updateClient,
    deleteClient,
    setViewMode,
    setSearchQuery,
    clearError,
  } = useClients();

  // Local state
  const [formOpen, setFormOpen] = useState(false);
  const [editingClient, setEditingClient] = useState<ClientResponse | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [clientToDelete, setClientToDelete] = useState<ClientResponse | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Filter clients when in list mode
  useEffect(() => {
    if (viewMode === 'list' && debouncedSearch !== undefined) {
      fetchClients({ search: debouncedSearch || undefined });
    }
  }, [viewMode, debouncedSearch, fetchClients]);

  // Handlers
  const handleViewModeChange = (_event: React.MouseEvent<HTMLElement>, newMode: ViewMode | null) => {
    if (newMode) {
      setViewMode(newMode);
    }
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
  };

  const handleAddClick = () => {
    setEditingClient(null);
    setFormOpen(true);
  };

  const handleEditClick = (client: ClientResponse) => {
    setEditingClient(client);
    setFormOpen(true);
    setDrawerOpen(false);
  };

  const handleFormClose = () => {
    setFormOpen(false);
    setEditingClient(null);
  };

  const handleFormSuccess = () => {
    setSnackbar({
      open: true,
      message: editingClient ? 'Client updated successfully' : 'Client created successfully',
      severity: 'success',
    });
  };

  const handleClientClick = async (client: ClientResponse) => {
    setSelectedClient(client);
    setDrawerOpen(true);
    // Fetch detailed data
    await Promise.all([
      fetchClientWithQuotations(client.id),
      fetchStatusHistory(client.id),
    ]);
  };

  const handleDrawerClose = () => {
    setDrawerOpen(false);
    setSelectedClient(null);
  };

  const handleStatusChange = async (clientId: string, newStatus: ClientStatus, notes?: string) => {
    try {
      await updateClientStatus(clientId, newStatus, notes);
      setSnackbar({
        open: true,
        message: 'Status updated successfully',
        severity: 'success',
      });
      // Refresh status history if drawer is open
      if (drawerOpen && selectedClient?.id === clientId) {
        await fetchStatusHistory(clientId);
      }
    } catch (err) {
      setSnackbar({
        open: true,
        message: 'Failed to update status',
        severity: 'error',
      });
    }
  };

  const handleDeleteClick = (client: ClientResponse) => {
    setClientToDelete(client);
    setDeleteDialogOpen(true);
    setDrawerOpen(false);
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setClientToDelete(null);
  };

  const handleDeleteConfirm = async () => {
    if (!clientToDelete) return;

    setDeleteLoading(true);
    try {
      await deleteClient(clientToDelete.id);
      setDeleteDialogOpen(false);
      setClientToDelete(null);
      setSnackbar({
        open: true,
        message: 'Client deleted successfully',
        severity: 'success',
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: err instanceof Error ? err.message : 'Failed to delete client',
        severity: 'error',
      });
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  // Filter pipeline based on search in Kanban mode
  const getFilteredPipeline = (): PipelineResponse => {
    if (!pipeline) return INITIAL_PIPELINE;
    if (!debouncedSearch) return pipeline;

    const searchLower = debouncedSearch.toLowerCase();
    const filterClients = (clients: ClientResponse[]) =>
      clients.filter(
        (c) =>
          c.company_name.toLowerCase().includes(searchLower) ||
          c.contact_name?.toLowerCase().includes(searchLower) ||
          c.email?.toLowerCase().includes(searchLower) ||
          c.project_name?.toLowerCase().includes(searchLower)
      );

    return {
      lead: filterClients(pipeline.lead),
      qualified: filterClients(pipeline.qualified),
      quoting: filterClients(pipeline.quoting),
      negotiating: filterClients(pipeline.negotiating),
      won: filterClients(pipeline.won),
      lost: filterClients(pipeline.lost),
    };
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Clients Pipeline</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleAddClick}>
          Add Client
        </Button>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={clearError}>
          {error}
        </Alert>
      )}

      {/* Toolbar */}
      <Box display="flex" gap={2} mb={2} alignItems="center" flexWrap="wrap">
        <TextField
          placeholder="Search clients..."
          value={searchQuery}
          onChange={handleSearchChange}
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

        <Box flex={1} />

        <ToggleButtonGroup
          value={viewMode}
          exclusive
          onChange={handleViewModeChange}
          size="small"
        >
          <ToggleButton value="kanban" aria-label="Kanban view">
            <ViewKanbanIcon sx={{ mr: 0.5 }} />
            Kanban
          </ToggleButton>
          <ToggleButton value="list" aria-label="List view">
            <ViewListIcon sx={{ mr: 0.5 }} />
            List
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {/* Loading State */}
      {isLoading ? (
        <Box display="flex" justifyContent="center" py={8}>
          <CircularProgress />
        </Box>
      ) : viewMode === 'kanban' ? (
        /* Kanban View */
        <ClientKanbanBoard
          pipeline={getFilteredPipeline()}
          onClientClick={handleClientClick}
          onStatusChange={handleStatusChange}
          isUpdating={isUpdating}
        />
      ) : (
        /* List View */
        <ClientListView
          clients={clients}
          isLoading={isLoading}
          onClientClick={handleClientClick}
          onEditClick={handleEditClick}
          onDeleteClick={handleDeleteClick}
        />
      )}

      {/* Client Detail Drawer */}
      <ClientDetailDrawer
        open={drawerOpen}
        client={selectedClient}
        clientWithQuotations={clientWithQuotations}
        statusHistory={statusHistory}
        onClose={handleDrawerClose}
        onEdit={handleEditClick}
        onStatusChange={handleStatusChange}
      />

      {/* Client Form Dialog */}
      <ClientForm
        open={formOpen}
        onClose={handleFormClose}
        onSuccess={handleFormSuccess}
        client={editingClient}
        onCreate={createClient}
        onUpdate={updateClient}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleDeleteCancel}>
        <DialogTitle>Delete Client</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete the client "{clientToDelete?.company_name}"? This action
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

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbar.severity} variant="filled">
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ClientsPage;
