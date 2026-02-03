# ABOUTME: Command-line interface for WordPress SVN repository analysis.
# ABOUTME: Orchestrates pipeline: fetch SVN logs -> extract -> aggregate -> write CSVs.

import argparse
import logging
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import List, Optional

from repo_analyzer.svn.aggregator import (
    ContributorTracker,
    SVNRollingWindowAggregator,
    SVNWeeklyAggregator,
)
from repo_analyzer.svn.csv_writer import SVNCSVWriter
from repo_analyzer.svn.diff_cache import SVNDiffCache
from repo_analyzer.svn.diff_fetcher import SVNDiffFetcher
from repo_analyzer.svn.extractor import SVNExtractor
from repo_analyzer.svn.models import SVNCommitData
from repo_analyzer.svn.repository import SVNRepository, WordPressSVNRepository


def setup_logging() -> None:
    """Configure logging for the CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def parse_date(date_str: str) -> date:
    """Parse date string in YYYY-MM-DD format.

    Args:
        date_str: Date string to parse.

    Returns:
        Date object.

    Raises:
        ValueError: If date string is invalid.
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError(
            f"Invalid date format '{date_str}'. Expected YYYY-MM-DD."
        ) from e


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Command-line arguments (defaults to sys.argv).

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Analyze WordPress SVN repository history with Props contributor tracking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze Q1 2024
  %(prog)s --since 2024-01-01 --to 2024-03-31

  # Analyze full year 2023
  %(prog)s --since 2023-01-01 --to 2023-12-31

  # Custom output directory
  %(prog)s --since 2024-01-01 --to 2024-12-31 --output-dir ./my_data

  # Use core.svn instead of develop.svn
  %(prog)s --since 2024-01-01 --to 2024-12-31 \\
    --svn-url https://core.svn.wordpress.org/
        """,
    )

    parser.add_argument(
        "--since",
        type=str,
        required=True,
        help="Start date (YYYY-MM-DD)",
        metavar="DATE",
    )

    parser.add_argument(
        "--to",
        type=str,
        required=True,
        help="End date (YYYY-MM-DD)",
        metavar="DATE",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./data"),
        help="Output directory for CSV files (default: ./data)",
        metavar="DIR",
    )

    parser.add_argument(
        "--svn-url",
        type=str,
        default=None,
        help="SVN repository URL (default: develop.svn.wordpress.org)",
        metavar="URL",
    )

    parser.add_argument(
        "--fetch-diffs",
        action="store_true",
        help="Fetch diffs to calculate line changes per commit",
    )

    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path("./.cache"),
        help="Cache directory for diff stats (default: ./.cache)",
        metavar="DIR",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Number of diffs to fetch per batch (default: 50)",
        metavar="N",
    )

    parser.add_argument(
        "--parallel",
        type=int,
        default=4,
        help="Number of parallel workers for diff fetching (default: 4)",
        metavar="N",
    )

    return parser.parse_args(args)


def _fetch_and_enrich_commits(
    commits: List[SVNCommitData],
    repo: SVNRepository,
    cache_dir: Path,
    batch_size: int,
    workers: int,
    logger: logging.Logger,
) -> List[SVNCommitData]:
    """Fetch diffs and enrich commits with line change statistics.

    Args:
        commits: List of commits to enrich.
        repo: SVN repository instance.
        cache_dir: Directory for caching diff stats.
        batch_size: Number of diffs to fetch per batch.
        workers: Number of parallel workers.
        logger: Logger instance.

    Returns:
        List of enriched SVNCommitData with line stats populated.
    """
    # Initialize cache
    cache = SVNDiffCache(cache_dir, repo.url)
    cache.load()
    logger.info(f"Loaded diff cache with {cache.size} entries")

    # Initialize fetcher
    fetcher = SVNDiffFetcher(repo, cache)

    # Get all revision numbers
    revisions = [c.revision for c in commits]
    uncached = cache.get_uncached_revisions(revisions)

    logger.info(f"Total revisions: {len(revisions)}, uncached: {len(uncached)}")

    # Fetch uncached diffs in batches
    if uncached:
        total_batches = (len(uncached) + batch_size - 1) // batch_size

        def on_progress(completed: int, total: int) -> None:
            pct = (completed / total * 100) if total > 0 else 100
            logger.info(f"Fetching diffs: {completed}/{total} ({pct:.1f}%)")

        for batch_idx in range(total_batches):
            batch_start = batch_idx * batch_size
            batch_end = min(batch_start + batch_size, len(uncached))
            batch_revisions = uncached[batch_start:batch_end]

            logger.info(
                f"Batch {batch_idx + 1}/{total_batches}: "
                f"revisions {batch_revisions[0]}-{batch_revisions[-1]}"
            )

            fetcher.fetch_diffs_batch(
                batch_revisions,
                workers=workers,
                save_cache=True,
                on_progress=on_progress,
            )

    # Enrich commits with line stats
    enriched_commits = []
    for commit in commits:
        entry = cache.get(commit.revision)
        if entry is not None:
            enriched = SVNCommitData(
                revision=commit.revision,
                author=commit.author,
                commit_date=commit.commit_date,
                message=commit.message,
                props=commit.props,
                lines_added=entry.lines_added,
                lines_deleted=entry.lines_deleted,
            )
            enriched_commits.append(enriched)
        else:
            enriched_commits.append(commit)

    # Log summary
    with_lines = sum(1 for c in enriched_commits if c.lines_added is not None)
    logger.info(f"Enriched {with_lines}/{len(enriched_commits)} commits with line stats")

    return enriched_commits


def main() -> None:
    """Main entry point for WordPress SVN analysis."""
    setup_logging()
    logger = logging.getLogger(__name__)

    args = parse_args()

    try:
        # Parse dates
        logger.info("Parsing date range...")
        start_date = parse_date(args.since)
        end_date = parse_date(args.to)

        if start_date > end_date:
            logger.error("Start date must be before end date")
            sys.exit(1)

        logger.info(f"Date range: {args.since} to {args.to}")

        # Create output directory
        args.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize repository
        if args.svn_url:
            logger.info(f"Using custom SVN URL: {args.svn_url}")
            repo = SVNRepository(args.svn_url)
        else:
            logger.info("Using WordPress develop SVN repository...")
            repo = WordPressSVNRepository()

        # Check SVN is available
        if not repo.check_svn_available():
            logger.error("SVN command not found. Please install Subversion.")
            logger.error("  macOS: brew install svn")
            logger.error("  Ubuntu: apt-get install subversion")
            sys.exit(1)

        # Fetch commit logs
        logger.info(f"Fetching commits from SVN ({start_date} to {end_date})...")
        xml_content = repo.fetch_commits_xml(start_date, end_date)

        # Parse commits
        logger.info("Parsing commit data...")
        extractor = SVNExtractor()
        commits = extractor.parse_commits_xml(xml_content)
        logger.info(f"Found {len(commits)} commits")

        if not commits:
            logger.warning("No commits found in the specified date range")

        # Fetch diffs if requested
        if args.fetch_diffs and commits:
            logger.info("Fetching diffs for line change analysis...")
            commits = _fetch_and_enrich_commits(
                commits=commits,
                repo=repo,
                cache_dir=args.cache_dir,
                batch_size=args.batch_size,
                workers=args.parallel,
                logger=logger,
            )

        # Aggregate weekly stats
        logger.info("Aggregating commits by week...")
        weekly_aggregator = SVNWeeklyAggregator()
        weekly_aggregates = weekly_aggregator.aggregate(commits)
        logger.info(f"Created {len(weekly_aggregates)} weekly aggregates")

        # Create rolling window aggregates
        logger.info("Creating 12-week rolling window aggregates...")
        rolling_aggregator = SVNRollingWindowAggregator()
        rolling_windows = rolling_aggregator.aggregate(commits, weekly_aggregates)
        logger.info(f"Created {len(rolling_windows)} rolling window aggregates")

        # Track contributor lifetimes
        logger.info("Tracking contributor lifetimes...")
        cutoff = datetime(
            end_date.year, end_date.month, end_date.day,
            23, 59, 59, tzinfo=timezone.utc
        )
        contributor_tracker = ContributorTracker()
        contributor_stats = contributor_tracker.track(commits, cutoff)
        logger.info(f"Tracked {len(contributor_stats)} unique Props contributors")

        # Count unique Props across all commits
        all_props = set()
        for commit in commits:
            all_props.update(commit.props)
        logger.info(f"Unique Props contributors total: {len(all_props)}")

        # Write CSV files
        svn_output_dir = args.output_dir / "svn"
        svn_output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Writing commits grouped by year...")
        SVNCSVWriter.write_commits_by_year(commits, args.output_dir, "svn")

        weekly_path = svn_output_dir / "weekly_aggregates.csv"
        logger.info(f"Writing weekly aggregates to {weekly_path}...")
        SVNCSVWriter.write_weekly_aggregates(weekly_aggregates, weekly_path)

        rolling_path = svn_output_dir / "rolling_window_aggregates.csv"
        logger.info(f"Writing rolling window aggregates to {rolling_path}...")
        SVNCSVWriter.write_rolling_aggregates(rolling_windows, rolling_path)

        contributors_path = svn_output_dir / "contributor_lifetimes.csv"
        logger.info(f"Writing contributor lifetimes to {contributors_path}...")
        SVNCSVWriter.write_contributor_stats(contributor_stats, contributors_path)

        # Write notebook-friendly CSV files (simpler date format, year/week columns)
        # These are written to src/notebooks/data/ for use by Marimo notebooks
        notebook_data_dir = Path(__file__).parent.parent.parent / "notebooks" / "data"
        notebook_data_dir.mkdir(parents=True, exist_ok=True)

        weekly_notebook_path = notebook_data_dir / "weekly_stats.csv"
        logger.info(f"Writing notebook-friendly weekly stats to {weekly_notebook_path}...")
        SVNCSVWriter.write_weekly_aggregates_marimo(weekly_aggregates, weekly_notebook_path)

        rolling_notebook_path = notebook_data_dir / "rolling_12week_stats.csv"
        logger.info(f"Writing notebook-friendly rolling window stats to {rolling_notebook_path}...")
        SVNCSVWriter.write_rolling_aggregates_marimo(rolling_windows, rolling_notebook_path)

        logger.info("Analysis complete!")
        logger.info(f"  Commits by year: {args.output_dir}/svn/YYYY/commits.csv")
        logger.info(f"  Weekly aggregates: {weekly_path}")
        logger.info(f"  Rolling windows: {rolling_path}")
        logger.info(f"  Contributor lifetimes: {contributors_path}")
        logger.info(f"  Notebook data: {notebook_data_dir}/")

    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        sys.exit(1)
    except RuntimeError as e:
        logger.error(f"SVN error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
