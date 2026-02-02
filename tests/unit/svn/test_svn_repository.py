# ABOUTME: Unit tests for SVN repository module.
# ABOUTME: Tests SVNRepository class for fetching commit data.

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from repo_analyzer.svn.repository import SVNRepository, WordPressSVNRepository


class TestSVNRepository:
    """Tests for SVNRepository class."""

    def test_repository_url(self):
        """SVNRepository stores the repository URL."""
        repo = SVNRepository("https://example.svn.org/")
        assert repo.url == "https://example.svn.org/"

    def test_repository_url_trailing_slash(self):
        """SVNRepository normalizes URL without trailing slash."""
        repo = SVNRepository("https://example.svn.org")
        assert repo.url == "https://example.svn.org/"

    def test_build_log_command(self):
        """SVNRepository builds correct svn log command."""
        repo = SVNRepository("https://example.svn.org/")
        cmd = repo._build_log_command(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )

        assert cmd == [
            "svn", "log", "https://example.svn.org/",
            "-r", "{2024-01-01}:{2024-01-31}",
            "--xml"
        ]

    def test_build_log_command_with_limit(self):
        """SVNRepository builds command with revision limit."""
        repo = SVNRepository("https://example.svn.org/")
        cmd = repo._build_log_command(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            limit=100,
        )

        assert "-l" in cmd
        assert "100" in cmd

    @patch("subprocess.run")
    def test_fetch_commits_xml(self, mock_run):
        """SVNRepository fetches and returns XML output."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='<?xml version="1.0"?><log></log>',
            stderr=""
        )

        repo = SVNRepository("https://example.svn.org/")
        xml = repo.fetch_commits_xml(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )

        assert xml == '<?xml version="1.0"?><log></log>'
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_fetch_commits_xml_error(self, mock_run):
        """SVNRepository raises error on SVN failure."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="svn: E000001: Unable to connect"
        )

        repo = SVNRepository("https://example.svn.org/")

        with pytest.raises(RuntimeError, match="SVN command failed"):
            repo.fetch_commits_xml(
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 31),
            )

    @patch("subprocess.run")
    def test_check_svn_available(self, mock_run):
        """SVNRepository verifies svn command is available."""
        mock_run.return_value = MagicMock(returncode=0)

        repo = SVNRepository("https://example.svn.org/")
        assert repo.check_svn_available() is True

    @patch("subprocess.run")
    def test_check_svn_not_available(self, mock_run):
        """SVNRepository detects when svn is not installed."""
        mock_run.side_effect = FileNotFoundError()

        repo = SVNRepository("https://example.svn.org/")
        assert repo.check_svn_available() is False


class TestWordPressSVNRepository:
    """Tests for WordPressSVNRepository class."""

    def test_default_url(self):
        """WordPressSVNRepository uses develop.svn.wordpress.org by default."""
        repo = WordPressSVNRepository()
        assert repo.url == "https://develop.svn.wordpress.org/"

    def test_custom_url(self):
        """WordPressSVNRepository allows custom URL override."""
        repo = WordPressSVNRepository("https://core.svn.wordpress.org/")
        assert repo.url == "https://core.svn.wordpress.org/"
