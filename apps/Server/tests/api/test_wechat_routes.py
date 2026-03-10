"""Unit tests for WeChat API routes."""

import hashlib
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def mock_wechat_settings():
    """Mock settings to prevent real config loading during import."""
    with patch("app.services.wechat_service.get_settings") as mock_get:
        settings = MagicMock()
        settings.WECHAT_APP_ID = "wx_test_id"
        settings.WECHAT_APP_SECRET = "wx_test_secret"
        settings.WECHAT_VERIFY_TOKEN = "test_token"
        settings.WECHAT_MOCK_MODE = True
        mock_get.return_value = settings
        yield settings


@pytest.fixture
def mock_auth():
    """Mock authentication dependency."""
    return {"id": "test-user-id", "email": "admin@test.com", "role": "admin"}


@pytest.fixture
def client(mock_auth):
    """Create test client with mocked auth."""
    from app.api.dependencies import get_current_user
    from main import app

    def override_auth():
        return mock_auth

    def override_roles(roles):
        def dependency():
            return mock_auth

        return dependency

    app.dependency_overrides[get_current_user] = override_auth

    with patch(
        "app.api.wechat_routes.require_roles",
        side_effect=lambda roles: override_auth,
    ):
        yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture
def unauth_client():
    """Create test client without auth overrides."""
    from main import app

    app.dependency_overrides.clear()
    yield TestClient(app)
    app.dependency_overrides.clear()


def _compute_signature(token: str, timestamp: str, nonce: str) -> str:
    """Compute valid WeChat webhook signature."""
    params = sorted([token, timestamp, nonce])
    return hashlib.sha1("".join(params).encode("utf-8")).hexdigest()


# =============================================================================
# WEBHOOK VERIFICATION TESTS
# =============================================================================


class TestWebhookVerification:
    """Tests for GET /api/wechat/webhook."""

    def test_webhook_get_valid(self, client):
        """Test valid webhook verification returns echostr."""
        timestamp = "1234567890"
        nonce = "test_nonce"
        echostr = "echo_123"
        signature = _compute_signature("test_token", timestamp, nonce)

        with patch(
            "app.api.wechat_routes.wechat_service.verify_webhook",
            return_value=echostr,
        ):
            response = client.get(
                "/api/wechat/webhook",
                params={
                    "signature": signature,
                    "timestamp": timestamp,
                    "nonce": nonce,
                    "echostr": echostr,
                },
            )

        assert response.status_code == 200
        assert response.text == echostr

    def test_webhook_get_invalid(self, client):
        """Test invalid webhook verification returns 403."""
        with patch(
            "app.api.wechat_routes.wechat_service.verify_webhook",
            side_effect=ValueError("Invalid signature"),
        ):
            response = client.get(
                "/api/wechat/webhook",
                params={
                    "signature": "bad_sig",
                    "timestamp": "123",
                    "nonce": "abc",
                    "echostr": "echo",
                },
            )

        assert response.status_code == 403


# =============================================================================
# WEBHOOK INCOMING MESSAGE TESTS
# =============================================================================


class TestWebhookIncoming:
    """Tests for POST /api/wechat/webhook."""

    def test_webhook_post_image_message(self, client):
        """Test incoming image message returns XML response."""
        xml_body = (
            "<xml>"
            "<ToUserName><![CDATA[gh_test]]></ToUserName>"
            "<FromUserName><![CDATA[user123]]></FromUserName>"
            "<CreateTime>1234567890</CreateTime>"
            "<MsgType><![CDATA[image]]></MsgType>"
            "<PicUrl><![CDATA[https://example.com/img.jpg]]></PicUrl>"
            "<MediaId><![CDATA[media123]]></MediaId>"
            "<MsgId>111</MsgId>"
            "</xml>"
        )

        reply_xml = (
            "<xml>"
            "<ToUserName><![CDATA[user123]]></ToUserName>"
            "<FromUserName><![CDATA[gh_test]]></FromUserName>"
            "<CreateTime>1234567890</CreateTime>"
            "<MsgType><![CDATA[text]]></MsgType>"
            "<Content><![CDATA[Thank you!]]></Content>"
            "</xml>"
        )

        with patch(
            "app.api.wechat_routes.wechat_service.handle_incoming_message",
            return_value=reply_xml,
        ):
            response = client.post(
                "/api/wechat/webhook",
                content=xml_body,
                headers={"Content-Type": "application/xml"},
            )

        assert response.status_code == 200
        assert "application/xml" in response.headers["content-type"]

    def test_webhook_post_text_message(self, client):
        """Test incoming text message returns XML response."""
        xml_body = (
            "<xml>"
            "<ToUserName><![CDATA[gh_test]]></ToUserName>"
            "<FromUserName><![CDATA[user456]]></FromUserName>"
            "<CreateTime>1234567890</CreateTime>"
            "<MsgType><![CDATA[text]]></MsgType>"
            "<Content><![CDATA[Hello]]></Content>"
            "<MsgId>222</MsgId>"
            "</xml>"
        )

        reply_xml = (
            "<xml>"
            "<ToUserName><![CDATA[user456]]></ToUserName>"
            "<Content><![CDATA[Thanks]]></Content>"
            "</xml>"
        )

        with patch(
            "app.api.wechat_routes.wechat_service.handle_incoming_message",
            return_value=reply_xml,
        ):
            response = client.post(
                "/api/wechat/webhook",
                content=xml_body,
            )

        assert response.status_code == 200


# =============================================================================
# SEND MESSAGE TESTS
# =============================================================================


class TestSendMessage:
    """Tests for POST /api/wechat/send/{supplier_id}."""

    def test_send_introduction_success(self, client):
        """Test sending introduction message returns success."""
        from app.models.kompass_dto import WeChatSendResultDTO

        supplier_id = "00000000-0000-0000-0000-000000000001"
        mock_supplier = MagicMock()
        mock_supplier.name = "Test Supplier"

        mock_result = WeChatSendResultDTO(
            success=True,
            message="Message sent (mock mode)",
            recipient_wechat_id="wx_123",
            mock_mode=True,
        )

        with patch(
            "app.api.wechat_routes.supplier_service.get_supplier",
            return_value=mock_supplier,
        ), patch(
            "app.api.wechat_routes.get_database_connection"
        ) as mock_conn_fn, patch(
            "app.api.wechat_routes.close_database_connection"
        ), patch(
            "app.api.wechat_routes.wechat_service.send_supplier_introduction",
            return_value=mock_result,
        ):
            # Mock DB connection for wechat_id lookup
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = ("wx_123",)
            mock_conn.cursor.return_value.__enter__ = MagicMock(
                return_value=mock_cursor
            )
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_conn_fn.return_value = mock_conn

            response = client.post(
                f"/api/wechat/send/{supplier_id}",
                json={
                    "supplier_id": supplier_id,
                    "message_type": "introduction",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_send_no_wechat_id(self, client):
        """Test sending to supplier without wechat_id returns 400."""
        supplier_id = "00000000-0000-0000-0000-000000000002"
        mock_supplier = MagicMock()
        mock_supplier.name = "No WeChat Supplier"

        with patch(
            "app.api.wechat_routes.supplier_service.get_supplier",
            return_value=mock_supplier,
        ), patch(
            "app.api.wechat_routes.get_database_connection"
        ) as mock_conn_fn, patch(
            "app.api.wechat_routes.close_database_connection"
        ):
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = (None,)
            mock_conn.cursor.return_value.__enter__ = MagicMock(
                return_value=mock_cursor
            )
            mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_conn_fn.return_value = mock_conn

            response = client.post(
                f"/api/wechat/send/{supplier_id}",
                json={
                    "supplier_id": supplier_id,
                    "message_type": "introduction",
                },
            )

        assert response.status_code == 400
        assert "WeChat ID" in response.json()["detail"]


# =============================================================================
# STATUS TESTS
# =============================================================================


class TestStatus:
    """Tests for GET /api/wechat/status."""

    def test_status_returns_config(self, client):
        """Test status endpoint returns configuration."""
        with patch.object(
            __import__("app.api.wechat_routes", fromlist=["wechat_service"]).wechat_service,
            "enabled",
            True,
        ), patch.object(
            __import__("app.api.wechat_routes", fromlist=["wechat_service"]).wechat_service,
            "mock_mode",
            True,
        ), patch.object(
            __import__("app.api.wechat_routes", fromlist=["wechat_service"]).wechat_service,
            "app_id",
            "wx_test",
        ), patch.object(
            __import__("app.api.wechat_routes", fromlist=["wechat_service"]).wechat_service,
            "app_secret",
            "secret",
        ):
            response = client.get("/api/wechat/status")

        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "mock_mode" in data
        assert "webhook_url" in data
