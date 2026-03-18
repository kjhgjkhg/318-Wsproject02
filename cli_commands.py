"""
cli_commands.py - 子命令具体实现

实现所有CLI子命令：
- search: 关键词搜索
- tags: 标签列表
- stats: 统计摘要
- list: 按标签列出笔记
- report: 生成完整报告

路径约束：
- 只读目录：./source_data/
- 只写目录：./output_build/

严禁修改 source_data/ 目录内任何文件！
"""

import os
import sys
from typing import List

from search_engine import SearchEngine
from stats_analyzer import StatsAnalyzer
from utils.validators import validate_keywords, validate_tag
from utils.config import OUTPUT_DIR, SEARCH_REPORT_FILENAME


def cmd_search(keywords: List[str], save_output: bool = False) -> int:
    """
    执行搜索命令
    
    Args:
        keywords: 搜索关键词列表
        save_output: 是否保存结果到文件
        
    Returns:
        退出码：0成功，1失败
    """
    # 验证关键词
    if not validate_keywords(keywords):
        print("错误: 关键词不能为空或包含非法字符", file=sys.stderr)
        return 1
    
    print(f"正在搜索: {' + '.join(keywords)}")
    print("-" * 50)
    
    try:
        engine = SearchEngine()
        results = engine.search(keywords)
        
        if not results:
            print("未找到匹配的笔记。")
            return 0
        
        print(f"找到 {len(results)} 篇匹配的笔记:\n")
        
        # 显示结果
        for i, result in enumerate(results, 1):
            print(f"[{i}/{len(results)}]")
            print(engine.format_search_result(result))
        
        # 保存报告
        if save_output:
            report = engine.generate_search_report(keywords, results)
            filepath = _save_to_output(SEARCH_REPORT_FILENAME, report)
            print(f"\n搜索报告已保存: {filepath}")
        
        return 0
        
    except Exception as e:
        print(f"搜索失败: {e}", file=sys.stderr)
        return 1


def cmd_tags(limit: int = 0) -> int:
    """
    执行标签列表命令
    
    Args:
        limit: 显示数量限制
        
    Returns:
        退出码：0成功，1失败
    """
    print("正在分析标签...")
    print("-" * 50)
    
    try:
        analyzer = StatsAnalyzer()
        tags = analyzer.get_all_tags(sort_by_count=True)
        
        if not tags:
            print("未发现任何标签。")
            print("提示: 标签格式为 #tag 或 #tag/subtag")
            return 0
        
        if limit > 0:
            tags = tags[:limit]
            print(f"显示前 {limit} 个标签（共 {len(analyzer._stats.tag_counts)} 个）:\n")
        else:
            print(f"共发现 {len(tags)} 个标签:\n")
        
        # 打印标签表格
        print(f"{'排名':<6}{'标签':<30}{'出现次数':<10}")
        print("-" * 50)
        
        for i, (tag, count) in enumerate(tags, 1):
            display_tag = tag[:28] + '..' if len(tag) > 30 else tag
            print(f"{i:<6}#{display_tag:<29}{count:<10}")
        
        print("-" * 50)
        print(f"总计: {len(analyzer._stats.tag_counts)} 个唯一标签")
        
        return 0
        
    except Exception as e:
        print(f"标签分析失败: {e}", file=sys.stderr)
        return 1


def cmd_stats() -> int:
    """
    执行统计命令
    
    Returns:
        退出码：0成功，1失败
    """
    print("正在生成统计信息...")
    print("-" * 50)
    
    try:
        analyzer = StatsAnalyzer()
        stats = analyzer.analyze()
        
        if stats.total_notes == 0:
            print("未发现任何Markdown笔记。")
            print(f"提示: 请将.md文件放入 {analyzer.source_dir} 目录")
            return 0
        
        # 打印统计摘要
        print(analyzer.format_stats_summary())
        
        return 0
        
    except Exception as e:
        print(f"统计失败: {e}", file=sys.stderr)
        return 1


def cmd_list(tag: str) -> int:
    """
    执行列出笔记命令（按标签筛选）
    
    Args:
        tag: 标签名称（不含#号）
        
    Returns:
        退出码：0成功，1失败
    """
    # 验证标签
    if not validate_tag(tag):
        print("错误: 标签格式无效", file=sys.stderr)
        return 1
    
    print(f"正在查找标签: #{tag}")
    print("-" * 50)
    
    try:
        engine = SearchEngine()
        notes = engine.search_by_tag(tag)
        
        if not notes:
            print(f"未找到包含标签 #{tag} 的笔记。")
            return 0
        
        print(f"找到 {len(notes)} 篇包含 #{tag} 标签的笔记:\n")
        
        for i, note in enumerate(notes, 1):
            print(f"{i}. {note.filename}")
            print(f"   路径: {note.filepath}")
            print(f"   行数: {note.line_count} | 标签: {', '.join(sorted(note.tags)) or '无'}")
            print()
        
        return 0
        
    except Exception as e:
        print(f"查询失败: {e}", file=sys.stderr)
        return 1


def cmd_report(filename: str = "full_report.txt") -> int:
    """
    执行生成报告命令
    
    Args:
        filename: 报告文件名
        
    Returns:
        退出码：0成功，1失败
    """
    print("正在生成完整统计报告...")
    print("-" * 50)
    
    try:
        analyzer = StatsAnalyzer()
        
        # 检查是否有笔记
        stats = analyzer.analyze()
        if stats.total_notes == 0:
            print("未发现任何Markdown笔记，无法生成报告。")
            print(f"提示: 请将.md文件放入 {analyzer.source_dir} 目录")
            return 0
        
        # 生成报告
        filepath = analyzer.generate_full_report(filename)
        
        print(f"✓ 报告生成成功!")
        print(f"  文件路径: {filepath}")
        print(f"  笔记数量: {stats.total_notes} 篇")
        print(f"  标签数量: {stats.total_tags} 个")
        print(f"  双链数量: {stats.total_wikilinks} 个")
        
        return 0
        
    except Exception as e:
        print(f"报告生成失败: {e}", file=sys.stderr)
        return 1


def _save_to_output(filename: str, content: str) -> str:
    """
    保存内容到输出目录
    
    Args:
        filename: 文件名
        content: 文件内容
        
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
        raise IOError(f"保存文件失败: {e}")
