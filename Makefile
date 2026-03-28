.PHONY: help install dev-install format format-check lint lint-fix typecheck test test-cov clean run run-stdio run-http check all bundle bump

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv sync --no-dev

dev-install: ## Install all dependencies including dev
	uv sync

format: ## Format code
	uv run ruff format src/ tests/

format-check: ## Check code formatting
	uv run ruff format --check src/ tests/

lint: ## Run linter
	uv run ruff check src/ tests/

lint-fix: ## Fix lint issues
	uv run ruff check --fix src/ tests/

typecheck: ## Run type checker
	uv run ty check src/

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage
	uv run pytest --cov=src/mcp_quiver --cov-report=term-missing

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .ruff_cache/ .coverage htmlcov/ __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

run: run-stdio ## Run server (stdio mode, default)

run-stdio: ## Run server in stdio mode
	uv run python -m mcp_quiver.server

run-http: ## Run server in HTTP mode
	uv run uvicorn mcp_quiver.server:app --host 0.0.0.0 --port 8000

check: format-check lint typecheck test ## Run all checks

all: dev-install check ## Full workflow

bundle: ## Build MCPB bundle
	mpak bundle build .

bump: ## Bump version (usage: make bump VERSION=0.2.0)
	@if [ -z "$(VERSION)" ]; then echo "Usage: make bump VERSION=0.2.0"; exit 1; fi
	@echo "Bumping to $(VERSION)..."
	@jq --arg v "$(VERSION)" '.version = $$v' manifest.json > manifest.tmp.json && mv manifest.tmp.json manifest.json
	@sed -i '' 's/^version = ".*"/version = "$(VERSION)"/' pyproject.toml
	@sed -i '' 's/^__version__ = ".*"/__version__ = "$(VERSION)"/' src/mcp_quiver/__init__.py
	@echo "Version bumped to $(VERSION) in manifest.json, pyproject.toml, __init__.py"

# Aliases
fmt: format
t: test
l: lint
