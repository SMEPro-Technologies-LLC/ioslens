"""Request orchestrator — sequences all middleware layers for each request."""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorContext:
    """Carries resolved identity and policy state through the request pipeline."""
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    roles: List[str]
    resource_type: str
    resource_id: Optional[uuid.UUID] = None
    purpose: Optional[str] = None
    action: str = "read"
    policy_id: Optional[uuid.UUID] = None
    execution_token: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class RequestOrchestrator:
    """
    Sequences the iOSLENS middleware stack:
      1. auth_service  — validate token, extract identity
      2. policy_engine — evaluate role + clearance + purpose
      3. token_service — issue or validate execution token
      4. udm_resolver  — resolve entity via Universal Decoding Matrix
      5. lens_engine   — 5-layer deterministic data narrowing
    """

    def __init__(
        self,
        auth_service,
        policy_engine,
        token_service,
        udm_resolver,
        lens_engine,
    ) -> None:
        self.auth_service = auth_service
        self.policy_engine = policy_engine
        self.token_service = token_service
        self.udm_resolver = udm_resolver
        self.lens_engine = lens_engine

    async def process(
        self,
        jwt_token: str,
        resource_type: str,
        purpose: str,
        action: str = "read",
        resource_id: Optional[uuid.UUID] = None,
        execution_token: Optional[str] = None,
    ) -> OrchestratorContext:
        """Run the full middleware sequence, returning a resolved context."""
        # Step 1: Validate JWT and extract identity
        identity = await self.auth_service.validate(jwt_token)
        logger.debug("Identity resolved: tenant=%s user=%s", identity.tenant_id, identity.user_id)

        ctx = OrchestratorContext(
            tenant_id=identity.tenant_id,
            user_id=identity.user_id,
            roles=identity.roles,
            resource_type=resource_type,
            resource_id=resource_id,
            purpose=purpose,
            action=action,
        )

        # Step 2: Policy evaluation
        policy_result = await self.policy_engine.evaluate(ctx)
        if not policy_result.allowed:
            raise PermissionError(f"Policy denied: {policy_result.reason}")
        ctx.policy_id = policy_result.policy_id
        logger.debug("Policy allowed: %s", policy_result.policy_id)

        # Step 3: Token service
        if execution_token:
            await self.token_service.validate(execution_token, ctx)
        else:
            ctx.execution_token = await self.token_service.issue(ctx)

        # Step 4: UDM resolution
        if resource_id:
            await self.udm_resolver.resolve(ctx)

        # Step 5: Lens engine narrowing
        await self.lens_engine.narrow(ctx)

        return ctx
