"""Pytest configuration and shared fixtures for iOSLENS tests."""

import os

# Ensure we're using development settings during tests
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-for-testing-only")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://localhost/ioslens_test",
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
