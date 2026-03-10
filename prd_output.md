# PRD: Business Card Capture & Supplier Creation UX Improvements

## Meeting Metadata
- **Date**: 10th March, 2026
- **Participants**: Speaker 1 (Developer), Speaker 2 (Rubén — User/Tester)
- **Duration**: ~8 minutes
- **Context**: Live feedback session where Rubén tested the business card capture feature on mobile and desktop, identifying UX issues and bugs in the card-to-supplier workflow.

## Executive Summary
Rubén tested the end-to-end business card capture flow (photo capture → AI extraction → card review → supplier creation → follow-up email) and surfaced several UX and data quality issues. The primary problems are: (1) no automatic navigation from card capture to card review, (2) card images cannot be viewed or downloaded, (3) the AI extraction frequently misidentifies the company/supplier name, and (4) the supplier name appears blank after approval. The follow-up email flow worked correctly. QR code scanning was mentioned as a future need but deferred.

## Work Streams

### Stream 1: Card Capture UX Flow
Improve the card capture page navigation and discoverability so users intuitively move through the capture → review → approve workflow.

#### Requirements

##### REQ-001: Auto-Navigate to Card Review After Capture
- **Type**: feature
- **Priority**: P1
- **Description**: After a user successfully captures and uploads a business card photo (from the CardCapturePage), the app should automatically navigate them to the CardReviewPage to review the extracted data. Currently, the user must manually navigate to the review page, which is not intuitive.
- **Affected Modules**: `apps/Client/src/pages/kompass/CardCapturePage.tsx`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] After a successful card photo upload and extraction response, the user is automatically redirected to the CardReviewPage
  - [ ] The newly captured card is pre-selected or highlighted on the review page
  - [ ] A loading/progress indicator is shown while the extraction is processing

##### REQ-002: Make Recent Captures Clickable
- **Type**: bug
- **Priority**: P1
- **Description**: The "Recent Capture" section on the Card Capture page displays captured cards but they are not clickable. Users expect to click a recent capture to navigate to its review or see its details.
- **Affected Modules**: `apps/Client/src/pages/kompass/CardCapturePage.tsx`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] Each item in the "Recent Captures" list is clickable
  - [ ] Clicking a recent capture navigates the user to the CardReviewPage with that card's data displayed

### Stream 2: Card Image Viewing & Download
Enable users to view and download the original business card photo from the review page.

#### Requirements

##### REQ-003: Enable Card Image Click-to-View
- **Type**: bug
- **Priority**: P1
- **Description**: On the CardReviewPage, clicking the business card thumbnail/image does nothing. Users expect to be able to click the image to view it at full size (e.g., in a lightbox or modal).
- **Affected Modules**: `apps/Client/src/pages/kompass/CardReviewPage.tsx`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] Clicking the card image thumbnail opens a full-size view of the original photo (modal/lightbox)
  - [ ] The full-size view can be closed by clicking outside it or pressing Escape

##### REQ-004: Enable Card Image Download
- **Type**: feature
- **Priority**: P2
- **Description**: Users should be able to download the original business card photo from the CardReviewPage. This allows them to keep a copy of the card image for their records.
- **Affected Modules**: `apps/Client/src/pages/kompass/CardReviewPage.tsx`
- **Dependencies**: REQ-003
- **Acceptance Criteria**:
  - [ ] A download button/icon is visible on the card image view (either on the thumbnail or in the full-size modal)
  - [ ] Clicking the download button saves the original card image to the user's device
  - [ ] The downloaded file has a meaningful name (e.g., includes the supplier/contact name)

### Stream 3: AI Extraction Accuracy — Company Name
Improve the AI extraction logic to correctly identify and extract the company/supplier name from business cards.

#### Requirements

##### REQ-005: Improve Company Name Extraction from Business Cards
- **Type**: bug
- **Priority**: P0
- **Description**: The AI extraction frequently fails to correctly identify the company/organization name from the business card. In testing, the company field was either left blank or populated with the contact person's name instead of the company name. This is a critical issue since the supplier record is created with a blank or incorrect name, requiring manual correction every time.
- **Affected Modules**: `apps/Server/app/services/business_card_service.py`, `apps/Server/app/services/extraction_service.py`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] The AI extraction correctly identifies and extracts the company/organization name as a distinct field from the contact person's name
  - [ ] When a company name is present on the card, the supplier record is created with the correct company name (not the contact person's name)
  - [ ] When a company name cannot be determined, the field is flagged for manual review rather than left blank

##### REQ-006: Fix Supplier Name Blank After Card Approval
- **Type**: bug
- **Priority**: P0
- **Description**: After approving a business card on the CardReviewPage and creating a supplier, the supplier appears in the Suppliers list with a blank name. The extracted name data appears to be mapped to the wrong field or lost during the approval/creation process.
- **Affected Modules**: `apps/Client/src/pages/kompass/CardReviewPage.tsx`, `apps/Server/app/services/business_card_service.py`, `apps/Client/src/pages/kompass/SuppliersPage.tsx`
- **Dependencies**: REQ-005
- **Acceptance Criteria**:
  - [ ] After approving a card and creating a supplier, the supplier name is correctly populated in the Suppliers list
  - [ ] The company name from extraction maps to the supplier `name` field
  - [ ] The contact person name from extraction maps to the appropriate contact field (not the supplier name)

## Implementation Waves

### Wave 1: Critical Data Fixes
**REQ-005, REQ-006** — These are P0 bugs that make the core card-to-supplier workflow produce incorrect data. Must be fixed first as they affect data integrity and are blocking for production use.

### Wave 2: Navigation & Discoverability
**REQ-001, REQ-002** — P1 UX improvements that make the capture-to-review flow intuitive. These don't depend on Wave 1 technically but are sequenced after to prioritize data correctness first.

### Wave 3: Image Viewing & Download
**REQ-003, REQ-004** — P1/P2 enhancements for viewing and downloading card images. REQ-004 depends on REQ-003.

## Cross-Cutting Concerns
- **AI Extraction Prompt/Model**: Improvements to company name extraction (REQ-005) may require changes to the AI prompt template or model parameters in the extraction service. These changes should be tested against a diverse set of business card layouts (single-person, multi-person, cards with logos, cards without explicit company names).
- **Field Mapping Contract**: The data contract between the extraction response, the CardReviewPage form, and the supplier creation endpoint needs to be audited to ensure `company_name` and `contact_name` are distinct fields mapped correctly end-to-end (REQ-005, REQ-006).
- **Mobile UX**: The card capture flow is primarily used on mobile devices. All navigation changes (REQ-001, REQ-002) and image viewing (REQ-003) must work well on mobile viewports and touch interactions.

## Open Questions

- **Q1**: Should the app support QR code scanning from business cards in addition to photo capture? — Context: "No, aquí no hay QR" / "Después vemos lo del QR" — Speaker 2 noticed a card had a QR code and Speaker 1 deferred this. Needs decision on whether QR scanning should be a future requirement and what data it would extract.
- **Q2**: Should mobile sessions share authentication state with desktop sessions? — Context: "¿Pero por qué no me las tiene si yo las tengo en el computador?" — Rubén expected his login to persist across devices. This is standard browser behavior (sessions are per-browser), but may indicate a need for easier mobile login (e.g., magic link, QR login, or "remember me" improvements).
- **Q3**: What specific business card layouts and edge cases should be used to validate extraction accuracy improvements? — Context: "Es que lo probés con tarjetas sin que me des feedback. Todo el feedback que me des lo necesito en audio." — Speaker 1 requested Rubén test with multiple cards. A test corpus of diverse card layouts is needed to measure extraction accuracy before and after fixes.
- **Q4**: What does "Witch" refer to in the context of the follow-up email flow? — Context: "Supongamos que bata Witch, ese es el que... Mientras saco lo de Witch" — This reference is unclear and may relate to a competing tool, an alternative email integration, or a feature name. Clarification needed on whether this impacts any requirements.
