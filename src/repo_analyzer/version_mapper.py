# ABOUTME: Maps git tags to WordPress version numbers.
# ABOUTME: Provides lookup from commit hash to version and date range to versions.

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
from pydriller import Git


@dataclass(frozen=True)
class VersionTag:
    """Represents a WordPress version tag."""
    name: str
    commit_hash: str
    tagged_date: datetime


class VersionMapper:
    """Maps WordPress version tags to commits and dates."""

    # Pattern for WordPress version tags: digits and dots only (e.g., "1.5", "6.4.2")
    VERSION_PATTERN = re.compile(r'^\d+(\.\d+)*$')

    def __init__(self, repo_path: str):
        """Initialize VersionMapper with a repository path.

        Args:
            repo_path: Path to the git repository
        """
        self._repo_path = repo_path
        self._git = Git(repo_path)
        self._tags: Dict[str, VersionTag] = {}
        self._commit_to_version: Dict[str, str] = {}
        self._load_tags()

    def _load_tags(self) -> None:
        """Load all WordPress version tags from repository."""
        # Access the underlying GitPython repository object
        for tag in self._git.repo.tags:
            tag_name = tag.name

            # Filter for version tags only (numeric pattern like "6.4.2")
            if self._is_version_tag(tag_name):
                version_tag = VersionTag(
                    name=tag_name,
                    commit_hash=tag.commit.hexsha,
                    tagged_date=tag.commit.committed_datetime
                )

                self._tags[tag_name] = version_tag
                self._commit_to_version[tag.commit.hexsha] = tag_name

    def _is_version_tag(self, tag_name: str) -> bool:
        """Check if a tag name matches WordPress version pattern.

        Args:
            tag_name: Git tag name

        Returns:
            True if tag matches version pattern (e.g., "1.5", "6.4.2")
        """
        return bool(self.VERSION_PATTERN.match(tag_name))

    def get_version_for_commit(self, commit_hash: str) -> Optional[str]:
        """Return WordPress version if commit is tagged, else None.

        Args:
            commit_hash: Git commit hash

        Returns:
            Version string if commit is tagged, None otherwise
        """
        return self._commit_to_version.get(commit_hash)

    def get_versions_in_date_range(self, start: datetime, end: datetime) -> List[str]:
        """Return all versions released within date range.

        Args:
            start: Start of date range (inclusive)
            end: End of date range (inclusive)

        Returns:
            List of version strings released in the range
        """
        versions = []

        for version_tag in self._tags.values():
            if start <= version_tag.tagged_date <= end:
                versions.append(version_tag.name)

        return versions
