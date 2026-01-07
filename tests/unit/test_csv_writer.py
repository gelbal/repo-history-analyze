# ABOUTME: Unit tests for CSVWriter class.
# ABOUTME: Tests CSV file creation, structure, encoding, and formatting.

import pytest
import csv
from pathlib import Path
from datetime import datetime, timezone


def test_write_commits_creates_file(output_dir, sample_commits):
    """Test that write_commits creates a CSV file."""
    from repo_analyzer.csv_writer import CSVWriter

    output_path = output_dir / "commits.csv"

    CSVWriter.write_commits(sample_commits, output_path)

    assert output_path.exists()
    assert output_path.is_file()


def test_write_commits_csv_structure(output_dir, sample_commits):
    """Test that commits CSV has correct column structure."""
    from repo_analyzer.csv_writer import CSVWriter

    output_path = output_dir / "commits.csv"
    CSVWriter.write_commits(sample_commits, output_path)

    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

        expected_headers = [
            'hash',
            'author_name',
            'commit_date',
            'lines_added',
            'lines_deleted',
            'version'
        ]

        assert headers == expected_headers


def test_write_commits_data_content(output_dir, sample_commits):
    """Test that commits CSV contains correct data."""
    from repo_analyzer.csv_writer import CSVWriter

    output_path = output_dir / "commits.csv"
    CSVWriter.write_commits(sample_commits, output_path)

    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        assert len(rows) == 4  # sample_commits has 4 commits

        # Check first commit
        assert rows[0]['hash'] == 'abc123'
        assert rows[0]['author_name'] == 'John Doe'
        assert rows[0]['lines_added'] == '42'
        assert rows[0]['lines_deleted'] == '7'
        assert rows[0]['version'] == '1.5'

        # Check commit without version (empty string, not "None")
        assert rows[1]['version'] == ''


def test_write_commits_iso_date_format(output_dir):
    """Test that commit dates are formatted as ISO 8601."""
    from repo_analyzer.csv_writer import CSVWriter
    from repo_analyzer.models import CommitData

    commits = [
        CommitData(
            hash="test123",
            author_name="Test Author",
            commit_date=datetime(2005, 4, 5, 12, 30, 45, tzinfo=timezone.utc),
            lines_added=10,
            lines_deleted=5,
            version=None
        )
    ]

    output_path = output_dir / "commits.csv"
    CSVWriter.write_commits(commits, output_path)

    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        row = next(reader)

        # Should be ISO 8601 format with timezone
        assert row['commit_date'] == '2005-04-05T12:30:45+00:00'


def test_write_commits_utf8_encoding(output_dir):
    """Test that commits CSV uses UTF-8 encoding for unicode names."""
    from repo_analyzer.csv_writer import CSVWriter
    from repo_analyzer.models import CommitData

    commits = [
        CommitData(
            hash="unicode123",
            author_name="Müller José 李明",
            commit_date=datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=50,
            lines_deleted=10,
            version=None
        )
    ]

    output_path = output_dir / "commits.csv"
    CSVWriter.write_commits(commits, output_path)

    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        row = next(reader)

        assert row['author_name'] == "Müller José 李明"


def test_write_commits_empty_list(output_dir):
    """Test writing empty commits list creates file with headers only."""
    from repo_analyzer.csv_writer import CSVWriter

    output_path = output_dir / "commits.csv"
    CSVWriter.write_commits([], output_path)

    assert output_path.exists()

    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        assert len(rows) == 0  # No data rows
        assert reader.fieldnames is not None  # But headers exist


def test_write_aggregates_creates_file(output_dir):
    """Test that write_aggregates creates a CSV file."""
    from repo_analyzer.csv_writer import CSVWriter
    from repo_analyzer.models import WeeklyAggregate

    aggregates = [
        WeeklyAggregate(
            week_start=datetime(2005, 4, 4, 0, 0, 0, tzinfo=timezone.utc),
            total_commits=47,
            unique_authors=12,
            total_lines_added=1523,
            total_lines_deleted=245,
            versions_released=["1.5"]
        )
    ]

    output_path = output_dir / "weekly_aggregates.csv"
    CSVWriter.write_aggregates(aggregates, output_path)

    assert output_path.exists()
    assert output_path.is_file()


def test_write_aggregates_csv_structure(output_dir):
    """Test that weekly aggregates CSV has correct column structure."""
    from repo_analyzer.csv_writer import CSVWriter
    from repo_analyzer.models import WeeklyAggregate

    aggregates = [
        WeeklyAggregate(
            week_start=datetime(2005, 4, 4, 0, 0, 0, tzinfo=timezone.utc),
            total_commits=47,
            unique_authors=12,
            total_lines_added=1523,
            total_lines_deleted=245,
            versions_released=["1.5"]
        )
    ]

    output_path = output_dir / "weekly_aggregates.csv"
    CSVWriter.write_aggregates(aggregates, output_path)

    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

        expected_headers = [
            'week_start',
            'total_commits',
            'unique_authors',
            'total_lines_added',
            'total_lines_deleted',
            'versions_released'
        ]

        assert headers == expected_headers


def test_write_aggregates_data_content(output_dir):
    """Test that aggregates CSV contains correct data."""
    from repo_analyzer.csv_writer import CSVWriter
    from repo_analyzer.models import WeeklyAggregate

    aggregates = [
        WeeklyAggregate(
            week_start=datetime(2005, 4, 4, 0, 0, 0, tzinfo=timezone.utc),
            total_commits=47,
            unique_authors=12,
            total_lines_added=1523,
            total_lines_deleted=245,
            versions_released=["1.5"]
        ),
        WeeklyAggregate(
            week_start=datetime(2005, 4, 11, 0, 0, 0, tzinfo=timezone.utc),
            total_commits=63,
            unique_authors=15,
            total_lines_added=2341,
            total_lines_deleted=412,
            versions_released=[]
        )
    ]

    output_path = output_dir / "weekly_aggregates.csv"
    CSVWriter.write_aggregates(aggregates, output_path)

    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        assert len(rows) == 2

        # First week with version
        assert rows[0]['total_commits'] == '47'
        assert rows[0]['unique_authors'] == '12'
        assert rows[0]['total_lines_added'] == '1523'
        assert rows[0]['total_lines_deleted'] == '245'
        assert rows[0]['versions_released'] == '1.5'

        # Second week without version (empty string)
        assert rows[1]['versions_released'] == ''


def test_write_aggregates_multiple_versions(output_dir):
    """Test that multiple versions are semicolon-separated."""
    from repo_analyzer.csv_writer import CSVWriter
    from repo_analyzer.models import WeeklyAggregate

    aggregates = [
        WeeklyAggregate(
            week_start=datetime(2005, 4, 11, 0, 0, 0, tzinfo=timezone.utc),
            total_commits=63,
            unique_authors=15,
            total_lines_added=2341,
            total_lines_deleted=412,
            versions_released=["1.5.1", "1.5.2"]
        )
    ]

    output_path = output_dir / "weekly_aggregates.csv"
    CSVWriter.write_aggregates(aggregates, output_path)

    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        row = next(reader)

        # Multiple versions separated by semicolon
        assert row['versions_released'] == '1.5.1;1.5.2'


def test_write_aggregates_empty_list(output_dir):
    """Test writing empty aggregates list creates file with headers only."""
    from repo_analyzer.csv_writer import CSVWriter

    output_path = output_dir / "weekly_aggregates.csv"
    CSVWriter.write_aggregates([], output_path)

    assert output_path.exists()

    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        assert len(rows) == 0
        assert reader.fieldnames is not None


def test_write_commits_creates_parent_directory(tmp_path):
    """Test that CSV writer creates parent directories if needed."""
    from repo_analyzer.csv_writer import CSVWriter
    from repo_analyzer.models import CommitData

    commits = [
        CommitData(
            hash="test123",
            author_name="Test",
            commit_date=datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=10,
            lines_deleted=5,
            version=None
        )
    ]

    # Create path with non-existent parent directory
    output_path = tmp_path / "subdir" / "nested" / "commits.csv"

    CSVWriter.write_commits(commits, output_path)

    assert output_path.exists()
    assert output_path.parent.exists()


def test_write_commits_by_year(tmp_path):
    """Test writing commits grouped by year into folders."""
    from repo_analyzer.csv_writer import CSVWriter
    from repo_analyzer.models import CommitData

    # Create commits from different years
    commits = [
        CommitData(
            hash="2005_1",
            author_name="Author 1",
            commit_date=datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=10,
            lines_deleted=5,
            version=None
        ),
        CommitData(
            hash="2005_2",
            author_name="Author 2",
            commit_date=datetime(2005, 4, 15, 14, 0, 0, tzinfo=timezone.utc),
            lines_added=20,
            lines_deleted=10,
            version="1.5"
        ),
        CommitData(
            hash="2005_3",
            author_name="Author 3",
            commit_date=datetime(2005, 12, 3, 9, 0, 0, tzinfo=timezone.utc),
            lines_added=30,
            lines_deleted=15,
            version=None
        ),
        CommitData(
            hash="2024_1",
            author_name="Author 1",
            commit_date=datetime(2024, 6, 10, 16, 0, 0, tzinfo=timezone.utc),
            lines_added=40,
            lines_deleted=20,
            version=None
        ),
    ]

    base_output_dir = tmp_path / "data"
    repo_name = "WordPress"

    CSVWriter.write_commits_by_year(commits, base_output_dir, repo_name)

    # Verify folder structure created
    year_2005_dir = base_output_dir / "WordPress" / "2005"
    year_2024_dir = base_output_dir / "WordPress" / "2024"

    assert year_2005_dir.exists()
    assert year_2024_dir.exists()

    # Verify 2005 commits CSV
    csv_2005 = year_2005_dir / "commits.csv"
    assert csv_2005.exists()

    with open(csv_2005, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 3  # 3 commits in 2005
        assert rows[0]['hash'] == '2005_1'
        assert rows[1]['hash'] == '2005_2'
        assert rows[1]['version'] == '1.5'
        assert rows[2]['hash'] == '2005_3'

    # Verify 2024 commits CSV
    csv_2024 = year_2024_dir / "commits.csv"
    assert csv_2024.exists()

    with open(csv_2024, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1  # 1 commit in 2024
        assert rows[0]['hash'] == '2024_1'


def test_write_commits_by_year_single_year(tmp_path):
    """Test writing commits all from the same year."""
    from repo_analyzer.csv_writer import CSVWriter
    from repo_analyzer.models import CommitData

    commits = [
        CommitData(
            hash="commit1",
            author_name="Author",
            commit_date=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            lines_added=10,
            lines_deleted=5,
            version=None
        ),
        CommitData(
            hash="commit2",
            author_name="Author",
            commit_date=datetime(2024, 12, 15, 14, 0, 0, tzinfo=timezone.utc),
            lines_added=20,
            lines_deleted=10,
            version=None
        ),
    ]

    base_output_dir = tmp_path / "data"
    repo_name = "WordPress"

    CSVWriter.write_commits_by_year(commits, base_output_dir, repo_name)

    # Only 2024 folder should exist
    year_2024_dir = base_output_dir / "WordPress" / "2024"
    assert year_2024_dir.exists()

    year_2024_csv = year_2024_dir / "commits.csv"
    assert year_2024_csv.exists()

    with open(year_2024_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2


def test_write_commits_by_year_empty_list(tmp_path):
    """Test writing empty commits list creates no folders."""
    from repo_analyzer.csv_writer import CSVWriter

    base_output_dir = tmp_path / "data"
    repo_name = "WordPress"

    CSVWriter.write_commits_by_year([], base_output_dir, repo_name)

    # No directories should be created for empty list
    if base_output_dir.exists():
        assert len(list(base_output_dir.iterdir())) == 0


def test_write_rolling_aggregates_creates_file(output_dir):
    """Test that write_rolling_aggregates creates a CSV file."""
    from repo_analyzer.csv_writer import CSVWriter
    from repo_analyzer.models import RollingWindowAggregate

    rolling_aggregates = [
        RollingWindowAggregate(
            window_start=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            window_end=datetime(2024, 3, 24, 23, 59, 59, tzinfo=timezone.utc),
            total_commits=564,
            unique_authors=45,
            total_lines_added=15234,
            total_lines_deleted=3421,
            versions_released=["6.4.1", "6.4.2"]
        )
    ]

    output_path = output_dir / "rolling_window_aggregates.csv"
    CSVWriter.write_rolling_aggregates(rolling_aggregates, output_path)

    assert output_path.exists()


def test_write_rolling_aggregates_csv_structure(output_dir):
    """Test that rolling aggregates CSV has correct headers."""
    from repo_analyzer.csv_writer import CSVWriter
    from repo_analyzer.models import RollingWindowAggregate

    rolling_aggregates = [
        RollingWindowAggregate(
            window_start=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            window_end=datetime(2024, 3, 24, 23, 59, 59, tzinfo=timezone.utc),
            total_commits=564,
            unique_authors=45,
            total_lines_added=15234,
            total_lines_deleted=3421,
            versions_released=["6.4.1", "6.4.2"]
        )
    ]

    output_path = output_dir / "rolling_window_aggregates.csv"
    CSVWriter.write_rolling_aggregates(rolling_aggregates, output_path)

    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

        expected_headers = [
            'window_start',
            'window_end',
            'total_commits',
            'unique_authors',
            'total_lines_added',
            'total_lines_deleted',
            'versions_released'
        ]

        assert headers == expected_headers


def test_write_rolling_aggregates_data_content(output_dir):
    """Test that rolling aggregates CSV contains correct data."""
    from repo_analyzer.csv_writer import CSVWriter
    from repo_analyzer.models import RollingWindowAggregate

    rolling_aggregates = [
        RollingWindowAggregate(
            window_start=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            window_end=datetime(2024, 3, 24, 23, 59, 59, tzinfo=timezone.utc),
            total_commits=564,
            unique_authors=45,
            total_lines_added=15234,
            total_lines_deleted=3421,
            versions_released=["6.4.1", "6.4.2"]
        ),
        RollingWindowAggregate(
            window_start=datetime(2024, 1, 8, 0, 0, 0, tzinfo=timezone.utc),
            window_end=datetime(2024, 3, 31, 23, 59, 59, tzinfo=timezone.utc),
            total_commits=580,
            unique_authors=48,
            total_lines_added=16000,
            total_lines_deleted=3500,
            versions_released=[]
        )
    ]

    output_path = output_dir / "rolling_window_aggregates.csv"
    CSVWriter.write_rolling_aggregates(rolling_aggregates, output_path)

    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        assert len(rows) == 2

        # First window
        assert rows[0]['total_commits'] == '564'
        assert rows[0]['unique_authors'] == '45'
        assert rows[0]['total_lines_added'] == '15234'
        assert rows[0]['total_lines_deleted'] == '3421'
        assert rows[0]['versions_released'] == '6.4.1;6.4.2'

        # Second window without versions
        assert rows[1]['versions_released'] == ''


def test_write_rolling_aggregates_iso_date_format(output_dir):
    """Test that dates are formatted as ISO 8601."""
    from repo_analyzer.csv_writer import CSVWriter
    from repo_analyzer.models import RollingWindowAggregate

    rolling_aggregates = [
        RollingWindowAggregate(
            window_start=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            window_end=datetime(2024, 3, 24, 23, 59, 59, tzinfo=timezone.utc),
            total_commits=564,
            unique_authors=45,
            total_lines_added=15234,
            total_lines_deleted=3421,
            versions_released=[]
        )
    ]

    output_path = output_dir / "rolling_window_aggregates.csv"
    CSVWriter.write_rolling_aggregates(rolling_aggregates, output_path)

    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        row = next(reader)

        # ISO 8601 format
        assert row['window_start'] == '2024-01-01T00:00:00+00:00'
        assert row['window_end'] == '2024-03-24T23:59:59+00:00'


def test_write_rolling_aggregates_empty_list(output_dir):
    """Test writing empty rolling aggregates list creates file with headers only."""
    from repo_analyzer.csv_writer import CSVWriter

    output_path = output_dir / "rolling_window_aggregates.csv"
    CSVWriter.write_rolling_aggregates([], output_path)

    assert output_path.exists()

    with open(output_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        assert len(rows) == 0
        assert reader.fieldnames is not None


def test_write_rolling_aggregates_utf8_encoding(output_dir):
    """Test that UTF-8 encoding is used for rolling aggregates."""
    from repo_analyzer.csv_writer import CSVWriter
    from repo_analyzer.models import RollingWindowAggregate

    rolling_aggregates = [
        RollingWindowAggregate(
            window_start=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
            window_end=datetime(2024, 3, 24, 23, 59, 59, tzinfo=timezone.utc),
            total_commits=100,
            unique_authors=10,
            total_lines_added=1000,
            total_lines_deleted=500,
            versions_released=["6.4.1"]
        )
    ]

    output_path = output_dir / "rolling_window_aggregates.csv"
    CSVWriter.write_rolling_aggregates(rolling_aggregates, output_path)

    # Verify file can be read with UTF-8 encoding
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
        assert len(content) > 0
