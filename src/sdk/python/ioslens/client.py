"""iOSLENS async HTTP client."""

from __future__ import annotations

import httpx


class IOSLensClient:
    """Async HTTP client for the iOSLENS REST API."""

    def __init__(
        self,
        base_url: str = "https://api.ioslens.ai",
        api_key: str = "",
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "IOSLensClient":
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": "Bearer " + self._api_key},
            timeout=self._timeout,
        )
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._client:
            await self._client.aclose()

    async def health(self) -> dict:
        """Check API health."""
        response = await self._get("/health")
        return response

    async def evaluate_governance(
        self,
        resource_type: str,
        action: str,
        resource_id: str | None = None,
        purpose: str = "",
    ) -> dict:
        """Evaluate a governance decision."""
        return await self._post(
            "/v1/governance/evaluate",
            {
                "resource_type": resource_type,
                "action": action,
                "resource_id": resource_id,
                "purpose": purpose,
            },
        )

    async def get_audit_logs(
        self,
        page: int = 1,
        per_page: int = 50,
    ) -> dict:
        """Retrieve audit log entries."""
        return await self._get(f"/v1/audit/logs?page={page}&per_page={per_page}")

    async def resolve_udm(
        self,
        cip_code: str | None = None,
        soc_code: str | None = None,
        naics_code: str | None = None,
    ) -> dict:
        """Resolve UDM cross-domain mappings."""
        params = "&".join(
            f"{k}={v}"
            for k, v in [
                ("cip_code", cip_code),
                ("soc_code", soc_code),
                ("naics_code", naics_code),
            ]
            if v is not None
        )
        return await self._get(f"/v1/udm/resolve?{params}")

    async def _get(self, path: str) -> dict:
        assert self._client is not None, "Use async context manager"
        response = await self._client.get(path)
        response.raise_for_status()
        return response.json()

    async def _post(self, path: str, body: dict) -> dict:
        assert self._client is not None, "Use async context manager"
        response = await self._client.post(path, json=body)
        response.raise_for_status()
        return response.json()
