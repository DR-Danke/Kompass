# Real SMTP Email Service

**ADW ID:** 9cd1e419
**Date:** 2026-03-09
**Specification:** specs/issue-143-adw-9cd1e419-sdlc_planner-real-smtp-email-service.md

## Overview

Replaces the inline mock email logic in `quotation_service.py` with a shared, standalone `EmailService` that sends real emails via SMTP TLS when configured and falls back to mock mode when SMTP credentials are absent. Also adds automated trade fair introduction emails sent to newly captured suppliers.

## What Was Built

- **Shared EmailService** (`email_service.py`) — Core SMTP email service with mock mode fallback, MIME message construction, attachment support, and reply-to headers
- **Supplier introduction email** — HTML template for automated trade fair outreach, triggered when a supplier is created from a business card capture
- **Quotation email delegation** — `quotation_service.py` refactored to delegate all email logic to the shared `EmailService`
- **EmailSendResultDTO** — Generic DTO for email send results, used across all email operations
- **SMTP settings** — Configuration fields added to `Settings` for SMTP host, port, credentials, and mock mode
- **Comprehensive unit tests** — 457 lines of tests covering mock mode, SMTP sending, error handling, attachments, and templates

## Technical Implementation

### Files Modified

- `apps/Server/app/config/settings.py`: Added SMTP configuration fields (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `FROM_EMAIL`, `FROM_NAME`, `EMAIL_MOCK_MODE`)
- `apps/Server/app/models/kompass_dto.py`: Added `EmailSendResultDTO` with `success`, `message`, `sent_at`, `recipient_email`, and `mock_mode` fields
- `apps/Server/app/services/email_service.py`: **New file** — `EmailService` class with `send_email()`, `send_supplier_introduction()`, `send_quotation_email()`, and `_render_introduction_template()` methods
- `apps/Server/app/services/quotation_service.py`: Refactored `send_email()` to delegate to `email_service.send_quotation_email()`, removed inline mock logic and `os.environ` check
- `apps/Server/app/services/supplier_service.py`: Added introduction email trigger in `create_supplier_from_card()` — fire-and-forget, email failure never blocks supplier creation
- `apps/Server/tests/services/test_email_service.py`: **New file** — Unit tests for all email service functionality

### Key Changes

- **Mock mode is the default**: `EMAIL_MOCK_MODE=True` by default, ensuring development/testing environments never send real emails
- **SMTP TLS on port 587**: Real mode connects via `smtplib.SMTP` with `starttls()`, authenticates, and sends
- **Graceful error handling**: SMTP auth errors, connection errors, and general failures all return `success=False` without raising exceptions
- **Attachment support**: PDF attachments are base64-encoded and added as `MIMEBase` parts inside a `MIMEMultipart("mixed")` wrapper
- **Non-blocking supplier emails**: The introduction email in `create_supplier_from_card()` is wrapped in try/except so failures are logged but never prevent supplier creation

## How to Use

1. **Development (default)**: No configuration needed. `EMAIL_MOCK_MODE=True` by default — emails are logged to console but not sent
2. **Production SMTP setup**: Set these environment variables:
   ```bash
   EMAIL_MOCK_MODE=false
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   FROM_EMAIL=your-email@gmail.com
   FROM_NAME=Kompass
   ```
3. **Send quotation email**: Use the existing `POST /api/quotations/{id}/send` endpoint — it now delegates to the real email service
4. **Supplier introduction emails**: Automatic — when a supplier is created from a business card with an email address, the introduction email is sent automatically

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `EMAIL_MOCK_MODE` | `true` | When true, logs emails without sending |
| `SMTP_HOST` | `smtp.gmail.com` | SMTP server hostname |
| `SMTP_PORT` | `587` | SMTP server port (TLS) |
| `SMTP_USER` | `""` | SMTP username/email |
| `SMTP_PASSWORD` | `""` | SMTP password (use App Password for Gmail) |
| `FROM_EMAIL` | `""` | Sender email address |
| `FROM_NAME` | `Kompass` | Sender display name |

**Gmail note**: Use an [App Password](https://myaccount.google.com/apppasswords), not your regular Google password.

## Testing

```bash
# Run email service unit tests
cd apps/Server && python -m pytest tests/services/test_email_service.py -v --tb=short

# Verify quotation email refactoring
cd apps/Server && python -m pytest tests/services/test_quotation_service.py -v --tb=short

# Verify supplier service integration
cd apps/Server && python -m pytest tests/services/test_supplier_service.py -v --tb=short

# Verify import works
cd apps/Server && python -c "from app.services.email_service import email_service; print('Import OK')"
```

## Notes

- **No new dependencies**: Uses Python's built-in `smtplib` and `email.mime` modules
- **Synchronous pattern**: Matches the codebase convention — synchronous service methods called from async FastAPI routes
- **Extensible**: New email templates can be added following the `send_supplier_introduction()` pattern
- **Singleton**: `email_service = EmailService()` instantiated at module level, shared across the application
