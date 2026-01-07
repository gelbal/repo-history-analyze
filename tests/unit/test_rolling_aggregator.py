# ABOUTME: Unit tests for RollingWindowAggregator class.
# ABOUTME: Tests 12-week rolling window calculation, deduplication, and edge cases.

import pytest
from datetime import datetime, timezone, timedelta
from repo_analyzer.models import CommitData, WeeklyAggregate, RollingWindowAggregate
from repo_analyzer.aggregator import RollingWindowAggregator, WeeklyAggregator


@pytest.fixture
def sample_commits_12_weeks():
    """Create sample commits spanning 12 weeks."""
    commits = []
    base_date = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)  # Monday

    for week in range(12):
        for day in range(7):  # 7 commits per week
            commit_date = base_date + timedelta(weeks=week, days=day)
            commits.append(CommitData(
                hash=f"hash_week{week}_day{day}",
                author_name=f"Author {week % 3}",  # 3 authors cycling
                commit_date=commit_date,
                lines_added=100 + week * 10,
                lines_deleted=50 + week * 5,
                version=f"1.{week}" if day == 0 else None  # Version on first day of week
            ))

    return commits


@pytest.fixture
def sample_weekly_aggregates_12_weeks():
    """Create sample weekly aggregates for 12 weeks."""
    aggregates = []
    base_date = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)  # Monday

    for week in range(12):
        week_start = base_date + timedelta(weeks=week)
        aggregates.append(WeeklyAggregate(
            week_start=week_start,
            total_commits=7,  # 7 commits per week
            unique_authors=3,  # 3 unique authors per week
            total_lines_added=700 + week * 70,
            total_lines_deleted=350 + week * 35,
            versions_released=[f"1.{week}"] if week < 10 else []
        ))

    return aggregates


def test_rolling_aggregator_initialization():
    """Test RollingWindowAggregator can be initialized."""
    aggregator = RollingWindowAggregator()

    assert aggregator is not None
    assert hasattr(aggregator, 'WINDOW_SIZE_WEEKS')
    assert aggregator.WINDOW_SIZE_WEEKS == 12


def test_rolling_aggregate_exact_12_weeks(sample_commits_12_weeks, sample_weekly_aggregates_12_weeks):
    """Test rolling window with exactly 12 weeks of data."""
    aggregator = RollingWindowAggregator()

    rolling_windows = aggregator.aggregate(sample_commits_12_weeks, sample_weekly_aggregates_12_weeks)

    # Should create 12 rolling windows (one per week)
    assert len(rolling_windows) == 12

    # First window should start at week 0
    assert rolling_windows[0].window_start == datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    # First window should include all 12 weeks (84 commits)
    assert rolling_windows[0].total_commits == 84


def test_rolling_aggregate_overlapping_windows(sample_commits_12_weeks, sample_weekly_aggregates_12_weeks):
    """Test that windows overlap correctly."""
    aggregator = RollingWindowAggregator()

    rolling_windows = aggregator.aggregate(sample_commits_12_weeks, sample_weekly_aggregates_12_weeks)

    # Windows should be overlapping - each starts one week later
    for i in range(len(rolling_windows) - 1):
        week_diff = (rolling_windows[i + 1].window_start - rolling_windows[i].window_start).days
        assert week_diff == 7  # One week apart


def test_rolling_aggregate_author_deduplication(sample_commits_12_weeks, sample_weekly_aggregates_12_weeks):
    """Test author deduplication across 12-week window."""
    aggregator = RollingWindowAggregator()

    rolling_windows = aggregator.aggregate(sample_commits_12_weeks, sample_weekly_aggregates_12_weeks)

    # With 3 authors cycling, each window should have 3 unique authors
    assert rolling_windows[0].unique_authors == 3


def test_rolling_aggregate_version_deduplication(sample_commits_12_weeks, sample_weekly_aggregates_12_weeks):
    """Test version deduplication across 12-week window."""
    aggregator = RollingWindowAggregator()

    rolling_windows = aggregator.aggregate(sample_commits_12_weeks, sample_weekly_aggregates_12_weeks)

    # First window should have 12 versions (1.0 through 1.11 for all 12 weeks)
    assert len(rolling_windows[0].versions_released) == 12
    assert "1.0" in rolling_windows[0].versions_released
    assert "1.11" in rolling_windows[0].versions_released


def test_rolling_aggregate_less_than_12_weeks():
    """Test rolling window with less than 12 weeks of data."""
    # Create only 5 weeks of commits
    commits = []
    base_date = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    for week in range(5):
        for day in range(7):
            commit_date = base_date + timedelta(weeks=week, days=day)
            commits.append(CommitData(
                hash=f"hash_week{week}_day{day}",
                author_name="Author 1",
                commit_date=commit_date,
                lines_added=100,
                lines_deleted=50,
                version=None
            ))

    # Create corresponding weekly aggregates
    aggregator_weekly = WeeklyAggregator()
    weekly_aggregates = aggregator_weekly.aggregate(commits)

    assert len(weekly_aggregates) == 5

    # Create rolling windows
    rolling_aggregator = RollingWindowAggregator()
    rolling_windows = rolling_aggregator.aggregate(commits, weekly_aggregates)

    # Should still create 5 windows, but each has fewer weeks
    assert len(rolling_windows) == 5

    # First window has all 5 weeks (35 commits)
    assert rolling_windows[0].total_commits == 35

    # Last window has only 1 week (7 commits)
    assert rolling_windows[-1].total_commits == 7


def test_rolling_aggregate_statistics_summation(sample_commits_12_weeks, sample_weekly_aggregates_12_weeks):
    """Test that line counts sum correctly across window."""
    aggregator = RollingWindowAggregator()

    rolling_windows = aggregator.aggregate(sample_commits_12_weeks, sample_weekly_aggregates_12_weeks)

    # Calculate expected totals for first window (all 12 weeks)
    expected_commits = 12 * 7  # 7 commits per week
    expected_lines_added = sum(7 * (100 + week * 10) for week in range(12))
    expected_lines_deleted = sum(7 * (50 + week * 5) for week in range(12))

    assert rolling_windows[0].total_commits == expected_commits
    assert rolling_windows[0].total_lines_added == expected_lines_added
    assert rolling_windows[0].total_lines_deleted == expected_lines_deleted


def test_rolling_aggregate_empty_input():
    """Test rolling window with empty input."""
    aggregator = RollingWindowAggregator()

    rolling_windows = aggregator.aggregate([], [])

    assert rolling_windows == []


def test_rolling_aggregate_single_week():
    """Test rolling window with only 1 week of data."""
    # Create 1 week of commits
    commits = []
    base_date = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    for day in range(7):
        commit_date = base_date + timedelta(days=day)
        commits.append(CommitData(
            hash=f"hash_day{day}",
            author_name="Author 1",
            commit_date=commit_date,
            lines_added=100,
            lines_deleted=50,
            version="1.0" if day == 0 else None
        ))

    # Create corresponding weekly aggregates
    aggregator_weekly = WeeklyAggregator()
    weekly_aggregates = aggregator_weekly.aggregate(commits)

    assert len(weekly_aggregates) == 1

    # Create rolling windows
    rolling_aggregator = RollingWindowAggregator()
    rolling_windows = rolling_aggregator.aggregate(commits, weekly_aggregates)

    # Should create 1 window with 1 week (7 commits)
    assert len(rolling_windows) == 1
    assert rolling_windows[0].total_commits == 7
    assert rolling_windows[0].unique_authors == 1
    assert rolling_windows[0].versions_released == ["1.0"]


def test_rolling_aggregate_window_boundaries(sample_commits_12_weeks, sample_weekly_aggregates_12_weeks):
    """Test that window start and end dates are correct."""
    aggregator = RollingWindowAggregator()

    rolling_windows = aggregator.aggregate(sample_commits_12_weeks, sample_weekly_aggregates_12_weeks)

    # First window: starts at week 0, ends at week 11
    first_window = rolling_windows[0]
    assert first_window.window_start == datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    # Window end should be end of last week in window
    # Week 11 starts on March 18, ends on March 24 (Sunday)
    expected_end = datetime(2024, 3, 24, 23, 59, 59, tzinfo=timezone.utc)
    assert first_window.window_end == expected_end


def test_rolling_aggregate_sorted_output(sample_commits_12_weeks, sample_weekly_aggregates_12_weeks):
    """Test that rolling windows are sorted by window_start."""
    aggregator = RollingWindowAggregator()

    rolling_windows = aggregator.aggregate(sample_commits_12_weeks, sample_weekly_aggregates_12_weeks)

    # Verify windows are sorted
    for i in range(len(rolling_windows) - 1):
        assert rolling_windows[i].window_start < rolling_windows[i + 1].window_start


def test_rolling_aggregate_versions_are_sorted(sample_commits_12_weeks, sample_weekly_aggregates_12_weeks):
    """Test that versions in each window are sorted."""
    aggregator = RollingWindowAggregator()

    rolling_windows = aggregator.aggregate(sample_commits_12_weeks, sample_weekly_aggregates_12_weeks)

    # Check first window versions are sorted
    versions = rolling_windows[0].versions_released
    assert versions == sorted(versions)


def test_rolling_aggregate_multiple_authors_deduplication():
    """Test deduplication with more complex author patterns."""
    commits = []
    base_date = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    # Create commits with specific author pattern
    authors = ["Alice", "Bob", "Charlie", "Alice", "Bob"]  # Alice and Bob appear twice

    for week in range(5):
        for idx, author in enumerate(authors):
            commit_date = base_date + timedelta(weeks=week, days=idx)
            commits.append(CommitData(
                hash=f"hash_week{week}_{idx}",
                author_name=author,
                commit_date=commit_date,
                lines_added=100,
                lines_deleted=50,
                version=None
            ))

    # Create corresponding weekly aggregates
    aggregator_weekly = WeeklyAggregator()
    weekly_aggregates = aggregator_weekly.aggregate(commits)

    # Create rolling windows
    rolling_aggregator = RollingWindowAggregator()
    rolling_windows = rolling_aggregator.aggregate(commits, weekly_aggregates)

    # First window should have 3 unique authors (Alice, Bob, Charlie)
    assert rolling_windows[0].unique_authors == 3
