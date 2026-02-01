import React from 'react';
import { Box, Typography } from '@mui/material';

const SettingsPage: React.FC = () => {
  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="60vh"
    >
      <Typography variant="h4" gutterBottom>
        Kompass Settings
      </Typography>
      <Typography variant="body1" color="text.secondary">
        Kompass settings page - Coming Soon
      </Typography>
    </Box>
  );
};

export default SettingsPage;
