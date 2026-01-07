# ABOUTME: Manages git repository cloning and provides PyDriller interface.
# ABOUTME: Handles lazy cloning, validation, and commit traversal with date filtering.

import subprocess
from pathlib import Path
from datetime import datetime
from pydriller import Repository


class GitRepository:
    """Generic git repository handler for any repository."""

    def __init__(self, repo_url: str, cache_dir: Path, repo_name: str):
        """Initialize GitRepository with URL, cache directory, and name.

        Args:
            repo_url: Git repository URL to clone
            cache_dir: Directory to cache the cloned repository
            repo_name: Repository name for organization
        """
        self.repo_url = repo_url
        self.cache_dir = cache_dir
        self.repo_name = repo_name
        # Sanitize repo_name for filesystem: lowercase, replace / with _
        sanitized_name = repo_name.lower().replace("/", "_")
        self.repo_path = cache_dir / sanitized_name

    def ensure_cloned(self) -> Path:
        """Clone repository if not present, return path.

        Returns:
            Path to the cloned repository

        Raises:
            RuntimeError: If cloning fails
        """
        # Check if repository already exists and is valid
        if self._is_valid_repo():
            # Repository exists - update it to get latest commits
            try:
                subprocess.run(
                    ["git", "-C", str(self.repo_path), "pull", "--ff-only"],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except subprocess.CalledProcessError:
                # Pull failed, but repo still valid - continue with existing commits
                pass
            return self.repo_path

        # Clone the repository
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        try:
            subprocess.run(
                ["git", "clone", self.repo_url, str(self.repo_path)],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Failed to clone repository from {self.repo_url}: {e.stderr}"
            ) from e

        return self.repo_path

    def _is_valid_repo(self) -> bool:
        """Check if repo_path exists and is a valid git repository.

        Returns:
            True if repository is valid, False otherwise
        """
        if not self.repo_path.exists():
            return False

        git_dir = self.repo_path / ".git"
        return git_dir.exists()

    def get_commits(self, since: datetime, to: datetime):
        """Yield commits in date range using PyDriller.

        Args:
            since: Start date (inclusive)
            to: End date (inclusive)

        Yields:
            PyDriller Commit objects in the date range
        """
        # Repository should be cloned before calling this
        # But we don't enforce it here to allow flexible usage

        repo = Repository(
            path_to_repo=str(self.repo_path),
            since=since,
            to=to
        )

        for commit in repo.traverse_commits():
            yield commit


class WordPressRepository(GitRepository):
    """WordPress repository with preconfigured URL.

    Convenience subclass of GitRepository for WordPress repository analysis.
    """

    REPO_URL = "https://github.com/WordPress/WordPress.git"

    def __init__(self, cache_dir: Path):
        """Initialize WordPressRepository with cache directory.

        Args:
            cache_dir: Directory to cache the cloned repository
        """
        super().__init__(self.REPO_URL, cache_dir, "wordpress")
