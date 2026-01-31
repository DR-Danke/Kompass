"""Health check endpoint."""

from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from app.config import get_settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: str
    version: str
    service: str
    mock_mode: bool


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns:
        HealthResponse with current status
    """
    settings = get_settings()

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
        service="your-api",
        mock_mode=settings.USE_MOCK_APIS,
    )
