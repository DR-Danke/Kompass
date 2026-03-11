-- =============================================================================
-- Migration: Add Outreach Templates Table
-- =============================================================================
-- Stores editable outreach email templates that were previously hardcoded
-- in email_service.py. Seeded with the 3 existing templates.

CREATE TABLE IF NOT EXISTS outreach_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_outreach_templates_key ON outreach_templates(key);
CREATE INDEX IF NOT EXISTS idx_outreach_templates_is_active ON outreach_templates(is_active);

-- Auto-update trigger for updated_at
CREATE OR REPLACE TRIGGER update_outreach_templates_updated_at
    BEFORE UPDATE ON outreach_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Seed with the 3 existing hardcoded templates
INSERT INTO outreach_templates (key, name, subject, body, sort_order)
VALUES
    (
        'introduction',
        'Presentación inicial',
        'Nice meeting you at {fair_name} — Kompass',
        E'Dear {contact_name},\n\nIt was a pleasure meeting you at {fair_name}. Thank you for taking the time to share your products and capabilities with us.\n\nWe are Kompass, a sourcing and trading company specializing in connecting quality manufacturers with buyers across Latin America and beyond. We are always looking for reliable partners who share our commitment to quality and competitive pricing.\n\nWe would love to explore potential collaboration opportunities with {company_name}. Could we schedule a follow-up call or exchange catalogs to discuss how we might work together?\n\nLooking forward to hearing from you.\n\nBest regards,\n{sender_name}\nKompass Trading',
        0
    ),
    (
        'follow_up_catalog',
        'Solicitud de catálogo',
        'Product catalog request — Kompass × {company_name}',
        E'Dear {contact_name},\n\nI hope this message finds you well. We met at {fair_name} and I wanted to follow up on our conversation.\n\nWe are very interested in {company_name}''s product range and would love to receive your latest product catalog, including pricing information if available.\n\nThis will help us identify the best products for our Latin American buyers and move forward with potential orders.\n\nThank you in advance for your time.\n\nBest regards,\n{sender_name}\nKompass Trading',
        1
    ),
    (
        'follow_up_pricing',
        'Solicitud de precios',
        'Pricing inquiry — Kompass × {company_name}',
        E'Dear {contact_name},\n\nThank you for sharing your catalog with us. We have reviewed your products and are interested in obtaining detailed pricing for the following:\n\n- FOB pricing per unit (USD)\n- Minimum order quantities (MOQ)\n- Lead times for production\n- Available packaging options\n\nWe are planning to place orders for the Latin American market and would appreciate a competitive quotation from {company_name}.\n\nPlease let us know if you need any additional information from our side.\n\nBest regards,\n{sender_name}\nKompass Trading',
        2
    )
ON CONFLICT (key) DO NOTHING;
