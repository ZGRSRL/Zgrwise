SHELL := /bin/bash

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