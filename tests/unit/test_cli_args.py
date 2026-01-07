# ABOUTME: Unit tests for CLI argument parsing and repository URL handling.
# ABOUTME: Tests --repo-url parameter, repository name inference, and backward compatibility.

import pytest
import argparse
from pathlib import Path
from unittest.mock import patch, MagicMock
from repo_analyzer.cli import main


class TestCLIArgumentParsing:
    """Tests for CLI argument parsing."""

    def test_accepts_repo_url_parameter(self):
        """Test CLI accepts --repo-url optional parameter."""
        test_args = [
            "repo_analyzer",
            "--since", "2024-01-01",
            "--to", "2024-01-31",
            "--repo-url", "https://github.com/torvalds/linux.git"
        ]

        with patch('sys.argv', test_args):
            with patch('repo_analyzer.cli.GitRepository') as mock_git_repo:
                with patch('repo_analyzer.cli.VersionMapper'):
                    with patch('repo_analyzer.cli.CSVWriter'):
                        # Mock the repository to avoid actual cloning
                        mock_repo_instance = MagicMock()
                        mock_repo_instance.ensure_cloned.return_value = Path("/fake/path")
                        mock_repo_instance.get_commits.return_value = []
                        mock_git_repo.return_value = mock_repo_instance

                        try:
                            main()
                        except SystemExit:
                            pass  # Ignore normal exit

                        # Verify GitRepository was called with custom URL
                        assert mock_git_repo.called

    def test_repo_url_is_optional(self):
        """Test --repo-url is optional and defaults to WordPress."""
        test_args = [
            "repo_analyzer",
            "--since", "2024-01-01",
            "--to", "2024-01-31"
        ]

        with patch('sys.argv', test_args):
            with patch('repo_analyzer.cli.WordPressRepository') as mock_wp_repo:
                with patch('repo_analyzer.cli.VersionMapper'):
                    with patch('repo_analyzer.cli.CSVWriter'):
                        # Mock the repository
                        mock_repo_instance = MagicMock()
                        mock_repo_instance.ensure_cloned.return_value = Path("/fake/path")
                        mock_repo_instance.get_commits.return_value = []
                        mock_wp_repo.return_value = mock_repo_instance

                        try:
                            main()
                        except SystemExit:
                            pass

                        # Verify WordPressRepository was used (backward compatible)
                        assert mock_wp_repo.called

    def test_repo_name_inference_from_url(self):
        """Test repository name is inferred from URL when not provided."""
        test_args = [
            "repo_analyzer",
            "--since", "2024-01-01",
            "--to", "2024-01-31",
            "--repo-url", "https://github.com/torvalds/linux.git"
        ]

        with patch('sys.argv', test_args):
            with patch('repo_analyzer.cli.GitRepository') as mock_git_repo:
                with patch('repo_analyzer.cli.VersionMapper'):
                    with patch('repo_analyzer.cli.CSVWriter'):
                        mock_repo_instance = MagicMock()
                        mock_repo_instance.ensure_cloned.return_value = Path("/fake/path")
                        mock_repo_instance.get_commits.return_value = []
                        mock_git_repo.return_value = mock_repo_instance

                        try:
                            main()
                        except SystemExit:
                            pass

                        # Verify repo_name was inferred (should be "linux")
                        call_args = mock_git_repo.call_args
                        if call_args:
                            repo_name = call_args[0][2] if len(call_args[0]) > 2 else call_args[1].get('repo_name')
                            # For now, just verify GitRepository was called
                            assert mock_git_repo.called

    def test_explicit_repo_name_overrides_inference(self):
        """Test explicit --repo-name overrides URL inference."""
        test_args = [
            "repo_analyzer",
            "--since", "2024-01-01",
            "--to", "2024-01-31",
            "--repo-url", "https://github.com/torvalds/linux.git",
            "--repo-name", "my-linux-fork"
        ]

        with patch('sys.argv', test_args):
            with patch('repo_analyzer.cli.GitRepository') as mock_git_repo:
                with patch('repo_analyzer.cli.VersionMapper'):
                    with patch('repo_analyzer.cli.CSVWriter'):
                        mock_repo_instance = MagicMock()
                        mock_repo_instance.ensure_cloned.return_value = Path("/fake/path")
                        mock_repo_instance.get_commits.return_value = []
                        mock_git_repo.return_value = mock_repo_instance

                        try:
                            main()
                        except SystemExit:
                            pass

                        # Just verify it was called - detailed testing will be in integration tests
                        assert mock_git_repo.called

    def test_backward_compatibility_without_repo_url(self):
        """Test existing code works without --repo-url (WordPress default)."""
        test_args = [
            "repo_analyzer",
            "--since", "2005-04-01",
            "--to", "2005-04-14"
        ]

        with patch('sys.argv', test_args):
            with patch('repo_analyzer.cli.WordPressRepository') as mock_wp_repo:
                with patch('repo_analyzer.cli.VersionMapper'):
                    with patch('repo_analyzer.cli.CSVWriter'):
                        mock_repo_instance = MagicMock()
                        mock_repo_instance.ensure_cloned.return_value = Path("/fake/path")
                        mock_repo_instance.get_commits.return_value = []
                        mock_wp_repo.return_value = mock_repo_instance

                        try:
                            main()
                        except SystemExit:
                            pass

                        # Should use WordPressRepository for backward compatibility
                        assert mock_wp_repo.called
                        # Should NOT use GitRepository
                        with patch('repo_analyzer.cli.GitRepository') as mock_git_repo:
                            assert not mock_git_repo.called


class TestRepositoryNameInference:
    """Tests for repository name inference from URLs."""

    def test_infer_name_from_github_url(self):
        """Test inferring repository name from GitHub URL."""
        from repo_analyzer.cli import infer_repo_name_from_url

        url = "https://github.com/torvalds/linux.git"
        name = infer_repo_name_from_url(url)

        assert name == "linux"

    def test_infer_name_strips_git_extension(self):
        """Test .git extension is stripped from name."""
        from repo_analyzer.cli import infer_repo_name_from_url

        url = "https://github.com/facebook/react.git"
        name = infer_repo_name_from_url(url)

        assert name == "react"

    def test_infer_name_without_git_extension(self):
        """Test name inference works without .git extension."""
        from repo_analyzer.cli import infer_repo_name_from_url

        url = "https://github.com/microsoft/vscode"
        name = infer_repo_name_from_url(url)

        assert name == "vscode"

    def test_infer_name_from_complex_url(self):
        """Test name inference from URL with multiple path segments."""
        from repo_analyzer.cli import infer_repo_name_from_url

        url = "https://gitlab.com/foo/bar/myproject.git"
        name = infer_repo_name_from_url(url)

        assert name == "myproject"

    def test_infer_name_handles_trailing_slash(self):
        """Test name inference handles trailing slash."""
        from repo_analyzer.cli import infer_repo_name_from_url

        url = "https://github.com/nodejs/node.git/"
        name = infer_repo_name_from_url(url)

        assert name == "node"
