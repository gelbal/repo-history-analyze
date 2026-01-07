# ABOUTME: Weekly aggregation logic for commit data and rolling window analysis.
# ABOUTME: Groups commits by ISO week and computes aggregate statistics and 12-week rolling windows.

from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import List

from .models import CommitData, WeeklyAggregate, RollingWindowAggregate


class WeeklyAggregator:
    """Aggregates commit data into weekly summaries."""

    def aggregate(self, commits: List[CommitData]) -> List[WeeklyAggregate]:
        """Group commits by ISO week and compute aggregates.

        Args:
            commits: List of CommitData objects to aggregate

        Returns:
            List of WeeklyAggregate objects sorted by week_start
        """
        if not commits:
            return []

        # Group commits by ISO week
        weeks_data = defaultdict(lambda: {
            'commits': [],
            'authors': set(),
            'lines_added': 0,
            'lines_deleted': 0,
            'versions': set()
        })

        for commit in commits:
            week_start = self._get_week_start(commit.commit_date)

            weeks_data[week_start]['commits'].append(commit)
            weeks_data[week_start]['authors'].add(commit.author_name)
            weeks_data[week_start]['lines_added'] += commit.lines_added
            weeks_data[week_start]['lines_deleted'] += commit.lines_deleted

            if commit.version is not None:
                weeks_data[week_start]['versions'].add(commit.version)

        # Create WeeklyAggregate objects
        aggregates = []
        for week_start, data in weeks_data.items():
            aggregate = WeeklyAggregate(
                week_start=week_start,
                total_commits=len(data['commits']),
                unique_authors=len(data['authors']),
                total_lines_added=data['lines_added'],
                total_lines_deleted=data['lines_deleted'],
                versions_released=sorted(list(data['versions']))
            )
            aggregates.append(aggregate)

        # Sort by week_start
        aggregates.sort(key=lambda x: x.week_start)

        return aggregates

    def _get_week_start(self, date: datetime) -> datetime:
        """Get the Monday (start) of the ISO week for a given date.

        Args:
            date: Datetime to get week start for

        Returns:
            Datetime representing Monday at 00:00:00 UTC of the ISO week
        """
        # Get ISO calendar info (year, week, weekday)
        # weekday: 1=Monday, 7=Sunday
        iso_year, iso_week, iso_weekday = date.isocalendar()

        # Calculate the Monday of this ISO week
        # Start from the given date and go back (weekday - 1) days
        days_from_monday = iso_weekday - 1
        monday = date - timedelta(days=days_from_monday)

        # Set to midnight UTC
        week_start = datetime(
            monday.year,
            monday.month,
            monday.day,
            0, 0, 0,
            tzinfo=timezone.utc
        )

        return week_start


class RollingWindowAggregator:
    """Aggregates commit data into 12-week rolling windows."""

    WINDOW_SIZE_WEEKS = 12

    def aggregate(
        self,
        commits: List[CommitData],
        weekly_aggregates: List[WeeklyAggregate]
    ) -> List[RollingWindowAggregate]:
        """Compute 12-week rolling windows.

        Uses weekly aggregates for numeric metrics and
        original commits for author/version deduplication.

        Args:
            commits: List of CommitData objects
            weekly_aggregates: List of WeeklyAggregate objects sorted by week_start

        Returns:
            List of RollingWindowAggregate objects, one per week
        """
        if not weekly_aggregates:
            return []

        # Group commits by week_start for deduplication
        commits_by_week = self._group_commits_by_week(commits)

        rolling_windows = []

        # For each week, create a rolling window
        for i, week_agg in enumerate(weekly_aggregates):
            # Get next 12 weeks (or fewer at end)
            window_weeks = weekly_aggregates[i:i + self.WINDOW_SIZE_WEEKS]

            # Collect all commits in window for deduplication
            window_commits = []
            for week in window_weeks:
                window_commits.extend(commits_by_week.get(week.week_start, []))

            # Create rolling window aggregate
            rolling_window = self._create_window_aggregate(window_weeks, window_commits)
            rolling_windows.append(rolling_window)

        return rolling_windows

    def _group_commits_by_week(self, commits: List[CommitData]) -> dict:
        """Group commits by their ISO week start date.

        Args:
            commits: List of CommitData objects

        Returns:
            Dictionary mapping week_start datetime to list of commits
        """
        weekly_aggregator = WeeklyAggregator()
        commits_by_week = defaultdict(list)

        for commit in commits:
            week_start = weekly_aggregator._get_week_start(commit.commit_date)
            commits_by_week[week_start].append(commit)

        return commits_by_week

    def _create_window_aggregate(
        self,
        window_weeks: List[WeeklyAggregate],
        window_commits: List[CommitData]
    ) -> RollingWindowAggregate:
        """Create a RollingWindowAggregate from weeks and commits.

        Args:
            window_weeks: List of WeeklyAggregate objects in the window
            window_commits: List of CommitData objects in the window

        Returns:
            RollingWindowAggregate with deduplicated authors and versions
        """
        if not window_weeks:
            raise ValueError("Cannot create window aggregate from empty weeks")

        # Window boundaries
        window_start = window_weeks[0].week_start

        # Calculate window_end as end of last week (Sunday 23:59:59)
        last_week_start = window_weeks[-1].week_start
        # Add 6 days to get to Sunday, then set time to end of day
        window_end = datetime(
            last_week_start.year,
            last_week_start.month,
            last_week_start.day,
            23, 59, 59,
            tzinfo=timezone.utc
        ) + timedelta(days=6)

        # Sum numeric metrics from weekly aggregates
        total_commits = sum(week.total_commits for week in window_weeks)
        total_lines_added = sum(week.total_lines_added for week in window_weeks)
        total_lines_deleted = sum(week.total_lines_deleted for week in window_weeks)

        # Deduplicate authors across window
        unique_authors_set = set(commit.author_name for commit in window_commits)
        unique_authors = len(unique_authors_set)

        # Deduplicate versions across window
        versions_set = set()
        for commit in window_commits:
            if commit.version is not None:
                versions_set.add(commit.version)
        versions_released = sorted(list(versions_set))

        return RollingWindowAggregate(
            window_start=window_start,
            window_end=window_end,
            total_commits=total_commits,
            unique_authors=unique_authors,
            total_lines_added=total_lines_added,
            total_lines_deleted=total_lines_deleted,
            versions_released=versions_released
        )
