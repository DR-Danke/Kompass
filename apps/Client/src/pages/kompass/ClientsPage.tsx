import React from 'react';
import { Box, Typography } from '@mui/material';

const ClientsPage: React.FC = () => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="60vh"
    >
      <Typography variant="h4" gutterBottom>
        Clients
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Clients management page - Coming Soon
      </Typography>
    </Box>
  );
};

export default ClientsPage;
