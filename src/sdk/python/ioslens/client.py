"""iOSLENS Python SDK — async HTTP client."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx

from ioslens.exceptions import (
    AuthenticationError,
    AuthorizationError,
    IOSLensError,
    RateLimitError,
    ValidationError,
)

logger = logging.getLogger(__name__)


class IOSLensClient:
    """Async HTTP client for the iOSLENS REST API."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        token: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._token = token
        self._timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> IOSLensClient:
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self._timeout,
            headers=self._auth_headers(),
        )
        return self

    async def __aexit__(self, *args) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    def _auth_headers(self) -> Dict[str, str]:
        if self._token:
            return {"Authorization": f"******"}
        return {}

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("Client not started. Use as async context manager.")
        return self._client

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code == 401:
            raise AuthenticationError(response.json().get("detail", "Unauthorized"))
        elif response.status_code == 403:
            raise AuthorizationError(response.json().get("detail", "Forbidden"))
        elif response.status_code == 422:
            raise ValidationError(str(response.json()))
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        elif response.status_code >= 400:
            raise IOSLensError(f"HTTP {response.status_code}: {response.text}")

    async def health(self) -> Dict[str, Any]:
        """Check service health."""
        r = await self._get_client().get("/health")
        self._raise_for_status(r)
        return r.json()

    async def governance_check(
        self,
        resource_type: str,
        purpose: str,
        action: str = "read",
        resource_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Evaluate a governance policy."""
        payload: Dict[str, Any] = {
            "resource_type": resource_type,
            "purpose": purpose,
            "action": action,
        }
        if resource_id:
            payload["resource_id"] = resource_id
        r = await self._get_client().post("/api/v1/governance/check", json=payload)
        self._raise_for_status(r)
        return r.json()

    async def list_policies(
        self,
        resource_type: Optional[str] = None,
        role: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """List governance policies."""
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if resource_type:
            params["resource_type"] = resource_type
        if role:
            params["role"] = role
        r = await self._get_client().get("/api/v1/governance/policies", params=params)
        self._raise_for_status(r)
        return r.json()

    async def get_audit_logs(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """Retrieve audit logs."""
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if user_id:
            params["user_id"] = user_id
        if action:
            params["action"] = action
        r = await self._get_client().get("/api/v1/audit/logs", params=params)
        self._raise_for_status(r)
        return r.json()

    async def verify_audit_chain(self) -> Dict[str, Any]:
        """Verify audit chain integrity."""
        r = await self._get_client().get("/api/v1/audit/verify")
        self._raise_for_status(r)
        return r.json()

    async def udm_resolve(
        self,
        query: str,
        systems: Optional[List[str]] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Resolve a UDM query."""
        payload: Dict[str, Any] = {"query": query, "limit": limit}
        if systems:
            payload["systems"] = systems
        r = await self._get_client().post("/api/v1/udm/resolve", json=payload)
        self._raise_for_status(r)
        return r.json()

    async def udm_crosswalk(
        self,
        from_system: str,
        from_code: str,
        to_system: str,
    ) -> Dict[str, Any]:
        """Get UDM crosswalk mappings."""
        r = await self._get_client().get(
            "/api/v1/udm/crosswalk",
            params={"from_system": from_system, "from_code": from_code, "to_system": to_system},
        )
        self._raise_for_status(r)
        return r.json()
