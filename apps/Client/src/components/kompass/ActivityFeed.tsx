import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Chip,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Skeleton,
  Tab,
  Tabs,
  Typography,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import type {
  RecentProduct,
  RecentQuotation,
  RecentClient,
  QuotationStatus,
  ClientStatus,
} from '@/types/kompass';

interface ActivityFeedProps {
  recentProducts: RecentProduct[];
  recentQuotations: RecentQuotation[];
  recentClients: RecentClient[];
  isLoading?: boolean;
}

type TabValue = 'products' | 'quotations' | 'clients';

const statusColors: Record<QuotationStatus | ClientStatus, 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'> = {
  draft: 'default',
  sent: 'info',
  viewed: 'primary',
  negotiating: 'warning',
  accepted: 'success',
  rejected: 'error',
  expired: 'default',
  lead: 'default',
  qualified: 'info',
  quoting: 'primary',
  won: 'success',
  lost: 'error',
};

const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    return 'Today';
  } else if (diffDays === 1) {
    return 'Yesterday';
  } else if (diffDays < 7) {
    return `${diffDays} days ago`;
  } else {
    return date.toLocaleDateString();
  }
};

export const ActivityFeed: React.FC<ActivityFeedProps> = ({
  recentProducts,
  recentQuotations,
  recentClients,
  isLoading = false,
}) => {
  const [tab, setTab] = useState<TabValue>('products');
  const navigate = useNavigate();

  const handleTabChange = (_: React.SyntheticEvent, newValue: TabValue) => {
    setTab(newValue);
  };

  const renderSkeleton = () => (
    <List disablePadding>
      {[1, 2, 3, 4, 5].map((i) => (
        <ListItem key={i} disablePadding>
          <ListItemButton disabled>
            <ListItemText
              primary={<Skeleton variant="text" width="60%" />}
              secondary={<Skeleton variant="text" width="40%" />}
            />
          </ListItemButton>
        </ListItem>
      ))}
    </List>
  );

  const renderEmptyState = (message: string) => (
    <Box sx={{ py: 4, textAlign: 'center' }}>
      <Typography variant="body2" color="text.secondary">
        {message}
      </Typography>
    </Box>
  );

  const renderProducts = () => {
    if (isLoading) return renderSkeleton();
    if (recentProducts.length === 0) return renderEmptyState('No products added yet');

    return (
      <List disablePadding data-testid="activity-feed-products">
        {recentProducts.map((product) => (
          <ListItem key={product.id} disablePadding>
            <ListItemButton onClick={() => navigate('/products')}>
              <ListItemText
                primary={product.name}
                secondary={
                  <Box component="span" sx={{ display: 'flex', gap: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      {product.sku}
                    </Typography>
                    {product.supplierName && (
                      <>
                        <Typography variant="caption" color="text.secondary">
                          |
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {product.supplierName}
                        </Typography>
                      </>
                    )}
                    <Typography variant="caption" color="text.secondary">
                      | {formatDate(product.createdAt)}
                    </Typography>
                  </Box>
                }
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    );
  };

  const renderQuotations = () => {
    if (isLoading) return renderSkeleton();
    if (recentQuotations.length === 0) return renderEmptyState('No quotations created yet');

    return (
      <List disablePadding data-testid="activity-feed-quotations">
        {recentQuotations.map((quotation) => (
          <ListItem key={quotation.id} disablePadding>
            <ListItemButton onClick={() => navigate(`/quotations/${quotation.id}`)}>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2">{quotation.quotationNumber}</Typography>
                    <Chip
                      label={quotation.status}
                      size="small"
                      color={statusColors[quotation.status] || 'default'}
                    />
                  </Box>
                }
                secondary={
                  <Box component="span" sx={{ display: 'flex', gap: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      {quotation.clientName || 'No client'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      | {formatDate(quotation.createdAt)}
                    </Typography>
                  </Box>
                }
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    );
  };

  const renderClients = () => {
    if (isLoading) return renderSkeleton();
    if (recentClients.length === 0) return renderEmptyState('No clients added yet');

    return (
      <List disablePadding data-testid="activity-feed-clients">
        {recentClients.map((client) => (
          <ListItem key={client.id} disablePadding>
            <ListItemButton onClick={() => navigate('/pipeline')}>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2">{client.companyName}</Typography>
                    <Chip
                      label={client.status}
                      size="small"
                      color={statusColors[client.status] || 'default'}
                    />
                  </Box>
                }
                secondary={
                  <Typography variant="caption" color="text.secondary">
                    {formatDate(client.createdAt)}
                  </Typography>
                }
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    );
  };

  return (
    <Card data-testid="activity-feed">
      <CardContent sx={{ pb: 1 }}>
        <Typography variant="h6" gutterBottom>
          Recent Activity
        </Typography>
        <Tabs
          value={tab}
          onChange={handleTabChange}
          sx={{ borderBottom: 1, borderColor: 'divider', mb: 1 }}
        >
          <Tab label="Products" value="products" data-testid="tab-products" />
          <Tab label="Quotations" value="quotations" data-testid="tab-quotations" />
          <Tab label="Clients" value="clients" data-testid="tab-clients" />
        </Tabs>
        {tab === 'products' && renderProducts()}
        {tab === 'quotations' && renderQuotations()}
        {tab === 'clients' && renderClients()}
      </CardContent>
    </Card>
  );
};

export default ActivityFeed;
