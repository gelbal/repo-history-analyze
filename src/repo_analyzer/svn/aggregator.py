# ABOUTME: SVN aggregation logic for commit data and props contributor tracking.
# ABOUTME: Groups commits by ISO week and computes rolling windows with contributor metrics.

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from repo_analyzer.svn.models import (
    ContributorStats,
    SVNCommitData,
    SVNRollingWindowAggregate,
    SVNWeeklyAggregate,
)


def get_iso_week_start(date: datetime) -> datetime:
    """Get the Monday (start) of the ISO week for a given date.

    Args:
        date: Datetime to get week start for.

    Returns:
        Datetime representing Monday at 00:00:00 UTC of the ISO week.
    """
    iso_year, iso_week, iso_weekday = date.isocalendar()

    # Calculate the Monday of this ISO week
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


class SVNWeeklyAggregator:
    """Aggregates SVN commit data into weekly summaries with props tracking."""

    def aggregate(self, commits: List[SVNCommitData]) -> List[SVNWeeklyAggregate]:
        """Group commits by ISO week and compute aggregates.

        Args:
            commits: List of SVNCommitData objects to aggregate.

        Returns:
            List of SVNWeeklyAggregate objects sorted by week_start.
        """
        if not commits:
            return []

        # Group commits by ISO week
        weeks_data = defaultdict(lambda: {
            "commits": [],
            "authors": set(),
            "props_contributors": set(),
            "lines_added": 0,
            "lines_deleted": 0,
        })

        for commit in commits:
            week_start = self._get_week_start(commit.commit_date)

            weeks_data[week_start]["commits"].append(commit)
            weeks_data[week_start]["authors"].add(commit.author)

            # Sum line changes (treat None as 0)
            if commit.lines_added is not None:
                weeks_data[week_start]["lines_added"] += commit.lines_added
            if commit.lines_deleted is not None:
                weeks_data[week_start]["lines_deleted"] += commit.lines_deleted

            for prop in commit.props:
                weeks_data[week_start]["props_contributors"].add(prop)

        # Create SVNWeeklyAggregate objects
        aggregates = []
        for week_start, data in weeks_data.items():
            aggregate = SVNWeeklyAggregate(
                week_start=week_start,
                total_commits=len(data["commits"]),
                unique_authors=len(data["authors"]),
                unique_props_contributors=len(data["props_contributors"]),
                total_lines_added=data["lines_added"],
                total_lines_deleted=data["lines_deleted"],
            )
            aggregates.append(aggregate)

        # Sort by week_start
        aggregates.sort(key=lambda x: x.week_start)

        return aggregates

    def _get_week_start(self, date: datetime) -> datetime:
        """Get the Monday (start) of the ISO week for a given date.

        Args:
            date: Datetime to get week start for.

        Returns:
            Datetime representing Monday at 00:00:00 UTC of the ISO week.
        """
        return get_iso_week_start(date)


class SVNRollingWindowAggregator:
    """Aggregates SVN commit data into 12-week rolling windows."""

    WINDOW_SIZE_WEEKS = 12

    def aggregate(
        self,
        commits: List[SVNCommitData],
        weekly_aggregates: List[SVNWeeklyAggregate],
    ) -> List[SVNRollingWindowAggregate]:
        """Compute 12-week rolling windows with props contributor tracking.

        Args:
            commits: List of SVNCommitData objects.
            weekly_aggregates: List of SVNWeeklyAggregate objects sorted by week_start.

        Returns:
            List of SVNRollingWindowAggregate objects, one per week.
        """
        if not weekly_aggregates:
            return []

        # Group commits by week_start for deduplication
        commits_by_week = self._group_commits_by_week(commits)

        rolling_windows = []

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

    def _group_commits_by_week(
        self, commits: List[SVNCommitData]
    ) -> Dict[datetime, List[SVNCommitData]]:
        """Group commits by their ISO week start date."""
        commits_by_week = defaultdict(list)

        for commit in commits:
            week_start = get_iso_week_start(commit.commit_date)
            commits_by_week[week_start].append(commit)

        return commits_by_week

    def _create_window_aggregate(
        self,
        window_weeks: List[SVNWeeklyAggregate],
        window_commits: List[SVNCommitData],
    ) -> SVNRollingWindowAggregate:
        """Create a SVNRollingWindowAggregate from weeks and commits."""
        if not window_weeks:
            raise ValueError("Cannot create window aggregate from empty weeks")

        # Window boundaries
        window_start = window_weeks[0].week_start

        # Calculate window_end as end of last week (Sunday 23:59:59)
        # Start from Monday at 23:59:59, then add 6 days to reach Sunday
        last_week_start = window_weeks[-1].week_start
        window_end = datetime(
            last_week_start.year,
            last_week_start.month,
            last_week_start.day,
            23, 59, 59,
            tzinfo=timezone.utc
        ) + timedelta(days=6)  # Monday + 6 days = Sunday

        # Sum commits from weekly aggregates
        total_commits = sum(week.total_commits for week in window_weeks)

        # Sum line changes from weekly aggregates
        total_lines_added = sum(week.total_lines_added for week in window_weeks)
        total_lines_deleted = sum(week.total_lines_deleted for week in window_weeks)

        # Deduplicate authors across window
        unique_authors_set = set(commit.author for commit in window_commits)
        unique_authors = len(unique_authors_set)

        # Deduplicate props contributors across window
        props_set = set()
        for commit in window_commits:
            for prop in commit.props:
                props_set.add(prop)
        unique_props_contributors = len(props_set)

        return SVNRollingWindowAggregate(
            window_start=window_start,
            window_end=window_end,
            total_commits=total_commits,
            unique_authors=unique_authors,
            unique_props_contributors=unique_props_contributors,
            total_lines_added=total_lines_added,
            total_lines_deleted=total_lines_deleted,
        )


class ContributorTracker:
    """Tracks contributor lifetime metrics from props attributions."""

    def track(
        self,
        commits: List[SVNCommitData],
        cutoff_date: datetime,
    ) -> Dict[str, ContributorStats]:
        """Track contributor statistics up to a cutoff date.

        Args:
            commits: List of SVNCommitData objects.
            cutoff_date: Only include contributions before this date.

        Returns:
            Dictionary mapping username to ContributorStats.
        """
        if not commits:
            return {}

        # Track first/latest contribution and count for each contributor
        contributor_data: Dict[str, dict] = {}

        for commit in commits:
            if commit.commit_date > cutoff_date:
                continue

            for prop in commit.props:
                if prop not in contributor_data:
                    contributor_data[prop] = {
                        "first_contribution": commit.commit_date,
                        "latest_contribution": commit.commit_date,
                        "count": 0,
                    }

                data = contributor_data[prop]

                if commit.commit_date < data["first_contribution"]:
                    data["first_contribution"] = commit.commit_date
                if commit.commit_date > data["latest_contribution"]:
                    data["latest_contribution"] = commit.commit_date

                data["count"] += 1

        # Convert to ContributorStats objects
        result = {}
        for username, data in contributor_data.items():
            result[username] = ContributorStats(
                username=username,
                first_contribution=data["first_contribution"],
                latest_contribution=data["latest_contribution"],
                total_props_count=data["count"],
            )

        return result
