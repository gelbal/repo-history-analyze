# ABOUTME: Unit tests for SVN diff fetcher module.
# ABOUTME: Tests unified diff parsing and batch fetching with caching.

from unittest.mock import MagicMock, patch

import pytest

from repo_analyzer.svn.diff_cache import SVNDiffCache
from repo_analyzer.svn.diff_fetcher import DiffStats, SVNDiffFetcher
from repo_analyzer.svn.repository import SVNRepository


class TestDiffStats:
    """Tests for DiffStats dataclass."""

    def test_create_stats(self):
        """Creates stats with lines added and deleted."""
        stats = DiffStats(lines_added=42, lines_deleted=7)

        assert stats.lines_added == 42
        assert stats.lines_deleted == 7

    def test_stats_total_changes(self):
        """Total changes is sum of added and deleted."""
        stats = DiffStats(lines_added=10, lines_deleted=5)

        assert stats.total_changes == 15

    def test_stats_zero_values(self):
        """Handles zero values."""
        stats = DiffStats(lines_added=0, lines_deleted=0)

        assert stats.lines_added == 0
        assert stats.lines_deleted == 0
        assert stats.total_changes == 0


class TestParseUnifiedDiff:
    """Tests for parse_unified_diff function."""

    def test_parse_additions_only(self):
        """Parses diff with only additions."""
        diff_output = """Index: trunk/src/file.php
===================================================================
--- trunk/src/file.php	(revision 100)
+++ trunk/src/file.php	(revision 101)
@@ -1,3 +1,6 @@
 <?php
+// New comment
+function new_function() {
+    return true;
+}
 ?>
"""
        fetcher = SVNDiffFetcher(MagicMock(), MagicMock())
        stats = fetcher.parse_unified_diff(diff_output)

        assert stats.lines_added == 4
        assert stats.lines_deleted == 0

    def test_parse_deletions_only(self):
        """Parses diff with only deletions."""
        diff_output = """Index: trunk/src/file.php
===================================================================
--- trunk/src/file.php	(revision 100)
+++ trunk/src/file.php	(revision 101)
@@ -1,6 +1,3 @@
 <?php
-// Old comment
-function old_function() {
-    return false;
-}
 ?>
"""
        fetcher = SVNDiffFetcher(MagicMock(), MagicMock())
        stats = fetcher.parse_unified_diff(diff_output)

        assert stats.lines_added == 0
        assert stats.lines_deleted == 4

    def test_parse_mixed_changes(self):
        """Parses diff with both additions and deletions."""
        diff_output = """Index: trunk/src/file.php
===================================================================
--- trunk/src/file.php	(revision 100)
+++ trunk/src/file.php	(revision 101)
@@ -1,5 +1,5 @@
 <?php
-// Old comment
+// New comment
 function test() {
-    return false;
+    return true;
 }
"""
        fetcher = SVNDiffFetcher(MagicMock(), MagicMock())
        stats = fetcher.parse_unified_diff(diff_output)

        assert stats.lines_added == 2
        assert stats.lines_deleted == 2

    def test_parse_empty_diff(self):
        """Handles empty diff output."""
        fetcher = SVNDiffFetcher(MagicMock(), MagicMock())
        stats = fetcher.parse_unified_diff("")

        assert stats.lines_added == 0
        assert stats.lines_deleted == 0

    def test_parse_diff_excludes_header_lines(self):
        """Does not count --- and +++ header lines."""
        diff_output = """Index: trunk/src/file.php
===================================================================
--- trunk/src/file.php	(revision 100)
+++ trunk/src/file.php	(revision 101)
@@ -1,3 +1,4 @@
 <?php
+// Added line
 ?>
"""
        fetcher = SVNDiffFetcher(MagicMock(), MagicMock())
        stats = fetcher.parse_unified_diff(diff_output)

        assert stats.lines_added == 1
        assert stats.lines_deleted == 0

    def test_parse_multiple_files(self):
        """Sums changes across multiple files in diff."""
        diff_output = """Index: trunk/src/file1.php
===================================================================
--- trunk/src/file1.php	(revision 100)
+++ trunk/src/file1.php	(revision 101)
@@ -1,2 +1,3 @@
 <?php
+// File 1 addition
 ?>

Index: trunk/src/file2.php
===================================================================
--- trunk/src/file2.php	(revision 100)
+++ trunk/src/file2.php	(revision 101)
@@ -1,3 +1,2 @@
 <?php
-// File 2 deletion
 ?>
"""
        fetcher = SVNDiffFetcher(MagicMock(), MagicMock())
        stats = fetcher.parse_unified_diff(diff_output)

        assert stats.lines_added == 1
        assert stats.lines_deleted == 1

    def test_parse_binary_file_skipped(self):
        """Binary file markers don't affect line counts."""
        diff_output = """Index: trunk/images/logo.png
===================================================================
Cannot display: file marked as a binary type.
svn:mime-type = image/png

Index: trunk/src/file.php
===================================================================
--- trunk/src/file.php	(revision 100)
+++ trunk/src/file.php	(revision 101)
@@ -1,2 +1,3 @@
 <?php
+// Added
 ?>
"""
        fetcher = SVNDiffFetcher(MagicMock(), MagicMock())
        stats = fetcher.parse_unified_diff(diff_output)

        assert stats.lines_added == 1
        assert stats.lines_deleted == 0

    def test_parse_property_changes_ignored(self):
        """Property changes (svn:*) don't affect line counts."""
        diff_output = """Index: trunk/src/file.php
===================================================================
--- trunk/src/file.php	(revision 100)
+++ trunk/src/file.php	(revision 101)

Property changes on: trunk/src/file.php
___________________________________________________________________
Added: svn:executable
## -0,0 +1 ##
+*
\\ No newline at end of property

@@ -1,2 +1,3 @@
 <?php
+// Added line
 ?>
"""
        fetcher = SVNDiffFetcher(MagicMock(), MagicMock())
        stats = fetcher.parse_unified_diff(diff_output)

        # Should only count the actual code change, not property
        assert stats.lines_added == 1
        assert stats.lines_deleted == 0


class TestSVNDiffFetcher:
    """Tests for SVNDiffFetcher class."""

    def test_fetch_diff_for_revision_success(self, tmp_path):
        """Fetches and parses diff for single revision."""
        mock_repo = MagicMock(spec=SVNRepository)
        mock_repo.fetch_diff_for_revision.return_value = """Index: trunk/src/file.php
===================================================================
--- trunk/src/file.php	(revision 99)
+++ trunk/src/file.php	(revision 100)
@@ -1,2 +1,4 @@
 <?php
+// Line 1
+// Line 2
 ?>
"""
        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")
        fetcher = SVNDiffFetcher(mock_repo, cache)

        stats = fetcher.fetch_diff_for_revision(100)

        assert stats.lines_added == 2
        assert stats.lines_deleted == 0
        mock_repo.fetch_diff_for_revision.assert_called_once_with(100)

    def test_fetch_diff_for_revision_caches_result(self, tmp_path):
        """Caches result after fetching."""
        mock_repo = MagicMock(spec=SVNRepository)
        mock_repo.fetch_diff_for_revision.return_value = """@@ -1 +1,2 @@
 line
+added
"""
        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")
        fetcher = SVNDiffFetcher(mock_repo, cache)

        fetcher.fetch_diff_for_revision(100)

        assert cache.has(100)
        assert cache.get(100).lines_added == 1

    def test_fetch_diff_uses_cache_if_available(self, tmp_path):
        """Returns cached result without fetching."""
        mock_repo = MagicMock(spec=SVNRepository)
        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")
        cache.put(100, lines_added=5, lines_deleted=3)

        fetcher = SVNDiffFetcher(mock_repo, cache)
        stats = fetcher.fetch_diff_for_revision(100)

        assert stats.lines_added == 5
        assert stats.lines_deleted == 3
        mock_repo.fetch_diff_for_revision.assert_not_called()

    def test_fetch_diff_for_revision_error(self, tmp_path):
        """Handles fetch error gracefully."""
        mock_repo = MagicMock(spec=SVNRepository)
        mock_repo.fetch_diff_for_revision.side_effect = RuntimeError("SVN error")

        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")
        fetcher = SVNDiffFetcher(mock_repo, cache)

        with pytest.raises(RuntimeError):
            fetcher.fetch_diff_for_revision(100)

    def test_fetch_diffs_batch_all_cached(self, tmp_path):
        """Batch fetch returns cached results without fetching."""
        mock_repo = MagicMock(spec=SVNRepository)
        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")
        cache.put(100, lines_added=10, lines_deleted=5)
        cache.put(200, lines_added=20, lines_deleted=10)

        fetcher = SVNDiffFetcher(mock_repo, cache)
        results = fetcher.fetch_diffs_batch([100, 200])

        assert results[100].lines_added == 10
        assert results[200].lines_added == 20
        mock_repo.fetch_diff_for_revision.assert_not_called()

    def test_fetch_diffs_batch_partial_cached(self, tmp_path):
        """Batch fetch only fetches uncached revisions."""
        mock_repo = MagicMock(spec=SVNRepository)
        mock_repo.fetch_diff_for_revision.return_value = """@@ -1 +1,2 @@
 line
+added
"""
        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")
        cache.put(100, lines_added=10, lines_deleted=5)

        fetcher = SVNDiffFetcher(mock_repo, cache)
        results = fetcher.fetch_diffs_batch([100, 200])

        assert results[100].lines_added == 10  # From cache
        assert results[200].lines_added == 1   # Freshly fetched
        mock_repo.fetch_diff_for_revision.assert_called_once_with(200)

    def test_fetch_diffs_batch_empty_list(self, tmp_path):
        """Handles empty revision list."""
        mock_repo = MagicMock(spec=SVNRepository)
        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")

        fetcher = SVNDiffFetcher(mock_repo, cache)
        results = fetcher.fetch_diffs_batch([])

        assert results == {}

    def test_fetch_diffs_batch_saves_cache(self, tmp_path):
        """Batch fetch saves cache after completion."""
        mock_repo = MagicMock(spec=SVNRepository)
        mock_repo.fetch_diff_for_revision.return_value = "@@ -1 +1 @@\n+line\n"

        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")
        fetcher = SVNDiffFetcher(mock_repo, cache)

        fetcher.fetch_diffs_batch([100, 200], save_cache=True)

        # Verify cache was saved (file exists)
        assert cache.cache_path.exists()

    def test_fetch_diffs_batch_with_progress_callback(self, tmp_path):
        """Calls progress callback during batch fetch."""
        mock_repo = MagicMock(spec=SVNRepository)
        mock_repo.fetch_diff_for_revision.return_value = "@@ -1 +1 @@\n+line\n"

        cache = SVNDiffCache(tmp_path, "https://example.com/repo/")
        fetcher = SVNDiffFetcher(mock_repo, cache)

        progress_calls = []
        def on_progress(completed, total):
            progress_calls.append((completed, total))

        fetcher.fetch_diffs_batch([100, 200, 300], on_progress=on_progress)

        assert len(progress_calls) >= 1
        # Last call should indicate completion
        assert progress_calls[-1][0] == progress_calls[-1][1]
