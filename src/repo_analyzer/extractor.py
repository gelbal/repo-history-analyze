# ABOUTME: Extracts structured metadata from PyDriller commit objects.
# ABOUTME: Converts PyDriller commits to CommitData model with version enrichment.

from pydriller.domain.commit import Commit as PyDrillerCommit

from .models import CommitData
from .version_mapper import VersionMapper


class CommitExtractor:
    """Extracts CommitData from PyDriller commit objects."""

    def __init__(self, version_mapper: VersionMapper):
        """Initialize CommitExtractor with a VersionMapper.

        Args:
            version_mapper: VersionMapper instance for looking up commit versions
        """
        self.version_mapper = version_mapper

    def extract(self, commit: PyDrillerCommit) -> CommitData:
        """Convert PyDriller commit to CommitData model.

        Args:
            commit: PyDriller Commit object

        Returns:
            CommitData object with metadata extracted from commit
        """
        return CommitData(
            hash=commit.hash,
            author_name=commit.author.name,
            commit_date=commit.author_date,
            lines_added=commit.insertions,
            lines_deleted=commit.deletions,
            version=self.version_mapper.get_version_for_commit(commit.hash)
        )
