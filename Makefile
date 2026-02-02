.PHONY: setup analyze analyze-svn test test-all lint clean help notebook notebook-run

# Default notebook to use if none specified
NOTEBOOK ?= chart_iterations.py

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup:  ## Install dependencies (including viz extras)
	uv sync --all-groups --all-extras

analyze:  ## Run full git analysis (2005 through 2025)
	uv run python -m repo_analyzer --since 2005-04-01 --to 2025-12-31

analyze-svn:  ## Run full SVN analysis (2003 through 2025)
	uv run python -m repo_analyzer.svn.cli --since 2003-04-01 --to 2025-12-31

test:  ## Run all tests (excluding slow E2E tests)
	uv run pytest -v -m "not slow"

test-all:  ## Run all tests including slow E2E tests
	uv run pytest -v

lint:  ## Run linters (ruff)
	uv run ruff check src/ tests/

notebook:  ## Launch Marimo notebook editor (NOTEBOOK=filename.py)
	uv run marimo edit src/notebooks/$(NOTEBOOK)

notebook-run:  ## Run notebook in view mode (NOTEBOOK=filename.py)
	uv run marimo run src/notebooks/$(NOTEBOOK)

clean:  ## Remove cache and generated data
	rm -rf cache/ data/

.DEFAULT_GOAL := help
