import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  Skeleton,
  Divider,
  Alert,
} from '@mui/material';
import FactoryIcon from '@mui/icons-material/Factory';
import StorefrontIcon from '@mui/icons-material/Storefront';
import PeopleIcon from '@mui/icons-material/People';
import SquareFootIcon from '@mui/icons-material/SquareFoot';
import PrecisionManufacturingIcon from '@mui/icons-material/PrecisionManufacturing';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import VisibilityIcon from '@mui/icons-material/Visibility';
import RefreshIcon from '@mui/icons-material/Refresh';
import EditIcon from '@mui/icons-material/Edit';
import ClassificationBadge from './ClassificationBadge';
import MarketsServedChart from './MarketsServedChart';
import type { SupplierAuditResponse } from '@/types/kompass';

interface AuditSummaryCardProps {
  audit: SupplierAuditResponse;
  onReprocess?: (auditId: string) => void;
  onViewPdf?: (auditId: string) => void;
  onOverrideClick?: () => void;
  showClassification?: boolean;
}

const AuditSummaryCard: React.FC<AuditSummaryCardProps> = ({
  audit,
  onReprocess,
  onViewPdf,
  onOverrideClick,
  showClassification = true,
}) => {
  const isProcessing = audit.extraction_status === 'pending' || audit.extraction_status === 'processing';
  const isFailed = audit.extraction_status === 'failed';
  const isCompleted = audit.extraction_status === 'completed';

  const currentGrade = audit.manual_classification || audit.ai_classification;
  const isManualOverride = !!audit.manual_classification;

  const formatNumber = (value: number | null): string => {
    if (value === null || value === undefined) return '-';
    return new Intl.NumberFormat('en-US').format(value);
  };

  const formatArea = (sqm: number | null): string => {
    if (sqm === null || sqm === undefined) return '-';
    return `${formatNumber(sqm)} sqm`;
  };

  // Loading skeleton for processing state
  if (isProcessing) {
    return (
      <Card variant="outlined">
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Audit Summary</Typography>
            <Chip label="Processing" color="info" size="small" />
          </Box>
          <Grid container spacing={2}>
            <Grid item xs={12} md={8}>
              <Grid container spacing={2}>
                {[1, 2, 3, 4].map((i) => (
                  <Grid item xs={6} key={i}>
                    <Skeleton variant="rectangular" height={60} />
                  </Grid>
                ))}
              </Grid>
            </Grid>
            <Grid item xs={12} md={4}>
              <Skeleton variant="rectangular" height={140} />
            </Grid>
          </Grid>
          <Box sx={{ mt: 2 }}>
            <Skeleton variant="rectangular" height={150} />
          </Box>
        </CardContent>
      </Card>
    );
  }

  // Error state for failed extraction
  if (isFailed) {
    return (
      <Card variant="outlined">
        <CardContent>
          <Alert
            severity="error"
            action={
              onReprocess && (
                <Button
                  color="inherit"
                  size="small"
                  startIcon={<RefreshIcon />}
                  onClick={() => onReprocess(audit.id)}
                >
                  Reprocess
                </Button>
              )
            }
          >
            Extraction failed. The audit document could not be processed.
          </Alert>
          <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
            {onViewPdf && (
              <Button
                variant="outlined"
                size="small"
                startIcon={<VisibilityIcon />}
                onClick={() => onViewPdf(audit.id)}
              >
                View Full PDF
              </Button>
            )}
          </Box>
        </CardContent>
      </Card>
    );
  }

  // Completed extraction - full summary
  return (
    <Card variant="outlined">
      <CardContent>
        {/* Header with classification */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="h6">Audit Summary</Typography>
          {showClassification && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <ClassificationBadge
                grade={currentGrade}
                aiReason={audit.ai_classification_reason}
                isManualOverride={isManualOverride}
              />
              {onOverrideClick && (
                <Button
                  size="small"
                  startIcon={<EditIcon />}
                  onClick={onOverrideClick}
                >
                  Override
                </Button>
              )}
            </Box>
          )}
        </Box>

        <Grid container spacing={3}>
          {/* Quick Summary Section */}
          <Grid item xs={12} md={8}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Quick Summary
            </Typography>
            <Grid container spacing={2}>
              {/* Supplier Type */}
              <Grid item xs={6} sm={3}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {audit.supplier_type === 'manufacturer' ? (
                    <FactoryIcon color="success" />
                  ) : audit.supplier_type === 'trader' ? (
                    <StorefrontIcon color="warning" />
                  ) : (
                    <StorefrontIcon color="disabled" />
                  )}
                  <Box>
                    <Typography variant="caption" color="text.secondary" display="block">
                      Type
                    </Typography>
                    <Typography variant="body2" fontWeight={500}>
                      {audit.supplier_type
                        ? audit.supplier_type.charAt(0).toUpperCase() + audit.supplier_type.slice(1)
                        : '-'}
                    </Typography>
                  </Box>
                </Box>
              </Grid>

              {/* Employee Count */}
              <Grid item xs={6} sm={3}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <PeopleIcon color="primary" />
                  <Box>
                    <Typography variant="caption" color="text.secondary" display="block">
                      Employees
                    </Typography>
                    <Typography variant="body2" fontWeight={500}>
                      {formatNumber(audit.employee_count)}
                    </Typography>
                  </Box>
                </Box>
              </Grid>

              {/* Factory Area */}
              <Grid item xs={6} sm={3}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <SquareFootIcon color="primary" />
                  <Box>
                    <Typography variant="caption" color="text.secondary" display="block">
                      Factory Area
                    </Typography>
                    <Typography variant="body2" fontWeight={500}>
                      {formatArea(audit.factory_area_sqm)}
                    </Typography>
                  </Box>
                </Box>
              </Grid>

              {/* Production Lines */}
              <Grid item xs={6} sm={3}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <PrecisionManufacturingIcon color="primary" />
                  <Box>
                    <Typography variant="caption" color="text.secondary" display="block">
                      Production Lines
                    </Typography>
                    <Typography variant="body2" fontWeight={500}>
                      {formatNumber(audit.production_lines_count)}
                    </Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>

            {/* Certifications */}
            {audit.certifications && audit.certifications.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                  Certifications
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {audit.certifications.map((cert, index) => (
                    <Chip key={index} label={cert} size="small" variant="outlined" />
                  ))}
                </Box>
              </Box>
            )}
          </Grid>

          {/* Markets Served Chart */}
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Markets Served
            </Typography>
            <MarketsServedChart markets={audit.markets_served} height={160} />
          </Grid>
        </Grid>

        <Divider sx={{ my: 2 }} />

        {/* Positive and Negative Points */}
        <Grid container spacing={3}>
          {/* Positive Points */}
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <CheckCircleIcon color="success" fontSize="small" />
              <Typography variant="subtitle2" color="success.main">
                Positive Points
              </Typography>
            </Box>
            {audit.positive_points && audit.positive_points.length > 0 ? (
              <Box component="ul" sx={{ m: 0, pl: 2 }}>
                {audit.positive_points.map((point, index) => (
                  <Typography component="li" variant="body2" key={index} sx={{ mb: 0.5 }}>
                    {point}
                  </Typography>
                ))}
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No positive points recorded
              </Typography>
            )}
          </Grid>

          {/* Negative Points */}
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <WarningIcon color="warning" fontSize="small" />
              <Typography variant="subtitle2" color="warning.main">
                Areas of Concern
              </Typography>
            </Box>
            {audit.negative_points && audit.negative_points.length > 0 ? (
              <Box component="ul" sx={{ m: 0, pl: 2 }}>
                {audit.negative_points.map((point, index) => (
                  <Typography component="li" variant="body2" key={index} sx={{ mb: 0.5 }}>
                    {point}
                  </Typography>
                ))}
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No areas of concern noted
              </Typography>
            )}
          </Grid>
        </Grid>

        <Divider sx={{ my: 2 }} />

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {onViewPdf && (
            <Button
              variant="outlined"
              size="small"
              startIcon={<VisibilityIcon />}
              onClick={() => onViewPdf(audit.id)}
            >
              View Full PDF
            </Button>
          )}
          {onReprocess && isCompleted && (
            <Button
              variant="outlined"
              size="small"
              startIcon={<RefreshIcon />}
              onClick={() => onReprocess(audit.id)}
            >
              Reprocess
            </Button>
          )}
        </Box>

        {/* Classification notes if present */}
        {audit.classification_notes && (
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="caption" fontWeight={600}>Override Notes:</Typography>
            <Typography variant="body2">{audit.classification_notes}</Typography>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default AuditSummaryCard;
