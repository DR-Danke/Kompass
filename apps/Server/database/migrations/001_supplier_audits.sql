-- =============================================================================
-- Migration 001: Supplier Audits Schema
-- =============================================================================
-- Purpose: Add supplier_audits table and certification columns to suppliers
-- Run this migration with: psql $DATABASE_URL -f database/migrations/001_supplier_audits.sql
--
-- This migration is idempotent and can be re-run safely using IF NOT EXISTS patterns.

-- =============================================================================
-- SUPPLIER AUDITS TABLE
-- =============================================================================
-- Stores factory audit documents and extracted data for supplier qualification

CREATE TABLE IF NOT EXISTS supplier_audits (
    -- Primary key and foreign key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id UUID NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,

    -- Document metadata
    audit_type VARCHAR(50) NOT NULL DEFAULT 'factory_audit'
        CHECK (audit_type IN ('factory_audit', 'container_inspection')),
    document_url VARCHAR(1000) NOT NULL,
    document_name VARCHAR(255),
    file_size_bytes BIGINT,

    -- Extracted data fields
    supplier_type VARCHAR(50) CHECK (supplier_type IS NULL OR supplier_type IN ('manufacturer', 'trader', 'unknown')),
    employee_count INTEGER CHECK (employee_count IS NULL OR employee_count >= 0),
    factory_area_sqm INTEGER CHECK (factory_area_sqm IS NULL OR factory_area_sqm >= 0),
    production_lines_count INTEGER CHECK (production_lines_count IS NULL OR production_lines_count >= 0),
    markets_served JSONB,
    certifications TEXT[],
    has_machinery_photos BOOLEAN DEFAULT false,
    positive_points TEXT[],
    negative_points TEXT[],
    products_verified TEXT[],

    -- Audit metadata
    audit_date DATE,
    inspector_name VARCHAR(255),

    -- Processing fields
    extraction_status VARCHAR(50) DEFAULT 'pending' NOT NULL
        CHECK (extraction_status IN ('pending', 'processing', 'completed', 'failed')),
    extraction_raw_response JSONB,
    extracted_at TIMESTAMP WITH TIME ZONE,

    -- Classification fields
    ai_classification VARCHAR(10) CHECK (ai_classification IS NULL OR ai_classification IN ('A', 'B', 'C')),
    ai_classification_reason TEXT,
    manual_classification VARCHAR(10) CHECK (manual_classification IS NULL OR manual_classification IN ('A', 'B', 'C')),
    classification_notes TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_supplier_audits_supplier_id ON supplier_audits(supplier_id);
CREATE INDEX IF NOT EXISTS idx_supplier_audits_audit_type ON supplier_audits(audit_type);
CREATE INDEX IF NOT EXISTS idx_supplier_audits_extraction_status ON supplier_audits(extraction_status);
CREATE INDEX IF NOT EXISTS idx_supplier_audits_ai_classification ON supplier_audits(ai_classification);
CREATE INDEX IF NOT EXISTS idx_supplier_audits_manual_classification ON supplier_audits(manual_classification);
CREATE INDEX IF NOT EXISTS idx_supplier_audits_created_at ON supplier_audits(created_at);

-- Auto-update trigger for updated_at
CREATE OR REPLACE TRIGGER update_supplier_audits_updated_at
    BEFORE UPDATE ON supplier_audits
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- ALTER SUPPLIERS TABLE - Add certification columns
-- =============================================================================

-- Certification status: tracks the supplier's certification level
ALTER TABLE suppliers
    ADD COLUMN IF NOT EXISTS certification_status VARCHAR(50) DEFAULT 'uncertified'
    CHECK (certification_status IS NULL OR certification_status IN ('uncertified', 'pending_review', 'certified_a', 'certified_b', 'certified_c'));

-- Pipeline status: tracks where the supplier is in the onboarding workflow
ALTER TABLE suppliers
    ADD COLUMN IF NOT EXISTS pipeline_status VARCHAR(50) DEFAULT 'contacted'
    CHECK (pipeline_status IS NULL OR pipeline_status IN ('contacted', 'potential', 'quoted', 'certified', 'active', 'inactive'));

-- Reference to the latest audit for quick access
ALTER TABLE suppliers
    ADD COLUMN IF NOT EXISTS latest_audit_id UUID REFERENCES supplier_audits(id) ON DELETE SET NULL;

-- Timestamp when supplier was certified
ALTER TABLE suppliers
    ADD COLUMN IF NOT EXISTS certified_at TIMESTAMP WITH TIME ZONE;

-- Indexes for new columns
CREATE INDEX IF NOT EXISTS idx_suppliers_certification_status ON suppliers(certification_status);
CREATE INDEX IF NOT EXISTS idx_suppliers_pipeline_status ON suppliers(pipeline_status);
CREATE INDEX IF NOT EXISTS idx_suppliers_latest_audit_id ON suppliers(latest_audit_id);
CREATE INDEX IF NOT EXISTS idx_suppliers_certified_at ON suppliers(certified_at);
