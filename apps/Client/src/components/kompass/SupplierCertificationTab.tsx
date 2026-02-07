import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Alert,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import AuditUploader from './AuditUploader';
import AuditSummaryCard from './AuditSummaryCard';
import ClassificationOverrideDialog from './ClassificationOverrideDialog';
import ClassificationBadge from './ClassificationBadge';
import { auditService } from '@/services/kompassService';
import type { SupplierAuditResponse, ClassificationOverride } from '@/types/kompass';

interface SupplierCertificationTabProps {
  supplierId: string;
  supplierName: string;
}

const SupplierCertificationTab: React.FC<SupplierCertificationTabProps> = ({
  supplierId,
  supplierName,
}) => {
  const [audits, setAudits] = useState<SupplierAuditResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [overrideDialogOpen, setOverrideDialogOpen] = useState(false);
  const [selectedAudit, setSelectedAudit] = useState<SupplierAuditResponse | null>(null);

  const fetchAudits = useCallback(async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      setError(null);
      console.log(`INFO [SupplierCertificationTab]: Fetching audits for supplier ${supplierId}`);
      const response = await auditService.list(supplierId);
      setAudits(response.items);
    } catch (err) {
      console.log('ERROR [SupplierCertificationTab]: Failed to fetch audits', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch audits');
    } finally {
      if (showLoading) setLoading(false);
    }
  }, [supplierId]);

  useEffect(() => {
    fetchAudits();
  }, [fetchAudits]);

  // Poll for status updates when there are pending/processing audits
  useEffect(() => {
    const hasPendingAudits = audits.some(
      (audit) => audit.extraction_status === 'pending' || audit.extraction_status === 'processing'
    );

    if (!hasPendingAudits) return;

    console.log('INFO [SupplierCertificationTab]: Starting polling for pending audits');
    const pollInterval = setInterval(() => {
      fetchAudits(false); // Silent refresh (no loading spinner)
    }, 5000); // Poll every 5 seconds

    return () => {
      console.log('INFO [SupplierCertificationTab]: Stopping polling');
      clearInterval(pollInterval);
    };
  }, [audits, fetchAudits]);

  const handleUploadComplete = (audit: SupplierAuditResponse) => {
    console.log(`INFO [SupplierCertificationTab]: Audit uploaded successfully, ID: ${audit.id}`);
    setAudits((prev) => [audit, ...prev]);
  };

  const handleUploadError = (errorMsg: string) => {
    console.log(`ERROR [SupplierCertificationTab]: Upload error - ${errorMsg}`);
    setError(errorMsg);
  };

  const handleReprocess = async (auditId: string) => {
    try {
      console.log(`INFO [SupplierCertificationTab]: Reprocessing audit ${auditId}`);
      const updatedAudit = await auditService.reprocess(supplierId, auditId);
      setAudits((prev) =>
        prev.map((a) => (a.id === auditId ? updatedAudit : a))
      );
    } catch (err) {
      console.log('ERROR [SupplierCertificationTab]: Failed to reprocess audit', err);
      setError(err instanceof Error ? err.message : 'Failed to reprocess audit');
    }
  };

  const handleViewPdf = (auditId: string) => {
    // Use the backend download endpoint to serve the PDF
    // This works for both local file:// URLs and Supabase Storage URLs
    // Token is passed as query parameter since browsers don't send headers when opening new tabs
    let apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
    if (window.location.protocol === 'https:' && apiUrl.startsWith('http://')) {
      apiUrl = apiUrl.replace('http://', 'https://');
    }
    const token = localStorage.getItem('token');
    const downloadUrl = `${apiUrl}/suppliers/${supplierId}/audits/${auditId}/download?token=${token}`;
    console.log(`INFO [SupplierCertificationTab]: Opening PDF via backend: ${downloadUrl}`);
    window.open(downloadUrl, '_blank');
  };

  const handleOverrideClick = (audit: SupplierAuditResponse) => {
    setSelectedAudit(audit);
    setOverrideDialogOpen(true);
  };

  const handleOverrideConfirm = async (data: ClassificationOverride) => {
    if (!selectedAudit) return;

    console.log(`INFO [SupplierCertificationTab]: Overriding classification for audit ${selectedAudit.id}`);
    const updatedAudit = await auditService.overrideClassification(
      supplierId,
      selectedAudit.id,
      data
    );
    setAudits((prev) =>
      prev.map((a) => (a.id === selectedAudit.id ? updatedAudit : a))
    );
  };

  const handleOverrideClose = () => {
    setOverrideDialogOpen(false);
    setSelectedAudit(null);
  };

  const latestAudit = audits.length > 0 ? audits[0] : null;
  const auditHistory = audits.length > 1 ? audits.slice(1) : [];

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getStatusChip = (status: string) => {
    const statusColors: Record<string, 'default' | 'info' | 'success' | 'error'> = {
      pending: 'default',
      processing: 'info',
      completed: 'success',
      failed: 'error',
    };
    return (
      <Chip
        label={status.charAt(0).toUpperCase() + status.slice(1)}
        size="small"
        color={statusColors[status] || 'default'}
      />
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Upload Section */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" fontWeight={600} gutterBottom>
          Upload New Audit
        </Typography>
        <AuditUploader
          supplierId={supplierId}
          onUploadComplete={handleUploadComplete}
          onError={handleUploadError}
        />
      </Box>

      {/* Latest Audit Summary */}
      {latestAudit ? (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            Latest Audit
          </Typography>
          <AuditSummaryCard
            audit={latestAudit}
            onReprocess={handleReprocess}
            onViewPdf={handleViewPdf}
            onOverrideClick={() => handleOverrideClick(latestAudit)}
          />
        </Box>
      ) : (
        <Paper variant="outlined" sx={{ p: 3, textAlign: 'center', mb: 3 }}>
          <Typography variant="body1" color="text.secondary">
            No audits uploaded yet.
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Upload a factory audit PDF to get started with supplier certification.
          </Typography>
        </Paper>
      )}

      {/* Audit History */}
      {auditHistory.length > 0 && (
        <Box>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            Audit History
          </Typography>
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Classification</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {auditHistory.map((audit) => (
                  <TableRow
                    key={audit.id}
                    hover
                    sx={{ cursor: 'pointer' }}
                    onClick={() => handleOverrideClick(audit)}
                  >
                    <TableCell>{formatDate(audit.audit_date || audit.created_at)}</TableCell>
                    <TableCell>
                      {audit.audit_type === 'factory_audit' ? 'Factory Audit' : 'Container Inspection'}
                    </TableCell>
                    <TableCell>{getStatusChip(audit.extraction_status)}</TableCell>
                    <TableCell>
                      <ClassificationBadge
                        grade={audit.manual_classification || audit.ai_classification}
                        isManualOverride={!!audit.manual_classification}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {/* Override Dialog */}
      <ClassificationOverrideDialog
        open={overrideDialogOpen}
        onClose={handleOverrideClose}
        onConfirm={handleOverrideConfirm}
        currentClassification={
          selectedAudit?.manual_classification || selectedAudit?.ai_classification || null
        }
        supplierName={supplierName}
      />
    </Box>
  );
};

export default SupplierCertificationTab;
