"""
search_engine.py - 全文搜索模块

实现全文搜索、关键词匹配、行预览等功能。
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

from core_note import Note, NoteCollection


@dataclass
class SearchResult:
    """
    搜索结果数据结构。

    Attributes:
        note: 匹配的笔记对象
        matched_lines: 匹配的行信息列表 [(行号, 行内容, 匹配的关键词列表)]
        match_count: 匹配次数
    """
    note: Note
    matched_lines: List[Tuple[int, str, List[str]]]
    match_count: int = 0

    def __post_init__(self) -> None:
        """计算匹配次数。"""
        self.match_count = len(self.matched_lines)


class SearchEngine:
    """
    搜索引擎类。

    提供全文搜索、关键词匹配等功能。
    """

    def __init__(self, notes: NoteCollection) -> None:
        """
        初始化搜索引擎。

        Args:
            notes: 笔记集合
        """
        self.notes = notes

    def search(
        self,
        keywords: List[str],
        case_sensitive: bool = False,
        match_all: bool = True
    ) -> List[SearchResult]:
        """
        搜索包含关键词的笔记。

        Args:
            keywords: 关键词列表
            case_sensitive: 是否区分大小写
            match_all: 是否需要匹配所有关键词（AND逻辑）

        Returns:
            搜索结果列表
        """
        results: List[SearchResult] = []
        if not keywords:
            return results

        normalized_keywords = self._normalize_keywords(keywords, case_sensitive)

        for note in self.notes:
            matched_lines = self._search_in_note(
                note, normalized_keywords, case_sensitive, match_all
            )
            if matched_lines:
                results.append(SearchResult(note=note, matched_lines=matched_lines))

        results.sort(key=lambda x: x.match_count, reverse=True)
        return results

    def _normalize_keywords(
        self, keywords: List[str], case_sensitive: bool
    ) -> List[str]:
        """
        标准化关键词。

        Args:
            keywords: 原始关键词列表
            case_sensitive: 是否区分大小写

        Returns:
            标准化后的关键词列表
        """
        if case_sensitive:
            return [kw.strip() for kw in keywords if kw.strip()]
        return [kw.strip().lower() for kw in keywords if kw.strip()]

    def _search_in_note(
        self,
        note: Note,
        keywords: List[str],
        case_sensitive: bool,
        match_all: bool
    ) -> List[Tuple[int, str, List[str]]]:
        """
        在单个笔记中搜索关键词。

        Args:
            note: 笔记对象
            keywords: 标准化后的关键词列表
            case_sensitive: 是否区分大小写
            match_all: 是否需要匹配所有关键词

        Returns:
            匹配的行信息列表
        """
        matched_lines: List[Tuple[int, str, List[str]]] = []

        for line_num, line_content in enumerate(note.lines, start=1):
            line_to_search = line_content if case_sensitive else line_content.lower()
            matched_keywords = []

            for kw in keywords:
                if kw in line_to_search:
                    matched_keywords.append(kw)

            if matched_keywords:
                if match_all:
                    if len(matched_keywords) == len(keywords):
                        matched_lines.append((line_num, line_content.strip(), matched_keywords))
                else:
                    matched_lines.append((line_num, line_content.strip(), matched_keywords))

        return matched_lines

    def search_single_keyword(
        self, keyword: str, case_sensitive: bool = False
    ) -> List[SearchResult]:
        """
        搜索单个关键词。

        Args:
            keyword: 搜索关键词
            case_sensitive: 是否区分大小写

        Returns:
            搜索结果列表
        """
        return self.search([keyword], case_sensitive=case_sensitive, match_all=True)


def format_search_result(result: SearchResult, max_preview_length: int = 100) -> str:
    """
    格式化单个搜索结果。

    Args:
        result: 搜索结果
        max_preview_length: 行预览最大长度

    Returns:
        格式化后的字符串
    """
    lines = []
    lines.append(f"文件: {result.note.file_name}")
    lines.append(f"匹配数: {result.match_count}")
    lines.append("匹配行:")

    for line_num, line_content, matched_kws in result.matched_lines:
        preview = line_content[:max_preview_length]
        if len(line_content) > max_preview_length:
            preview += "..."
        lines.append(f"  L{line_num}: {preview}")

    return "\n".join(lines)


def format_search_results(
    results: List[SearchResult],
    max_preview_length: int = 100,
    show_summary: bool = True
) -> str:
    """
    格式化搜索结果列表。

    Args:
        results: 搜索结果列表
        max_preview_length: 行预览最大长度
        show_summary: 是否显示摘要

    Returns:
        格式化后的字符串
    """
    if not results:
        return "未找到匹配结果。"

    lines = []
    lines.append("=" * 60)
    lines.append("搜索结果")
    lines.append("=" * 60)

    for idx, result in enumerate(results, start=1):
        lines.append(f"\n[{idx}] {format_search_result(result, max_preview_length)}")
        lines.append("-" * 40)

    if show_summary:
        lines.append("\n" + "=" * 60)
        lines.append(f"共找到 {len(results)} 个文件，")
        total_matches = sum(r.match_count for r in results)
        lines.append(f"总计 {total_matches} 处匹配。")
        lines.append("=" * 60)

    return "\n".join(lines)
