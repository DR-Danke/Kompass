import React from 'react';
import { Chip } from '@mui/material';
import type { QuotationStatus } from '@/types/kompass';

interface QuotationStatusBadgeProps {
  status: QuotationStatus;
  size?: 'small' | 'medium';
}

type StatusConfig = {
  label: string;
  color: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning';
  bgcolor?: string;
};

const STATUS_CONFIG: Record<QuotationStatus, StatusConfig> = {
  draft: { label: 'Draft', color: 'default' },
  sent: { label: 'Sent', color: 'info' },
  viewed: { label: 'Viewed', color: 'secondary' },
  negotiating: { label: 'Negotiating', color: 'warning' },
  accepted: { label: 'Accepted', color: 'success' },
  rejected: { label: 'Rejected', color: 'error' },
  expired: { label: 'Expired', color: 'default', bgcolor: '#616161' },
};

const QuotationStatusBadge: React.FC<QuotationStatusBadgeProps> = ({ status, size = 'small' }) => {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.draft;

  return (
    <Chip
      label={config.label}
      color={config.color}
      size={size}
      sx={{
        fontWeight: 500,
        ...(config.bgcolor && {
          backgroundColor: config.bgcolor,
          color: '#fff',
        }),
      }}
    />
  );
};

export default QuotationStatusBadge;
