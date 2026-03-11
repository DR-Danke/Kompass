"""Shared SMTP email service with mock mode fallback.

Provides real email sending via SMTP TLS when configured, and graceful
mock mode when SMTP credentials are absent. Used by quotation_service
for quotation emails and supplier_service for trade fair introduction emails.
"""

import smtplib
from datetime import datetime
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from typing import Dict, List, Optional, Tuple

from app.config.settings import get_settings
from app.models.kompass_dto import EmailSendResultDTO


# =============================================================================
# OUTREACH TEMPLATES
# =============================================================================

OUTREACH_TEMPLATES = {
    "introduction": {
        "name": "Presentación inicial",
        "subject": "Nice meeting you at {fair_name} — Kompass",
        "body": (
            "Dear {contact_name},\n\n"
            "It was a pleasure meeting you at {fair_name}. Thank you for taking the time "
            "to share your products and capabilities with us.\n\n"
            "We are Kompass, a sourcing and trading company specializing in connecting "
            "quality manufacturers with buyers across Latin America and beyond. "
            "We are always looking for reliable partners who share our commitment "
            "to quality and competitive pricing.\n\n"
            "We would love to explore potential collaboration opportunities with {company_name}. "
            "Could we schedule a follow-up call or exchange catalogs to discuss "
            "how we might work together?\n\n"
            "Looking forward to hearing from you.\n\n"
            "Best regards,\n"
            "{sender_name}\n"
            "Kompass Trading"
        ),
    },
    "follow_up_catalog": {
        "name": "Solicitud de catálogo",
        "subject": "Product catalog request — Kompass × {company_name}",
        "body": (
            "Dear {contact_name},\n\n"
            "I hope this message finds you well. We met at {fair_name} and I wanted to "
            "follow up on our conversation.\n\n"
            "We are very interested in {company_name}'s product range and would love to "
            "receive your latest product catalog, including pricing information if available.\n\n"
            "This will help us identify the best products for our Latin American buyers and "
            "move forward with potential orders.\n\n"
            "Thank you in advance for your time.\n\n"
            "Best regards,\n"
            "{sender_name}\n"
            "Kompass Trading"
        ),
    },
    "follow_up_pricing": {
        "name": "Solicitud de precios",
        "subject": "Pricing inquiry — Kompass × {company_name}",
        "body": (
            "Dear {contact_name},\n\n"
            "Thank you for sharing your catalog with us. We have reviewed your products "
            "and are interested in obtaining detailed pricing for the following:\n\n"
            "- FOB pricing per unit (USD)\n"
            "- Minimum order quantities (MOQ)\n"
            "- Lead times for production\n"
            "- Available packaging options\n\n"
            "We are planning to place orders for the Latin American market and would "
            "appreciate a competitive quotation from {company_name}.\n\n"
            "Please let us know if you need any additional information from our side.\n\n"
            "Best regards,\n"
            "{sender_name}\n"
            "Kompass Trading"
        ),
    },
}


class EmailService:
    """SMTP email service with mock mode fallback."""

    def __init__(self) -> None:
        settings = get_settings()
        self.smtp_host: str = settings.SMTP_HOST
        self.smtp_port: int = settings.SMTP_PORT
        self.smtp_user: str = settings.SMTP_USER
        self.smtp_password: str = settings.SMTP_PASSWORD
        self.from_email: str = settings.FROM_EMAIL
        self.from_name: str = settings.FROM_NAME
        self.mock_mode: bool = settings.EMAIL_MOCK_MODE
        print(
            f"INFO [EmailService]: Initialized (mock_mode={self.mock_mode}, "
            f"host={self.smtp_host}:{self.smtp_port})"
        )

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        plain_body: Optional[str] = None,
        attachments: Optional[List[Dict[str, bytes]]] = None,
        reply_to: Optional[str] = None,
    ) -> EmailSendResultDTO:
        """Send an email via SMTP or mock mode.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_body: HTML email body
            plain_body: Optional plain text fallback
            attachments: Optional list of dicts with 'filename' and 'data' keys
            reply_to: Optional reply-to address

        Returns:
            EmailSendResultDTO with send result
        """
        if not to_email:
            return EmailSendResultDTO(
                success=False,
                message="Recipient email address is required",
                recipient_email="",
                mock_mode=self.mock_mode,
            )

        if self.mock_mode:
            print(
                f"INFO [EmailService]: MOCK EMAIL - To: {to_email}, "
                f"Subject: '{subject}'"
            )
            if attachments:
                for att in attachments:
                    print(
                        f"INFO [EmailService]: MOCK EMAIL - Attachment: "
                        f"{att['filename']} ({len(att['data'])} bytes)"
                    )
            return EmailSendResultDTO(
                success=True,
                message=f"Email would be sent to {to_email} (mock mode)",
                sent_at=datetime.utcnow(),
                recipient_email=to_email,
                mock_mode=True,
            )

        # Build MIME message
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            if reply_to:
                msg["Reply-To"] = reply_to

            # Add plain text part
            if plain_body:
                msg.attach(MIMEText(plain_body, "plain", "utf-8"))

            # Add HTML part
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            # Add attachments
            if attachments:
                # Switch to mixed for attachments
                msg_with_attachments = MIMEMultipart("mixed")
                msg_with_attachments["Subject"] = msg["Subject"]
                msg_with_attachments["From"] = msg["From"]
                msg_with_attachments["To"] = msg["To"]
                if reply_to:
                    msg_with_attachments["Reply-To"] = reply_to
                msg_with_attachments.attach(msg)

                for att in attachments:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(att["data"])
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f'attachment; filename="{att["filename"]}"',
                    )
                    msg_with_attachments.attach(part)

                msg = msg_with_attachments

            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())

            print(f"INFO [EmailService]: Email sent to {to_email}, subject: '{subject}'")
            return EmailSendResultDTO(
                success=True,
                message=f"Email sent to {to_email}",
                sent_at=datetime.utcnow(),
                recipient_email=to_email,
                mock_mode=False,
            )

        except smtplib.SMTPAuthenticationError as e:
            print(f"ERROR [EmailService]: SMTP authentication failed: {e}")
            return EmailSendResultDTO(
                success=False,
                message=f"SMTP authentication failed: {e}",
                recipient_email=to_email,
                mock_mode=False,
            )
        except smtplib.SMTPException as e:
            print(f"ERROR [EmailService]: SMTP error: {e}")
            return EmailSendResultDTO(
                success=False,
                message=f"SMTP error: {e}",
                recipient_email=to_email,
                mock_mode=False,
            )
        except Exception as e:
            print(f"ERROR [EmailService]: Failed to send email: {e}")
            return EmailSendResultDTO(
                success=False,
                message=f"Failed to send email: {e}",
                recipient_email=to_email,
                mock_mode=False,
            )

    def get_templates(self) -> list:
        """Return metadata for all available outreach templates from DB with fallback.

        Returns:
            List of template metadata dicts with key, name, subject, body, body_preview
        """
        try:
            from app.repository.outreach_template_repository import outreach_template_repository

            db_templates = outreach_template_repository.list_templates(active_only=True)
            if db_templates:
                for t in db_templates:
                    body = t.get("body", "")
                    t["body_preview"] = (body[:150] + "...") if len(body) > 150 else body
                return db_templates
        except Exception as e:
            print(f"WARN [EmailService]: Failed to read templates from DB, using defaults: {e}")

        # Fallback to hardcoded defaults
        templates = []
        for key, tmpl in OUTREACH_TEMPLATES.items():
            templates.append({
                "key": key,
                "name": tmpl["name"],
                "subject": tmpl["subject"],
                "body": tmpl["body"],
                "body_preview": tmpl["body"][:150] + "...",
            })
        return templates

    def send_template_email(
        self,
        supplier: dict,
        template_name: str,
        custom_message: Optional[str] = None,
    ) -> EmailSendResultDTO:
        """Send a template-based outreach email to a supplier.

        Args:
            supplier: Supplier dict with contact_name, contact_email, etc.
            template_name: Key from OUTREACH_TEMPLATES
            custom_message: Optional override for the template body

        Returns:
            EmailSendResultDTO with send result
        """
        # Try DB first, fallback to hardcoded
        template = None
        try:
            from app.repository.outreach_template_repository import outreach_template_repository

            db_template = outreach_template_repository.get_by_key(template_name)
            if db_template:
                template = db_template
        except Exception as e:
            print(f"WARN [EmailService]: Failed to read template from DB: {e}")

        if not template:
            if template_name not in OUTREACH_TEMPLATES:
                return EmailSendResultDTO(
                    success=False,
                    message=f"Template '{template_name}' not found",
                    recipient_email=supplier.get("contact_email", ""),
                    mock_mode=self.mock_mode,
                )
            template = OUTREACH_TEMPLATES[template_name]
        context = {
            "contact_name": supplier.get("contact_name") or supplier.get("name", ""),
            "company_name": supplier.get("name", ""),
            "fair_name": supplier.get("fair_name") or "the trade fair",
            "sender_name": self.from_name or "Kompass",
        }

        subject = template["subject"].format(**context)
        body = custom_message if custom_message else template["body"].format(**context)

        # Wrap plain text body in simple HTML
        html_body = f"""\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
{body.replace(chr(10), '<br>')}
</body>
</html>"""

        to_email = supplier.get("contact_email", "")
        print(
            f"INFO [EmailService]: Sending template '{template_name}' email to "
            f"{to_email} (supplier: {supplier.get('name', '')})"
        )

        return self.send_email(
            to_email=to_email,
            subject=subject,
            html_body=html_body,
            plain_body=body,
        )

    def _render_introduction_template(
        self, supplier_name: str, fair_name: str, sender_name: str = "Rubén"
    ) -> Tuple[str, str, str]:
        """Render the trade fair introduction email template.

        Args:
            supplier_name: Name of the supplier
            fair_name: Name of the trade fair
            sender_name: Name of the sender

        Returns:
            Tuple of (subject, html_body, plain_body)
        """
        subject = f"Nice meeting you at {fair_name} — Kompass"

        html_body = f"""\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
  <p>Dear {supplier_name},</p>

  <p>It was a pleasure meeting you at <strong>{fair_name}</strong>. Thank you for taking the time to share your products and capabilities with us.</p>

  <p>We are <strong>Kompass</strong>, a sourcing and trading company specializing in connecting quality manufacturers with buyers across Latin America and beyond. We are always looking for reliable partners who share our commitment to quality and competitive pricing.</p>

  <p>We would love to explore potential collaboration opportunities with your company. Could we schedule a follow-up call or exchange catalogs to discuss how we might work together?</p>

  <p>Looking forward to hearing from you.</p>

  <p>
    Best regards,<br>
    <strong>{sender_name}</strong><br>
    Kompass Trading
  </p>
</body>
</html>"""

        plain_body = (
            f"Dear {supplier_name},\n\n"
            f"It was a pleasure meeting you at {fair_name}. "
            f"Thank you for taking the time to share your products and capabilities with us.\n\n"
            f"We are Kompass, a sourcing and trading company specializing in connecting "
            f"quality manufacturers with buyers across Latin America and beyond. "
            f"We are always looking for reliable partners who share our commitment "
            f"to quality and competitive pricing.\n\n"
            f"We would love to explore potential collaboration opportunities with your company. "
            f"Could we schedule a follow-up call or exchange catalogs to discuss "
            f"how we might work together?\n\n"
            f"Looking forward to hearing from you.\n\n"
            f"Best regards,\n"
            f"{sender_name}\n"
            f"Kompass Trading"
        )

        return subject, html_body, plain_body

    def send_supplier_introduction(
        self,
        supplier_name: str,
        supplier_email: str,
        fair_name: str,
        sender_name: str = "Rubén",
    ) -> EmailSendResultDTO:
        """Send a trade fair introduction email to a supplier.

        Args:
            supplier_name: Name of the supplier
            supplier_email: Supplier's email address
            fair_name: Name of the trade fair where they were met
            sender_name: Name of the sender

        Returns:
            EmailSendResultDTO with send result
        """
        subject, html_body, plain_body = self._render_introduction_template(
            supplier_name=supplier_name,
            fair_name=fair_name,
            sender_name=sender_name,
        )

        print(
            f"INFO [EmailService]: Sending introduction email to "
            f"{supplier_email} (supplier: {supplier_name}, fair: {fair_name})"
        )

        return self.send_email(
            to_email=supplier_email,
            subject=subject,
            html_body=html_body,
            plain_body=plain_body,
        )

    def send_quotation_email(
        self,
        recipient_email: str,
        subject: str,
        body_html: str,
        pdf_attachment: Optional[Dict[str, bytes]] = None,
    ) -> EmailSendResultDTO:
        """Send a quotation email with optional PDF attachment.

        Args:
            recipient_email: Recipient email address
            subject: Email subject line
            body_html: HTML email body
            pdf_attachment: Optional dict with 'filename' and 'data' keys

        Returns:
            EmailSendResultDTO with send result
        """
        attachments = [pdf_attachment] if pdf_attachment else None

        return self.send_email(
            to_email=recipient_email,
            subject=subject,
            html_body=body_html,
            attachments=attachments,
        )


# Singleton instance
email_service = EmailService()
