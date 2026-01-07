# ABOUTME: End-to-end integration tests for full pipeline.
# ABOUTME: Tests complete workflow from repository to CSV output.

import pytest
from pathlib import Path
from datetime import datetime, timezone
import csv


@pytest.mark.integration
def test_full_pipeline_with_mock_data(cache_dir, output_dir):
    """Test full pipeline with mocked repository data."""
    from repo_analyzer.models import CommitData
    from repo_analyzer.extractor import CommitExtractor
    from repo_analyzer.aggregator import WeeklyAggregator
    from repo_analyzer.csv_writer import CSVWriter
    from repo_analyzer.version_mapper import VersionMapper
    from unittest.mock import MagicMock

    # Create mock commits
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
            commit_date=datetime(2005, 4, 12, 9, 15, 0, tzinfo=timezone.utc),
            lines_added=64,
            lines_deleted=12,
            version="1.5.1"
        ),
    ]

    # Aggregate commits
    aggregator = WeeklyAggregator()
    aggregates = aggregator.aggregate(commits)

    # Write to CSV
    commits_path = output_dir / "commits.csv"
    aggregates_path = output_dir / "weekly_aggregates.csv"

    CSVWriter.write_commits(commits, commits_path)
    CSVWriter.write_aggregates(aggregates, aggregates_path)

    # Verify commits CSV exists and has correct data
    assert commits_path.exists()
    with open(commits_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 3
        assert rows[0]['hash'] == 'abc123'
        assert rows[0]['version'] == '1.5'

    # Verify aggregates CSV exists and has correct data
    assert aggregates_path.exists()
    with open(aggregates_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2  # Two weeks
        assert rows[0]['total_commits'] == '2'  # First week has 2 commits
        assert rows[1]['total_commits'] == '1'  # Second week has 1 commit


@pytest.mark.integration
def test_pipeline_preserves_data_integrity(cache_dir, output_dir):
    """Test that data integrity is maintained through the pipeline."""
    from repo_analyzer.models import CommitData
    from repo_analyzer.aggregator import WeeklyAggregator
    from repo_analyzer.csv_writer import CSVWriter

    # Create commit with specific values
    commit = CommitData(
        hash="test_hash_123",
        author_name="Test Author",
        commit_date=datetime(2005, 4, 5, 15, 30, 45, tzinfo=timezone.utc),
        lines_added=100,
        lines_deleted=50,
        version="2.0"
    )

    # Write to CSV
    commits_path = output_dir / "commits.csv"
    CSVWriter.write_commits([commit], commits_path)

    # Read back and verify
    with open(commits_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        row = next(reader)

        assert row['hash'] == 'test_hash_123'
        assert row['author_name'] == 'Test Author'
        assert row['commit_date'] == '2005-04-05T15:30:45+00:00'
        assert row['lines_added'] == '100'
        assert row['lines_deleted'] == '50'
        assert row['version'] == '2.0'


@pytest.mark.integration
def test_pipeline_handles_unicode(cache_dir, output_dir):
    """Test that pipeline correctly handles unicode characters."""
    from repo_analyzer.models import CommitData
    from repo_analyzer.csv_writer import CSVWriter

    commit = CommitData(
        hash="unicode123",
        author_name="Müller José 李明",
        commit_date=datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc),
        lines_added=50,
        lines_deleted=10,
        version=None
    )

    commits_path = output_dir / "commits.csv"
    CSVWriter.write_commits([commit], commits_path)

    # Read back with UTF-8 encoding
    with open(commits_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        row = next(reader)

        assert row['author_name'] == "Müller José 李明"


@pytest.mark.integration
def test_pipeline_empty_data(cache_dir, output_dir):
    """Test pipeline handles empty data gracefully."""
    from repo_analyzer.aggregator import WeeklyAggregator
    from repo_analyzer.csv_writer import CSVWriter

    # Empty commits list
    aggregator = WeeklyAggregator()
    aggregates = aggregator.aggregate([])

    # Should produce empty CSV with headers
    commits_path = output_dir / "commits.csv"
    aggregates_path = output_dir / "weekly_aggregates.csv"

    CSVWriter.write_commits([], commits_path)
    CSVWriter.write_aggregates(aggregates, aggregates_path)

    assert commits_path.exists()
    assert aggregates_path.exists()

    # Both should have headers but no data
    with open(commits_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 0
        assert reader.fieldnames is not None


@pytest.mark.integration
def test_aggregation_accuracy(cache_dir, output_dir):
    """Test that aggregation produces mathematically correct results."""
    from repo_analyzer.models import CommitData
    from repo_analyzer.aggregator import WeeklyAggregator
    from repo_analyzer.csv_writer import CSVWriter

    # Create known commits in single week
    commits = [
        CommitData(
            hash=f"commit{i}",
            author_name="Author1" if i % 2 == 0 else "Author2",
            commit_date=datetime(2005, 4, 5 + i, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=10 * (i + 1),
            lines_deleted=5 * (i + 1),
            version=None
        )
        for i in range(3)
    ]

    aggregator = WeeklyAggregator()
    aggregates = aggregator.aggregate(commits)

    aggregates_path = output_dir / "weekly_aggregates.csv"
    CSVWriter.write_aggregates(aggregates, aggregates_path)

    with open(aggregates_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        row = next(reader)

        # 3 commits
        assert row['total_commits'] == '3'
        # 2 unique authors
        assert row['unique_authors'] == '2'
        # Total lines added: 10 + 20 + 30 = 60
        assert row['total_lines_added'] == '60'
        # Total lines deleted: 5 + 10 + 15 = 30
        assert row['total_lines_deleted'] == '30'


@pytest.mark.integration
def test_pipeline_with_yearly_folder_structure(cache_dir, output_dir):
    """Test full pipeline with yearly folder structure for commits."""
    from repo_analyzer.models import CommitData
    from repo_analyzer.aggregator import WeeklyAggregator
    from repo_analyzer.csv_writer import CSVWriter

    # Create commits spanning multiple years (2005 and 2024)
    commits = [
        CommitData(
            hash="2005_1",
            author_name="Author 1",
            commit_date=datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=10,
            lines_deleted=5,
            version="1.5"
        ),
        CommitData(
            hash="2005_2",
            author_name="Author 2",
            commit_date=datetime(2005, 4, 15, 14, 0, 0, tzinfo=timezone.utc),
            lines_added=20,
            lines_deleted=10,
            version=None
        ),
        CommitData(
            hash="2005_3",
            author_name="Author 1",
            commit_date=datetime(2005, 5, 3, 9, 0, 0, tzinfo=timezone.utc),
            lines_added=30,
            lines_deleted=15,
            version="1.5.1"
        ),
        CommitData(
            hash="2024_1",
            author_name="Author 3",
            commit_date=datetime(2024, 6, 10, 16, 0, 0, tzinfo=timezone.utc),
            lines_added=40,
            lines_deleted=20,
            version=None
        ),
    ]

    repo_name = "WordPress"

    # Write commits using yearly structure
    CSVWriter.write_commits_by_year(commits, output_dir, repo_name)

    # Verify yearly folder structure
    year_2005_dir = output_dir / "WordPress" / "2005"
    year_2024_dir = output_dir / "WordPress" / "2024"

    assert year_2005_dir.exists()
    assert year_2024_dir.exists()

    # Verify 2005 commits CSV
    csv_2005 = year_2005_dir / "commits.csv"
    assert csv_2005.exists()
    with open(csv_2005, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 3  # All 2005 commits
        assert rows[0]['hash'] == '2005_1'
        assert rows[1]['hash'] == '2005_2'
        assert rows[2]['hash'] == '2005_3'

    # Verify 2024 commits CSV
    csv_2024 = year_2024_dir / "commits.csv"
    assert csv_2024.exists()
    with open(csv_2024, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1  # 2024 commit
        assert rows[0]['hash'] == '2024_1'

    # Verify single weekly aggregates at repo root
    aggregator = WeeklyAggregator()
    aggregates = aggregator.aggregate(commits)
    aggregates_path = output_dir / "WordPress" / "weekly_aggregates.csv"
    CSVWriter.write_aggregates(aggregates, aggregates_path)

    assert aggregates_path.exists()
    with open(aggregates_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        # Should have aggregates spanning multiple weeks
        assert len(rows) > 0
        # Verify data integrity (all 4 commits should be included)
        total_commits = sum(int(row['total_commits']) for row in rows)
        assert total_commits == 4
