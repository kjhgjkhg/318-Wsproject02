"""
stats_analyzer.py - 标签统计、关键词频率、报告生成核心

提供Markdown笔记的统计分析功能：
- 标签频率统计（支持多级标签）
- 双链（[[wikilink]]）统计
- 笔记元数据统计
- 纯文本报告生成

路径约束：
- 只读目录：./source_data/
- 只写目录：./output_build/

严禁修改 source_data/ 目录内任何文件！
"""

import os
from typing import List, Dict, Tuple, Optional, Counter as CounterType
from collections import Counter
from dataclasses import dataclass, field

from core_note import Note
from search_engine import SearchEngine
from utils.config import (
    SOURCE_DIR,
    OUTPUT_DIR,
    TOP_TAGS_LIMIT,
    REPORT_SEPARATOR,
)


@dataclass
class StatsSummary:
    """
    统计摘要数据类
    
    Attributes:
        total_notes: 笔记总数
        total_lines: 总行数
        total_chars: 总字符数
        total_tags: 标签总数（去重）
        total_wikilinks: 双链总数（去重）
        tag_counts: 标签频率字典
        wikilink_counts: 双链频率字典
        top_tags: 热门标签列表
    """
    total_notes: int = 0
    total_lines: int = 0
    total_chars: int = 0
    total_tags: int = 0
    total_wikilinks: int = 0
    tag_counts: Dict[str, int] = field(default_factory=dict)
    wikilink_counts: Dict[str, int] = field(default_factory=dict)
    top_tags: List[Tuple[str, int]] = field(default_factory=list)
    
    @property
    def avg_lines_per_note(self) -> float:
        """平均每篇笔记行数"""
        if self.total_notes == 0:
            return 0.0
        return round(self.total_lines / self.total_notes, 2)
    
    @property
    def avg_chars_per_note(self) -> float:
        """平均每篇笔记字符数"""
        if self.total_notes == 0:
            return 0.0
        return round(self.total_chars / self.total_notes, 2)


class StatsAnalyzer:
    """
    统计分析器类
    
    负责：
    - 收集所有标签并统计频率
    - 收集所有双链并统计频率
    - 计算笔记元数据
    - 生成统计报告
    """
    
    def __init__(self, source_dir: str = SOURCE_DIR):
        """
        初始化统计分析器
        
        Args:
            source_dir: 笔记源目录路径
        """
        self.source_dir = source_dir
        self.search_engine = SearchEngine(source_dir)
        self._stats: Optional[StatsSummary] = None
    
    def analyze(self) -> StatsSummary:
        """
        执行完整统计分析
        
        Returns:
            统计摘要对象
        """
        # 加载所有笔记
        self.search_engine.load_notes()
        notes = self.search_engine.get_all_notes()
        
        if not notes:
            self._stats = StatsSummary()
            return self._stats
        
        # 基础统计
        total_lines = sum(note.line_count for note in notes)
        total_chars = sum(note.char_count for note in notes)
        
        # 标签统计
        all_tags = []
        for note in notes:
            all_tags.extend(note.tags)
        tag_counter = Counter(all_tags)
        
        # 双链统计
        all_wikilinks = []
        for note in notes:
            all_wikilinks.extend(note.wikilinks)
        wikilink_counter = Counter(all_wikilinks)
        
        # 热门标签
        top_tags = tag_counter.most_common(TOP_TAGS_LIMIT)
        
        self._stats = StatsSummary(
            total_notes=len(notes),
            total_lines=total_lines,
            total_chars=total_chars,
            total_tags=len(tag_counter),
            total_wikilinks=len(wikilink_counter),
            tag_counts=dict(tag_counter),
            wikilink_counts=dict(wikilink_counter),
            top_tags=top_tags
        )
        
        return self._stats
    
    def get_all_tags(self, sort_by_count: bool = True) -> List[Tuple[str, int]]:
        """
        获取所有标签及其出现次数
        
        Args:
            sort_by_count: 是否按次数降序排序
            
        Returns:
            (标签, 次数) 元组列表
        """
        if self._stats is None:
            self.analyze()
        
        tags = list(self._stats.tag_counts.items())
        
        if sort_by_count:
            tags.sort(key=lambda x: x[1], reverse=True)
        else:
            tags.sort(key=lambda x: x[0])
        
        return tags
    
    def get_top_wikilinks(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        获取热门双链
        
        Args:
            limit: 返回数量限制
            
        Returns:
            (双链, 次数) 元组列表
        """
        if self._stats is None:
            self.analyze()
        
        wikilinks = list(self._stats.wikilink_counts.items())
        wikilinks.sort(key=lambda x: x[1], reverse=True)
        
        return wikilinks[:limit]
    
    def format_tags_table(self, limit: int = 0) -> str:
        """
        格式化标签列表为表格
        
        Args:
            limit: 显示数量限制（0表示无限制）
            
        Returns:
            格式化字符串
        """
        tags = self.get_all_tags()
        
        if not tags:
            return "暂无标签数据。"
        
        if limit > 0:
            tags = tags[:limit]
        
        lines = []
        lines.append(REPORT_SEPARATOR)
        lines.append(f"{'排名':<6}{'标签':<30}{'出现次数':<10}")
        lines.append(REPORT_SEPARATOR)
        
        for i, (tag, count) in enumerate(tags, 1):
            # 截断过长标签名
            display_tag = tag[:28] + '..' if len(tag) > 30 else tag
            lines.append(f"{i:<6}{display_tag:<30}{count:<10}")
        
        lines.append(REPORT_SEPARATOR)
        lines.append(f"总计: {len(self._stats.tag_counts)} 个唯一标签")
        
        return '\n'.join(lines)
    
    def format_stats_summary(self) -> str:
        """
        格式化统计摘要
        
        Returns:
            格式化字符串
        """
        if self._stats is None:
            self.analyze()
        
        stats = self._stats
        lines = []
        
        lines.append(REPORT_SEPARATOR)
        lines.append("📊 笔记统计摘要")
        lines.append(REPORT_SEPARATOR)
        lines.append("")
        lines.append("【基础统计】")
        lines.append(f"  笔记总数:      {stats.total_notes} 篇")
        lines.append(f"  总行数:        {stats.total_lines} 行")
        lines.append(f"  总字符数:      {stats.total_chars} 字符")
        lines.append(f"  平均每篇行数:  {stats.avg_lines_per_note} 行")
        lines.append(f"  平均每篇字符:  {stats.avg_chars_per_note} 字符")
        lines.append("")
        lines.append("【标签统计】")
        lines.append(f"  唯一标签数:    {stats.total_tags} 个")
        lines.append(f"  标签总出现:    {sum(stats.tag_counts.values())} 次")
        lines.append("")
        lines.append("【双链统计】")
        lines.append(f"  唯一双链数:    {stats.total_wikilinks} 个")
        lines.append(f"  双链总出现:    {sum(stats.wikilink_counts.values())} 次")
        lines.append("")
        
        # 热门标签
        if stats.top_tags:
            lines.append("【热门标签 TOP 10】")
            for i, (tag, count) in enumerate(stats.top_tags[:10], 1):
                lines.append(f"  {i:2}. #{tag:<25} {count:>4} 次")
            lines.append("")
        
        # 热门双链
        top_wikilinks = self.get_top_wikilinks(10)
        if top_wikilinks:
            lines.append("【热门双链 TOP 10】")
            for i, (link, count) in enumerate(top_wikilinks, 1):
                display_link = link[:25] + '..' if len(link) > 27 else link
                lines.append(f"  {i:2}. [[{display_link}]]{ ' ' * max(0, 27-len(display_link))} {count:>4} 次")
            lines.append("")
        
        lines.append(REPORT_SEPARATOR)
        
        return '\n'.join(lines)
    
    def generate_full_report(self, filename: str = "full_report.txt") -> str:
        """
        生成完整统计报告并保存
        
        Args:
            filename: 报告文件名
            
        Returns:
            报告文件完整路径
        """
        if self._stats is None:
            self.analyze()
        
        lines = []
        
        # 报告头
        lines.append("=" * 70)
        lines.append(" " * 20 + "Markdown笔记完整统计报告")
        lines.append("=" * 70)
        lines.append(f"扫描目录: {self.source_dir}")
        lines.append(f"生成时间: {self._get_timestamp()}")
        lines.append("=" * 70)
        lines.append("")
        
        # 统计摘要
        lines.append(self.format_stats_summary())
        lines.append("")
        
        # 完整标签列表
        lines.append("=" * 70)
        lines.append(" " * 25 + "完整标签列表")
        lines.append("=" * 70)
        lines.append("")
        lines.append(self.format_tags_table(limit=0))
        lines.append("")
        
        # 完整双链列表
        if self._stats.wikilink_counts:
            lines.append("=" * 70)
            lines.append(" " * 25 + "完整双链列表")
            lines.append("=" * 70)
            lines.append("")
            wikilinks = sorted(
                self._stats.wikilink_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            lines.append(f"{'排名':<6}{'双链':<40}{'出现次数':<10}")
            lines.append(REPORT_SEPARATOR)
            for i, (link, count) in enumerate(wikilinks, 1):
                display_link = link[:38] + '..' if len(link) > 40 else link
                lines.append(f"{i:<6}[[{display_link}]]{' ' * max(0, 38-len(display_link))}{count:<10}")
            lines.append("")
        
        # 报告尾
        lines.append("=" * 70)
        lines.append(" " * 25 + "报告生成完成")
        lines.append("=" * 70)
        
        # 保存报告
        report_content = '\n'.join(lines)
        return self._save_report(filename, report_content)
    
    def _save_report(self, filename: str, content: str) -> str:
        """
        保存报告到输出目录
        
        Args:
            filename: 文件名
            content: 报告内容
            
        Returns:
            保存的文件路径
        """
        try:
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return filepath
        except Exception as e:
            raise IOError(f"保存报告失败: {e}")
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
