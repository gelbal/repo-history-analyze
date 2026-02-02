# ABOUTME: JSON-based persistent cache for SVN diff statistics.
# ABOUTME: Stores lines added/deleted per revision to avoid re-fetching.

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class DiffCacheEntry:
    """Represents cached diff statistics for a single SVN revision.

    Attributes:
        revision: SVN revision number.
        lines_added: Number of lines added in this revision.
        lines_deleted: Number of lines deleted in this revision.
        fetched_at: ISO 8601 timestamp when the diff was fetched.
    """

    revision: int
    lines_added: int
    lines_deleted: int
    fetched_at: str

    def to_dict(self) -> Dict:
        """Convert entry to dictionary for JSON serialization."""
        return {
            "revision": self.revision,
            "lines_added": self.lines_added,
            "lines_deleted": self.lines_deleted,
            "fetched_at": self.fetched_at,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "DiffCacheEntry":
        """Create entry from dictionary."""
        return cls(
            revision=data["revision"],
            lines_added=data["lines_added"],
            lines_deleted=data["lines_deleted"],
            fetched_at=data["fetched_at"],
        )


class SVNDiffCache:
    """Persistent cache for SVN diff statistics.

    Stores diff stats (lines added/deleted) keyed by revision number.
    Cache is persisted as JSON file organized by repository URL hash.

    Cache structure:
        {cache_dir}/svn/{repo_hash}.json
    """

    def __init__(self, cache_dir: Path, repo_url: str) -> None:
        """Initialize cache for a specific repository.

        Args:
            cache_dir: Base directory for cache files.
            repo_url: SVN repository URL (used for cache key).
        """
        self._cache_dir = Path(cache_dir)
        self._repo_url = repo_url.rstrip("/")
        self._repo_hash = self._hash_url(self._repo_url)
        self._entries: Dict[int, DiffCacheEntry] = {}

    def _hash_url(self, url: str) -> str:
        """Create consistent hash from repository URL."""
        normalized = url.lower().rstrip("/")
        return hashlib.md5(normalized.encode()).hexdigest()[:12]

    @property
    def cache_path(self) -> Path:
        """Path to the cache JSON file."""
        return self._cache_dir / "svn" / f"{self._repo_hash}.json"

    @property
    def size(self) -> int:
        """Number of entries in the cache."""
        return len(self._entries)

    def get(self, revision: int) -> Optional[DiffCacheEntry]:
        """Get cached entry for a revision.

        Args:
            revision: SVN revision number.

        Returns:
            DiffCacheEntry if cached, None otherwise.
        """
        return self._entries.get(revision)

    def put(self, revision: int, lines_added: int, lines_deleted: int) -> None:
        """Store diff stats for a revision.

        Args:
            revision: SVN revision number.
            lines_added: Number of lines added.
            lines_deleted: Number of lines deleted.
        """
        entry = DiffCacheEntry(
            revision=revision,
            lines_added=lines_added,
            lines_deleted=lines_deleted,
            fetched_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )
        self._entries[revision] = entry

    def has(self, revision: int) -> bool:
        """Check if revision is cached.

        Args:
            revision: SVN revision number.

        Returns:
            True if revision is cached, False otherwise.
        """
        return revision in self._entries

    def get_uncached_revisions(self, revisions: List[int]) -> List[int]:
        """Filter list to only uncached revisions.

        Args:
            revisions: List of revision numbers to check.

        Returns:
            List of revisions not in cache.
        """
        return [r for r in revisions if not self.has(r)]

    def save(self) -> None:
        """Persist cache to disk.

        Creates parent directories if needed.
        Uses atomic write (temp file + rename) for safety.
        """
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            str(rev): entry.to_dict()
            for rev, entry in self._entries.items()
        }

        # Write to temp file first for atomic operation
        temp_path = self.cache_path.with_suffix(".tmp")
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=2)

        # Atomic rename
        temp_path.rename(self.cache_path)

    def load(self) -> None:
        """Load cache from disk.

        Creates empty cache if file doesn't exist.
        """
        if not self.cache_path.exists():
            self._entries = {}
            return

        with open(self.cache_path) as f:
            data = json.load(f)

        self._entries = {
            int(rev): DiffCacheEntry.from_dict(entry_data)
            for rev, entry_data in data.items()
        }
