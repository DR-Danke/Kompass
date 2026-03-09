# PRD: Kompass Trade Fair Supplier Capture System

## Meeting Metadata
- **Date**: March 9, 2026
- **Participants**: Speaker 1 (Dani — Tech Lead), Speaker 2 (Rubén — Client / Kompass CEO), Speaker 3 (Team Member)
- **Duration**: ~17 minutes
- **Context**: Planning session for a new feature enabling Rubén to capture supplier contacts at a trade fair in China, automatically process business cards, and initiate outreach — all integrated into the existing Kompass platform.

## Executive Summary
Rubén travels to a trade fair in China (arrives ~March 27, fair starts March 29) and needs a system to photograph supplier business cards, automatically extract contact data (name, phone, email, factory name, address), create supplier records in Kompass, and auto-send outreach messages via WeChat and email. The goal is for Rubén's back-office team to have organized supplier and product information within one day of each factory visit. The feature will be built on the existing Kompass app within a ~2-week timeline. Budget is capped at $1,000/month recurring.

## Work Streams

### Stream 1: Business Card Capture & Data Extraction
Extend the existing AI extraction pipeline to process business card photos, extract structured supplier contact information, and auto-create supplier records in the system.

#### Requirements

##### REQ-001: Business Card Photo Ingestion
- **Type**: feature
- **Priority**: P0
- **Description**: Enable users to upload or send photos of business cards (from a phone camera) into the Kompass system. The input channel must work from China. The initial implementation should support direct upload via the Kompass web app (mobile-responsive). A messaging-based input channel (WeChat) is addressed separately in REQ-005.
- **Affected Modules**: `apps/Client/src/pages/kompass/` (new page or extension of ImportWizardPage), `apps/Server/app/api/extraction_routes.py`, `apps/Server/app/services/extraction_service.py`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] User can upload one or more business card photos (.png, .jpg, .jpeg) from a mobile browser
  - [ ] Uploaded images are queued for AI extraction processing
  - [ ] System provides upload confirmation and processing status feedback

##### REQ-002: Business Card AI Data Extraction
- **Type**: feature
- **Priority**: P0
- **Description**: Use the existing AI extraction pipeline (Claude/OpenAI vision) to parse business card photos and extract structured fields: contact name, phone number (including international prefixes like +86), email address, factory/company name, physical address, province/city, and detect whether a QR code is present on the card. Business cards may vary widely in format and language (Chinese + English).
- **Affected Modules**: `apps/Server/app/services/extraction_service.py`, `apps/Server/app/models/kompass_dto.py`
- **Dependencies**: REQ-001
- **Acceptance Criteria**:
  - [ ] AI extraction correctly identifies and returns: contact_name, contact_phone, contact_email, company_name, address, province, and qr_code_detected (boolean) from a business card photo
  - [ ] Extraction handles bilingual (Chinese/English) business cards
  - [ ] Extraction returns a confidence score per field
  - [ ] Extraction gracefully handles missing fields (not all cards have all data)

##### REQ-003: Auto-Create Supplier from Extracted Data
- **Type**: feature
- **Priority**: P0
- **Description**: After extraction, automatically create a new supplier record in the Kompass system using the extracted data. The supplier should be created with pipeline status "contacted" and a flag indicating it was captured at a trade fair. If a supplier with the same email or phone already exists, flag it as a potential duplicate for manual review rather than creating a duplicate record.
- **Affected Modules**: `apps/Server/app/services/supplier_service.py`, `apps/Server/app/repository/kompass_repository.py`, `apps/Server/app/api/supplier_routes.py`
- **Dependencies**: REQ-002
- **Acceptance Criteria**:
  - [ ] Extracted business card data automatically creates a supplier record with all available fields populated
  - [ ] New supplier is assigned pipeline status "contacted"
  - [ ] Duplicate detection by email or phone prevents creating duplicate suppliers
  - [ ] Potential duplicates are flagged for manual review
  - [ ] Supplier record includes metadata indicating trade fair origin (source field)

##### REQ-004: Review & Confirm Extracted Suppliers
- **Type**: feature
- **Priority**: P1
- **Description**: Provide a review interface where the user (or back-office team) can see recently extracted business card data, correct any AI extraction errors, confirm or reject supplier creation, and enrich the record before it is finalized. This is similar to the existing ImportWizard review step but adapted for supplier contacts rather than products.
- **Affected Modules**: `apps/Client/src/pages/kompass/` (new component or page), `apps/Client/src/hooks/kompass/`, `apps/Client/src/components/kompass/`
- **Dependencies**: REQ-002, REQ-003
- **Acceptance Criteria**:
  - [ ] UI displays list of recently extracted business cards with extracted fields
  - [ ] User can edit any extracted field before confirming
  - [ ] User can approve or reject each extracted supplier
  - [ ] Approved suppliers are persisted; rejected ones are discarded
  - [ ] Back-office team can access this review interface (not just the person at the fair)

### Stream 2: Automated Outreach (Email & WeChat)
Automate initial contact with newly captured suppliers via email and WeChat messaging.

#### Requirements

##### REQ-005: WeChat Integration for Input & Messaging
- **Type**: feature
- **Priority**: P1
- **Description**: Integrate with WeChat to support two flows: (1) allow the user to send business card photos to a WeChat bot/account that forwards them into the Kompass extraction pipeline, and (2) send automated outreach messages to suppliers via WeChat. This includes attempting to find a supplier's WeChat ID from their phone number. The QR code on a business card should be used to add the contact on WeChat when detected.
- **Affected Modules**: `apps/Server/app/services/` (new wechat_service.py), `apps/Server/app/api/` (new wechat_routes.py), infrastructure/deployment configuration
- **Dependencies**: REQ-002
- **Acceptance Criteria**:
  - [ ] System can receive business card photos sent via WeChat and route them to the extraction pipeline
  - [ ] System can send a templated introduction message to a WeChat contact
  - [ ] System attempts to resolve phone numbers to WeChat IDs
  - [ ] QR codes detected on business cards are processed for WeChat contact addition
  - [ ] WeChat integration functions correctly from within China (no Great Firewall issues)

##### REQ-006: Automated Email Outreach
- **Type**: feature
- **Priority**: P0
- **Description**: Replace the current mock email implementation with real SMTP email sending. After a supplier is created from a business card, automatically send a templated introduction email (e.g., "Hi, I'm Rubén from Kompass, we just met at [fair name]. I'd love to receive your brochure/portfolio and product catalog."). The email template should be configurable.
- **Affected Modules**: `apps/Server/app/services/quotation_service.py` (existing email mock), new `apps/Server/app/services/email_service.py`, `apps/Server/app/models/kompass_dto.py`
- **Dependencies**: REQ-003
- **Acceptance Criteria**:
  - [ ] System sends real emails via SMTP (not mock mode)
  - [ ] Introduction email is sent automatically when a new supplier is confirmed from a business card
  - [ ] Email includes configurable template with supplier name, user name, and fair context
  - [ ] Email requests the supplier's brochure/portfolio and product catalog
  - [ ] Failed email sends are logged and retryable

##### REQ-007: Follow-Up Message Templates
- **Type**: feature
- **Priority**: P2
- **Description**: Support a second follow-up message (via email and/or WeChat) that can be triggered manually or after a configurable delay. The follow-up requests pricing information from the supplier (e.g., "Thank you for the catalog. Can you send me prices for [products]?"). This enables the team to start gathering pricing data while Rubén is still at the fair.
- **Affected Modules**: `apps/Server/app/services/email_service.py`, `apps/Server/app/services/wechat_service.py`, `apps/Client/src/pages/kompass/SuppliersPage.tsx`
- **Dependencies**: REQ-005, REQ-006
- **Acceptance Criteria**:
  - [ ] User can trigger a follow-up message to a supplier from the supplier detail view
  - [ ] Follow-up template requests brochure/portfolio and pricing
  - [ ] Follow-up can be sent via email, WeChat, or both
  - [ ] Message templates are configurable (not hardcoded)

### Stream 3: Real-Time Team Visibility
Ensure the back-office team has near-real-time access to supplier data captured at the trade fair.

#### Requirements

##### REQ-008: Trade Fair Dashboard / Activity Feed
- **Type**: feature
- **Priority**: P1
- **Description**: Provide a view (dashboard widget or dedicated page) where the back-office team can see suppliers captured during the trade fair in near-real-time. This should show recently added suppliers, their status (pending review, confirmed, contacted), and whether outreach messages have been sent. The goal is that the team has organized data within one day of capture.
- **Affected Modules**: `apps/Client/src/pages/kompass/DashboardPage.tsx` or new page, `apps/Server/app/api/dashboard_routes.py`, `apps/Server/app/services/dashboard_service.py`
- **Dependencies**: REQ-003
- **Acceptance Criteria**:
  - [ ] Dashboard shows list of suppliers added in the last 24–48 hours
  - [ ] Each entry shows supplier name, contact info, pipeline status, and outreach status (email sent, WeChat contacted)
  - [ ] Data is accessible to all team members with appropriate roles (not just the fair attendee)
  - [ ] Dashboard auto-refreshes or supports manual refresh

##### REQ-009: Supplier-to-Product Pipeline
- **Type**: feature
- **Priority**: P2
- **Description**: When a supplier responds with their brochure/portfolio (via email or WeChat), the team should be able to feed that document into the existing Import Wizard to extract products and associate them with the supplier. This connects the supplier capture flow to the existing product import pipeline, populating the "Biblia" (product catalog) for the team.
- **Affected Modules**: `apps/Client/src/pages/kompass/ImportWizardPage.tsx`, `apps/Server/app/services/extraction_service.py`, `apps/Server/app/api/extraction_routes.py`
- **Dependencies**: REQ-003, existing Import Wizard functionality
- **Acceptance Criteria**:
  - [ ] User can initiate product extraction from a supplier's detail page, pre-selecting that supplier
  - [ ] Extracted products are automatically associated with the originating supplier
  - [ ] Imported products appear in the Biblia General (Products page) linked to the supplier

## Implementation Waves

### Wave 1: Foundation (Must be ready by March 27)
**REQ-001, REQ-002, REQ-003, REQ-006**

Rationale: These are the core pipeline — capture a business card photo, extract data, create a supplier, and send an introduction email. This is the minimum viable feature for the trade fair. No external messaging platform dependencies. Uses existing AI extraction infrastructure and adds real SMTP email.

### Wave 2: Team Enablement
**REQ-004, REQ-008**

Rationale: Once suppliers are being captured, the team needs to review/correct extractions and see what's been captured. Depends on Wave 1 supplier creation being functional.

### Wave 3: WeChat & Advanced Outreach
**REQ-005, REQ-007**

Rationale: WeChat integration requires research into API access, potential business account setup, and Great Firewall considerations. This is high-value but higher-risk and may not be ready for the initial fair date. Email outreach (Wave 1) provides a fallback.

### Wave 4: Full Pipeline
**REQ-009**

Rationale: Once suppliers are captured and responding with catalogs, connect to existing Import Wizard for product extraction. This builds on the complete flow being operational.

## Cross-Cutting Concerns

- **Mobile-Responsive UI**: The capture interface must work well on a phone browser since Rubén will be using it at the trade fair. All new UI components must be tested on mobile viewports.
- **China Network Considerations**: The app must be accessible from China. Verify that Vercel (frontend) and Render (backend) are not blocked by the Great Firewall. Consider a VPN fallback plan.
- **Database Schema Changes**: New fields may be needed on the `suppliers` table: `source` (e.g., "trade_fair"), `fair_name`, `capture_date`, `outreach_status`, `wechat_id`. A migration plan is required.
- **AI Extraction Prompt Tuning**: The existing extraction prompt is optimized for product catalogs. A new prompt template is needed for business card parsing (different fields, different layouts, bilingual handling).
- **SMTP Configuration**: Real email sending requires SMTP credentials in environment variables. This affects both Render (production) and local development environments.
- **Rate Limiting**: If many cards are scanned in quick succession at the fair, the extraction pipeline and email sending must handle bursts without overwhelming AI APIs or SMTP servers.
- **Existing Email Mock Replacement**: The current `EMAIL_MOCK_MODE` in `quotation_service.py` needs to be replaced with a shared, real email service that can be used by both quotation sending and supplier outreach.

## Open Questions

- **Q1**: What specific WeChat integration approach should be used — official WeChat Business API, WeChat Work (企业微信), or a third-party service? Official APIs require business verification which may take weeks. — Context: "Entonces toca averiguar bien todo el tema con WeChat"

- **Q2**: Should the system use a dedicated phone number/WeChat account for automated outreach, or use Rubén's personal account? This affects WeChat setup and message deliverability. — Context: "Ese QR code es el que lo va a llevar a que agregue ese contacto a un wechat"

- **Q3**: What is the exact outreach message template? The transcript mentions a generic "Hi, we just met, I need your portfolio/brochure" but the exact wording, language (English? Chinese?), and tone need to be defined. — Context: "hola, soy Rubén de Compas, nos acabamos de conocer, me gustaría que tu roshuro portafolio"

- **Q4**: How should the system handle business cards that are entirely in Chinese with no English text? Should the extraction output be translated, kept in original language, or both? — Context: Business cards at Chinese trade fairs may be Chinese-only.

- **Q5**: What is the trade fair name and date range? This is needed for email templates and source tracking metadata. — Context: "yo arranco la feria el 29" — fair starts March 29 but name is not mentioned.

- **Q6**: Is the VPN situation in China handled? Vercel and Render may be inaccessible without VPN from mainland China. Need confirmation that Rubén will have VPN access, or consider alternative hosting. — Context: "China... es un pedo, no es por capricho"

- **Q7**: Budget agreement needs confirmation with Tomás — the $1,000/month cap was mentioned but not finalized in this call. Implementation scope depends on this. — Context: "Tomás me dijo que no podíamos pagar ni a bala más de mil dólares mensuales... lo puedes revisar con él"