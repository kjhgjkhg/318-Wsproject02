"""
main.py - Markdown笔记搜索与统计工具主入口

此模块为CLI工具的唯一入口，负责：
- 解析命令行参数（argparse）
- 调度各子命令执行
- 处理全局异常

路径约束：
- 只读目录：./source_data/
- 只写目录：./output_build/

严禁修改 source_data/ 目录内任何文件！
"""

import argparse
import sys
from typing import Optional

from cli_commands import (
    cmd_search,
    cmd_tags,
    cmd_stats,
    cmd_list,
    cmd_report,
)
from utils.validators import validate_source_directory
from utils.config import SOURCE_DIR


def create_parser() -> argparse.ArgumentParser:
    """创建并配置argparse解析器"""
    parser = argparse.ArgumentParser(
        prog='notes',
        description='本地Markdown笔记快速搜索与标签统计工具',
        epilog='示例: notes search "Python" | notes tags | notes stats'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用子命令')
    
    # search 子命令
    search_parser = subparsers.add_parser(
        'search',
        help='搜索包含关键词的笔记'
    )
    search_parser.add_argument(
        'keywords',
        nargs='+',
        help='搜索关键词（支持多个，AND逻辑）'
    )
    search_parser.add_argument(
        '--output', '-o',
        action='store_true',
        help='将结果保存到输出目录'
    )
    
    # tags 子命令
    tags_parser = subparsers.add_parser(
        'tags',
        help='列出所有标签及出现次数'
    )
    tags_parser.add_argument(
        '--limit', '-n',
        type=int,
        default=0,
        help='限制显示数量（0表示无限制）'
    )
    
    # stats 子命令
    stats_parser = subparsers.add_parser(
        'stats',
        help='显示统计信息'
    )
    
    # list 子命令
    list_parser = subparsers.add_parser(
        'list',
        help='列出指定标签的笔记'
    )
    list_parser.add_argument(
        '--tag', '-t',
        required=True,
        help='标签名称（不含#号）'
    )
    
    # report 子命令
    report_parser = subparsers.add_parser(
        'report',
        help='生成完整统计报告'
    )
    report_parser.add_argument(
        '--filename', '-f',
        default='full_report.txt',
        help='报告文件名（默认: full_report.txt）'
    )
    
    return parser


def main(args: Optional[list] = None) -> int:
    """
    主入口函数
    
    Args:
        args: 命令行参数列表，None表示使用sys.argv
        
    Returns:
        退出码：0成功，1失败
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # 验证源目录
    if not validate_source_directory(SOURCE_DIR):
        print(f"错误: 源目录不存在或无法访问: {SOURCE_DIR}", file=sys.stderr)
        return 1
    
    # 无子命令时显示帮助
    if parsed_args.command is None:
        parser.print_help()
        return 0
    
    # 调度子命令
    try:
        if parsed_args.command == 'search':
            return cmd_search(parsed_args.keywords, parsed_args.output)
        elif parsed_args.command == 'tags':
            return cmd_tags(parsed_args.limit)
        elif parsed_args.command == 'stats':
            return cmd_stats()
        elif parsed_args.command == 'list':
            return cmd_list(parsed_args.tag)
        elif parsed_args.command == 'report':
            return cmd_report(parsed_args.filename)
        else:
            parser.print_help()
            return 0
    except KeyboardInterrupt:
        print("\n操作已取消", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
