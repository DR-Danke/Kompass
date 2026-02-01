import React from 'react';
import { Box, Typography } from '@mui/material';

const ProductsPage: React.FC = () => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="60vh"
    >
      <Typography variant="h4" gutterBottom>
        Biblia General
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Products catalog page - Coming Soon
      </Typography>
    </Box>
  );
};

export default ProductsPage;
