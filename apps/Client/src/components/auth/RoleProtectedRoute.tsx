import React from 'react';
import { Navigate } from 'react-router-dom';
import { Box, Typography, Button, CircularProgress } from '@mui/material';
import BlockIcon from '@mui/icons-material/Block';
import { useAuth } from '@/hooks/useAuth';

interface RoleProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles: string[];
}

export const RoleProtectedRoute: React.FC<RoleProtectedRouteProps> = ({
  children,
  allowedRoles,
}) => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!isAuthenticated) {
    console.log('INFO [RoleProtectedRoute]: User not authenticated, redirecting to login');
    return <Navigate to="/login" replace />;
  }

  if (!user || !allowedRoles.includes(user.role)) {
    console.log('INFO [RoleProtectedRoute]: User role not allowed:', user?.role);
    return (
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="80vh"
        textAlign="center"
        p={4}
      >
        <BlockIcon sx={{ fontSize: 80, color: 'error.main', mb: 2 }} />
        <Typography variant="h4" gutterBottom>
          Access Denied
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          You don't have permission to access this page.
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Your role: <strong>{user?.role}</strong>
        </Typography>
        <Box display="flex" gap={2}>
          <Button variant="contained" href="/dashboard">
            Go to Dashboard
          </Button>
          <Button variant="outlined" href="/">
            Go Home
          </Button>
        </Box>
      </Box>
    );
  }

  return <>{children}</>;
};
