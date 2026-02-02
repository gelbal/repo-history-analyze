# ABOUTME: End-to-end tests for SVN CLI analyzer.
# ABOUTME: Tests the full CLI execution with real WordPress SVN data.

import csv
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.e2e
@pytest.mark.slow
class TestSVNCLIE2E:
    """End-to-end tests for SVN CLI."""

    def test_cli_produces_all_outputs(self, tmp_path):
        """CLI produces all expected output files."""
        result = subprocess.run(
            [
                sys.executable, "-m", "repo_analyzer.svn.cli",
                "--since", "2024-01-01",
                "--to", "2024-01-07",
                "--output-dir", str(tmp_path),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        # Check all expected files exist
        assert (tmp_path / "svn" / "2024" / "commits.csv").exists()
        assert (tmp_path / "svn" / "weekly_aggregates.csv").exists()
        assert (tmp_path / "svn" / "rolling_window_aggregates.csv").exists()
        assert (tmp_path / "svn" / "contributor_lifetimes.csv").exists()

    def test_cli_weekly_aggregates_content(self, tmp_path):
        """CLI produces valid weekly aggregates with Props data."""
        subprocess.run(
            [
                sys.executable, "-m", "repo_analyzer.svn.cli",
                "--since", "2024-01-01",
                "--to", "2024-01-07",
                "--output-dir", str(tmp_path),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        weekly_path = tmp_path / "svn" / "weekly_aggregates.csv"
        with open(weekly_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) > 0
        for row in rows:
            assert int(row["total_commits"]) >= 0
            assert int(row["unique_authors"]) >= 0
            assert int(row["unique_props_contributors"]) >= 0

    def test_cli_contributor_lifetimes_content(self, tmp_path):
        """CLI produces valid contributor lifetime data."""
        subprocess.run(
            [
                sys.executable, "-m", "repo_analyzer.svn.cli",
                "--since", "2024-01-01",
                "--to", "2024-01-07",
                "--output-dir", str(tmp_path),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        contributors_path = tmp_path / "svn" / "contributor_lifetimes.csv"
        with open(contributors_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Should have Props contributors
        assert len(rows) > 0

        for row in rows:
            assert row["username"] != ""
            assert int(row["total_props_count"]) > 0
            assert int(row["lifetime_days"]) >= 0
