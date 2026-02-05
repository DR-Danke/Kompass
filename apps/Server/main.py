"""
Main FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.health import router as health_router
from app.api.auth_routes import router as auth_router
from app.api.supplier_routes import router as supplier_router
from app.api.product_routes import router as products_router
from app.api.category_routes import router as category_router
from app.api.tag_routes import router as tag_router
from app.api.niche_routes import router as niche_router
from app.api.extraction_routes import router as extraction_router
from app.api.portfolio_routes import router as portfolio_router
from app.api.client_routes import router as client_router
from app.api.quotation_routes import router as quotation_router
from app.api.pricing_routes import router as pricing_router
from app.api.dashboard_routes import router as dashboard_router
from app.api.audit_routes import router as audit_router
from database.init_db import init_database


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    print("INFO [Main]: Starting application...")

    settings = get_settings()

    # Initialize database
    if settings.DATABASE_URL:
        print("INFO [Main]: Initializing database...")
        db_success = init_database()
        if db_success:
            print("INFO [Main]: Database initialization complete")
        else:
            print("WARN [Main]: Database initialization failed, continuing anyway")
    else:
        print("WARN [Main]: DATABASE_URL not set, skipping database initialization")

    yield

    # Shutdown
    print("INFO [Main]: Shutting down application...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Your API",
        description="API for Your Application",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(health_router, prefix="/api")
    app.include_router(auth_router, prefix="/api/auth")
    app.include_router(supplier_router, prefix="/api/suppliers")
    app.include_router(products_router, prefix="/api/products")
    app.include_router(category_router, prefix="/api/categories")
    app.include_router(tag_router, prefix="/api/tags")
    app.include_router(niche_router, prefix="/api/niches")
    app.include_router(extraction_router, prefix="/api/extract")
    app.include_router(portfolio_router, prefix="/api/portfolios")
    app.include_router(client_router, prefix="/api/clients")
    app.include_router(quotation_router, prefix="/api/quotations")
    app.include_router(pricing_router, prefix="/api/pricing")
    app.include_router(dashboard_router, prefix="/api/dashboard")
    app.include_router(audit_router, prefix="/api/suppliers")

    print(f"INFO [Main]: Application configured with CORS origins: {settings.get_cors_origins()}")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVER_PORT,
        reload=True,
    )
