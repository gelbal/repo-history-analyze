.PHONY: setup analyze test test-all lint clean help notebook notebook-run export-charts

# Default notebook
NOTEBOOK ?= wordpress_code_evolution.py

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup:  ## Install dependencies (including viz extras)
	uv sync --all-groups --all-extras

analyze:  ## Run full SVN analysis (2003 through 2025)
	uv run python -m repo_analyzer.svn.cli --since 2003-04-01 --to 2025-12-31

test:  ## Run all tests (excluding slow E2E tests)
	uv run pytest -v -m "not slow"

test-all:  ## Run all tests including slow E2E tests
	uv run pytest -v

lint:  ## Run linters (ruff)
	uv run ruff check src/ tests/

notebook:  ## Launch Marimo notebook editor
	uv run marimo edit src/notebooks/$(NOTEBOOK)

notebook-run:  ## Run notebook in view mode
	uv run marimo run src/notebooks/$(NOTEBOOK)

export-charts:  ## Export all chart iterations as PNG
	@mkdir -p src/notebooks/plots
	uv run python -c "import sys; sys.path.insert(0, 'src/notebooks'); exec(open('src/notebooks/wordpress_code_evolution.py').read().split('# export_charts()')[0] + 'export_charts()')" 2>/dev/null || echo "Run 'make notebook' and uncomment export_charts() to export"

clean:  ## Remove cache and generated data
	rm -rf cache/ data/

.DEFAULT_GOAL := help
