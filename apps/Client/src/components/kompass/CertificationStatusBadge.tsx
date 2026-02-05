import React from 'react';
import { Box, Chip, Tooltip } from '@mui/material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import type { CertificationStatus, AuditExtractionStatus } from '@/types/kompass';
import ClassificationBadge from './ClassificationBadge';

interface CertificationStatusBadgeProps {
  certificationStatus: CertificationStatus;
  latestAuditId?: string | null;
  extractionStatus?: AuditExtractionStatus | null;
  size?: 'small' | 'medium';
}

const CERTIFICATION_CONFIG: Record<
  CertificationStatus,
  { label: string; description: string; grade: 'A' | 'B' | 'C' | null }
> = {
  certified_a: {
    label: 'Type A',
    description: 'Certified Type A - Excellent supplier quality',
    grade: 'A',
  },
  certified_b: {
    label: 'Type B',
    description: 'Certified Type B - Good supplier quality',
    grade: 'B',
  },
  certified_c: {
    label: 'Type C',
    description: 'Certified Type C - Acceptable supplier quality',
    grade: 'C',
  },
  pending_review: {
    label: 'Pending',
    description: 'Certification pending review',
    grade: null,
  },
  uncertified: {
    label: 'Uncertified',
    description: 'Supplier not yet certified',
    grade: null,
  },
};

const CertificationStatusBadge: React.FC<CertificationStatusBadgeProps> = ({
  certificationStatus,
  latestAuditId,
  extractionStatus,
  size = 'small',
}) => {
  const config = CERTIFICATION_CONFIG[certificationStatus] || CERTIFICATION_CONFIG.uncertified;
  const showWarning = extractionStatus === 'failed' && latestAuditId;

  // If certified (A, B, or C), use the ClassificationBadge
  if (config.grade) {
    return (
      <Box sx={{ display: 'inline-flex', alignItems: 'center', gap: 0.5 }}>
        <ClassificationBadge grade={config.grade} size={size} />
        {showWarning && (
          <Tooltip title="Audit extraction failed - manual review required">
            <WarningAmberIcon
              sx={{
                fontSize: size === 'small' ? 16 : 20,
                color: 'warning.main',
              }}
            />
          </Tooltip>
        )}
      </Box>
    );
  }

  // For uncertified or pending, show a simple chip
  return (
    <Box sx={{ display: 'inline-flex', alignItems: 'center', gap: 0.5 }}>
      <Tooltip title={config.description}>
        <Chip
          label={config.label}
          size={size}
          sx={{
            backgroundColor:
              certificationStatus === 'pending_review' ? '#fff3e0' : '#f5f5f5',
            color: certificationStatus === 'pending_review' ? '#e65100' : '#757575',
            fontWeight: 500,
            '& .MuiChip-label': {
              px: size === 'small' ? 1 : 1.5,
            },
          }}
        />
      </Tooltip>
      {showWarning && (
        <Tooltip title="Audit extraction failed - manual review required">
          <WarningAmberIcon
            sx={{
              fontSize: size === 'small' ? 16 : 20,
              color: 'warning.main',
            }}
          />
        </Tooltip>
      )}
    </Box>
  );
};

export default React.memo(CertificationStatusBadge);

export { CERTIFICATION_CONFIG };
