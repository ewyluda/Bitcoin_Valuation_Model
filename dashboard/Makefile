# Bitcoin Valuation Dashboard Makefile

.PHONY: help install dev build up down logs shell test clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development Commands
install: ## Install all dependencies
	pip install -r api/requirements.txt
	pip install -r pipeline/requirements.txt
	cd webapp && npm install

dev-backend: ## Run backend in development mode
	cd api/src && uvicorn main:app --reload --port 8000

dev-frontend: ## Run frontend in development mode
	cd webapp && npm run dev

dev-pipeline: ## Run pipeline once
	python -m pipeline.src.scheduler run

# Database Commands
db-init: ## Initialize database
	python -c "from shared.models.database import init_database; init_database('sqlite:///data/btc_valuation.db')"

db-import: ## Import legacy CSV data
	python -m pipeline.src.scheduler import --csv resources/btc.csv

db-backfill: ## Backfill historical data
	python -m pipeline.src.scheduler backfill --start-date 2021-01-01

# Docker Commands
build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## View logs
	docker-compose logs -f

shell-api: ## Open shell in API container
	docker-compose exec api /bin/bash

shell-pipeline: ## Open shell in pipeline container
	docker-compose exec pipeline /bin/bash

# Testing
test: ## Run all tests
	cd api && pytest -v
	cd webapp && npm test

test-backend: ## Run backend tests
	cd api && pytest -v

test-frontend: ## Run frontend tests
	cd webapp && npm test

# Cleanup
clean: ## Clean build artifacts
	rm -rf webapp/.next
	rm -rf webapp/node_modules
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.db" -delete

# Production
deploy: ## Deploy to production (configure first)
	@echo "Configure deployment settings in docker-compose.prod.yml"
	# docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
