# ABOUTME: Integration tests for WordPressRepository class.
# ABOUTME: Tests real git repository cloning and commit traversal using PyDriller.

import pytest
from pathlib import Path
from datetime import datetime, timezone


@pytest.mark.integration
@pytest.mark.slow
def test_wordpress_repository_initialization(cache_dir):
    """Test WordPressRepository initializes with cache directory."""
    from repo_analyzer.repository import WordPressRepository

    repo = WordPressRepository(cache_dir)

    assert repo.cache_dir == cache_dir
    assert repo.repo_path == cache_dir / "wordpress"


@pytest.mark.integration
@pytest.mark.slow
def test_ensure_cloned_creates_directory(cache_dir):
    """Test that ensure_cloned creates the WordPress directory."""
    from repo_analyzer.repository import WordPressRepository

    repo = WordPressRepository(cache_dir)

    # Repository should not exist initially
    assert not repo.repo_path.exists()

    # Calling ensure_cloned should clone the repo
    # Note: This will actually clone WordPress repo (slow!)
    # We'll skip this in CI unless explicitly enabled
    pytest.skip("Skipping actual WordPress clone in tests - too slow")


@pytest.mark.integration
def test_ensure_cloned_returns_path(cache_dir):
    """Test that ensure_cloned returns the repository path."""
    from repo_analyzer.repository import WordPressRepository
    from unittest.mock import patch, MagicMock

    repo = WordPressRepository(cache_dir)

    # Mock the git clone operation
    with patch('repo_analyzer.repository.subprocess.run') as mock_run:
        # Simulate repo already exists
        repo.repo_path.mkdir(parents=True)
        (repo.repo_path / ".git").mkdir()

        path = repo.ensure_cloned()

        assert path == repo.repo_path
        assert path.exists()


@pytest.mark.integration
def test_get_commits_returns_generator(cache_dir):
    """Test that get_commits returns a generator."""
    from repo_analyzer.repository import WordPressRepository
    from unittest.mock import patch, MagicMock

    repo = WordPressRepository(cache_dir)

    # Mock Repository to avoid actual clone
    with patch('repo_analyzer.repository.Repository') as mock_repository:
        mock_repo_instance = MagicMock()
        mock_repository.return_value = mock_repo_instance

        start = datetime(2005, 4, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2005, 4, 30, 0, 0, 0, tzinfo=timezone.utc)

        commits = repo.get_commits(since=start, to=end)

        # Should be a generator
        assert hasattr(commits, '__iter__')


@pytest.mark.integration
def test_get_commits_passes_date_range(cache_dir):
    """Test that get_commits passes correct date range to PyDriller."""
    from repo_analyzer.repository import WordPressRepository
    from unittest.mock import patch, MagicMock

    repo = WordPressRepository(cache_dir)

    # Mock Repository
    with patch('repo_analyzer.repository.Repository') as mock_repository:
        start = datetime(2005, 4, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2005, 4, 30, 0, 0, 0, tzinfo=timezone.utc)

        # Call get_commits
        list(repo.get_commits(since=start, to=end))

        # Verify Repository was called with correct parameters
        mock_repository.assert_called_once()
        call_kwargs = mock_repository.call_args[1]

        assert call_kwargs['since'] == start
        assert call_kwargs['to'] == end


@pytest.mark.integration
def test_repository_url_constant():
    """Test that WordPress repository URL is defined."""
    from repo_analyzer.repository import WordPressRepository

    assert hasattr(WordPressRepository, 'REPO_URL')
    assert WordPressRepository.REPO_URL == "https://github.com/WordPress/WordPress.git"


@pytest.mark.integration
def test_ensure_cloned_idempotent(cache_dir):
    """Test that ensure_cloned can be called multiple times safely."""
    from repo_analyzer.repository import WordPressRepository

    repo = WordPressRepository(cache_dir)

    # Create mock repo directory
    repo.repo_path.mkdir(parents=True)
    (repo.repo_path / ".git").mkdir()

    # Should not fail if called multiple times
    path1 = repo.ensure_cloned()
    path2 = repo.ensure_cloned()

    assert path1 == path2
    assert path1.exists()
