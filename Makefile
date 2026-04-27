# Makefile for Docker management

.PHONY: help build run start stop restart down logs logs-backend logs-frontend ps shell-backend shell-frontend shell-db

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build docker images
	docker compose build

run: ## Start containers in the background, rebuilding images if necessary
	docker compose up --build -d

start: ## Start existing containers without rebuilding
	docker compose up -d

stop: ## Stop and remove containers
	docker compose down

restart: stop start ## Restart containers

down: stop ## Alias for stop

logs: ## Tail logs of all containers
	docker compose logs -f

logs-backend: ## Tail logs of the backend container
	docker compose logs -f backend

logs-frontend: ## Tail logs of the frontend container
	docker compose logs -f frontend

ps: ## List running containers
	docker compose ps

shell-backend: ## Access the backend container shell
	docker compose exec backend /bin/bash

shell-frontend: ## Access the frontend container shell
	docker compose exec frontend /bin/sh

shell-db: ## Access the database container shell
	docker compose exec db /bin/sh
