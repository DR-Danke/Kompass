import React from 'react';
import { Chip } from '@mui/material';
import type { ProductStatus } from '@/types/kompass';

interface ProductStatusBadgeProps {
  status: ProductStatus;
  size?: 'small' | 'medium';
}

const statusConfig: Record<ProductStatus, { label: string; color: 'success' | 'default' | 'warning' | 'error' }> = {
  active: { label: 'Active', color: 'success' },
  inactive: { label: 'Inactive', color: 'default' },
  draft: { label: 'Draft', color: 'warning' },
  discontinued: { label: 'Discontinued', color: 'error' },
};

const ProductStatusBadge: React.FC<ProductStatusBadgeProps> = ({ status, size = 'small' }) => {
  const config = statusConfig[status] || { label: status, color: 'default' as const };

  return (
    <Chip
      label={config.label}
      color={config.color}
      size={size}
      sx={{ fontWeight: 500 }}
    />
  );
};

export default ProductStatusBadge;
