"""Integration tests for the FastAPI REST API."""

import pytest
from fastapi.testclient import TestClient

from ioslens.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    """GET /health should return 200 with healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data


def test_governance_evaluate_requires_auth(client: TestClient) -> None:
    """POST /v1/governance/evaluate should require authentication."""
    response = client.post(
        "/v1/governance/evaluate",
        json={"resource_type": "student_record", "action": "read"},
    )
    assert response.status_code == 401


def test_audit_logs_requires_auth(client: TestClient) -> None:
    """GET /v1/audit/logs should require authentication."""
    response = client.get("/v1/audit/logs")
    assert response.status_code == 401


def test_udm_resolve_requires_auth(client: TestClient) -> None:
    """GET /v1/udm/resolve should require authentication."""
    response = client.get("/v1/udm/resolve?cip_code=11.0701")
    assert response.status_code == 401


def test_tenants_me_requires_auth(client: TestClient) -> None:
    """GET /v1/tenants/me should require authentication."""
    response = client.get("/v1/tenants/me")
    assert response.status_code == 401


def test_health_no_auth_required(client: TestClient) -> None:
    """GET /health should not require authentication."""
    response = client.get("/health")
    assert response.status_code == 200


def test_governance_evaluate_with_valid_token(client: TestClient) -> None:
    """POST /v1/governance/evaluate with a valid JWT should return 200."""
    from ioslens.middleware.auth_service import AuthService

    auth = AuthService()
    token = auth.create_jwt(
        user_id="00000000-0000-0000-0000-000000000001",
        tenant_id="00000000-0000-0000-0000-000000000002",
        email="test@example.com",
        role="analyst",
        clearance=2,
    )

    response = client.post(
        "/v1/governance/evaluate",
        headers={"Authorization": "Bearer " + token},
        json={"resource_type": "student_record", "action": "read", "purpose": "testing"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "decision" in data
    assert data["decision"] in ("PERMIT", "DENY", "FILTER")
