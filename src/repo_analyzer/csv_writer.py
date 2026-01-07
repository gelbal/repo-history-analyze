# ABOUTME: Writes CommitData, WeeklyAggregate, and RollingWindowAggregate objects to CSV files.
# ABOUTME: Handles UTF-8 encoding, ISO 8601 dates, and semicolon-separated version lists.

import csv
from pathlib import Path
from typing import List, Dict
from collections import defaultdict

from .models import CommitData, WeeklyAggregate, RollingWindowAggregate


class CSVWriter:
    """Writes analysis results to CSV files."""

    @staticmethod
    def write_commits(commits: List[CommitData], output_path: Path) -> None:
        """Write per-commit data to commits.csv.

        Args:
            commits: List of CommitData objects to write
            output_path: Path to output CSV file
        """
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = [
                'hash',
                'author_name',
                'commit_date',
                'lines_added',
                'lines_deleted',
                'version'
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for commit in commits:
                writer.writerow({
                    'hash': commit.hash,
                    'author_name': commit.author_name,
                    'commit_date': commit.commit_date.isoformat(),
                    'lines_added': commit.lines_added,
                    'lines_deleted': commit.lines_deleted,
                    'version': commit.version if commit.version is not None else ''
                })

    @staticmethod
    def write_aggregates(aggregates: List[WeeklyAggregate],
                        output_path: Path) -> None:
        """Write weekly aggregates to weekly_aggregates.csv.

        Args:
            aggregates: List of WeeklyAggregate objects to write
            output_path: Path to output CSV file
        """
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = [
                'week_start',
                'total_commits',
                'unique_authors',
                'total_lines_added',
                'total_lines_deleted',
                'versions_released'
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for aggregate in aggregates:
                # Join versions list with semicolon separator
                versions_str = ';'.join(aggregate.versions_released)

                writer.writerow({
                    'week_start': aggregate.week_start.isoformat(),
                    'total_commits': aggregate.total_commits,
                    'unique_authors': aggregate.unique_authors,
                    'total_lines_added': aggregate.total_lines_added,
                    'total_lines_deleted': aggregate.total_lines_deleted,
                    'versions_released': versions_str
                })

    @staticmethod
    def write_commits_by_year(commits: List[CommitData], base_output_dir: Path, repo_name: str) -> None:
        """Write commits grouped by year into separate folders.

        Args:
            commits: List of all CommitData objects
            base_output_dir: Base directory (e.g., 'data/')
            repo_name: Repository name for output organization (e.g., 'WordPress')

        Creates structure:
            base_output_dir/repo_name/YYYY/commits.csv
        """
        if not commits:
            return

        # Group commits by year
        yearly_commits: Dict[int, List[CommitData]] = defaultdict(list)

        for commit in commits:
            year = commit.commit_date.year
            yearly_commits[year].append(commit)

        # Write each year's commits to its own file
        for year, year_commits in yearly_commits.items():
            # Create directory path: base_output_dir/repo_name/YYYY/
            year_dir = base_output_dir / repo_name / str(year)
            year_dir.mkdir(parents=True, exist_ok=True)

            # Write commits.csv for this year
            commits_path = year_dir / "commits.csv"
            CSVWriter.write_commits(year_commits, commits_path)

    @staticmethod
    def write_rolling_aggregates(
        rolling_aggregates: List[RollingWindowAggregate],
        output_path: Path
    ) -> None:
        """Write 12-week rolling window aggregates to CSV.

        Args:
            rolling_aggregates: List of RollingWindowAggregate objects to write
            output_path: Path to output CSV file
        """
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            fieldnames = [
                'window_start',
                'window_end',
                'total_commits',
                'unique_authors',
                'total_lines_added',
                'total_lines_deleted',
                'versions_released'
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for aggregate in rolling_aggregates:
                # Join versions list with semicolon separator
                versions_str = ';'.join(aggregate.versions_released)

                writer.writerow({
                    'window_start': aggregate.window_start.isoformat(),
                    'window_end': aggregate.window_end.isoformat(),
                    'total_commits': aggregate.total_commits,
                    'unique_authors': aggregate.unique_authors,
                    'total_lines_added': aggregate.total_lines_added,
                    'total_lines_deleted': aggregate.total_lines_deleted,
                    'versions_released': versions_str
                })
