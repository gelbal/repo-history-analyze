# ABOUTME: Unit tests for generic GitRepository class and repository abstraction.
# ABOUTME: Tests repository initialization, URL handling, and WordPressRepository subclass.

import pytest
from pathlib import Path
from repo_analyzer.repository import GitRepository, WordPressRepository


class TestGitRepository:
    """Tests for generic GitRepository class."""

    def test_init_with_standard_repo_name(self, tmp_path):
        """Test GitRepository initialization with standard repo name."""
        repo_url = "https://github.com/torvalds/linux.git"
        repo_name = "linux"

        repo = GitRepository(repo_url, tmp_path, repo_name)

        assert repo.repo_url == repo_url
        assert repo.cache_dir == tmp_path
        assert repo.repo_name == repo_name
        assert repo.repo_path == tmp_path / "linux"

    def test_init_with_mixed_case_repo_name(self, tmp_path):
        """Test GitRepository converts repo name to lowercase."""
        repo_url = "https://github.com/WordPress/WordPress.git"
        repo_name = "WordPress"

        repo = GitRepository(repo_url, tmp_path, repo_name)

        assert repo.repo_name == repo_name
        assert repo.repo_path == tmp_path / "wordpress"

    def test_init_with_special_chars_in_repo_name(self, tmp_path):
        """Test GitRepository sanitizes special characters in repo name."""
        repo_url = "https://github.com/foo/bar.git"
        repo_name = "foo/bar"

        repo = GitRepository(repo_url, tmp_path, repo_name)

        assert repo.repo_name == "foo/bar"
        assert repo.repo_path == tmp_path / "foo_bar"

    def test_init_with_dots_in_repo_name(self, tmp_path):
        """Test GitRepository handles dots in repo name."""
        repo_url = "https://github.com/foo/bar.js.git"
        repo_name = "bar.js"

        repo = GitRepository(repo_url, tmp_path, repo_name)

        assert repo.repo_path == tmp_path / "bar.js"

    def test_init_with_hyphens_in_repo_name(self, tmp_path):
        """Test GitRepository handles hyphens in repo name."""
        repo_url = "https://github.com/foo/my-repo.git"
        repo_name = "my-repo"

        repo = GitRepository(repo_url, tmp_path, repo_name)

        assert repo.repo_path == tmp_path / "my-repo"

    def test_has_ensure_cloned_method(self, tmp_path):
        """Test GitRepository has ensure_cloned method."""
        repo = GitRepository("https://github.com/test/test.git", tmp_path, "test")

        assert hasattr(repo, 'ensure_cloned')
        assert callable(repo.ensure_cloned)

    def test_has_get_commits_method(self, tmp_path):
        """Test GitRepository has get_commits method."""
        repo = GitRepository("https://github.com/test/test.git", tmp_path, "test")

        assert hasattr(repo, 'get_commits')
        assert callable(repo.get_commits)

    def test_has_is_valid_repo_method(self, tmp_path):
        """Test GitRepository has _is_valid_repo method."""
        repo = GitRepository("https://github.com/test/test.git", tmp_path, "test")

        assert hasattr(repo, '_is_valid_repo')
        assert callable(repo._is_valid_repo)


class TestWordPressRepository:
    """Tests for WordPressRepository subclass."""

    def test_wordpress_repository_has_default_url(self):
        """Test WordPressRepository has correct default URL."""
        assert WordPressRepository.REPO_URL == "https://github.com/WordPress/WordPress.git"

    def test_wordpress_repository_init(self, tmp_path):
        """Test WordPressRepository initialization."""
        repo = WordPressRepository(tmp_path)

        assert repo.repo_url == "https://github.com/WordPress/WordPress.git"
        assert repo.cache_dir == tmp_path
        assert repo.repo_name == "wordpress"
        assert repo.repo_path == tmp_path / "wordpress"

    def test_wordpress_repository_is_git_repository_subclass(self, tmp_path):
        """Test WordPressRepository is a subclass of GitRepository."""
        repo = WordPressRepository(tmp_path)

        assert isinstance(repo, GitRepository)

    def test_backward_compatibility_with_existing_code(self, tmp_path):
        """Test WordPressRepository maintains backward compatibility."""
        # This ensures existing code using WordPressRepository continues to work
        repo = WordPressRepository(tmp_path)

        # Should have all required attributes
        assert hasattr(repo, 'cache_dir')
        assert hasattr(repo, 'repo_path')
        assert hasattr(repo, 'ensure_cloned')
        assert hasattr(repo, 'get_commits')

        # repo_path should be cache_dir / "wordpress"
        assert repo.repo_path == tmp_path / "wordpress"
