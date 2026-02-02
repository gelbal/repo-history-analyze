# ABOUTME: Unit tests for SVN aggregator module.
# ABOUTME: Tests weekly and rolling window aggregation with props contributor tracking.

from datetime import datetime, timezone, timedelta

import pytest

from repo_analyzer.svn.aggregator import (
    SVNWeeklyAggregator,
    SVNRollingWindowAggregator,
    ContributorTracker,
)
from repo_analyzer.svn.models import SVNCommitData, ContributorStats


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


class TestSVNWeeklyAggregator:
    """Tests for SVNWeeklyAggregator class."""

    def test_aggregate_empty_commits(self):
        """Returns empty list for no commits."""
        aggregator = SVNWeeklyAggregator()
        result = aggregator.aggregate([])
        assert result == []

    def test_aggregate_single_commit(self):
        """Aggregates single commit into one week."""
        aggregator = SVNWeeklyAggregator()
        commits = [
            make_commit(
                100,
                "user1",
                datetime(2024, 1, 3, 12, 0, 0, tzinfo=timezone.utc),
                props=["prop1", "prop2"],
            )
        ]

        result = aggregator.aggregate(commits)

        assert len(result) == 1
        assert result[0].total_commits == 1
        assert result[0].unique_authors == 1
        assert result[0].unique_props_contributors == 2

    def test_aggregate_multiple_commits_same_week(self):
        """Aggregates commits in same week with deduplication."""
        aggregator = SVNWeeklyAggregator()
        commits = [
            make_commit(
                100, "user1",
                datetime(2024, 1, 3, tzinfo=timezone.utc),
                props=["prop1", "prop2"]
            ),
            make_commit(
                101, "user1",
                datetime(2024, 1, 4, tzinfo=timezone.utc),
                props=["prop2", "prop3"]
            ),
            make_commit(
                102, "user2",
                datetime(2024, 1, 5, tzinfo=timezone.utc),
                props=["prop1"]
            ),
        ]

        result = aggregator.aggregate(commits)

        assert len(result) == 1
        assert result[0].total_commits == 3
        assert result[0].unique_authors == 2  # user1, user2
        assert result[0].unique_props_contributors == 3  # prop1, prop2, prop3

    def test_aggregate_multiple_weeks(self):
        """Aggregates commits across multiple weeks."""
        aggregator = SVNWeeklyAggregator()
        commits = [
            make_commit(
                100, "user1",
                datetime(2024, 1, 3, tzinfo=timezone.utc),  # Week 1
                props=["prop1"]
            ),
            make_commit(
                101, "user2",
                datetime(2024, 1, 10, tzinfo=timezone.utc),  # Week 2
                props=["prop2"]
            ),
        ]

        result = aggregator.aggregate(commits)

        assert len(result) == 2
        assert result[0].week_start < result[1].week_start

    def test_week_start_is_monday(self):
        """Week start is Monday UTC midnight."""
        aggregator = SVNWeeklyAggregator()
        # Wednesday January 3, 2024
        commits = [
            make_commit(100, "user1", datetime(2024, 1, 3, tzinfo=timezone.utc))
        ]

        result = aggregator.aggregate(commits)

        # Monday of that week is January 1, 2024
        assert result[0].week_start == datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


class TestSVNRollingWindowAggregator:
    """Tests for SVNRollingWindowAggregator class."""

    def test_rolling_window_empty(self):
        """Returns empty list for no aggregates."""
        aggregator = SVNRollingWindowAggregator()
        result = aggregator.aggregate([], [])
        assert result == []

    def test_rolling_window_single_week(self):
        """Creates window from single week."""
        aggregator = SVNRollingWindowAggregator()
        commits = [
            make_commit(
                100, "user1",
                datetime(2024, 1, 3, tzinfo=timezone.utc),
                props=["prop1"]
            )
        ]

        weekly_agg = SVNWeeklyAggregator()
        weekly_results = weekly_agg.aggregate(commits)
        result = aggregator.aggregate(commits, weekly_results)

        assert len(result) == 1
        assert result[0].unique_props_contributors == 1

    def test_rolling_window_12_weeks(self):
        """Creates proper 12-week rolling windows."""
        aggregator = SVNRollingWindowAggregator()

        # Create commits across 14 weeks
        commits = []
        base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        for week in range(14):
            commit_date = base_date + timedelta(weeks=week)
            commits.append(
                make_commit(
                    100 + week,
                    f"user{week}",
                    commit_date,
                    props=[f"prop{week}"]
                )
            )

        weekly_agg = SVNWeeklyAggregator()
        weekly_results = weekly_agg.aggregate(commits)
        result = aggregator.aggregate(commits, weekly_results)

        # Should have 14 rolling windows
        assert len(result) == 14

        # First window should have 12 props contributors
        assert result[0].unique_props_contributors == 12

        # Last window should have 1 props contributor
        assert result[-1].unique_props_contributors == 1

    def test_rolling_window_deduplicates_props(self):
        """Deduplicates props contributors across window."""
        aggregator = SVNRollingWindowAggregator()

        # Same prop across multiple weeks
        commits = [
            make_commit(
                100, "user1",
                datetime(2024, 1, 3, tzinfo=timezone.utc),
                props=["shared_prop", "unique1"]
            ),
            make_commit(
                101, "user2",
                datetime(2024, 1, 10, tzinfo=timezone.utc),
                props=["shared_prop", "unique2"]
            ),
        ]

        weekly_agg = SVNWeeklyAggregator()
        weekly_results = weekly_agg.aggregate(commits)
        result = aggregator.aggregate(commits, weekly_results)

        # First window includes both weeks
        # unique props: shared_prop, unique1, unique2 = 3
        assert result[0].unique_props_contributors == 3


class TestContributorTracker:
    """Tests for ContributorTracker class."""

    def test_track_empty_commits(self):
        """Returns empty dict for no commits."""
        tracker = ContributorTracker()
        result = tracker.track([], datetime(2024, 1, 1, tzinfo=timezone.utc))
        assert result == {}

    def test_track_single_contributor(self):
        """Tracks single contributor lifetime."""
        tracker = ContributorTracker()
        commits = [
            make_commit(
                100, "author",
                datetime(2024, 1, 3, tzinfo=timezone.utc),
                props=["contributor1"]
            ),
            make_commit(
                200, "author",
                datetime(2024, 6, 15, tzinfo=timezone.utc),
                props=["contributor1"]
            ),
        ]

        result = tracker.track(commits, datetime(2024, 6, 15, tzinfo=timezone.utc))

        assert "contributor1" in result
        stats = result["contributor1"]
        assert stats.username == "contributor1"
        assert stats.first_contribution == datetime(2024, 1, 3, tzinfo=timezone.utc)
        assert stats.latest_contribution == datetime(2024, 6, 15, tzinfo=timezone.utc)
        assert stats.total_props_count == 2
        assert stats.lifetime_days > 0

    def test_track_multiple_contributors(self):
        """Tracks multiple contributors."""
        tracker = ContributorTracker()
        commits = [
            make_commit(
                100, "author",
                datetime(2024, 1, 3, tzinfo=timezone.utc),
                props=["user1", "user2"]
            ),
            make_commit(
                101, "author",
                datetime(2024, 1, 10, tzinfo=timezone.utc),
                props=["user2", "user3"]
            ),
        ]

        result = tracker.track(commits, datetime(2024, 1, 10, tzinfo=timezone.utc))

        assert len(result) == 3
        assert result["user1"].total_props_count == 1
        assert result["user2"].total_props_count == 2
        assert result["user3"].total_props_count == 1

    def test_track_contributor_lifetime(self):
        """Calculates correct lifetime in days."""
        tracker = ContributorTracker()
        commits = [
            make_commit(
                100, "author",
                datetime(2024, 1, 1, tzinfo=timezone.utc),
                props=["user1"]
            ),
            make_commit(
                200, "author",
                datetime(2024, 1, 31, tzinfo=timezone.utc),
                props=["user1"]
            ),
        ]

        result = tracker.track(commits, datetime(2024, 1, 31, tzinfo=timezone.utc))

        # 30 days between Jan 1 and Jan 31
        assert result["user1"].lifetime_days == 30

    def test_track_filters_by_cutoff_date(self):
        """Only includes contributions before cutoff date."""
        tracker = ContributorTracker()
        commits = [
            make_commit(
                100, "author",
                datetime(2024, 1, 1, tzinfo=timezone.utc),
                props=["user1"]
            ),
            make_commit(
                200, "author",
                datetime(2024, 6, 1, tzinfo=timezone.utc),
                props=["user1"]
            ),
        ]

        # Cutoff before second commit
        result = tracker.track(commits, datetime(2024, 3, 1, tzinfo=timezone.utc))

        assert result["user1"].total_props_count == 1
        assert result["user1"].latest_contribution == datetime(2024, 1, 1, tzinfo=timezone.utc)
