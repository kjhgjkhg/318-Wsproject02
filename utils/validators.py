"""Input validation utilities for the Markdown notes tool."""

import os
import re
from typing import List, Optional

from utils.config import SOURCE_DIR, OUTPUT_DIR, VALID_KEYWORD_PATTERN


def validate_source_directory() -> bool:
    """Validate that the source directory exists."""
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory not found: {SOURCE_DIR}")
        return False
    if not os.path.isdir(SOURCE_DIR):
        print(f"Error: Source path is not a directory: {SOURCE_DIR}")
        return False
    return True


def validate_output_directory() -> bool:
    """Validate and create output directory if needed."""
    try:
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR, exist_ok=True)
        return True
    except OSError as e:
        print(f"Error: Could not create output directory: {e}")
        return False


def validate_keywords(keywords: List[str]) -> bool:
    """Validate search keywords."""
    if not keywords:
        print("Error: No keywords provided")
        return False
    pattern = re.compile(VALID_KEYWORD_PATTERN)
    for keyword in keywords:
        if not keyword.strip():
            print("Error: Empty keyword provided")
            return False
        if not pattern.match(keyword):
            print(f"Error: Invalid keyword format: {keyword}")
            return False
    return True


def validate_tag(tag: str) -> bool:
    """Validate tag format."""
    if not tag:
        print("Error: No tag provided")
        return False
    if not re.match(r'^[\w/-]+$', tag):
        print(f"Error: Invalid tag format: {tag}")
        return False
    return True


def get_markdown_files() -> List[str]:
    """Get all markdown files from source directory."""
    markdown_files = []
    try:
        for root, _, files in os.walk(SOURCE_DIR):
            for file in files:
                if file.endswith('.md'):
                    markdown_files.append(os.path.join(root, file))
    except OSError as e:
        print(f"Error: Could not scan source directory: {e}")
        return []
    return markdown_files


def safe_read_file(filepath: str) -> Optional[str]:
    """Safely read a file with error handling."""
    encodings = ['utf-8-sig', 'utf-8', 'utf-16', 'cp1252', 'latin-1']
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
                if encoding == 'utf-16':
                    content = content.encode('utf-8').decode('utf-8')
                return content
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Warning: Could not read {filepath}: {e}")
            return None
    try:
        with open(filepath, 'r', encoding='latin-1') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}")
        return None
