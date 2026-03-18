"""
search_engine.py - 全文搜索与关键词匹配引擎

提供Markdown笔记的全文搜索功能：
- 关键词匹配（AND逻辑）
- 行预览与上下文提取
- 搜索结果格式化

路径约束：
- 只读目录：./source_data/
- 只写目录：./output_build/

严禁修改 source_data/ 目录内任何文件！
"""

import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

from core_note import Note
from utils.config import SOURCE_DIR, MAX_PREVIEW_LENGTH


@dataclass
class SearchResult:
    """
    搜索结果数据类
    
    Attributes:
        note: 匹配的Note对象
        matched_keywords: 匹配的关键词列表
        matching_lines: 匹配行详情列表
        match_count: 总匹配次数
    """
    note: Note
    matched_keywords: List[str] = field(default_factory=list)
    matching_lines: List[dict] = field(default_factory=list)
    match_count: int = 0
    
    def __post_init__(self):
        if not self.match_count and self.matching_lines:
            self.match_count = len(self.matching_lines)


class SearchEngine:
    """
    搜索引擎类
    
    负责：
    - 加载所有Markdown笔记
    - 执行关键词搜索
    - 生成搜索结果报告
    """
    
    def __init__(self, source_dir: str = SOURCE_DIR):
        """
        初始化搜索引擎
        
        Args:
            source_dir: 笔记源目录路径
        """
        self.source_dir = source_dir
        self.notes: List[Note] = []
        self._loaded = False
    
    def load_notes(self) -> int:
        """
        加载所有Markdown笔记
        
        Returns:
            成功加载的笔记数量
            
        Note:
            只读取.md文件，忽略其他格式
        """
        if self._loaded:
            return len(self.notes)
        
        self.notes = []
        
        try:
            if not os.path.isdir(self.source_dir):
                return 0
            
            for root, dirs, files in os.walk(self.source_dir):
                # 跳过隐藏目录
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for filename in files:
                    if filename.lower().endswith('.md'):
                        filepath = os.path.join(root, filename)
                        note = Note.from_file(filepath)
                        if note:
                            self.notes.append(note)
            
            self._loaded = True
            return len(self.notes)
            
        except Exception:
            return 0
    
    def search(
        self,
        keywords: List[str],
        case_sensitive: bool = False
    ) -> List[SearchResult]:
        """
        搜索包含所有关键词的笔记（AND逻辑）
        
        Args:
            keywords: 关键词列表
            case_sensitive: 是否区分大小写（默认否）
            
        Returns:
            搜索结果列表
        """
        if not self._loaded:
            self.load_notes()
        
        if not keywords:
            return []
        
        results = []
        
        for note in self.notes:
            # 检查是否包含所有关键词
            if case_sensitive:
                match = all(kw in note.content for kw in keywords)
            else:
                match = note.has_all_keywords(keywords)
            
            if match:
                # 获取匹配行详情
                matching_lines = note.get_matching_lines(keywords, context=1)
                
                if matching_lines:
                    result = SearchResult(
                        note=note,
                        matched_keywords=keywords,
                        matching_lines=matching_lines,
                        match_count=len(matching_lines)
                    )
                    results.append(result)
        
        # 按匹配次数降序排序
        results.sort(key=lambda x: x.match_count, reverse=True)
        
        return results
    
    def search_by_tag(self, tag: str) -> List[Note]:
        """
        按标签搜索笔记
        
        Args:
            tag: 标签名称（不含#号）
            
        Returns:
            包含该标签的笔记列表
        """
        if not self._loaded:
            self.load_notes()
        
        return [note for note in self.notes if note.has_tag(tag)]
    
    def format_search_result(
        self,
        result: SearchResult,
        max_preview_lines: int = 3
    ) -> str:
        """
        格式化单个搜索结果为字符串
        
        Args:
            result: 搜索结果对象
            max_preview_lines: 最大预览行数
            
        Returns:
            格式化后的字符串
        """
        lines = []
        
        # 文件信息
        lines.append(f"📄 {result.note.filename}")
        lines.append(f"   路径: {result.note.filepath}")
        lines.append(f"   匹配次数: {result.match_count} | 标签: {', '.join(sorted(result.note.tags)) or '无'}")
        
        # 预览匹配行
        lines.append("   匹配内容:")
        preview_lines = result.matching_lines[:max_preview_lines]
        
        for match in preview_lines:
            line_num = match['line_number']
            content = match['line_content'].strip()
            
            # 截断过长内容
            if len(content) > MAX_PREVIEW_LENGTH:
                content = content[:MAX_PREVIEW_LENGTH - 3] + '...'
            
            lines.append(f"      行{line_num}: {content}")
        
        if len(result.matching_lines) > max_preview_lines:
            lines.append(f"      ... 还有 {len(result.matching_lines) - max_preview_lines} 处匹配")
        
        lines.append("")
        
        return '\n'.join(lines)
    
    def generate_search_report(
        self,
        keywords: List[str],
        results: List[SearchResult]
    ) -> str:
        """
        生成搜索报告
        
        Args:
            keywords: 搜索关键词
            results: 搜索结果列表
            
        Returns:
            报告文本
        """
        lines = []
        
        # 报告头
        lines.append("=" * 60)
        lines.append("Markdown笔记搜索报告")
        lines.append("=" * 60)
        lines.append(f"搜索关键词: {' + '.join(keywords)}")
        lines.append(f"扫描目录: {self.source_dir}")
        lines.append(f"笔记总数: {len(self.notes)}")
        lines.append(f"匹配结果: {len(results)} 篇笔记")
        lines.append("=" * 60)
        lines.append("")
        
        # 结果详情
        if not results:
            lines.append("未找到匹配的笔记。")
        else:
            for i, result in enumerate(results, 1):
                lines.append(f"[{i}/{len(results)}]")
                lines.append(self.format_search_result(result))
        
        lines.append("=" * 60)
        lines.append("报告生成完成")
        lines.append("=" * 60)
        
        return '\n'.join(lines)
    
    def get_all_notes(self) -> List[Note]:
        """获取所有已加载的笔记"""
        if not self._loaded:
            self.load_notes()
        return self.notes
    
    def clear_cache(self) -> None:
        """清除已加载的笔记缓存"""
        self.notes = []
        self._loaded = False
