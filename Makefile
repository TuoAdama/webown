.PHONY: help build up down logs restart clean test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show application logs
	docker-compose logs -f app

restart: ## Restart all services
	docker-compose restart

clean: ## Remove containers, volumes and images
	docker-compose down -v
	docker system prune -f

test: ## Run tests (when implemented)
	docker-compose exec app python -m pytest

shell: ## Open a shell in the app container
	docker-compose exec app /bin/bash

db-shell: ## Open MySQL shell
	docker-compose exec mysql mysql -u webown -p webown

scrape-once: ## Run scraping once
	docker-compose exec app python -c "from app.scheduler import ScrapingScheduler; s = ScrapingScheduler(); s.run_once()"

