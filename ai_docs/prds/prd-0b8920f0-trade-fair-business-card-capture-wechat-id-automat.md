# PRD: Trade Fair Business Card Capture — WeChat ID & Automated Follow-Up

## Meeting Metadata
- **Date**: 10th March, 2026
- **Participants**: Speaker 1 (Developer), Speaker 2 (Rubén — Business User/Stakeholder)
- **Duration**: ~4 minutes
- **Context**: Feedback session on improving the trade fair business card capture workflow in Kompass, focusing on WeChat ID extraction and automated email follow-up during supplier onboarding at Chinese trade fairs.

## Executive Summary
Rubén described his trade fair workflow where he visits supplier booths, collects business cards, and adds suppliers on WeChat. He wants the Kompass card capture feature to (1) extract WeChat ID from business cards or QR codes and store it as a supplier field, and (2) automatically send a follow-up email to the supplier upon card capture. WeChat contact management itself will remain manual — the app should focus on data extraction and automated outreach.

## Work Streams

### Stream 1: WeChat ID Supplier Field
Extend the supplier data model and business card extraction to capture and store WeChat IDs from business cards and QR codes scanned at trade fairs.

#### Requirements

##### REQ-001: Add WeChat ID Field to Supplier Data Model
- **Type**: feature
- **Priority**: P1
- **Description**: Add a `wechat_id` text field to the suppliers table and all related DTOs, API endpoints, and frontend forms. This field stores the supplier contact's WeChat identifier, which is critical for ongoing communication with Chinese suppliers. The field should be optional and editable.
- **Affected Modules**: `apps/Server/database/schema.sql` (suppliers table), `apps/Server/app/models/kompass_dto.py`, `apps/Server/app/repository/kompass_repository.py`, `apps/Server/app/services/supplier_service.py`, `apps/Server/app/api/suppliers.py`, `apps/Client/src/types/kompass.ts`, `apps/Client/src/pages/kompass/SuppliersPage.tsx`, `apps/Client/src/services/kompassService.ts`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] `wechat_id` column exists in the `suppliers` table as an optional text field
  - [ ] Supplier create/update API endpoints accept and persist `wechat_id`
  - [ ] Supplier detail view and edit form display the WeChat ID field
  - [ ] WeChat ID is included in supplier list/detail API responses
  - [ ] Existing suppliers without a WeChat ID are unaffected (field defaults to null)

##### REQ-002: Extract WeChat ID from Business Card via AI
- **Type**: feature
- **Priority**: P1
- **Description**: Enhance the AI-powered business card extraction to recognize and extract WeChat IDs from business card images. WeChat IDs may appear as text (e.g., labeled "WeChat", "微信", or "Wechat ID") or embedded in QR codes printed on the card. The extracted WeChat ID should be included in the extraction result and mapped to the new `wechat_id` supplier field.
- **Affected Modules**: `apps/Server/app/services/` (extraction service), `apps/Server/app/api/` (extract routes), `apps/Client/src/pages/kompass/` (CardCapturePage, CardReviewPage)
- **Dependencies**: REQ-001
- **Acceptance Criteria**:
  - [ ] AI extraction prompt/schema includes WeChat ID as an expected field
  - [ ] When a business card image contains a visible WeChat ID (text or QR code label), the extraction output includes it
  - [ ] Extracted WeChat ID is displayed on the Card Review page for user confirmation
  - [ ] Confirmed WeChat ID is saved to the supplier's `wechat_id` field upon supplier creation

### Stream 2: Automated Follow-Up Email on Card Capture
Automatically send a follow-up email to newly captured suppliers during trade fair card scanning, so the user can continue conversations at the fair while outreach happens in the background.

#### Requirements

##### REQ-003: Auto-Send Follow-Up Email After Business Card Capture
- **Type**: feature
- **Priority**: P1
- **Description**: When a business card is captured and the supplier is confirmed/created, automatically trigger a follow-up email to the supplier's extracted email address. This should happen in the background so the user can continue scanning cards at the fair. The email should use the existing outreach/follow-up email template system. The user should be able to see that an email was sent (or queued) from the card review flow.
- **Affected Modules**: `apps/Server/app/services/` (outreach/email service, supplier service), `apps/Server/app/api/` (extract or suppliers routes), `apps/Client/src/pages/kompass/` (CardReviewPage or CardCapturePage)
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] Upon confirming a newly captured supplier (from business card), a follow-up email is automatically sent to the supplier's email address
  - [ ] The email uses an existing follow-up template (or a configurable "trade fair introduction" template)
  - [ ] Email sending occurs asynchronously and does not block the card capture/review flow
  - [ ] The user receives visual confirmation (e.g., toast notification or status indicator) that the email was sent or queued
  - [ ] If no email address was extracted from the card, no email is sent and the user is informed

##### REQ-004: Trade Fair Follow-Up Email Template
- **Type**: feature
- **Priority**: P2
- **Description**: Create a default email template specifically for trade fair follow-up. The template should introduce the buyer, reference the trade fair meeting, and express interest in the supplier's products. The template should support placeholder variables for supplier name, company name, fair name, and buyer name.
- **Affected Modules**: `apps/Server/app/services/` (outreach/template service), `apps/Client/src/pages/kompass/` (outreach or settings-related pages)
- **Dependencies**: REQ-003
- **Acceptance Criteria**:
  - [ ] A "Trade Fair Follow-Up" email template exists in the system (seeded or user-creatable)
  - [ ] Template supports placeholder variables: `{supplier_name}`, `{company_name}`, `{fair_name}`, `{buyer_name}`
  - [ ] The template is selectable as the default for auto-send on card capture
  - [ ] User can preview and edit the template before it is used

## Implementation Waves

### Wave 1: Foundation
**REQ-001** — Add the WeChat ID field to the data model across backend and frontend. This is a prerequisite for extraction and has no dependencies.

**REQ-003** — Implement automated email sending on card capture. This is independent of the WeChat ID work and addresses the highest-impact user pain point (manual follow-up during fairs).

### Wave 2: AI Extraction & Templates
**REQ-002** — Enhance AI extraction to capture WeChat IDs from business cards. Depends on REQ-001 (field must exist to store the extracted value).

**REQ-004** — Create the trade fair email template. Depends on REQ-003 (email sending infrastructure must exist).

## Cross-Cutting Concerns
- **Database Migration**: REQ-001 requires an `ALTER TABLE suppliers ADD COLUMN wechat_id TEXT` migration. Must be backward-compatible (nullable column).
- **AI Extraction Prompt Changes**: REQ-002 modifies the extraction prompt/schema. Must be tested to ensure existing fields (name, email, phone, company, province) are not degraded by adding WeChat ID extraction.
- **Email Service Configuration**: REQ-003 relies on the existing outreach email infrastructure. Must confirm that email sending works in mock mode during development and that SMTP/email provider credentials are properly configured for production fair use.
- **Mobile UX**: The card capture flow is used on mobile devices at trade fairs. Any UI additions (WeChat ID display, email confirmation) must be responsive and fast to not slow down the scanning workflow.

## Open Questions

- **Q1**: Should the system attempt to decode QR codes embedded in business card photos to extract the WeChat ID, or only extract it from visible text? — Context: "al escanear el QR que lo agregue de una mi wechat" / "suele estar en QR" — QR decoding from a photo of a business card is technically complex and may require a separate QR detection step. Clarify whether this is in scope or if text-based extraction is sufficient for V1.

- **Q2**: Which follow-up email template should be used for auto-send? Is there an existing template, or does a new "trade fair" template need to be created? — Context: "que se mande mail automatizado, se atrape un mail con la tarjeta" — The transcript mentions automated email but does not specify the template content or whether existing outreach templates apply.

- **Q3**: Should the auto-email be opt-in (user confirms before send) or fully automatic (sent immediately upon card confirmation)? — Context: "mientras yo hable ya esté mandando mails" — Rubén implies it should be automatic, but this could lead to accidental emails if a card is confirmed prematurely. Clarify the desired level of user control.

- **Q4**: What specific information should be included in the follow-up email? Should it attach the business card image? — Context: "se atrape un mail con la tarjeta" — "atrape un mail con la tarjeta" could mean the email should include/attach the business card photo, or simply that capturing the card triggers the email. Clarification needed.