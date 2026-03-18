"""
main.py - 程序主入口

命令行工具入口，使用 argparse 实现子命令解析与流程调度。
"""

import argparse
import sys
from typing import List, Optional

from cli_commands import (
    cmd_search,
    cmd_tags,
    cmd_stats,
    cmd_list,
    cmd_report,
    CommandContext
)


def create_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器。

    Returns:
        配置好的 ArgumentParser 实例
    """
    parser = argparse.ArgumentParser(
        prog="notes",
        description="Markdown 笔记快速搜索与标签统计工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  notes search "关键词"        搜索包含关键词的笔记
  notes search "关键词1" "关键词2"  搜索同时包含多个关键词的笔记
  notes tags                   列出所有标签
  notes stats                  显示统计信息
  notes list --tag work        列出带有指定标签的笔记
  notes report                 生成完整统计报告
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    search_parser = subparsers.add_parser(
        "search",
        help="搜索包含关键词的笔记"
    )
    search_parser.add_argument(
        "keywords",
        nargs="+",
        help="搜索关键词（支持多个关键词，AND 逻辑）"
    )
    search_parser.add_argument(
        "-c", "--case-sensitive",
        action="store_true",
        help="区分大小写"
    )

    subparsers.add_parser(
        "tags",
        help="列出所有标签（按出现次数降序）"
    )

    subparsers.add_parser(
        "stats",
        help="显示统计信息"
    )

    list_parser = subparsers.add_parser(
        "list",
        help="列出带有指定标签的笔记"
    )
    list_parser.add_argument(
        "--tag",
        required=True,
        help="过滤标签"
    )

    subparsers.add_parser(
        "report",
        help="生成完整统计报告"
    )

    return parser


def main(args: Optional[List[str]] = None) -> int:
    """
    主函数。

    Args:
        args: 命令行参数列表，为 None 时从 sys.argv 获取

    Returns:
        退出码
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 0

    ctx = CommandContext()

    if parsed_args.command == "search":
        return cmd_search(parsed_args.keywords, ctx)
    elif parsed_args.command == "tags":
        return cmd_tags(ctx)
    elif parsed_args.command == "stats":
        return cmd_stats(ctx)
    elif parsed_args.command == "list":
        return cmd_list(parsed_args.tag, ctx)
    elif parsed_args.command == "report":
        return cmd_report(ctx)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
