import React from 'react';
import { Box, Chip, Tooltip, Typography } from '@mui/material';
import type { ClassificationGrade } from '@/types/kompass';

interface ClassificationBadgeProps {
  grade: ClassificationGrade | null;
  aiReason?: string | null;
  isManualOverride?: boolean;
  size?: 'small' | 'medium' | 'large';
}

const GRADE_COLORS: Record<ClassificationGrade, string> = {
  A: '#4caf50',
  B: '#ff9800',
  C: '#f44336',
};

const GRADE_LABELS: Record<ClassificationGrade, string> = {
  A: 'Grade A - Excellent',
  B: 'Grade B - Acceptable',
  C: 'Grade C - Needs Improvement',
};

const SIZE_MAP = {
  small: { height: 24, fontSize: '0.75rem' },
  medium: { height: 32, fontSize: '0.875rem' },
  large: { height: 40, fontSize: '1rem' },
};

const ClassificationBadge: React.FC<ClassificationBadgeProps> = ({
  grade,
  aiReason,
  isManualOverride = false,
  size = 'medium',
}) => {
  const sizeStyles = SIZE_MAP[size];
  const backgroundColor = grade ? GRADE_COLORS[grade] : '#9e9e9e';
  const label = grade ? `Grade ${grade}` : 'Pending';
  const tooltipContent = grade
    ? `${GRADE_LABELS[grade]}${aiReason ? `\n\nReason: ${aiReason}` : ''}`
    : 'Classification pending';

  return (
    <Tooltip
      title={
        <Box sx={{ whiteSpace: 'pre-line' }}>
          <Typography variant="body2">{tooltipContent}</Typography>
          {isManualOverride && (
            <Typography variant="caption" sx={{ fontStyle: 'italic', mt: 0.5, display: 'block' }}>
              Manually overridden
            </Typography>
          )}
        </Box>
      }
      arrow
    >
      <Box sx={{ display: 'inline-flex', alignItems: 'center', gap: 0.5 }}>
        <Chip
          label={label}
          sx={{
            backgroundColor,
            color: 'white',
            fontWeight: 600,
            height: sizeStyles.height,
            fontSize: sizeStyles.fontSize,
            '& .MuiChip-label': {
              px: size === 'small' ? 1 : 1.5,
            },
          }}
        />
        {isManualOverride && (
          <Chip
            label="Manual"
            size="small"
            variant="outlined"
            sx={{
              height: 20,
              fontSize: '0.65rem',
              borderColor: backgroundColor,
              color: backgroundColor,
            }}
          />
        )}
      </Box>
    </Tooltip>
  );
};

export default ClassificationBadge;
