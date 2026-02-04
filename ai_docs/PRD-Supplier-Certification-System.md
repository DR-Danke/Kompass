# PRD: Supplier Certification & Audit System

> **Document Version:** 1.0
> **Date:** February 4, 2026
> **Source:** Requirements call with Kompass Trading team (Rubén, Diana, Alejandro)

---

## Executive Summary

This PRD outlines requirements for a **Supplier Certification System** that uses AI to extract and analyze factory audit documents, enabling rapid supplier qualification and certification tracking. The system will integrate with the existing Kompass Supplier module to create a complete supplier pipeline workflow.

---

## 1. Problem Statement

### Current Pain Points
1. **Manual audit analysis**: Factory audits are 70+ page PDF documents (~21MB) that require manual review
2. **Inconsistent audit formats**: Different inspectors provide varying levels of detail
3. **No centralized supplier qualification**: Supplier certification status is tracked manually
4. **Time-consuming comparisons**: Difficult to quickly compare factory qualifications across suppliers
5. **Missing pipeline visibility**: No clear workflow from initial contact to certified supplier

### Business Impact
- Delays in supplier qualification decisions
- Risk of working with unverified suppliers
- Inefficient use of team time reviewing lengthy documents
- Lack of standardized evaluation criteria

---

## 2. Requirements Overview

### 2.1 Supplier Pipeline Workflow

**New Supplier Status Flow:**

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐     ┌──────────────┐
│  Contacted  │ ──► │ Potential/Quoted │ ──► │  Certified  │ ──► │ Active Order │
└─────────────┘     └──────────────────┘     └─────────────┘     └──────────────┘
     │                      │                       │
     │                      │                       │
     ▼                      ▼                       ▼
 Basic Info          Catalog Received       Audit Uploaded
 Manual Entry        Products Quoted        AI Extraction
                                            Classification
```

**Status Definitions:**
| Status | Description | Can Order? |
|--------|-------------|------------|
| `contacted` | Initial contact made, basic info only | No |
| `potential` | Catalog received, products being evaluated | No |
| `quoted` | Products quoted to clients, awaiting certification | No |
| `certified` | Factory audit completed and approved | Yes |
| `active` | Has active orders in progress | Yes |
| `inactive` | Previously certified, currently not working together | No |

### 2.2 Factory Audit Document Processing

**Supported Document Types:**
1. **Factory Audit** (Primary) - Initial certification, 70+ pages
2. **Container Inspection** (Secondary) - Pre-shipment verification, shorter format

**AI Extraction Requirements:**

The system shall extract the following ~10 key data points from audit PDFs:

| # | Field | Type | Priority | Notes |
|---|-------|------|----------|-------|
| 1 | `supplier_type` | Enum | Critical | `manufacturer` or `trader` - Most important criterion |
| 2 | `employee_count` | Integer | High | Total number of factory workers |
| 3 | `factory_area_sqm` | Integer | Medium | Factory size in square meters |
| 4 | `production_lines` | Integer | High | Number of active production lines |
| 5 | `markets_served` | JSON | High | Markets with percentages: `{"south_america": 30, "us": 40, "europe": 20, "asia": 10}` |
| 6 | `certifications` | Array | High | List of certifications (ISO, etc.) |
| 7 | `has_machinery_photos` | Boolean | Medium | Production machinery documented |
| 8 | `positive_points` | Array | Critical | Strengths identified in audit |
| 9 | `negative_points` | Array | Critical | Weaknesses/concerns identified |
| 10 | `products_verified` | Array | High | Products physically verified during audit |
| 11 | `audit_date` | Date | High | Date of factory inspection |
| 12 | `inspector_name` | String | Medium | Name of inspector/auditor |

### 2.3 Supplier Classification

**Classification Tiers:**

| Tier | Criteria (AI Suggested) | Human Override |
|------|------------------------|----------------|
| **Type A** | Manufacturer, 3+ certifications, active production lines, minimal negative points | Always allowed |
| **Type B** | Manufacturer or verified trader, some certifications, moderate concerns | Always allowed |
| **Type C** | Trader without verification, significant concerns, limited documentation | Always allowed |

> **Important:** Classification is a *recommendation*, not a final decision. Human judgment is required based on:
> - Specific product requirements
> - Client needs
> - Price competitiveness
> - Input from China-based agent (Hijin)

### 2.4 User Interface Requirements

**Suppliers Page Enhancements:**

1. **Status Column** - Show pipeline status with visual indicators
2. **Certification Badge** - Type A/B/C classification badge
3. **Audit Upload Button** - For uploading factory audit PDFs
4. **Quick Summary View** - Extracted key points without reading full audit

**Supplier Detail View - New "Certification" Tab:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Supplier: Hilda Furniture Co.                    Status: ● Certified (A)   │
├─────────────────────────────────────────────────────────────────────────────┤
│ [General] [Products] [Certification] [Documents] [Orders]                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────┐  ┌──────────────────────────────────┐ │
│  │ QUICK SUMMARY                   │  │ CLASSIFICATION                   │ │
│  │                                 │  │                                  │ │
│  │ Type: Manufacturer ✓            │  │      ┌───┐                       │ │
│  │ Employees: 156                  │  │      │ A │  Recommended          │ │
│  │ Factory: 5,200 m²               │  │      └───┘                       │ │
│  │ Production Lines: 4 active      │  │                                  │ │
│  │ Certifications: ISO 9001, CE    │  │  [Override Classification ▼]    │ │
│  │                                 │  │                                  │ │
│  └─────────────────────────────────┘  └──────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ MARKETS SERVED                                                          ││
│  │ ████████████░░░░░░░░ South America 40%                                 ││
│  │ ██████████░░░░░░░░░░ USA 35%                                           ││
│  │ ████░░░░░░░░░░░░░░░░ Europe 15%                                        ││
│  │ ██░░░░░░░░░░░░░░░░░░ Asia 10%                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────────┐  │
│  │ ✓ POSITIVE POINTS           │  │ ⚠ NEGATIVE POINTS / ALERTS         │  │
│  │                             │  │                                     │  │
│  │ • Direct manufacturer       │  │ • No client references provided    │  │
│  │ • Multiple production lines │  │ • Some machinery idle              │  │
│  │ • ISO 9001 certified        │  │ • Limited export experience to     │  │
│  │ • Products verified in-     │  │   South America                    │  │
│  │   person                    │  │                                     │  │
│  │                             │  │                                     │  │
│  └─────────────────────────────┘  └─────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │ AUDIT DOCUMENTS                                                         ││
│  │                                                                          ││
│  │ 📄 Factory_Audit_2026-01-15.pdf    21.3 MB    [View] [Reprocess]       ││
│  │ 📄 Container_Inspection_2026-02.pdf 3.2 MB    [View] [Reprocess]       ││
│  │                                                                          ││
│  │ [+ Upload New Audit Document]                                           ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technical Implementation

### 3.1 Database Schema Changes

```sql
-- New table for supplier audits
CREATE TABLE IF NOT EXISTS supplier_audits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id UUID NOT NULL REFERENCES suppliers(id) ON DELETE CASCADE,
    audit_type VARCHAR(50) NOT NULL DEFAULT 'factory_audit', -- 'factory_audit', 'container_inspection'
    document_url VARCHAR(1000) NOT NULL,
    document_name VARCHAR(255),
    file_size_bytes BIGINT,

    -- Extracted data
    supplier_type VARCHAR(50), -- 'manufacturer', 'trader', 'unknown'
    employee_count INTEGER,
    factory_area_sqm INTEGER,
    production_lines_count INTEGER,
    markets_served JSONB, -- {"south_america": 40, "us": 35, ...}
    certifications TEXT[], -- ARRAY of certification names
    has_machinery_photos BOOLEAN DEFAULT false,
    positive_points TEXT[],
    negative_points TEXT[],
    products_verified TEXT[],

    -- Audit metadata
    audit_date DATE,
    inspector_name VARCHAR(255),

    -- AI processing
    extraction_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    extraction_raw_response JSONB,
    extracted_at TIMESTAMP WITH TIME ZONE,

    -- Classification
    ai_classification VARCHAR(10), -- 'A', 'B', 'C'
    ai_classification_reason TEXT,
    manual_classification VARCHAR(10), -- Override
    classification_notes TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add certification fields to suppliers table
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS certification_status VARCHAR(50) DEFAULT 'uncertified';
-- Values: 'uncertified', 'pending_review', 'certified_a', 'certified_b', 'certified_c'

ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS pipeline_status VARCHAR(50) DEFAULT 'contacted';
-- Values: 'contacted', 'potential', 'quoted', 'certified', 'active', 'inactive'

ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS latest_audit_id UUID REFERENCES supplier_audits(id);
ALTER TABLE suppliers ADD COLUMN IF NOT EXISTS certified_at TIMESTAMP WITH TIME ZONE;

-- Index for quick lookups
CREATE INDEX idx_supplier_audits_supplier_id ON supplier_audits(supplier_id);
CREATE INDEX idx_suppliers_certification_status ON suppliers(certification_status);
CREATE INDEX idx_suppliers_pipeline_status ON suppliers(pipeline_status);
```

### 3.2 Backend Services

**New Service: `audit_service.py`**

```python
class AuditService:
    """Service for processing supplier audit documents."""

    async def upload_audit(
        self,
        supplier_id: str,
        file: UploadFile,
        audit_type: str = "factory_audit"
    ) -> SupplierAudit:
        """Upload and queue audit document for processing."""

    async def process_audit(self, audit_id: str) -> SupplierAudit:
        """Extract data from audit PDF using AI."""

    async def classify_supplier(self, audit_id: str) -> str:
        """Generate A/B/C classification based on extracted data."""

    async def override_classification(
        self,
        audit_id: str,
        classification: str,
        notes: str
    ) -> SupplierAudit:
        """Allow manual override of AI classification."""

    async def get_supplier_audits(self, supplier_id: str) -> List[SupplierAudit]:
        """Get all audits for a supplier."""
```

**AI Extraction Prompt Template:**

```python
AUDIT_EXTRACTION_PROMPT = """
Analyze this factory audit document and extract the following information in JSON format:

{
    "supplier_type": "manufacturer" or "trader" or "unknown",
    "employee_count": <number or null>,
    "factory_area_sqm": <number or null>,
    "production_lines_count": <number or null>,
    "markets_served": {
        "south_america": <percentage>,
        "north_america": <percentage>,
        "europe": <percentage>,
        "asia": <percentage>,
        "other": <percentage>
    },
    "certifications": ["list", "of", "certifications"],
    "has_machinery_photos": true/false,
    "positive_points": ["strength 1", "strength 2", ...],
    "negative_points": ["concern 1", "concern 2", ...],
    "products_verified": ["product 1", "product 2", ...],
    "audit_date": "YYYY-MM-DD" or null,
    "inspector_name": "name" or null,
    "summary": "Brief 2-3 sentence summary of the factory"
}

Focus on:
1. Whether this is a true manufacturer or a trader/middleman
2. Production capacity indicators (employees, factory size, active lines)
3. Quality certifications
4. Export market experience
5. Any red flags or concerns noted
6. Any positive highlights noted

If information is not found in the document, use null.
"""
```

### 3.3 API Endpoints

```
POST   /api/suppliers/{supplier_id}/audits              Upload new audit document
GET    /api/suppliers/{supplier_id}/audits              List supplier audits
GET    /api/suppliers/{supplier_id}/audits/{audit_id}   Get audit details
POST   /api/suppliers/{supplier_id}/audits/{audit_id}/reprocess   Reprocess extraction
PUT    /api/suppliers/{supplier_id}/audits/{audit_id}/classification   Override classification
DELETE /api/suppliers/{supplier_id}/audits/{audit_id}   Delete audit

GET    /api/suppliers/certified                         List certified suppliers
GET    /api/suppliers/pipeline/{status}                 List suppliers by pipeline status
PUT    /api/suppliers/{supplier_id}/pipeline-status     Update pipeline status
```

### 3.4 Frontend Components

**New Components:**

| Component | Location | Purpose |
|-----------|----------|---------|
| `AuditUploader.tsx` | `components/kompass/` | Upload audit documents with drag-drop |
| `AuditSummaryCard.tsx` | `components/kompass/` | Display extracted audit summary |
| `ClassificationBadge.tsx` | `components/kompass/` | Show A/B/C classification |
| `SupplierPipelineColumn.tsx` | `components/kompass/` | Kanban-style pipeline view |
| `MarketsServedChart.tsx` | `components/kompass/` | Bar chart of market percentages |

**Modified Components:**

| Component | Changes |
|-----------|---------|
| `SuppliersPage.tsx` | Add pipeline status filter, certification badge column |
| `SupplierForm.tsx` | Add Certification tab with audit management |

---

## 4. Integration with Existing System

### 4.1 Leveraging Existing Extraction Service

The current `extraction_service.py` already supports:
- PDF parsing with Claude/OpenAI vision
- File upload handling
- Background job processing

**Recommended approach:** Extend the existing extraction service with a new prompt template for audits rather than creating a separate service.

### 4.2 File Storage Requirements

Audit documents are large (up to 21MB). Options:
1. **Cloudflare R2** (recommended) - S3-compatible, no egress fees
2. **Supabase Storage** - Already have Supabase connection
3. **Google Drive integration** - Client already uses Drive

### 4.3 Supplier Module Integration

Update existing supplier workflow:
1. SuppliersPage shows pipeline status
2. Supplier detail drawer includes Certification tab
3. Products can filter by certified suppliers only

---

## 5. User Stories

### Epic: Supplier Certification

**US-1: Upload Factory Audit**
> As a sourcing manager, I want to upload a factory audit PDF so that the system can automatically extract key supplier information.

**Acceptance Criteria:**
- [ ] Can upload PDF files up to 25MB
- [ ] Progress indicator during upload
- [ ] Extraction starts automatically after upload
- [ ] Notification when extraction completes
- [ ] Can view extracted data in summary format

**US-2: View Audit Summary**
> As a sourcing manager, I want to see a quick summary of the audit findings so that I can make faster qualification decisions.

**Acceptance Criteria:**
- [ ] Summary shows manufacturer/trader status prominently
- [ ] Positive and negative points displayed side by side
- [ ] Markets served shown as visual chart
- [ ] Certifications listed with icons
- [ ] Can click to view full PDF document

**US-3: Classify Supplier**
> As a sourcing manager, I want the system to suggest a supplier classification (A/B/C) based on the audit, while allowing me to override if needed.

**Acceptance Criteria:**
- [ ] AI suggests classification with reasoning
- [ ] Can override to different classification
- [ ] Must provide notes when overriding
- [ ] Classification history is tracked

**US-4: Filter Suppliers by Certification**
> As a sales team member, I want to filter suppliers by certification status so that I only quote products from certified factories.

**Acceptance Criteria:**
- [ ] Filter by: All, Certified Only, Type A, Type B, Type C, Uncertified
- [ ] Products page shows supplier certification status
- [ ] Warning when adding uncertified supplier products to quote

**US-5: Supplier Pipeline View**
> As a sourcing manager, I want to see suppliers organized by pipeline stage so that I can track onboarding progress.

**Acceptance Criteria:**
- [ ] Kanban view of supplier pipeline
- [ ] Can drag suppliers between stages
- [ ] Count of suppliers per stage
- [ ] Click to open supplier detail

---

## 6. Future Enhancements (Out of Scope for V1)

The following were mentioned in the call but deferred:

1. **WhatsApp/Telegram Bot Integration**
   - Automated supplier onboarding messages
   - "Hello, we are Kompass Trading, please send your catalog..."

2. **AI Catalog Analysis**
   - Auto-analyze supplier catalogs
   - Generate product shortlists based on needs
   - Auto-request pricing for selected items

3. **Container Inspection Workflow**
   - Pre-shipment inspection document processing
   - Link inspections to specific orders

4. **Express Quotation Migration**
   - Migrate Excel quotation matrix to app
   - Auto-calculate: FOB + Tariff + Freight + Inspection + Markup = Price

---

## 7. Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Time to review audit | 30-60 min | 5 min |
| Supplier qualification decisions/week | 2-3 | 10+ |
| Certified supplier visibility | Manual tracking | 100% dashboard |
| Audit data completeness | Varies | Standardized extraction |

---

## 8. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Inconsistent audit formats | Extraction accuracy varies | Require standardized format from inspectors |
| Large file uploads fail | User frustration | Chunked uploads, retry logic, progress feedback |
| AI misclassification | Bad supplier decisions | Always show reasoning, require human confirmation for orders |
| PDF parsing fails | No data extracted | Fallback to manual entry, flag for review |

---

## 9. Implementation Phases

### Phase 1: Core Audit Processing (Week 1-2)
- Database schema changes
- Audit upload endpoint
- PDF extraction with AI
- Basic summary display

### Phase 2: Classification System (Week 2-3)
- AI classification logic
- Override functionality
- Certification badges

### Phase 3: Pipeline Workflow (Week 3-4)
- Pipeline status field
- Status transitions
- Kanban view
- Filters and search

### Phase 4: Integration & Polish (Week 4)
- Products integration (filter by certified)
- Quotations integration (warnings)
- UI refinements
- Testing

---

## 10. Appendix

### A. Sample Audit Document Structure

Based on the call, typical factory audits contain:
1. Factory "business card" - basic info
2. Summary/Introduction
3. Positive points section
4. Negative points section
5. Administrative info / org chart
6. Product photos with specifications
7. Production line photos
8. Machinery inventory
9. Materials/stock photos
10. Staff/operations photos

### B. Glossary

| Term | Definition |
|------|------------|
| Biblia General | Master product catalog with all curated products |
| Trader | Company that resells products but doesn't manufacture |
| Manufacturer | Company that produces its own products |
| FOB | Free On Board - price at port of origin |
| MOQ | Minimum Order Quantity |
| HS Code | Harmonized System code for customs/tariffs |
| Hijin | Kompass's China-based agent who provides local expertise |

---

*Document prepared based on requirements call dated February 4, 2026*
