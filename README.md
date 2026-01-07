# Git Repository History Analyzer

Analyzes git repository history and generates CSV reports with per-commit metadata and weekly aggregates. Uses WordPress as the default example, but works with any git repository.

## Quick Start (WordPress Example)

```bash
# Install dependencies
make setup

# Run full 20-year WordPress analysis (2005-2025)
make analyze

# Or analyze a specific date range
uv run python -m repo_analyzer --since 2024-01-01 --to 2024-12-31
```

## Analyzing Other Repositories

```bash
# Analyze Linux kernel
uv run python -m repo_analyzer \
  --since 2024-01-01 \
  --to 2024-12-31 \
  --repo-url https://github.com/torvalds/linux.git

# Analyze React with custom name
uv run python -m repo_analyzer \
  --since 2023-01-01 \
  --to 2023-12-31 \
  --repo-url https://github.com/facebook/react.git \
  --repo-name react-2023

# Analyze any repository with custom directories
uv run python -m repo_analyzer \
  --since 2024-01-01 \
  --to 2024-12-31 \
  --repo-url https://github.com/microsoft/vscode.git \
  --output-dir ./my_analysis \
  --cache-dir ./my_cache
```

## Usage

```bash
# Analyze specific date ranges (WordPress default)
uv run python -m repo_analyzer --since 2005-04-01 --to 2005-04-30

# Custom output directory
uv run python -m repo_analyzer \
  --since 2024-01-01 \
  --to 2024-12-31 \
  --output-dir ./my_analysis \
  --cache-dir ./my_cache
```

**Options:**
- `--since DATE` - Start date (YYYY-MM-DD, required)
- `--to DATE` - End date (YYYY-MM-DD, required)
- `--repo-url URL` - Git repository URL to analyze (default: WordPress repository)
- `--repo-name NAME` - Repository name for output organization (default: inferred from URL or 'WordPress')
- `--cache-dir DIR` - Repository cache directory (default: ./cache)
- `--output-dir DIR` - Output directory (default: ./data)

## Output Files

```
data/WordPress/
├── 2005/commits.csv                   # Per-commit data for 2005
├── 2006/commits.csv                   # Per-commit data for 2006
...
├── 2026/commits.csv                   # Per-commit data for 2026
├── weekly_aggregates.csv              # Weekly statistics (all years)
└── rolling_window_aggregates.csv      # 12-week rolling windows
```

**commits.csv** - Per-commit metadata:
- `hash`, `author_name`, `commit_date`, `lines_added`, `lines_deleted`, `version`

**weekly_aggregates.csv** - Weekly statistics (ISO calendar weeks):
- `week_start`, `total_commits`, `unique_authors`, `total_lines_added`, `total_lines_deleted`, `versions_released`

**rolling_window_aggregates.csv** - 12-week rolling window statistics:
- `window_start`, `window_end`, `total_commits`, `unique_authors`, `total_lines_added`, `total_lines_deleted`, `versions_released`
- Authors and versions deduplicated across entire 12-week period
- One row per week (overlapping windows)
- Windows at end of date range may contain < 12 weeks

## Development

```bash
# Run tests (excluding slow E2E tests)
make test

# Run all tests
make test-all

# Run linter
make lint

# Clean generated data
make clean

# Show all commands
make help
```

## Notes

- First run clones the specified repository (size and time varies by repository)
- Subsequent runs use cached repository
- Uses ISO 8601 week boundaries (Monday start)
- Version numbers extracted from git tags (numeric patterns only)
- WordPress repository (~500MB, 5-10 min for first clone)
