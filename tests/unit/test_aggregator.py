# ABOUTME: Unit tests for WeeklyAggregator class.
# ABOUTME: Tests ISO week calculation, commit grouping, and aggregation logic.

import pytest
from datetime import datetime, timezone


def test_aggregate_single_week(sample_commits):
    """Test aggregating commits from a single week."""
    from repo_analyzer.aggregator import WeeklyAggregator
    from repo_analyzer.models import CommitData

    # Create commits all in the same week (April 4-10, 2005)
    commits = [
        CommitData(
            hash="abc123",
            author_name="John Doe",
            commit_date=datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=42,
            lines_deleted=7,
            version="1.5"
        ),
        CommitData(
            hash="def456",
            author_name="Jane Smith",
            commit_date=datetime(2005, 4, 6, 14, 30, 0, tzinfo=timezone.utc),
            lines_added=128,
            lines_deleted=3,
            version=None
        ),
        CommitData(
            hash="ghi789",
            author_name="John Doe",
            commit_date=datetime(2005, 4, 7, 9, 15, 0, tzinfo=timezone.utc),
            lines_added=64,
            lines_deleted=12,
            version=None
        ),
    ]

    aggregator = WeeklyAggregator()
    result = aggregator.aggregate(commits)

    assert len(result) == 1
    aggregate = result[0]

    # Week starting Monday, April 4, 2005
    assert aggregate.week_start == datetime(2005, 4, 4, 0, 0, 0, tzinfo=timezone.utc)
    assert aggregate.total_commits == 3
    assert aggregate.unique_authors == 2  # John Doe and Jane Smith
    assert aggregate.total_lines_added == 234  # 42 + 128 + 64
    assert aggregate.total_lines_deleted == 22  # 7 + 3 + 12
    assert aggregate.versions_released == ["1.5"]


def test_aggregate_multiple_weeks(sample_commits):
    """Test aggregating commits spanning multiple weeks."""
    from repo_analyzer.aggregator import WeeklyAggregator

    aggregator = WeeklyAggregator()
    result = aggregator.aggregate(sample_commits)

    # sample_commits spans 2 weeks: April 4-10 and April 11-17, 2005
    assert len(result) == 2

    # First week (April 4-10)
    week1 = result[0]
    assert week1.week_start == datetime(2005, 4, 4, 0, 0, 0, tzinfo=timezone.utc)
    assert week1.total_commits == 2
    assert week1.unique_authors == 2  # John Doe and Jane Smith
    assert week1.total_lines_added == 170  # 42 + 128
    assert week1.total_lines_deleted == 10  # 7 + 3
    assert week1.versions_released == ["1.5"]

    # Second week (April 11-17)
    week2 = result[1]
    assert week2.week_start == datetime(2005, 4, 11, 0, 0, 0, tzinfo=timezone.utc)
    assert week2.total_commits == 2
    assert week2.unique_authors == 2  # John Doe and Alice Johnson
    assert week2.total_lines_added == 155  # 64 + 91
    assert week2.total_lines_deleted == 37  # 12 + 25
    assert week2.versions_released == ["1.5.1"]


def test_aggregate_empty_list():
    """Test aggregating an empty commit list."""
    from repo_analyzer.aggregator import WeeklyAggregator

    aggregator = WeeklyAggregator()
    result = aggregator.aggregate([])

    assert result == []


def test_aggregate_week_boundary():
    """Test that ISO week boundaries are correctly calculated."""
    from repo_analyzer.aggregator import WeeklyAggregator
    from repo_analyzer.models import CommitData

    # Sunday April 3, 2005 should be in week starting March 28
    # Monday April 4, 2005 should be in week starting April 4
    commits = [
        CommitData(
            hash="sunday",
            author_name="Sunday Author",
            commit_date=datetime(2005, 4, 3, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=10,
            lines_deleted=5,
            version=None
        ),
        CommitData(
            hash="monday",
            author_name="Monday Author",
            commit_date=datetime(2005, 4, 4, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=20,
            lines_deleted=10,
            version=None
        ),
    ]

    aggregator = WeeklyAggregator()
    result = aggregator.aggregate(commits)

    assert len(result) == 2
    # First week should start on Monday March 28
    assert result[0].week_start == datetime(2005, 3, 28, 0, 0, 0, tzinfo=timezone.utc)
    # Second week should start on Monday April 4
    assert result[1].week_start == datetime(2005, 4, 4, 0, 0, 0, tzinfo=timezone.utc)


def test_aggregate_unique_authors_counting():
    """Test that unique authors are counted correctly per week."""
    from repo_analyzer.aggregator import WeeklyAggregator
    from repo_analyzer.models import CommitData

    commits = [
        CommitData(
            hash="commit1",
            author_name="John Doe",
            commit_date=datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=10,
            lines_deleted=5,
            version=None
        ),
        CommitData(
            hash="commit2",
            author_name="John Doe",  # Same author
            commit_date=datetime(2005, 4, 6, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=20,
            lines_deleted=10,
            version=None
        ),
        CommitData(
            hash="commit3",
            author_name="Jane Smith",  # Different author
            commit_date=datetime(2005, 4, 7, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=30,
            lines_deleted=15,
            version=None
        ),
    ]

    aggregator = WeeklyAggregator()
    result = aggregator.aggregate(commits)

    assert len(result) == 1
    assert result[0].unique_authors == 2  # John Doe and Jane Smith


def test_aggregate_version_deduplication():
    """Test that duplicate versions within a week are deduplicated."""
    from repo_analyzer.aggregator import WeeklyAggregator
    from repo_analyzer.models import CommitData

    commits = [
        CommitData(
            hash="commit1",
            author_name="Author 1",
            commit_date=datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=10,
            lines_deleted=5,
            version="1.5"
        ),
        CommitData(
            hash="commit2",
            author_name="Author 2",
            commit_date=datetime(2005, 4, 6, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=20,
            lines_deleted=10,
            version="1.5"  # Duplicate version
        ),
        CommitData(
            hash="commit3",
            author_name="Author 3",
            commit_date=datetime(2005, 4, 7, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=30,
            lines_deleted=15,
            version="1.5.1"
        ),
    ]

    aggregator = WeeklyAggregator()
    result = aggregator.aggregate(commits)

    assert len(result) == 1
    # Should only have unique versions: 1.5 and 1.5.1
    assert len(result[0].versions_released) == 2
    assert "1.5" in result[0].versions_released
    assert "1.5.1" in result[0].versions_released


def test_aggregate_none_versions_filtered():
    """Test that None versions are filtered out from released versions."""
    from repo_analyzer.aggregator import WeeklyAggregator
    from repo_analyzer.models import CommitData

    commits = [
        CommitData(
            hash="commit1",
            author_name="Author 1",
            commit_date=datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=10,
            lines_deleted=5,
            version=None
        ),
        CommitData(
            hash="commit2",
            author_name="Author 2",
            commit_date=datetime(2005, 4, 6, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=20,
            lines_deleted=10,
            version="1.5"
        ),
        CommitData(
            hash="commit3",
            author_name="Author 3",
            commit_date=datetime(2005, 4, 7, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=30,
            lines_deleted=15,
            version=None
        ),
    ]

    aggregator = WeeklyAggregator()
    result = aggregator.aggregate(commits)

    assert len(result) == 1
    # Should only have "1.5", None values filtered out
    assert result[0].versions_released == ["1.5"]


def test_aggregate_results_sorted_by_week():
    """Test that aggregation results are sorted by week start date."""
    from repo_analyzer.aggregator import WeeklyAggregator
    from repo_analyzer.models import CommitData

    # Create commits in reverse chronological order
    commits = [
        CommitData(
            hash="commit3",
            author_name="Author 3",
            commit_date=datetime(2005, 4, 20, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=30,
            lines_deleted=15,
            version=None
        ),
        CommitData(
            hash="commit1",
            author_name="Author 1",
            commit_date=datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=10,
            lines_deleted=5,
            version=None
        ),
        CommitData(
            hash="commit2",
            author_name="Author 2",
            commit_date=datetime(2005, 4, 12, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=20,
            lines_deleted=10,
            version=None
        ),
    ]

    aggregator = WeeklyAggregator()
    result = aggregator.aggregate(commits)

    # Should return 3 weeks in chronological order
    assert len(result) == 3
    assert result[0].week_start < result[1].week_start < result[2].week_start
