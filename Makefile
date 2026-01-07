.PHONY: setup analyze test test-all lint clean help

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup:  ## Install dependencies
	uv sync --all-groups

analyze:  ## Run full analysis (2005 through current week 2026-01-05)
	uv run python -m repo_analyzer --since 2005-04-01 --to 2026-01-05

test:  ## Run all tests (excluding slow E2E tests)
	uv run pytest -v -m "not slow"

test-all:  ## Run all tests including slow E2E tests
	uv run pytest -v

lint:  ## Run linters (ruff)
	uv run ruff check src/ tests/

clean:  ## Remove cache and generated data
	rm -rf cache/ data/

.DEFAULT_GOAL := help
