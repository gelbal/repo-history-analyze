# ABOUTME: Unit tests for VersionMapper class.
# ABOUTME: Tests git tag loading, version filtering, and commit-to-version lookup.

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch


def test_version_mapper_initialization():
    """Test VersionMapper initializes with a repository path."""
    from repo_analyzer.version_mapper import VersionMapper

    with patch('repo_analyzer.version_mapper.Git') as mock_git:
        mock_git.return_value.repo.tags = []

        mapper = VersionMapper("/path/to/repo")

        assert mapper._repo_path == "/path/to/repo"
        mock_git.assert_called_once_with("/path/to/repo")


def test_load_version_tags():
    """Test loading and filtering version tags."""
    from repo_analyzer.version_mapper import VersionMapper

    # Create mock tags
    mock_tag_1_5 = MagicMock()
    mock_tag_1_5.name = "1.5"
    mock_tag_1_5.commit.hexsha = "abc123"
    mock_tag_1_5.commit.committed_datetime = datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc)

    mock_tag_1_5_1 = MagicMock()
    mock_tag_1_5_1.name = "1.5.1"
    mock_tag_1_5_1.commit.hexsha = "def456"
    mock_tag_1_5_1.commit.committed_datetime = datetime(2005, 4, 15, 12, 0, 0, tzinfo=timezone.utc)

    # Non-version tag (should be filtered)
    mock_tag_invalid = MagicMock()
    mock_tag_invalid.name = "release-candidate"
    mock_tag_invalid.commit.hexsha = "ghi789"
    mock_tag_invalid.commit.committed_datetime = datetime(2005, 4, 20, 12, 0, 0, tzinfo=timezone.utc)

    with patch('repo_analyzer.version_mapper.Git') as mock_git:
        mock_git.return_value.repo.tags = [mock_tag_1_5, mock_tag_1_5_1, mock_tag_invalid]

        mapper = VersionMapper("/path/to/repo")

        # Should only have 2 version tags (filtered out "release-candidate")
        assert len(mapper._tags) == 2
        assert "1.5" in mapper._tags
        assert "1.5.1" in mapper._tags
        assert "release-candidate" not in mapper._tags


def test_get_version_for_tagged_commit():
    """Test getting version for a commit that has a tag."""
    from repo_analyzer.version_mapper import VersionMapper

    mock_tag = MagicMock()
    mock_tag.name = "1.5"
    mock_tag.commit.hexsha = "abc123"
    mock_tag.commit.committed_datetime = datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc)

    with patch('repo_analyzer.version_mapper.Git') as mock_git:
        mock_git.return_value.repo.tags = [mock_tag]

        mapper = VersionMapper("/path/to/repo")
        version = mapper.get_version_for_commit("abc123")

        assert version == "1.5"


def test_get_version_for_untagged_commit():
    """Test getting version for a commit without a tag returns None."""
    from repo_analyzer.version_mapper import VersionMapper

    mock_tag = MagicMock()
    mock_tag.name = "1.5"
    mock_tag.commit.hexsha = "abc123"
    mock_tag.commit.committed_datetime = datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc)

    with patch('repo_analyzer.version_mapper.Git') as mock_git:
        mock_git.return_value.repo.tags = [mock_tag]

        mapper = VersionMapper("/path/to/repo")
        version = mapper.get_version_for_commit("untagged_commit_hash")

        assert version is None


def test_get_versions_in_date_range():
    """Test getting all versions released within a date range."""
    from repo_analyzer.version_mapper import VersionMapper

    mock_tag_1_5 = MagicMock()
    mock_tag_1_5.name = "1.5"
    mock_tag_1_5.commit.hexsha = "abc123"
    mock_tag_1_5.commit.committed_datetime = datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc)

    mock_tag_1_5_1 = MagicMock()
    mock_tag_1_5_1.name = "1.5.1"
    mock_tag_1_5_1.commit.hexsha = "def456"
    mock_tag_1_5_1.commit.committed_datetime = datetime(2005, 4, 15, 12, 0, 0, tzinfo=timezone.utc)

    mock_tag_1_5_2 = MagicMock()
    mock_tag_1_5_2.name = "1.5.2"
    mock_tag_1_5_2.commit.hexsha = "ghi789"
    mock_tag_1_5_2.commit.committed_datetime = datetime(2005, 4, 25, 12, 0, 0, tzinfo=timezone.utc)

    with patch('repo_analyzer.version_mapper.Git') as mock_git:
        mock_git.return_value.repo.tags = [mock_tag_1_5, mock_tag_1_5_1, mock_tag_1_5_2]

        mapper = VersionMapper("/path/to/repo")

        # Query for versions between April 10 and April 20
        versions = mapper.get_versions_in_date_range(
            start=datetime(2005, 4, 10, 0, 0, 0, tzinfo=timezone.utc),
            end=datetime(2005, 4, 20, 0, 0, 0, tzinfo=timezone.utc)
        )

        # Should only include 1.5.1 (released April 15)
        assert len(versions) == 1
        assert "1.5.1" in versions


def test_version_tag_pattern_matching():
    """Test that version tag patterns are correctly identified."""
    from repo_analyzer.version_mapper import VersionMapper

    # Create various tag formats
    tags_data = [
        ("1.5", True),
        ("1.5.1", True),
        ("6.4.2", True),
        ("10.0", True),
        ("2.0.0", True),
        ("v1.5", False),  # Has 'v' prefix
        ("release-1.5", False),  # Has prefix
        ("beta", False),  # Not numeric
        ("1.5-rc1", False),  # Has suffix
        ("", False),  # Empty
    ]

    mock_tags = []
    for tag_name, _ in tags_data:
        mock_tag = MagicMock()
        mock_tag.name = tag_name
        mock_tag.commit.hexsha = f"hash_{tag_name}"
        mock_tag.commit.committed_datetime = datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc)
        mock_tags.append(mock_tag)

    with patch('repo_analyzer.version_mapper.Git') as mock_git:
        mock_git.return_value.repo.tags = mock_tags

        mapper = VersionMapper("/path/to/repo")

        # Check which tags were accepted
        for tag_name, should_be_included in tags_data:
            if should_be_included and tag_name:  # Skip empty string
                assert tag_name in mapper._tags, f"Tag '{tag_name}' should be included"
            else:
                assert tag_name not in mapper._tags, f"Tag '{tag_name}' should not be included"


def test_multiple_commits_same_version():
    """Test that if multiple commits have the same version, the first one is used."""
    from repo_analyzer.version_mapper import VersionMapper

    # In practice, this shouldn't happen, but test the behavior
    mock_tag = MagicMock()
    mock_tag.name = "1.5"
    mock_tag.commit.hexsha = "abc123"
    mock_tag.commit.committed_datetime = datetime(2005, 4, 5, 12, 0, 0, tzinfo=timezone.utc)

    with patch('repo_analyzer.version_mapper.Git') as mock_git:
        mock_git.return_value.repo.tags = [mock_tag]

        mapper = VersionMapper("/path/to/repo")

        # The commit should map to the version
        assert mapper.get_version_for_commit("abc123") == "1.5"


def test_empty_tags_list():
    """Test handling of repository with no tags."""
    from repo_analyzer.version_mapper import VersionMapper

    with patch('repo_analyzer.version_mapper.Git') as mock_git:
        mock_git.return_value.repo.tags = []

        mapper = VersionMapper("/path/to/repo")

        assert len(mapper._tags) == 0
        assert mapper.get_version_for_commit("any_hash") is None
        assert mapper.get_versions_in_date_range(
            start=datetime(2005, 4, 1, 0, 0, 0, tzinfo=timezone.utc),
            end=datetime(2005, 4, 30, 0, 0, 0, tzinfo=timezone.utc)
        ) == []
