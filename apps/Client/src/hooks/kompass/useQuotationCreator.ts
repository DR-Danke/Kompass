import { useState, useCallback, useEffect, useRef } from 'react';
import { quotationService } from '@/services/kompassService';
import type {
  QuotationResponse,
  QuotationCreate,
  QuotationUpdate,
  QuotationItemCreate,
  QuotationPricing,
  ClientResponse,
  ProductResponse,
  Incoterm,
  QuotationSendEmailRequest,
  QuotationSendEmailResponse,
  QuotationShareTokenResponse,
} from '@/types/kompass';

export interface LineItem {
  id?: string;
  tempId: string;
  product_id: string | null;
  product: ProductResponse | null;
  sku: string | null;
  product_name: string;
  description: string | null;
  quantity: number;
  unit_of_measure: string;
  unit_cost: number;
  unit_price: number;
  unit_price_override: number | null;
  hs_code: string | null;
  line_total: number;
  sort_order: number;
  notes: string | null;
}

export interface QuotationSettings {
  incoterm: Incoterm;
  currency: string;
  freight_cost: number;
  insurance_cost: number;
  other_costs: number;
  discount_percent: number;
  margin_percent: number;
  notes: string;
  terms_and_conditions: string;
  valid_days: number;
}

export interface UseQuotationCreatorState {
  quotationId: string | null;
  quotationNumber: string | null;
  selectedClient: ClientResponse | null;
  lineItems: LineItem[];
  settings: QuotationSettings;
  pricing: QuotationPricing | null;
  isLoading: boolean;
  isSaving: boolean;
  isCalculating: boolean;
  error: string | null;
  isDirty: boolean;
}

export interface UseQuotationCreatorReturn extends UseQuotationCreatorState {
  loadQuotation: (id: string) => Promise<void>;
  setClient: (client: ClientResponse | null) => void;
  addItem: (product: ProductResponse, quantity?: number) => void;
  updateItem: (tempId: string, updates: Partial<LineItem>) => void;
  removeItem: (tempId: string) => void;
  updateSettings: (updates: Partial<QuotationSettings>) => void;
  calculatePricing: () => Promise<void>;
  saveQuotation: () => Promise<QuotationResponse>;
  exportPdf: () => Promise<Blob>;
  sendEmail: (request: QuotationSendEmailRequest) => Promise<QuotationSendEmailResponse>;
  getShareToken: () => Promise<QuotationShareTokenResponse>;
  resetForm: () => void;
  canSave: boolean;
  canCalculate: boolean;
}

const DEFAULT_SETTINGS: QuotationSettings = {
  incoterm: 'FOB',
  currency: 'USD',
  freight_cost: 0,
  insurance_cost: 0,
  other_costs: 0,
  discount_percent: 0,
  margin_percent: 15,
  notes: '',
  terms_and_conditions: '',
  valid_days: 30,
};

let tempIdCounter = 0;
const generateTempId = () => `temp-${++tempIdCounter}-${Date.now()}`;

export function useQuotationCreator(initialQuotationId?: string): UseQuotationCreatorReturn {
  const [quotationId, setQuotationId] = useState<string | null>(initialQuotationId || null);
  const [quotationNumber, setQuotationNumber] = useState<string | null>(null);
  const [selectedClient, setSelectedClient] = useState<ClientResponse | null>(null);
  const [lineItems, setLineItems] = useState<LineItem[]>([]);
  const [settings, setSettings] = useState<QuotationSettings>(DEFAULT_SETTINGS);
  const [pricing, setPricing] = useState<QuotationPricing | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);

  const isInitialLoad = useRef(true);

  const loadQuotation = useCallback(async (id: string) => {
    console.log(`INFO [useQuotationCreator]: Loading quotation ${id}`);
    setIsLoading(true);
    setError(null);

    try {
      const quotation = await quotationService.get(id);
      setQuotationId(quotation.id);
      setQuotationNumber(quotation.quotation_number);

      // Set client info (basic info from quotation, full client details may need separate fetch)
      if (quotation.client_id) {
        setSelectedClient({
          id: quotation.client_id,
          company_name: quotation.client_name || '',
          contact_name: null,
          email: null,
          phone: null,
          whatsapp: null,
          address: null,
          city: null,
          state: null,
          country: null,
          postal_code: null,
          niche_id: null,
          niche_name: null,
          status: 'lead',
          notes: null,
          assigned_to: null,
          assigned_to_name: null,
          source: null,
          project_deadline: null,
          project_name: null,
          incoterm_preference: null,
          created_at: '',
          updated_at: '',
        });
      }

      // Convert quotation items to LineItem format
      const items: LineItem[] = quotation.items.map((item) => ({
        id: item.id,
        tempId: generateTempId(),
        product_id: item.product_id,
        product: null,
        sku: item.sku,
        product_name: item.product_name,
        description: item.description,
        quantity: item.quantity,
        unit_of_measure: item.unit_of_measure,
        unit_cost: typeof item.unit_cost === 'string' ? parseFloat(item.unit_cost) : item.unit_cost,
        unit_price: typeof item.unit_price === 'string' ? parseFloat(item.unit_price) : item.unit_price,
        unit_price_override: null,
        hs_code: null,
        line_total: typeof item.line_total === 'string' ? parseFloat(item.line_total) : item.line_total,
        sort_order: item.sort_order,
        notes: item.notes,
      }));
      setLineItems(items);

      // Set settings
      setSettings({
        incoterm: quotation.incoterm,
        currency: quotation.currency,
        freight_cost: typeof quotation.freight_cost === 'string' ? parseFloat(quotation.freight_cost) : quotation.freight_cost,
        insurance_cost: typeof quotation.insurance_cost === 'string' ? parseFloat(quotation.insurance_cost) : quotation.insurance_cost,
        other_costs: typeof quotation.other_costs === 'string' ? parseFloat(quotation.other_costs) : quotation.other_costs,
        discount_percent: typeof quotation.discount_percent === 'string' ? parseFloat(quotation.discount_percent) : quotation.discount_percent,
        margin_percent: DEFAULT_SETTINGS.margin_percent,
        notes: quotation.notes || '',
        terms_and_conditions: quotation.terms_and_conditions || '',
        valid_days: 30,
      });

      setIsDirty(false);
      isInitialLoad.current = false;
      console.log('INFO [useQuotationCreator]: Quotation loaded successfully');
    } catch (err) {
      console.error('ERROR [useQuotationCreator]: Failed to load quotation:', err);
      setError(err instanceof Error ? err.message : 'Failed to load quotation');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load initial quotation if ID provided
  useEffect(() => {
    if (initialQuotationId && isInitialLoad.current) {
      loadQuotation(initialQuotationId);
    }
  }, [initialQuotationId, loadQuotation]);

  const setClient = useCallback((client: ClientResponse | null) => {
    console.log(`INFO [useQuotationCreator]: Setting client to ${client?.company_name || 'none'}`);
    setSelectedClient(client);
    setIsDirty(true);
  }, []);

  const addItem = useCallback((product: ProductResponse, quantity = 1) => {
    console.log(`INFO [useQuotationCreator]: Adding product ${product.name}`);

    // Check if product already in list
    const exists = lineItems.some((item) => item.product_id === product.id);
    if (exists) {
      console.log('INFO [useQuotationCreator]: Product already in quote, incrementing quantity');
      setLineItems((prev) =>
        prev.map((item) =>
          item.product_id === product.id
            ? { ...item, quantity: item.quantity + quantity, line_total: (item.quantity + quantity) * item.unit_price }
            : item
        )
      );
    } else {
      const unitPrice = typeof product.unit_price === 'string' ? parseFloat(product.unit_price) : product.unit_price;
      const unitCost = typeof product.unit_cost === 'string' ? parseFloat(product.unit_cost) : product.unit_cost;

      const newItem: LineItem = {
        tempId: generateTempId(),
        product_id: product.id,
        product: product,
        sku: product.sku,
        product_name: product.name,
        description: product.description,
        quantity: quantity,
        unit_of_measure: product.unit_of_measure,
        unit_cost: unitCost,
        unit_price: unitPrice,
        unit_price_override: null,
        hs_code: product.hs_code,
        line_total: quantity * unitPrice,
        sort_order: lineItems.length,
        notes: null,
      };
      setLineItems((prev) => [...prev, newItem]);
    }
    setIsDirty(true);
  }, [lineItems]);

  const updateItem = useCallback((tempId: string, updates: Partial<LineItem>) => {
    console.log(`INFO [useQuotationCreator]: Updating item ${tempId}`);
    setLineItems((prev) =>
      prev.map((item) => {
        if (item.tempId !== tempId) return item;

        const updated = { ...item, ...updates };

        // Recalculate line total if quantity or price changed
        const effectivePrice = updated.unit_price_override ?? updated.unit_price;
        updated.line_total = updated.quantity * effectivePrice;

        return updated;
      })
    );
    setIsDirty(true);
  }, []);

  const removeItem = useCallback((tempId: string) => {
    console.log(`INFO [useQuotationCreator]: Removing item ${tempId}`);
    setLineItems((prev) => prev.filter((item) => item.tempId !== tempId));
    setIsDirty(true);
  }, []);

  const updateSettings = useCallback((updates: Partial<QuotationSettings>) => {
    console.log('INFO [useQuotationCreator]: Updating settings');
    setSettings((prev) => ({ ...prev, ...updates }));
    setIsDirty(true);
  }, []);

  const calculatePricing = useCallback(async () => {
    if (!quotationId) {
      console.log('INFO [useQuotationCreator]: Cannot calculate - no quotation saved yet');
      setError('Please save the quotation first before calculating pricing');
      return;
    }

    console.log('INFO [useQuotationCreator]: Calculating pricing');
    setIsCalculating(true);
    setError(null);

    try {
      const result = await quotationService.calculate(quotationId);
      setPricing(result);
      console.log('INFO [useQuotationCreator]: Pricing calculated successfully');
    } catch (err) {
      console.error('ERROR [useQuotationCreator]: Failed to calculate pricing:', err);
      setError(err instanceof Error ? err.message : 'Failed to calculate pricing');
    } finally {
      setIsCalculating(false);
    }
  }, [quotationId]);

  const saveQuotation = useCallback(async (): Promise<QuotationResponse> => {
    if (!selectedClient) {
      throw new Error('Please select a client');
    }
    if (lineItems.length === 0) {
      throw new Error('Please add at least one product');
    }

    console.log('INFO [useQuotationCreator]: Saving quotation');
    setIsSaving(true);
    setError(null);

    try {
      const validFrom = new Date().toISOString().split('T')[0];
      const validUntil = new Date(Date.now() + settings.valid_days * 24 * 60 * 60 * 1000)
        .toISOString()
        .split('T')[0];

      const items: QuotationItemCreate[] = lineItems.map((item, index) => ({
        product_id: item.product_id,
        sku: item.sku,
        product_name: item.product_name,
        description: item.description,
        quantity: item.quantity,
        unit_of_measure: item.unit_of_measure,
        unit_cost: item.unit_cost,
        unit_price: item.unit_price_override ?? item.unit_price,
        sort_order: index,
        notes: item.notes,
      }));

      let result: QuotationResponse;

      if (quotationId) {
        // Update existing quotation
        const updateData: QuotationUpdate = {
          incoterm: settings.incoterm,
          currency: settings.currency,
          freight_cost: settings.freight_cost,
          insurance_cost: settings.insurance_cost,
          other_costs: settings.other_costs,
          discount_percent: settings.discount_percent,
          notes: settings.notes || null,
          terms_and_conditions: settings.terms_and_conditions || null,
          valid_from: validFrom,
          valid_until: validUntil,
        };
        result = await quotationService.update(quotationId, updateData);

        // Update items - delete existing and add new
        const existingQuotation = await quotationService.get(quotationId);
        for (const existingItem of existingQuotation.items) {
          await quotationService.deleteItem(quotationId, existingItem.id);
        }
        for (const item of items) {
          await quotationService.addItem(quotationId, item);
        }

        // Refetch to get updated data
        result = await quotationService.get(quotationId);
      } else {
        // Create new quotation
        const createData: QuotationCreate = {
          client_id: selectedClient.id,
          status: 'draft',
          incoterm: settings.incoterm,
          currency: settings.currency,
          freight_cost: settings.freight_cost,
          insurance_cost: settings.insurance_cost,
          other_costs: settings.other_costs,
          discount_percent: settings.discount_percent,
          notes: settings.notes || null,
          terms_and_conditions: settings.terms_and_conditions || null,
          valid_from: validFrom,
          valid_until: validUntil,
          items: items,
        };
        result = await quotationService.create(createData);
        setQuotationId(result.id);
        setQuotationNumber(result.quotation_number);
      }

      setIsDirty(false);
      console.log(`INFO [useQuotationCreator]: Quotation saved with ID ${result.id}`);
      return result;
    } catch (err) {
      console.error('ERROR [useQuotationCreator]: Failed to save quotation:', err);
      const message = err instanceof Error ? err.message : 'Failed to save quotation';
      setError(message);
      throw err;
    } finally {
      setIsSaving(false);
    }
  }, [selectedClient, lineItems, settings, quotationId]);

  const exportPdf = useCallback(async (): Promise<Blob> => {
    if (!quotationId) {
      throw new Error('Please save the quotation first');
    }

    console.log('INFO [useQuotationCreator]: Exporting PDF');
    try {
      return await quotationService.exportPdf(quotationId);
    } catch (err) {
      console.error('ERROR [useQuotationCreator]: Failed to export PDF:', err);
      throw err;
    }
  }, [quotationId]);

  const sendEmail = useCallback(async (
    request: QuotationSendEmailRequest
  ): Promise<QuotationSendEmailResponse> => {
    if (!quotationId) {
      throw new Error('Please save the quotation first');
    }

    console.log('INFO [useQuotationCreator]: Sending email');
    try {
      return await quotationService.sendEmail(quotationId, request);
    } catch (err) {
      console.error('ERROR [useQuotationCreator]: Failed to send email:', err);
      throw err;
    }
  }, [quotationId]);

  const getShareToken = useCallback(async (): Promise<QuotationShareTokenResponse> => {
    if (!quotationId) {
      throw new Error('Please save the quotation first');
    }

    console.log('INFO [useQuotationCreator]: Getting share token');
    try {
      return await quotationService.getShareToken(quotationId);
    } catch (err) {
      console.error('ERROR [useQuotationCreator]: Failed to get share token:', err);
      throw err;
    }
  }, [quotationId]);

  const resetForm = useCallback(() => {
    console.log('INFO [useQuotationCreator]: Resetting form');
    setQuotationId(null);
    setQuotationNumber(null);
    setSelectedClient(null);
    setLineItems([]);
    setSettings(DEFAULT_SETTINGS);
    setPricing(null);
    setError(null);
    setIsDirty(false);
    isInitialLoad.current = true;
  }, []);

  const canSave = selectedClient !== null && lineItems.length > 0;
  const canCalculate = quotationId !== null && lineItems.length > 0;

  return {
    quotationId,
    quotationNumber,
    selectedClient,
    lineItems,
    settings,
    pricing,
    isLoading,
    isSaving,
    isCalculating,
    error,
    isDirty,
    loadQuotation,
    setClient,
    addItem,
    updateItem,
    removeItem,
    updateSettings,
    calculatePricing,
    saveQuotation,
    exportPdf,
    sendEmail,
    getShareToken,
    resetForm,
    canSave,
    canCalculate,
  };
}
