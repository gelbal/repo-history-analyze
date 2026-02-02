# ABOUTME: Data models for SVN commit and contributor statistics.
# ABOUTME: Defines immutable dataclasses for WordPress SVN analysis pipeline.

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class SVNCommitData:
    """Represents metadata extracted from a single SVN commit.

    Attributes:
        revision: SVN revision number (integer identifier).
        author: Username of the committer.
        commit_date: Timestamp of the commit.
        message: Full commit message text.
        props: List of usernames from Props attribution line.
        lines_added: Number of lines added (None if not fetched).
        lines_deleted: Number of lines deleted (None if not fetched).
    """

    revision: int
    author: str
    commit_date: datetime
    message: str
    props: list[str]
    lines_added: Optional[int] = None
    lines_deleted: Optional[int] = None


@dataclass(frozen=True)
class ContributorStats:
    """Tracks lifetime metrics for a props contributor.

    Attributes:
        username: Contributor's WordPress.org username.
        first_contribution: Date of first props attribution.
        latest_contribution: Date of most recent props attribution.
        total_props_count: Total number of props received.
    """

    username: str
    first_contribution: datetime
    latest_contribution: datetime
    total_props_count: int

    @property
    def lifetime_days(self) -> int:
        """Calculate contributor lifetime in days."""
        delta = self.latest_contribution - self.first_contribution
        return delta.days


@dataclass(frozen=True)
class SVNWeeklyAggregate:
    """Aggregated commit statistics for one week including props contributors.

    Attributes:
        week_start: Monday of the ISO week at UTC midnight.
        total_commits: Number of commits in the week.
        unique_authors: Number of unique commit authors.
        unique_props_contributors: Number of unique Props usernames.
        total_lines_added: Total lines added in the week.
        total_lines_deleted: Total lines deleted in the week.
    """

    week_start: datetime
    total_commits: int
    unique_authors: int
    unique_props_contributors: int
    total_lines_added: int = 0
    total_lines_deleted: int = 0


@dataclass(frozen=True)
class SVNRollingWindowAggregate:
    """Aggregated statistics for a 12-week rolling window.

    Attributes:
        window_start: Start date of the window.
        window_end: End date of the window.
        total_commits: Total commits in the window.
        unique_authors: Unique commit authors across the window.
        unique_props_contributors: Unique Props usernames across the window.
        total_lines_added: Total lines added across the window.
        total_lines_deleted: Total lines deleted across the window.
    """

    window_start: datetime
    window_end: datetime
    total_commits: int
    unique_authors: int
    unique_props_contributors: int
    total_lines_added: int = 0
    total_lines_deleted: int = 0
