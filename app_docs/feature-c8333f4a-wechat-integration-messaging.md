# WeChat Integration Messaging

**ADW ID:** c8333f4a
**Date:** 2026-03-09
**Specification:** specs/issue-146-adw-c8333f4a-sdlc_planner-wechat-integration-messaging.md

## Overview

Adds WeChat Official Account integration to the Kompass Trade Fair Supplier Capture system. Supports two flows: (1) receiving business card photos via WeChat webhook and routing them to the existing extraction pipeline, and (2) sending automated outreach messages to suppliers via WeChat. Includes mock mode fallback for development when WeChat API credentials are not configured.

## What Was Built

- **WeChatService** — Singleton service with mock mode fallback following the EmailService pattern
- **WeChat webhook endpoints** — Unauthenticated GET (verification) and POST (incoming messages) as required by WeChat
- **Authenticated messaging endpoint** — POST `/api/wechat/send/{supplier_id}` for sending introduction or custom messages
- **Status endpoint** — GET `/api/wechat/status` for checking configuration status
- **QR code decoding** — Extracts QR codes from business card images using pyzbar
- **WeChat DTOs** — WeChatMessageDTO, WeChatStatusDTO, WeChatSendResultDTO
- **Comprehensive test suite** — Unit tests for both service and routes

## Technical Implementation

### Files Modified

- `apps/Server/app/config/settings.py`: Added WECHAT_APP_ID, WECHAT_APP_SECRET, WECHAT_VERIFY_TOKEN, WECHAT_MOCK_MODE settings
- `apps/Server/app/models/kompass_dto.py`: Added WeChatMessageDTO, WeChatStatusDTO, WeChatSendResultDTO
- `apps/Server/main.py`: Registered wechat_router at `/api/wechat`
- `apps/Server/requirements.txt`: Added `pyzbar>=0.1.9` dependency

### Files Created

- `apps/Server/app/services/wechat_service.py`: Core WeChat integration service (371 lines)
- `apps/Server/app/api/wechat_routes.py`: API route handlers (122 lines)
- `apps/Server/tests/services/test_wechat_service.py`: Service unit tests (425 lines)
- `apps/Server/tests/api/test_wechat_routes.py`: Route unit tests (323 lines)

### Key Changes

- **Webhook verification**: Implements WeChat's SHA1 signature verification protocol — sorts `[verify_token, timestamp, nonce]`, joins and hashes with SHA1, compares to provided signature
- **Incoming message handling**: Parses WeChat XML messages; image messages are routed to `business_card_service.create_capture()` for AI extraction; text messages receive an acknowledgment reply
- **Outgoing messaging**: Sends text messages via WeChat Custom Message API with access token caching (auto-refresh on expiry). Supports introduction templates and custom messages
- **Mock mode**: When `WECHAT_MOCK_MODE=True` (default) or credentials are empty, all operations log instead of calling WeChat API. Returns success DTOs with `mock_mode=True`
- **QR decoding**: Uses pyzbar + Pillow to decode QR codes from business card images, enabling WeChat ID extraction from printed QR codes

### API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/wechat/webhook` | None | WeChat webhook verification |
| POST | `/api/wechat/webhook` | None | Incoming message handler |
| POST | `/api/wechat/send/{supplier_id}` | admin/manager | Send message to supplier |
| GET | `/api/wechat/status` | authenticated | Configuration status |

## How to Use

1. **Configure WeChat credentials** in `.env`:
   ```bash
   WECHAT_APP_ID=your-app-id
   WECHAT_APP_SECRET=your-app-secret
   WECHAT_VERIFY_TOKEN=your-verify-token
   WECHAT_MOCK_MODE=False
   ```

2. **Set up webhook** in WeChat Official Account admin console pointing to `https://your-domain/api/wechat/webhook`

3. **Send introduction message** to a supplier:
   ```bash
   POST /api/wechat/send/{supplier_id}
   Authorization: Bearer <token>
   {
     "supplier_id": "uuid",
     "message_type": "introduction"
   }
   ```

4. **Send custom message**:
   ```bash
   POST /api/wechat/send/{supplier_id}
   Authorization: Bearer <token>
   {
     "supplier_id": "uuid",
     "message_type": "custom",
     "custom_content": "Your message here"
   }
   ```

5. **Check status**: `GET /api/wechat/status` returns enabled, configured, mock_mode flags

6. **Mock mode** (default): Leave credentials empty or set `WECHAT_MOCK_MODE=True`. Messages are logged but not sent. Users can preview generated messages and manually copy-paste them into WeChat.

## Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `WECHAT_APP_ID` | str | `""` | WeChat Official Account App ID |
| `WECHAT_APP_SECRET` | str | `""` | WeChat Official Account App Secret |
| `WECHAT_VERIFY_TOKEN` | str | `""` | Token for webhook signature verification |
| `WECHAT_MOCK_MODE` | bool | `True` | When True, logs instead of calling WeChat API |

## Testing

```bash
# WeChat service tests
cd apps/Server && python -m pytest tests/services/test_wechat_service.py -v --tb=short

# WeChat route tests
cd apps/Server && python -m pytest tests/api/test_wechat_routes.py -v --tb=short

# All tests (zero regression check)
cd apps/Server && python -m pytest tests/ -v --tb=short
```

## Notes

- **pyzbar system dependency**: Requires `libzbar0` system library (`sudo apt-get install libzbar0`). QR decoding gracefully returns None if not installed.
- **WeChat API limitations**: Official Account API only allows messaging users who have followed the account and messaged within the last 48 hours.
- **Phone-to-WeChat resolution**: `resolve_phone_to_wechat()` always returns None — WeChat does not expose a phone-to-ID lookup API.
- **Webhook endpoints are unauthenticated**: Required by WeChat's server-to-server protocol. All other endpoints require JWT authentication.
- **Future extension**: TF-008 (follow-up message templates) will add a `send_follow_up` method and "follow_up" message_type support.
