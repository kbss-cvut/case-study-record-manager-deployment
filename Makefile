BASE     = -f docker-compose.yml
DEV      = $(BASE) -f docker-compose.dev.yml
PROD     = $(BASE) -f docker-compose.prod.yml

# ── Environments ────────────────────────────────────────────────

dev:
	docker compose $(DEV) up --build -d

prod:
	docker compose $(PROD) up --build -d

prod-local:
	docker compose $(PROD) -f docker-compose.local-oauth.yml  up --build -d


# ── Helpers ──────────────────────────────────────────────────────

down:
	docker compose $(BASE) down

logs:
	docker compose $(BASE) logs -f

ps:
	docker compose $(BASE) ps

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  dev            Local dev stack (no auth)"
	@echo "  prod           Production deployment"
	@echo "  prod-local     Production deployment for localhost"
	@echo "  down           Stop all services"
	@echo "  logs           Tail logs"
	@echo "  ps             Show running containers"
