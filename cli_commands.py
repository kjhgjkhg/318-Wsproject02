"""CLI command implementations for the notes tool."""

import os
from typing import List

from core_note import Note, load_all_notes
from search_engine import search_notes, format_search_result
from stats_analyzer import StatsAnalyzer, generate_stats_text, generate_full_report
from utils.validators import validate_keywords, validate_tag, validate_output_directory
from utils.config import OUTPUT_DIR, SEARCH_REPORT_FILENAME, STATS_REPORT_FILENAME


def cmd_search(args) -> None:
    """Execute 'notes search' command."""
    keywords = args.keywords
    if not validate_keywords(keywords):
        return

    notes = load_all_notes()
    if not notes:
        return

    results = search_notes(notes, keywords)

    if not results:
        print(f"No matches found for: {' '.join(keywords)}")
        return

    output_lines = []
    for result in results:
        formatted = format_search_result(result, keywords)
        output_lines.append(formatted)
        print(formatted)

    print(f"\nFound {len(results)} notes matching your query.")

    if validate_output_directory():
        try:
            filepath = os.path.join(OUTPUT_DIR, SEARCH_REPORT_FILENAME)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output_lines))
            print(f"\nSearch results saved to: {filepath}")
        except Exception as e:
            print(f"\nWarning: Could not save results: {e}")


def cmd_tags(args) -> None:
    """Execute 'notes tags' command."""
    notes = load_all_notes()
    if not notes:
        return

    analyzer = StatsAnalyzer(notes)
    all_tags = analyzer.get_all_tags()

    if not all_tags:
        print("No tags found.")
        return

    print("=" * 60)
    print("ALL TAGS (by frequency)")
    print("=" * 60)
    for tag, count in all_tags.items():
        print(f"{tag:<40} {count:>5}")
    print(f"\nTotal unique tags: {len(all_tags)}")


def cmd_stats(args) -> None:
    """Execute 'notes stats' command."""
    notes = load_all_notes()
    if not notes:
        return

    analyzer = StatsAnalyzer(notes)
    report = generate_stats_text(analyzer)
    print(report)


def cmd_list(args) -> None:
    """Execute 'notes list' command."""
    tag_filter = args.tag
    if tag_filter and not validate_tag(tag_filter):
        return

    notes = load_all_notes()
    if not notes:
        return

    if tag_filter:
        analyzer = StatsAnalyzer(notes)
        filtered_notes = analyzer.get_notes_with_tag(tag_filter)
        if not filtered_notes:
            print(f"No notes found with tag: #{tag_filter}")
            return
        print(f"Notes with tag #{tag_filter}:")
        print("=" * 40)
        for note in filtered_notes:
            print(f"  - {note.filename}")
        print(f"\nTotal: {len(filtered_notes)}")
    else:
        print("All Markdown notes:")
        print("=" * 40)
        for note in notes:
            print(f"  - {note.filename}")
        print(f"\nTotal: {len(notes)}")


def cmd_report(args) -> None:
    """Execute 'notes report' command."""
    if not validate_output_directory():
        return

    notes = load_all_notes()
    if not notes:
        return

    analyzer = StatsAnalyzer(notes)
    report = generate_full_report(analyzer)

    try:
        filepath = os.path.join(OUTPUT_DIR, STATS_REPORT_FILENAME)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        print(report)
        print(f"\nFull report saved to: {filepath}")
    except Exception as e:
        print(f"Error: Could not save report: {e}")
