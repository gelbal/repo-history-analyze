# ABOUTME: SVN repository interface for fetching commit data.
# ABOUTME: Wraps svn command-line tool to retrieve commit logs in XML format.

import subprocess
from datetime import date
from typing import Optional


class SVNRepository:
    """Interface for fetching commit data from an SVN repository.

    Uses the svn command-line tool to retrieve commit logs in XML format.
    The XML format provides structured data for parsing revision, author,
    date, and commit message.
    """

    def __init__(self, url: str) -> None:
        """Initialize SVN repository with URL.

        Args:
            url: SVN repository URL (e.g., https://develop.svn.wordpress.org/).
        """
        self._url = url.rstrip("/") + "/"

    @property
    def url(self) -> str:
        """Repository URL."""
        return self._url

    def check_svn_available(self) -> bool:
        """Check if svn command is available on the system."""
        try:
            subprocess.run(
                ["svn", "--version"],
                capture_output=True,
                check=False,
            )
            return True
        except FileNotFoundError:
            return False

    def _build_log_command(
        self,
        start_date: date,
        end_date: date,
        limit: Optional[int] = None,
    ) -> list[str]:
        """Build svn log command with date range.

        Args:
            start_date: Start date for log range.
            end_date: End date for log range.
            limit: Maximum number of revisions to fetch.

        Returns:
            Command as list of strings for subprocess.
        """
        cmd = [
            "svn", "log", self._url,
            "-r", f"{{{start_date}}}:{{{end_date}}}",
            "--xml"
        ]

        if limit is not None:
            cmd.extend(["-l", str(limit)])

        return cmd

    def fetch_commits_xml(
        self,
        start_date: date,
        end_date: date,
        limit: Optional[int] = None,
    ) -> str:
        """Fetch commit logs as XML for a date range.

        Args:
            start_date: Start date for log range.
            end_date: End date for log range.
            limit: Maximum number of revisions to fetch.

        Returns:
            XML string containing commit log entries.

        Raises:
            RuntimeError: If svn command fails.
        """
        cmd = self._build_log_command(start_date, end_date, limit)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(f"SVN command failed: {result.stderr}")

        return result.stdout

    def _build_diff_command(self, revision: int) -> list[str]:
        """Build svn diff command for a single revision.

        Args:
            revision: SVN revision number.

        Returns:
            Command as list of strings for subprocess.
        """
        return [
            "svn", "diff",
            "-c", str(revision),
            self._url,
        ]

    def fetch_diff_for_revision(self, revision: int, timeout: int = 60) -> str:
        """Fetch unified diff for a single revision.

        Args:
            revision: SVN revision number.
            timeout: Timeout in seconds for the SVN command.

        Returns:
            Unified diff output as string.

        Raises:
            RuntimeError: If svn command fails or times out.
        """
        cmd = self._build_diff_command(revision)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"SVN diff timed out for revision {revision}")

        if result.returncode != 0:
            raise RuntimeError(
                f"SVN diff failed for revision {revision}: {result.stderr}"
            )

        return result.stdout


class WordPressSVNRepository(SVNRepository):
    """SVN repository preconfigured for WordPress development.

    Uses the develop.svn.wordpress.org repository by default, which is
    the canonical source for WordPress core development.
    """

    DEFAULT_URL = "https://develop.svn.wordpress.org/"

    def __init__(self, url: Optional[str] = None) -> None:
        """Initialize WordPress SVN repository.

        Args:
            url: Optional URL override. Defaults to develop.svn.wordpress.org.
        """
        super().__init__(url or self.DEFAULT_URL)
