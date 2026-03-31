"""
core_note.py - Note 数据结构模块

定义 Note 数据结构，包含文件名、内容、提取的标签/链接等信息。
"""

import os
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from utils.config import TAG_PATTERN, WIKI_LINK_PATTERN, ENCODING
from utils.validators import is_markdown_file


@dataclass
class Note:
    """
    Markdown 笔记数据结构。

    Attributes:
        file_path: 文件完整路径
        file_name: 文件名
        content: 文件内容
        lines: 按行分割的内容列表
        tags: 提取的标签列表
        wiki_links: 提取的双链列表
        line_count: 总行数
        word_count: 总字数（粗略统计）
    """
    file_path: str
    file_name: str = ""
    content: str = ""
    lines: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    wiki_links: List[str] = field(default_factory=list)
    line_count: int = 0
    word_count: int = 0

    def __post_init__(self) -> None:
        """初始化后处理。"""
        self.file_name = os.path.basename(self.file_path)

    def load_content(self) -> bool:
        """
        从文件加载内容。

        Returns:
            是否加载成功
        """
        try:
            with open(self.file_path, "r", encoding=ENCODING) as f:
                self.content = f.read()
            self._parse_content()
            return True
        except UnicodeDecodeError:
            try:
                with open(self.file_path, "r", encoding="gbk") as f:
                    self.content = f.read()
                self._parse_content()
                return True
            except Exception as e:
                print(f"警告: 无法读取文件 {self.file_path}: {e}")
                return False
        except FileNotFoundError:
            print(f"警告: 文件不存在 {self.file_path}")
            return False
        except Exception as e:
            print(f"警告: 读取文件时发生错误 {self.file_path}: {e}")
            return False

    def _parse_content(self) -> None:
        """解析内容，提取标签和链接。"""
        self.lines = self.content.split("\n")
        self.line_count = len(self.lines)
        self.word_count = len(self.content.replace("\n", "").replace(" ", ""))
        self._extract_tags()
        self._extract_wiki_links()

    def _extract_tags(self) -> None:
        """提取所有标签。"""
        try:
            pattern = re.compile(TAG_PATTERN)
            matches = pattern.findall(self.content)
            self.tags = list(set(matches))
        except re.error as e:
            print(f"警告: 标签提取正则错误: {e}")
            self.tags = []

    def _extract_wiki_links(self) -> None:
        """提取所有双链。"""
        try:
            pattern = re.compile(WIKI_LINK_PATTERN)
            matches = pattern.findall(self.content)
            self.wiki_links = list(set(matches))
        except re.error as e:
            print(f"警告: 双链提取正则错误: {e}")
            self.wiki_links = []

    def has_tag(self, tag: str) -> bool:
        """
        检查是否包含指定标签。

        Args:
            tag: 标签

        Returns:
            是否包含该标签
        """
        normalized = tag if tag.startswith("#") else "#" + tag
        return normalized in self.tags

    def get_matching_lines(self, keyword: str, case_sensitive: bool = False) -> List[tuple]:
        """
        获取包含关键词的行及其行号。

        Args:
            keyword: 搜索关键词
            case_sensitive: 是否区分大小写

        Returns:
            (行号, 行内容) 元组列表
        """
        matches = []
        search_content = keyword if case_sensitive else keyword.lower()
        for idx, line in enumerate(self.lines, start=1):
            line_to_search = line if case_sensitive else line.lower()
            if search_content in line_to_search:
                matches.append((idx, line.strip()))
        return matches


class NoteCollection:
    """
    笔记集合管理器。

    用于批量加载和管理多个笔记文件。
    """

    def __init__(self) -> None:
        """初始化笔记集合。"""
        self.notes: List[Note] = []
        self._file_paths: List[str] = []

    def load_from_directory(self, directory: str) -> int:
        """
        从目录加载所有 Markdown 文件。

        Args:
            directory: 目录路径

        Returns:
            成功加载的文件数量
        """
        loaded_count = 0
        try:
            for root, dirs, files in os.walk(directory):
                for filename in files:
                    if is_markdown_file(filename):
                        file_path = os.path.join(root, filename)
                        note = Note(file_path=file_path)
                        if note.load_content():
                            self.notes.append(note)
                            self._file_paths.append(file_path)
                            loaded_count += 1
        except Exception as e:
            print(f"错误: 扫描目录时发生异常: {e}")
        return loaded_count

    def get_all_tags(self) -> Dict[str, int]:
        """
        获取所有标签及其出现次数。

        Returns:
            标签到出现次数的映射
        """
        tag_counts: Dict[str, int] = {}
        for note in self.notes:
            for tag in note.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return tag_counts

    def get_all_wiki_links(self) -> Dict[str, int]:
        """
        获取所有双链及其出现次数。

        Returns:
            双链到出现次数的映射
        """
        link_counts: Dict[str, int] = {}
        for note in self.notes:
            for link in note.wiki_links:
                link_counts[link] = link_counts.get(link, 0) + 1
        return link_counts

    def get_total_lines(self) -> int:
        """
        获取所有笔记的总行数。

        Returns:
            总行数
        """
        return sum(note.line_count for note in self.notes)

    def get_total_words(self) -> int:
        """
        获取所有笔记的总字数。

        Returns:
            总字数
        """
        return sum(note.word_count for note in self.notes)

    def filter_by_tag(self, tag: str) -> List[Note]:
        """
        按标签过滤笔记。

        Args:
            tag: 标签

        Returns:
            包含该标签的笔记列表
        """
        return [note for note in self.notes if note.has_tag(tag)]

    def __len__(self) -> int:
        """返回笔记数量。"""
        return len(self.notes)

    def __iter__(self):
        """迭代器。"""
        return iter(self.notes)
