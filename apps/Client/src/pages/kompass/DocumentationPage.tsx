import React, { useState } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Paper,
  Card,
  CardContent,
  CardActionArea,
  Grid,
  Chip,
  TextField,
  InputAdornment,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Button,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import SpeedIcon from '@mui/icons-material/Speed';
import PersonIcon from '@mui/icons-material/Person';
import HelpIcon from '@mui/icons-material/Help';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import LightbulbIcon from '@mui/icons-material/Lightbulb';
import WarningIcon from '@mui/icons-material/Warning';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

// Quick Reference Data
const quickReferenceData = {
  createActions: [
    { action: 'Supplier', path: 'Suppliers > + Add Supplier' },
    { action: 'Product', path: 'Biblia General > + Add Product' },
    { action: 'Category', path: 'Categories > + Add Category' },
    { action: 'Tag', path: 'Categories > Tags > + Add Tag' },
    { action: 'Portfolio', path: 'Portfolios > + Create Portfolio' },
    { action: 'Client', path: 'Clients > + Add Client' },
    { action: 'Quotation', path: 'Quotations > + New Quotation' },
    { action: 'HS Code', path: 'Pricing > HS Codes > + Add' },
    { action: 'Freight Rate', path: 'Pricing > Freight Rates > + Add' },
  ],
  statusFlow: {
    quotation: ['Draft', 'Sent', 'Viewed', 'Negotiating', 'Accepted/Rejected/Expired'],
    client: ['Lead', 'Qualified', 'Quoting', 'Negotiating', 'Won/Lost'],
    product: ['Draft', 'Active', 'Inactive', 'Discontinued'],
  },
  shortcuts: [
    { keys: 'Ctrl/Cmd + K', action: 'Quick search' },
    { keys: 'Esc', action: 'Close modal/dialog' },
    { keys: 'Enter', action: 'Confirm action' },
    { keys: 'Tab', action: 'Next field' },
  ],
};

// FAQ Data
const faqData = [
  {
    category: 'Products',
    questions: [
      {
        q: "Can't find a product I know exists?",
        a: 'Check the Status filter - product might be in Draft status. Reset all filters and search again.',
      },
      {
        q: 'How many products can I have in the catalog?',
        a: "There's no hard limit. Performance may degrade with 10,000+ products.",
      },
      {
        q: 'What image formats are supported?',
        a: 'JPG, PNG, GIF, WebP. Recommended: JPG or PNG under 2MB.',
      },
    ],
  },
  {
    category: 'Quotations',
    questions: [
      {
        q: 'Why is my quotation total showing $0?',
        a: 'Check that line items have quantities > 0 and unit prices > 0. Click Recalculate if available.',
      },
      {
        q: 'How long are share links valid?',
        a: 'Share links expire after 30 days. Generate a new one if needed.',
      },
      {
        q: 'Can I edit a quotation after sending?',
        a: 'Yes, but consider cloning and sending a new version for better audit trail.',
      },
    ],
  },
  {
    category: 'Import',
    questions: [
      {
        q: 'What file formats can I import?',
        a: 'PDF, Excel (.xlsx, .xls), and images (JPG, PNG). Maximum 20MB per file.',
      },
      {
        q: 'Extraction produces garbage data?',
        a: 'Try clearer scans, use Excel format, or import fewer pages at a time.',
      },
    ],
  },
  {
    category: 'Pricing',
    questions: [
      {
        q: 'Tariff not calculating correctly?',
        a: 'Products need HS codes assigned. Edit products and assign appropriate HS codes.',
      },
      {
        q: 'How often should I update the exchange rate?',
        a: 'Weekly, or when it changes significantly (>2%).',
      },
    ],
  },
];

// Workflow guides
const workflowGuides = [
  {
    title: 'Create a Quotation',
    icon: <MenuBookIcon />,
    time: '15 min',
    steps: [
      'Go to Quotations > + New Quotation',
      'Select client (or create new)',
      'Configure incoterm, currency, dates',
      'Add products and set quantities',
      'Review pricing panel',
      'Save and send/share',
    ],
  },
  {
    title: 'Import Products',
    icon: <RocketLaunchIcon />,
    time: '30 min',
    steps: [
      'Go to Import Wizard',
      'Upload PDF/Excel catalog',
      'Wait for AI extraction',
      'Review and correct data',
      'Assign categories/tags',
      'Confirm import',
    ],
  },
  {
    title: 'Build a Portfolio',
    icon: <AccountTreeIcon />,
    time: '20 min',
    steps: [
      'Go to Portfolios > + Create Portfolio',
      'Name it and select target niche',
      'Search and add products',
      'Reorder and add curator notes',
      'Set status to Published',
      'Share link or export PDF',
    ],
  },
];

const DocumentationPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedFaq, setExpandedFaq] = useState<string | false>(false);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleFaqChange = (panel: string) => (_event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpandedFaq(isExpanded ? panel : false);
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Documentation & Help
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Learn how to use Kompass effectively with guides, quick references, and FAQs.
        </Typography>
      </Box>

      {/* Search */}
      <TextField
        fullWidth
        placeholder="Search documentation..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        sx={{ mb: 3, maxWidth: 500 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
        }}
      />

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange} variant="scrollable" scrollButtons="auto">
          <Tab icon={<RocketLaunchIcon />} label="Getting Started" iconPosition="start" />
          <Tab icon={<SpeedIcon />} label="Quick Reference" iconPosition="start" />
          <Tab icon={<PersonIcon />} label="Workflows" iconPosition="start" />
          <Tab icon={<HelpIcon />} label="FAQ" iconPosition="start" />
          <Tab icon={<AccountTreeIcon />} label="Diagrams" iconPosition="start" />
        </Tabs>
      </Paper>

      {/* Getting Started */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          {/* Welcome Card */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3, background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)', color: 'white' }}>
              <Typography variant="h5" gutterBottom>
                Welcome to Kompass!
              </Typography>
              <Typography variant="body1" sx={{ mb: 2, opacity: 0.9 }}>
                The Portfolio & Quotation Automation System for China sourcing businesses.
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Chip label="Import 100 products: 8 hrs → 30 min" sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }} />
                <Chip label="Create quotation: 1 day → 15 min" sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }} />
              </Box>
            </Paper>
          </Grid>

          {/* Role Cards */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <PersonIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">Diana (Design)</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Focus: Products, Portfolios, Import
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon><CheckCircleIcon color="success" fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Import Wizard" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><CheckCircleIcon color="success" fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Biblia General" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><CheckCircleIcon color="success" fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Portfolios" />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <PersonIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">Alejandro (Commercial)</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Focus: Quotations, Clients, Pricing
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon><CheckCircleIcon color="success" fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Quotations" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><CheckCircleIcon color="success" fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Clients Pipeline" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><CheckCircleIcon color="success" fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Pricing Config" />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <PersonIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">Ruben (CEO)</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Focus: Dashboard, Pipeline Overview
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon><CheckCircleIcon color="success" fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Dashboard KPIs" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><CheckCircleIcon color="success" fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Pipeline Review" />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><CheckCircleIcon color="success" fontSize="small" /></ListItemIcon>
                    <ListItemText primary="Quotation Trends" />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* Key Concepts */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
              Key Concepts
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Pricing Formula
              </Typography>
              <Box sx={{ fontFamily: 'monospace', fontSize: '0.85rem', bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
                <div>FOB Price × Qty</div>
                <div>+ Tariff (HS code %)</div>
                <div>+ International Freight</div>
                <div>+ Inspection ($150)</div>
                <div>+ Insurance (1.5%)</div>
                <div>× Exchange Rate (4,200)</div>
                <div>+ National Freight</div>
                <div>+ Nationalization (200K COP)</div>
                <div>+ Margin (20%)</div>
                <Divider sx={{ my: 1 }} />
                <div><strong>= Final Price COP</strong></div>
              </Box>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                Data Relationships
              </Typography>
              <Box sx={{ fontFamily: 'monospace', fontSize: '0.85rem', bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
                <div>Products → Categories (hierarchy)</div>
                <div>Products → Tags (flexible)</div>
                <div>Products → Suppliers</div>
                <div>Products → HS Codes</div>
                <Divider sx={{ my: 1 }} />
                <div>Clients → Niches</div>
                <div>Quotations → Clients</div>
                <div>Portfolios → Niches</div>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Quick Reference */}
      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          {/* Create Actions */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                How to Create
              </Typography>
              <List dense>
                {quickReferenceData.createActions.map((item) => (
                  <ListItem key={item.action}>
                    <ListItemIcon>
                      <ArrowForwardIcon fontSize="small" color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={item.action}
                      secondary={item.path}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>

          {/* Keyboard Shortcuts */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Keyboard Shortcuts
              </Typography>
              <List dense>
                {quickReferenceData.shortcuts.map((item) => (
                  <ListItem key={item.keys}>
                    <Chip label={item.keys} size="small" sx={{ mr: 2, fontFamily: 'monospace' }} />
                    <ListItemText primary={item.action} />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>

          {/* Status Flows */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Status Flows
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="primary" gutterBottom>
                    Quotation Status
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {quickReferenceData.statusFlow.quotation.map((status, idx) => (
                      <React.Fragment key={status}>
                        <Chip label={status} size="small" variant="outlined" />
                        {idx < quickReferenceData.statusFlow.quotation.length - 1 && (
                          <ArrowForwardIcon fontSize="small" sx={{ alignSelf: 'center' }} />
                        )}
                      </React.Fragment>
                    ))}
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="primary" gutterBottom>
                    Client Pipeline
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {quickReferenceData.statusFlow.client.map((status, idx) => (
                      <React.Fragment key={status}>
                        <Chip label={status} size="small" variant="outlined" />
                        {idx < quickReferenceData.statusFlow.client.length - 1 && (
                          <ArrowForwardIcon fontSize="small" sx={{ alignSelf: 'center' }} />
                        )}
                      </React.Fragment>
                    ))}
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Typography variant="subtitle2" color="primary" gutterBottom>
                    Product Status
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {quickReferenceData.statusFlow.product.map((status) => (
                      <Chip key={status} label={status} size="small" variant="outlined" />
                    ))}
                  </Box>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Tips */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2, bgcolor: 'warning.light' }}>
              <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                <LightbulbIcon sx={{ mr: 1, color: 'warning.dark' }} />
                <Box>
                  <Typography variant="subtitle1" fontWeight="bold" color="warning.dark">
                    Pro Tips
                  </Typography>
                  <List dense>
                    <ListItem>
                      <ListItemText primary="Keep the exchange rate updated weekly" />
                    </ListItem>
                    <ListItem>
                      <ListItemText primary="Assign HS codes to products for accurate tariff calculation" />
                    </ListItem>
                    <ListItem>
                      <ListItemText primary="Clone quotations instead of editing old ones" />
                    </ListItem>
                    <ListItem>
                      <ListItemText primary="Use portfolios to speed up quotation creation" />
                    </ListItem>
                  </List>
                </Box>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Workflows */}
      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          {workflowGuides.map((workflow) => (
            <Grid item xs={12} md={4} key={workflow.title}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    {workflow.icon}
                    <Typography variant="h6" sx={{ ml: 1 }}>
                      {workflow.title}
                    </Typography>
                  </Box>
                  <Chip label={workflow.time} size="small" color="primary" variant="outlined" sx={{ mb: 2 }} />
                  <List dense>
                    {workflow.steps.map((step, idx) => (
                      <ListItem key={idx}>
                        <ListItemIcon>
                          <Chip label={idx + 1} size="small" sx={{ minWidth: 24, height: 24 }} />
                        </ListItemIcon>
                        <ListItemText primary={step} />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
          ))}

          {/* Do's and Don'ts */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, bgcolor: 'success.light' }}>
              <Typography variant="h6" gutterBottom color="success.dark">
                Do's
              </Typography>
              <List dense>
                {[
                  'Keep exchange rate updated weekly',
                  'Assign HS codes to products',
                  'Add images to products',
                  'Use descriptive portfolio names',
                  'Add notes when moving pipeline cards',
                ].map((item) => (
                  <ListItem key={item}>
                    <ListItemIcon>
                      <CheckCircleIcon color="success" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary={item} />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2, bgcolor: 'error.light' }}>
              <Typography variant="h6" gutterBottom color="error.dark">
                Don'ts
              </Typography>
              <List dense>
                {[
                  "Create duplicate suppliers (search first)",
                  'Leave products in Draft forever',
                  'Ignore pricing panel warnings',
                  'Share unpublished portfolios',
                  'Delete sent quotations',
                ].map((item) => (
                  <ListItem key={item}>
                    <ListItemIcon>
                      <WarningIcon color="error" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary={item} />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      {/* FAQ */}
      <TabPanel value={tabValue} index={3}>
        {faqData.map((category) => (
          <Box key={category.category} sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom color="primary">
              {category.category}
            </Typography>
            {category.questions.map((faq, idx) => (
              <Accordion
                key={idx}
                expanded={expandedFaq === `${category.category}-${idx}`}
                onChange={handleFaqChange(`${category.category}-${idx}`)}
              >
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography fontWeight="medium">{faq.q}</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography color="text.secondary">{faq.a}</Typography>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        ))}

        {/* Common Errors */}
        <Paper sx={{ p: 2, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Common Error Codes
          </Typography>
          <Grid container spacing={1}>
            {[
              { code: '400', desc: 'Bad request - Check required fields' },
              { code: '401', desc: 'Not authenticated - Log in again' },
              { code: '403', desc: 'Not authorized - Check permissions' },
              { code: '404', desc: 'Not found - Resource does not exist' },
              { code: '422', desc: 'Validation error - Check field formats' },
              { code: '500', desc: 'Server error - Contact admin' },
            ].map((err) => (
              <Grid item xs={12} sm={6} md={4} key={err.code}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Chip label={err.code} size="small" color="error" sx={{ mr: 1 }} />
                  <Typography variant="body2">{err.desc}</Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Paper>
      </TabPanel>

      {/* Diagrams */}
      <TabPanel value={tabValue} index={4}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Visual Workflow Diagrams
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Interactive flowcharts showing system architecture, quotation workflows, pipeline stages, and more.
              </Typography>
              <Button
                variant="contained"
                startIcon={<AccountTreeIcon />}
                onClick={() => window.open('/docs/KOMPASS_WORKFLOW_DIAGRAMS.html', '_blank')}
              >
                Open Workflow Diagrams
              </Button>
            </Paper>
          </Grid>

          {/* Diagram Previews */}
          {[
            { title: 'Quotation Status Flow', desc: 'Draft → Sent → Viewed → Negotiating → Accepted/Rejected' },
            { title: 'Client Pipeline', desc: 'Lead → Qualified → Quoting → Negotiating → Won/Lost' },
            { title: 'Import Workflow', desc: 'Upload → Extract → Review → Confirm → Finalize' },
            { title: 'Pricing Calculation', desc: 'FOB + Tariff + Freight + Costs × Rate + Margin' },
          ].map((diagram) => (
            <Grid item xs={12} sm={6} md={3} key={diagram.title}>
              <Card variant="outlined">
                <CardActionArea sx={{ p: 2 }}>
                  <Typography variant="subtitle1" fontWeight="medium">
                    {diagram.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {diagram.desc}
                  </Typography>
                </CardActionArea>
              </Card>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      {/* Footer */}
      <Divider sx={{ my: 4 }} />
      <Box sx={{ textAlign: 'center', color: 'text.secondary' }}>
        <Typography variant="body2">
          Need more help? Contact your system administrator.
        </Typography>
        <Typography variant="caption">
          Documentation files available in: ai_docs/
        </Typography>
      </Box>
    </Box>
  );
};

export default DocumentationPage;
