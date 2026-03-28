"""Search engine for full-text search in Markdown notes."""

from typing import List, Dict, Tuple, Optional

from core_note import Note
from utils.config import PREVIEW_CONTEXT_LINES, PREVIEW_MAX_CHARS


class SearchResult:
    """Represents a single search result."""

    def __init__(self, note: Note, matches: List[Tuple[int, str]], preview: str):
        self.note = note
        self.matches = matches
        self.preview = preview
        self.match_count = len(matches)


def search_notes(notes: List[Note], keywords: List[str], case_sensitive: bool = False) -> List[SearchResult]:
    """
    Search notes for all keywords (AND logic).
    Returns notes that contain ALL keywords.
    """
    if not keywords:
        return []

    results = []
    normalized_keywords = [k if case_sensitive else k.lower() for k in keywords]

    for note in notes:
        if not note.content:
            continue

        search_content = note.content if case_sensitive else note.content.lower()
        all_keywords_found = True

        for keyword in normalized_keywords:
            if keyword not in search_content:
                all_keywords_found = False
                break

        if all_keywords_found:
            matches = _find_matches(note, normalized_keywords, case_sensitive)
            preview = _generate_preview(note, matches)
            results.append(SearchResult(note, matches, preview))

    return sorted(results, key=lambda x: x.match_count, reverse=True)


def _find_matches(note: Note, keywords: List[str], case_sensitive: bool) -> List[Tuple[int, str]]:
    """Find all matching lines with line numbers."""
    matches = []
    for line_num, line in enumerate(note.lines, start=1):
        search_line = line if case_sensitive else line.lower()
        for keyword in keywords:
            if keyword in search_line:
                matches.append((line_num, line.strip()))
                break
    return matches


def _generate_preview(note: Note, matches: List[Tuple[int, str]]) -> str:
    """Generate a preview of matching content."""
    if not matches:
        return ""

    preview_parts = []
    seen_lines = set()

    for line_num, _ in matches:
        if line_num in seen_lines:
            continue
        seen_lines.add(line_num)

        start_idx = max(0, line_num - 1 - PREVIEW_CONTEXT_LINES)
        end_idx = min(len(note.lines), line_num + PREVIEW_CONTEXT_LINES)

        context = note.lines[start_idx:end_idx]
        preview_chunk = '\n'.join(context)
        if len(preview_chunk) > PREVIEW_MAX_CHARS:
            preview_chunk = preview_chunk[:PREVIEW_MAX_CHARS] + "..."

        preview_parts.append(f"[Line {line_num}]: {preview_chunk}")

    return '\n'.join(preview_parts)


def highlight_matches(text: str, keywords: List[str]) -> str:
    """Highlight matching keywords (for display only)."""
    result = text
    for keyword in keywords:
        try:
            import re
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            result = pattern.sub(lambda m: f"*{m.group(0)}*", result)
        except Exception:
            pass
    return result


def format_search_result(result: SearchResult, keywords: List[str]) -> str:
    """Format a search result for display."""
    lines = [
        f"{'='*60}",
        f"File: {result.note.filename}",
        f"Matches: {result.match_count}",
        f"Tags: {', '.join(result.note.tags[:5])}" if result.note.tags else "Tags: none",
        f"{'-'*60}",
        highlight_matches(result.preview, keywords),
        ""
    ]
    return '\n'.join(lines)
