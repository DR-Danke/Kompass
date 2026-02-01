import React from 'react';
import { Chip } from '@mui/material';

interface PortfolioStatusBadgeProps {
  isActive: boolean;
  size?: 'small' | 'medium';
}

const PortfolioStatusBadge: React.FC<PortfolioStatusBadgeProps> = ({ isActive, size = 'small' }) => {
  const config = isActive
    ? { label: 'Published', color: 'success' as const }
    : { label: 'Draft', color: 'default' as const };

  return (
    <Chip
      label={config.label}
      color={config.color}
      size={size}
      sx={{ fontWeight: 500 }}
    />
  );
};

export default PortfolioStatusBadge;
