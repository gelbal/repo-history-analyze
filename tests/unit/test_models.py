# ABOUTME: Unit tests for data models (CommitData and WeeklyAggregate).
# ABOUTME: Tests dataclass creation, immutability, and field validation.

import pytest
from datetime import datetime, timezone


def test_commit_data_creation():
    """Test creating a CommitData instance with all fields."""
    from repo_analyzer.models import CommitData

    commit = CommitData(
        hash="abc123",
        author_name="John Doe",
        commit_date=datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc),
        lines_added=42,
        lines_deleted=7,
        version="1.5"
    )

    assert commit.hash == "abc123"
    assert commit.author_name == "John Doe"
    assert commit.commit_date == datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc)
    assert commit.lines_added == 42
    assert commit.lines_deleted == 7
    assert commit.version == "1.5"


def test_commit_data_with_none_version():
    """Test CommitData with None version (untagged commit)."""
    from repo_analyzer.models import CommitData

    commit = CommitData(
        hash="def456",
        author_name="Jane Smith",
        commit_date=datetime(2005, 4, 6, 14, 30, 0, tzinfo=timezone.utc),
        lines_added=128,
        lines_deleted=3,
        version=None
    )

    assert commit.version is None


def test_commit_data_immutability():
    """Test that CommitData is immutable (frozen=True)."""
    from repo_analyzer.models import CommitData

    commit = CommitData(
        hash="abc123",
        author_name="John Doe",
        commit_date=datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc),
        lines_added=42,
        lines_deleted=7,
        version="1.5"
    )

    with pytest.raises(AttributeError):
        commit.hash = "new_hash"


def test_weekly_aggregate_creation():
    """Test creating a WeeklyAggregate instance with all fields."""
    from repo_analyzer.models import WeeklyAggregate

    aggregate = WeeklyAggregate(
        week_start=datetime(2005, 4, 4, 0, 0, 0, tzinfo=timezone.utc),
        total_commits=47,
        unique_authors=12,
        total_lines_added=1523,
        total_lines_deleted=245,
        versions_released=["1.5"]
    )

    assert aggregate.week_start == datetime(2005, 4, 4, 0, 0, 0, tzinfo=timezone.utc)
    assert aggregate.total_commits == 47
    assert aggregate.unique_authors == 12
    assert aggregate.total_lines_added == 1523
    assert aggregate.total_lines_deleted == 245
    assert aggregate.versions_released == ["1.5"]


def test_weekly_aggregate_empty_versions():
    """Test WeeklyAggregate with empty versions list."""
    from repo_analyzer.models import WeeklyAggregate

    aggregate = WeeklyAggregate(
        week_start=datetime(2005, 4, 11, 0, 0, 0, tzinfo=timezone.utc),
        total_commits=63,
        unique_authors=15,
        total_lines_added=2341,
        total_lines_deleted=412,
        versions_released=[]
    )

    assert aggregate.versions_released == []


def test_weekly_aggregate_multiple_versions():
    """Test WeeklyAggregate with multiple versions released in one week."""
    from repo_analyzer.models import WeeklyAggregate

    aggregate = WeeklyAggregate(
        week_start=datetime(2005, 4, 11, 0, 0, 0, tzinfo=timezone.utc),
        total_commits=63,
        unique_authors=15,
        total_lines_added=2341,
        total_lines_deleted=412,
        versions_released=["1.5.1", "1.5.2"]
    )

    assert len(aggregate.versions_released) == 2
    assert "1.5.1" in aggregate.versions_released
    assert "1.5.2" in aggregate.versions_released


def test_weekly_aggregate_immutability():
    """Test that WeeklyAggregate is immutable (frozen=True)."""
    from repo_analyzer.models import WeeklyAggregate

    aggregate = WeeklyAggregate(
        week_start=datetime(2005, 4, 4, 0, 0, 0, tzinfo=timezone.utc),
        total_commits=47,
        unique_authors=12,
        total_lines_added=1523,
        total_lines_deleted=245,
        versions_released=["1.5"]
    )

    with pytest.raises(AttributeError):
        aggregate.total_commits = 100


def test_commit_data_with_zero_lines():
    """Test CommitData with zero lines added/deleted."""
    from repo_analyzer.models import CommitData

    commit = CommitData(
        hash="xyz789",
        author_name="Bob Builder",
        commit_date=datetime(2005, 4, 7, 10, 0, 0, tzinfo=timezone.utc),
        lines_added=0,
        lines_deleted=0,
        version=None
    )

    assert commit.lines_added == 0
    assert commit.lines_deleted == 0


def test_commit_data_with_unicode_author():
    """Test CommitData with unicode characters in author name."""
    from repo_analyzer.models import CommitData

    commit = CommitData(
        hash="unicode123",
        author_name="Müller José 李明",
        commit_date=datetime(2005, 4, 8, 15, 0, 0, tzinfo=timezone.utc),
        lines_added=50,
        lines_deleted=10,
        version=None
    )

    assert commit.author_name == "Müller José 李明"


def test_rolling_window_aggregate_creation():
    """Test creating a RollingWindowAggregate instance with all fields."""
    from repo_analyzer.models import RollingWindowAggregate

    rolling_agg = RollingWindowAggregate(
        window_start=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        window_end=datetime(2024, 3, 24, 23, 59, 59, tzinfo=timezone.utc),
        total_commits=564,
        unique_authors=45,
        total_lines_added=15234,
        total_lines_deleted=3421,
        versions_released=["6.4.1", "6.4.2"]
    )

    assert rolling_agg.window_start == datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert rolling_agg.window_end == datetime(2024, 3, 24, 23, 59, 59, tzinfo=timezone.utc)
    assert rolling_agg.total_commits == 564
    assert rolling_agg.unique_authors == 45
    assert rolling_agg.total_lines_added == 15234
    assert rolling_agg.total_lines_deleted == 3421
    assert rolling_agg.versions_released == ["6.4.1", "6.4.2"]


def test_rolling_window_aggregate_empty_versions():
    """Test RollingWindowAggregate with empty versions list."""
    from repo_analyzer.models import RollingWindowAggregate

    rolling_agg = RollingWindowAggregate(
        window_start=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        window_end=datetime(2024, 3, 24, 23, 59, 59, tzinfo=timezone.utc),
        total_commits=123,
        unique_authors=10,
        total_lines_added=5000,
        total_lines_deleted=1000,
        versions_released=[]
    )

    assert rolling_agg.versions_released == []


def test_rolling_window_aggregate_immutability():
    """Test that RollingWindowAggregate is immutable (frozen=True)."""
    from repo_analyzer.models import RollingWindowAggregate

    rolling_agg = RollingWindowAggregate(
        window_start=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        window_end=datetime(2024, 3, 24, 23, 59, 59, tzinfo=timezone.utc),
        total_commits=564,
        unique_authors=45,
        total_lines_added=15234,
        total_lines_deleted=3421,
        versions_released=["6.4.1", "6.4.2"]
    )

    with pytest.raises(AttributeError):
        rolling_agg.total_commits = 1000
