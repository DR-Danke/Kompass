import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  TextField,
  Switch,
  FormControlLabel,
  CircularProgress,
  Alert,
  Snackbar,
  Paper,
  IconButton,
  Tooltip,
  Autocomplete,
  Breadcrumbs,
  Link,
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import LinkIcon from '@mui/icons-material/Link';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { usePortfolioBuilder } from '@/hooks/kompass/usePortfolioBuilder';
import { nicheService } from '@/services/kompassService';
import ProductCatalogMini from '@/components/kompass/ProductCatalogMini';
import PortfolioBuilder from '@/components/kompass/PortfolioBuilder';
import type { NicheResponse } from '@/types/kompass';

const PortfolioBuilderPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isNewPortfolio = id === 'new';

  const {
    portfolio,
    items,
    isLoading,
    isSaving,
    error,
    isDirty,
    isNew,
    loadPortfolio,
    initNewPortfolio,
    updateMetadata,
    addItem,
    removeItem,
    updateItemNotes,
    reorderItems,
    savePortfolio,
    getShareToken,
    exportPdf,
    isProductInPortfolio,
  } = usePortfolioBuilder();

  const [niches, setNiches] = useState<NicheResponse[]>([]);
  const [selectedNiche, setSelectedNiche] = useState<NicheResponse | null>(null);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' | 'info' }>({
    open: false,
    message: '',
    severity: 'success',
  });
  const [isExporting, setIsExporting] = useState(false);
  const [isCopyingLink, setIsCopyingLink] = useState(false);

  // Load portfolio or initialize new one
  useEffect(() => {
    if (isNewPortfolio) {
      initNewPortfolio();
    } else if (id) {
      loadPortfolio(id);
    }
  }, [id, isNewPortfolio, loadPortfolio, initNewPortfolio]);

  // Fetch niches
  useEffect(() => {
    const fetchNiches = async () => {
      try {
        const response = await nicheService.list(1, 100);
        setNiches(response.items);
      } catch (err) {
        console.error('ERROR [PortfolioBuilderPage]: Failed to fetch niches:', err);
      }
    };
    fetchNiches();
  }, []);

  // Set selected niche when portfolio loads
  useEffect(() => {
    if (portfolio?.niche_id && niches.length > 0) {
      const niche = niches.find(n => n.id === portfolio.niche_id);
      setSelectedNiche(niche || null);
    }
  }, [portfolio?.niche_id, niches]);

  const handleNameChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    updateMetadata({ name: event.target.value });
  }, [updateMetadata]);

  const handleNicheChange = useCallback((_event: React.SyntheticEvent, newValue: NicheResponse | null) => {
    setSelectedNiche(newValue);
    updateMetadata({ niche_id: newValue?.id || null });
  }, [updateMetadata]);

  const handleStatusChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    updateMetadata({ is_active: event.target.checked });
  }, [updateMetadata]);

  const handleSave = async () => {
    try {
      const savedPortfolio = await savePortfolio();
      setSnackbar({
        open: true,
        message: 'Portfolio saved successfully',
        severity: 'success',
      });
      // Navigate to the portfolio ID if it was a new portfolio
      if (isNew && savedPortfolio.id) {
        navigate(`/portfolios/${savedPortfolio.id}`, { replace: true });
      }
    } catch (err) {
      console.error('ERROR [PortfolioBuilderPage]: Failed to save portfolio:', err);
      setSnackbar({
        open: true,
        message: 'Failed to save portfolio',
        severity: 'error',
      });
    }
  };

  const handleCopyShareLink = async () => {
    if (isNew) {
      setSnackbar({
        open: true,
        message: 'Please save the portfolio first to generate a share link',
        severity: 'info',
      });
      return;
    }

    setIsCopyingLink(true);
    try {
      const token = await getShareToken();
      const shareUrl = `${window.location.origin}/share/portfolio/${token}`;
      await navigator.clipboard.writeText(shareUrl);
      setSnackbar({
        open: true,
        message: 'Share link copied to clipboard',
        severity: 'success',
      });
    } catch (err) {
      console.error('ERROR [PortfolioBuilderPage]: Failed to copy share link:', err);
      setSnackbar({
        open: true,
        message: 'Failed to copy share link',
        severity: 'error',
      });
    } finally {
      setIsCopyingLink(false);
    }
  };

  const handleExportPdf = async () => {
    if (isNew) {
      setSnackbar({
        open: true,
        message: 'Please save the portfolio first to export PDF',
        severity: 'info',
      });
      return;
    }

    setIsExporting(true);
    try {
      await exportPdf();
      setSnackbar({
        open: true,
        message: 'PDF exported successfully',
        severity: 'success',
      });
    } catch (err) {
      console.error('ERROR [PortfolioBuilderPage]: Failed to export PDF:', err);
      setSnackbar({
        open: true,
        message: 'Failed to export PDF',
        severity: 'error',
      });
    } finally {
      setIsExporting(false);
    }
  };

  const handleAddProduct = async (productId: string) => {
    try {
      await addItem(productId);
    } catch (err) {
      console.error('ERROR [PortfolioBuilderPage]: Failed to add product:', err);
      setSnackbar({
        open: true,
        message: 'Failed to add product to portfolio',
        severity: 'error',
      });
    }
  };

  const handleRemoveItem = async (itemId: string) => {
    try {
      await removeItem(itemId);
    } catch (err) {
      console.error('ERROR [PortfolioBuilderPage]: Failed to remove item:', err);
      setSnackbar({
        open: true,
        message: 'Failed to remove product from portfolio',
        severity: 'error',
      });
    }
  };

  const handleReorder = async (productIds: string[]) => {
    try {
      await reorderItems(productIds);
    } catch (err) {
      console.error('ERROR [PortfolioBuilderPage]: Failed to reorder items:', err);
      setSnackbar({
        open: true,
        message: 'Failed to reorder products',
        severity: 'error',
      });
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  const handleBackClick = () => {
    navigate('/portfolios');
  };

  if (isLoading && !portfolio) {
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error && !portfolio) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="contained" onClick={handleBackClick}>
          Back to Portfolios
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link
          component="button"
          underline="hover"
          color="inherit"
          onClick={handleBackClick}
          sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}
        >
          <ArrowBackIcon sx={{ mr: 0.5, fontSize: 18 }} />
          Portfolios
        </Link>
        <Typography color="text.primary">
          {isNew ? 'New Portfolio' : portfolio?.name || 'Edit Portfolio'}
        </Typography>
      </Breadcrumbs>

      {/* Top Bar */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
          {/* Portfolio Name */}
          <TextField
            label="Portfolio Name"
            value={portfolio?.name || ''}
            onChange={handleNameChange}
            size="small"
            sx={{ minWidth: 200, flex: 1, maxWidth: 300 }}
          />

          {/* Niche Selector */}
          <Autocomplete
            options={niches}
            getOptionLabel={(option) => option.name}
            value={selectedNiche}
            onChange={handleNicheChange}
            size="small"
            sx={{ minWidth: 180 }}
            renderInput={(params) => (
              <TextField {...params} label="Niche" />
            )}
          />

          {/* Status Toggle */}
          <FormControlLabel
            control={
              <Switch
                checked={portfolio?.is_active ?? true}
                onChange={handleStatusChange}
                color="success"
              />
            }
            label={portfolio?.is_active ? 'Published' : 'Draft'}
          />

          <Box sx={{ flex: 1 }} />

          {/* Action Buttons */}
          <Tooltip title="Copy Share Link">
            <IconButton
              onClick={handleCopyShareLink}
              disabled={isCopyingLink}
            >
              {isCopyingLink ? <CircularProgress size={20} /> : <LinkIcon />}
            </IconButton>
          </Tooltip>

          <Tooltip title="Preview PDF">
            <IconButton
              onClick={handleExportPdf}
              disabled={isExporting}
            >
              {isExporting ? <CircularProgress size={20} /> : <PictureAsPdfIcon />}
            </IconButton>
          </Tooltip>

          <Button
            variant="contained"
            startIcon={isSaving ? <CircularProgress size={16} color="inherit" /> : <SaveIcon />}
            onClick={handleSave}
            disabled={isSaving || (!isDirty && !isNew)}
          >
            {isSaving ? 'Saving...' : 'Save'}
          </Button>
        </Box>
      </Paper>

      {/* Two-Column Layout */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          gap: 2,
          minHeight: 0,
        }}
      >
        {/* Left Panel - Product Catalog (40%) */}
        <Paper
          sx={{
            width: '40%',
            p: 2,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          <ProductCatalogMini
            onAddProduct={handleAddProduct}
            isProductInPortfolio={isProductInPortfolio}
          />
        </Paper>

        {/* Right Panel - Portfolio Builder (60%) */}
        <Paper
          sx={{
            flex: 1,
            p: 2,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          <PortfolioBuilder
            items={items}
            isLoading={isLoading}
            onReorder={handleReorder}
            onRemoveItem={handleRemoveItem}
            onUpdateNotes={updateItemNotes}
          />
        </Paper>
      </Box>

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

export default PortfolioBuilderPage;
