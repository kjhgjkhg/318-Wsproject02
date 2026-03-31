"""
cli_commands.py - 子命令实现模块

实现 search / tags / stats / list / report 等子命令的具体逻辑。
"""

import os
from typing import List, Optional

from core_note import NoteCollection
from search_engine import SearchEngine, format_search_results
from stats_analyzer import StatsAnalyzer, ReportGenerator
from utils.config import (
    SOURCE_DATA_DIR,
    OUTPUT_BUILD_DIR,
    SEARCH_REPORT_FILE,
    STATS_REPORT_FILE,
    ENCODING
)
from utils.validators import (
    validate_source_directory,
    validate_output_directory,
    validate_keywords,
    validate_tag_filter,
    normalize_tag
)


class CommandContext:
    """
    命令执行上下文。

    管理共享的笔记集合和状态。
    """

    def __init__(self) -> None:
        """初始化上下文。"""
        self._notes: Optional[NoteCollection] = None
        self._loaded: bool = False

    def load_notes(self) -> bool:
        """
        加载笔记。

        Returns:
            是否加载成功
        """
        if self._loaded:
            return True

        is_valid, error = validate_source_directory()
        if not is_valid:
            print(f"错误: {error}")
            return False

        self._notes = NoteCollection()
        count = self._notes.load_from_directory(SOURCE_DATA_DIR)

        if count == 0:
            print("警告: 源目录中没有找到 Markdown 文件")
            self._loaded = True
            return True

        print(f"已加载 {count} 个笔记文件")
        self._loaded = True
        return True

    @property
    def notes(self) -> NoteCollection:
        """获取笔记集合。"""
        if self._notes is None:
            self._notes = NoteCollection()
        return self._notes


def cmd_search(keywords: List[str], ctx: Optional[CommandContext] = None) -> int:
    """
    执行搜索命令。

    Args:
        keywords: 搜索关键词列表
        ctx: 命令上下文

    Returns:
        退出码
    """
    is_valid, error = validate_keywords(keywords)
    if not is_valid:
        print(f"错误: {error}")
        return 1

    if ctx is None:
        ctx = CommandContext()

    if not ctx.load_notes():
        return 1

    engine = SearchEngine(ctx.notes)
    results = engine.search(keywords, case_sensitive=False, match_all=True)

    output = format_search_results(results)
    print(output)

    return 0


def cmd_tags(ctx: Optional[CommandContext] = None) -> int:
    """
    执行标签列表命令。

    Args:
        ctx: 命令上下文

    Returns:
        退出码
    """
    if ctx is None:
        ctx = CommandContext()

    if not ctx.load_notes():
        return 1

    analyzer = StatsAnalyzer(ctx.notes)
    tag_stats = analyzer.get_tag_statistics()

    if not tag_stats:
        print("未找到任何标签")
        return 0

    print("=" * 50)
    print("标签列表（按出现次数降序）")
    print("=" * 50)
    print(f"{'排名':<6}{'标签':<30}{'次数':<10}")
    print("-" * 46)

    for idx, (tag, count) in enumerate(tag_stats.items(), start=1):
        print(f"{idx:<6}{tag:<30}{count:<10}")

    print("=" * 50)
    print(f"共 {len(tag_stats)} 个标签")

    return 0


def cmd_stats(ctx: Optional[CommandContext] = None) -> int:
    """
    执行统计命令。

    Args:
        ctx: 命令上下文

    Returns:
        退出码
    """
    if ctx is None:
        ctx = CommandContext()

    if not ctx.load_notes():
        return 1

    analyzer = StatsAnalyzer(ctx.notes)
    stats = analyzer.get_full_statistics()

    print("=" * 50)
    print("笔记统计概览")
    print("=" * 50)
    print(f"笔记总数: {stats['note_count']} 个")
    print(f"总行数: {stats['total_lines']} 行")
    print(f"总字数: {stats['total_words']} 字")
    print("")
    print("-" * 50)
    print(f"热门标签 Top 10:")
    print("-" * 50)

    if stats['top_tags']:
        for idx, (tag, count) in enumerate(stats['top_tags'], start=1):
            print(f"  {idx}. {tag}: {count}")
    else:
        print("  暂无标签数据")

    print("")
    print("-" * 50)
    print("双链统计:")
    print("-" * 50)
    print(f"  双链总数: {stats['wiki_link_count']} 个")
    print(f"  唯一双链: {stats['unique_wiki_links']} 个")

    return 0


def cmd_list(tag: str, ctx: Optional[CommandContext] = None) -> int:
    """
    执行列表命令。

    Args:
        tag: 过滤标签
        ctx: 命令上下文

    Returns:
        退出码
    """
    is_valid, error = validate_tag_filter(tag)
    if not is_valid:
        print(f"错误: {error}")
        return 1

    normalized_tag = normalize_tag(tag)

    if ctx is None:
        ctx = CommandContext()

    if not ctx.load_notes():
        return 1

    filtered_notes = ctx.notes.filter_by_tag(normalized_tag)

    if not filtered_notes:
        print(f"未找到带有标签 {normalized_tag} 的笔记")
        return 0

    print("=" * 50)
    print(f"带有标签 {normalized_tag} 的笔记")
    print("=" * 50)

    for idx, note in enumerate(filtered_notes, start=1):
        print(f"  {idx}. {note.file_name}")

    print("-" * 50)
    print(f"共 {len(filtered_notes)} 个笔记")

    return 0


def cmd_report(ctx: Optional[CommandContext] = None) -> int:
    """
    执行报告生成命令。

    Args:
        ctx: 命令上下文

    Returns:
        退出码
    """
    is_valid, error = validate_output_directory()
    if not is_valid:
        print(f"错误: {error}")
        return 1

    if ctx is None:
        ctx = CommandContext()

    if not ctx.load_notes():
        return 1

    analyzer = StatsAnalyzer(ctx.notes)
    generator = ReportGenerator(analyzer)

    stats_report = generator.generate_stats_report()
    stats_report_path = os.path.join(OUTPUT_BUILD_DIR, STATS_REPORT_FILE)

    try:
        with open(stats_report_path, "w", encoding=ENCODING) as f:
            f.write(stats_report)
        print(f"统计报告已保存: {stats_report_path}")
    except IOError as e:
        print(f"错误: 无法保存统计报告: {e}")
        return 1

    tags_report = generator.generate_tags_report()
    tags_report_path = os.path.join(OUTPUT_BUILD_DIR, "tags_report.txt")

    try:
        with open(tags_report_path, "w", encoding=ENCODING) as f:
            f.write(tags_report)
        print(f"标签报告已保存: {tags_report_path}")
    except IOError as e:
        print(f"错误: 无法保存标签报告: {e}")
        return 1

    print("")
    print("报告生成完成！")

    return 0
