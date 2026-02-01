import React, { useState, useCallback, useEffect, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Button,
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  List,
  ListItem,
  ListItemText,
  Snackbar,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import { useExtractionJob } from '@/hooks/useExtractionJob';
import { supplierService, productService, extractionService } from '@/services/kompassService';
import { ExtractedProductTable } from '@/components/kompass/ExtractedProductTable';
import type { ExtractedProduct, SupplierResponse, ProductResponse } from '@/types/kompass';

const STEPS = ['Upload Files', 'Processing', 'Review Products', 'Confirm Import'];

const ALLOWED_EXTENSIONS = ['.pdf', '.xlsx', '.xls', '.png', '.jpg', '.jpeg'];
const MAX_FILE_SIZE_MB = 20;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

const DRAFT_STORAGE_KEY = 'kompass_import_wizard_draft';

interface ValidationError {
  field: string;
  message: string;
}

interface ProductValidationErrors {
  [productIndex: number]: ValidationError[];
}

interface DraftData {
  filesMetadata: Array<{ name: string; size: number; type: string }>;
  extractedProducts: ExtractedProduct[];
  selectedIndices: number[];
  supplierId: string | null;
}

function validateFileType(file: File): boolean {
  const extension = '.' + file.name.split('.').pop()?.toLowerCase();
  return ALLOWED_EXTENSIONS.includes(extension);
}

function validateFileSize(file: File): boolean {
  return file.size <= MAX_FILE_SIZE_BYTES;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function validateProducts(
  products: ExtractedProduct[],
  selectedIndices: Set<number>
): ProductValidationErrors {
  const errors: ProductValidationErrors = {};

  products.forEach((product, index) => {
    if (!selectedIndices.has(index)) return;

    const productErrors: ValidationError[] = [];

    if (!product.name || product.name.trim() === '') {
      productErrors.push({ field: 'name', message: 'Name is required' });
    }

    const price = typeof product.price_fob_usd === 'string'
      ? parseFloat(product.price_fob_usd)
      : product.price_fob_usd;
    if (price !== null && price !== undefined && price < 0) {
      productErrors.push({ field: 'price_fob_usd', message: 'Price must be >= 0' });
    }

    if (product.moq !== null && product.moq !== undefined && product.moq < 1) {
      productErrors.push({ field: 'moq', message: 'MOQ must be >= 1' });
    }

    if (productErrors.length > 0) {
      errors[index] = productErrors;
    }
  });

  return errors;
}

export default function ImportWizardPage() {
  const [activeStep, setActiveStep] = useState(0);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [fileErrors, setFileErrors] = useState<string[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
  const [draftDialogOpen, setDraftDialogOpen] = useState(false);
  const [successDialogOpen, setSuccessDialogOpen] = useState(false);
  const [importResult, setImportResult] = useState<{ imported: number; failed: number } | null>(null);

  // Extraction job state
  const {
    jobId,
    status,
    progress,
    products: extractedProducts,
    errors: extractionErrors,
    totalFiles,
    processedFiles,
    startJob,
    resetJob,
    uploadError,
  } = useExtractionJob();

  // Editable products state
  const [editedProducts, setEditedProducts] = useState<ExtractedProduct[]>([]);
  const [selectedIndices, setSelectedIndices] = useState<Set<number>>(new Set());
  const [validationErrors, setValidationErrors] = useState<ProductValidationErrors>({});

  // Confirm step state
  const [suppliers, setSuppliers] = useState<SupplierResponse[]>([]);
  const [selectedSupplierId, setSelectedSupplierId] = useState<string>('');
  const [existingProducts, setExistingProducts] = useState<ProductResponse[]>([]);
  const [duplicateSkus, setDuplicateSkus] = useState<string[]>([]);
  const [isImporting, setIsImporting] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState<string | null>(null);

  // Check for draft on mount
  useEffect(() => {
    const draft = localStorage.getItem(DRAFT_STORAGE_KEY);
    if (draft) {
      setDraftDialogOpen(true);
    }
  }, []);

  // Load suppliers when reaching confirm step
  useEffect(() => {
    if (activeStep === 3) {
      supplierService.list(1, 100).then((res) => {
        setSuppliers(res.items);
      });
      productService.list(1, 1000).then((res) => {
        setExistingProducts(res.items);
      });
    }
  }, [activeStep]);

  // Check for duplicate SKUs
  useEffect(() => {
    if (existingProducts.length > 0 && editedProducts.length > 0) {
      const existingSkuSet = new Set(existingProducts.map((p) => p.sku.toLowerCase()));
      const duplicates = editedProducts
        .filter((p, i) => selectedIndices.has(i) && p.sku)
        .filter((p) => existingSkuSet.has(p.sku!.toLowerCase()))
        .map((p) => p.sku!);
      setDuplicateSkus(duplicates);
    }
  }, [existingProducts, editedProducts, selectedIndices]);

  // Sync extracted products to editable products when extraction completes
  useEffect(() => {
    if (status === 'completed' && extractedProducts.length > 0) {
      setEditedProducts([...extractedProducts]);
      setSelectedIndices(new Set(extractedProducts.map((_, i) => i)));
    }
  }, [status, extractedProducts]);

  // Auto-advance to review when processing completes
  useEffect(() => {
    if (status === 'completed' && activeStep === 1) {
      setActiveStep(2);
    }
  }, [status, activeStep]);

  // Validate products when selection or products change
  useEffect(() => {
    const errors = validateProducts(editedProducts, selectedIndices);
    setValidationErrors(errors);
  }, [editedProducts, selectedIndices]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    addFiles(files);
  }, []);

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      addFiles(files);
    }
    e.target.value = '';
  }, []);

  const addFiles = useCallback((files: File[]) => {
    const errors: string[] = [];
    const validFiles: File[] = [];

    files.forEach((file) => {
      if (!validateFileType(file)) {
        errors.push(`${file.name}: Invalid file type. Allowed: ${ALLOWED_EXTENSIONS.join(', ')}`);
      } else if (!validateFileSize(file)) {
        errors.push(`${file.name}: File too large. Maximum size: ${MAX_FILE_SIZE_MB}MB`);
      } else {
        validFiles.push(file);
      }
    });

    setFileErrors(errors);
    setSelectedFiles((prev) => [...prev, ...validFiles]);
  }, []);

  const handleRemoveFile = useCallback((index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const handleNext = useCallback(async () => {
    if (activeStep === 0 && selectedFiles.length > 0) {
      setActiveStep(1);
      const dt = new DataTransfer();
      selectedFiles.forEach((f) => dt.items.add(f));
      await startJob(dt.files);
    } else if (activeStep === 2) {
      setActiveStep(3);
    }
  }, [activeStep, selectedFiles, startJob]);

  const handleBack = useCallback(() => {
    if (activeStep === 2) {
      setActiveStep(0);
      resetJob();
      setSelectedFiles([]);
      setEditedProducts([]);
      setSelectedIndices(new Set());
    } else if (activeStep === 3) {
      setActiveStep(2);
    }
  }, [activeStep, resetJob]);

  const handleProductChange = useCallback(
    (index: number, field: keyof ExtractedProduct, value: string | number | null) => {
      setEditedProducts((prev) => {
        const updated = [...prev];
        updated[index] = { ...updated[index], [field]: value };
        return updated;
      });
    },
    []
  );

  const handleProductSelect = useCallback((index: number, selected: boolean) => {
    setSelectedIndices((prev) => {
      const next = new Set(prev);
      if (selected) {
        next.add(index);
      } else {
        next.delete(index);
      }
      return next;
    });
  }, []);

  const handleSelectAll = useCallback(
    (selected: boolean) => {
      if (selected) {
        setSelectedIndices(new Set(editedProducts.map((_, i) => i)));
      } else {
        setSelectedIndices(new Set());
      }
    },
    [editedProducts]
  );

  const handleImport = useCallback(async () => {
    if (!jobId || !selectedSupplierId) return;

    setIsImporting(true);
    try {
      const productIndices = Array.from(selectedIndices);
      const response = await extractionService.confirmImport({
        job_id: jobId,
        product_indices: productIndices,
        supplier_id: selectedSupplierId,
      });

      setImportResult({
        imported: response.imported_count,
        failed: response.failed_count,
      });
      setSuccessDialogOpen(true);

      // Clear draft on success
      localStorage.removeItem(DRAFT_STORAGE_KEY);
    } catch (error) {
      console.error('INFO [ImportWizardPage]: Import failed', error);
      setSnackbarMessage('Import failed. Please try again.');
    } finally {
      setIsImporting(false);
    }
  }, [jobId, selectedSupplierId, selectedIndices]);

  const handleSaveDraft = useCallback(() => {
    const draft: DraftData = {
      filesMetadata: selectedFiles.map((f) => ({ name: f.name, size: f.size, type: f.type })),
      extractedProducts: editedProducts,
      selectedIndices: Array.from(selectedIndices),
      supplierId: selectedSupplierId || null,
    };
    localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(draft));
    setSnackbarMessage('Draft saved successfully');
  }, [selectedFiles, editedProducts, selectedIndices, selectedSupplierId]);

  const handleLoadDraft = useCallback(() => {
    const draftStr = localStorage.getItem(DRAFT_STORAGE_KEY);
    if (draftStr) {
      const draft: DraftData = JSON.parse(draftStr);
      setEditedProducts(draft.extractedProducts);
      setSelectedIndices(new Set(draft.selectedIndices));
      if (draft.supplierId) {
        setSelectedSupplierId(draft.supplierId);
      }
      if (draft.extractedProducts.length > 0) {
        setActiveStep(2);
      }
    }
    setDraftDialogOpen(false);
  }, []);

  const handleDiscardDraft = useCallback(() => {
    localStorage.removeItem(DRAFT_STORAGE_KEY);
    setDraftDialogOpen(false);
  }, []);

  const handleCancelConfirm = useCallback(() => {
    setCancelDialogOpen(false);
    resetJob();
    setSelectedFiles([]);
    setEditedProducts([]);
    setSelectedIndices(new Set());
    setActiveStep(0);
    setSelectedSupplierId('');
  }, [resetJob]);

  const handleSuccessClose = useCallback(() => {
    setSuccessDialogOpen(false);
    handleCancelConfirm();
  }, [handleCancelConfirm]);

  const canProceedToNext = useMemo(() => {
    if (activeStep === 0) {
      return selectedFiles.length > 0;
    }
    if (activeStep === 2) {
      const hasSelection = selectedIndices.size > 0;
      const hasNoErrors = Object.keys(validationErrors).length === 0;
      return hasSelection && hasNoErrors;
    }
    return false;
  }, [activeStep, selectedFiles, selectedIndices, validationErrors]);

  const validationErrorCount = Object.keys(validationErrors).length;

  // Render Upload Step
  const renderUploadStep = () => (
    <Box>
      <Box
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        sx={{
          border: '2px dashed',
          borderColor: isDragOver ? 'primary.main' : 'grey.400',
          borderRadius: 2,
          p: 4,
          minHeight: 250,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          backgroundColor: isDragOver ? 'action.hover' : 'background.paper',
          cursor: 'pointer',
          transition: 'all 0.2s',
          mb: 2,
        }}
        component="label"
      >
        <input
          type="file"
          hidden
          multiple
          accept={ALLOWED_EXTENSIONS.join(',')}
          onChange={handleFileInputChange}
        />
        <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
        <Typography variant="h6">Drag and drop files here</Typography>
        <Typography variant="body2" color="text.secondary">
          or click to browse
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Supported formats: {ALLOWED_EXTENSIONS.join(', ')} (max {MAX_FILE_SIZE_MB}MB each)
        </Typography>
      </Box>

      {fileErrors.length > 0 && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {fileErrors.map((err, i) => (
            <div key={i}>{err}</div>
          ))}
        </Alert>
      )}

      {selectedFiles.length > 0 && (
        <Paper variant="outlined" sx={{ p: 2 }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Selected Files ({selectedFiles.length})
          </Typography>
          <List dense>
            {selectedFiles.map((file, index) => (
              <ListItem
                key={index}
                secondaryAction={
                  <Button size="small" color="error" onClick={() => handleRemoveFile(index)}>
                    Remove
                  </Button>
                }
              >
                <ListItemText
                  primary={file.name}
                  secondary={formatFileSize(file.size)}
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );

  // Render Processing Step
  const renderProcessingStep = () => (
    <Box sx={{ textAlign: 'center', py: 4 }}>
      {uploadError ? (
        <Alert severity="error" sx={{ mb: 2 }}>
          {uploadError}
          <Button size="small" onClick={handleBack} sx={{ ml: 2 }}>
            Try Again
          </Button>
        </Alert>
      ) : (
        <>
          <Typography variant="h6" sx={{ mb: 2 }}>
            {status === 'pending' && 'Starting extraction...'}
            {status === 'processing' && `Processing file ${processedFiles + 1} of ${totalFiles}`}
            {status === 'completed' && 'Extraction complete!'}
            {status === 'failed' && 'Extraction failed'}
          </Typography>

          <Box sx={{ width: '100%', mb: 2 }}>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{ height: 10, borderRadius: 5 }}
            />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {progress}% complete
            </Typography>
          </Box>

          {status === 'failed' && extractionErrors.length > 0 && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {extractionErrors.map((err, i) => (
                <div key={i}>{err}</div>
              ))}
              <Button size="small" onClick={handleBack} sx={{ mt: 1 }}>
                Try Again
              </Button>
            </Alert>
          )}
        </>
      )}
    </Box>
  );

  // Render Review Step
  const renderReviewStep = () => (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Review Extracted Products ({editedProducts.length})
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Chip
            label={`${selectedIndices.size} selected`}
            color="primary"
            variant="outlined"
          />
          {validationErrorCount > 0 && (
            <Chip
              icon={<ErrorIcon />}
              label={`${validationErrorCount} validation errors`}
              color="error"
              variant="outlined"
            />
          )}
        </Box>
      </Box>

      {editedProducts.length === 0 ? (
        <Alert severity="info">No products were extracted. Please try with different files.</Alert>
      ) : (
        <ExtractedProductTable
          products={editedProducts}
          selectedIndices={selectedIndices}
          onProductChange={handleProductChange}
          onProductSelect={handleProductSelect}
          onSelectAll={handleSelectAll}
          validationErrors={validationErrors}
        />
      )}
    </Box>
  );

  // Render Confirm Step
  const renderConfirmStep = () => {
    const selectedProducts = editedProducts.filter((_, i) => selectedIndices.has(i));

    return (
      <Box>
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Import Summary
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
              <CheckCircleIcon color="success" />
              <Typography>
                {selectedProducts.length} products selected for import
              </Typography>
            </Box>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Supplier *</InputLabel>
              <Select
                value={selectedSupplierId}
                onChange={(e) => setSelectedSupplierId(e.target.value)}
                label="Supplier *"
              >
                {suppliers.map((supplier) => (
                  <MenuItem key={supplier.id} value={supplier.id}>
                    {supplier.name} ({supplier.country})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {duplicateSkus.length > 0 && (
              <Alert severity="warning" icon={<WarningIcon />} sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Duplicate SKUs Detected</Typography>
                <Typography variant="body2">
                  The following SKUs already exist in the database: {duplicateSkus.join(', ')}
                </Typography>
              </Alert>
            )}

            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              Products to Import:
            </Typography>
            <Paper variant="outlined" sx={{ maxHeight: 200, overflow: 'auto', p: 1 }}>
              <List dense>
                {selectedProducts.map((product, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={product.name || 'Unnamed Product'}
                      secondary={`SKU: ${product.sku || 'N/A'} | Price: $${product.price_fob_usd ?? 'N/A'}`}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </CardContent>
        </Card>
      </Box>
    );
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return renderUploadStep();
      case 1:
        return renderProcessingStep();
      case 2:
        return renderReviewStep();
      case 3:
        return renderConfirmStep();
      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, margin: '0 auto' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Product Import Wizard</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {activeStep > 0 && activeStep !== 1 && (
            <Button variant="outlined" onClick={handleSaveDraft}>
              Save Draft
            </Button>
          )}
          <Button
            variant="outlined"
            color="error"
            onClick={() => setCancelDialogOpen(true)}
          >
            Cancel
          </Button>
        </Box>
      </Box>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {STEPS.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {renderStepContent()}

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
          <Button
            disabled={activeStep === 0 || activeStep === 1}
            onClick={handleBack}
          >
            Back
          </Button>
          <Box>
            {activeStep === 0 && (
              <Button
                variant="contained"
                onClick={handleNext}
                disabled={!canProceedToNext}
              >
                Start Extraction
              </Button>
            )}
            {activeStep === 2 && (
              <Button
                variant="contained"
                onClick={handleNext}
                disabled={!canProceedToNext}
              >
                Continue to Import
              </Button>
            )}
            {activeStep === 3 && (
              <Button
                variant="contained"
                color="success"
                onClick={handleImport}
                disabled={!selectedSupplierId || isImporting}
              >
                {isImporting ? 'Importing...' : 'Import Products'}
              </Button>
            )}
          </Box>
        </Box>
      </Paper>

      {/* Cancel Confirmation Dialog */}
      <Dialog open={cancelDialogOpen} onClose={() => setCancelDialogOpen(false)}>
        <DialogTitle>Cancel Import?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to cancel? All progress will be lost unless you save a draft.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCancelDialogOpen(false)}>Continue Editing</Button>
          <Button onClick={handleCancelConfirm} color="error">
            Cancel Import
          </Button>
        </DialogActions>
      </Dialog>

      {/* Draft Dialog */}
      <Dialog open={draftDialogOpen} onClose={handleDiscardDraft}>
        <DialogTitle>Resume Draft?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            A previous import draft was found. Would you like to continue where you left off?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDiscardDraft} color="error">
            Discard Draft
          </Button>
          <Button onClick={handleLoadDraft} variant="contained">
            Load Draft
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success Dialog */}
      <Dialog open={successDialogOpen} onClose={handleSuccessClose}>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CheckCircleIcon color="success" />
            Import Complete
          </Box>
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {importResult && (
              <>
                Successfully imported {importResult.imported} products.
                {importResult.failed > 0 && (
                  <Typography color="error">
                    {importResult.failed} products failed to import.
                  </Typography>
                )}
              </>
            )}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleSuccessClose} variant="contained">
            Done
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={!!snackbarMessage}
        autoHideDuration={4000}
        onClose={() => setSnackbarMessage(null)}
        message={snackbarMessage}
      />
    </Box>
  );
}
