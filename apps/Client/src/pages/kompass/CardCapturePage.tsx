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
} from '@mui/material';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import { businessCardService } from '@/services/kompassService';
import type { BusinessCardCapture, BusinessCardCaptureStatus } from '@/types/kompass';

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

const CardCapturePage: React.FC = () => {
  const [captures, setCaptures] = useState<BusinessCardCapture[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [fairName, setFairName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
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
      setSuccess('Tarjeta capturada exitosamente');
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
        {captures.map((capture) => (
          <Card key={capture.id} sx={{ display: 'flex', overflow: 'hidden' }}>
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
                <Typography variant="caption" color="text.secondary">
                  {formatTimestamp(capture.created_at)}
                </Typography>
              </Box>
              {capture.company_name && (
                <Typography variant="body2" fontWeight="medium" noWrap>
                  {capture.company_name}
                </Typography>
              )}
              {capture.fair_name && (
                <Typography variant="caption" color="text.secondary" noWrap>
                  {capture.fair_name}
                </Typography>
              )}
              {!capture.company_name && !capture.fair_name && (
                <Typography variant="caption" color="text.secondary" fontStyle="italic">
                  Pendiente de extracción
                </Typography>
              )}
            </Box>
          </Card>
        ))}
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
