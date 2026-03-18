"""
core_note.py - Note 数据结构与核心类

定义Note类，封装Markdown笔记的元数据和内容：
- 文件名、路径
- 原始内容
- 提取的标签（#tag格式）
- 提取的链接（[[双链]]格式）
- 行数统计

路径约束：
- 只读目录：./source_data/
- 只写目录：./output_build/

严禁修改 source_data/ 目录内任何文件！
"""

import os
import re
from typing import List, Set, Optional
from dataclasses import dataclass, field

from utils.config import SOURCE_DIR, TAG_PATTERN, WIKILINK_PATTERN


@dataclass
class Note:
    """
    Markdown笔记数据类
    
    Attributes:
        filepath: 笔记文件的绝对路径
        filename: 笔记文件名（不含路径）
        content: 文件原始内容
        lines: 按行分割的内容列表
        tags: 提取的所有标签集合
        wikilinks: 提取的所有双链集合
    """
    filepath: str
    filename: str
    content: str
    lines: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    wikilinks: Set[str] = field(default_factory=set)
    
    @property
    def line_count(self) -> int:
        """返回笔记总行数"""
        return len(self.lines)
    
    @property
    def char_count(self) -> int:
        """返回笔记总字符数"""
        return len(self.content)
    
    @classmethod
    def from_file(cls, filepath: str) -> Optional['Note']:
        """
        从文件路径创建Note实例
        
        Args:
            filepath: Markdown文件的绝对路径
            
        Returns:
            Note实例，如果读取失败则返回None
            
        Raises:
            不抛出异常，所有错误内部处理并返回None
        """
        try:
            # 验证文件存在且为.md文件
            if not os.path.isfile(filepath):
                return None
            if not filepath.lower().endswith('.md'):
                return None
            
            # 读取文件内容
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            filename = os.path.basename(filepath)
            lines = content.split('\n')
            
            # 创建实例
            note = cls(
                filepath=filepath,
                filename=filename,
                content=content,
                lines=lines
            )
            
            # 提取标签和链接
            note._extract_tags()
            note._extract_wikilinks()
            
            return note
            
        except UnicodeDecodeError:
            # 编码错误，尝试其他编码
            try:
                with open(filepath, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                filename = os.path.basename(filepath)
                lines = content.split('\n')
                note = cls(
                    filepath=filepath,
                    filename=filename,
                    content=content,
                    lines=lines
                )
                note._extract_tags()
                note._extract_wikilinks()
                return note
            except Exception:
                return None
        except Exception:
            return None
    
    def _extract_tags(self) -> None:
        """
        从内容中提取标签（#tag格式）
        
        支持格式：
        - #tag
        - #tag/subtag
        - #tag-name
        - 行内任意位置的标签
        """
        try:
            matches = re.findall(TAG_PATTERN, self.content)
            for match in matches:
                # 去除开头的#号
                tag = match[1:] if match.startswith('#') else match
                if tag:
                    self.tags.add(tag.lower())
        except Exception:
            self.tags = set()
    
    def _extract_wikilinks(self) -> None:
        """
        从内容中提取双链（[[link]]格式）
        
        支持格式：
        - [[Page Title]]
        - [[Page Title|Display Text]]
        """
        try:
            matches = re.findall(WIKILINK_PATTERN, self.content)
            for match in matches:
                if match:
                    self.wikilinks.add(match)
        except Exception:
            self.wikilinks = set()
    
    def has_tag(self, tag: str) -> bool:
        """
        检查笔记是否包含指定标签
        
        Args:
            tag: 标签名称（不含#号，大小写不敏感）
            
        Returns:
            如果包含该标签返回True
        """
        return tag.lower() in self.tags
    
    def has_all_keywords(self, keywords: List[str]) -> bool:
        """
        检查笔记是否包含所有关键词（AND逻辑）
        
        Args:
            keywords: 关键词列表
            
        Returns:
            如果包含所有关键词返回True
        """
        content_lower = self.content.lower()
        return all(kw.lower() in content_lower for kw in keywords)
    
    def get_matching_lines(self, keywords: List[str], context: int = 1) -> List[dict]:
        """
        获取包含关键词的行及其上下文
        
        Args:
            keywords: 关键词列表
            context: 上下文行数（默认1行）
            
        Returns:
            匹配行信息列表，每项包含行号、行内容、匹配的关键词
        """
        matches = []
        
        for i, line in enumerate(self.lines):
            line_lower = line.lower()
            matched_keywords = [kw for kw in keywords if kw.lower() in line_lower]
            
            if matched_keywords:
                # 计算上下文范围
                start = max(0, i - context)
                end = min(len(self.lines), i + context + 1)
                context_lines = self.lines[start:end]
                
                matches.append({
                    'line_number': i + 1,  # 1-based
                    'line_content': line,
                    'matched_keywords': matched_keywords,
                    'context_start': start + 1,
                    'context_end': end,
                    'context_lines': context_lines
                })
        
        return matches
    
    def __repr__(self) -> str:
        return f"Note(filename='{self.filename}', tags={len(self.tags)}, lines={self.line_count})"
