# WordPress SVN Repository Analyzer

Analyzes WordPress core SVN repository history and generates statistical reports. Tracks contributors via the `Props` tag in commit messages, line changes, and development activity over WordPress's 20+ year history.

## Features

- **Props Tracking**: Extract contributor credits from WordPress commit messages
- **Line Change Analysis**: Track additions, deletions, and net code growth
- **Rolling Windows**: 12-week (quarterly) aggregations for trend analysis
- **Diff Caching**: Efficient fetching with persistent cache for large analysis runs
- **Interactive Visualization**: Marimo notebook with iterative chart design

## Quick Start

```bash
# Install dependencies
make setup

# Run SVN analysis (2003-2025)
make analyze-svn

# Launch visualization notebook
make notebook NOTEBOOK=wordpress_code_evolution.py
```

## Visualization Notebook

The `wordpress_code_evolution.py` notebook demonstrates AI-assisted chart design through 6 iterations:

- **Iteration 0**: Raw weekly data (Plotly defaults)
- **Iteration 1**: Rolling data with Plotly defaults
- **Iteration 2**: Decluttered with semantic colors
- **Iteration 3**: WordPress brand colors + peak annotations
- **Iteration 4**: Three-panel layout with area fills
- **Iteration 5**: Full storytelling with milestones

```bash
# Edit notebook
make notebook NOTEBOOK=wordpress_code_evolution.py

# View notebook (read-only)
make notebook-run NOTEBOOK=wordpress_code_evolution.py

# Export charts
uv run marimo run src/notebooks/wordpress_code_evolution.py
# Then uncomment export_charts() in the notebook
```

## Output Files

```
data/svn/
├── commits/                      # Per-year commit data
│   ├── 2003/commits.csv
│   ├── 2004/commits.csv
│   └── ...
├── marimo/                       # Aggregated data for visualization
│   ├── weekly_stats.csv          # Weekly statistics
│   ├── rolling_12week_stats.csv  # 12-week rolling windows
│   └── contributor_lifetimes.csv # Contributor first/last activity
└── contributor_stats.csv         # All-time contributor statistics
```

### Data Schema

**weekly_stats.csv** - Per-week statistics:
- `date`, `year`, `week`, `total_commits`, `unique_authors`
- `unique_props_contributors`, `total_lines_added`, `total_lines_deleted`

**rolling_12week_stats.csv** - Quarterly rolling windows:
- Same fields, with contributors deduplicated across 12-week periods
- Smooths weekly noise to reveal sustained activity trends

## Development

```bash
# Run tests
make test

# Run all tests (including slow E2E)
make test-all

# Lint code
make lint

# Clean generated data
make clean
```

## Notes

- SVN diffs are cached to avoid repeated fetches
- First full run (2003-2025) fetches ~60K commits and their diffs
- Props tags follow WordPress convention: `Props @username, @username2.`
- Uses ISO 8601 week boundaries (Monday start)
