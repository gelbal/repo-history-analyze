# ABOUTME: Data models for commit and weekly aggregate statistics.
# ABOUTME: Defines immutable dataclasses used throughout the analysis pipeline.

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class CommitData:
    """Represents metadata extracted from a single git commit."""
    hash: str
    author_name: str
    commit_date: datetime
    lines_added: int
    lines_deleted: int
    version: Optional[str]


@dataclass(frozen=True)
class WeeklyAggregate:
    """Represents aggregated commit statistics for one week."""
    week_start: datetime
    total_commits: int
    unique_authors: int
    total_lines_added: int
    total_lines_deleted: int
    versions_released: list[str]


@dataclass(frozen=True)
class RollingWindowAggregate:
    """Represents aggregated statistics for a 12-week rolling window."""
    window_start: datetime
    window_end: datetime
    total_commits: int
    unique_authors: int
    total_lines_added: int
    total_lines_deleted: int
    versions_released: list[str]
