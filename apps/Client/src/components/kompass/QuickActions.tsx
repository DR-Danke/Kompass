import React from 'react';
import { Box, Button, Card, CardContent, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import DescriptionIcon from '@mui/icons-material/Description';
import UploadFileIcon from '@mui/icons-material/UploadFile';

export const QuickActions: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Card data-testid="quick-actions">
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/products')}
            data-testid="quick-action-add-product"
          >
            Add Product
          </Button>
          <Button
            variant="contained"
            color="secondary"
            startIcon={<DescriptionIcon />}
            onClick={() => navigate('/quotations/new')}
            data-testid="quick-action-create-quotation"
          >
            Create Quotation
          </Button>
          <Button
            variant="outlined"
            startIcon={<UploadFileIcon />}
            onClick={() => navigate('/import-wizard')}
            data-testid="quick-action-import-catalog"
          >
            Import Catalog
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default QuickActions;
