"""Pydantic/dataclass models mirroring the database schema."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Tenant(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    domain: str
    tier: str = "standard"
    features: List[str] = []
    settings: Dict[str, Any] = {}
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class User(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    external_id: str
    email: str
    display_name: Optional[str] = None
    roles: List[str] = []
    clearance: int = 0
    metadata: Dict[str, Any] = {}
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class GovernancePolicy(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    name: str
    resource_type: str
    allowed_roles: List[str] = []
    allowed_purposes: List[str] = []
    min_clearance: int = 0
    conditions: Dict[str, Any] = {}
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AuditEntry(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    resource_type: str
    resource_id: Optional[uuid.UUID] = None
    action: str
    purpose: Optional[str] = None
    outcome: str = "success"
    metadata: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    prev_hash: str = "genesis"
    chain_hash: str = ""
    seq: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ExecutionToken(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    resource_type: str
    resource_id: Optional[uuid.UUID] = None
    purpose: str
    state: str = "DESIGNED"
    token_hash: str
    expires_at: datetime
    consumed_at: Optional[datetime] = None
    policy_id: Optional[uuid.UUID] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UDMEntity(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    system: str
    code: str
    title: str
    description: Optional[str] = None
    parent_code: Optional[str] = None
    level: int = 1
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
