import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box,
  Typography,
  TextField,
  Card,
  CardMedia,
  Chip,
  LinearProgress,
  Snackbar,
  Alert,
  Paper,
  Button,
  CircularProgress,
  Tooltip,
} from '@mui/material';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ReplayIcon from '@mui/icons-material/Replay';
import PersonIcon from '@mui/icons-material/Person';
import PhoneIcon from '@mui/icons-material/Phone';
import EmailIcon from '@mui/icons-material/Email';
import BusinessIcon from '@mui/icons-material/Business';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import { businessCardService } from '@/services/kompassService';
import type { BusinessCardCapture, BusinessCardCaptureStatus, SupplierFromCardResult } from '@/types/kompass';

const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024; // 10MB
const ACCEPTED_EXTENSIONS = '.png,.jpg,.jpeg';

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

function formatTimestamp(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60000);

  if (diffMin < 1) return 'Ahora';
  if (diffMin < 60) return `Hace ${diffMin} min`;
  const diffHours = Math.floor(diffMin / 60);
  if (diffHours < 24) return `Hace ${diffHours}h`;
  return date.toLocaleDateString('es-CO', { day: '2-digit', month: 'short', year: 'numeric' });
}

function getConfidenceColor(score: number): 'success' | 'warning' | 'error' {
  if (score >= 0.8) return 'success';
  if (score >= 0.5) return 'warning';
  return 'error';
}

function ConfidenceBadge({ score }: { score: number }) {
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

interface ExtractedFieldProps {
  icon: React.ReactNode;
  value: string | null | undefined;
  confidence?: number;
}

function ExtractedField({ icon, value, confidence }: ExtractedFieldProps) {
  if (!value) return null;
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.25 }}>
      {icon}
      <Typography variant="caption" noWrap sx={{ flex: 1 }}>
        {value}
      </Typography>
      {confidence !== undefined && confidence > 0 && <ConfidenceBadge score={confidence} />}
    </Box>
  );
}

const CardCapturePage: React.FC = () => {
  const [captures, setCaptures] = useState<BusinessCardCapture[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [fairName, setFairName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [extractingIds, setExtractingIds] = useState<Set<string>>(new Set());
  const [creatingSupplierIds, setCreatingSupplierIds] = useState<Set<string>>(new Set());
  const [supplierResults, setSupplierResults] = useState<Record<string, SupplierFromCardResult>>({});
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadCaptures = useCallback(async () => {
    try {
      console.log('INFO [CardCapturePage]: Loading captures');
      const result = await businessCardService.listCaptures();
      setCaptures(result.captures);
    } catch (err) {
      console.error('ERROR [CardCapturePage]: Failed to load captures', err);
    }
  }, []);

  useEffect(() => {
    loadCaptures();
  }, [loadCaptures]);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Reset input so same file can be selected again
    event.target.value = '';

    // Client-side validation
    const ext = file.name.toLowerCase().split('.').pop();
    if (!ext || !['png', 'jpg', 'jpeg'].includes(ext)) {
      setError('Tipo de archivo no permitido. Solo se permiten archivos .png, .jpg, .jpeg');
      return;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      setError('El archivo excede el tamaño máximo de 10MB');
      return;
    }

    // Upload
    setUploading(true);
    setUploadProgress(0);
    setError(null);

    try {
      console.log('INFO [CardCapturePage]: Uploading file', file.name);
      const capture = await businessCardService.uploadCard(
        file,
        fairName || undefined,
        undefined,
        (percent) => setUploadProgress(percent)
      );

      setCaptures((prev) => [capture, ...prev]);
      const statusMsg = capture.status === 'extracted'
        ? 'Tarjeta capturada y datos extraídos'
        : 'Tarjeta capturada exitosamente';
      setSuccess(statusMsg);
      console.log('INFO [CardCapturePage]: Upload complete', capture.id);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al subir la imagen';
      setError(message);
      console.error('ERROR [CardCapturePage]: Upload failed', err);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleExtract = async (captureId: string) => {
    setExtractingIds((prev) => new Set(prev).add(captureId));
    try {
      console.log('INFO [CardCapturePage]: Triggering extraction for', captureId);
      const updated = await businessCardService.triggerExtraction(captureId);
      setCaptures((prev) =>
        prev.map((c) => (c.id === captureId ? updated : c))
      );
      setSuccess('Datos extraídos exitosamente');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al extraer datos';
      setError(message);
      console.error('ERROR [CardCapturePage]: Extraction failed', err);
    } finally {
      setExtractingIds((prev) => {
        const next = new Set(prev);
        next.delete(captureId);
        return next;
      });
    }
  };

  const handleCreateSupplier = async (captureId: string) => {
    setCreatingSupplierIds((prev) => new Set(prev).add(captureId));
    try {
      console.log('INFO [CardCapturePage]: Creating supplier from card', captureId);
      const result = await businessCardService.createSupplierFromCard(captureId);
      setSupplierResults((prev) => ({ ...prev, [captureId]: result }));

      if (result.success) {
        setCaptures((prev) =>
          prev.map((c) =>
            c.id === captureId
              ? { ...c, status: 'confirmed' as BusinessCardCaptureStatus, supplier_id: result.supplier_id ?? null }
              : c
          )
        );
        setSuccess(`Proveedor creado: ${result.supplier_name}`);
      } else if (result.is_duplicate) {
        setCaptures((prev) =>
          prev.map((c) =>
            c.id === captureId
              ? { ...c, status: 'rejected' as BusinessCardCaptureStatus }
              : c
          )
        );
        setError(`Proveedor duplicado: ${result.duplicate_supplier_name}`);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al crear proveedor';
      setError(message);
      console.error('ERROR [CardCapturePage]: Create supplier failed', err);
    } finally {
      setCreatingSupplierIds((prev) => {
        const next = new Set(prev);
        next.delete(captureId);
        return next;
      });
    }
  };

  const getConfidenceScores = (capture: BusinessCardCapture): Record<string, number> => {
    const raw = capture.extraction_raw_response;
    if (!raw || typeof raw !== 'object') return {};
    const scores = (raw as Record<string, unknown>).confidence_scores;
    if (!scores || typeof scores !== 'object') return {};
    return scores as Record<string, number>;
  };

  const isExtracting = (captureId: string) => extractingIds.has(captureId);

  return (
    <Box sx={{ p: { xs: 2, sm: 3 }, maxWidth: 800, mx: 'auto' }}>
      {/* Page Title */}
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Captura de Tarjetas
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Fotografía tarjetas de presentación de proveedores en ferias comerciales
      </Typography>

      {/* Fair Name Field */}
      <TextField
        fullWidth
        label="Nombre de la Feria"
        placeholder="Ej: Canton Fair 2026"
        value={fairName}
        onChange={(e) => setFairName(e.target.value)}
        size="small"
        sx={{ mb: 2 }}
      />

      {/* Upload Button */}
      <Paper
        variant="outlined"
        sx={{
          p: 3,
          mb: 3,
          textAlign: 'center',
          borderStyle: 'dashed',
          borderColor: 'primary.main',
          backgroundColor: 'action.hover',
          cursor: uploading ? 'default' : 'pointer',
        }}
        onClick={uploading ? undefined : handleUploadClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_EXTENSIONS}
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
        <CameraAltIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
        <Typography variant="h6" color="primary">
          {uploading ? 'Subiendo...' : 'Tomar Foto o Seleccionar Imagen'}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          PNG, JPG — Máximo 10MB
        </Typography>
      </Paper>

      {/* Upload Progress */}
      {uploading && (
        <Box sx={{ mb: 3 }}>
          <LinearProgress variant="determinate" value={uploadProgress} sx={{ height: 8, borderRadius: 4 }} />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block', textAlign: 'center' }}>
            {uploadProgress}%
          </Typography>
        </Box>
      )}

      {/* Recent Captures */}
      <Typography variant="h6" sx={{ mb: 2 }}>
        Capturas Recientes
      </Typography>

      {captures.length === 0 && !uploading && (
        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
          No hay capturas aún. Toma una foto de una tarjeta para comenzar.
        </Typography>
      )}

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {captures.map((capture) => {
          const scores = getConfidenceScores(capture);
          const extracting = isExtracting(capture.id);
          const showSpinner = capture.status === 'processing' || extracting;
          const showExtracted = capture.status === 'extracted';
          const showExtractButton = capture.status === 'pending' && !extracting;
          const showRetryButton = capture.status === 'failed' && !extracting;

          return (
            <Card key={capture.id} sx={{ overflow: 'hidden' }}>
              <Box sx={{ display: 'flex' }}>
                <CardMedia
                  component="img"
                  sx={{ width: 100, height: 100, objectFit: 'cover', flexShrink: 0 }}
                  image={capture.image_url}
                  alt="Tarjeta de presentación"
                />
                <Box sx={{ p: 1.5, flex: 1, minWidth: 0 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                    <Chip
                      label={STATUS_LABELS[capture.status]}
                      color={STATUS_COLORS[capture.status]}
                      size="small"
                    />
                    {showSpinner && <CircularProgress size={16} />}
                    <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
                      {formatTimestamp(capture.created_at)}
                    </Typography>
                  </Box>

                  {/* Extracted fields with confidence */}
                  {showExtracted && (
                    <Box sx={{ mt: 0.5 }}>
                      <ExtractedField
                        icon={<BusinessIcon sx={{ fontSize: 14, color: 'text.secondary' }} />}
                        value={capture.company_name}
                        confidence={scores.company_name}
                      />
                      <ExtractedField
                        icon={<PersonIcon sx={{ fontSize: 14, color: 'text.secondary' }} />}
                        value={capture.contact_name}
                        confidence={scores.contact_name}
                      />
                      <ExtractedField
                        icon={<PhoneIcon sx={{ fontSize: 14, color: 'text.secondary' }} />}
                        value={capture.contact_phone}
                        confidence={scores.contact_phone}
                      />
                      <ExtractedField
                        icon={<EmailIcon sx={{ fontSize: 14, color: 'text.secondary' }} />}
                        value={capture.contact_email}
                        confidence={scores.contact_email}
                      />
                      <ExtractedField
                        icon={<LocationOnIcon sx={{ fontSize: 14, color: 'text.secondary' }} />}
                        value={capture.address}
                        confidence={scores.address}
                      />
                    </Box>
                  )}

                  {/* Pending state — no extracted data yet */}
                  {!showExtracted && !showSpinner && capture.fair_name && (
                    <Typography variant="caption" color="text.secondary" noWrap>
                      {capture.fair_name}
                    </Typography>
                  )}
                  {!showExtracted && !showSpinner && !capture.fair_name && capture.status === 'pending' && (
                    <Typography variant="caption" color="text.secondary" fontStyle="italic">
                      Pendiente de extracción
                    </Typography>
                  )}

                  {/* Processing spinner text */}
                  {showSpinner && (
                    <Typography variant="caption" color="text.secondary" fontStyle="italic">
                      Extrayendo datos con IA...
                    </Typography>
                  )}

                  {/* Failed state — show error */}
                  {capture.status === 'failed' && !extracting && (
                    <Typography variant="caption" color="error">
                      Error en la extracción
                    </Typography>
                  )}

                  {/* Action buttons */}
                  <Box sx={{ mt: 0.5, display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
                    {showExtractButton && (
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<SmartToyIcon />}
                        onClick={() => handleExtract(capture.id)}
                      >
                        Extraer
                      </Button>
                    )}
                    {showRetryButton && (
                      <Button
                        size="small"
                        variant="outlined"
                        color="warning"
                        startIcon={<ReplayIcon />}
                        onClick={() => handleExtract(capture.id)}
                      >
                        Reintentar
                      </Button>
                    )}
                    {capture.status === 'extracted' && !capture.supplier_id && (
                      <Button
                        size="small"
                        variant="contained"
                        color="primary"
                        startIcon={creatingSupplierIds.has(capture.id) ? <CircularProgress size={16} /> : <PersonAddIcon />}
                        disabled={creatingSupplierIds.has(capture.id)}
                        onClick={() => handleCreateSupplier(capture.id)}
                      >
                        {creatingSupplierIds.has(capture.id) ? 'Creando...' : 'Crear Proveedor'}
                      </Button>
                    )}
                    {capture.status === 'confirmed' && capture.supplier_id && (
                      <Chip
                        icon={<CheckCircleIcon />}
                        label="Proveedor vinculado"
                        color="primary"
                        size="small"
                        variant="outlined"
                      />
                    )}
                  </Box>

                  {/* Supplier creation result messages */}
                  {supplierResults[capture.id]?.is_duplicate && (
                    <Alert severity="warning" icon={<WarningIcon />} sx={{ mt: 0.5, py: 0, fontSize: '0.75rem' }}>
                      Duplicado: {supplierResults[capture.id].duplicate_supplier_name}
                    </Alert>
                  )}
                  {supplierResults[capture.id]?.success && (
                    <Alert severity="success" icon={<CheckCircleIcon />} sx={{ mt: 0.5, py: 0, fontSize: '0.75rem' }}>
                      Proveedor creado: {supplierResults[capture.id].supplier_name}
                    </Alert>
                  )}
                </Box>
              </Box>
            </Card>
          );
        })}
      </Box>

      {/* Snackbars */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setError(null)} severity="error" variant="filled">
          {error}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!success}
        autoHideDuration={4000}
        onClose={() => setSuccess(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setSuccess(null)} severity="success" variant="filled">
          {success}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default CardCapturePage;
