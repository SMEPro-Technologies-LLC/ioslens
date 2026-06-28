# iOSLENS.ai

## Governed AI Execution Layer for Regulated Industries

**Patent-Pending Architecture** · MCP-Native Middleware · PostgreSQL + pgvector

iOSLENS enforces AI scope at the database layer through the Universal Decoding Matrix (UDM), so the model only ever sees what the LENS allows. The 5-layer deterministic narrowing pipeline ensures compliance scope is a query-plan constraint, not a prompt suggestion.

---

## Quick Start

```bash
# Clone and enter
git clone https://github.com/smepro/ioslens.git && cd ioslens

# Start local stack (Postgres 16 + pgvector, API, MCP server)
make dev

# Run migrations
make migrate

# Seed UDM data
make seed

# Verify
make test
make health
```

## Architecture Overview

| Layer | Component | Technology |
|-------|-----------|------------|
| L1 | Edge & DNS | Route 53, CloudFront, WAF |
| L2 | API Gateway | Kong, ALB, Istio Ingress |
| L3 | Middleware | iOSLENS+ Orchestrator, Token Service, LENS Engine, UDM Resolver |
| L4 | AI/ML | LENS Executor, Context Assembler, LLM Gateway, Predictive Scoring |
| L5 | Execution Plane | PostgreSQL 16 + pgvector, RLS (SECURITY INVOKER), GIN, HNSW |
| L6 | Storage | S3, Encrypted Backups, 7-year Audit Archive |
| L7 | Security | IAM, SSO, SOC 2, FedRAMP, ISO 27001 |
| L8 | Observability | Prometheus, Grafana, PagerDuty |
| L9 | CI/CD | GitHub Actions, Terraform, ArgoCD |

## Delivery Model: MCP-Native Middleware

iOSLENS is delivered as **MCP-native middleware** with four interface layers:

1. **MCP Server** — JSON-RPC 2.0 tools/resources/prompts; works with any MCP-compatible AI client
2. **REST API** — Full-featured API with Python/Node/Go SDKs
3. **Connector Ecosystem** — Pre-built plugins for Teams, Slack, Salesforce, Banner
4. **SaaS Portal** — Web UI for compliance officers and auditors

## Core Components

| Component | Status | Description |
|-----------|--------|-------------|
| LENS Pipeline Engine | **BUILT** | 5-layer deterministic narrowing |
| UDM Resolver | **BUILT** | Knowledge graph traversal, active node isolation |
| RLS Policy Engine | **BUILT** | SECURITY INVOKER, RESTRICTIVE, fail-closed null-guard |
| Audit Ledger | **BUILT** | SHA-256 chained hashing, HMAC signing, advisory-lock serialization |
| PostgreSQL + pgvector | **BUILT** | halfvec(3072), HNSW, single atomic query plan |
| Execution Token Service | **DESIGNED** | Cryptographic tokens (next hardening increment) |
| MCP Server | **BUILT** | JSON-RPC 2.0 tools/resources/prompts |

## How It's Deployed

iOSLENS deploys as **MCP-native middleware** in four configurations:

| Model | Multiplier | Who Runs It | Setup Time |
|-------|-----------|-------------|------------|
| **Cloud SaaS** | 1.0x | SMEPro (our GCP) | Instant — customer gets API key |
| **Hybrid** | 1.3x | Split — API in cloud, DB on-prem | 1 day — VPN tunnel + DB install |
| **On-Premise** | 1.5x | Customer (SMEPro assists) | 2 days — K8s + images on customer hardware |
| **Air-Gapped / FedRAMP** | 2.0-3.0x | Customer (SMEPro FedRAMP team) | 1-2 weeks — HSM, WORM, 3PAO |

**See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** for step-by-step commands for every model.

## Pricing Tiers

| Tier | Annual Price | Frameworks | Users |
|------|-------------|------------|-------|
| Professional | $24,000-$48,000 | 1 | Up to 50 |
| Business | $72,000-$120,000 | Up to 3 | Unlimited |
| Enterprise | $180,000-$480,000 | Unlimited + AI | Unlimited |

## API Documentation

- [REST API Spec](docs/API.md)
- [MCP Protocol Docs](docs/MCP.md)
- [Architecture Reference](docs/ARCHITECTURE.md)
- [Security & Threat Model](docs/SECURITY.md)
- [PostgreSQL Design](docs/POSTGRES.md)

## License

Proprietary — Patent Pending. See [LICENSE](LICENSE).

---

*SMEPro Technologies · ioslens.ai · Patent-Pending Architecture*
