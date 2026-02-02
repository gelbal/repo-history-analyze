# ABOUTME: Batch fetching and parsing of SVN diffs.
# ABOUTME: Extracts line change statistics from unified diff output.

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from repo_analyzer.svn.diff_cache import SVNDiffCache
from repo_analyzer.svn.repository import SVNRepository


@dataclass(frozen=True)
class DiffStats:
    """Statistics extracted from a unified diff.

    Attributes:
        lines_added: Number of lines added.
        lines_deleted: Number of lines deleted.
    """

    lines_added: int
    lines_deleted: int

    @property
    def total_changes(self) -> int:
        """Total number of changed lines."""
        return self.lines_added + self.lines_deleted


class SVNDiffFetcher:
    """Fetches and parses SVN diffs with caching support.

    Uses SVNRepository to fetch unified diffs and parses them to extract
    line change statistics. Results are cached to avoid re-fetching.
    """

    # Pattern to match unified diff header lines (--- and +++)
    _HEADER_PATTERN = re.compile(r"^(\+\+\+|---).*$")

    # Pattern to match property change sections
    _PROPERTY_SECTION_PATTERN = re.compile(r"^Property changes on:")

    def __init__(self, repo: SVNRepository, cache: SVNDiffCache) -> None:
        """Initialize fetcher with repository and cache.

        Args:
            repo: SVNRepository instance for fetching diffs.
            cache: SVNDiffCache instance for caching results.
        """
        self._repo = repo
        self._cache = cache

    def parse_unified_diff(self, diff_output: str) -> DiffStats:
        """Parse unified diff output to extract line statistics.

        Counts lines starting with + (additions) and - (deletions),
        excluding header lines (--- and +++).

        Args:
            diff_output: Unified diff output string.

        Returns:
            DiffStats with lines_added and lines_deleted.
        """
        if not diff_output:
            return DiffStats(lines_added=0, lines_deleted=0)

        lines_added = 0
        lines_deleted = 0
        in_property_section = False

        for line in diff_output.split("\n"):
            # Skip property change sections
            if self._PROPERTY_SECTION_PATTERN.match(line):
                in_property_section = True
                continue

            # Reset property section flag when we see a new file index or diff hunk
            if line.startswith("Index:") or line.startswith("@@"):
                in_property_section = False

            # Skip lines in property sections
            if in_property_section:
                continue

            # Skip header lines
            if self._HEADER_PATTERN.match(line):
                continue

            # Count additions (lines starting with +)
            if line.startswith("+"):
                lines_added += 1
            # Count deletions (lines starting with -)
            elif line.startswith("-"):
                lines_deleted += 1

        return DiffStats(lines_added=lines_added, lines_deleted=lines_deleted)

    def fetch_diff_for_revision(self, revision: int) -> DiffStats:
        """Fetch and parse diff for a single revision.

        Returns cached result if available, otherwise fetches from SVN.

        Args:
            revision: SVN revision number.

        Returns:
            DiffStats with lines_added and lines_deleted.

        Raises:
            RuntimeError: If SVN command fails.
        """
        # Check cache first
        cached = self._cache.get(revision)
        if cached is not None:
            return DiffStats(
                lines_added=cached.lines_added,
                lines_deleted=cached.lines_deleted,
            )

        # Fetch from SVN
        diff_output = self._repo.fetch_diff_for_revision(revision)
        stats = self.parse_unified_diff(diff_output)

        # Cache the result
        self._cache.put(revision, stats.lines_added, stats.lines_deleted)

        return stats

    def fetch_diffs_batch(
        self,
        revisions: List[int],
        workers: int = 4,
        save_cache: bool = False,
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> Dict[int, DiffStats]:
        """Fetch diffs for multiple revisions with parallel processing.

        Only fetches uncached revisions, returns cached results for others.

        Args:
            revisions: List of SVN revision numbers.
            workers: Number of parallel workers (default: 4).
            save_cache: Whether to save cache after completion.
            on_progress: Optional callback (completed, total) for progress updates.

        Returns:
            Dictionary mapping revision to DiffStats.
        """
        if not revisions:
            return {}

        results: Dict[int, DiffStats] = {}
        total = len(revisions)

        # Get cached results first
        uncached = []
        for rev in revisions:
            cached = self._cache.get(rev)
            if cached is not None:
                results[rev] = DiffStats(
                    lines_added=cached.lines_added,
                    lines_deleted=cached.lines_deleted,
                )
            else:
                uncached.append(rev)

        # Fetch uncached revisions in parallel
        if uncached:
            completed = len(results)

            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {
                    executor.submit(self._fetch_single, rev): rev
                    for rev in uncached
                }

                for future in as_completed(futures):
                    rev = futures[future]
                    try:
                        stats = future.result()
                        results[rev] = stats
                    except Exception:
                        # Skip failed revisions, log could be added
                        results[rev] = DiffStats(lines_added=0, lines_deleted=0)

                    completed += 1
                    if on_progress:
                        on_progress(completed, total)

        # Report final progress if we only had cached results
        if not uncached and on_progress:
            on_progress(total, total)

        # Save cache if requested
        if save_cache:
            self._cache.save()

        return results

    def _fetch_single(self, revision: int) -> DiffStats:
        """Fetch and parse diff for a single revision (internal helper).

        Args:
            revision: SVN revision number.

        Returns:
            DiffStats with lines_added and lines_deleted.
        """
        diff_output = self._repo.fetch_diff_for_revision(revision)
        stats = self.parse_unified_diff(diff_output)

        # Cache the result
        self._cache.put(revision, stats.lines_added, stats.lines_deleted)

        return stats
