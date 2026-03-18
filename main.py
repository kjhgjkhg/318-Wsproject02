"""Main entry point for the Markdown notes CLI tool."""

import argparse
import sys

from cli_commands import cmd_search, cmd_tags, cmd_stats, cmd_list, cmd_report


def main():
    """Parse arguments and execute commands."""
    parser = argparse.ArgumentParser(
        prog='notes',
        description='Markdown notes search and statistics tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    search_parser = subparsers.add_parser('search', help='Search notes by keyword')
    search_parser.add_argument('keywords', nargs='+', help='Search keywords (AND logic)')
    search_parser.set_defaults(func=cmd_search)

    tags_parser = subparsers.add_parser('tags', help='List all tags by frequency')
    tags_parser.set_defaults(func=cmd_tags)

    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.set_defaults(func=cmd_stats)

    list_parser = subparsers.add_parser('list', help='List notes')
    list_parser.add_argument('--tag', help='Filter by tag')
    list_parser.set_defaults(func=cmd_list)

    report_parser = subparsers.add_parser('report', help='Generate full report')
    report_parser.set_defaults(func=cmd_report)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
