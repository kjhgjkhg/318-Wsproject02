"""Configuration constants for the Markdown notes tool."""

import os
from typing import List

SOURCE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "source_data")
OUTPUT_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output_build")

TAG_PATTERN: str = r'#[\w/-]+'
WIKILINK_PATTERN: str = r'\[\[[^\]]+\]\]'
MARKDOWN_EXTENSION: str = '.md'

SEARCH_REPORT_FILENAME: str = 'search_report.txt'
STATS_REPORT_FILENAME: str = 'stats_report.txt'
REPORT_HEADER_WIDTH: int = 80
TABLE_COLUMN_WIDTH: int = 30

TOP_TAGS_LIMIT: int = 10
PREVIEW_CONTEXT_LINES: int = 2
PREVIEW_MAX_CHARS: int = 100

VALID_KEYWORD_PATTERN: str = r'^[\w\s/-]+$'
