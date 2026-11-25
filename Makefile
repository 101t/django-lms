# Developer shortcuts. Run `make` to list them.
.DEFAULT_GOAL := help
.PHONY: help install env migrate demo superuser run worker test lint format check migrations docker-up docker-down docker-logs clean

UV ?= uv
MANAGE = $(UV) run python manage.py
PORT ?= 8000

help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "} {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: env ## Install dependencies, create .env and set up the database
	@command -v $(UV) >/dev/null || { echo "uv is required: https://docs.astral.sh/uv/getting-started/installation/"; exit 1; }
	$(UV) sync
	$(MANAGE) migrate
	@echo "\nReady. Next: 'make demo' for sample data, 'make superuser', then 'make run'."

env: ## Create .env from example.env (never overwrites an existing one)
	@test -f .env || { cp example.env .env && echo "Created .env from example.env"; }

migrate: ## Apply database migrations
	$(MANAGE) migrate

demo: ## Load demo courses and users (teacher / student1, password demo12345)
	$(MANAGE) seed_demo

superuser: ## Create an admin account
	$(MANAGE) createsuperuser

run: ## Start the dev server on http://127.0.0.1:8000 (change with PORT=9000)
	$(MANAGE) runserver $(PORT)

worker: ## Start a Celery worker (needs REDIS_URL in .env)
	$(UV) run celery -A config worker --beat --loglevel=info

test: ## Run the test suite
	SECRET_KEY=test $(MANAGE) test

lint: ## Check code style
	$(UV) run ruff check .
	$(UV) run ruff format --check .

format: ## Auto-fix code style
	$(UV) run ruff check --fix .
	$(UV) run ruff format .

migrations: ## Create migrations after changing models
	$(MANAGE) makemigrations

check: lint test ## Everything CI runs
	SECRET_KEY=test $(MANAGE) makemigrations --check --dry-run

docker-up: ## Build and start the full Docker stack on http://localhost
	docker compose up -d --build

docker-down: ## Stop the Docker stack (keeps data)
	docker compose down

docker-logs: ## Follow Docker logs
	docker compose logs -f

clean: ## Remove caches and collected static files (keeps db.sqlite3 and .env)
	find . -name __pycache__ -type d -prune -not -path "./.venv/*" -exec rm -rf {} +
	rm -rf .ruff_cache staticfiles
