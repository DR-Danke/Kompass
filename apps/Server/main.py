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

    # Add more routers here:
    # app.include_router(your_router, prefix="/api/your-module")

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
