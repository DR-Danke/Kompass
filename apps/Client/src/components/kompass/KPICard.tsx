import React from 'react';
import { Box, Card, CardContent, Skeleton, Typography } from '@mui/material';
import type { SxProps, Theme } from '@mui/material';

export interface KPICardProps {
  title: string;
  value: number | string;
  icon?: React.ReactNode;
  isLoading?: boolean;
  formatValue?: (value: number | string) => string;
  sx?: SxProps<Theme>;
}

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  icon,
  isLoading = false,
  formatValue,
  sx,
}) => {
  const displayValue = formatValue ? formatValue(value) : value.toString();

  return (
    <Card sx={{ height: '100%', ...sx }} data-testid={`kpi-card-${title.toLowerCase().replace(/\s+/g, '-')}`}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
          <Box sx={{ flex: 1 }}>
            <Typography
              variant="body2"
              color="text.secondary"
              gutterBottom
              sx={{ fontWeight: 500 }}
            >
              {title}
            </Typography>
            {isLoading ? (
              <Skeleton variant="text" width="60%" height={40} />
            ) : (
              <Typography variant="h4" component="div" sx={{ fontWeight: 600 }}>
                {displayValue}
              </Typography>
            )}
          </Box>
          {icon && (
            <Box
              sx={{
                color: 'primary.main',
                opacity: 0.8,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {icon}
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default KPICard;
