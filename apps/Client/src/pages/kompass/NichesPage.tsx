import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import PeopleIcon from '@mui/icons-material/People';
import type { NicheWithClientCount } from '@/types/kompass';
import { nicheService } from '@/services/kompassService';
import NicheForm from '@/components/kompass/NicheForm';
import axios from 'axios';

const NichesPage: React.FC = () => {
  // Data state
  const [niches, setNiches] = useState<NicheWithClientCount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Dialog state
  const [formOpen, setFormOpen] = useState(false);
  const [selectedNiche, setSelectedNiche] = useState<NicheWithClientCount | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [nicheToDelete, setNicheToDelete] = useState<NicheWithClientCount | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  // Fetch niches
  const fetchNiches = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      console.log('INFO [NichesPage]: Fetching niches');
      const response = await nicheService.list(1, 100);
      // Cast to NicheWithClientCount since the API returns client_count
      const items = response.items || [];
      setNiches(items as NicheWithClientCount[]);
      console.log(`INFO [NichesPage]: Fetched ${items.length} niches`);
    } catch (err) {
      console.log('ERROR [NichesPage]: Failed to fetch niches', err);
      setError(err instanceof Error ? err.message : 'Failed to load niches');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNiches();
  }, [fetchNiches]);

  // Handle add/edit
  const handleAddClick = () => {
    setSelectedNiche(null);
    setFormOpen(true);
  };

  const handleEditClick = (niche: NicheWithClientCount) => {
    setSelectedNiche(niche);
    setFormOpen(true);
  };

  const handleFormClose = () => {
    setFormOpen(false);
    setSelectedNiche(null);
  };

  const handleFormSuccess = () => {
    fetchNiches();
  };

  // Handle delete
  const handleDeleteClick = (niche: NicheWithClientCount) => {
    setNicheToDelete(niche);
    setDeleteError(null);
    setDeleteDialogOpen(true);
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setNicheToDelete(null);
    setDeleteError(null);
  };

  const handleDeleteConfirm = async () => {
    if (!nicheToDelete) return;

    setDeleteLoading(true);
    setDeleteError(null);

    try {
      console.log(`INFO [NichesPage]: Deleting niche ${nicheToDelete.id}`);
      await nicheService.delete(nicheToDelete.id);
      setDeleteDialogOpen(false);
      setNicheToDelete(null);
      fetchNiches();
    } catch (err) {
      console.log('ERROR [NichesPage]: Failed to delete niche', err);
      // Check for 409 Conflict (niche has clients)
      if (axios.isAxiosError(err) && err.response?.status === 409) {
        setDeleteError(
          'This niche cannot be deleted because it has associated clients. Please reassign the clients first.'
        );
      } else {
        setDeleteError(err instanceof Error ? err.message : 'Failed to delete niche');
      }
    } finally {
      setDeleteLoading(false);
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Niches</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={handleAddClick}>
          Add Niche
        </Button>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Loading State */}
      {loading && (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      )}

      {/* Empty State */}
      {!loading && niches.length === 0 && (
        <Box textAlign="center" py={4}>
          <Typography color="text.secondary">
            No niches found. Click "Add Niche" to create one.
          </Typography>
        </Box>
      )}

      {/* Niches Grid */}
      {!loading && niches.length > 0 && (
        <Grid container spacing={3}>
          {niches.map((niche) => (
            <Grid item xs={12} sm={6} md={4} key={niche.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
                    <Typography
                      variant="h6"
                      component="h2"
                      sx={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        maxWidth: '70%',
                      }}
                    >
                      {niche.name}
                    </Typography>
                    <Chip
                      icon={<PeopleIcon fontSize="small" />}
                      label={niche.client_count ?? 0}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </Box>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                      minHeight: 60,
                    }}
                  >
                    {niche.description || 'No description'}
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'flex-end' }}>
                  <IconButton
                    size="small"
                    onClick={() => handleEditClick(niche)}
                    aria-label="edit"
                  >
                    <EditIcon fontSize="small" />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDeleteClick(niche)}
                    aria-label="delete"
                    color="error"
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Niche Form Dialog */}
      <NicheForm
        open={formOpen}
        onClose={handleFormClose}
        onSuccess={handleFormSuccess}
        niche={selectedNiche}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={handleDeleteCancel}>
        <DialogTitle>Delete Niche</DialogTitle>
        <DialogContent>
          {deleteError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {deleteError}
            </Alert>
          )}
          <DialogContentText>
            Are you sure you want to delete the niche "{nicheToDelete?.name}"? This action cannot be
            undone.
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

export default NichesPage;
