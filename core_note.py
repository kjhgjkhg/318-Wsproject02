"""Core Note data structure for Markdown file representation."""

import re
import os
from typing import List, Dict, Optional

from utils.config import TAG_PATTERN, WIKILINK_PATTERN
from utils.validators import safe_read_file


class Note:
    """Represents a single Markdown note file."""

    def __init__(self, filepath: str):
        self.filepath: str = filepath
        self.filename: str = os.path.basename(filepath)
        self.content: Optional[str] = None
        self.lines: List[str] = []
        self.tags: List[str] = []
        self.wikilinks: List[str] = []
        self._load_and_parse()

    def _load_and_parse(self) -> None:
        """Load file content and extract metadata."""
        self.content = safe_read_file(self.filepath)
        if self.content is None:
            return
        self.lines = self.content.split('\n')
        self._extract_tags()
        self._extract_wikilinks()

    def _extract_tags(self) -> None:
        """Extract all #tags from content."""
        try:
            pattern = re.compile(TAG_PATTERN)
            self.tags = pattern.findall(self.content)
        except re.error as e:
            print(f"Warning: Tag extraction failed for {self.filename}: {e}")
            self.tags = []

    def _extract_wikilinks(self) -> None:
        """Extract all [[wikilinks]] from content."""
        try:
            pattern = re.compile(WIKILINK_PATTERN)
            self.wikilinks = pattern.findall(self.content)
        except re.error as e:
            print(f"Warning: Wikilink extraction failed for {self.filename}: {e}")
            self.wikilinks = []

    def has_tag(self, tag: str) -> bool:
        """Check if note contains a specific tag."""
        normalized_tag = tag.lower()
        for t in self.tags:
            if t.lower() == normalized_tag or t.lower().lstrip('#') == normalized_tag:
                return True
        return False

    def get_line_count(self) -> int:
        """Get total line count."""
        return len(self.lines)

    def get_word_count(self) -> int:
        """Get approximate word count."""
        if not self.content:
            return 0
        return len(self.content.split())

    def __str__(self) -> str:
        return f"Note('{self.filename}', tags={len(self.tags)})"

    def __repr__(self) -> str:
        return self.__str__()


def load_all_notes() -> List[Note]:
    """Load all markdown files as Note objects."""
    from utils.validators import get_markdown_files, validate_source_directory

    if not validate_source_directory():
        return []

    markdown_files = get_markdown_files()
    if not markdown_files:
        print("No markdown files found in source directory.")
        return []

    notes = []
    for filepath in markdown_files:
        note = Note(filepath)
        if note.content is not None:
            notes.append(note)
    return notes
