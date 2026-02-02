# ABOUTME: Unit tests for SVN CLI module.
# ABOUTME: Tests argument parsing and date validation.

from datetime import date

import pytest

from repo_analyzer.svn.cli import parse_args, parse_date


class TestParseDateFunction:
    """Tests for parse_date function."""

    def test_parse_valid_date(self):
        """Parses valid YYYY-MM-DD format."""
        result = parse_date("2024-01-15")
        assert result == date(2024, 1, 15)

    def test_parse_invalid_format(self):
        """Raises ValueError for invalid format."""
        with pytest.raises(ValueError, match="Invalid date format"):
            parse_date("01-15-2024")

    def test_parse_invalid_date(self):
        """Raises ValueError for invalid date."""
        with pytest.raises(ValueError, match="Invalid date format"):
            parse_date("2024-02-30")


class TestParseArgs:
    """Tests for parse_args function."""

    def test_required_args(self):
        """Requires --since and --to arguments."""
        args = parse_args(["--since", "2024-01-01", "--to", "2024-01-31"])
        assert args.since == "2024-01-01"
        assert args.to == "2024-01-31"

    def test_custom_output_dir(self):
        """Accepts custom output directory."""
        args = parse_args([
            "--since", "2024-01-01",
            "--to", "2024-01-31",
            "--output-dir", "/custom/path"
        ])
        assert str(args.output_dir) == "/custom/path"

    def test_custom_svn_url(self):
        """Accepts custom SVN URL."""
        args = parse_args([
            "--since", "2024-01-01",
            "--to", "2024-01-31",
            "--svn-url", "https://custom.svn.org/"
        ])
        assert args.svn_url == "https://custom.svn.org/"
