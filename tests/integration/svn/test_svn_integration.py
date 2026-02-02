# ABOUTME: Integration tests for SVN module with real WordPress SVN repository.
# ABOUTME: Tests the full pipeline from fetching to CSV output.

import csv
from datetime import date

import pytest

from repo_analyzer.svn.aggregator import (
    ContributorTracker,
    SVNRollingWindowAggregator,
    SVNWeeklyAggregator,
)
from repo_analyzer.svn.csv_writer import SVNCSVWriter
from repo_analyzer.svn.extractor import SVNExtractor
from repo_analyzer.svn.repository import WordPressSVNRepository


@pytest.mark.integration
@pytest.mark.slow
class TestSVNIntegration:
    """Integration tests with real WordPress SVN repository."""

    def test_fetch_and_parse_commits(self):
        """Fetches real commits from WordPress SVN and parses them."""
        repo = WordPressSVNRepository()

        # Skip if SVN not available
        if not repo.check_svn_available():
            pytest.skip("SVN not installed")

        # Fetch a small date range (1 week)
        xml_content = repo.fetch_commits_xml(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7),
        )

        extractor = SVNExtractor()
        commits = extractor.parse_commits_xml(xml_content)

        # Should have some commits
        assert len(commits) > 0

        # Each commit should have required fields
        for commit in commits:
            assert commit.revision > 0
            assert commit.author != ""
            assert commit.commit_date is not None

    def test_extract_props_from_real_commits(self):
        """Extracts Props from real WordPress commits."""
        repo = WordPressSVNRepository()

        if not repo.check_svn_available():
            pytest.skip("SVN not installed")

        xml_content = repo.fetch_commits_xml(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7),
        )

        extractor = SVNExtractor()
        commits = extractor.parse_commits_xml(xml_content)

        # Collect all Props
        all_props = set()
        for commit in commits:
            all_props.update(commit.props)

        # Should find some Props contributors
        assert len(all_props) > 0

    def test_full_pipeline(self, tmp_path):
        """Tests full pipeline: fetch -> parse -> aggregate -> write CSV."""
        repo = WordPressSVNRepository()

        if not repo.check_svn_available():
            pytest.skip("SVN not installed")

        # Fetch commits
        xml_content = repo.fetch_commits_xml(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 7),
        )

        # Parse
        extractor = SVNExtractor()
        commits = extractor.parse_commits_xml(xml_content)

        # Aggregate
        weekly_agg = SVNWeeklyAggregator()
        weekly_results = weekly_agg.aggregate(commits)

        rolling_agg = SVNRollingWindowAggregator()
        rolling_results = rolling_agg.aggregate(commits, weekly_results)

        # Write CSVs
        SVNCSVWriter.write_commits_by_year(commits, tmp_path, "svn")
        SVNCSVWriter.write_weekly_aggregates(
            weekly_results, tmp_path / "svn" / "weekly.csv"
        )
        SVNCSVWriter.write_rolling_aggregates(
            rolling_results, tmp_path / "svn" / "rolling.csv"
        )

        # Verify files exist
        assert (tmp_path / "svn" / "2024" / "commits.csv").exists()
        assert (tmp_path / "svn" / "weekly.csv").exists()
        assert (tmp_path / "svn" / "rolling.csv").exists()

        # Verify weekly CSV content
        with open(tmp_path / "svn" / "weekly.csv") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) > 0
        assert "unique_props_contributors" in rows[0]
