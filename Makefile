# iOSLENS.ai — Production Makefile

.PHONY: dev build migrate seed test health clean deploy-staging deploy-prod

COMPOSE = docker compose -f docker-compose.yml
PYTEST  = pytest tests/ -v --tb=short
COVERAGE = --cov=src/ioslens --cov-report=term-missing --cov-report=html

# ── Development ──────────────────────────────────────────────────

dev:
	$(COMPOSE) up -d --build
	@echo "iOSLENS stack running. API: http://localhost:8000  MCP: http://localhost:8001"
	@echo "Postgres: localhost:5432  Grafana: http://localhost:3000"

stop:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f api mcp postgres

# ── Database ─────────────────────────────────────────────────────

migrate:
	@echo "Running database migrations..."
	@for f in database/migrations/*.sql; do \
		echo "  Applying $$f"; \
		$(COMPOSE) exec -T postgres psql -U ioslens -d ioslens < $$f; \
	done
	@echo "Migrations complete."

seed:
	@echo "Seeding UDM reference data..."
	$(COMPOSE) exec -T postgres psql -U ioslens -d ioslens < database/seeds/seed_udm.sql
	@echo "Seed complete."

migrate-local:
	@echo "Running migrations against local Postgres..."
	@for f in database/migrations/*.sql; do \
		echo "  Applying $$f"; \
		psql -U ioslens -d ioslens < $$f; \
	done

# ── Testing ──────────────────────────────────────────────────────

test:
	PYTHONPATH=src $(PYTEST) $(COVERAGE)

test-unit:
	PYTHONPATH=src $(PYTEST) tests/unit/

test-integration:
	PYTHONPATH=src $(PYTEST) tests/integration/

lint:
	flake8 src/ --max-line-length=100 --ignore=E203,W503
	black src/ --check --line-length=100
	isort src/ --check-only --profile=black

fmt:
	black src/ --line-length=100
	isort src/ --profile=black

# ── Build ────────────────────────────────────────────────────────

build:
	docker build -t ioslens/api:latest -f Dockerfile --target api .
	docker build -t ioslens/mcp:latest -f Dockerfile --target mcp .

push: build
	docker push ioslens/api:latest
	docker push ioslens/mcp:latest

# ── Operations ───────────────────────────────────────────────────

health:
	@echo "API Health:"
	@curl -s http://localhost:8000/health | jq . || echo "  API not reachable"
	@echo "MCP Health:"
	@curl -s http://localhost:8001/health | jq . || echo "  MCP not reachable"
	@echo "Postgres:"
	@$(COMPOSE) exec postgres pg_isready -U ioslens || echo "  Postgres not ready"

clean:
	$(COMPOSE) down -v --remove-orphans
	docker system prune -f

# ── Deployment ───────────────────────────────────────────────────

deploy-staging:
	cd infra/terraform && terraform workspace select staging && terraform apply -auto-approve
	cd infra/kubernetes && kustomize build overlays/staging | kubectl apply -f -

deploy-prod:
	cd infra/terraform && terraform workspace select production && terraform apply
	cd infra/kubernetes && kustomize build overlays/production | kubectl apply -f -

# ── Utilities ────────────────────────────────────────────────────

psql:
	$(COMPOSE) exec postgres psql -U ioslens -d ioslens

redis-cli:
	$(COMPOSE) exec redis redis-cli

logs-api:
	$(COMPOSE) logs -f api

logs-mcp:
	$(COMPOSE) logs -f mcp

requirements:
	pip install -r src/requirements.txt
	pip install -r src/requirements-dev.txt
