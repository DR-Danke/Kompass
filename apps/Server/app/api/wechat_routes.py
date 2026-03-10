"""WeChat API routes for webhook handling and messaging.

Provides endpoints for WeChat webhook verification (unauthenticated, required
by WeChat), incoming message handling, authenticated message sending, and
configuration status checking.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse, Response

from app.api.dependencies import get_current_user
from app.api.rbac_dependencies import require_roles
from app.models.kompass_dto import (
    WeChatMessageDTO,
    WeChatSendResultDTO,
    WeChatStatusDTO,
)
from app.services.supplier_service import supplier_service
from app.services.wechat_service import wechat_service
from app.config.database import get_database_connection, close_database_connection

router = APIRouter(tags=["WeChat"])


@router.get("/webhook")
async def verify_webhook(
    signature: str = Query(..., description="SHA1 signature from WeChat"),
    timestamp: str = Query(..., description="Timestamp from WeChat"),
    nonce: str = Query(..., description="Random number from WeChat"),
    echostr: str = Query(..., description="Echo string to return on success"),
) -> PlainTextResponse:
    """Verify WeChat webhook (unauthenticated, required by WeChat)."""
    try:
        result = wechat_service.verify_webhook(signature, timestamp, nonce, echostr)
        return PlainTextResponse(content=result)
    except ValueError:
        raise HTTPException(status_code=403, detail="Webhook verification failed")


@router.post("/webhook")
async def handle_incoming_message(request: Request) -> Response:
    """Handle incoming WeChat messages (unauthenticated, required by WeChat)."""
    body = await request.body()
    message_xml = body.decode("utf-8")

    reply = wechat_service.handle_incoming_message(message_xml)

    if reply:
        return Response(content=reply, media_type="application/xml")

    return PlainTextResponse(content="success")


@router.post("/send/{supplier_id}", response_model=WeChatSendResultDTO)
async def send_message(
    supplier_id: UUID,
    dto: WeChatMessageDTO,
    current_user: dict = Depends(require_roles(["admin", "manager"])),
) -> WeChatSendResultDTO:
    """Send a WeChat message to a supplier (admin/manager only)."""
    supplier = supplier_service.get_supplier(supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    # Get wechat_id from DB since SupplierResponseDTO doesn't include it
    wechat_id = None
    conn = get_database_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT wechat_id FROM suppliers WHERE id = %s",
                    (str(supplier_id),),
                )
                row = cur.fetchone()
                if row:
                    wechat_id = row[0]
        except Exception as e:
            print(f"ERROR [WeChatRoutes]: Failed to get wechat_id: {e}")
        finally:
            close_database_connection(conn)

    if not wechat_id:
        raise HTTPException(
            status_code=400,
            detail="Supplier does not have a WeChat ID configured",
        )

    if dto.message_type == "introduction":
        return wechat_service.send_supplier_introduction(
            wechat_id=wechat_id,
            supplier_name=supplier.name,
            fair_name="Trade Fair",
        )
    elif dto.message_type == "custom":
        if not dto.custom_content:
            raise HTTPException(
                status_code=400,
                detail="custom_content is required for custom message type",
            )
        return wechat_service.send_message(wechat_id, dto.custom_content)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported message type: {dto.message_type}",
        )


@router.get("/status", response_model=WeChatStatusDTO)
async def get_status(
    current_user: dict = Depends(get_current_user),
) -> WeChatStatusDTO:
    """Get WeChat integration configuration status."""
    return WeChatStatusDTO(
        enabled=wechat_service.enabled,
        configured=bool(wechat_service.app_id and wechat_service.app_secret),
        app_id_set=bool(wechat_service.app_id),
        webhook_url="/api/wechat/webhook",
        mock_mode=wechat_service.mock_mode,
    )
