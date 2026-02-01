import React from 'react';
import { Box, Typography } from '@mui/material';

const PortfoliosPage: React.FC = () => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="60vh"
    >
      <Typography variant="h4" gutterBottom>
        Portfolios
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Portfolios management page - Coming Soon
      </Typography>
    </Box>
  );
};

export default PortfoliosPage;
