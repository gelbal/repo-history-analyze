# ABOUTME: Unit tests for SVN CSV writer module.
# ABOUTME: Tests CSV output for commits, aggregates, and contributor lifetimes.

import csv
from datetime import datetime, timezone
from pathlib import Path

import pytest

from repo_analyzer.svn.csv_writer import SVNCSVWriter
from repo_analyzer.svn.models import (
    ContributorStats,
    SVNCommitData,
    SVNRollingWindowAggregate,
    SVNWeeklyAggregate,
)


def make_commit(
    revision: int,
    author: str,
    date: datetime,
    props: list[str] = None,
) -> SVNCommitData:
    """Helper to create test commits."""
    return SVNCommitData(
        revision=revision,
        author=author,
        commit_date=date,
        message="Test commit",
        props=props or [],
    )


class TestSVNCSVWriterCommits:
    """Tests for writing SVN commits to CSV."""

    def test_write_commits_creates_file(self, tmp_path):
        """Creates CSV file at specified path."""
        output_path = tmp_path / "commits.csv"
        commits = [
            make_commit(100, "user1", datetime(2024, 1, 3, tzinfo=timezone.utc))
        ]

        SVNCSVWriter.write_commits(commits, output_path)

        assert output_path.exists()

    def test_write_commits_header(self, tmp_path):
        """CSV has correct header row."""
        output_path = tmp_path / "commits.csv"
        commits = [
            make_commit(100, "user1", datetime(2024, 1, 3, tzinfo=timezone.utc))
        ]

        SVNCSVWriter.write_commits(commits, output_path)

        with open(output_path) as f:
            reader = csv.reader(f)
            header = next(reader)

        assert "revision" in header
        assert "author" in header
        assert "commit_date" in header
        assert "props" in header

    def test_write_commits_data(self, tmp_path):
        """CSV contains commit data."""
        output_path = tmp_path / "commits.csv"
        commits = [
            make_commit(
                100, "user1",
                datetime(2024, 1, 3, 12, 0, 0, tzinfo=timezone.utc),
                props=["prop1", "prop2"]
            )
        ]

        SVNCSVWriter.write_commits(commits, output_path)

        with open(output_path) as f:
            reader = csv.DictReader(f)
            row = next(reader)

        assert row["revision"] == "100"
        assert row["author"] == "user1"
        assert "2024-01-03" in row["commit_date"]
        assert row["props"] == "prop1;prop2"

    def test_write_commits_empty_props(self, tmp_path):
        """CSV handles empty props list."""
        output_path = tmp_path / "commits.csv"
        commits = [
            make_commit(100, "user1", datetime(2024, 1, 3, tzinfo=timezone.utc), props=[])
        ]

        SVNCSVWriter.write_commits(commits, output_path)

        with open(output_path) as f:
            reader = csv.DictReader(f)
            row = next(reader)

        assert row["props"] == ""

    def test_write_commits_by_year(self, tmp_path):
        """Creates year folders with commits.csv."""
        commits = [
            make_commit(100, "user1", datetime(2023, 6, 15, tzinfo=timezone.utc)),
            make_commit(101, "user2", datetime(2024, 3, 20, tzinfo=timezone.utc)),
        ]

        SVNCSVWriter.write_commits_by_year(commits, tmp_path, "svn")

        assert (tmp_path / "svn" / "2023" / "commits.csv").exists()
        assert (tmp_path / "svn" / "2024" / "commits.csv").exists()


class TestSVNCSVWriterWeeklyAggregates:
    """Tests for writing weekly aggregates to CSV."""

    def test_write_weekly_aggregates_header(self, tmp_path):
        """CSV has correct header row."""
        output_path = tmp_path / "weekly.csv"
        aggregates = [
            SVNWeeklyAggregate(
                week_start=datetime(2024, 1, 1, tzinfo=timezone.utc),
                total_commits=10,
                unique_authors=3,
                unique_props_contributors=5,
            )
        ]

        SVNCSVWriter.write_weekly_aggregates(aggregates, output_path)

        with open(output_path) as f:
            reader = csv.reader(f)
            header = next(reader)

        assert "week_start" in header
        assert "total_commits" in header
        assert "unique_authors" in header
        assert "unique_props_contributors" in header

    def test_write_weekly_aggregates_data(self, tmp_path):
        """CSV contains aggregate data."""
        output_path = tmp_path / "weekly.csv"
        aggregates = [
            SVNWeeklyAggregate(
                week_start=datetime(2024, 1, 1, tzinfo=timezone.utc),
                total_commits=10,
                unique_authors=3,
                unique_props_contributors=5,
            )
        ]

        SVNCSVWriter.write_weekly_aggregates(aggregates, output_path)

        with open(output_path) as f:
            reader = csv.DictReader(f)
            row = next(reader)

        assert row["total_commits"] == "10"
        assert row["unique_authors"] == "3"
        assert row["unique_props_contributors"] == "5"


class TestSVNCSVWriterRollingAggregates:
    """Tests for writing rolling window aggregates to CSV."""

    def test_write_rolling_aggregates_header(self, tmp_path):
        """CSV has correct header row."""
        output_path = tmp_path / "rolling.csv"
        aggregates = [
            SVNRollingWindowAggregate(
                window_start=datetime(2024, 1, 1, tzinfo=timezone.utc),
                window_end=datetime(2024, 3, 24, tzinfo=timezone.utc),
                total_commits=100,
                unique_authors=20,
                unique_props_contributors=50,
            )
        ]

        SVNCSVWriter.write_rolling_aggregates(aggregates, output_path)

        with open(output_path) as f:
            reader = csv.reader(f)
            header = next(reader)

        assert "window_start" in header
        assert "window_end" in header
        assert "unique_props_contributors" in header


class TestSVNCSVWriterContributorStats:
    """Tests for writing contributor lifetime stats to CSV."""

    def test_write_contributor_stats_header(self, tmp_path):
        """CSV has correct header row."""
        output_path = tmp_path / "contributors.csv"
        stats = {
            "user1": ContributorStats(
                username="user1",
                first_contribution=datetime(2020, 1, 1, tzinfo=timezone.utc),
                latest_contribution=datetime(2024, 1, 1, tzinfo=timezone.utc),
                total_props_count=100,
            )
        }

        SVNCSVWriter.write_contributor_stats(stats, output_path)

        with open(output_path) as f:
            reader = csv.reader(f)
            header = next(reader)

        assert "username" in header
        assert "first_contribution" in header
        assert "latest_contribution" in header
        assert "total_props_count" in header
        assert "lifetime_days" in header

    def test_write_contributor_stats_data(self, tmp_path):
        """CSV contains contributor stats data."""
        output_path = tmp_path / "contributors.csv"
        stats = {
            "user1": ContributorStats(
                username="user1",
                first_contribution=datetime(2020, 1, 1, tzinfo=timezone.utc),
                latest_contribution=datetime(2024, 1, 1, tzinfo=timezone.utc),
                total_props_count=100,
            )
        }

        SVNCSVWriter.write_contributor_stats(stats, output_path)

        with open(output_path) as f:
            reader = csv.DictReader(f)
            row = next(reader)

        assert row["username"] == "user1"
        assert row["total_props_count"] == "100"
        assert row["lifetime_days"] == "1461"  # ~4 years

    def test_write_contributor_stats_sorted_by_count(self, tmp_path):
        """CSV sorts contributors by props count descending."""
        output_path = tmp_path / "contributors.csv"
        stats = {
            "low_user": ContributorStats(
                username="low_user",
                first_contribution=datetime(2024, 1, 1, tzinfo=timezone.utc),
                latest_contribution=datetime(2024, 1, 1, tzinfo=timezone.utc),
                total_props_count=5,
            ),
            "high_user": ContributorStats(
                username="high_user",
                first_contribution=datetime(2024, 1, 1, tzinfo=timezone.utc),
                latest_contribution=datetime(2024, 1, 1, tzinfo=timezone.utc),
                total_props_count=100,
            ),
        }

        SVNCSVWriter.write_contributor_stats(stats, output_path)

        with open(output_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert rows[0]["username"] == "high_user"
        assert rows[1]["username"] == "low_user"
