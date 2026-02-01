import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';
import { useAuth } from './hooks/useAuth';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { MainLayout } from './components/layout/MainLayout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import SuppliersPage from './pages/kompass/SuppliersPage';
import ProductsPage from './pages/kompass/ProductsPage';
import PortfoliosPage from './pages/kompass/PortfoliosPage';
import ClientsPage from './pages/kompass/ClientsPage';
import QuotationsPage from './pages/kompass/QuotationsPage';
import SettingsPage from './pages/kompass/SettingsPage';
import ImportWizardPage from './pages/kompass/ImportWizardPage';

function App() {
  const { isLoading } = useAuth();

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />

      {/* Protected routes */}
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Routes>
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="suppliers" element={<SuppliersPage />} />
                <Route path="products" element={<ProductsPage />} />
                <Route path="import-wizard" element={<ImportWizardPage />} />
                <Route path="portfolios" element={<PortfoliosPage />} />
                <Route path="clients" element={<ClientsPage />} />
                <Route path="quotations" element={<QuotationsPage />} />
                <Route path="settings" element={<SettingsPage />} />
              </Routes>
            </MainLayout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;
