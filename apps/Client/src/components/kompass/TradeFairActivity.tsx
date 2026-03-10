import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Chip,
  Grid,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Skeleton,
  Tooltip,
  Typography,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import BusinessIcon from '@mui/icons-material/Business';
import EmailIcon from '@mui/icons-material/Email';
import ReplyIcon from '@mui/icons-material/Reply';
import { useTradeFairActivity } from '@/hooks/kompass/useTradeFairActivity';
import { KPICard } from '@/components/kompass/KPICard';
import type { BusinessCardCaptureStatus } from '@/types/kompass';

const STATUS_COLORS: Record<string, 'warning' | 'info' | 'secondary' | 'success' | 'error' | 'default'> = {
  pending: 'warning',
  processing: 'info',
  extracted: 'secondary',
  confirmed: 'success',
  rejected: 'error',
  failed: 'default',
};

const STATUS_LABELS: Record<string, string> = {
  pending: 'Pendiente',
  processing: 'Procesando',
  extracted: 'Extraído',
  confirmed: 'Confirmado',
  rejected: 'Rechazado',
  failed: 'Fallido',
};

const OUTREACH_LABELS: Record<string, string> = {
  none: 'Sin contacto',
  pending: 'Pendiente',
  contacted: 'Contactado',
  responded: 'Respondió',
  meeting_scheduled: 'Reunión',
  completed: 'Completado',
};

function getTimeAgo(dateStr: string): string {
  const now = new Date();
  const date = new Date(dateStr);
  const diffMs = now.getTime() - date.getTime();
  const diffMinutes = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMinutes < 1) return 'ahora';
  if (diffMinutes < 60) return `hace ${diffMinutes} min`;
  if (diffHours < 24) return `hace ${diffHours}h`;
  if (diffDays === 1) return 'hace 1 día';
  return `hace ${diffDays} días`;
}

const formatNumber = (value: number | string): string => {
  const num = typeof value === 'string' ? parseInt(value, 10) : value;
  if (isNaN(num)) return '0';
  return num.toString();
};

export const TradeFairActivity: React.FC = () => {
  const { activity, isLoading, refreshActivity } = useTradeFairActivity();

  // Hide widget when no captures exist and not loading
  if (!isLoading && (!activity || activity.total_captures === 0)) {
    return null;
  }

  return (
    <Card data-testid="trade-fair-activity">
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Actividad Feria Comercial</Typography>
          <Tooltip title="Actualizar">
            <IconButton onClick={refreshActivity} disabled={isLoading} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>

        {isLoading && !activity ? (
          <Box>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              {[1, 2, 3, 4].map((i) => (
                <Grid item xs={6} sm={3} key={i}>
                  <Skeleton variant="rectangular" height={80} />
                </Grid>
              ))}
            </Grid>
            <Skeleton variant="rectangular" height={200} />
          </Box>
        ) : activity ? (
          <>
            {/* KPI Cards */}
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={6} sm={3}>
                <KPICard
                  title="Capturas Totales"
                  value={activity.total_captures}
                  icon={<CameraAltIcon />}
                  formatValue={formatNumber}
                />
              </Grid>
              <Grid item xs={6} sm={3}>
                <KPICard
                  title="Proveedores Creados"
                  value={activity.total_suppliers_created}
                  icon={<BusinessIcon />}
                  formatValue={formatNumber}
                />
              </Grid>
              <Grid item xs={6} sm={3}>
                <KPICard
                  title="Emails Enviados"
                  value={activity.outreach_status?.email_sent ?? 0}
                  icon={<EmailIcon />}
                  formatValue={formatNumber}
                />
              </Grid>
              <Grid item xs={6} sm={3}>
                <KPICard
                  title="Respuestas"
                  value={activity.outreach_status?.responded ?? 0}
                  icon={<ReplyIcon />}
                  formatValue={formatNumber}
                />
              </Grid>
            </Grid>

            {/* Time summary */}
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <Chip label={`Hoy: ${activity.captures_today}`} size="small" variant="outlined" />
              <Chip label={`Últimas 48h: ${activity.captures_last_48h}`} size="small" variant="outlined" />
            </Box>

            {/* Status Breakdown */}
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
              {Object.entries(activity.by_status).map(([status, count]) => (
                <Chip
                  key={status}
                  label={`${STATUS_LABELS[status] || status}: ${count}`}
                  color={STATUS_COLORS[status] || 'default'}
                  size="small"
                />
              ))}
            </Box>

            {/* Recent Captures */}
            {activity.recent_captures.length > 0 && (
              <>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Capturas Recientes
                </Typography>
                <List dense disablePadding>
                  {activity.recent_captures.map((capture) => (
                    <ListItem
                      key={capture.id}
                      sx={{ px: 0, py: 0.5 }}
                      secondaryAction={
                        <Typography variant="caption" color="text.secondary">
                          {getTimeAgo(capture.created_at)}
                        </Typography>
                      }
                    >
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2" fontWeight={600}>
                              {capture.company_name || '—'}
                            </Typography>
                            <Chip
                              label={STATUS_LABELS[capture.status as BusinessCardCaptureStatus] || capture.status}
                              color={STATUS_COLORS[capture.status] || 'default'}
                              size="small"
                              sx={{ height: 20, fontSize: '0.7rem' }}
                            />
                            {capture.outreach_status && capture.outreach_status !== 'none' && (
                              <Chip
                                label={OUTREACH_LABELS[capture.outreach_status] || capture.outreach_status}
                                size="small"
                                variant="outlined"
                                sx={{ height: 20, fontSize: '0.7rem' }}
                              />
                            )}
                          </Box>
                        }
                        secondary={capture.contact_name || '—'}
                      />
                    </ListItem>
                  ))}
                </List>
              </>
            )}
          </>
        ) : null}
      </CardContent>
    </Card>
  );
};

export default TradeFairActivity;
