# ABOUTME: Unit tests for SVN diff cache module.
# ABOUTME: Tests JSON-based persistent caching of diff statistics.

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from repo_analyzer.svn.diff_cache import DiffCacheEntry, SVNDiffCache


class TestDiffCacheEntry:
    """Tests for DiffCacheEntry dataclass."""

    def test_create_entry(self):
        """Creates entry with all required fields."""
        entry = DiffCacheEntry(
            revision=12345,
            lines_added=42,
            lines_deleted=7,
            fetched_at="2024-01-15T10:30:00Z",
        )

        assert entry.revision == 12345
        assert entry.lines_added == 42
        assert entry.lines_deleted == 7
        assert entry.fetched_at == "2024-01-15T10:30:00Z"

    def test_entry_to_dict(self):
        """Entry can be converted to dict for JSON serialization."""
        entry = DiffCacheEntry(
            revision=100,
            lines_added=10,
            lines_deleted=5,
            fetched_at="2024-01-01T00:00:00Z",
        )

        d = entry.to_dict()

        assert d["revision"] == 100
        assert d["lines_added"] == 10
        assert d["lines_deleted"] == 5
        assert d["fetched_at"] == "2024-01-01T00:00:00Z"

    def test_entry_from_dict(self):
        """Entry can be created from dict."""
        d = {
            "revision": 100,
            "lines_added": 10,
            "lines_deleted": 5,
            "fetched_at": "2024-01-01T00:00:00Z",
        }

        entry = DiffCacheEntry.from_dict(d)

        assert entry.revision == 100
        assert entry.lines_added == 10
        assert entry.lines_deleted == 5


class TestSVNDiffCache:
    """Tests for SVNDiffCache class."""

    def test_init_creates_repo_hash(self):
        """Cache creates consistent hash from repo URL."""
        cache1 = SVNDiffCache(Path("/tmp/cache"), "https://example.com/repo/")
        cache2 = SVNDiffCache(Path("/tmp/cache"), "https://example.com/repo")
        cache3 = SVNDiffCache(Path("/tmp/cache"), "https://other.com/repo/")

        assert cache1._repo_hash == cache2._repo_hash
        assert cache1._repo_hash != cache3._repo_hash

    def test_cache_path(self):
        """Cache path is constructed from cache_dir and repo hash."""
        cache = SVNDiffCache(Path("/tmp/cache"), "https://example.com/repo/")

        assert cache.cache_path.parent == Path("/tmp/cache/svn")
        assert cache.cache_path.name == f"{cache._repo_hash}.json"

    def test_put_and_get(self, tmp_path):
        """Put stores entry and get retrieves it."""
        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")

        cache.put(12345, lines_added=42, lines_deleted=7)
        entry = cache.get(12345)

        assert entry is not None
        assert entry.revision == 12345
        assert entry.lines_added == 42
        assert entry.lines_deleted == 7

    def test_get_nonexistent_returns_none(self, tmp_path):
        """Get returns None for non-existent revision."""
        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")

        entry = cache.get(99999)

        assert entry is None

    def test_has_returns_true_for_existing(self, tmp_path):
        """Has returns True for existing revision."""
        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")
        cache.put(12345, lines_added=10, lines_deleted=5)

        assert cache.has(12345) is True

    def test_has_returns_false_for_nonexistent(self, tmp_path):
        """Has returns False for non-existent revision."""
        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")

        assert cache.has(99999) is False

    def test_save_creates_cache_file(self, tmp_path):
        """Save creates JSON file on disk."""
        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")
        cache.put(100, lines_added=10, lines_deleted=5)
        cache.put(200, lines_added=20, lines_deleted=10)

        cache.save()

        assert cache.cache_path.exists()
        with open(cache.cache_path) as f:
            data = json.load(f)
        assert "100" in data
        assert "200" in data

    def test_load_reads_existing_cache(self, tmp_path):
        """Load reads entries from existing cache file."""
        cache_dir = tmp_path / "svn"
        cache_dir.mkdir(parents=True)

        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")
        cache_file = cache.cache_path

        # Write cache file directly
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "100": {
                "revision": 100,
                "lines_added": 10,
                "lines_deleted": 5,
                "fetched_at": "2024-01-01T00:00:00Z",
            },
        }
        with open(cache_file, "w") as f:
            json.dump(data, f)

        # Load and verify
        cache.load()
        entry = cache.get(100)

        assert entry is not None
        assert entry.lines_added == 10

    def test_load_empty_cache_on_missing_file(self, tmp_path):
        """Load creates empty cache if file doesn't exist."""
        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")

        cache.load()

        assert cache.get(100) is None

    def test_save_creates_parent_directories(self, tmp_path):
        """Save creates parent directories if needed."""
        cache_dir = tmp_path / "deep" / "nested" / "path"
        cache = SVNDiffCache(cache_dir, "https://example.com/repo/")
        cache.put(100, lines_added=10, lines_deleted=5)

        cache.save()

        assert cache.cache_path.exists()

    def test_put_sets_fetched_at_timestamp(self, tmp_path):
        """Put automatically sets fetched_at timestamp."""
        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")

        cache.put(100, lines_added=10, lines_deleted=5)
        entry = cache.get(100)

        assert entry.fetched_at is not None
        # Verify it's a valid ISO timestamp
        datetime.fromisoformat(entry.fetched_at.replace("Z", "+00:00"))

    def test_cache_persistence_roundtrip(self, tmp_path):
        """Cache survives save and load roundtrip."""
        cache1 = SVNDiffCache(tmp_path, "https://example.com/repo/")
        cache1.put(100, lines_added=10, lines_deleted=5)
        cache1.put(200, lines_added=20, lines_deleted=10)
        cache1.save()

        # Create new cache instance and load
        cache2 = SVNDiffCache(tmp_path, "https://example.com/repo/")
        cache2.load()

        assert cache2.has(100)
        assert cache2.has(200)
        assert cache2.get(100).lines_added == 10
        assert cache2.get(200).lines_deleted == 10

    def test_get_uncached_revisions(self, tmp_path):
        """Returns list of revisions not in cache."""
        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")
        cache.put(100, lines_added=10, lines_deleted=5)
        cache.put(300, lines_added=30, lines_deleted=15)

        uncached = cache.get_uncached_revisions([100, 200, 300, 400])

        assert uncached == [200, 400]

    def test_get_uncached_revisions_empty_cache(self, tmp_path):
        """All revisions are uncached when cache is empty."""
        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")

        uncached = cache.get_uncached_revisions([100, 200, 300])

        assert uncached == [100, 200, 300]

    def test_cache_size(self, tmp_path):
        """Returns number of cached entries."""
        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")

        assert cache.size == 0

        cache.put(100, lines_added=10, lines_deleted=5)
        assert cache.size == 1

        cache.put(200, lines_added=20, lines_deleted=10)
        assert cache.size == 2
