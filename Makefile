.PHONY: help up down build migrate seed clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

build: ## Build all services
	docker compose build

migrate: ## Run database migrations
	docker compose exec api alembic upgrade head

seed: ## Seed database with sample data
	docker compose exec api python -m app.seed

clean: ## Clean up containers and volumes
	docker compose down -v
	docker system prune -f

logs: ## Show logs for all services
	docker compose logs -f

api-logs: ## Show API logs
	docker compose logs -f api

worker-logs: ## Show worker logs
	docker compose logs -f worker

web-logs: ## Show web logs
	docker compose logs -f web

health: ## Check service health
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health || echo "API not ready"
	@curl -s http://localhost:3000 || echo "Web not ready" 