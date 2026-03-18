"""Statistics analyzer for Markdown notes."""

from typing import List, Dict, Tuple
from collections import Counter

from core_note import Note
from utils.config import TOP_TAGS_LIMIT, REPORT_HEADER_WIDTH, TABLE_COLUMN_WIDTH


class StatsAnalyzer:
    """Analyzes notes and generates statistics."""

    def __init__(self, notes: List[Note]):
        self.notes = notes
        self._tag_counter: Counter = Counter()
        self._wikilink_counter: Counter = Counter()
        self._total_lines: int = 0
        self._total_words: int = 0
        self._analyze()

    def _analyze(self) -> None:
        """Analyze all notes and collect statistics."""
        for note in self.notes:
            for tag in note.tags:
                self._tag_counter[tag] += 1
            for link in note.wikilinks:
                self._wikilink_counter[link] += 1
            self._total_lines += note.get_line_count()
            self._total_words += note.get_word_count()

    def get_total_notes(self) -> int:
        """Get total number of notes."""
        return len(self.notes)

    def get_total_lines(self) -> int:
        """Get total line count."""
        return self._total_lines

    def get_total_words(self) -> int:
        """Get total word count."""
        return self._total_words

    def get_all_tags(self, min_count: int = 1) -> Dict[str, int]:
        """Get all tags with counts, sorted by frequency."""
        return {tag: count for tag, count in self._tag_counter.most_common() if count >= min_count}

    def get_top_tags(self, limit: int = None) -> Dict[str, int]:
        """Get top N tags by frequency."""
        if limit is None:
            limit = TOP_TAGS_LIMIT
        return dict(self._tag_counter.most_common(limit))

    def get_total_wikilinks(self) -> int:
        """Get total number of wikilinks."""
        return sum(self._wikilink_counter.values())

    def get_unique_wikilinks(self) -> int:
        """Get number of unique wikilinks."""
        return len(self._wikilink_counter)

    def get_notes_with_tag(self, tag: str) -> List[Note]:
        """Get all notes containing a specific tag."""
        return [note for note in self.notes if note.has_tag(tag)]


def generate_stats_text(analyzer: StatsAnalyzer) -> str:
    """Generate statistics text report."""
    lines = []

    lines.append("=" * REPORT_HEADER_WIDTH)
    lines.append("MARKDOWN NOTES STATISTICS")
    lines.append("=" * REPORT_HEADER_WIDTH)
    lines.append("")

    lines.append("-" * REPORT_HEADER_WIDTH)
    lines.append("OVERVIEW")
    lines.append("-" * REPORT_HEADER_WIDTH)
    lines.append(f"Total Notes:        {analyzer.get_total_notes():>6}")
    lines.append(f"Total Lines:        {analyzer.get_total_lines():>6}")
    lines.append(f"Total Words:        {analyzer.get_total_words():>6}")
    lines.append("")

    lines.append("-" * REPORT_HEADER_WIDTH)
    lines.append(f"TOP {TOP_TAGS_LIMIT} TAGS")
    lines.append("-" * REPORT_HEADER_WIDTH)
    top_tags = analyzer.get_top_tags()
    if top_tags:
        lines.append(f"{'Tag':<{TABLE_COLUMN_WIDTH}} {'Count':>10}")
        lines.append("-" * (TABLE_COLUMN_WIDTH + 11))
        for tag, count in top_tags.items():
            lines.append(f"{tag:<{TABLE_COLUMN_WIDTH}} {count:>10}")
    else:
        lines.append("No tags found.")
    lines.append("")

    lines.append("-" * REPORT_HEADER_WIDTH)
    lines.append("WIKILINK STATISTICS")
    lines.append("-" * REPORT_HEADER_WIDTH)
    lines.append(f"Total Wikilinks:    {analyzer.get_total_wikilinks():>6}")
    lines.append(f"Unique Wikilinks:   {analyzer.get_unique_wikilinks():>6}")
    lines.append("")

    return '\n'.join(lines)


def generate_full_report(analyzer: StatsAnalyzer) -> str:
    """Generate complete statistics report."""
    return generate_stats_text(analyzer)
