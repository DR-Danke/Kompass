# Feature: Real SMTP Email Service

## Metadata
issue_number: `143`
adw_id: `9cd1e419`
issue_json: ``

## Feature Description
Replace the existing mock email implementation (`EMAIL_MOCK_MODE` in `quotation_service.py`) with a real, shared SMTP email service. This service will handle both the existing quotation email sending and a new automated introduction email for trade fair supplier outreach. The service supports a graceful mock mode fallback when SMTP is not configured, making it safe for development and testing environments.

## User Story
As a trading company operator
I want a real email service that sends quotation emails via SMTP and automated introduction emails to newly captured trade fair suppliers
So that I can communicate professionally with suppliers and clients without manual email composition

## Problem Statement
The current email sending in `quotation_service.py` is entirely mocked — it logs what it would send but never delivers actual emails. There is no shared email infrastructure, and no mechanism exists to send automated outreach emails to suppliers captured at trade fairs. This blocks the Trade Fair Supplier Capture workflow from completing its automated outreach pipeline.

## Solution Statement
Create a standalone `EmailService` class in `apps/Server/app/services/email_service.py` that:
1. Sends real emails via SMTP (TLS on port 587 by default) when configured
2. Falls back to mock mode when SMTP credentials are absent
3. Provides a `send_supplier_introduction()` method with an HTML introduction email template for trade fair outreach
4. Provides a `send_quotation_email()` method that the existing `quotation_service.py` will delegate to
5. Uses a generic `send_email()` core method that handles SMTP connection, MIME message construction, attachments, and reply-to headers
6. Adds an `EmailSendResultDTO` to the shared DTO module for consistent return types

## Relevant Files
Use these files to implement the feature:

- `apps/Server/app/services/quotation_service.py` — Contains the existing mock email implementation (lines 1130-1197) that will be refactored to delegate to the new `EmailService`. The `send_email` method currently checks `EMAIL_MOCK_MODE` env var and returns `QuotationSendEmailResponseDTO`.
- `apps/Server/app/models/kompass_dto.py` — Contains `QuotationSendEmailRequestDTO` (line 1512) and `QuotationSendEmailResponseDTO` (line 1530). A new generic `EmailSendResultDTO` will be added here.
- `apps/Server/app/api/quotation_routes.py` — Route handler for `POST /{quotation_id}/send` (line 472) that calls `quotation_service.send_email`. No changes needed to the route itself — the refactoring is internal to the service layer.
- `apps/Server/app/config/settings.py` — Application settings. SMTP configuration env vars will be added here.
- `apps/Server/app/services/supplier_service.py` — Contains `create_supplier_from_card()` (line 526). The introduction email trigger hook will be added here (but left inactive until TF-003 merges).
- `apps/Server/app/services/business_card_service.py` — Business card capture service, provides context for the trade fair workflow.
- `apps/Server/requirements.txt` — No new dependencies needed. Python's built-in `smtplib` and `email` modules are sufficient.
- `apps/Server/tests/services/test_quotation_service.py` — Existing email tests (lines 838-888) that must continue passing after refactoring.
- `apps/Server/tests/api/test_quotation_routes.py` — Existing route-level email tests that must continue passing.

### New Files
- `apps/Server/app/services/email_service.py` — The new shared email service with SMTP support, mock mode, introduction template, and quotation email delegation.
- `apps/Server/tests/services/test_email_service.py` — Unit tests for the new email service covering mock mode, SMTP sending, introduction template, quotation email, error handling, and attachment support.

## Implementation Plan
### Phase 1: Foundation
- Add SMTP configuration fields to `Settings` class (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `FROM_EMAIL`, `FROM_NAME`, `EMAIL_MOCK_MODE`)
- Add a generic `EmailSendResultDTO` to `kompass_dto.py` for the email service return type

### Phase 2: Core Implementation
- Create `email_service.py` with:
  - `EmailService` class with SMTP config loaded from env/settings
  - Core `send_email()` method: constructs MIME multipart message, connects via SMTP TLS, handles attachments, supports reply-to, falls back to mock mode
  - `send_supplier_introduction()` method: renders the trade fair introduction HTML template and calls `send_email()`
  - `send_quotation_email()` method: wraps `send_email()` with quotation-specific logic (PDF attachment support)
  - Singleton instance `email_service`
- Follow the existing service pattern: synchronous methods (matching `quotation_service.py`, `supplier_service.py`), print-based logging, singleton instance

### Phase 3: Integration
- Refactor `quotation_service.py` `send_email()` to delegate SMTP/mock logic to `email_service.send_quotation_email()` instead of inline mock code
- Add an email trigger hook in `supplier_service.py` `create_supplier_from_card()` that calls `email_service.send_supplier_introduction()` when the supplier has an email address (this fires after supplier creation)
- Ensure all existing tests pass without modification (the refactoring is internal)
- Add comprehensive unit tests for the new email service

## Step by Step Tasks

### Step 1: Add SMTP Settings to Configuration
- Open `apps/Server/app/config/settings.py`
- Add the following fields to the `Settings` class:
  - `SMTP_HOST: str = "smtp.gmail.com"`
  - `SMTP_PORT: int = 587`
  - `SMTP_USER: str = ""`
  - `SMTP_PASSWORD: str = ""`
  - `FROM_EMAIL: str = ""`
  - `FROM_NAME: str = "Kompass"`
  - `EMAIL_MOCK_MODE: bool = True`

### Step 2: Add EmailSendResultDTO to DTOs
- Open `apps/Server/app/models/kompass_dto.py`
- Add a new `EmailSendResultDTO` class near the existing email DTOs (after `QuotationSendEmailResponseDTO`):
  ```python
  class EmailSendResultDTO(BaseModel):
      """Generic result for email send operations."""
      success: bool
      message: str
      sent_at: Optional[datetime] = None
      recipient_email: str
      mock_mode: bool = Field(default=False, description="Whether email was sent in mock mode")
  ```

### Step 3: Create the Email Service
- Create new file `apps/Server/app/services/email_service.py`
- Implement `EmailService` class with:
  - `__init__`: Load SMTP config from `get_settings()` with env var overrides for backward compatibility (reads `EMAIL_MOCK_MODE` from env to maintain existing behavior)
  - `send_email(to_email, subject, html_body, plain_body=None, attachments=None, reply_to=None) -> EmailSendResultDTO`: Core method that:
    - In mock mode: logs and returns success with `mock_mode=True`
    - In real mode: constructs `MIMEMultipart("alternative")` message, adds plain text and HTML parts, adds file attachments if provided, connects via `smtplib.SMTP` with `starttls()`, authenticates, sends, and returns result
    - Handles SMTP errors gracefully with try/except returning `success=False`
  - `send_supplier_introduction(supplier_name, supplier_email, fair_name, sender_name="Rubén") -> EmailSendResultDTO`: Renders HTML introduction template and calls `send_email()`
  - `send_quotation_email(recipient_email, subject, body_html, pdf_attachment=None) -> EmailSendResultDTO`: Wraps `send_email()` with optional PDF attachment dict
  - Singleton: `email_service = EmailService()`
- Use Python's built-in `smtplib`, `email.mime.multipart`, `email.mime.text`, `email.mime.base` — no new dependencies
- Follow the project's synchronous service pattern (not async, matching all other services)
- Use print-based logging: `print(f"INFO [EmailService]: ...")`

### Step 4: Create Introduction Email HTML Template
- Inside `email_service.py`, add a method `_render_introduction_template(supplier_name, fair_name, sender_name) -> tuple[str, str, str]` that returns `(subject, html_body, plain_body)`
- Subject: `"Nice meeting you at {fair_name} — Kompass"`
- HTML body: Professional, mobile-friendly HTML email with:
  - Greeting referencing the trade fair
  - Brief company introduction
  - Call to action for collaboration
  - Sender signature with name
- Plain text fallback: Stripped version of the same content

### Step 5: Refactor Quotation Service to Use Email Service
- Open `apps/Server/app/services/quotation_service.py`
- Add import: `from app.services.email_service import email_service`
- Refactor the `send_email()` method (lines 1135-1197):
  - Keep the quotation lookup and PDF generation logic
  - Replace the inline mock/email logic with a call to `email_service.send_quotation_email()`
  - Map the `EmailSendResultDTO` result back to `QuotationSendEmailResponseDTO` for backward compatibility
  - Remove the direct `os.environ.get("EMAIL_MOCK_MODE")` check — let the email service handle it

### Step 6: Add Email Trigger Hook in Supplier Service
- Open `apps/Server/app/services/supplier_service.py`
- Add import: `from app.services.email_service import email_service`
- In `create_supplier_from_card()`, after the successful supplier creation (after line 614, before the return), add:
  ```python
  # Send introduction email if supplier has an email address
  if contact_email:
      try:
          email_result = email_service.send_supplier_introduction(
              supplier_name=supplier_name,
              supplier_email=contact_email,
              fair_name=fair_name or "the trade fair",
          )
          print(
              f"INFO [SupplierService]: Introduction email sent to {contact_email}: "
              f"success={email_result.success}, mock={email_result.mock_mode}"
          )
      except Exception as e:
          # Email failure should not block supplier creation
          print(f"WARN [SupplierService]: Failed to send introduction email: {e}")
  ```
- This is a non-blocking fire-and-forget: email failure must never prevent supplier creation from succeeding

### Step 7: Write Unit Tests for Email Service
- Create `apps/Server/tests/services/test_email_service.py`
- Test classes:
  - `TestEmailServiceInit`: Verify settings are loaded correctly, mock mode defaults to True
  - `TestSendEmailMockMode`: Test `send_email()` in mock mode returns success with `mock_mode=True`, logs appropriately
  - `TestSendEmailRealMode`: Patch `smtplib.SMTP` to test real mode — verify SMTP connection, starttls, login, sendmail are called with correct args
  - `TestSendEmailWithAttachments`: Test that attachments are properly added to MIME message
  - `TestSendEmailErrorHandling`: Test SMTP connection errors, auth errors, send errors all return `success=False` gracefully
  - `TestSendSupplierIntroduction`: Test template rendering produces correct subject and HTML, calls `send_email()` with expected args
  - `TestSendQuotationEmail`: Test quotation email with and without PDF attachment
- Use `@patch.dict("os.environ", {...})` and `@patch("smtplib.SMTP")` patterns matching existing test conventions

### Step 8: Verify Existing Tests Still Pass
- Run `cd apps/Server && python -m pytest tests/services/test_quotation_service.py -v --tb=short` to ensure the refactored quotation email tests pass
- Run `cd apps/Server && python -m pytest tests/api/test_quotation_routes.py -v --tb=short` to ensure route tests pass
- Run `cd apps/Server && python -m pytest tests/services/test_supplier_service.py -v --tb=short` to ensure supplier tests pass

### Step 9: Run Full Validation Suite
- Execute all validation commands listed below to ensure zero regressions

## Testing Strategy
### Unit Tests
- **EmailService initialization**: Verify SMTP config is read from settings/env vars, mock mode defaults correctly
- **Mock mode sending**: Verify emails return success without touching SMTP, `mock_mode=True` in result
- **Real SMTP sending**: Patch `smtplib.SMTP`, verify connection lifecycle (connect, starttls, login, sendmail, quit)
- **MIME message construction**: Verify subject, from, to, reply-to headers; HTML and plain text parts; attachment encoding
- **Attachment handling**: Verify PDF bytes are base64 encoded and attached with correct Content-Disposition
- **Error handling**: SMTP connection refused, auth failure, send failure all return `success=False` without raising
- **Introduction template**: Verify subject contains fair name, HTML contains supplier name and fair name, plain text fallback exists
- **Quotation email delegation**: Verify `quotation_service.send_email()` correctly delegates to `email_service` and maps results back to `QuotationSendEmailResponseDTO`
- **Supplier email trigger**: Verify `create_supplier_from_card()` calls `email_service.send_supplier_introduction()` when email present, skips when absent, doesn't fail on email error

### Edge Cases
- SMTP not configured (empty user/password) — should stay in mock mode or return meaningful error
- Empty/None `to_email` — should return `success=False` with error message
- Very large PDF attachment — should not crash
- Non-ASCII characters in supplier name, fair name, email body — proper encoding
- Email send failure after supplier creation — supplier creation must still succeed
- No `fair_name` on capture — uses fallback "the trade fair"
- `contact_email` is None on card — introduction email is skipped (no error)

## Acceptance Criteria
- A new `EmailService` class exists in `apps/Server/app/services/email_service.py` with `send_email()`, `send_supplier_introduction()`, and `send_quotation_email()` methods
- The service reads SMTP config from environment variables (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `FROM_EMAIL`, `FROM_NAME`, `EMAIL_MOCK_MODE`)
- When `EMAIL_MOCK_MODE=true` (default), emails are logged but not sent, and results include `mock_mode=True`
- When `EMAIL_MOCK_MODE=false` and SMTP is configured, real emails are sent via SMTP TLS
- `quotation_service.py` no longer contains inline email mock logic — it delegates to `email_service`
- `supplier_service.py` `create_supplier_from_card()` sends an introduction email when the supplier has an email address
- Email failures in the supplier flow do not block supplier creation
- The introduction email template includes the trade fair name, supplier name, and sender name
- All existing quotation email tests pass without modification
- New unit tests for the email service achieve full coverage of mock mode, SMTP sending, error handling, and templates
- No new Python dependencies are required (uses stdlib `smtplib` and `email`)
- `EmailSendResultDTO` is added to `kompass_dto.py`

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/services/test_email_service.py -v --tb=short` — Run new email service unit tests
- `cd apps/Server && python -m pytest tests/services/test_quotation_service.py -v --tb=short` — Verify refactored quotation email tests pass
- `cd apps/Server && python -m pytest tests/services/test_supplier_service.py -v --tb=short` — Verify supplier service tests pass (with email trigger)
- `cd apps/Server && python -m pytest tests/api/test_quotation_routes.py -v --tb=short` — Verify quotation route tests pass
- `cd apps/Server && python -m pytest tests/ -v --tb=short` — Run all Server tests to validate zero regressions
- `cd apps/Server && python -c "from app.services.email_service import email_service; print('Import OK')"` — Verify email service imports cleanly
- `cd apps/Client && npx tsc --noEmit` — Run Client type check (no client changes expected, regression check)
- `cd apps/Client && npm run build` — Run Client build (regression check)

## Notes
- **No new dependencies**: Python's built-in `smtplib` and `email.mime` modules handle SMTP and MIME construction. No need for `aiosmtplib` since all services in this codebase are synchronous.
- **Synchronous pattern**: Despite the issue describing `async def` methods, the codebase consistently uses synchronous service methods called from async FastAPI routes. The email service follows this pattern for consistency.
- **Parallel execution with TF-003**: This issue runs in parallel with issue #142 (Auto-Create Supplier from Business Card). The email trigger in `create_supplier_from_card()` is safe because that method already exists from TF-003. If building in isolation before TF-003 merges, the trigger code still compiles — it just won't be exercised until TF-003's supplier creation from cards is live.
- **Gmail App Passwords**: When using Gmail SMTP, users need to generate an App Password (not their regular password) at https://myaccount.google.com/apppasswords. This should be documented in `.env.sample`.
- **Future Wave 4 (TF-008)**: The email service is designed to be extensible for follow-up message templates. Adding new templates follows the same pattern as `send_supplier_introduction()`.
- **Settings consolidation**: The `EMAIL_MOCK_MODE` env var is kept for backward compatibility with existing tests that use `@patch.dict("os.environ", {"EMAIL_MOCK_MODE": "true"})`. The new Settings field also reads it, providing two access paths that stay in sync.
