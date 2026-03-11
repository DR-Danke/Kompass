import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  TextField,
  Chip,
  Snackbar,
  Alert,
  Paper,
  Button,
  CircularProgress,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Checkbox,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  ToggleButton,
  ToggleButtonGroup,
  Skeleton,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import BrokenImageIcon from '@mui/icons-material/BrokenImage';
import CloseIcon from '@mui/icons-material/Close';
import { useLocation } from 'react-router-dom';
import type { BusinessCardCaptureStatus } from '@/types/kompass';
import { useCardReview } from '@/hooks/kompass/useCardReview';

const STATUS_COLORS: Record<BusinessCardCaptureStatus, 'warning' | 'info' | 'success' | 'error' | 'default'> = {
  pending: 'warning',
  processing: 'info',
  extracted: 'success',
  confirmed: 'default',
  rejected: 'error',
  failed: 'error',
};

const STATUS_LABELS: Record<BusinessCardCaptureStatus, string> = {
  pending: 'Pendiente',
  processing: 'Procesando',
  extracted: 'Extraído',
  confirmed: 'Confirmado',
  rejected: 'Rechazado',
  failed: 'Fallido',
};

const FILTER_OPTIONS: { value: BusinessCardCaptureStatus | 'all'; label: string }[] = [
  { value: 'all', label: 'Todos' },
  { value: 'pending', label: 'Pendientes' },
  { value: 'extracted', label: 'Extraídas' },
  { value: 'confirmed', label: 'Confirmadas' },
  { value: 'rejected', label: 'Rechazadas' },
];

function getConfidenceColor(score: number): 'success' | 'warning' | 'error' {
  if (score >= 0.8) return 'success';
  if (score >= 0.5) return 'warning';
  return 'error';
}

function ConfidenceChip({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  return (
    <Tooltip title={`Confianza: ${pct}%`}>
      <Chip
        label={`${pct}%`}
        color={getConfidenceColor(score)}
        size="small"
        variant="outlined"
        sx={{ height: 18, fontSize: '0.65rem', ml: 0.5 }}
      />
    </Tooltip>
  );
}

function formatTimestamp(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' });
}

interface EditableCellProps {
  value: string | null;
  fieldName: string;
  captureId: string;
  confidenceScore?: number;
  onSave: (captureId: string, fieldName: string, value: string) => void;
  disabled?: boolean;
}

function EditableCell({ value, fieldName, captureId, confidenceScore, onSave, disabled }: EditableCellProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(value || '');

  const handleClick = () => {
    if (disabled) return;
    setEditValue(value || '');
    setIsEditing(true);
  };

  const handleBlur = () => {
    setIsEditing(false);
    if (editValue !== (value || '')) {
      onSave(captureId, fieldName, editValue);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      (e.target as HTMLInputElement).blur();
    } else if (e.key === 'Escape') {
      setEditValue(value || '');
      setIsEditing(false);
    }
  };

  if (isEditing) {
    return (
      <TextField
        value={editValue}
        onChange={e => setEditValue(e.target.value)}
        onBlur={handleBlur}
        onKeyDown={handleKeyDown}
        size="small"
        autoFocus
        variant="standard"
        fullWidth
        sx={{ minWidth: 100 }}
      />
    );
  }

  return (
    <Box
      onClick={handleClick}
      sx={{
        cursor: disabled ? 'default' : 'pointer',
        display: 'flex',
        alignItems: 'center',
        minHeight: 28,
        '&:hover': disabled ? {} : { bgcolor: 'action.hover', borderRadius: 1 },
        px: 0.5,
      }}
    >
      <Typography variant="body2" noWrap sx={{ color: value ? 'text.primary' : 'text.disabled' }}>
        {value || '—'}
      </Typography>
      {confidenceScore !== undefined && <ConfidenceChip score={confidenceScore} />}
    </Box>
  );
}

export default function CardReviewPage() {
  const location = useLocation();
  const {
    captures,
    total,
    statusFilter,
    selectedIds,
    isLoading,
    isProcessing,
    error,
    updateField,
    approveCard,
    rejectCard,
    batchApprove,
    batchReject,
    toggleSelection,
    toggleSelectAll,
    setStatusFilter,
    clearError,
  } = useCardReview();

  const [highlightId, setHighlightId] = useState<string | undefined>(
    (location.state as { highlightCaptureId?: string } | null)?.highlightCaptureId
  );
  const highlightTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Scroll to highlighted row and clear highlight after 3s
  useEffect(() => {
    if (!highlightId || isLoading || captures.length === 0) return;

    // Clear navigation state to prevent re-highlight on refresh
    window.history.replaceState({}, document.title);

    const row = document.querySelector(`[data-capture-id="${highlightId}"]`);
    if (row) {
      row.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    highlightTimerRef.current = setTimeout(() => {
      setHighlightId(undefined);
    }, 3000);

    return () => {
      if (highlightTimerRef.current) clearTimeout(highlightTimerRef.current);
    };
  }, [highlightId, isLoading, captures.length]);

  const [lightboxImage, setLightboxImage] = useState<string | null>(null);
  const [brokenImages, setBrokenImages] = useState<Set<string>>(new Set());

  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [rejectTarget, setRejectTarget] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState('');
  const [snackbar, setSnackbar] = useState<{ message: string; severity: 'success' | 'error' | 'warning' } | null>(null);

  const handleFilterChange = (_: React.MouseEvent<HTMLElement>, value: string | null) => {
    if (value === null) return;
    setStatusFilter(value === 'all' ? null : value as BusinessCardCaptureStatus);
  };

  const handleApprove = async (captureId: string) => {
    try {
      const result = await approveCard(captureId);
      if (result.is_duplicate) {
        setSnackbar({ message: `Duplicado detectado: ${result.duplicate_supplier_name || 'proveedor existente'}`, severity: 'error' });
      } else if (result.email_sent) {
        setSnackbar({ message: `Proveedor "${result.supplier_name}" creado. Correo de seguimiento enviado`, severity: 'success' });
      } else if (result.email_error) {
        setSnackbar({ message: `Proveedor "${result.supplier_name}" creado. Error al enviar correo de seguimiento`, severity: 'warning' });
      } else if (result.no_email_address) {
        setSnackbar({ message: `Proveedor "${result.supplier_name}" creado. No se encontró correo electrónico — seguimiento manual requerido`, severity: 'warning' });
      } else {
        setSnackbar({ message: `Proveedor "${result.supplier_name}" creado exitosamente`, severity: 'success' });
      }
    } catch {
      setSnackbar({ message: 'Error al aprobar la tarjeta', severity: 'error' });
    }
  };

  const openRejectDialog = (captureId: string) => {
    setRejectTarget(captureId);
    setRejectReason('');
    setRejectDialogOpen(true);
  };

  const handleRejectConfirm = async () => {
    if (!rejectTarget) return;
    setRejectDialogOpen(false);
    try {
      await rejectCard(rejectTarget, rejectReason || undefined);
      setSnackbar({ message: 'Tarjeta rechazada', severity: 'success' });
    } catch {
      setSnackbar({ message: 'Error al rechazar la tarjeta', severity: 'error' });
    }
    setRejectTarget(null);
  };

  const handleBatchApprove = async () => {
    const ids = Array.from(selectedIds);
    await batchApprove(ids);
    setSnackbar({ message: `${ids.length} tarjeta(s) procesada(s)`, severity: 'success' });
  };

  const handleBatchReject = async () => {
    setRejectTarget('__batch__');
    setRejectReason('');
    setRejectDialogOpen(true);
  };

  const handleBatchRejectConfirm = async () => {
    setRejectDialogOpen(false);
    const ids = Array.from(selectedIds);
    await batchReject(ids, rejectReason || undefined);
    setSnackbar({ message: `${ids.length} tarjeta(s) rechazada(s)`, severity: 'success' });
    setRejectTarget(null);
  };

  const getConfidenceScores = (capture: typeof captures[0]): Record<string, number> => {
    const raw = capture.extraction_raw_response;
    if (!raw || typeof raw !== 'object') return {};
    const scores = (raw as Record<string, unknown>).confidence_scores;
    if (!scores || typeof scores !== 'object') return {};
    return scores as Record<string, number>;
  };

  const canApprove = (status: BusinessCardCaptureStatus) => status === 'extracted';
  const canReject = (status: BusinessCardCaptureStatus) =>
    status === 'extracted' || status === 'pending' || status === 'failed';
  const isEditable = (status: BusinessCardCaptureStatus) =>
    status !== 'processing';

  const allSelected = captures.length > 0 && selectedIds.size === captures.length;

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom fontWeight="bold">
        Revisión de Tarjetas
      </Typography>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Revise, edite y apruebe o rechace las tarjetas de presentación extraídas.
        Total: {total} captura(s).
      </Typography>

      {/* Status filter */}
      <ToggleButtonGroup
        value={statusFilter || 'all'}
        exclusive
        onChange={handleFilterChange}
        size="small"
        sx={{ mb: 2 }}
      >
        {FILTER_OPTIONS.map(opt => (
          <ToggleButton key={opt.value} value={opt.value}>
            {opt.label}
          </ToggleButton>
        ))}
      </ToggleButtonGroup>

      {/* Batch action bar */}
      {selectedIds.size > 0 && (
        <Paper sx={{ p: 1.5, mb: 2, display: 'flex', alignItems: 'center', gap: 2, bgcolor: 'action.selected' }}>
          <Typography variant="body2" fontWeight="bold">
            {selectedIds.size} seleccionada(s)
          </Typography>
          <Button
            variant="contained"
            color="success"
            size="small"
            startIcon={<CheckCircleIcon />}
            onClick={handleBatchApprove}
            disabled={isProcessing}
          >
            Aprobar Seleccionados
          </Button>
          <Button
            variant="contained"
            color="error"
            size="small"
            startIcon={<CancelIcon />}
            onClick={handleBatchReject}
            disabled={isProcessing}
          >
            Rechazar Seleccionados
          </Button>
          {isProcessing && <CircularProgress size={20} />}
        </Paper>
      )}

      {/* Loading skeleton */}
      {isLoading && (
        <Box>
          {[1, 2, 3].map(i => (
            <Skeleton key={i} variant="rectangular" height={60} sx={{ mb: 1, borderRadius: 1 }} />
          ))}
        </Box>
      )}

      {/* Empty state */}
      {!isLoading && captures.length === 0 && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">
            No se encontraron capturas{statusFilter ? ` con estado "${STATUS_LABELS[statusFilter]}"` : ''}.
          </Typography>
        </Paper>
      )}

      {/* Table */}
      {!isLoading && captures.length > 0 && (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <Checkbox checked={allSelected} onChange={toggleSelectAll} />
                </TableCell>
                <TableCell>Imagen</TableCell>
                <TableCell>Empresa</TableCell>
                <TableCell>Contacto</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Teléfono</TableCell>
                <TableCell>WeChat ID</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Feria</TableCell>
                <TableCell>Fecha</TableCell>
                <TableCell>Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {captures.map(capture => {
                const scores = getConfidenceScores(capture);
                const editable = isEditable(capture.status);
                return (
                  <TableRow
                    key={capture.id}
                    hover
                    selected={selectedIds.has(capture.id)}
                    data-capture-id={capture.id}
                    sx={{
                      ...(capture.id === highlightId && {
                        '@keyframes highlightPulse': {
                          '0%': { backgroundColor: 'rgba(25, 118, 210, 0.15)' },
                          '100%': { backgroundColor: 'transparent' },
                        },
                        animation: 'highlightPulse 3s ease-out',
                      }),
                    }}
                  >
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={selectedIds.has(capture.id)}
                        onChange={() => toggleSelection(capture.id)}
                      />
                    </TableCell>
                    <TableCell>
                      {capture.image_url && !brokenImages.has(capture.image_url) ? (
                        <Box
                          sx={{
                            position: 'relative',
                            width: 80,
                            height: 80,
                            cursor: 'pointer',
                            borderRadius: 1,
                            overflow: 'hidden',
                            '&:hover .lightbox-overlay': { opacity: 1 },
                          }}
                          onClick={(e) => {
                            e.stopPropagation();
                            setLightboxImage(capture.image_url);
                          }}
                        >
                          <Box
                            component="img"
                            src={capture.image_url}
                            alt="Tarjeta de presentación"
                            onError={() => {
                              setBrokenImages(prev => new Set(prev).add(capture.image_url!));
                            }}
                            sx={{ width: 80, height: 80, objectFit: 'cover', borderRadius: 1 }}
                          />
                          <Box
                            className="lightbox-overlay"
                            sx={{
                              position: 'absolute',
                              top: 0,
                              left: 0,
                              width: '100%',
                              height: '100%',
                              bgcolor: 'rgba(0,0,0,0.5)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              opacity: 0,
                              transition: 'opacity 0.2s',
                              borderRadius: 1,
                            }}
                          >
                            <ZoomInIcon sx={{ color: 'white', fontSize: 32 }} />
                          </Box>
                        </Box>
                      ) : (
                        <Box
                          sx={{
                            width: 80,
                            height: 80,
                            bgcolor: 'grey.200',
                            borderRadius: 1,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                          }}
                        >
                          <BrokenImageIcon sx={{ color: 'grey.500', fontSize: 32 }} />
                        </Box>
                      )}
                    </TableCell>
                    <TableCell>
                      <EditableCell
                        value={capture.company_name}
                        fieldName="company_name"
                        captureId={capture.id}
                        confidenceScore={scores.company_name}
                        onSave={updateField}
                        disabled={!editable}
                      />
                    </TableCell>
                    <TableCell>
                      <EditableCell
                        value={capture.contact_name}
                        fieldName="contact_name"
                        captureId={capture.id}
                        confidenceScore={scores.contact_name}
                        onSave={updateField}
                        disabled={!editable}
                      />
                    </TableCell>
                    <TableCell>
                      <EditableCell
                        value={capture.contact_email}
                        fieldName="contact_email"
                        captureId={capture.id}
                        confidenceScore={scores.contact_email}
                        onSave={updateField}
                        disabled={!editable}
                      />
                    </TableCell>
                    <TableCell>
                      <EditableCell
                        value={capture.contact_phone}
                        fieldName="contact_phone"
                        captureId={capture.id}
                        confidenceScore={scores.contact_phone}
                        onSave={updateField}
                        disabled={!editable}
                      />
                    </TableCell>
                    <TableCell>
                      <EditableCell
                        value={capture.contact_wechat}
                        fieldName="contact_wechat"
                        captureId={capture.id}
                        confidenceScore={scores.contact_wechat}
                        onSave={updateField}
                        disabled={!editable}
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={STATUS_LABELS[capture.status]}
                        color={STATUS_COLORS[capture.status]}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" noWrap>
                        {capture.fair_name || '—'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" noWrap>
                        {formatTimestamp(capture.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        {canApprove(capture.status) && (
                          <Tooltip title="Aprobar">
                            <Button
                              variant="outlined"
                              color="success"
                              size="small"
                              startIcon={<CheckCircleIcon />}
                              onClick={() => handleApprove(capture.id)}
                              disabled={isProcessing}
                            >
                              Aprobar
                            </Button>
                          </Tooltip>
                        )}
                        {canReject(capture.status) && (
                          <Tooltip title="Rechazar">
                            <Button
                              variant="outlined"
                              color="error"
                              size="small"
                              startIcon={<CancelIcon />}
                              onClick={() => openRejectDialog(capture.id)}
                              disabled={isProcessing}
                            >
                              Rechazar
                            </Button>
                          </Tooltip>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Lightbox dialog */}
      <Dialog open={!!lightboxImage} onClose={() => setLightboxImage(null)} maxWidth="md" fullWidth>
        <DialogContent
          sx={{
            p: 0,
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            bgcolor: 'black',
            position: 'relative',
            minHeight: 300,
          }}
        >
          <Tooltip title="Cerrar">
            <IconButton
              onClick={() => setLightboxImage(null)}
              sx={{ position: 'absolute', top: 8, right: 8, color: 'white' }}
            >
              <CloseIcon />
            </IconButton>
          </Tooltip>
          <Box
            component="img"
            src={lightboxImage || ''}
            alt="Tarjeta de presentación"
            sx={{ maxWidth: '100%', maxHeight: '80vh', objectFit: 'contain' }}
          />
        </DialogContent>
      </Dialog>

      {/* Reject confirmation dialog */}
      <Dialog open={rejectDialogOpen} onClose={() => setRejectDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Rechazar Tarjeta</DialogTitle>
        <DialogContent>
          <TextField
            label="Motivo del rechazo (opcional)"
            value={rejectReason}
            onChange={e => setRejectReason(e.target.value)}
            fullWidth
            multiline
            rows={3}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRejectDialogOpen(false)}>Cancelar</Button>
          <Button
            variant="contained"
            color="error"
            onClick={rejectTarget === '__batch__' ? handleBatchRejectConfirm : handleRejectConfirm}
          >
            Confirmar Rechazo
          </Button>
        </DialogActions>
      </Dialog>

      {/* Error from hook */}
      <Snackbar open={!!error} autoHideDuration={6000} onClose={clearError}>
        <Alert onClose={clearError} severity="error" variant="filled">
          {error}
        </Alert>
      </Snackbar>

      {/* Success/error snackbar */}
      <Snackbar
        open={!!snackbar}
        autoHideDuration={4000}
        onClose={() => setSnackbar(null)}
      >
        <Alert
          onClose={() => setSnackbar(null)}
          severity={snackbar?.severity || 'success'}
          variant="filled"
        >
          {snackbar?.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
