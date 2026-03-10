"""WeChat integration service with mock mode fallback.

Provides WeChat Official Account integration for receiving business card
photos via webhook and sending automated outreach messages to suppliers.
Gracefully degrades to mock mode when WeChat API credentials are not configured.
"""

import hashlib
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from io import BytesIO
from typing import Optional

import httpx

from app.config.settings import get_settings
from app.models.kompass_dto import WeChatSendResultDTO


class WeChatService:
    """WeChat integration service with mock mode fallback."""

    def __init__(self) -> None:
        settings = get_settings()
        self.app_id: str = settings.WECHAT_APP_ID
        self.app_secret: str = settings.WECHAT_APP_SECRET
        self.verify_token: str = settings.WECHAT_VERIFY_TOKEN
        self.mock_mode: bool = settings.WECHAT_MOCK_MODE
        self.enabled: bool = bool(self.app_id and self.app_secret)
        self.access_token: Optional[str] = None
        self.token_expires_at: float = 0
        print(
            f"INFO [WeChatService]: Initialized (mock_mode={self.mock_mode}, "
            f"enabled={self.enabled})"
        )

    def verify_webhook(
        self, signature: str, timestamp: str, nonce: str, echostr: str
    ) -> str:
        """Verify WeChat webhook signature.

        Args:
            signature: SHA1 signature from WeChat
            timestamp: Timestamp from WeChat
            nonce: Random number from WeChat
            echostr: Echo string to return on success

        Returns:
            echostr if verification succeeds

        Raises:
            ValueError: If signature verification fails
        """
        params = sorted([self.verify_token, timestamp, nonce])
        hash_str = "".join(params)
        computed = hashlib.sha1(hash_str.encode("utf-8")).hexdigest()

        if computed != signature:
            print(
                f"WARN [WeChatService]: Webhook verification failed "
                f"(expected={computed}, got={signature})"
            )
            raise ValueError("Invalid webhook signature")

        print("INFO [WeChatService]: Webhook verification successful")
        return echostr

    def _get_access_token(self) -> str:
        """Get a valid WeChat API access token, refreshing if needed.

        Returns:
            Access token string
        """
        if self.mock_mode:
            return "mock-access-token"

        if self.access_token and self.token_expires_at > time.time():
            return self.access_token

        url = (
            f"https://api.weixin.qq.com/cgi-bin/token"
            f"?grant_type=client_credential"
            f"&appid={self.app_id}&secret={self.app_secret}"
        )

        try:
            response = httpx.get(url, timeout=10)
            data = response.json()

            if "access_token" in data:
                self.access_token = data["access_token"]
                self.token_expires_at = time.time() + data.get("expires_in", 7200) - 60
                print("INFO [WeChatService]: Access token refreshed")
                return self.access_token
            else:
                error_msg = data.get("errmsg", "Unknown error")
                print(f"ERROR [WeChatService]: Failed to get access token: {error_msg}")
                raise RuntimeError(f"WeChat token error: {error_msg}")
        except httpx.HTTPError as e:
            print(f"ERROR [WeChatService]: HTTP error getting access token: {e}")
            raise RuntimeError(f"WeChat API unreachable: {e}")

    def handle_incoming_message(self, message_xml: str) -> Optional[str]:
        """Handle an incoming WeChat message.

        Args:
            message_xml: Raw XML message body from WeChat

        Returns:
            XML reply string, or None if no reply needed
        """
        try:
            root = ET.fromstring(message_xml)
        except ET.ParseError as e:
            print(f"ERROR [WeChatService]: Failed to parse incoming XML: {e}")
            return None

        msg_type = root.findtext("MsgType", "")
        from_user = root.findtext("FromUserName", "")
        to_user = root.findtext("ToUserName", "")

        if msg_type == "image":
            pic_url = root.findtext("PicUrl", "")
            print(
                f"INFO [WeChatService]: Received image message from {from_user}, "
                f"pic_url={pic_url}"
            )

            try:
                from app.services.business_card_service import business_card_service

                business_card_service.create_capture(
                    image_url=pic_url,
                    notes=f"Received via WeChat from {from_user}",
                )
                print("INFO [WeChatService]: Image routed to business card extraction")
            except Exception as e:
                print(f"ERROR [WeChatService]: Failed to route image to extraction: {e}")

            reply_content = (
                "Thank you! We received your business card and are processing it."
            )

        elif msg_type == "text":
            content = root.findtext("Content", "")
            print(
                f"INFO [WeChatService]: Received text message from {from_user}: "
                f"{content[:50]}"
            )
            reply_content = (
                "Thank you for your message. Our team will follow up shortly."
            )

        else:
            print(
                f"INFO [WeChatService]: Received {msg_type} message from {from_user}"
            )
            reply_content = "Message received. Thank you!"

        timestamp = str(int(time.time()))
        return (
            f"<xml>"
            f"<ToUserName><![CDATA[{from_user}]]></ToUserName>"
            f"<FromUserName><![CDATA[{to_user}]]></FromUserName>"
            f"<CreateTime>{timestamp}</CreateTime>"
            f"<MsgType><![CDATA[text]]></MsgType>"
            f"<Content><![CDATA[{reply_content}]]></Content>"
            f"</xml>"
        )

    def send_message(
        self, wechat_id: str, content: str
    ) -> WeChatSendResultDTO:
        """Send a text message to a WeChat user.

        Args:
            wechat_id: Recipient's WeChat OpenID
            content: Message text content

        Returns:
            WeChatSendResultDTO with send result
        """
        if not wechat_id:
            return WeChatSendResultDTO(
                success=False,
                message="WeChat ID is required",
                recipient_wechat_id="",
                mock_mode=self.mock_mode,
            )

        if self.mock_mode:
            print(
                f"INFO [WeChatService]: MOCK MESSAGE - To: {wechat_id}, "
                f"Content: {content[:100]}"
            )
            return WeChatSendResultDTO(
                success=True,
                message=f"Message would be sent to {wechat_id} (mock mode)",
                sent_at=datetime.utcnow(),
                recipient_wechat_id=wechat_id,
                mock_mode=True,
            )

        try:
            token = self._get_access_token()
            url = (
                f"https://api.weixin.qq.com/cgi-bin/message/custom/send"
                f"?access_token={token}"
            )
            payload = {
                "touser": wechat_id,
                "msgtype": "text",
                "text": {"content": content},
            }
            response = httpx.post(url, json=payload, timeout=10)
            data = response.json()

            if data.get("errcode", 0) == 0:
                print(f"INFO [WeChatService]: Message sent to {wechat_id}")
                return WeChatSendResultDTO(
                    success=True,
                    message=f"Message sent to {wechat_id}",
                    sent_at=datetime.utcnow(),
                    recipient_wechat_id=wechat_id,
                    mock_mode=False,
                )
            else:
                error_msg = data.get("errmsg", "Unknown error")
                print(
                    f"ERROR [WeChatService]: Failed to send message: {error_msg}"
                )
                return WeChatSendResultDTO(
                    success=False,
                    message=f"WeChat API error: {error_msg}",
                    recipient_wechat_id=wechat_id,
                    mock_mode=False,
                )

        except (httpx.HTTPError, RuntimeError) as e:
            print(f"ERROR [WeChatService]: Failed to send message: {e}")
            return WeChatSendResultDTO(
                success=False,
                message=f"Failed to send message: {e}",
                recipient_wechat_id=wechat_id,
                mock_mode=False,
            )

    def send_template_message(
        self,
        supplier: dict,
        template_name: str,
        custom_message: Optional[str] = None,
    ) -> WeChatSendResultDTO:
        """Send a template-based outreach message to a supplier via WeChat.

        Args:
            supplier: Supplier dict with wechat_id, contact_name, etc.
            template_name: Key from OUTREACH_TEMPLATES
            custom_message: Optional override for the template body

        Returns:
            WeChatSendResultDTO with send result
        """
        from app.services.email_service import OUTREACH_TEMPLATES

        if template_name not in OUTREACH_TEMPLATES:
            return WeChatSendResultDTO(
                success=False,
                message=f"Template '{template_name}' not found",
                recipient_wechat_id=supplier.get("wechat_id", ""),
                mock_mode=self.mock_mode,
            )

        template = OUTREACH_TEMPLATES[template_name]
        context = {
            "contact_name": supplier.get("contact_name") or supplier.get("name", ""),
            "company_name": supplier.get("name", ""),
            "fair_name": supplier.get("fair_name") or "the trade fair",
            "sender_name": "Kompass",
        }

        body = custom_message if custom_message else template["body"].format(**context)
        wechat_id = supplier.get("wechat_id", "")

        print(
            f"INFO [WeChatService]: Sending template '{template_name}' message to "
            f"{wechat_id} (supplier: {supplier.get('name', '')})"
        )

        return self.send_message(wechat_id, body)

    def _render_introduction_message(
        self,
        supplier_name: str,
        fair_name: str,
        sender_name: str = "Rubén",
    ) -> str:
        """Render a trade fair introduction message for WeChat.

        Args:
            supplier_name: Name of the supplier
            fair_name: Name of the trade fair
            sender_name: Name of the sender

        Returns:
            Plain text introduction message
        """
        return (
            f"Dear {supplier_name},\n\n"
            f"It was a pleasure meeting you at {fair_name}. "
            f"Thank you for taking the time to share your products "
            f"and capabilities with us.\n\n"
            f"We are Kompass, a sourcing and trading company specializing "
            f"in connecting quality manufacturers with buyers across "
            f"Latin America and beyond. We are always looking for reliable "
            f"partners who share our commitment to quality and competitive "
            f"pricing.\n\n"
            f"We would love to explore potential collaboration opportunities "
            f"with your company. Could we schedule a follow-up call or "
            f"exchange catalogs to discuss how we might work together?\n\n"
            f"Looking forward to hearing from you.\n\n"
            f"Best regards,\n"
            f"{sender_name}\n"
            f"Kompass Trading"
        )

    def send_supplier_introduction(
        self,
        wechat_id: str,
        supplier_name: str,
        fair_name: str,
        sender_name: str = "Rubén",
    ) -> WeChatSendResultDTO:
        """Send a trade fair introduction message to a supplier via WeChat.

        Args:
            wechat_id: Supplier's WeChat OpenID
            supplier_name: Name of the supplier
            fair_name: Name of the trade fair
            sender_name: Name of the sender

        Returns:
            WeChatSendResultDTO with send result
        """
        message_text = self._render_introduction_message(
            supplier_name=supplier_name,
            fair_name=fair_name,
            sender_name=sender_name,
        )

        print(
            f"INFO [WeChatService]: Sending introduction to "
            f"{wechat_id} (supplier: {supplier_name}, fair: {fair_name})"
        )

        return self.send_message(wechat_id, message_text)

    def resolve_phone_to_wechat(self, phone: str) -> Optional[str]:
        """Attempt to resolve a phone number to a WeChat ID.

        Note: WeChat Official Account API does not support phone-to-ID lookup.
        This method always returns None.

        Args:
            phone: Phone number to look up

        Returns:
            None (not supported by WeChat API)
        """
        print(
            f"INFO [WeChatService]: Phone-to-WeChat resolution not supported "
            f"by WeChat Official Account API (phone={phone})"
        )
        return None

    def decode_qr_from_image(self, image_data: bytes) -> Optional[str]:
        """Decode QR codes from an image.

        Args:
            image_data: Raw image bytes

        Returns:
            Decoded QR code data string, or None if no QR found
        """
        try:
            from PIL import Image
            from pyzbar.pyzbar import decode as pyzbar_decode
        except ImportError as e:
            print(
                f"WARN [WeChatService]: QR decoding unavailable "
                f"(missing dependency: {e})"
            )
            return None

        try:
            image = Image.open(BytesIO(image_data))
            results = pyzbar_decode(image)

            qr_results = [r for r in results if r.type == "QRCODE"]
            if qr_results:
                decoded = qr_results[0].data.decode("utf-8")
                print(f"INFO [WeChatService]: QR code decoded: {decoded[:50]}")
                return decoded

            print("INFO [WeChatService]: No QR code found in image")
            return None

        except Exception as e:
            print(f"ERROR [WeChatService]: QR decoding failed: {e}")
            return None


# Singleton instance
wechat_service = WeChatService()
