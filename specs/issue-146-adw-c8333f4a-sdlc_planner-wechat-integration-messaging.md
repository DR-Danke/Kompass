# Feature: WeChat Integration for Input & Messaging

## Metadata
issue_number: `146`
adw_id: `c8333f4a`
issue_json: ``

## Feature Description
Add WeChat integration to the Kompass Trade Fair Supplier Capture system supporting two flows: (1) receiving business card photos via WeChat webhook and routing them to the existing extraction pipeline, and (2) sending automated outreach messages to suppliers via WeChat. This includes webhook verification for WeChat Official Account setup, incoming message handling (image messages routed to business card extraction), outgoing text messaging for supplier introductions, QR code decoding from business card images, and a mock mode fallback for development and when WeChat API credentials are not yet available. The implementation mirrors the existing EmailService pattern with mock mode support, ensuring a manual workflow fallback where users can copy generated messages and send them via WeChat manually.

## User Story
As a trade fair sourcing agent
I want to receive business card photos via WeChat and send automated introduction messages to suppliers through WeChat
So that I can streamline supplier capture and outreach at trade fairs where WeChat is the dominant communication platform

## Problem Statement
At Chinese trade fairs, WeChat is the primary communication channel. Currently there is no way to receive business card photos via WeChat for AI extraction, nor send automated outreach messages to newly captured suppliers through WeChat. Email (TF-004) provides a fallback but WeChat integration is critical for the Chinese supplier market.

## Solution Statement
Build a WeChat integration service following the existing EmailService pattern with mock mode support. Implement webhook verification for WeChat Official Account setup, incoming image message handling that routes to the business card extraction pipeline, outgoing text messaging for supplier introductions, QR code decoding from card images, and configuration status endpoints. The service gracefully degrades to mock mode when WeChat API credentials are not configured, and supports a manual workflow where users can preview and copy messages to send via WeChat manually.

## Relevant Files
Use these files to implement the feature:

### Existing Files to Modify
- `apps/Server/main.py` — Register the new wechat_router (line 88, add import and `app.include_router`)
- `apps/Server/app/models/kompass_dto.py` — Add WeChat DTOs (WeChatMessageDTO, WeChatStatusDTO, WeChatSendResultDTO) following the EmailSendResultDTO pattern at line 1542
- `apps/Server/app/config/settings.py` — Add WECHAT_* settings (APP_ID, APP_SECRET, VERIFY_TOKEN, MOCK_MODE) following the SMTP settings pattern at line 35

### Existing Files to Reference (Read-Only)
- `apps/Server/app/services/email_service.py` — Reference implementation for messaging service pattern (singleton, mock mode, result DTO, logging)
- `apps/Server/app/services/business_card_service.py` — Integration point: `extract_card()` method and `_get_image_data()` pattern for routing incoming WeChat images
- `apps/Server/app/services/extraction_service.py` — AI extraction service used by business card service
- `apps/Server/app/repository/business_card_repository.py` — Repository pattern for business card captures
- `apps/Server/app/api/supplier_routes.py` — Reference for route pattern (APIRouter, auth dependencies, error handling)
- `apps/Server/app/api/dependencies.py` — `get_current_user` dependency for authenticated endpoints
- `apps/Server/app/api/rbac_dependencies.py` — `require_roles` dependency for role-based access
- `apps/Server/database/schema.sql` — Existing schema with `suppliers.wechat_id` (line 137) and `business_card_captures.contact_wechat` (line 221)
- `apps/Server/tests/services/test_email_service.py` — Reference for test structure (mock settings fixture, mock/real mode tests, error handling tests)
- `apps/Server/requirements.txt` — Current dependencies (already has `pillow`, `qrcode[pil]`, `httpx`)

### New Files
- `apps/Server/app/services/wechat_service.py` — WeChat integration service (webhook verification, incoming message handling, outgoing messaging, QR decode, mock mode)
- `apps/Server/app/api/wechat_routes.py` — WeChat API routes (webhook GET/POST, send message, status)
- `apps/Server/tests/services/test_wechat_service.py` — Unit tests for WeChat service
- `apps/Server/tests/api/test_wechat_routes.py` — Unit tests for WeChat routes

## Implementation Plan
### Phase 1: Foundation
Add WeChat configuration settings and DTOs to establish the data contracts and configuration needed by the service layer. This includes WECHAT_APP_ID, WECHAT_APP_SECRET, WECHAT_VERIFY_TOKEN, and WECHAT_MOCK_MODE settings, plus WeChatMessageDTO, WeChatStatusDTO, and WeChatSendResultDTO Pydantic models.

### Phase 2: Core Implementation
Build the WeChatService class following the EmailService singleton + mock mode pattern. Implement webhook signature verification using SHA1 (WeChat's standard), incoming XML message parsing, image message routing to the business card extraction pipeline, outgoing text message sending via the WeChat Official Account API, supplier introduction message templating, QR code decoding from images using pyzbar/pillow, and phone-to-WeChat resolution (limited, returns None with a log).

### Phase 3: Integration
Create the wechat_routes.py API router with webhook GET (verification) and POST (incoming messages) endpoints that are unauthenticated (required by WeChat), plus authenticated endpoints for sending messages and checking configuration status. Register the router in main.py. Write comprehensive unit tests following the test_email_service.py pattern.

## Step by Step Tasks

### Step 1: Add WeChat Settings to Configuration
- Read `apps/Server/app/config/settings.py`
- Add the following settings after the SMTP Email section (after line 42):
  - `WECHAT_APP_ID: str = ""` — WeChat Official Account App ID
  - `WECHAT_APP_SECRET: str = ""` — WeChat Official Account App Secret
  - `WECHAT_VERIFY_TOKEN: str = ""` — Token for webhook verification
  - `WECHAT_MOCK_MODE: bool = True` — When True, logs instead of calling WeChat API

### Step 2: Add WeChat DTOs to kompass_dto.py
- Read `apps/Server/app/models/kompass_dto.py`
- Add a new `# WECHAT DTOs` section before the `# BULK OPERATION DTOs` section (before line 1554)
- Add the following DTOs:

```python
class WeChatMessageDTO(BaseModel):
    """Request DTO for sending a WeChat message to a supplier."""
    supplier_id: UUID
    message_type: str = Field(default="introduction", description="Type: introduction, follow_up, or custom")
    custom_content: Optional[str] = Field(default=None, max_length=2000)

class WeChatStatusDTO(BaseModel):
    """Response DTO for WeChat configuration status."""
    enabled: bool
    configured: bool
    app_id_set: bool
    webhook_url: str
    mock_mode: bool = Field(default=True)

class WeChatSendResultDTO(BaseModel):
    """Result DTO for WeChat message send operations."""
    success: bool
    message: str
    sent_at: Optional[datetime] = None
    recipient_wechat_id: str = ""
    mock_mode: bool = Field(default=False, description="Whether message was sent in mock mode")
```

### Step 3: Add pyzbar Dependency for QR Code Decoding
- Add `pyzbar>=0.1.9` to `apps/Server/requirements.txt` after the `qrcode[pil]` line
- This library decodes QR codes from images (complementary to qrcode which generates them)
- Note: pyzbar requires the system library `libzbar0` — add a note in the Notes section

### Step 4: Create WeChat Service
- Create `apps/Server/app/services/wechat_service.py`
- Read `apps/Server/app/services/email_service.py` for the singleton + mock mode pattern
- Read `apps/Server/app/services/business_card_service.py` for the extraction integration pattern
- Implement the `WeChatService` class with the following methods:

**`__init__(self)`**:
  - Load settings via `get_settings()`
  - Set `self.app_id`, `self.app_secret`, `self.verify_token`, `self.mock_mode`
  - Set `self.enabled = bool(self.app_id and self.app_secret)`
  - Set `self.access_token = None` and `self.token_expires_at = 0` for caching
  - Log initialization state

**`verify_webhook(self, signature: str, timestamp: str, nonce: str, echostr: str) -> str`**:
  - Implements WeChat's webhook verification protocol
  - Sort `[self.verify_token, timestamp, nonce]` alphabetically
  - Join and compute SHA1 hash
  - Compare with signature
  - Return echostr if valid, raise ValueError if not
  - This works even in mock mode (needed for setup)

**`_get_access_token(self) -> str`**:
  - If mock mode, return "mock-access-token"
  - Check if cached token is still valid (self.token_expires_at > time.time())
  - If expired, call WeChat API: GET `https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}`
  - Cache the token and expires_in
  - Return access_token string
  - Use httpx for HTTP calls

**`handle_incoming_message(self, message_xml: str) -> Optional[str]`**:
  - Parse incoming XML using `xml.etree.ElementTree`
  - Extract MsgType, FromUserName, ToUserName, Content/PicUrl/MediaId
  - If MsgType is "image":
    - Log receipt of image message
    - If not mock mode, download the image via media URL
    - Route to business card extraction: call `business_card_service.create_capture(image_url=pic_url, notes=f"Received via WeChat from {from_user}")`
    - Return XML reply: "Thank you! We received your business card and are processing it."
  - If MsgType is "text":
    - Log the text message
    - Return XML reply: "Thank you for your message. Our team will follow up shortly."
  - For other types, return a generic acknowledgment
  - XML reply format: `<xml><ToUserName>...</ToUserName><FromUserName>...</FromUserName><CreateTime>...</CreateTime><MsgType>text</MsgType><Content>...</Content></xml>`

**`send_message(self, wechat_id: str, content: str) -> WeChatSendResultDTO`**:
  - If not wechat_id, return failure result
  - If mock mode, log and return success with mock_mode=True
  - Get access token via `_get_access_token()`
  - POST to `https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={token}`
  - Body: `{"touser": wechat_id, "msgtype": "text", "text": {"content": content}}`
  - Return WeChatSendResultDTO with success/failure
  - Handle httpx errors gracefully

**`send_supplier_introduction(self, wechat_id: str, supplier_name: str, fair_name: str, sender_name: str = "Rubén") -> WeChatSendResultDTO`**:
  - Render introduction message text (plain text version, adapted from email template)
  - Call `self.send_message(wechat_id, message_text)`
  - Log the operation

**`_render_introduction_message(self, supplier_name: str, fair_name: str, sender_name: str = "Rubén") -> str`**:
  - Return plain text version of the trade fair introduction (similar to EmailService's plain_body)
  - Include: greeting, pleasure meeting at fair, Kompass intro, collaboration interest, sign-off

**`resolve_phone_to_wechat(self, phone: str) -> Optional[str]`**:
  - Log that this operation is not supported by the WeChat Official Account API
  - Return None
  - Note: WeChat does not provide a public API for phone-to-WeChat resolution

**`decode_qr_from_image(self, image_data: bytes) -> Optional[str]`**:
  - Use pyzbar to decode QR codes from the image bytes
  - Convert image_data to PIL Image
  - Call `pyzbar.decode(image)` to find all barcodes/QR codes
  - Filter for QR type results
  - Return the first decoded data string, or None if no QR found
  - Handle import errors gracefully (pyzbar may not be installed)
  - Log results

- Export singleton: `wechat_service = WeChatService()`

### Step 5: Create WeChat Routes
- Create `apps/Server/app/api/wechat_routes.py`
- Read `apps/Server/app/api/supplier_routes.py` for route patterns
- Implement the router with `APIRouter(tags=["WeChat"])`

**`GET /webhook`** (unauthenticated — required by WeChat):
  - Query params: signature, timestamp, nonce, echostr (all strings)
  - Call `wechat_service.verify_webhook(...)`
  - Return PlainTextResponse with echostr on success
  - Return 403 on verification failure

**`POST /webhook`** (unauthenticated — required by WeChat):
  - Receive raw XML body via `Request.body()`
  - Call `wechat_service.handle_incoming_message(body_xml)`
  - Return XML response with content-type `application/xml`
  - Return empty "success" string if no reply needed

**`POST /send/{supplier_id}`** (authenticated, admin/manager):
  - Depends on `get_current_user` and `require_roles(['admin', 'manager'])`
  - Accept `WeChatMessageDTO` body
  - Look up supplier by ID to get wechat_id (import supplier_service or use repository)
  - If supplier has no wechat_id, return 400 error
  - Based on message_type:
    - "introduction": call `wechat_service.send_supplier_introduction(wechat_id, supplier_name, fair_name)`
    - "custom": call `wechat_service.send_message(wechat_id, custom_content)`
  - Return WeChatSendResultDTO

**`GET /status`** (authenticated):
  - Depends on `get_current_user`
  - Return WeChatStatusDTO with configuration status
  - webhook_url: provide the expected webhook URL pattern

### Step 6: Register WeChat Router in main.py
- Read `apps/Server/main.py`
- Add import: `from app.api.wechat_routes import router as wechat_router`
- Add router registration: `app.include_router(wechat_router, prefix="/api/wechat")` after the user_router line

### Step 7: Write Unit Tests for WeChat Service
- Create `apps/Server/tests/services/test_wechat_service.py`
- Read `apps/Server/tests/services/test_email_service.py` for the test structure pattern
- Implement tests following the same mock_settings fixture pattern:

**TestWeChatServiceInit**:
  - `test_init_loads_settings` — Verify settings are loaded correctly
  - `test_init_mock_mode` — Verify mock mode is set
  - `test_init_enabled_when_credentials_set` — Verify enabled flag
  - `test_init_disabled_when_no_credentials` — Verify disabled when APP_ID or SECRET empty

**TestVerifyWebhook**:
  - `test_verify_webhook_valid_signature` — Compute correct SHA1, verify echostr returned
  - `test_verify_webhook_invalid_signature` — Verify ValueError raised
  - `test_verify_webhook_empty_params` — Verify error handling

**TestHandleIncomingMessage**:
  - `test_handle_image_message` — Verify image message triggers capture creation (mock business_card_service)
  - `test_handle_text_message` — Verify text message returns acknowledgment
  - `test_handle_unknown_message_type` — Verify generic response
  - `test_handle_invalid_xml` — Verify error handling for malformed XML

**TestSendMessageMockMode**:
  - `test_send_message_mock_returns_success` — Verify mock mode returns success
  - `test_send_message_empty_wechat_id` — Verify failure for empty ID
  - `test_send_message_mock_logs_content` — Verify content is logged

**TestSendMessageRealMode**:
  - `test_send_message_real_mode` — Mock httpx, verify API call
  - `test_send_message_api_error` — Mock httpx error, verify failure result

**TestSendSupplierIntroduction**:
  - `test_introduction_message_content` — Verify template includes supplier name and fair name
  - `test_introduction_calls_send_message` — Verify delegation to send_message
  - `test_introduction_non_ascii` — Verify Chinese characters work

**TestDecodeQrFromImage**:
  - `test_decode_qr_success` — Mock pyzbar, verify decoded data returned
  - `test_decode_qr_no_qr_found` — Mock pyzbar returning empty, verify None
  - `test_decode_qr_import_error` — Verify graceful handling when pyzbar not installed

**TestResolvePhoneToWechat**:
  - `test_resolve_phone_returns_none` — Verify always returns None (API limitation)

### Step 8: Write Unit Tests for WeChat Routes
- Create `apps/Server/tests/api/test_wechat_routes.py`
- Read `apps/Server/tests/api/test_supplier_routes.py` for route test patterns
- Use FastAPI TestClient with mocked wechat_service and auth dependencies

**TestWebhookVerification**:
  - `test_webhook_get_valid` — Verify returns echostr
  - `test_webhook_get_invalid` — Verify returns 403

**TestWebhookIncoming**:
  - `test_webhook_post_image_message` — Verify XML response
  - `test_webhook_post_text_message` — Verify XML response

**TestSendMessage**:
  - `test_send_introduction_success` — Verify 200 with result DTO
  - `test_send_no_wechat_id` — Verify 400 when supplier has no wechat_id
  - `test_send_unauthorized` — Verify 401 without auth
  - `test_send_forbidden_for_viewer` — Verify 403 for viewer role

**TestStatus**:
  - `test_status_returns_config` — Verify configuration status response
  - `test_status_requires_auth` — Verify 401 without auth

### Step 9: Run Validation Commands
- Run `cd apps/Server && python -m pytest tests/ -v --tb=short` to validate all tests pass
- Run `cd apps/Server && python -m ruff check .` to validate linting passes

## Testing Strategy
### Unit Tests
- **WeChat Service tests** (`tests/services/test_wechat_service.py`): Test all service methods with mocked settings, mocked httpx for API calls, mocked pyzbar for QR decoding, and mocked business_card_service for extraction routing. Cover both mock mode and real mode paths.
- **WeChat Route tests** (`tests/api/test_wechat_routes.py`): Test all endpoints using FastAPI TestClient with mocked service layer and auth dependencies. Verify auth requirements, role restrictions, and response formats.

### Edge Cases
- Empty or None wechat_id when sending messages
- Malformed XML in incoming webhook messages
- WeChat API returning error responses (invalid token, rate limited, user not following)
- Non-ASCII characters in messages (Chinese supplier names, fair names)
- QR code image with no QR codes detected
- QR code image with multiple QR codes (return first)
- pyzbar library not installed (graceful import error handling)
- Expired access token requiring refresh
- Invalid webhook signature (replay attack protection)
- Supplier not found when sending via supplier_id
- Supplier found but missing wechat_id field

## Acceptance Criteria
- WeChat webhook verification endpoint (GET /api/wechat/webhook) correctly validates SHA1 signatures and returns echostr
- WeChat incoming message endpoint (POST /api/wechat/webhook) parses image messages and routes them to business card extraction pipeline
- WeChat incoming message endpoint handles text messages with acknowledgment replies
- Send message endpoint (POST /api/wechat/send/{supplier_id}) sends introduction messages to suppliers with wechat_id
- Send message endpoint returns 400 when supplier has no wechat_id
- Send message endpoint requires admin or manager role
- Status endpoint (GET /api/wechat/status) returns configuration status
- Mock mode works for all operations when WECHAT_MOCK_MODE=True or credentials not set
- QR code decoding extracts WeChat IDs/URLs from business card images
- All existing tests continue to pass (zero regressions)
- Ruff linting passes with no errors
- WeChatSendResultDTO follows the same pattern as EmailSendResultDTO

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/services/test_wechat_service.py -v --tb=short` — Run WeChat service unit tests
- `cd apps/Server && python -m pytest tests/api/test_wechat_routes.py -v --tb=short` — Run WeChat route unit tests
- `cd apps/Server && python -m pytest tests/ -v --tb=short` — Run all Server tests to validate zero regressions
- `cd apps/Server && python -m ruff check .` — Run linting to validate code quality

## Notes
- **pyzbar system dependency**: The `pyzbar` Python package requires the `libzbar0` system library. Install via `sudo apt-get install libzbar0` on Ubuntu/Debian. If not available, QR decoding will gracefully degrade (returns None with a warning log).
- **WeChat Official Account verification**: WeChat requires business verification which can take weeks. The mock mode ensures the system is fully functional during this period. Users can preview generated messages in the status/send response and manually copy-paste them into WeChat.
- **WeChat API limitations**: The Official Account API only allows messaging users who have followed the account and sent a message within the last 48 hours. The `resolve_phone_to_wechat` method returns None because WeChat does not expose a phone-to-ID lookup API.
- **No new pip dependency needed for XML parsing**: Python's built-in `xml.etree.ElementTree` is sufficient for parsing WeChat's XML messages.
- **Webhook endpoints are unauthenticated**: The GET and POST `/api/wechat/webhook` endpoints must be unauthenticated because WeChat's servers call them directly. All other endpoints require JWT authentication.
- **Parallel execution**: This feature runs in parallel with TF-005 (Review UI) and TF-006 (Dashboard). No file conflicts expected since this creates new files and only modifies shared files (main.py, settings.py, kompass_dto.py) with additive changes.
- **Wave 4 dependency**: TF-008 (follow-up message templates) will extend this service with a `send_follow_up` method and "follow_up" message_type support.
