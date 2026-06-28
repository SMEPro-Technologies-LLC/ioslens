"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ioslens.api.router import api_router
from ioslens.config import get_settings
from ioslens.database.connection import close_pool, init_pool

settings = get_settings()
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown."""
    logger.info("iOSLENS starting up (env=%s)", settings.environment)
    await init_pool()
    logger.info("Database pool initialized")
    yield
    logger.info("iOSLENS shutting down")
    await close_pool()


app = FastAPI(
    title="iOSLENS.ai",
    description="Governed AI Intelligence Platform",
    version=settings.version,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(api_router, prefix="/api")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "type": "https://api.ioslens.ai/errors/internal",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred.",
        },
    )


if __name__ == "__main__":
    uvicorn.run(
        "ioslens.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        proxy_headers=True,
    )
