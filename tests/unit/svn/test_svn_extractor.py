# ABOUTME: Unit tests for SVN extractor module.
# ABOUTME: Tests XML parsing and Props extraction from commit messages.

from datetime import datetime, timezone

import pytest

from repo_analyzer.svn.extractor import SVNExtractor, extract_props


class TestExtractProps:
    """Tests for extract_props function."""

    def test_extract_single_prop(self):
        """Extracts single username from Props line."""
        message = "Fix bug.\n\nProps mukesh27.\nFixes #12345."
        assert extract_props(message) == ["mukesh27"]

    def test_extract_multiple_props(self):
        """Extracts multiple usernames from Props line."""
        message = "Add feature.\n\nProps audrasjb, jorbin, muryam.\nFixes #54321."
        assert extract_props(message) == ["audrasjb", "jorbin", "muryam"]

    def test_extract_props_with_spaces(self):
        """Handles Props with varying whitespace."""
        message = "Update docs.\n\nProps  user1,  user2 ,user3 .\nSee #111."
        props = extract_props(message)
        assert "user1" in props
        assert "user2" in props
        assert "user3" in props

    def test_extract_props_case_insensitive(self):
        """Handles Props keyword in different cases."""
        message1 = "Fix.\n\nProps user1."
        message2 = "Fix.\n\nprops user1."
        message3 = "Fix.\n\nPROPS user1."

        assert extract_props(message1) == ["user1"]
        assert extract_props(message2) == ["user1"]
        assert extract_props(message3) == ["user1"]

    def test_no_props_returns_empty_list(self):
        """Returns empty list when no Props line exists."""
        message = "Happy New Year!\n\nUpdate copyright year."
        assert extract_props(message) == []

    def test_props_at_end_of_message(self):
        """Handles Props at the very end of message."""
        message = "Fix typo.\n\nProps shailu25."
        assert extract_props(message) == ["shailu25"]

    def test_props_with_underscores(self):
        """Handles usernames with underscores."""
        message = "Update.\n\nProps hello_from_tonya, test_user123."
        props = extract_props(message)
        assert "hello_from_tonya" in props
        assert "test_user123" in props

    def test_props_with_numbers(self):
        """Handles usernames with numbers."""
        message = "Fix.\n\nProps user123, 123user, u1s2e3r."
        props = extract_props(message)
        assert len(props) == 3

    def test_props_with_periods_in_username(self):
        """Handles usernames containing periods."""
        message = "Fix.\n\nProps john.doe, jane.smith."
        props = extract_props(message)
        assert "john.doe" in props
        assert "jane.smith" in props
        assert len(props) == 2


class TestSVNExtractor:
    """Tests for SVNExtractor class."""

    SAMPLE_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<log>
<logentry revision="57238">
<author>SergeyBiryukov</author>
<date>2024-01-03T16:20:02.740525Z</date>
<msg>Customize: Pass the previous status to post trash hooks.

Follow-up to [56043].

Props joelcj91, mukesh27.
Fixes #60183.</msg>
</logentry>
<logentry revision="57235">
<author>pento</author>
<date>2024-01-01T00:00:37.249691Z</date>
<msg>Happy New Year!

Update copyright year to 2024.</msg>
</logentry>
</log>'''

    def test_parse_commits(self):
        """SVNExtractor parses XML into SVNCommitData objects."""
        extractor = SVNExtractor()
        commits = extractor.parse_commits_xml(self.SAMPLE_XML)

        assert len(commits) == 2

    def test_parse_commit_revision(self):
        """SVNExtractor extracts revision number."""
        extractor = SVNExtractor()
        commits = extractor.parse_commits_xml(self.SAMPLE_XML)

        assert commits[0].revision == 57238
        assert commits[1].revision == 57235

    def test_parse_commit_author(self):
        """SVNExtractor extracts author."""
        extractor = SVNExtractor()
        commits = extractor.parse_commits_xml(self.SAMPLE_XML)

        assert commits[0].author == "SergeyBiryukov"
        assert commits[1].author == "pento"

    def test_parse_commit_date(self):
        """SVNExtractor extracts and parses date."""
        extractor = SVNExtractor()
        commits = extractor.parse_commits_xml(self.SAMPLE_XML)

        assert commits[0].commit_date == datetime(
            2024, 1, 3, 16, 20, 2, 740525, tzinfo=timezone.utc
        )

    def test_parse_commit_message(self):
        """SVNExtractor extracts full message."""
        extractor = SVNExtractor()
        commits = extractor.parse_commits_xml(self.SAMPLE_XML)

        assert "Customize: Pass the previous status" in commits[0].message

    def test_parse_commit_props(self):
        """SVNExtractor extracts Props from message."""
        extractor = SVNExtractor()
        commits = extractor.parse_commits_xml(self.SAMPLE_XML)

        assert commits[0].props == ["joelcj91", "mukesh27"]
        assert commits[1].props == []

    def test_parse_empty_log(self):
        """SVNExtractor handles empty log."""
        extractor = SVNExtractor()
        xml = '<?xml version="1.0"?><log></log>'
        commits = extractor.parse_commits_xml(xml)

        assert commits == []

    def test_parse_commit_with_empty_author(self):
        """SVNExtractor handles missing author gracefully."""
        extractor = SVNExtractor()
        xml = '''<?xml version="1.0"?>
<log>
<logentry revision="100">
<date>2024-01-01T00:00:00.000000Z</date>
<msg>Test</msg>
</logentry>
</log>'''
        commits = extractor.parse_commits_xml(xml)

        assert commits[0].author == ""
