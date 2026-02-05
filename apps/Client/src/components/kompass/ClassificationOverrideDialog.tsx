import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Box,
  Alert,
  CircularProgress,
  Typography,
} from '@mui/material';
import type { ClassificationGrade, ClassificationOverride } from '@/types/kompass';
import ClassificationBadge from './ClassificationBadge';

interface ClassificationOverrideDialogProps {
  open: boolean;
  onClose: () => void;
  onConfirm: (data: ClassificationOverride) => Promise<void>;
  currentClassification: ClassificationGrade | null;
  supplierName: string;
}

interface FormData {
  classification: ClassificationGrade;
  notes: string;
}

const gradeOptions: { value: ClassificationGrade; label: string }[] = [
  { value: 'A', label: 'Grade A - Excellent' },
  { value: 'B', label: 'Grade B - Acceptable' },
  { value: 'C', label: 'Grade C - Needs Improvement' },
];

const ClassificationOverrideDialog: React.FC<ClassificationOverrideDialogProps> = ({
  open,
  onClose,
  onConfirm,
  currentClassification,
  supplierName,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<FormData>({
    defaultValues: {
      classification: currentClassification || 'B',
      notes: '',
    },
  });

  const notesValue = watch('notes');
  const notesLength = notesValue?.length || 0;
  const isNotesValid = notesLength >= 10;

  React.useEffect(() => {
    if (open) {
      setError(null);
      reset({
        classification: currentClassification || 'B',
        notes: '',
      });
    }
  }, [open, currentClassification, reset]);

  const onSubmit = async (data: FormData) => {
    if (!isNotesValid) {
      setError('Notes must be at least 10 characters');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log(`INFO [ClassificationOverrideDialog]: Overriding classification to ${data.classification}`);
      await onConfirm({
        classification: data.classification,
        notes: data.notes,
      });
      onClose();
    } catch (err) {
      console.log('ERROR [ClassificationOverrideDialog]: Failed to override classification', err);
      setError(err instanceof Error ? err.message : 'Failed to override classification');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Override Classification</DialogTitle>
      <form onSubmit={handleSubmit(onSubmit)}>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Supplier: <strong>{supplierName}</strong>
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Current Classification:
              </Typography>
              <ClassificationBadge grade={currentClassification} size="small" />
            </Box>
          </Box>

          <TextField
            fullWidth
            select
            label="New Classification"
            {...register('classification', { required: 'Classification is required' })}
            error={!!errors.classification}
            helperText={errors.classification?.message}
            disabled={loading}
            sx={{ mb: 2 }}
          >
            {gradeOptions.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            fullWidth
            multiline
            rows={4}
            label="Override Notes"
            placeholder="Explain the reason for this override (minimum 10 characters)..."
            {...register('notes', {
              required: 'Notes are required',
              minLength: {
                value: 10,
                message: 'Notes must be at least 10 characters',
              },
            })}
            error={!!errors.notes}
            helperText={
              errors.notes?.message ||
              `${notesLength}/10 characters minimum${notesLength >= 10 ? ' - Valid' : ''}`
            }
            disabled={loading}
          />

          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              Overriding the AI classification will mark this as a manual override. This action can
              be revised later but will be logged for audit purposes.
            </Typography>
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Box sx={{ position: 'relative' }}>
            <Button
              type="submit"
              variant="contained"
              disabled={loading || !isNotesValid}
            >
              Confirm Override
            </Button>
            {loading && (
              <CircularProgress
                size={24}
                sx={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  marginTop: '-12px',
                  marginLeft: '-12px',
                }}
              />
            )}
          </Box>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default ClassificationOverrideDialog;
