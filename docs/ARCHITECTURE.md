# iOSLENS.ai — 9-Layer Architecture Reference

## Overview

iOSLENS.ai is a governed AI intelligence platform built on a deterministic 9-layer architecture that ensures every model interaction is scoped, audited, and policy-enforced before execution.

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1 │  Identity & Access (Ethos/Banner SAML/OIDC)          │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2 │  API Gateway (FastAPI, rate-limit, JWT validation)    │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3 │  iOSLENS+ Middleware Orchestration                    │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4 │  AI/ML Intelligence Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  Layer 5 │  Governed Execution Plane (PostgreSQL + RLS)          │
├─────────────────────────────────────────────────────────────────┤
│  Layer 6 │  Universal Decoding Matrix (UDM)                      │
├─────────────────────────────────────────────────────────────────┤
│  Layer 7 │  Audit Ledger (chained-hash immutable log)            │
├─────────────────────────────────────────────────────────────────┤
│  Layer 8 │  Connector Ecosystem (Banner, Teams, Slack)           │
├─────────────────────────────────────────────────────────────────┤
│  Layer 9 │  Observability (Prometheus, Grafana, OTel)            │
└─────────────────────────────────────────────────────────────────┘
```

## Layer Descriptions

### Layer 1 — Identity & Access (Ethos/Banner Seam)

Ethos grants **application-level access** to iOSLENS. It acts as the upstream identity provider via SAML 2.0 / OIDC. Banner ERP provides the authoritative source of institutional records (students, employees, courses).

**Key principle**: Ethos/Banner authenticates *who* the caller is at the application boundary. Per-identity data scoping is enforced *inside* iOSLENS via UDM filtering and PostgreSQL RLS — never delegated back to the upstream provider.

### Layer 2 — API Gateway

FastAPI application server exposing REST endpoints under `/api/v1/`. Responsibilities:
- JWT validation (RS256)
- Tenant extraction from JWT claims
- Rate limiting via Redis
- Request/response schema validation (Pydantic)

### Layer 3 — iOSLENS+ Middleware Orchestration

The orchestrator sequences every inbound request through:
1. `auth_service` — validate token, extract identity
2. `policy_engine` — evaluate role + clearance + purpose
3. `token_service` — issue or validate execution token
4. `udm_resolver` — resolve entity via Universal Decoding Matrix
5. `lens_engine` — 5-layer deterministic data narrowing

### Layer 4 — AI/ML Intelligence

- **LLM Gateway**: Routes to OpenAI / Anthropic / Gemini based on tenant config
- **Context Assembler**: Builds bounded, policy-scoped context chunks
- **Predictive Scoring**: Compliance posture ML model
- **Anomaly Detection**: Baseline deviation detection

### Layer 5 — Governed Execution Plane

PostgreSQL 16 with `pgvector`. All queries execute under:
- Row-Level Security (RLS) with `SECURITY INVOKER` + `RESTRICTIVE` policies
- Tenant isolation via `current_setting('app.tenant_id')`
- Execution token validation before any write

### Layer 6 — Universal Decoding Matrix (UDM)

Cross-domain taxonomy resolution: CIP (education), SOC (workforce), NAICS (industry). Enables natural-language entity lookup across classification systems.

### Layer 7 — Audit Ledger

Tamper-evident chained-hash audit log. Each record includes:
- `sha256(previous_hash || event_data)` forming an append-only chain
- Tenant ID, user ID, resource, action, timestamp
- Queryable via `/api/v1/audit`

### Layer 8 — Connector Ecosystem

- **Banner**: Bidirectional ERP data sync
- **Microsoft Teams**: Notification and workflow integration
- **Slack**: Alert routing

### Layer 9 — Observability

Prometheus metrics exposed at `/metrics`. Grafana dashboards for:
- Request latency p50/p95/p99
- Database pool utilization
- RLS policy hit rate
- Audit chain integrity

## Request Lifecycle

```
Client → [L1 Ethos Auth] → [L2 API Gateway] → [L3 Orchestrator]
       → [L4 AI/UDM] → [L5 PostgreSQL RLS] → [L7 Audit Ledger]
       → Response ← [L9 Metrics]
```

## Security Model

See [SECURITY.md](SECURITY.md) for threat model, RLS policy details, and token flow.

## Data Model

See [POSTGRES.md](POSTGRES.md) for schema design, indexing strategy, and pgvector configuration.
