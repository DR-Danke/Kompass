import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Paper,
  Snackbar,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import RestoreIcon from '@mui/icons-material/Restore';
import type { OutreachTemplate, OutreachTemplateUpdate } from '@/types/kompass';
import { supplierService } from '@/services/kompassService';

const SAMPLE_DATA: Record<string, string> = {
  '{contact_name}': 'Juan Pérez',
  '{company_name}': 'Empresa ABC',
  '{fair_name}': 'Canton Fair 2026',
  '{sender_name}': 'Kompass',
};

function renderPreview(text: string): string {
  let rendered = text;
  for (const [placeholder, value] of Object.entries(SAMPLE_DATA)) {
    rendered = rendered.split(placeholder).join(value);
  }
  return rendered;
}

const SettingsPage: React.FC = () => {
  const [templates, setTemplates] = useState<OutreachTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<OutreachTemplate | null>(null);
  const [editName, setEditName] = useState('');
  const [editSubject, setEditSubject] = useState('');
  const [editBody, setEditBody] = useState('');
  const [saving, setSaving] = useState(false);
  const [resetConfirmOpen, setResetConfirmOpen] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });
  const bodyRef = useRef<HTMLTextAreaElement>(null);

  const fetchTemplates = useCallback(async () => {
    try {
      setLoading(true);
      const data = await supplierService.getOutreachTemplates(false);
      setTemplates(data);
    } catch (err) {
      console.error('ERROR [SettingsPage]: Failed to fetch templates', err);
      setSnackbar({ open: true, message: 'Error al cargar las plantillas', severity: 'error' });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTemplates();
  }, [fetchTemplates]);

  const handleOpenEdit = (template: OutreachTemplate) => {
    setSelectedTemplate(template);
    setEditName(template.name);
    setEditSubject(template.subject);
    setEditBody(template.body);
    setEditDialogOpen(true);
  };

  const handleCloseEdit = () => {
    setEditDialogOpen(false);
    setSelectedTemplate(null);
  };

  const handleSave = async () => {
    if (!selectedTemplate) return;
    setSaving(true);
    try {
      const updates: OutreachTemplateUpdate = {};
      if (editName !== selectedTemplate.name) updates.name = editName;
      if (editSubject !== selectedTemplate.subject) updates.subject = editSubject;
      if (editBody !== selectedTemplate.body) updates.body = editBody;

      if (Object.keys(updates).length === 0) {
        handleCloseEdit();
        return;
      }

      await supplierService.updateTemplate(selectedTemplate.id, updates);
      setSnackbar({ open: true, message: 'Plantilla actualizada exitosamente', severity: 'success' });
      handleCloseEdit();
      fetchTemplates();
    } catch (err) {
      console.error('ERROR [SettingsPage]: Failed to save template', err);
      setSnackbar({ open: true, message: 'Error al guardar la plantilla', severity: 'error' });
    } finally {
      setSaving(false);
    }
  };

  const handleToggleActive = async (template: OutreachTemplate) => {
    try {
      await supplierService.updateTemplate(template.id, { is_active: !template.is_active });
      setSnackbar({
        open: true,
        message: template.is_active ? 'Plantilla desactivada' : 'Plantilla activada',
        severity: 'success',
      });
      fetchTemplates();
    } catch (err) {
      console.error('ERROR [SettingsPage]: Failed to toggle template', err);
      setSnackbar({ open: true, message: 'Error al cambiar estado de la plantilla', severity: 'error' });
    }
  };

  const handleResetConfirm = () => {
    setResetConfirmOpen(true);
  };

  const handleResetExecute = async () => {
    if (!selectedTemplate) return;
    setResetConfirmOpen(false);
    setSaving(true);
    try {
      const resetTemplate = await supplierService.resetTemplate(selectedTemplate.id);
      setEditName(resetTemplate.name);
      setEditSubject(resetTemplate.subject);
      setEditBody(resetTemplate.body);
      setSelectedTemplate(resetTemplate);
      setSnackbar({ open: true, message: 'Plantilla restaurada a valores originales', severity: 'success' });
      fetchTemplates();
    } catch (err) {
      console.error('ERROR [SettingsPage]: Failed to reset template', err);
      setSnackbar({ open: true, message: 'Error al restaurar la plantilla', severity: 'error' });
    } finally {
      setSaving(false);
    }
  };

  const handleInsertPlaceholder = (placeholder: string) => {
    const textarea = bodyRef.current;
    if (textarea) {
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newBody = editBody.substring(0, start) + placeholder + editBody.substring(end);
      setEditBody(newBody);
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(start + placeholder.length, start + placeholder.length);
      }, 0);
    } else {
      setEditBody(editBody + placeholder);
    }
  };

  const unrecognizedPlaceholders = editBody
    .match(/\{[^}]+\}/g)
    ?.filter((p) => !Object.keys(SAMPLE_DATA).includes(p)) || [];

  return (
    <Box sx={{ p: 3, maxWidth: 1000, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Configuración
      </Typography>

      <Paper sx={{ p: 3, mt: 2 }}>
        <Typography variant="h6" gutterBottom>
          Plantillas de Seguimiento
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Edite las plantillas de email utilizadas para el seguimiento de proveedores.
        </Typography>

        {loading ? (
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        ) : (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Nombre</TableCell>
                  <TableCell>Clave</TableCell>
                  <TableCell>Asunto</TableCell>
                  <TableCell align="center">Activa</TableCell>
                  <TableCell align="center">Acciones</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {templates.map((tmpl) => (
                  <TableRow
                    key={tmpl.id}
                    hover
                    sx={{ cursor: 'pointer' }}
                    onClick={() => handleOpenEdit(tmpl)}
                  >
                    <TableCell>
                      <Typography variant="body2" fontWeight={500}>
                        {tmpl.name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={tmpl.key} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary" noWrap sx={{ maxWidth: 300 }}>
                        {tmpl.subject}
                      </Typography>
                    </TableCell>
                    <TableCell align="center" onClick={(e) => e.stopPropagation()}>
                      <Switch
                        checked={tmpl.is_active}
                        onChange={() => handleToggleActive(tmpl)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="center" onClick={(e) => e.stopPropagation()}>
                      <Button
                        size="small"
                        startIcon={<EditIcon />}
                        onClick={() => handleOpenEdit(tmpl)}
                      >
                        Editar
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>

      {/* Edit Template Dialog */}
      <Dialog open={editDialogOpen} onClose={handleCloseEdit} maxWidth="md" fullWidth>
        <DialogTitle>Editar Plantilla</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
            <TextField
              label="Nombre"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              fullWidth
              size="small"
            />
            <TextField
              label="Asunto"
              value={editSubject}
              onChange={(e) => setEditSubject(e.target.value)}
              fullWidth
              size="small"
            />
            <TextField
              label="Cuerpo del Mensaje"
              value={editBody}
              onChange={(e) => setEditBody(e.target.value)}
              fullWidth
              multiline
              rows={10}
              inputRef={bodyRef}
            />
            {unrecognizedPlaceholders.length > 0 && (
              <Alert severity="warning" sx={{ py: 0 }}>
                Variables no reconocidas: {unrecognizedPlaceholders.join(', ')}
              </Alert>
            )}

            <Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                Variables Disponibles
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {selectedTemplate?.available_placeholders.map((placeholder) => (
                  <Chip
                    key={placeholder}
                    label={placeholder}
                    size="small"
                    color="primary"
                    variant="outlined"
                    onClick={() => handleInsertPlaceholder(placeholder)}
                    sx={{ cursor: 'pointer' }}
                  />
                ))}
              </Box>
            </Box>

            <Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                Vista Previa
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50', maxHeight: 250, overflow: 'auto' }}>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                  Asunto: {renderPreview(editSubject)}
                </Typography>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-line', fontSize: '0.85rem' }}>
                  {renderPreview(editBody)}
                </Typography>
              </Paper>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2, justifyContent: 'space-between' }}>
          <Button
            startIcon={<RestoreIcon />}
            onClick={handleResetConfirm}
            color="warning"
            disabled={saving}
          >
            Restaurar Original
          </Button>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button onClick={handleCloseEdit} disabled={saving}>
              Cancelar
            </Button>
            <Button
              onClick={handleSave}
              variant="contained"
              disabled={saving || !editName.trim() || !editSubject.trim() || !editBody.trim()}
            >
              {saving ? <CircularProgress size={20} /> : 'Guardar'}
            </Button>
          </Box>
        </DialogActions>
      </Dialog>

      {/* Reset Confirmation Dialog */}
      <Dialog open={resetConfirmOpen} onClose={() => setResetConfirmOpen(false)}>
        <DialogTitle>Confirmar Restauración</DialogTitle>
        <DialogContent>
          <DialogContentText>
            ¿Está seguro de que desea restaurar esta plantilla a su contenido original?
            Los cambios actuales se perderán.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResetConfirmOpen(false)}>Cancelar</Button>
          <Button onClick={handleResetExecute} color="warning" variant="contained">
            Restaurar
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
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

export default SettingsPage;
