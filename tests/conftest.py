# ABOUTME: Shared pytest fixtures for all tests.
# ABOUTME: Provides temporary directories and sample data for testing.

import pytest
from pathlib import Path
from datetime import datetime, timezone
from typing import List


@pytest.fixture
def cache_dir(tmp_path: Path) -> Path:
    """Temporary cache directory for tests."""
    cache = tmp_path / "cache"
    cache.mkdir()
    return cache


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Temporary output directory for tests."""
    output = tmp_path / "data"
    output.mkdir()
    return output


@pytest.fixture
def sample_commits():
    """Sample CommitData objects for testing."""
    from repo_analyzer.models import CommitData

    # Create commits spanning multiple weeks
    return [
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
            version=None
        ),
        CommitData(
            hash="jkl012",
            author_name="Alice Johnson",
            commit_date=datetime(2005, 4, 13, 16, 45, 0, tzinfo=timezone.utc),
            lines_added=91,
            lines_deleted=25,
            version="1.5.1"
        ),
    ]


@pytest.fixture
def mock_pydriller_commit():
    """Mock PyDriller commit object."""
    from unittest.mock import MagicMock

    commit = MagicMock()
    commit.hash = "abc123"
    commit.author.name = "John Doe"
    commit.author_date = datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc)
    commit.insertions = 42
    commit.deletions = 7

    return commit
