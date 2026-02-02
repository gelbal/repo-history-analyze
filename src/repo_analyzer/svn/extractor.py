# ABOUTME: SVN commit extractor for parsing XML logs and extracting Props.
# ABOUTME: Converts SVN log XML into SVNCommitData objects with Props attribution.

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from repo_analyzer.svn.models import SVNCommitData


def extract_props(message: str) -> list[str]:
    """Extract usernames from Props attribution line in commit message.

    WordPress uses the Props keyword followed by comma-separated usernames
    to attribute changes to contributors. Format: "Props user1, user2, user3."

    Args:
        message: Full commit message text.

    Returns:
        List of usernames from Props line, or empty list if none found.
    """
    # Match "Props" followed by comma-separated usernames ending with period
    # Use greedy match to line end with MULTILINE to handle usernames containing periods
    pattern = r"Props\s+([^\n]+)\.$"
    match = re.search(pattern, message, re.IGNORECASE | re.MULTILINE)

    if not match:
        return []

    props_str = match.group(1)
    # Split by comma and clean up whitespace
    usernames = [name.strip() for name in props_str.split(",")]
    # Filter out empty strings
    return [name for name in usernames if name]


class SVNExtractor:
    """Extracts commit data from SVN log XML output.

    Parses the XML format produced by `svn log --xml` and converts
    each log entry into an SVNCommitData object, including Props
    extraction from commit messages.
    """

    def parse_commits_xml(self, xml_content: str) -> list[SVNCommitData]:
        """Parse SVN log XML into list of SVNCommitData objects.

        Args:
            xml_content: XML string from `svn log --xml`.

        Returns:
            List of SVNCommitData objects, one per commit.
        """
        root = ET.fromstring(xml_content)
        commits = []

        for entry in root.findall("logentry"):
            commit = self._parse_log_entry(entry)
            commits.append(commit)

        return commits

    def _parse_log_entry(self, entry: ET.Element) -> SVNCommitData:
        """Parse a single logentry XML element.

        Args:
            entry: XML Element for a logentry.

        Returns:
            SVNCommitData object.
        """
        revision = int(entry.get("revision"))

        author_elem = entry.find("author")
        author = author_elem.text if author_elem is not None and author_elem.text else ""

        date_elem = entry.find("date")
        date_str = date_elem.text if date_elem is not None else ""
        commit_date = self._parse_date(date_str)

        msg_elem = entry.find("msg")
        message = msg_elem.text if msg_elem is not None and msg_elem.text else ""

        props = extract_props(message)

        return SVNCommitData(
            revision=revision,
            author=author,
            commit_date=commit_date,
            message=message,
            props=props,
        )

    def _parse_date(self, date_str: str) -> datetime:
        """Parse ISO 8601 date string from SVN.

        SVN uses format: 2024-01-03T16:20:02.740525Z

        Args:
            date_str: ISO 8601 date string.

        Returns:
            Timezone-aware datetime in UTC.
        """
        if not date_str:
            return datetime.min.replace(tzinfo=timezone.utc)

        # Handle Z suffix for UTC
        date_str = date_str.replace("Z", "+00:00")
        return datetime.fromisoformat(date_str)
