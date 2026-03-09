# PRD: Trade Fair Business Card Capture & Automated Supplier Outreach

## Meeting Metadata
- **Date**: March 9, 2026
- **Participants**: Speaker 1 (Dani — Tech Lead), Speaker 2 (Rubén — Client/User, Compas founder), Speaker 3 (Team member)
- **Duration**: ~17 minutes
- **Context**: Rubén needs a tool to streamline supplier discovery at trade fairs in China. He will attend a fair starting March 29, 2026, and needs a system to photograph business cards, automatically extract supplier data, store it in the Kompass platform, and initiate automated outreach via WeChat and email — so his team back home can start working with the supplier data in near-real-time.

## Executive Summary
Rubén requires a mobile-friendly workflow to capture supplier business cards at Chinese trade fairs, extract structured contact data (name, phone, email, address, factory name) via AI/OCR, auto-create suppliers in Kompass, and trigger automated outreach messages through WeChat and email requesting brochures/portfolios. The goal is to enable his back-office team to begin organizing supplier products in the Kompass catalog ("Biblia") with no more than a one-day delay. The system must be ready by March 27, 2026. A follow-up automated message requesting pricing is desired but lower priority.

## Work Streams

### Stream 1: Business Card Capture & OCR Extraction
Extend the existing Kompass extraction pipeline to accept business card photos and extract structured supplier contact data (name, phone, email, factory name, address/province) using AI vision.

#### Requirements

##### REQ-001: Business Card Photo Upload (Mobile-Optimized)
- **Type**: feature
- **Priority**: P0
- **Description**: Provide a mobile-friendly UI within the existing Kompass app that allows the user to take or upload a photo of a business card. The UI must work on mobile browsers since the user will be at a trade fair. It should support quick sequential captures (one card after another).
- **Affected Modules**: `apps/Client/src/pages/kompass/`, new page or component; `apps/Client/src/services/kompassService.ts`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] User can access a mobile-optimized page to capture/upload business card photos
  - [ ] Camera capture and gallery upload are both supported
  - [ ] Multiple cards can be submitted in rapid succession without navigating away
  - [ ] Upload shows progress indicator and success/failure feedback

##### REQ-002: AI-Powered Business Card Data Extraction
- **Type**: feature
- **Priority**: P0
- **Description**: Process uploaded business card images using AI vision (Claude or GPT-4o, leveraging the existing extraction service architecture) to extract structured fields: contact name, phone number (with country code, e.g., +86), email address, factory/company name, physical address (city/province), website, and detect presence of a QR code. Return extracted data as a structured JSON payload.
- **Affected Modules**: `apps/Server/app/services/extraction_service.py` (extend or new method); `apps/Server/app/api/extraction_routes.py` (new endpoint)
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] System extracts contact_name, contact_phone, contact_email, company_name, address, city, country, and website from a business card image
  - [ ] Extraction handles Chinese and English business cards
  - [ ] Extraction detects and returns QR code presence (boolean) and QR code image region if present
  - [ ] Confidence scores are returned for each extracted field
  - [ ] Extraction completes within 10 seconds per card

##### REQ-003: Auto-Create Supplier from Extracted Data
- **Type**: feature
- **Priority**: P0
- **Description**: After business card extraction, automatically create a new supplier record in Kompass using the extracted data. Map extracted fields to existing supplier table columns (name → company name, contact_name, contact_email, contact_phone, address, city, country). Set initial `pipeline_status` to `contacted` and `status` to `pending_review`. If a supplier with a matching email or phone already exists, flag it as a potential duplicate instead of creating a new record.
- **Affected Modules**: `apps/Server/app/services/supplier_service.py`; `apps/Server/app/api/supplier_routes.py`; `apps/Server/app/repository/kompass_repository.py`
- **Dependencies**: REQ-002
- **Acceptance Criteria**:
  - [ ] Supplier record is created with all extracted fields mapped correctly
  - [ ] Pipeline status is set to `contacted` on creation
  - [ ] Duplicate detection triggers when email or phone matches an existing supplier
  - [ ] User is shown a confirmation/review screen before supplier creation with option to edit extracted fields
  - [ ] Created supplier appears immediately in the Suppliers list and Pipeline Kanban

### Stream 2: Automated Outreach (WeChat & Email)
Automatically contact newly captured suppliers via email and WeChat to request brochures, portfolios, and pricing information.

#### Requirements

##### REQ-004: Automated Email Outreach
- **Type**: feature
- **Priority**: P1
- **Description**: After a supplier is created from a business card, automatically send a templated introduction email to the supplier's extracted email address. The email should introduce Rubén/Compas, reference their meeting at the trade fair, and request the supplier's product portfolio/brochure. Email templates should be configurable. The system should use a transactional email service (e.g., SMTP or a provider API).
- **Affected Modules**: `apps/Server/app/services/` (new email_outreach_service.py); `apps/Server/app/api/` (new or extended route); backend `.env` for SMTP/email config
- **Dependencies**: REQ-003
- **Acceptance Criteria**:
  - [ ] Email is sent automatically upon supplier creation from business card capture
  - [ ] Email uses a configurable template with placeholders (supplier name, contact name, user name)
  - [ ] Email send status (sent/failed) is logged and visible in the supplier record
  - [ ] User can customize the email template from settings
  - [ ] Email includes a professional greeting in English

##### REQ-005: WeChat Contact Addition via QR Code
- **Type**: feature
- **Priority**: P1
- **Description**: When a QR code is detected on the business card, decode it and provide a deep-link or redirect to add the contact on WeChat. If no QR code is present, attempt to look up the phone number as a potential WeChat ID. The system should facilitate (not necessarily fully automate) adding the supplier as a WeChat contact.
- **Affected Modules**: `apps/Server/app/services/` (new wechat_service.py); `apps/Client/` (UI for QR redirect/deep-link)
- **Dependencies**: REQ-002
- **Acceptance Criteria**:
  - [ ] QR code on business card is decoded and a WeChat deep-link is generated
  - [ ] If no QR code, the phone number is displayed as a suggested WeChat ID for manual addition
  - [ ] User can tap a button to open WeChat with the decoded QR or contact info
  - [ ] The system logs which contact method was used (QR, phone, none)

##### REQ-006: Automated WeChat Message
- **Type**: feature
- **Priority**: P1
- **Description**: After adding a supplier on WeChat, send (or prepare for manual sending) a templated introduction message in English requesting the supplier's portfolio/brochure. Due to WeChat API limitations, this may need to be a "copy-to-clipboard" message that the user can paste, or use WeChat's official API if available.
- **Affected Modules**: `apps/Client/` (message template UI, clipboard functionality); `apps/Server/app/services/` (wechat_service.py)
- **Dependencies**: REQ-005
- **Acceptance Criteria**:
  - [ ] A templated message is generated with supplier name and Compas introduction
  - [ ] Message is either auto-sent via WeChat API or copied to clipboard for manual paste
  - [ ] Message status is tracked in the supplier record
  - [ ] Template is configurable from settings

##### REQ-007: Follow-Up Message for Pricing
- **Type**: feature
- **Priority**: P2
- **Description**: After initial outreach, enable a follow-up automated or semi-automated message requesting pricing information. This could be triggered manually or on a schedule (e.g., 24-48 hours after first message). The follow-up message should reference the initial contact and request product prices.
- **Affected Modules**: `apps/Server/app/services/` (outreach_service.py); `apps/Server/app/api/`; potential scheduler/cron
- **Dependencies**: REQ-004, REQ-006
- **Acceptance Criteria**:
  - [ ] Follow-up message can be triggered manually per supplier
  - [ ] Follow-up template references the initial introduction
  - [ ] Both email and WeChat follow-up templates are available
  - [ ] Follow-up status is tracked per supplier

### Stream 3: Real-Time Team Collaboration
Ensure the back-office team can access newly captured supplier data and start organizing products with minimal delay.

#### Requirements

##### REQ-008: Real-Time Supplier Data Visibility
- **Type**: feature
- **Priority**: P1
- **Description**: Suppliers created via business card capture must be immediately visible to all team members in the Kompass Suppliers page, Pipeline Kanban, and any relevant dashboards. No manual sync or refresh should be required beyond a standard page load. The dashboard should show a "recently added" section or filter for suppliers added during the current trade fair period.
- **Affected Modules**: `apps/Client/src/pages/kompass/SuppliersPage.tsx`; `apps/Client/src/pages/kompass/DashboardPage.tsx`; `apps/Server/app/services/dashboard_service.py`
- **Dependencies**: REQ-003
- **Acceptance Criteria**:
  - [ ] Newly created suppliers appear in the Suppliers list within seconds of creation
  - [ ] Dashboard shows a count or feed of suppliers added today
  - [ ] Team members can filter suppliers by creation date to see fair captures
  - [ ] Pipeline Kanban shows new suppliers in the "contacted" column immediately

##### REQ-009: Supplier Activity Log
- **Type**: feature
- **Priority**: P2
- **Description**: Add an activity log or timeline to each supplier record showing key events: creation (with "source: business card" tag), email sent, WeChat contact added, messages sent, brochure received. This gives the back-office team visibility into the outreach status for each supplier.
- **Affected Modules**: `apps/Server/database/schema.sql` (new supplier_activity_log table); `apps/Server/app/services/supplier_service.py`; `apps/Client/src/components/kompass/` (activity timeline component)
- **Dependencies**: REQ-003, REQ-004
- **Acceptance Criteria**:
  - [ ] Each supplier has a chronological activity log
  - [ ] Activities are auto-logged for: creation, email sent, WeChat contact added, message sent
  - [ ] Activity log is visible in the supplier detail view
  - [ ] Each activity entry has a timestamp, type, and description

### Stream 4: Messaging Platform Integration Infrastructure
Investigate and implement the foundational WeChat integration layer needed for outreach features.

#### Requirements

##### REQ-010: WeChat API/Integration Research & Implementation
- **Type**: architecture_decision
- **Priority**: P0
- **Description**: Research WeChat's official API capabilities for: (1) adding contacts from QR codes, (2) sending messages programmatically, (3) any restrictions for business/international accounts. Determine the best integration approach — WeChat Official Account API, WeChat Work API, third-party services, or a semi-manual workflow with deep-links and clipboard. Document findings and implement the chosen approach.
- **Affected Modules**: `apps/Server/app/services/` (new wechat integration); infrastructure/deployment config
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] WeChat API capabilities and limitations are documented
  - [ ] A decision is made and documented on the integration approach (full API, deep-links, or hybrid)
  - [ ] A proof-of-concept demonstrates the chosen approach working end-to-end
  - [ ] Fallback behavior is defined for scenarios where WeChat API is unavailable

##### REQ-011: Message Template Management
- **Type**: feature
- **Priority**: P2
- **Description**: Create a settings page or section where the user can manage outreach message templates for both email and WeChat. Templates should support placeholders (e.g., `{{supplier_name}}`, `{{contact_name}}`, `{{user_name}}`). Default templates should be pre-configured.
- **Affected Modules**: `apps/Server/database/schema.sql` (new message_templates table); `apps/Server/app/services/`; `apps/Client/src/pages/kompass/SettingsPage.tsx`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] User can create, edit, and delete message templates
  - [ ] Templates support placeholder variables that are auto-filled
  - [ ] Default templates are provided for: initial email, initial WeChat message, follow-up email, follow-up WeChat
  - [ ] Templates are accessible from the settings page

## Implementation Waves

### Wave 1: Foundation (Days 1–4)
**REQ-010** (WeChat API Research), **REQ-001** (Mobile Photo Upload), **REQ-002** (Business Card AI Extraction), **REQ-011** (Message Templates)

Rationale: REQ-010 is critical path — the WeChat integration approach must be determined before building outreach features. REQ-001 and REQ-002 are the core capture pipeline with no dependencies. REQ-011 provides the template infrastructure needed by outreach features. All four can proceed in parallel.

### Wave 2: Core Pipeline (Days 5–8)
**REQ-003** (Auto-Create Supplier), **REQ-005** (WeChat QR Contact Addition), **REQ-008** (Real-Time Visibility)

Rationale: REQ-003 depends on REQ-002 for extracted data. REQ-005 depends on REQ-002 for QR detection and REQ-010 for the WeChat integration approach. REQ-008 depends on REQ-003 for suppliers to display.

### Wave 3: Outreach Automation (Days 9–12)
**REQ-004** (Email Outreach), **REQ-006** (WeChat Message), **REQ-009** (Activity Log)

Rationale: Email and WeChat outreach depend on supplier creation (REQ-003) and WeChat integration (REQ-010). Activity log depends on having events to log from creation and outreach.

### Wave 4: Enhancements (Days 13–14)
**REQ-007** (Follow-Up Messages)

Rationale: Follow-up messaging builds on top of the initial outreach system and is lower priority. Implement only if time permits before the March 27 deadline.

## Cross-Cutting Concerns

- **Database Migrations**: New tables needed for `supplier_activity_log` and `message_templates`. The existing `suppliers` table may need a `source` column (e.g., `manual`, `business_card`, `import`) to track how suppliers were created.
- **Mobile Responsiveness**: The existing Kompass app is desktop-oriented (Material-UI). The business card capture flow must be usable on mobile browsers — this may require a dedicated mobile-optimized route or PWA adjustments.
- **WeChat Restrictions in China**: Telegram and some Western services are blocked in China. The entire workflow must function over WeChat or direct HTTPS (not relying on blocked services). VPN availability should not be assumed.
- **Email Infrastructure**: The backend currently has no transactional email sending capability. An SMTP service or email API (e.g., SendGrid, AWS SES, Resend) must be configured.
- **API Rate Limits**: AI extraction (Claude/GPT-4o) may have rate limits. If many business cards are captured in quick succession at a fair, the system should queue and process them gracefully.
- **Existing Extraction Service Reuse**: The current extraction service (`extraction_service.py`) supports image processing via AI vision. The business card extraction should extend this existing architecture rather than building a parallel system.
- **Authentication on Mobile**: The user must be able to authenticate on a mobile browser at the trade fair. The existing JWT auth should work, but session persistence and token refresh should be verified for mobile use.
- **Internationalization**: Business cards will be in Chinese and/or English. The AI extraction prompt must handle both languages and mixed-language cards.

## Open Questions

- **Q1**: What is the exact WeChat integration approach? WeChat's API ecosystem (Official Account, Mini Programs, WeChat Work) has varying capabilities and restrictions. Can messages be sent programmatically, or will the workflow be semi-manual (deep-link to WeChat + copy/paste message)? — Context: "Ese QR code es el que lo va a llevar a que agregue ese contacto a un wechat... lo más importante es atacar esos tres frentes y empezar a comunicarse con la fábrica"

- **Q2**: Should business card photos be submitted via a messaging bot (e.g., Telegram/WeChat bot) or directly through the Kompass web app? The transcript initially discussed sending photos via a messaging app, then pivoted to using the existing web app. — Context: "vos estás diciendo... dos proveedores te la pasan tarjetas... a eso lo mandas por Telegram, no sé si te sirva... que podemos adecuarla" vs. "Nosotros la idea es montarla en la app que ya te disponibilizamos"

- **Q3**: How should brochures/portfolios received from suppliers be processed? Rubén wants his team to organize products in the "Biblia" (product catalog). Should incoming brochures be auto-imported using the existing AI extraction pipeline, or will the team manually upload them? — Context: "empezar a recibir la información de esa fábrica y poder organizar en la biblia nuestra para que el equipo mío... empiece a tener la información de cada fábrica y los productos"

- **Q4**: What is the scope of the "second message" for pricing? Is it a one-time manual trigger, an automated follow-up after a set delay, or a multi-step drip campaign? — Context: "si es posible que el segundo mes sea amazing. Thank you. Can you set me the prices? Lo que sea. Y empezar a tener números de precios."

- **Q5**: How many suppliers/business cards are expected per day at the fair? This affects the architecture (synchronous vs. queue-based processing) and AI API cost projections. — Context: Not explicitly discussed in the transcript.

- **Q6**: Does the monthly budget of ~$1,000 USD cover only infrastructure/hosting, or does it also need to cover AI API costs (Claude/GPT-4o vision calls for extraction)? — Context: "Tomás me dijo que no podíamos pagar ni a bala más de mil dólares mensuales"
