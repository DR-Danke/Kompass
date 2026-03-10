import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
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
  TableSortLabel,
  Paper,
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
  FormControl,
  InputLabel,
  Select,
  FormControlLabel,
  Checkbox,
  FormGroup,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import SearchIcon from '@mui/icons-material/Search';
import ViewListIcon from '@mui/icons-material/ViewList';
import ViewKanbanIcon from '@mui/icons-material/ViewKanban';
import type {
  SupplierResponse,
  SupplierStatus,
  SupplierPipelineStatus,
  SupplierWithProductCount,
  CertificationStatus,
  SupplierDeletePreview,
  OutreachTemplate,
  SupplierOutreachRequest,
} from '@/types/kompass';
import { supplierService } from '@/services/kompassService';
import SupplierForm from '@/components/kompass/SupplierForm';
import PipelineStatusBadge from '@/components/kompass/PipelineStatusBadge';
import CertificationStatusBadge from '@/components/kompass/CertificationStatusBadge';
import SupplierQuickActionsMenu from '@/components/kompass/SupplierQuickActionsMenu';
import SupplierPipelineKanban from '@/components/kompass/SupplierPipelineKanban';
import AuditUploader from '@/components/kompass/AuditUploader';
import { useSupplierPipeline, ViewMode } from '@/hooks/kompass/useSupplierPipeline';

type StatusFilter = SupplierStatus | 'all';
type PipelineFilter = SupplierPipelineStatus | 'all';
type CertificationFilter = 'all' | 'certified' | 'certified_a' | 'certified_b' | 'certified_c' | 'uncertified';
type SortField = 'name' | 'certification_status' | 'pipeline_status' | 'certified_at';
type SortOrder = 'asc' | 'desc';

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

const certificationOptions: { value: CertificationFilter; label: string }[] = [
  { value: 'all', label: 'All Certifications' },
  { value: 'certified', label: 'Certified (Any)' },
  { value: 'certified_a', label: 'Type A' },
  { value: 'certified_b', label: 'Type B' },
  { value: 'certified_c', label: 'Type C' },
  { value: 'uncertified', label: 'Uncertified' },
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

const OUTREACH_STATUS_CONFIG: Record<string, { label: string; color: 'default' | 'warning' | 'info' | 'success' | 'secondary' }> = {
  none: { label: 'Sin contactar', color: 'default' },
  pending: { label: 'Pendiente', color: 'warning' },
  contacted: { label: 'Contactado', color: 'info' },
  responded: { label: 'Respondió', color: 'success' },
  meeting_scheduled: { label: 'Reunión agendada', color: 'secondary' },
  completed: { label: 'Completado', color: 'success' },
};

const formatDate = (dateString: string | null): string => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

const SuppliersPage: React.FC = () => {
  const navigate = useNavigate();

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
  const [certificationFilter, setCertificationFilter] = useState<CertificationFilter>('all');

  // Sorting state
  const [sortField, setSortField] = useState<SortField>('name');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');

  // Dialog state
  const [formOpen, setFormOpen] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState<SupplierResponse | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [supplierToDelete, setSupplierToDelete] = useState<SupplierResponse | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deletePreview, setDeletePreview] = useState<SupplierDeletePreview | null>(null);
  const [deletePreviewLoading, setDeletePreviewLoading] = useState(false);

  // Audit upload dialog state
  const [auditUploadOpen, setAuditUploadOpen] = useState(false);
  const [auditUploadSupplier, setAuditUploadSupplier] = useState<SupplierResponse | null>(null);

  // Pipeline status update loading state
  const [pipelineStatusLoading, setPipelineStatusLoading] = useState<string | null>(null);

  // Excel export loading state
  const [exporting, setExporting] = useState(false);

  // Outreach dialog state
  const [outreachDialogOpen, setOutreachDialogOpen] = useState(false);
  const [outreachSupplier, setOutreachSupplier] = useState<SupplierResponse | null>(null);
  const [outreachTemplates, setOutreachTemplates] = useState<OutreachTemplate[]>([]);
  const [outreachSelectedTemplate, setOutreachSelectedTemplate] = useState('follow_up_catalog');
  const [outreachChannels, setOutreachChannels] = useState<('email' | 'wechat')[]>(['email']);
  const [outreachCustomMessage, setOutreachCustomMessage] = useState('');
  const [outreachLoading, setOutreachLoading] = useState(false);
  const [outreachResult, setOutreachResult] = useState<{ success: boolean; message: string } | null>(null);

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
      const filters: {
        status?: string;
        search?: string;
        pipeline_status?: string;
        certification_status?: string;
        sort_by?: string;
        sort_order?: 'asc' | 'desc';
      } = {};
      if (statusFilter !== 'all') {
        filters.status = statusFilter;
      }
      if (pipelineFilter !== 'all') {
        filters.pipeline_status = pipelineFilter;
      }
      if (certificationFilter !== 'all') {
        filters.certification_status = certificationFilter;
      }
      if (debouncedSearch) {
        filters.search = debouncedSearch;
      }
      filters.sort_by = sortField;
      filters.sort_order = sortOrder;

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
  }, [page, limit, statusFilter, pipelineFilter, certificationFilter, debouncedSearch, sortField, sortOrder]);

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

  const handleCertificationFilterChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setCertificationFilter(event.target.value as CertificationFilter);
    setPage(0);
  };

  // Handle sorting
  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
    setPage(0);
  };

  // Handle Excel export
  const handleExportExcel = async () => {
    setExporting(true);
    try {
      const filters: {
        status?: string;
        search?: string;
        pipeline_status?: string;
        certification_status?: string;
        sort_by?: string;
        sort_order?: 'asc' | 'desc';
      } = {};
      if (statusFilter !== 'all') filters.status = statusFilter;
      if (pipelineFilter !== 'all') filters.pipeline_status = pipelineFilter;
      if (certificationFilter !== 'all') filters.certification_status = certificationFilter;
      if (debouncedSearch) filters.search = debouncedSearch;
      filters.sort_by = sortField;
      filters.sort_order = sortOrder;

      const blob = await supplierService.exportVerificationExcel(filters);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `supplier_verification_export_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.log('ERROR [SuppliersPage]: Failed to export Excel', err);
      setError(err instanceof Error ? err.message : 'Failed to export supplier data');
    } finally {
      setExporting(false);
    }
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
  const handleDeleteClick = async (supplier: SupplierResponse) => {
    setSupplierToDelete(supplier);
    setDeleteDialogOpen(true);
    setDeletePreviewLoading(true);
    try {
      const preview = await supplierService.getDeletePreview(supplier.id);
      setDeletePreview(preview);
    } catch (err) {
      console.log('ERROR [SuppliersPage]: Failed to fetch delete preview', err);
      setDeletePreview(null);
    } finally {
      setDeletePreviewLoading(false);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setSupplierToDelete(null);
    setDeletePreview(null);
  };

  const handleDeleteConfirm = async () => {
    if (!supplierToDelete) return;

    setDeleteLoading(true);
    try {
      console.log(`INFO [SuppliersPage]: Hard deleting supplier ${supplierToDelete.id}`);
      const result = await supplierService.delete(supplierToDelete.id);
      console.log(
        `INFO [SuppliersPage]: Supplier deleted - products: ${result.products_deleted}, audits: ${result.audits_deleted}`
      );
      setDeleteDialogOpen(false);
      setSupplierToDelete(null);
      setDeletePreview(null);
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

  // Handle quick action: Upload Audit
  const handleUploadAudit = (supplier: SupplierResponse) => {
    setAuditUploadSupplier(supplier);
    setAuditUploadOpen(true);
  };

  const handleAuditUploadClose = () => {
    setAuditUploadOpen(false);
    setAuditUploadSupplier(null);
  };

  const handleAuditUploadComplete = () => {
    console.log('INFO [SuppliersPage]: Audit upload completed');
    setAuditUploadOpen(false);
    setAuditUploadSupplier(null);
    // Refresh suppliers to get updated certification status
    if (viewMode === 'list') {
      fetchSuppliers();
    } else {
      fetchPipeline();
    }
  };

  // Handle quick action: View Certification
  // Opens the supplier form - user can navigate to Certification tab
  const handleViewCertification = (supplier: SupplierResponse) => {
    setSelectedSupplier(supplier);
    setFormOpen(true);
  };

  // Handle quick action: Change Pipeline Status
  const handleChangePipelineStatus = async (supplier: SupplierResponse, status: SupplierPipelineStatus) => {
    setPipelineStatusLoading(supplier.id);
    try {
      console.log(`INFO [SuppliersPage]: Changing pipeline status for ${supplier.id} to ${status}`);
      await supplierService.updatePipelineStatus(supplier.id, status);
      if (viewMode === 'list') {
        fetchSuppliers();
      } else {
        fetchPipeline();
      }
    } catch (err) {
      console.log('ERROR [SuppliersPage]: Failed to change pipeline status', err);
      setError(err instanceof Error ? err.message : 'Failed to change pipeline status');
    } finally {
      setPipelineStatusLoading(null);
    }
  };

  // Handle quick action: Send Outreach
  const handleSendOutreach = async (supplier: SupplierResponse) => {
    setOutreachSupplier(supplier);
    setOutreachResult(null);
    setOutreachCustomMessage('');
    setOutreachSelectedTemplate('follow_up_catalog');
    setOutreachChannels(supplier.contact_email ? ['email'] : []);
    setOutreachDialogOpen(true);

    // Load templates if not already loaded
    if (outreachTemplates.length === 0) {
      try {
        const templates = await supplierService.getOutreachTemplates();
        setOutreachTemplates(templates);
      } catch (err) {
        console.log('ERROR [SuppliersPage]: Failed to load outreach templates', err);
      }
    }
  };

  const handleOutreachClose = () => {
    setOutreachDialogOpen(false);
    setOutreachSupplier(null);
    setOutreachResult(null);
  };

  const handleOutreachSend = async () => {
    if (!outreachSupplier || outreachChannels.length === 0) return;
    setOutreachLoading(true);
    setOutreachResult(null);
    try {
      const request: SupplierOutreachRequest = {
        template: outreachSelectedTemplate,
        channels: outreachChannels,
        custom_message: outreachCustomMessage || undefined,
      };
      const result = await supplierService.sendOutreach(outreachSupplier.id, request);
      const success = result.email_sent || result.wechat_sent;
      setOutreachResult({ success, message: result.message });
      if (success) {
        // Refresh supplier data to reflect updated outreach_status
        if (viewMode === 'list') {
          fetchSuppliers();
        } else {
          fetchPipeline();
        }
      }
    } catch (err) {
      console.log('ERROR [SuppliersPage]: Failed to send outreach', err);
      setOutreachResult({ success: false, message: err instanceof Error ? err.message : 'Error al enviar' });
    } finally {
      setOutreachLoading(false);
    }
  };

  const handleOutreachChannelToggle = (channel: 'email' | 'wechat') => {
    setOutreachChannels(prev =>
      prev.includes(channel)
        ? prev.filter(c => c !== channel)
        : [...prev, channel]
    );
  };

  // Handle quick action: Import Products
  const handleImportProducts = (supplier: SupplierResponse) => {
    navigate(`/import-wizard?supplier_id=${supplier.id}`);
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

  const hasActiveFilters =
    debouncedSearch ||
    statusFilter !== 'all' ||
    pipelineFilter !== 'all' ||
    certificationFilter !== 'all';

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
            variant="outlined"
            startIcon={exporting ? <CircularProgress size={20} /> : <FileDownloadIcon />}
            onClick={handleExportExcel}
            disabled={exporting}
          >
            Export Excel
          </Button>
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
      <Box display="flex" gap={2} mb={2} flexWrap="wrap">
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
              sx={{ width: 160 }}
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
              sx={{ width: 160 }}
            >
              {pipelineOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Certification"
              value={certificationFilter}
              onChange={handleCertificationFilterChange}
              size="small"
              sx={{ width: 180 }}
            >
              {certificationOptions.map((option) => (
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
                <TableCell>
                  <TableSortLabel
                    active={sortField === 'name'}
                    direction={sortField === 'name' ? sortOrder : 'asc'}
                    onClick={() => handleSort('name')}
                  >
                    Name
                  </TableSortLabel>
                </TableCell>
                <TableCell>Country</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === 'certification_status'}
                    direction={sortField === 'certification_status' ? sortOrder : 'asc'}
                    onClick={() => handleSort('certification_status')}
                  >
                    Certification
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === 'pipeline_status'}
                    direction={sortField === 'pipeline_status' ? sortOrder : 'asc'}
                    onClick={() => handleSort('pipeline_status')}
                  >
                    Pipeline
                  </TableSortLabel>
                </TableCell>
                <TableCell>
                  <TableSortLabel
                    active={sortField === 'certified_at'}
                    direction={sortField === 'certified_at' ? sortOrder : 'asc'}
                    onClick={() => handleSort('certified_at')}
                  >
                    Certified Date
                  </TableSortLabel>
                </TableCell>
                <TableCell>Seguimiento</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : suppliers.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">
                      {hasActiveFilters
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
                          maxWidth: 200,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {supplier.name}
                      </Typography>
                    </TableCell>
                    <TableCell>{supplier.country}</TableCell>
                    <TableCell>
                      <Chip
                        label={getStatusLabel(supplier.status)}
                        color={getStatusChipColor(supplier.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <CertificationStatusBadge
                        certificationStatus={supplier.certification_status as CertificationStatus}
                        latestAuditId={supplier.latest_audit_id}
                      />
                    </TableCell>
                    <TableCell>
                      <PipelineStatusBadge status={supplier.pipeline_status} />
                    </TableCell>
                    <TableCell>{formatDate(supplier.certified_at)}</TableCell>
                    <TableCell>
                      {(supplier.outreach_status && supplier.outreach_status !== 'none') && (
                        <Chip
                          label={OUTREACH_STATUS_CONFIG[supplier.outreach_status]?.label || supplier.outreach_status}
                          color={OUTREACH_STATUS_CONFIG[supplier.outreach_status]?.color || 'default'}
                          size="small"
                          variant="outlined"
                        />
                      )}
                    </TableCell>
                    <TableCell align="right">
                      <SupplierQuickActionsMenu
                        supplier={supplier}
                        onEdit={handleEditClick}
                        onDelete={handleDeleteClick}
                        onUploadAudit={handleUploadAudit}
                        onViewCertification={handleViewCertification}
                        onImportProducts={handleImportProducts}
                        onChangePipelineStatus={handleChangePipelineStatus}
                        onSendOutreach={handleSendOutreach}
                        isUpdating={pipelineStatusLoading === supplier.id}
                      />
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
        <DialogTitle sx={{ color: 'error.main' }}>Permanently Delete Supplier</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This action is irreversible. All associated data will be permanently removed.
          </Alert>
          <DialogContentText>
            Are you sure you want to permanently delete the supplier &quot;{supplierToDelete?.name}&quot;?
          </DialogContentText>
          {deletePreviewLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
              <CircularProgress size={24} />
            </Box>
          ) : deletePreview && (deletePreview.products_count > 0 || deletePreview.audits_count > 0) ? (
            <DialogContentText sx={{ mt: 1 }}>
              This will also delete:
              {deletePreview.products_count > 0 && (
                <Box component="span" sx={{ display: 'block', ml: 2 }}>
                  - {deletePreview.products_count} product{deletePreview.products_count !== 1 ? 's' : ''} (and associated images, tags, portfolio references)
                </Box>
              )}
              {deletePreview.audits_count > 0 && (
                <Box component="span" sx={{ display: 'block', ml: 2 }}>
                  - {deletePreview.audits_count} audit report{deletePreview.audits_count !== 1 ? 's' : ''}
                </Box>
              )}
            </DialogContentText>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} disabled={deleteLoading}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
            disabled={deleteLoading || deletePreviewLoading}
          >
            {deleteLoading ? <CircularProgress size={20} /> : 'Delete Permanently'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Audit Upload Dialog */}
      <Dialog
        open={auditUploadOpen}
        onClose={handleAuditUploadClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Upload Audit for {auditUploadSupplier?.name}</DialogTitle>
        <DialogContent>
          {auditUploadSupplier && (
            <Box sx={{ pt: 2 }}>
              <AuditUploader
                supplierId={auditUploadSupplier.id}
                onUploadComplete={handleAuditUploadComplete}
                onError={(err) => setError(err)}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleAuditUploadClose}>Cancel</Button>
        </DialogActions>
      </Dialog>

      {/* Outreach Dialog */}
      <Dialog
        open={outreachDialogOpen}
        onClose={handleOutreachClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Enviar Seguimiento — {outreachSupplier?.name}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
            {/* Template selector */}
            <FormControl fullWidth size="small">
              <InputLabel>Plantilla</InputLabel>
              <Select
                value={outreachSelectedTemplate}
                label="Plantilla"
                onChange={(e) => setOutreachSelectedTemplate(e.target.value)}
              >
                {outreachTemplates.map((tmpl) => (
                  <MenuItem key={tmpl.key} value={tmpl.key}>
                    {tmpl.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Channel checkboxes */}
            <FormControl component="fieldset">
              <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                Canales
              </Typography>
              <FormGroup row>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={outreachChannels.includes('email')}
                      onChange={() => handleOutreachChannelToggle('email')}
                      disabled={!outreachSupplier?.contact_email}
                    />
                  }
                  label={`Email${!outreachSupplier?.contact_email ? ' (sin email)' : ''}`}
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={outreachChannels.includes('wechat')}
                      onChange={() => handleOutreachChannelToggle('wechat')}
                      disabled={!outreachSupplier?.contact_phone}
                    />
                  }
                  label={`WeChat${!outreachSupplier?.contact_phone ? ' (sin ID)' : ''}`}
                />
              </FormGroup>
            </FormControl>

            {/* Message preview */}
            {outreachTemplates.length > 0 && (
              <Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                  Vista previa
                </Typography>
                <Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'grey.50' }}>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                    Asunto: {outreachTemplates.find(t => t.key === outreachSelectedTemplate)?.subject || ''}
                  </Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-line', fontSize: '0.8rem' }}>
                    {outreachTemplates.find(t => t.key === outreachSelectedTemplate)?.body_preview || ''}
                  </Typography>
                </Paper>
              </Box>
            )}

            {/* Custom message override */}
            <TextField
              label="Mensaje personalizado (opcional)"
              multiline
              rows={3}
              value={outreachCustomMessage}
              onChange={(e) => setOutreachCustomMessage(e.target.value)}
              size="small"
              helperText="Si se proporciona, reemplaza el cuerpo de la plantilla"
            />

            {/* Result feedback */}
            {outreachResult && (
              <Alert severity={outreachResult.success ? 'success' : 'error'}>
                {outreachResult.message}
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleOutreachClose}>Cancelar</Button>
          <Button
            onClick={handleOutreachSend}
            variant="contained"
            disabled={outreachLoading || outreachChannels.length === 0}
          >
            {outreachLoading ? <CircularProgress size={20} /> : 'Enviar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SuppliersPage;
