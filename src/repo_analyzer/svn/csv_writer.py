# ABOUTME: Writes SVN commit data, aggregates, and contributor stats to CSV files.
# ABOUTME: Outputs to data/svn/ folder structure with UTF-8 encoding.

import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from repo_analyzer.svn.models import (
    ContributorStats,
    SVNCommitData,
    SVNRollingWindowAggregate,
    SVNWeeklyAggregate,
)


class SVNCSVWriter:
    """Writes SVN analysis results to CSV files."""

    @staticmethod
    def write_commits(commits: List[SVNCommitData], output_path: Path) -> None:
        """Write per-commit data to commits.csv.

        Args:
            commits: List of SVNCommitData objects to write.
            output_path: Path to output CSV file.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            fieldnames = [
                "revision",
                "author",
                "commit_date",
                "props",
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for commit in commits:
                props_str = ";".join(commit.props)

                writer.writerow({
                    "revision": commit.revision,
                    "author": commit.author,
                    "commit_date": commit.commit_date.isoformat(),
                    "props": props_str,
                })

    @staticmethod
    def write_commits_by_year(
        commits: List[SVNCommitData],
        base_output_dir: Path,
        folder_name: str,
    ) -> None:
        """Write commits grouped by year into separate folders.

        Args:
            commits: List of all SVNCommitData objects.
            base_output_dir: Base directory (e.g., 'data/').
            folder_name: Folder name for output organization (e.g., 'svn').

        Creates structure:
            base_output_dir/folder_name/YYYY/commits.csv
        """
        if not commits:
            return

        # Group commits by year
        yearly_commits: Dict[int, List[SVNCommitData]] = defaultdict(list)

        for commit in commits:
            year = commit.commit_date.year
            yearly_commits[year].append(commit)

        # Write each year's commits to its own file
        for year, year_commits in yearly_commits.items():
            year_dir = base_output_dir / folder_name / str(year)
            year_dir.mkdir(parents=True, exist_ok=True)

            commits_path = year_dir / "commits.csv"
            SVNCSVWriter.write_commits(year_commits, commits_path)

    @staticmethod
    def write_weekly_aggregates(
        aggregates: List[SVNWeeklyAggregate],
        output_path: Path,
    ) -> None:
        """Write weekly aggregates to CSV.

        Args:
            aggregates: List of SVNWeeklyAggregate objects to write.
            output_path: Path to output CSV file.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            fieldnames = [
                "week_start",
                "total_commits",
                "unique_authors",
                "unique_props_contributors",
                "total_lines_added",
                "total_lines_deleted",
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for aggregate in aggregates:
                writer.writerow({
                    "week_start": aggregate.week_start.isoformat(),
                    "total_commits": aggregate.total_commits,
                    "unique_authors": aggregate.unique_authors,
                    "unique_props_contributors": aggregate.unique_props_contributors,
                    "total_lines_added": aggregate.total_lines_added,
                    "total_lines_deleted": aggregate.total_lines_deleted,
                })

    @staticmethod
    def write_rolling_aggregates(
        aggregates: List[SVNRollingWindowAggregate],
        output_path: Path,
    ) -> None:
        """Write 12-week rolling window aggregates to CSV.

        Args:
            aggregates: List of SVNRollingWindowAggregate objects to write.
            output_path: Path to output CSV file.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            fieldnames = [
                "window_start",
                "window_end",
                "total_commits",
                "unique_authors",
                "unique_props_contributors",
                "total_lines_added",
                "total_lines_deleted",
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for aggregate in aggregates:
                writer.writerow({
                    "window_start": aggregate.window_start.isoformat(),
                    "window_end": aggregate.window_end.isoformat(),
                    "total_commits": aggregate.total_commits,
                    "unique_authors": aggregate.unique_authors,
                    "unique_props_contributors": aggregate.unique_props_contributors,
                    "total_lines_added": aggregate.total_lines_added,
                    "total_lines_deleted": aggregate.total_lines_deleted,
                })

    @staticmethod
    def write_contributor_stats(
        stats: Dict[str, ContributorStats],
        output_path: Path,
    ) -> None:
        """Write contributor lifetime statistics to CSV.

        Contributors are sorted by total_props_count descending.

        Args:
            stats: Dictionary mapping username to ContributorStats.
            output_path: Path to output CSV file.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Sort by props count descending
        sorted_contributors = sorted(
            stats.values(),
            key=lambda x: x.total_props_count,
            reverse=True,
        )

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            fieldnames = [
                "username",
                "first_contribution",
                "latest_contribution",
                "total_props_count",
                "lifetime_days",
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for contributor in sorted_contributors:
                writer.writerow({
                    "username": contributor.username,
                    "first_contribution": contributor.first_contribution.isoformat(),
                    "latest_contribution": contributor.latest_contribution.isoformat(),
                    "total_props_count": contributor.total_props_count,
                    "lifetime_days": contributor.lifetime_days,
                })

    @staticmethod
    def write_rolling_aggregates_marimo(
        aggregates: List[SVNRollingWindowAggregate],
        output_path: Path,
    ) -> None:
        """Write 12-week rolling window aggregates in marimo-friendly format.

        Uses simple date format (YYYY-MM-DD) and includes year/week columns
        for easy filtering and plotting in marimo notebooks.

        Args:
            aggregates: List of SVNRollingWindowAggregate objects to write.
            output_path: Path to output CSV file.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            fieldnames = [
                "date",
                "year",
                "week",
                "total_commits",
                "unique_authors",
                "unique_props_contributors",
                "total_lines_added",
                "total_lines_deleted",
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for aggregate in aggregates:
                iso_cal = aggregate.window_start.isocalendar()
                writer.writerow({
                    "date": aggregate.window_start.strftime("%Y-%m-%d"),
                    "year": iso_cal.year,
                    "week": iso_cal.week,
                    "total_commits": aggregate.total_commits,
                    "unique_authors": aggregate.unique_authors,
                    "unique_props_contributors": aggregate.unique_props_contributors,
                    "total_lines_added": aggregate.total_lines_added,
                    "total_lines_deleted": aggregate.total_lines_deleted,
                })

    @staticmethod
    def write_weekly_aggregates_marimo(
        aggregates: List[SVNWeeklyAggregate],
        output_path: Path,
    ) -> None:
        """Write weekly aggregates in marimo-friendly format.

        Uses simple date format (YYYY-MM-DD) and includes year/week columns.

        Args:
            aggregates: List of SVNWeeklyAggregate objects to write.
            output_path: Path to output CSV file.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            fieldnames = [
                "date",
                "year",
                "week",
                "total_commits",
                "unique_authors",
                "unique_props_contributors",
                "total_lines_added",
                "total_lines_deleted",
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for aggregate in aggregates:
                iso_cal = aggregate.week_start.isocalendar()
                writer.writerow({
                    "date": aggregate.week_start.strftime("%Y-%m-%d"),
                    "year": iso_cal.year,
                    "week": iso_cal.week,
                    "total_commits": aggregate.total_commits,
                    "unique_authors": aggregate.unique_authors,
                    "unique_props_contributors": aggregate.unique_props_contributors,
                    "total_lines_added": aggregate.total_lines_added,
                    "total_lines_deleted": aggregate.total_lines_deleted,
                })

    @staticmethod
    def write_contributor_stats_marimo(
        stats: Dict[str, ContributorStats],
        output_path: Path,
    ) -> None:
        """Write contributor lifetime statistics in marimo-friendly format.

        Uses simple date format and includes years_active column.

        Args:
            stats: Dictionary mapping username to ContributorStats.
            output_path: Path to output CSV file.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        sorted_contributors = sorted(
            stats.values(),
            key=lambda x: x.total_props_count,
            reverse=True,
        )

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            fieldnames = [
                "username",
                "first_contribution_date",
                "latest_contribution_date",
                "total_props_count",
                "lifetime_days",
                "years_active",
            ]

            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for contributor in sorted_contributors:
                years_active = round(contributor.lifetime_days / 365.25, 1)
                writer.writerow({
                    "username": contributor.username,
                    "first_contribution_date": contributor.first_contribution.strftime("%Y-%m-%d"),
                    "latest_contribution_date": contributor.latest_contribution.strftime("%Y-%m-%d"),
                    "total_props_count": contributor.total_props_count,
                    "lifetime_days": contributor.lifetime_days,
                    "years_active": years_active,
                })
