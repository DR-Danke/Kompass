-- =============================================================================
-- Migration: Add Business Card Captures table and Trade Fair columns to Suppliers
-- =============================================================================

-- =============================================================================
-- BUSINESS CARD CAPTURES TABLE
-- =============================================================================

DROP TABLE IF EXISTS business_card_captures CASCADE;

CREATE TABLE IF NOT EXISTS business_card_captures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    image_url VARCHAR(2000) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' NOT NULL
        CHECK (status IN ('pending', 'processing', 'extracted', 'confirmed', 'rejected', 'failed')),

    -- Extracted contact fields (populated by AI in TF-002)
    company_name VARCHAR(255),
    contact_name VARCHAR(200),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(100),
    contact_wechat VARCHAR(100),
    website VARCHAR(500),
    address TEXT,

    -- Linked supplier (populated after supplier creation in TF-003)
    supplier_id UUID REFERENCES suppliers(id) ON DELETE SET NULL,

    -- Capture metadata
    fair_name VARCHAR(255),
    notes TEXT,
    captured_by UUID REFERENCES users(id) ON DELETE SET NULL,
    extraction_raw_response JSONB,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_business_card_captures_status ON business_card_captures(status);
CREATE INDEX IF NOT EXISTS idx_business_card_captures_supplier_id ON business_card_captures(supplier_id);
CREATE INDEX IF NOT EXISTS idx_business_card_captures_created_at ON business_card_captures(created_at);

-- Auto-update trigger
CREATE OR REPLACE TRIGGER update_business_card_captures_updated_at
    BEFORE UPDATE ON business_card_captures
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- ADD TRADE FAIR COLUMNS TO SUPPLIERS
-- =============================================================================

ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS source VARCHAR(50);
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS fair_name VARCHAR(255);
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS capture_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS outreach_status VARCHAR(20) DEFAULT 'none'
    CHECK (outreach_status IS NULL OR outreach_status IN ('none', 'pending', 'contacted', 'responded', 'meeting_scheduled', 'completed'));
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS wechat_id VARCHAR(100);
