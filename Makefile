USERNAME ?= $(shell bash -c 'read -p "Enter username: " username; echo $$username')
PASSWORD ?= $(shell bash -c 'read -s -p "Password: " pwd; echo $$pwd')

.PHONY: help
help:
	@echo ------------------------------
	@echo - Makefile Taget Information -
	@echo ------------------------------
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: ## Build the images to prepare for runtime.
	@printf '\033[33m'
	@echo --------------------------
	@echo - Building Docker Images -
	@echo --------------------------
	docker-compose build

.PHONY: build-clean
build-clean: ## Build the images using no-cache to prepare for runtime.
	@printf '\033[33m'
	@echo --------------------------
	@echo - Building Docker Images -
	@echo --------------------------
	docker-compose build --no-cache

.PHONY: up
up: ## Start backend and db containers in foreground.
	@printf '\033[33m'
	@echo -------------------------------------------
	@echo - Starting the Stock Simulator containers -
	@echo -------------------------------------------
	docker-compose up

.PHONY: up-new
up-new: ## Delete database volume and start a clean environment.
	@printf '\033[33m'
	@echo -------------------------------------------
	@echo - Starting the Stock Simulator containers -
	@echo -------------------------------------------
	@make down; docker volume rm stock-db;
	docker-compose up

.PHONY: down
down: ## Stop a running stock simulator containers.
	@printf '\033[33m'
	@echo -------------------------------------------
	@echo - Stopping the Stock Simulator containers -
	@echo -------------------------------------------
	docker-compose down

.PHONY: shell
shell: ## Build the images using no-cache to prepare for runtime.
	@printf '\033[33m'
	@echo -----------------------------------
	@echo - Connecting to backend container -
	@echo -----------------------------------
	docker-compose exec -e LS_COLORS='di=93:fi=0:ln=31:pi=5:so=5:bd=5:cd=5:or=31:mi=0:ex=35:*.rpm=90' -e CLICOLOR=1 -e TERM=xterm-256color backend bash -i -o vi

.PHONY: psql
psql: ## Connect to stock simulator database as DB user postgres
	@printf '\033[33m'
	@echo -----------------------------------------------------------
	@echo - Connecting to stock simulator database as postgres user -
	@echo -----------------------------------------------------------
	docker-compose exec db bash -c "psql -U postgres -d stocks"

.PHONY: createsuperuser
createsuperuser: ## Performs a ./manage.py createsuperuser inside backend container.
	@printf '\033[33m'
	@echo -------------------------------------
	@echo - Executing createsuperuser command -
	@echo -------------------------------------
	docker-compose exec backend python manage.py createsuperuser

.PHONY: migrate
migrate: ## Performs database migration using the backend models.
	@printf '\033[33m'
	@echo --------------------------------------------------------
	@echo - Starting database migration using the backend models -
	@echo --------------------------------------------------------
	docker-compose exec backend python manage.py makemigrations stock_simulator
	docker-compose exec backend python manage.py migrate

.PHONY: obtain-token
obtain-token: ## Generate jwt token.
	@printf '\033[33m'
	@echo ----------------
	@echo - Obtain Token -
	@echo ----------------
	@echo curl -X POST http://127.0.0.1:8000/api/token-auth/ -H 'Content-Type: application/json' \
	-d '{"username": "$ USERNAME", "password": "$ PASSWORD"}'
	$(eval TOKEN=$(shell curl -X POST http://127.0.0.1:8000/api/obtain-token/ -H 'Content-Type: application/json' -d '{"username": "$(USERNAME)", "password": "$(PASSWORD)"}'))
	@echo "\033[036mToken    :\033[m $(TOKEN)"
