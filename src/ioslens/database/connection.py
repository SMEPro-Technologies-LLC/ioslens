"""Async PostgreSQL connection pool using SQLAlchemy 2.0 + asyncpg."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ioslens.config import get_settings

logger = logging.getLogger(__name__)

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Return (or create) the global async engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        # Convert postgres:// to postgresql+asyncpg://
        url = settings.database_url
        if url.startswith("postgresql://") or url.startswith("postgres://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)

        _engine = create_async_engine(
            url,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            echo=settings.debug,
        )
        logger.info("Database engine created")
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return (or create) the global async session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            class_=AsyncSession,
        )
    return _session_factory


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager that yields a database session."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def close_engine() -> None:
    """Dispose of the engine (call on application shutdown)."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        logger.info("Database engine disposed")
