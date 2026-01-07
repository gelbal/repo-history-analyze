# ABOUTME: Unit tests for CommitExtractor class.
# ABOUTME: Tests PyDriller commit conversion to CommitData objects.

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock


def test_extractor_initialization():
    """Test CommitExtractor initializes with a VersionMapper."""
    from repo_analyzer.extractor import CommitExtractor
    from repo_analyzer.version_mapper import VersionMapper

    mock_version_mapper = MagicMock(spec=VersionMapper)

    extractor = CommitExtractor(mock_version_mapper)

    assert extractor.version_mapper == mock_version_mapper


def test_extract_commit_with_version(mock_pydriller_commit):
    """Test extracting CommitData from PyDriller commit with version."""
    from repo_analyzer.extractor import CommitExtractor
    from repo_analyzer.version_mapper import VersionMapper

    # Setup mock version mapper to return a version
    mock_version_mapper = MagicMock(spec=VersionMapper)
    mock_version_mapper.get_version_for_commit.return_value = "1.5"

    extractor = CommitExtractor(mock_version_mapper)
    result = extractor.extract(mock_pydriller_commit)

    assert result.hash == "abc123"
    assert result.author_name == "John Doe"
    assert result.commit_date == datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc)
    assert result.lines_added == 42
    assert result.lines_deleted == 7
    assert result.version == "1.5"

    # Verify version mapper was called with correct hash
    mock_version_mapper.get_version_for_commit.assert_called_once_with("abc123")


def test_extract_commit_without_version(mock_pydriller_commit):
    """Test extracting CommitData from PyDriller commit without version."""
    from repo_analyzer.extractor import CommitExtractor
    from repo_analyzer.version_mapper import VersionMapper

    # Setup mock version mapper to return None
    mock_version_mapper = MagicMock(spec=VersionMapper)
    mock_version_mapper.get_version_for_commit.return_value = None

    extractor = CommitExtractor(mock_version_mapper)
    result = extractor.extract(mock_pydriller_commit)

    assert result.hash == "abc123"
    assert result.author_name == "John Doe"
    assert result.commit_date == datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc)
    assert result.lines_added == 42
    assert result.lines_deleted == 7
    assert result.version is None


def test_extract_commit_with_zero_lines():
    """Test extracting commit with zero lines changed."""
    from repo_analyzer.extractor import CommitExtractor
    from repo_analyzer.version_mapper import VersionMapper

    mock_commit = MagicMock()
    mock_commit.hash = "zero123"
    mock_commit.author.name = "Zero Author"
    mock_commit.author_date = datetime(2005, 4, 10, 10, 0, 0, tzinfo=timezone.utc)
    mock_commit.insertions = 0
    mock_commit.deletions = 0

    mock_version_mapper = MagicMock(spec=VersionMapper)
    mock_version_mapper.get_version_for_commit.return_value = None

    extractor = CommitExtractor(mock_version_mapper)
    result = extractor.extract(mock_commit)

    assert result.lines_added == 0
    assert result.lines_deleted == 0


def test_extract_commit_with_unicode_author():
    """Test extracting commit with unicode characters in author name."""
    from repo_analyzer.extractor import CommitExtractor
    from repo_analyzer.version_mapper import VersionMapper

    mock_commit = MagicMock()
    mock_commit.hash = "unicode123"
    mock_commit.author.name = "Müller José 李明"
    mock_commit.author_date = datetime(2005, 4, 15, 15, 0, 0, tzinfo=timezone.utc)
    mock_commit.insertions = 50
    mock_commit.deletions = 10

    mock_version_mapper = MagicMock(spec=VersionMapper)
    mock_version_mapper.get_version_for_commit.return_value = None

    extractor = CommitExtractor(mock_version_mapper)
    result = extractor.extract(mock_commit)

    assert result.author_name == "Müller José 李明"


def test_extract_commit_with_large_changes():
    """Test extracting commit with large number of line changes."""
    from repo_analyzer.extractor import CommitExtractor
    from repo_analyzer.version_mapper import VersionMapper

    mock_commit = MagicMock()
    mock_commit.hash = "large123"
    mock_commit.author.name = "Large Change Author"
    mock_commit.author_date = datetime(2005, 4, 20, 20, 0, 0, tzinfo=timezone.utc)
    mock_commit.insertions = 10000
    mock_commit.deletions = 5000

    mock_version_mapper = MagicMock(spec=VersionMapper)
    mock_version_mapper.get_version_for_commit.return_value = "2.0"

    extractor = CommitExtractor(mock_version_mapper)
    result = extractor.extract(mock_commit)

    assert result.lines_added == 10000
    assert result.lines_deleted == 5000
    assert result.version == "2.0"


def test_extract_preserves_timezone():
    """Test that extraction preserves timezone information."""
    from repo_analyzer.extractor import CommitExtractor
    from repo_analyzer.version_mapper import VersionMapper

    # Create commit with specific timezone
    mock_commit = MagicMock()
    mock_commit.hash = "tz123"
    mock_commit.author.name = "TZ Author"
    mock_commit.author_date = datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc)
    mock_commit.insertions = 10
    mock_commit.deletions = 5

    mock_version_mapper = MagicMock(spec=VersionMapper)
    mock_version_mapper.get_version_for_commit.return_value = None

    extractor = CommitExtractor(mock_version_mapper)
    result = extractor.extract(mock_commit)

    # Verify timezone is preserved
    assert result.commit_date.tzinfo is not None
    assert result.commit_date.tzinfo == timezone.utc


def test_extract_multiple_commits():
    """Test extracting multiple commits sequentially."""
    from repo_analyzer.extractor import CommitExtractor
    from repo_analyzer.version_mapper import VersionMapper

    mock_commit1 = MagicMock()
    mock_commit1.hash = "commit1"
    mock_commit1.author.name = "Author 1"
    mock_commit1.author_date = datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc)
    mock_commit1.insertions = 10
    mock_commit1.deletions = 5

    mock_commit2 = MagicMock()
    mock_commit2.hash = "commit2"
    mock_commit2.author.name = "Author 2"
    mock_commit2.author_date = datetime(2005, 4, 6, 13, 0, 0, tzinfo=timezone.utc)
    mock_commit2.insertions = 20
    mock_commit2.deletions = 10

    mock_version_mapper = MagicMock(spec=VersionMapper)
    mock_version_mapper.get_version_for_commit.side_effect = ["1.5", None]

    extractor = CommitExtractor(mock_version_mapper)

    result1 = extractor.extract(mock_commit1)
    result2 = extractor.extract(mock_commit2)

    assert result1.hash == "commit1"
    assert result1.version == "1.5"
    assert result2.hash == "commit2"
    assert result2.version is None
