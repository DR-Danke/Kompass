"""Unit tests for EmailService."""

from datetime import datetime
from unittest.mock import MagicMock, patch, call
from uuid import uuid4

import pytest


# Patch settings before importing email_service to avoid real config loading
@pytest.fixture(autouse=True)
def mock_settings():
    """Mock settings for all tests to prevent real SMTP config loading."""
    with patch("app.services.email_service.get_settings") as mock_get:
        settings = MagicMock()
        settings.SMTP_HOST = "smtp.test.com"
        settings.SMTP_PORT = 587
        settings.SMTP_USER = "user@test.com"
        settings.SMTP_PASSWORD = "testpassword"
        settings.FROM_EMAIL = "noreply@test.com"
        settings.FROM_NAME = "TestApp"
        settings.EMAIL_MOCK_MODE = True
        mock_get.return_value = settings
        yield settings


@pytest.fixture
def email_service_mock_mode(mock_settings):
    """Create an EmailService instance in mock mode."""
    mock_settings.EMAIL_MOCK_MODE = True
    from app.services.email_service import EmailService

    return EmailService()


@pytest.fixture
def email_service_real_mode(mock_settings):
    """Create an EmailService instance in real mode."""
    mock_settings.EMAIL_MOCK_MODE = False
    from app.services.email_service import EmailService

    return EmailService()


# =============================================================================
# INITIALIZATION TESTS
# =============================================================================


class TestEmailServiceInit:
    """Tests for EmailService initialization."""

    def test_init_loads_settings(self, email_service_mock_mode):
        """Test that settings are loaded correctly."""
        svc = email_service_mock_mode
        assert svc.smtp_host == "smtp.test.com"
        assert svc.smtp_port == 587
        assert svc.smtp_user == "user@test.com"
        assert svc.smtp_password == "testpassword"
        assert svc.from_email == "noreply@test.com"
        assert svc.from_name == "TestApp"
        assert svc.mock_mode is True

    def test_init_real_mode(self, email_service_real_mode):
        """Test initialization in real mode."""
        assert email_service_real_mode.mock_mode is False


# =============================================================================
# MOCK MODE TESTS
# =============================================================================


class TestSendEmailMockMode:
    """Tests for send_email() in mock mode."""

    def test_send_email_mock_mode_returns_success(self, email_service_mock_mode):
        """Test that mock mode returns success without sending."""
        result = email_service_mock_mode.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            html_body="<p>Hello</p>",
        )

        assert result.success is True
        assert result.mock_mode is True
        assert result.recipient_email == "recipient@example.com"
        assert result.sent_at is not None
        assert "mock mode" in result.message

    def test_send_email_mock_mode_with_attachments(self, email_service_mock_mode):
        """Test mock mode with attachments logs attachment info."""
        attachments = [{"filename": "test.pdf", "data": b"fake pdf content"}]

        result = email_service_mock_mode.send_email(
            to_email="recipient@example.com",
            subject="Test",
            html_body="<p>Test</p>",
            attachments=attachments,
        )

        assert result.success is True
        assert result.mock_mode is True

    def test_send_email_empty_recipient(self, email_service_mock_mode):
        """Test that empty recipient returns failure."""
        result = email_service_mock_mode.send_email(
            to_email="",
            subject="Test",
            html_body="<p>Test</p>",
        )

        assert result.success is False
        assert "required" in result.message.lower()

    def test_send_email_none_recipient(self, email_service_mock_mode):
        """Test that None recipient returns failure."""
        result = email_service_mock_mode.send_email(
            to_email=None,
            subject="Test",
            html_body="<p>Test</p>",
        )

        assert result.success is False


# =============================================================================
# REAL MODE TESTS
# =============================================================================


class TestSendEmailRealMode:
    """Tests for send_email() in real SMTP mode."""

    @patch("app.services.email_service.smtplib.SMTP")
    def test_send_email_real_mode(self, mock_smtp_class, email_service_real_mode):
        """Test real SMTP sending calls correct methods."""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        result = email_service_real_mode.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            html_body="<p>Hello</p>",
            plain_body="Hello",
        )

        assert result.success is True
        assert result.mock_mode is False
        assert result.recipient_email == "recipient@example.com"
        assert result.sent_at is not None

        # Verify SMTP connection
        mock_smtp_class.assert_called_once_with("smtp.test.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user@test.com", "testpassword")
        mock_server.sendmail.assert_called_once()

        # Verify sendmail args
        send_args = mock_server.sendmail.call_args
        assert send_args[0][0] == "noreply@test.com"
        assert send_args[0][1] == "recipient@example.com"

    @patch("app.services.email_service.smtplib.SMTP")
    def test_send_email_with_reply_to(self, mock_smtp_class, email_service_real_mode):
        """Test that reply-to header is included."""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        result = email_service_real_mode.send_email(
            to_email="recipient@example.com",
            subject="Test",
            html_body="<p>Test</p>",
            reply_to="reply@example.com",
        )

        assert result.success is True
        # Check Reply-To in the sent message
        sent_msg = mock_server.sendmail.call_args[0][2]
        assert "Reply-To: reply@example.com" in sent_msg


# =============================================================================
# ATTACHMENT TESTS
# =============================================================================


class TestSendEmailWithAttachments:
    """Tests for attachment handling."""

    @patch("app.services.email_service.smtplib.SMTP")
    def test_send_email_with_pdf_attachment(self, mock_smtp_class, email_service_real_mode):
        """Test that PDF attachment is properly encoded and attached."""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        pdf_data = b"%PDF-1.4 fake pdf content here"
        attachments = [{"filename": "quotation.pdf", "data": pdf_data}]

        result = email_service_real_mode.send_email(
            to_email="recipient@example.com",
            subject="Your Quotation",
            html_body="<p>Attached</p>",
            attachments=attachments,
        )

        assert result.success is True
        # Verify the message contains the attachment filename
        sent_msg = mock_server.sendmail.call_args[0][2]
        assert "quotation.pdf" in sent_msg

    @patch("app.services.email_service.smtplib.SMTP")
    def test_send_email_with_multiple_attachments(self, mock_smtp_class, email_service_real_mode):
        """Test multiple attachments."""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        attachments = [
            {"filename": "doc1.pdf", "data": b"pdf1"},
            {"filename": "doc2.pdf", "data": b"pdf2"},
        ]

        result = email_service_real_mode.send_email(
            to_email="recipient@example.com",
            subject="Test",
            html_body="<p>Test</p>",
            attachments=attachments,
        )

        assert result.success is True
        sent_msg = mock_server.sendmail.call_args[0][2]
        assert "doc1.pdf" in sent_msg
        assert "doc2.pdf" in sent_msg


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


class TestSendEmailErrorHandling:
    """Tests for SMTP error handling."""

    @patch("app.services.email_service.smtplib.SMTP")
    def test_smtp_auth_error(self, mock_smtp_class, email_service_real_mode):
        """Test SMTP authentication error returns failure."""
        import smtplib

        mock_server = MagicMock()
        mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Auth failed")
        mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        result = email_service_real_mode.send_email(
            to_email="recipient@example.com",
            subject="Test",
            html_body="<p>Test</p>",
        )

        assert result.success is False
        assert "authentication" in result.message.lower()
        assert result.mock_mode is False

    @patch("app.services.email_service.smtplib.SMTP")
    def test_smtp_connection_error(self, mock_smtp_class, email_service_real_mode):
        """Test SMTP connection error returns failure."""
        import smtplib

        mock_smtp_class.return_value.__enter__ = MagicMock(
            side_effect=smtplib.SMTPConnectError(421, b"Connection refused")
        )
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        result = email_service_real_mode.send_email(
            to_email="recipient@example.com",
            subject="Test",
            html_body="<p>Test</p>",
        )

        assert result.success is False
        assert result.mock_mode is False

    @patch("app.services.email_service.smtplib.SMTP")
    def test_smtp_generic_error(self, mock_smtp_class, email_service_real_mode):
        """Test generic SMTP error returns failure."""
        import smtplib

        mock_server = MagicMock()
        mock_server.sendmail.side_effect = smtplib.SMTPException("Send failed")
        mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        result = email_service_real_mode.send_email(
            to_email="recipient@example.com",
            subject="Test",
            html_body="<p>Test</p>",
        )

        assert result.success is False

    @patch("app.services.email_service.smtplib.SMTP")
    def test_unexpected_exception(self, mock_smtp_class, email_service_real_mode):
        """Test unexpected exception returns failure gracefully."""
        mock_smtp_class.return_value.__enter__ = MagicMock(
            side_effect=ConnectionRefusedError("Connection refused")
        )
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        result = email_service_real_mode.send_email(
            to_email="recipient@example.com",
            subject="Test",
            html_body="<p>Test</p>",
        )

        assert result.success is False
        assert result.mock_mode is False


# =============================================================================
# SUPPLIER INTRODUCTION TESTS
# =============================================================================


class TestSendSupplierIntroduction:
    """Tests for send_supplier_introduction()."""

    def test_introduction_template_subject(self, email_service_mock_mode):
        """Test introduction email subject contains fair name."""
        result = email_service_mock_mode.send_supplier_introduction(
            supplier_name="Acme Corp",
            supplier_email="acme@example.com",
            fair_name="Canton Fair 2026",
        )

        assert result.success is True
        assert result.mock_mode is True
        assert result.recipient_email == "acme@example.com"

    def test_introduction_template_rendering(self, email_service_mock_mode):
        """Test introduction template contains expected content."""
        subject, html, plain = email_service_mock_mode._render_introduction_template(
            supplier_name="Acme Corp",
            fair_name="Canton Fair 2026",
            sender_name="Rubén",
        )

        assert "Canton Fair 2026" in subject
        assert "Acme Corp" in html
        assert "Canton Fair 2026" in html
        assert "Rubén" in html
        assert "Acme Corp" in plain
        assert "Canton Fair 2026" in plain
        assert "Rubén" in plain

    def test_introduction_custom_sender(self, email_service_mock_mode):
        """Test introduction with custom sender name."""
        subject, html, plain = email_service_mock_mode._render_introduction_template(
            supplier_name="Test Supplier",
            fair_name="Expo 2026",
            sender_name="Carlos",
        )

        assert "Carlos" in html
        assert "Carlos" in plain

    def test_introduction_non_ascii_characters(self, email_service_mock_mode):
        """Test introduction with non-ASCII characters."""
        result = email_service_mock_mode.send_supplier_introduction(
            supplier_name="上海贸易公司",
            supplier_email="shanghai@example.com",
            fair_name="广交会",
        )

        assert result.success is True

    @patch.object(
        __import__("app.services.email_service", fromlist=["EmailService"]).EmailService,
        "send_email",
    )
    def test_introduction_calls_send_email(self, mock_send, email_service_mock_mode):
        """Test that send_supplier_introduction delegates to send_email."""
        from app.models.kompass_dto import EmailSendResultDTO

        mock_send.return_value = EmailSendResultDTO(
            success=True,
            message="Sent",
            recipient_email="test@example.com",
            mock_mode=True,
        )

        email_service_mock_mode.send_supplier_introduction(
            supplier_name="Test",
            supplier_email="test@example.com",
            fair_name="Fair 2026",
        )

        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args
        assert call_kwargs[1]["to_email"] == "test@example.com"
        assert "Fair 2026" in call_kwargs[1]["subject"]


# =============================================================================
# QUOTATION EMAIL TESTS
# =============================================================================


class TestSendQuotationEmail:
    """Tests for send_quotation_email()."""

    def test_quotation_email_without_attachment(self, email_service_mock_mode):
        """Test quotation email without PDF attachment."""
        result = email_service_mock_mode.send_quotation_email(
            recipient_email="client@example.com",
            subject="Quotation Q-001",
            body_html="<p>Your quotation is attached.</p>",
        )

        assert result.success is True
        assert result.mock_mode is True
        assert result.recipient_email == "client@example.com"

    def test_quotation_email_with_pdf(self, email_service_mock_mode):
        """Test quotation email with PDF attachment."""
        pdf = {"filename": "quotation_Q001.pdf", "data": b"%PDF fake"}

        result = email_service_mock_mode.send_quotation_email(
            recipient_email="client@example.com",
            subject="Quotation Q-001",
            body_html="<p>Attached</p>",
            pdf_attachment=pdf,
        )

        assert result.success is True

    @patch("app.services.email_service.smtplib.SMTP")
    def test_quotation_email_real_mode_with_pdf(self, mock_smtp_class, email_service_real_mode):
        """Test quotation email in real mode with PDF."""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        pdf = {"filename": "Q001.pdf", "data": b"%PDF content"}

        result = email_service_real_mode.send_quotation_email(
            recipient_email="client@example.com",
            subject="Quotation",
            body_html="<p>Here</p>",
            pdf_attachment=pdf,
        )

        assert result.success is True
        assert result.mock_mode is False
        sent_msg = mock_server.sendmail.call_args[0][2]
        assert "Q001.pdf" in sent_msg
