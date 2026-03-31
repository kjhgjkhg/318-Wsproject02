"""
stats_analyzer.py - 统计分析模块

实现标签统计、关键词频率、前缀计数、报告生成等功能。
"""

from collections import Counter
from typing import List, Dict, Tuple, Optional
from datetime import datetime

from core_note import NoteCollection
from utils.config import TOP_TAGS_COUNT


class StatsAnalyzer:
    """
    统计分析器。

    提供标签统计、关键词频率分析、报告生成等功能。
    """

    def __init__(self, notes: NoteCollection) -> None:
        """
        初始化统计分析器。

        Args:
            notes: 笔记集合
        """
        self.notes = notes

    def get_note_count(self) -> int:
        """
        获取笔记总数。

        Returns:
            笔记数量
        """
        return len(self.notes)

    def get_total_lines(self) -> int:
        """
        获取总行数。

        Returns:
            总行数
        """
        return self.notes.get_total_lines()

    def get_total_words(self) -> int:
        """
        获取总字数。

        Returns:
            总字数
        """
        return self.notes.get_total_words()

    def get_tag_statistics(self) -> Dict[str, int]:
        """
        获取标签统计。

        Returns:
            标签到出现次数的映射（按次数降序）
        """
        tag_counts = self.notes.get_all_tags()
        return dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True))

    def get_top_tags(self, top_n: int = TOP_TAGS_COUNT) -> List[Tuple[str, int]]:
        """
        获取热门标签。

        Args:
            top_n: 返回数量

        Returns:
            (标签, 次数) 元组列表
        """
        tag_stats = self.get_tag_statistics()
        return list(tag_stats.items())[:top_n]

    def get_wiki_link_statistics(self) -> Dict[str, int]:
        """
        获取双链统计。

        Returns:
            双链到出现次数的映射（按次数降序）
        """
        link_counts = self.notes.get_all_wiki_links()
        return dict(sorted(link_counts.items(), key=lambda x: x[1], reverse=True))

    def get_wiki_link_count(self) -> int:
        """
        获取双链总数。

        Returns:
            双链总数
        """
        return sum(self.notes.get_all_wiki_links().values())

    def get_unique_wiki_link_count(self) -> int:
        """
        获取唯一双链数量。

        Returns:
            唯一双链数量
        """
        return len(self.notes.get_all_wiki_links())

    def get_full_statistics(self) -> Dict:
        """
        获取完整统计数据。

        Returns:
            包含所有统计信息的字典
        """
        return {
            "note_count": self.get_note_count(),
            "total_lines": self.get_total_lines(),
            "total_words": self.get_total_words(),
            "top_tags": self.get_top_tags(),
            "all_tags": self.get_tag_statistics(),
            "wiki_link_count": self.get_wiki_link_count(),
            "unique_wiki_links": self.get_unique_wiki_link_count(),
            "top_wiki_links": list(self.get_wiki_link_statistics().items())[:TOP_TAGS_COUNT]
        }


class ReportGenerator:
    """
    报告生成器。

    生成纯文本格式的统计报告。
    """

    def __init__(self, analyzer: StatsAnalyzer) -> None:
        """
        初始化报告生成器。

        Args:
            analyzer: 统计分析器
        """
        self.analyzer = analyzer

    def generate_stats_report(self) -> str:
        """
        生成统计报告。

        Returns:
            报告文本
        """
        stats = self.analyzer.get_full_statistics()
        lines = []

        lines.append("=" * 70)
        lines.append("Markdown 笔记统计报告")
        lines.append("=" * 70)
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        lines.append("-" * 70)
        lines.append("基础统计")
        lines.append("-" * 70)
        lines.append(f"笔记总数: {stats['note_count']} 个")
        lines.append(f"总行数: {stats['total_lines']} 行")
        lines.append(f"总字数: {stats['total_words']} 字")
        lines.append("")

        lines.append("-" * 70)
        lines.append(f"热门标签 Top {TOP_TAGS_COUNT}")
        lines.append("-" * 70)
        if stats['top_tags']:
            lines.append(f"{'排名':<6}{'标签':<30}{'出现次数':<10}")
            lines.append("-" * 46)
            for idx, (tag, count) in enumerate(stats['top_tags'], start=1):
                lines.append(f"{idx:<6}{tag:<30}{count:<10}")
        else:
            lines.append("暂无标签数据")
        lines.append("")

        lines.append("-" * 70)
        lines.append("双链统计")
        lines.append("-" * 70)
        lines.append(f"双链总数: {stats['wiki_link_count']} 个")
        lines.append(f"唯一双链: {stats['unique_wiki_links']} 个")
        if stats['top_wiki_links']:
            lines.append("")
            lines.append(f"热门双链 Top {TOP_TAGS_COUNT}:")
            lines.append(f"{'排名':<6}{'链接':<40}{'次数':<10}")
            lines.append("-" * 56)
            for idx, (link, count) in enumerate(stats['top_wiki_links'], start=1):
                lines.append(f"{idx:<6}{link:<40}{count:<10}")
        lines.append("")

        lines.append("-" * 70)
        lines.append("全部标签列表")
        lines.append("-" * 70)
        if stats['all_tags']:
            for tag, count in stats['all_tags'].items():
                lines.append(f"  {tag}: {count}")
        else:
            lines.append("暂无标签数据")
        lines.append("")

        lines.append("=" * 70)
        lines.append("报告结束")
        lines.append("=" * 70)

        return "\n".join(lines)

    def generate_tags_report(self) -> str:
        """
        生成标签报告。

        Returns:
            报告文本
        """
        tag_stats = self.analyzer.get_tag_statistics()
        lines = []

        lines.append("=" * 70)
        lines.append("标签统计报告")
        lines.append("=" * 70)
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"标签总数: {len(tag_stats)} 个")
        lines.append("")

        lines.append("-" * 70)
        lines.append(f"{'排名':<6}{'标签':<30}{'出现次数':<10}")
        lines.append("-" * 46)

        for idx, (tag, count) in enumerate(tag_stats.items(), start=1):
            lines.append(f"{idx:<6}{tag:<30}{count:<10}")

        lines.append("")
        lines.append("=" * 70)

        return "\n".join(lines)

    def generate_search_report(
        self,
        keywords: List[str],
        matched_files: List[str],
        total_matches: int
    ) -> str:
        """
        生成搜索报告。

        Args:
            keywords: 搜索关键词
            matched_files: 匹配的文件列表
            total_matches: 总匹配数

        Returns:
            报告文本
        """
        lines = []

        lines.append("=" * 70)
        lines.append("搜索结果报告")
        lines.append("=" * 70)
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"搜索关键词: {', '.join(keywords)}")
        lines.append(f"匹配文件数: {len(matched_files)} 个")
        lines.append(f"总匹配数: {total_matches} 处")
        lines.append("")

        lines.append("-" * 70)
        lines.append("匹配文件列表")
        lines.append("-" * 70)

        for idx, filename in enumerate(matched_files, start=1):
            lines.append(f"  {idx}. {filename}")

        lines.append("")
        lines.append("=" * 70)

        return "\n".join(lines)
