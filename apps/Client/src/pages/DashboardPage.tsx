import React from 'react';
import { Box, Typography, Card, CardContent, Grid } from '@mui/material';
import { useAuth } from '@/hooks/useAuth';

const DashboardPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Welcome back, {user?.first_name || user?.email}!
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Card 1
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Add your dashboard content here.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Card 2
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Add your dashboard content here.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Card 3
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Add your dashboard content here.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;
