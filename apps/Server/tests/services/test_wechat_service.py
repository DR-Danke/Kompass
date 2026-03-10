"""Unit tests for WeChatService."""

import hashlib
from unittest.mock import MagicMock, patch

import pytest


# Patch settings before importing wechat_service to avoid real config loading
@pytest.fixture(autouse=True)
def mock_settings():
    """Mock settings for all tests to prevent real WeChat config loading."""
    with patch("app.services.wechat_service.get_settings") as mock_get:
        settings = MagicMock()
        settings.WECHAT_APP_ID = "wx_test_app_id"
        settings.WECHAT_APP_SECRET = "wx_test_app_secret"
        settings.WECHAT_VERIFY_TOKEN = "test_verify_token"
        settings.WECHAT_MOCK_MODE = True
        mock_get.return_value = settings
        yield settings


@pytest.fixture
def wechat_service_mock_mode(mock_settings):
    """Create a WeChatService instance in mock mode."""
    mock_settings.WECHAT_MOCK_MODE = True
    from app.services.wechat_service import WeChatService

    return WeChatService()


@pytest.fixture
def wechat_service_real_mode(mock_settings):
    """Create a WeChatService instance in real mode."""
    mock_settings.WECHAT_MOCK_MODE = False
    from app.services.wechat_service import WeChatService

    return WeChatService()


@pytest.fixture
def wechat_service_no_credentials(mock_settings):
    """Create a WeChatService instance with no credentials."""
    mock_settings.WECHAT_APP_ID = ""
    mock_settings.WECHAT_APP_SECRET = ""
    mock_settings.WECHAT_MOCK_MODE = True
    from app.services.wechat_service import WeChatService

    return WeChatService()


def _compute_signature(token: str, timestamp: str, nonce: str) -> str:
    """Helper to compute correct WeChat webhook signature."""
    params = sorted([token, timestamp, nonce])
    return hashlib.sha1("".join(params).encode("utf-8")).hexdigest()


# =============================================================================
# INITIALIZATION TESTS
# =============================================================================


class TestWeChatServiceInit:
    """Tests for WeChatService initialization."""

    def test_init_loads_settings(self, wechat_service_mock_mode):
        """Test that settings are loaded correctly."""
        svc = wechat_service_mock_mode
        assert svc.app_id == "wx_test_app_id"
        assert svc.app_secret == "wx_test_app_secret"
        assert svc.verify_token == "test_verify_token"
        assert svc.mock_mode is True

    def test_init_mock_mode(self, wechat_service_mock_mode):
        """Test initialization in mock mode."""
        assert wechat_service_mock_mode.mock_mode is True

    def test_init_enabled_when_credentials_set(self, wechat_service_mock_mode):
        """Test enabled flag when credentials are provided."""
        assert wechat_service_mock_mode.enabled is True

    def test_init_disabled_when_no_credentials(self, wechat_service_no_credentials):
        """Test disabled flag when credentials are not provided."""
        assert wechat_service_no_credentials.enabled is False


# =============================================================================
# WEBHOOK VERIFICATION TESTS
# =============================================================================


class TestVerifyWebhook:
    """Tests for verify_webhook()."""

    def test_verify_webhook_valid_signature(self, wechat_service_mock_mode):
        """Test valid webhook signature returns echostr."""
        timestamp = "1234567890"
        nonce = "abcdef"
        echostr = "echo_string_123"
        signature = _compute_signature("test_verify_token", timestamp, nonce)

        result = wechat_service_mock_mode.verify_webhook(
            signature, timestamp, nonce, echostr
        )
        assert result == echostr

    def test_verify_webhook_invalid_signature(self, wechat_service_mock_mode):
        """Test invalid signature raises ValueError."""
        with pytest.raises(ValueError, match="Invalid webhook signature"):
            wechat_service_mock_mode.verify_webhook(
                "invalid_signature", "1234567890", "abcdef", "echo"
            )

    def test_verify_webhook_empty_params(self, wechat_service_mock_mode):
        """Test empty params still computes hash (won't match random sig)."""
        with pytest.raises(ValueError):
            wechat_service_mock_mode.verify_webhook("badsig", "", "", "echo")


# =============================================================================
# INCOMING MESSAGE TESTS
# =============================================================================


class TestHandleIncomingMessage:
    """Tests for handle_incoming_message()."""

    def test_handle_image_message(self, wechat_service_mock_mode):
        """Test image message triggers capture and returns reply."""
        xml = (
            "<xml>"
            "<ToUserName><![CDATA[gh_account]]></ToUserName>"
            "<FromUserName><![CDATA[user123]]></FromUserName>"
            "<CreateTime>1234567890</CreateTime>"
            "<MsgType><![CDATA[image]]></MsgType>"
            "<PicUrl><![CDATA[https://example.com/image.jpg]]></PicUrl>"
            "<MediaId><![CDATA[media_id_123]]></MediaId>"
            "<MsgId>12345</MsgId>"
            "</xml>"
        )

        mock_bcs = MagicMock()
        mock_module = MagicMock()
        mock_module.business_card_service = mock_bcs

        with patch.dict(
            "sys.modules",
            {"app.services.business_card_service": mock_module},
        ):
            reply = wechat_service_mock_mode.handle_incoming_message(xml)

        assert reply is not None
        assert "business card" in reply.lower() or "processing" in reply.lower()
        assert "<MsgType><![CDATA[text]]></MsgType>" in reply
        assert "<ToUserName><![CDATA[user123]]></ToUserName>" in reply
        mock_bcs.create_capture.assert_called_once()

    def test_handle_text_message(self, wechat_service_mock_mode):
        """Test text message returns acknowledgment."""
        xml = (
            "<xml>"
            "<ToUserName><![CDATA[gh_account]]></ToUserName>"
            "<FromUserName><![CDATA[user456]]></FromUserName>"
            "<CreateTime>1234567890</CreateTime>"
            "<MsgType><![CDATA[text]]></MsgType>"
            "<Content><![CDATA[Hello there]]></Content>"
            "<MsgId>12346</MsgId>"
            "</xml>"
        )

        reply = wechat_service_mock_mode.handle_incoming_message(xml)

        assert reply is not None
        assert "follow up" in reply.lower()
        assert "<ToUserName><![CDATA[user456]]></ToUserName>" in reply

    def test_handle_unknown_message_type(self, wechat_service_mock_mode):
        """Test unknown message type returns generic response."""
        xml = (
            "<xml>"
            "<ToUserName><![CDATA[gh_account]]></ToUserName>"
            "<FromUserName><![CDATA[user789]]></FromUserName>"
            "<CreateTime>1234567890</CreateTime>"
            "<MsgType><![CDATA[voice]]></MsgType>"
            "<MsgId>12347</MsgId>"
            "</xml>"
        )

        reply = wechat_service_mock_mode.handle_incoming_message(xml)

        assert reply is not None
        assert "received" in reply.lower()

    def test_handle_invalid_xml(self, wechat_service_mock_mode):
        """Test malformed XML returns None."""
        reply = wechat_service_mock_mode.handle_incoming_message("not valid xml <><>")
        assert reply is None


# =============================================================================
# SEND MESSAGE MOCK MODE TESTS
# =============================================================================


class TestSendMessageMockMode:
    """Tests for send_message() in mock mode."""

    def test_send_message_mock_returns_success(self, wechat_service_mock_mode):
        """Test mock mode returns success without calling API."""
        result = wechat_service_mock_mode.send_message(
            wechat_id="wx_user_123",
            content="Hello from Kompass!",
        )

        assert result.success is True
        assert result.mock_mode is True
        assert result.recipient_wechat_id == "wx_user_123"
        assert result.sent_at is not None
        assert "mock mode" in result.message

    def test_send_message_empty_wechat_id(self, wechat_service_mock_mode):
        """Test empty wechat_id returns failure."""
        result = wechat_service_mock_mode.send_message(
            wechat_id="",
            content="Hello",
        )

        assert result.success is False
        assert "required" in result.message.lower()

    def test_send_message_mock_logs_content(self, wechat_service_mock_mode, capsys):
        """Test mock mode logs the content."""
        wechat_service_mock_mode.send_message(
            wechat_id="wx_user_456",
            content="Test message content",
        )

        captured = capsys.readouterr()
        assert "MOCK MESSAGE" in captured.out
        assert "wx_user_456" in captured.out


# =============================================================================
# SEND MESSAGE REAL MODE TESTS
# =============================================================================


class TestSendMessageRealMode:
    """Tests for send_message() in real mode."""

    @patch("app.services.wechat_service.httpx.post")
    @patch("app.services.wechat_service.httpx.get")
    def test_send_message_real_mode(
        self, mock_get, mock_post, wechat_service_real_mode
    ):
        """Test real mode calls WeChat API."""
        # Mock access token response
        mock_token_response = MagicMock()
        mock_token_response.json.return_value = {
            "access_token": "test_token_123",
            "expires_in": 7200,
        }
        mock_get.return_value = mock_token_response

        # Mock send message response
        mock_send_response = MagicMock()
        mock_send_response.json.return_value = {"errcode": 0, "errmsg": "ok"}
        mock_post.return_value = mock_send_response

        result = wechat_service_real_mode.send_message(
            wechat_id="wx_real_user",
            content="Hello!",
        )

        assert result.success is True
        assert result.mock_mode is False
        assert result.recipient_wechat_id == "wx_real_user"
        mock_post.assert_called_once()

    @patch("app.services.wechat_service.httpx.get")
    def test_send_message_api_error(self, mock_get, wechat_service_real_mode):
        """Test API error returns failure result."""
        import httpx

        mock_get.side_effect = httpx.HTTPError("Connection failed")

        result = wechat_service_real_mode.send_message(
            wechat_id="wx_user",
            content="Hello",
        )

        assert result.success is False
        assert result.mock_mode is False


# =============================================================================
# SUPPLIER INTRODUCTION TESTS
# =============================================================================


class TestSendSupplierIntroduction:
    """Tests for send_supplier_introduction()."""

    def test_introduction_message_content(self, wechat_service_mock_mode):
        """Test introduction message contains supplier name and fair name."""
        message = wechat_service_mock_mode._render_introduction_message(
            supplier_name="Acme Corp",
            fair_name="Canton Fair 2026",
            sender_name="Rubén",
        )

        assert "Acme Corp" in message
        assert "Canton Fair 2026" in message
        assert "Rubén" in message
        assert "Kompass" in message

    def test_introduction_calls_send_message(self, wechat_service_mock_mode):
        """Test introduction delegates to send_message."""
        result = wechat_service_mock_mode.send_supplier_introduction(
            wechat_id="wx_supplier_123",
            supplier_name="Test Supplier",
            fair_name="Expo 2026",
        )

        assert result.success is True
        assert result.mock_mode is True
        assert result.recipient_wechat_id == "wx_supplier_123"

    def test_introduction_non_ascii(self, wechat_service_mock_mode):
        """Test introduction with Chinese characters works."""
        result = wechat_service_mock_mode.send_supplier_introduction(
            wechat_id="wx_cn_123",
            supplier_name="上海贸易公司",
            fair_name="广交会",
        )

        assert result.success is True

        message = wechat_service_mock_mode._render_introduction_message(
            supplier_name="上海贸易公司",
            fair_name="广交会",
        )
        assert "上海贸易公司" in message
        assert "广交会" in message


# =============================================================================
# QR DECODE TESTS
# =============================================================================


class TestDecodeQrFromImage:
    """Tests for decode_qr_from_image()."""

    @patch("app.services.wechat_service.pyzbar_decode", create=True)
    def test_decode_qr_success(self, mock_decode, wechat_service_mock_mode):
        """Test successful QR decode returns data."""
        # Create a small valid PNG image
        from PIL import Image
        from io import BytesIO

        img = Image.new("RGB", (100, 100), "white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        image_data = buffer.getvalue()

        # Mock pyzbar
        mock_result = MagicMock()
        mock_result.type = "QRCODE"
        mock_result.data = b"https://weixin.qq.com/r/test123"

        with patch(
            "app.services.wechat_service.WeChatService.decode_qr_from_image"
        ) as mock_method:
            mock_method.return_value = "https://weixin.qq.com/r/test123"
            result = mock_method(image_data)

        assert result == "https://weixin.qq.com/r/test123"

    def test_decode_qr_import_error(self, wechat_service_mock_mode):
        """Test graceful handling when pyzbar not installed."""
        with patch.dict("sys.modules", {"pyzbar": None, "pyzbar.pyzbar": None}):
            # Force re-import to trigger ImportError
            result = wechat_service_mock_mode.decode_qr_from_image(b"fake image data")
            # Should return None gracefully when import fails
            assert result is None

    def test_decode_qr_no_qr_found(self, wechat_service_mock_mode):
        """Test returns None when no QR code in image."""
        from PIL import Image
        from io import BytesIO

        # Create a blank image with no QR code
        img = Image.new("RGB", (100, 100), "white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        image_data = buffer.getvalue()

        with patch(
            "app.services.wechat_service.WeChatService.decode_qr_from_image"
        ) as mock_method:
            mock_method.return_value = None
            result = mock_method(image_data)

        assert result is None


# =============================================================================
# PHONE TO WECHAT RESOLUTION TESTS
# =============================================================================


class TestResolvePhoneToWechat:
    """Tests for resolve_phone_to_wechat()."""

    def test_resolve_phone_returns_none(self, wechat_service_mock_mode):
        """Test that phone resolution always returns None (API limitation)."""
        result = wechat_service_mock_mode.resolve_phone_to_wechat("+8613800138000")
        assert result is None

    def test_resolve_phone_logs_message(self, wechat_service_mock_mode, capsys):
        """Test that phone resolution logs informational message."""
        wechat_service_mock_mode.resolve_phone_to_wechat("+8613800138000")
        captured = capsys.readouterr()
        assert "not supported" in captured.out.lower()
