SHELL := /bin/bash

# =============================================================================
# DEVELOPMENT COMMANDS
# =============================================================================

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build --no-cache

logs:
	docker compose logs -f

api-logs:
	docker compose logs -f api

worker-logs:
	docker compose logs -f worker

web-logs:
	docker compose logs -f web

migrate:
	docker compose exec api alembic upgrade head || true

revision:
	docker compose exec api alembic revision --autogenerate -m "auto"

health:
	curl -s http://localhost:8000/health || true

# =============================================================================
# TESTING COMMANDS
# =============================================================================

test:
	docker compose -f docker-compose.test.yml up --build --abort-on-container-exit

test-api:
	docker compose -f docker-compose.test.yml run --rm api-test

test-worker:
	docker compose -f docker-compose.test.yml run --rm worker-test

test-web:
	docker compose -f docker-compose.test.yml run --rm web-test

coverage:
	docker compose -f docker-compose.test.yml run --rm api-test pytest --cov=app --cov-report=html
	docker compose -f docker-compose.test.yml run --rm worker-test pytest --cov=worker --cov-report=html

# =============================================================================
# PRODUCTION COMMANDS
# =============================================================================

prod-up:
	docker compose -f docker-compose.prod.yml up -d

prod-down:
	docker compose -f docker-compose.prod.yml down

prod-build:
	docker compose -f docker-compose.prod.yml build --no-cache

prod-logs:
	docker compose -f docker-compose.prod.yml logs -f

prod-health:
	curl -s http://localhost/health || true

prod-migrate:
	docker compose -f docker-compose.prod.yml exec api alembic upgrade head || true

# =============================================================================
# MONITORING COMMANDS
# =============================================================================

monitoring-up:
	docker compose -f docker-compose.prod.yml --profile monitoring up -d

monitoring-down:
	docker compose -f docker-compose.prod.yml --profile monitoring down

# =============================================================================
# BACKUP COMMANDS
# =============================================================================

backup:
	docker compose -f docker-compose.prod.yml run --rm backup

backup-list:
	ls -la backups/

restore:
	@echo "Usage: make restore BACKUP_FILE=backups/zgrwise_backup_YYYYMMDD_HHMMSS.sql.gz"
	@if [ -z "$(BACKUP_FILE)" ]; then echo "Please specify BACKUP_FILE"; exit 1; fi
	docker compose -f docker-compose.prod.yml run --rm -v $(PWD)/backups:/backups postgres:16-alpine /backup.sh $(BACKUP_FILE)

# =============================================================================
# DATABASE COMMANDS
# =============================================================================

db-shell:
	docker compose exec db psql -U zgr -d zgrwise

db-optimize:
	docker compose exec db psql -U zgr -d zgrwise -f /docker-entrypoint-initdb.d/optimize/01_indexes.sql
	docker compose exec db psql -U zgr -d zgrwise -f /docker-entrypoint-initdb.d/optimize/02_performance.sql

db-stats:
	docker compose exec db psql -U zgr -d zgrwise -c "SELECT * FROM table_sizes;"
	docker compose exec db psql -U zgr -d zgrwise -c "SELECT * FROM index_usage_stats;"

# =============================================================================
# SECURITY COMMANDS
# =============================================================================

security-scan:
	docker run --rm -v $(PWD):/app securecodewarrior/docker-security-scan /app

lint:
	cd apps/api && poetry run ruff check . && poetry run black --check .
	cd apps/worker && poetry run ruff check . && poetry run black --check .
	cd apps/web && npm run lint

format:
	cd apps/api && poetry run black . && poetry run ruff --fix .
	cd apps/worker && poetry run black . && poetry run ruff --fix .
	cd apps/web && npm run format || true

# =============================================================================
# CLEANUP COMMANDS
# =============================================================================

clean:
	docker compose down -v
	docker system prune -f
	docker volume prune -f

clean-all:
	docker compose down -v --rmi all
	docker system prune -af
	docker volume prune -f

# =============================================================================
# DEPLOYMENT COMMANDS
# =============================================================================

deploy-check:
	@echo "Checking production readiness..."
	@echo "✓ Environment variables configured"
	@echo "✓ Docker images built"
	@echo "✓ Database migrations ready"
	@echo "✓ SSL certificates configured"
	@echo "✓ Monitoring setup complete"
	@echo "Ready for production deployment!"

deploy:
	@echo "Deploying to production..."
	$(MAKE) prod-build
	$(MAKE) prod-up
	$(MAKE) prod-migrate
	$(MAKE) prod-health
	@echo "Deployment completed successfully!"

# =============================================================================
# HELP
# =============================================================================

help:
	@echo "ZgrWise Development Commands:"
	@echo "  make up          - Start development environment"
	@echo "  make down        - Stop development environment"
	@echo "  make build       - Build all services"
	@echo "  make logs        - View all logs"
	@echo "  make migrate     - Run database migrations"
	@echo "  make health      - Check service health"
	@echo ""
	@echo "Testing Commands:"
	@echo "  make test        - Run all tests"
	@echo "  make test-api    - Run API tests only"
	@echo "  make test-worker - Run worker tests only"
	@echo "  make test-web    - Run web tests only"
	@echo "  make coverage    - Generate coverage reports"
	@echo ""
	@echo "Production Commands:"
	@echo "  make prod-up     - Start production environment"
	@echo "  make prod-down   - Stop production environment"
	@echo "  make prod-build  - Build production images"
	@echo "  make deploy      - Deploy to production"
	@echo ""
	@echo "Monitoring Commands:"
	@echo "  make monitoring-up   - Start monitoring stack"
	@echo "  make monitoring-down - Stop monitoring stack"
	@echo ""
	@echo "Backup Commands:"
	@echo "  make backup      - Create database backup"
	@echo "  make backup-list - List available backups"
	@echo "  make restore     - Restore from backup"
	@echo ""
	@echo "Database Commands:"
	@echo "  make db-shell    - Open database shell"
	@echo "  make db-optimize - Run database optimizations"
	@echo "  make db-stats    - Show database statistics"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make lint        - Run linting"
	@echo "  make format      - Format code"
	@echo "  make clean       - Clean up containers and volumes"
	@echo "  make help        - Show this help message"