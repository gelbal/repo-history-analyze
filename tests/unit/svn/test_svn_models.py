# ABOUTME: Unit tests for SVN data models.
# ABOUTME: Tests SVNCommitData and ContributorStats dataclasses.

from datetime import datetime, timezone

import pytest

from repo_analyzer.svn.models import ContributorStats, SVNCommitData


class TestSVNCommitData:
    """Tests for SVNCommitData dataclass."""

    def test_create_commit_with_props(self):
        """SVNCommitData stores revision, author, date, message, and props."""
        commit = SVNCommitData(
            revision=59000,
            author="peterwilsoncc",
            commit_date=datetime(2024, 1, 17, 0, 12, 26, tzinfo=timezone.utc),
            message="Options/Meta APIs: Document type juggling.",
            props=["sukhendu2002", "azaozz", "jrf"],
        )

        assert commit.revision == 59000
        assert commit.author == "peterwilsoncc"
        assert commit.commit_date.year == 2024
        assert commit.message == "Options/Meta APIs: Document type juggling."
        assert commit.props == ["sukhendu2002", "azaozz", "jrf"]

    def test_create_commit_without_props(self):
        """SVNCommitData handles commits with no props."""
        commit = SVNCommitData(
            revision=57235,
            author="pento",
            commit_date=datetime(2024, 1, 1, 0, 0, 37, tzinfo=timezone.utc),
            message="Happy New Year!",
            props=[],
        )

        assert commit.revision == 57235
        assert commit.props == []

    def test_commit_stores_lines_placeholders(self):
        """SVNCommitData stores lines_added and lines_deleted for future use."""
        commit = SVNCommitData(
            revision=59000,
            author="peterwilsoncc",
            commit_date=datetime(2024, 1, 17, tzinfo=timezone.utc),
            message="Test",
            props=[],
            lines_added=100,
            lines_deleted=50,
        )

        assert commit.lines_added == 100
        assert commit.lines_deleted == 50

    def test_commit_lines_default_to_none(self):
        """SVNCommitData lines default to None when not provided."""
        commit = SVNCommitData(
            revision=59000,
            author="peterwilsoncc",
            commit_date=datetime(2024, 1, 17, tzinfo=timezone.utc),
            message="Test",
            props=[],
        )

        assert commit.lines_added is None
        assert commit.lines_deleted is None


class TestContributorStats:
    """Tests for ContributorStats dataclass."""

    def test_create_contributor_stats(self):
        """ContributorStats tracks contributor lifetime metrics."""
        stats = ContributorStats(
            username="mukesh27",
            first_contribution=datetime(2020, 3, 15, tzinfo=timezone.utc),
            latest_contribution=datetime(2024, 1, 6, tzinfo=timezone.utc),
            total_props_count=150,
        )

        assert stats.username == "mukesh27"
        assert stats.first_contribution.year == 2020
        assert stats.latest_contribution.year == 2024
        assert stats.total_props_count == 150

    def test_contributor_stats_lifetime_days(self):
        """ContributorStats calculates lifetime in days."""
        stats = ContributorStats(
            username="mukesh27",
            first_contribution=datetime(2020, 1, 1, tzinfo=timezone.utc),
            latest_contribution=datetime(2024, 1, 1, tzinfo=timezone.utc),
            total_props_count=100,
        )

        # 4 years = 1461 days (includes leap year)
        assert stats.lifetime_days == 1461

    def test_contributor_stats_single_contribution(self):
        """ContributorStats handles single contribution (lifetime = 0)."""
        date = datetime(2024, 1, 15, tzinfo=timezone.utc)
        stats = ContributorStats(
            username="newuser",
            first_contribution=date,
            latest_contribution=date,
            total_props_count=1,
        )

        assert stats.lifetime_days == 0
