# ABOUTME: Command-line interface for git repository analysis.
# ABOUTME: Orchestrates the full pipeline: clone -> extract -> aggregate -> write CSVs.

import argparse
import logging
from datetime import datetime
from pathlib import Path
import sys

from .repository import GitRepository, WordPressRepository
from .version_mapper import VersionMapper
from .extractor import CommitExtractor
from .aggregator import WeeklyAggregator, RollingWindowAggregator
from .csv_writer import CSVWriter


def setup_logging():
    """Configure logging for the CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # Suppress verbose PyDriller logging
    logging.getLogger('pydriller').setLevel(logging.WARNING)


def parse_date(date_str: str) -> datetime:
    """Parse date string in YYYY-MM-DD format.

    Args:
        date_str: Date string to parse

    Returns:
        Datetime object with UTC timezone

    Raises:
        ValueError: If date string is invalid
    """
    try:
        # Parse as naive datetime
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        # Add UTC timezone
        return dt.replace(hour=0, minute=0, second=0, microsecond=0,
                         tzinfo=datetime.now().astimezone().tzinfo)
    except ValueError as e:
        raise ValueError(
            f"Invalid date format '{date_str}'. Expected YYYY-MM-DD."
        ) from e


def infer_repo_name_from_url(repo_url: str) -> str:
    """Infer repository name from URL.

    Args:
        repo_url: Git repository URL

    Returns:
        Repository name extracted from URL

    Examples:
        >>> infer_repo_name_from_url("https://github.com/torvalds/linux.git")
        'linux'
        >>> infer_repo_name_from_url("https://github.com/facebook/react")
        'react'
    """
    # Strip trailing slash
    url = repo_url.rstrip('/')

    # Get last path segment
    last_segment = url.split('/')[-1]

    # Strip .git extension if present
    if last_segment.endswith('.git'):
        last_segment = last_segment[:-4]

    return last_segment


def main():
    """Main entry point for git repository analysis."""
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(
        description="Analyze git repository history (defaults to WordPress as example)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze first 2 weeks of WordPress history (default)
  %(prog)s --since 2005-04-01 --to 2005-04-14

  # Analyze December 2024 WordPress
  %(prog)s --since 2024-12-01 --to 2024-12-31

  # Analyze a different repository
  %(prog)s --since 2024-01-01 --to 2024-12-31 \\
    --repo-url https://github.com/torvalds/linux.git

  # Custom output directory
  %(prog)s --since 2024-01-01 --to 2024-12-31 --output-dir ./my_data
        """
    )

    parser.add_argument(
        "--since",
        type=str,
        required=True,
        help="Start date (YYYY-MM-DD)",
        metavar="DATE"
    )

    parser.add_argument(
        "--to",
        type=str,
        required=True,
        help="End date (YYYY-MM-DD)",
        metavar="DATE"
    )

    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path("./cache"),
        help="Repository cache directory (default: ./cache)",
        metavar="DIR"
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./data"),
        help="Output directory for CSV files (default: ./data)",
        metavar="DIR"
    )

    parser.add_argument(
        "--repo-name",
        type=str,
        default=None,
        help="Repository name for output organization (default: inferred from URL or 'WordPress')",
        metavar="NAME"
    )

    parser.add_argument(
        "--repo-url",
        type=str,
        default=None,
        help="Git repository URL to analyze (default: WordPress repository)",
        metavar="URL"
    )

    args = parser.parse_args()

    try:
        # Parse dates
        logger.info("Parsing date range...")
        start_date = parse_date(args.since)
        end_date = parse_date(args.to)

        if start_date > end_date:
            logger.error("Start date must be before end date")
            sys.exit(1)

        logger.info(f"Date range: {args.since} to {args.to}")

        # Create directories
        args.cache_dir.mkdir(parents=True, exist_ok=True)
        args.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize repository
        if args.repo_url:
            # Custom repository URL provided
            if not args.repo_name:
                args.repo_name = infer_repo_name_from_url(args.repo_url)

            logger.info(f"Initializing repository from {args.repo_url}...")
            repo = GitRepository(args.repo_url, args.cache_dir, args.repo_name)
        else:
            # Default to WordPress for backward compatibility
            if not args.repo_name:
                args.repo_name = "WordPress"

            logger.info("Initializing WordPress repository...")
            repo = WordPressRepository(args.cache_dir)

        logger.info("Ensuring repository is cloned...")
        repo_path = repo.ensure_cloned()
        logger.info(f"Repository ready at: {repo_path}")

        # Initialize components
        logger.info("Initializing version mapper...")
        version_mapper = VersionMapper(str(repo_path))

        extractor = CommitExtractor(version_mapper)
        aggregator = WeeklyAggregator()

        # Traverse commits
        logger.info(f"Traversing commits from {args.since} to {args.to}...")
        commits = []
        commit_count = 0

        for pydriller_commit in repo.get_commits(since=start_date, to=end_date):
            commit_data = extractor.extract(pydriller_commit)
            commits.append(commit_data)
            commit_count += 1

            # Log progress every 1000 commits
            if commit_count % 1000 == 0:
                logger.info(f"Processed {commit_count} commits...")

        logger.info(f"Total commits processed: {commit_count}")

        if commit_count == 0:
            logger.warning("No commits found in the specified date range")
            logger.info("Creating empty CSV files...")

        # Aggregate commits
        logger.info("Aggregating commits by week...")
        aggregates = aggregator.aggregate(commits)
        logger.info(f"Created {len(aggregates)} weekly aggregates")

        # Create rolling window aggregates
        logger.info("Aggregating 12-week rolling windows...")
        rolling_aggregator = RollingWindowAggregator()
        rolling_windows = rolling_aggregator.aggregate(commits, aggregates)
        logger.info(f"Created {len(rolling_windows)} rolling window aggregates")

        # Write CSV files
        aggregates_path = args.output_dir / args.repo_name / "weekly_aggregates.csv"
        rolling_path = args.output_dir / args.repo_name / "rolling_window_aggregates.csv"

        logger.info("Writing commits grouped by year...")
        CSVWriter.write_commits_by_year(commits, args.output_dir, args.repo_name)

        logger.info(f"Writing combined weekly aggregates to {aggregates_path}...")
        CSVWriter.write_aggregates(aggregates, aggregates_path)

        logger.info(f"Writing 12-week rolling window aggregates to {rolling_path}...")
        CSVWriter.write_rolling_aggregates(rolling_windows, rolling_path)

        logger.info("Analysis complete!")
        logger.info(f"  Commits organized by year in: {args.output_dir}/{args.repo_name}/YYYY/commits.csv")
        logger.info(f"  Combined weekly aggregates: {aggregates_path}")
        logger.info(f"  12-week rolling window aggregates: {rolling_path}")

    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
