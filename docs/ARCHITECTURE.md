# iOSLENS Architecture

## Overview

iOSLENS is a 9-layer governed AI middleware platform designed for higher education and workforce compliance. It provides deterministic data narrowing, role-based access control, audit trail integrity, and an MCP-native server interface.

## 9-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  L1  │  Client Layer             │  Web, Mobile, MCP        │
├─────────────────────────────────────────────────────────────┤
│  L2  │  API Gateway              │  FastAPI + Auth          │
├─────────────────────────────────────────────────────────────┤
│  L3  │  Middleware Orchestration │  Lens Engine + UDM       │
├─────────────────────────────────────────────────────────────┤
│  L4  │  AI/ML Intelligence       │  LLM Gateway + Scoring   │
├─────────────────────────────────────────────────────────────┤
│  L5  │  Governed Execution       │  RLS + Audit + pgvector  │
├─────────────────────────────────────────────────────────────┤
│  L6  │  Data Layer               │  PostgreSQL 16 + vector  │
├─────────────────────────────────────────────────────────────┤
│  L7  │  Cache / Replay Store     │  Redis 7                 │
├─────────────────────────────────────────────────────────────┤
│  L8  │  Connector Plane          │  Teams / Slack / Banner  │
├─────────────────────────────────────────────────────────────┤
│  L9  │  Observability            │  Prometheus + Grafana    │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### LENS Engine (L3)
Five-layer deterministic narrowing that progressively filters data based on:
1. Tenant context
2. User role
3. Data clearance level
4. Purpose binding
5. Temporal scope

### Universal Decoding Matrix (UDM)
A traversal graph mapping CIP codes (academic programs), SOC codes (occupations), and NAICS codes (industries) to enable cross-domain compliance reasoning.

### MCP Server (JSON-RPC 2.0)
Model Context Protocol server exposing governance tools, audit resources, and standard prompts for AI agent consumption.

### Row-Level Security (RLS)
PostgreSQL `SECURITY INVOKER RESTRICTIVE` policies enforce tenant isolation at the database layer. No query can bypass RLS without explicit superuser grants.

### Audit Ledger
Chained-hash append-only audit table. Each record includes `SHA-256(prev_hash || event_data)` to detect tampering.

## Technology Stack

| Component      | Technology                          |
|----------------|-------------------------------------|
| API Framework  | FastAPI 0.110+                      |
| Database       | PostgreSQL 16 + pgvector            |
| ORM            | SQLAlchemy 2.0 (async)              |
| DB Driver      | asyncpg                             |
| Cache          | Redis 7                             |
| AI Gateway     | OpenAI / Anthropic / Google Gemini  |
| Auth           | SAML 2.0 / OIDC / JWT               |
| Infra          | GKE / Terraform                     |
| Observability  | Prometheus + Grafana                |
| Container      | Docker + docker-compose             |

## Deployment Topologies

- **Local Dev**: docker-compose with all services
- **Staging**: GKE cluster with managed Cloud SQL
- **Production**: Multi-region GKE with Cloud SQL HA + Redis Memorystore

## Security Model

See [SECURITY.md](SECURITY.md) for the full threat model and policy documentation.
