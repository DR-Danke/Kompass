import React from 'react';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  Skeleton,
  Typography,
} from '@mui/material';
import {
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  ResponsiveContainer,
} from 'recharts';
import InventoryIcon from '@mui/icons-material/Inventory';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import LocalShippingIcon from '@mui/icons-material/LocalShipping';
import SendIcon from '@mui/icons-material/Send';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useAuth } from '@/hooks/useAuth';
import { useDashboard } from '@/hooks/kompass/useDashboard';
import { KPICard } from '@/components/kompass/KPICard';
import { ActivityFeed } from '@/components/kompass/ActivityFeed';
import { QuickActions } from '@/components/kompass/QuickActions';

const STATUS_COLORS: Record<string, string> = {
  draft: '#9e9e9e',
  sent: '#2196f3',
  viewed: '#03a9f4',
  negotiating: '#ff9800',
  accepted: '#4caf50',
  rejected: '#f44336',
  expired: '#757575',
};

const formatCurrency = (value: number | string): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '$0';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(num);
};

const formatNumber = (value: number | string): string => {
  const num = typeof value === 'string' ? parseInt(value, 10) : value;
  if (isNaN(num)) return '0';
  return new Intl.NumberFormat('en-US').format(num);
};

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const { stats, isLoading, error, refreshStats } = useDashboard();

  const pieChartData = stats
    ? Object.entries(stats.quotationsByStatus)
        .filter(([, count]) => count > 0)
        .map(([status, count]) => ({
          name: status.charAt(0).toUpperCase() + status.slice(1),
          value: count,
          color: STATUS_COLORS[status] || '#888',
        }))
    : [];

  const trendChartData = stats?.quotationTrend.map((point) => ({
    date: new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    sent: point.sent,
    accepted: point.accepted,
  })) || [];

  const topProductsData = stats?.topQuotedProducts.map((product) => ({
    name: product.name.length > 20 ? `${product.name.substring(0, 20)}...` : product.name,
    quotes: product.quoteCount,
  })) || [];

  if (error) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Alert
          severity="error"
          action={
            <Button color="inherit" size="small" onClick={refreshStats} startIcon={<RefreshIcon />}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      </Box>
    );
  }

  return (
    <Box data-testid="dashboard-page">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
            Welcome back, {user?.first_name || user?.email}!
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={refreshStats}
          disabled={isLoading}
        >
          Refresh
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12}>
          <QuickActions />
        </Grid>

        {/* KPI Cards */}
        <Grid item xs={12} sm={6} md={2.4}>
          <KPICard
            title="Total Products"
            value={stats?.kpis.totalProducts ?? 0}
            icon={<InventoryIcon fontSize="large" />}
            isLoading={isLoading}
            formatValue={formatNumber}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <KPICard
            title="Added This Month"
            value={stats?.kpis.productsAddedThisMonth ?? 0}
            icon={<TrendingUpIcon fontSize="large" />}
            isLoading={isLoading}
            formatValue={formatNumber}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <KPICard
            title="Active Suppliers"
            value={stats?.kpis.activeSuppliers ?? 0}
            icon={<LocalShippingIcon fontSize="large" />}
            isLoading={isLoading}
            formatValue={formatNumber}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <KPICard
            title="Quotations This Week"
            value={stats?.kpis.quotationsSentThisWeek ?? 0}
            icon={<SendIcon fontSize="large" />}
            isLoading={isLoading}
            formatValue={formatNumber}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2.4}>
          <KPICard
            title="Pipeline Value"
            value={stats?.kpis.pipelineValue ?? 0}
            icon={<AttachMoneyIcon fontSize="large" />}
            isLoading={isLoading}
            formatValue={formatCurrency}
          />
        </Grid>

        {/* Charts Row */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: 350 }} data-testid="chart-quotations-by-status">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quotations by Status
              </Typography>
              {isLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 250 }}>
                  <Skeleton variant="circular" width={200} height={200} />
                </Box>
              ) : pieChartData.length === 0 ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 250 }}>
                  <Typography color="text.secondary">No quotations yet</Typography>
                </Box>
              ) : (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={pieChartData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      label={({ name, percent }) => `${name} (${((percent ?? 0) * 100).toFixed(0)}%)`}
                    >
                      {pieChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ height: 350 }} data-testid="chart-quotations-trend">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quotation Trend (30 Days)
              </Typography>
              {isLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 250 }}>
                  <Skeleton variant="rectangular" width="100%" height={200} />
                </Box>
              ) : trendChartData.length === 0 ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 250 }}>
                  <Typography color="text.secondary">No trend data available</Typography>
                </Box>
              ) : (
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={trendChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="sent" stroke="#2196f3" name="Sent" />
                    <Line type="monotone" dataKey="accepted" stroke="#4caf50" name="Accepted" />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ height: 350 }} data-testid="chart-top-products">
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Quoted Products
              </Typography>
              {isLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 250 }}>
                  <Skeleton variant="rectangular" width="100%" height={200} />
                </Box>
              ) : topProductsData.length === 0 ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 250 }}>
                  <Typography color="text.secondary">No quoted products yet</Typography>
                </Box>
              ) : (
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={topProductsData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" allowDecimals={false} />
                    <YAxis dataKey="name" type="category" width={100} tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="quotes" fill="#8884d8" name="Quote Count" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Activity Feed */}
        <Grid item xs={12}>
          <ActivityFeed
            recentProducts={stats?.recentProducts ?? []}
            recentQuotations={stats?.recentQuotations ?? []}
            recentClients={stats?.recentClients ?? []}
            isLoading={isLoading}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;
