import React, { useState, useRef, useCallback } from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Alert,
  Button,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import { auditService } from '@/services/kompassService';
import type { SupplierAuditResponse } from '@/types/kompass';

interface AuditUploaderProps {
  supplierId: string;
  onUploadComplete: (audit: SupplierAuditResponse) => void;
  onError?: (error: string) => void;
  disabled?: boolean;
}

type UploadState = 'idle' | 'dragging' | 'uploading' | 'processing' | 'complete' | 'error';

const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25MB

const AuditUploader: React.FC<AuditUploaderProps> = ({
  supplierId,
  onUploadComplete,
  onError,
  disabled = false,
}) => {
  const [uploadState, setUploadState] = useState<UploadState>('idle');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const resetState = () => {
    setUploadState('idle');
    setUploadProgress(0);
    setErrorMessage(null);
  };

  const validateFile = (file: File): string | null => {
    if (file.type !== 'application/pdf') {
      return 'Only PDF files are accepted';
    }
    if (file.size > MAX_FILE_SIZE) {
      return `File size exceeds maximum of 25MB (${(file.size / 1024 / 1024).toFixed(1)}MB)`;
    }
    return null;
  };

  const handleUpload = useCallback(
    async (file: File) => {
      const validationError = validateFile(file);
      if (validationError) {
        setErrorMessage(validationError);
        setUploadState('error');
        onError?.(validationError);
        return;
      }

      setErrorMessage(null);
      setUploadState('uploading');
      setUploadProgress(0);

      try {
        console.log(`INFO [AuditUploader]: Uploading file ${file.name} for supplier ${supplierId}`);
        const audit = await auditService.upload(supplierId, file, 'factory_audit', (percent) => {
          setUploadProgress(percent);
          if (percent === 100) {
            setUploadState('processing');
          }
        });

        setUploadState('complete');
        console.log(`INFO [AuditUploader]: Upload complete, audit ID: ${audit.id}`);
        onUploadComplete(audit);

        // Reset after showing success briefly
        setTimeout(resetState, 2000);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Upload failed';
        console.log(`ERROR [AuditUploader]: Upload failed - ${message}`);
        setErrorMessage(message);
        setUploadState('error');
        onError?.(message);
      }
    },
    [supplierId, onUploadComplete, onError]
  );

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled && uploadState === 'idle') {
      setUploadState('dragging');
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (uploadState === 'dragging') {
      setUploadState('idle');
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (disabled) return;

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleUpload(files[0]);
    } else {
      setUploadState('idle');
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleUpload(files[0]);
    }
    // Reset input value to allow re-uploading same file
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleClick = () => {
    if (!disabled && uploadState === 'idle') {
      fileInputRef.current?.click();
    }
  };

  const getBorderColor = () => {
    switch (uploadState) {
      case 'dragging':
        return 'primary.main';
      case 'uploading':
      case 'processing':
        return 'info.main';
      case 'complete':
        return 'success.main';
      case 'error':
        return 'error.main';
      default:
        return 'grey.400';
    }
  };

  const getBackgroundColor = () => {
    switch (uploadState) {
      case 'dragging':
        return 'action.hover';
      case 'complete':
        return 'success.light';
      case 'error':
        return 'error.light';
      default:
        return 'background.paper';
    }
  };

  return (
    <Box>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        accept="application/pdf"
        style={{ display: 'none' }}
        disabled={disabled}
      />
      <Box
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        sx={{
          border: '2px dashed',
          borderColor: getBorderColor(),
          borderRadius: 2,
          p: 3,
          textAlign: 'center',
          cursor: disabled || uploadState !== 'idle' ? 'default' : 'pointer',
          backgroundColor: getBackgroundColor(),
          transition: 'all 0.2s ease',
          opacity: disabled ? 0.5 : 1,
          '&:hover': {
            borderColor: disabled || uploadState !== 'idle' ? undefined : 'primary.main',
            backgroundColor: disabled || uploadState !== 'idle' ? undefined : 'action.hover',
          },
        }}
      >
        {uploadState === 'idle' && (
          <>
            <CloudUploadIcon sx={{ fontSize: 48, color: 'grey.500', mb: 1 }} />
            <Typography variant="body1" color="text.secondary">
              Drag and drop a PDF file here
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              or click to browse (max 25MB)
            </Typography>
          </>
        )}

        {uploadState === 'dragging' && (
          <>
            <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
            <Typography variant="body1" color="primary">
              Drop file to upload
            </Typography>
          </>
        )}

        {uploadState === 'uploading' && (
          <>
            <CloudUploadIcon sx={{ fontSize: 48, color: 'info.main', mb: 1 }} />
            <Typography variant="body1" color="info.main" sx={{ mb: 1 }}>
              Uploading... {uploadProgress}%
            </Typography>
            <LinearProgress variant="determinate" value={uploadProgress} sx={{ width: '100%' }} />
          </>
        )}

        {uploadState === 'processing' && (
          <>
            <CloudUploadIcon sx={{ fontSize: 48, color: 'info.main', mb: 1 }} />
            <Typography variant="body1" color="info.main" sx={{ mb: 1 }}>
              Processing...
            </Typography>
            <LinearProgress sx={{ width: '100%' }} />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Extracting audit information
            </Typography>
          </>
        )}

        {uploadState === 'complete' && (
          <>
            <CheckCircleIcon sx={{ fontSize: 48, color: 'success.main', mb: 1 }} />
            <Typography variant="body1" color="success.main">
              Upload complete!
            </Typography>
          </>
        )}

        {uploadState === 'error' && (
          <>
            <ErrorIcon sx={{ fontSize: 48, color: 'error.main', mb: 1 }} />
            <Typography variant="body1" color="error.main">
              Upload failed
            </Typography>
          </>
        )}
      </Box>

      {errorMessage && (
        <Alert
          severity="error"
          sx={{ mt: 2 }}
          action={
            <Button color="inherit" size="small" onClick={resetState}>
              Retry
            </Button>
          }
        >
          {errorMessage}
        </Alert>
      )}
    </Box>
  );
};

export default AuditUploader;
