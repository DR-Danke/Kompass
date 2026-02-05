import React from 'react';
import { Chip, Tooltip } from '@mui/material';
import type { SupplierPipelineStatus } from '@/types/kompass';

interface PipelineStatusBadgeProps {
  status: SupplierPipelineStatus;
  size?: 'small' | 'medium';
}

interface StatusConfig {
  label: string;
  description: string;
  backgroundColor: string;
  textColor: string;
}

const STATUS_CONFIG: Record<SupplierPipelineStatus, StatusConfig> = {
  contacted: {
    label: 'Contacted',
    description: 'Initial contact made with supplier',
    backgroundColor: '#f5f5f5',
    textColor: '#616161',
  },
  potential: {
    label: 'Potential',
    description: 'Supplier shows potential for partnership',
    backgroundColor: '#e3f2fd',
    textColor: '#1565c0',
  },
  quoted: {
    label: 'Quoted',
    description: 'Pricing quotations received from supplier',
    backgroundColor: '#fff8e1',
    textColor: '#f57c00',
  },
  certified: {
    label: 'Certified',
    description: 'Supplier passed certification audit',
    backgroundColor: '#e8f5e9',
    textColor: '#2e7d32',
  },
  active: {
    label: 'Active',
    description: 'Supplier is actively supplying products',
    backgroundColor: '#c8e6c9',
    textColor: '#1b5e20',
  },
  inactive: {
    label: 'Inactive',
    description: 'Supplier is no longer active',
    backgroundColor: '#ffebee',
    textColor: '#c62828',
  },
};

const PipelineStatusBadge: React.FC<PipelineStatusBadgeProps> = ({
  status,
  size = 'small',
}) => {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.contacted;

  return (
    <Tooltip title={config.description}>
      <Chip
        label={config.label}
        size={size}
        sx={{
          backgroundColor: config.backgroundColor,
          color: config.textColor,
          fontWeight: 500,
          '& .MuiChip-label': {
            px: size === 'small' ? 1 : 1.5,
          },
        }}
      />
    </Tooltip>
  );
};

export default React.memo(PipelineStatusBadge);

export { STATUS_CONFIG };
