import React, { useState } from 'react';
import {
  Box,
  Button,
  ButtonGroup,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Snackbar,
  Alert,
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import CalculateIcon from '@mui/icons-material/Calculate';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import EmailIcon from '@mui/icons-material/Email';
import LinkIcon from '@mui/icons-material/Link';
import type { QuotationSendEmailRequest, QuotationSendEmailResponse } from '@/types/kompass';

interface QuotationActionsProps {
  canSave: boolean;
  canCalculate: boolean;
  isSaving: boolean;
  isCalculating: boolean;
  quotationId: string | null;
  onSave: () => Promise<void>;
  onCalculate: () => Promise<void>;
  onExportPdf: () => Promise<Blob>;
  onSendEmail: (request: QuotationSendEmailRequest) => Promise<QuotationSendEmailResponse>;
  onGetShareLink: () => Promise<string>;
  disabled?: boolean;
}

const QuotationActions: React.FC<QuotationActionsProps> = ({
  canSave,
  canCalculate,
  isSaving,
  isCalculating,
  quotationId,
  onSave,
  onCalculate,
  onExportPdf,
  onSendEmail,
  onGetShareLink,
  disabled = false,
}) => {
  const [emailDialogOpen, setEmailDialogOpen] = useState(false);
  const [emailRecipient, setEmailRecipient] = useState('');
  const [emailRecipientName, setEmailRecipientName] = useState('');
  const [emailSubject, setEmailSubject] = useState('');
  const [emailMessage, setEmailMessage] = useState('');
  const [isSendingEmail, setIsSendingEmail] = useState(false);
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [isCopyingLink, setIsCopyingLink] = useState(false);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  }>({
    open: false,
    message: '',
    severity: 'success',
  });

  const handleSave = async () => {
    try {
      await onSave();
      setSnackbar({
        open: true,
        message: 'Quotation saved successfully',
        severity: 'success',
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: err instanceof Error ? err.message : 'Failed to save quotation',
        severity: 'error',
      });
    }
  };

  const handleCalculate = async () => {
    try {
      await onCalculate();
      setSnackbar({
        open: true,
        message: 'Pricing calculated successfully',
        severity: 'success',
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: err instanceof Error ? err.message : 'Failed to calculate pricing',
        severity: 'error',
      });
    }
  };

  const handleExportPdf = async () => {
    if (!quotationId) {
      setSnackbar({
        open: true,
        message: 'Please save the quotation first',
        severity: 'error',
      });
      return;
    }

    setIsExportingPdf(true);
    try {
      const blob = await onExportPdf();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `quotation-${quotationId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      setSnackbar({
        open: true,
        message: 'PDF downloaded successfully',
        severity: 'success',
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: err instanceof Error ? err.message : 'Failed to export PDF',
        severity: 'error',
      });
    } finally {
      setIsExportingPdf(false);
    }
  };

  const handleOpenEmailDialog = () => {
    if (!quotationId) {
      setSnackbar({
        open: true,
        message: 'Please save the quotation first',
        severity: 'error',
      });
      return;
    }
    setEmailDialogOpen(true);
  };

  const handleSendEmail = async () => {
    if (!emailRecipient) {
      setSnackbar({
        open: true,
        message: 'Please enter a recipient email',
        severity: 'error',
      });
      return;
    }

    setIsSendingEmail(true);
    try {
      const request: QuotationSendEmailRequest = {
        recipient_email: emailRecipient,
        recipient_name: emailRecipientName || undefined,
        subject: emailSubject || undefined,
        message: emailMessage || undefined,
        include_pdf: true,
      };
      await onSendEmail(request);
      setEmailDialogOpen(false);
      setEmailRecipient('');
      setEmailRecipientName('');
      setEmailSubject('');
      setEmailMessage('');
      setSnackbar({
        open: true,
        message: 'Email sent successfully',
        severity: 'success',
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: err instanceof Error ? err.message : 'Failed to send email',
        severity: 'error',
      });
    } finally {
      setIsSendingEmail(false);
    }
  };

  const handleCopyShareLink = async () => {
    if (!quotationId) {
      setSnackbar({
        open: true,
        message: 'Please save the quotation first',
        severity: 'error',
      });
      return;
    }

    setIsCopyingLink(true);
    try {
      const shareUrl = await onGetShareLink();
      await navigator.clipboard.writeText(shareUrl);
      setSnackbar({
        open: true,
        message: 'Share link copied to clipboard',
        severity: 'success',
      });
    } catch (err) {
      setSnackbar({
        open: true,
        message: err instanceof Error ? err.message : 'Failed to copy share link',
        severity: 'error',
      });
    } finally {
      setIsCopyingLink(false);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <>
      <Box display="flex" gap={1} flexWrap="wrap">
        {/* Primary Actions */}
        <Button
          variant="contained"
          color="primary"
          startIcon={isSaving ? <CircularProgress size={16} color="inherit" /> : <SaveIcon />}
          onClick={handleSave}
          disabled={disabled || !canSave || isSaving}
        >
          {isSaving ? 'Saving...' : 'Save Draft'}
        </Button>

        <Button
          variant="outlined"
          startIcon={isCalculating ? <CircularProgress size={16} /> : <CalculateIcon />}
          onClick={handleCalculate}
          disabled={disabled || !canCalculate || isCalculating}
        >
          {isCalculating ? 'Calculating...' : 'Calculate'}
        </Button>

        {/* Secondary Actions */}
        <ButtonGroup variant="outlined" disabled={disabled || !quotationId}>
          <Button
            startIcon={isExportingPdf ? <CircularProgress size={16} /> : <PictureAsPdfIcon />}
            onClick={handleExportPdf}
            disabled={isExportingPdf}
          >
            PDF
          </Button>
          <Button
            startIcon={<EmailIcon />}
            onClick={handleOpenEmailDialog}
          >
            Email
          </Button>
          <Button
            startIcon={isCopyingLink ? <CircularProgress size={16} /> : <LinkIcon />}
            onClick={handleCopyShareLink}
            disabled={isCopyingLink}
          >
            Share
          </Button>
        </ButtonGroup>
      </Box>

      {/* Email Dialog */}
      <Dialog open={emailDialogOpen} onClose={() => setEmailDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Send Quotation via Email</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={1}>
            <TextField
              label="Recipient Email"
              type="email"
              value={emailRecipient}
              onChange={(e) => setEmailRecipient(e.target.value)}
              required
              fullWidth
            />
            <TextField
              label="Recipient Name (optional)"
              value={emailRecipientName}
              onChange={(e) => setEmailRecipientName(e.target.value)}
              fullWidth
            />
            <TextField
              label="Subject (optional)"
              value={emailSubject}
              onChange={(e) => setEmailSubject(e.target.value)}
              fullWidth
              placeholder="Leave empty for default subject"
            />
            <TextField
              label="Message (optional)"
              value={emailMessage}
              onChange={(e) => setEmailMessage(e.target.value)}
              fullWidth
              multiline
              rows={4}
              placeholder="Add a personal message to include in the email"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEmailDialogOpen(false)} disabled={isSendingEmail}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSendEmail}
            disabled={isSendingEmail || !emailRecipient}
          >
            {isSendingEmail ? <CircularProgress size={20} /> : 'Send Email'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbar.severity} variant="filled">
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
};

export default QuotationActions;
