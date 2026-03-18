"""
utils/validators.py - 输入校验模块

提供各类输入验证功能：
- 关键词合法性校验
- 路径存在性校验
- 标签格式校验
- 文件名安全性校验

路径约束：
- 只读目录：./source_data/
- 只写目录：./output_build/

严禁修改 source_data/ 目录内任何文件！
"""

import os
import re
from typing import List

from utils.config import SOURCE_DIR, VALID_TAG_PATTERN


def validate_source_directory(path: str = SOURCE_DIR) -> bool:
    """
    验证源目录是否存在且可访问
    
    Args:
        path: 目录路径
        
    Returns:
        如果目录存在且可读返回True
    """
    try:
        return os.path.isdir(path) and os.access(path, os.R_OK)
    except Exception:
        return False


def validate_output_directory(path: str) -> bool:
    """
    验证输出目录是否可写
    
    Args:
        path: 目录路径
        
    Returns:
        如果目录存在或可创建且可写返回True
    """
    try:
        if os.path.exists(path):
            return os.path.isdir(path) and os.access(path, os.W_OK)
        # 尝试创建目录
        os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False


def validate_keywords(keywords: List[str]) -> bool:
    """
    验证关键词列表是否合法
    
    规则：
    - 不能为空列表
    - 每个关键词不能为空字符串
    - 不能包含控制字符
    
    Args:
        keywords: 关键词列表
        
    Returns:
        如果所有关键词合法返回True
    """
    if not keywords:
        return False
    
    for kw in keywords:
        if not isinstance(kw, str):
            return False
        if not kw.strip():
            return False
        # 检查控制字符
        if any(ord(c) < 32 for c in kw):
            return False
    
    return True


def validate_tag(tag: str) -> bool:
    """
    验证标签格式是否合法
    
    规则：
    - 不能为空
    - 只能包含字母、数字、下划线、连字符、斜杠
    - 不能以数字开头（可选规则）
    
    Args:
        tag: 标签名称（不含#号）
        
    Returns:
        如果标签格式合法返回True
    """
    if not isinstance(tag, str):
        return False
    
    tag = tag.strip()
    if not tag:
        return False
    
    # 使用正则验证
    if not re.match(VALID_TAG_PATTERN, tag):
        return False
    
    return True


def validate_filename(filename: str) -> bool:
    """
    验证文件名是否安全
    
    规则：
    - 不能为空
    - 不能包含路径分隔符
    - 不能包含特殊字符
    - 不能以.开头（隐藏文件）
    
    Args:
        filename: 文件名
        
    Returns:
        如果文件名安全返回True
    """
    if not isinstance(filename, str):
        return False
    
    if not filename.strip():
        return False
    
    # 检查路径分隔符
    if '/' in filename or '\\' in filename:
        return False
    
    # 检查非法字符
    invalid_chars = '<>:"|?*'
    if any(c in filename for c in invalid_chars):
        return False
    
    # 检查是否以.开头
    if filename.startswith('.'):
        return False
    
    return True


def sanitize_tag(tag: str) -> str:
    """
    清理标签字符串
    
    移除首尾空白，统一小写
    
    Args:
        tag: 原始标签
        
    Returns:
        清理后的标签
    """
    if not isinstance(tag, str):
        return ""
    
    # 移除首尾的#号
    tag = tag.strip().lstrip('#')
    return tag.lower()


def is_safe_path(filepath: str, base_dir: str) -> bool:
    """
    检查文件路径是否在安全目录内
    
    防止目录遍历攻击
    
    Args:
        filepath: 待检查路径
        base_dir: 基础安全目录
        
    Returns:
        如果路径安全返回True
    """
    try:
        # 获取绝对路径
        abs_filepath = os.path.abspath(filepath)
        abs_base = os.path.abspath(base_dir)
        
        # 检查是否为子目录
        return abs_filepath.startswith(abs_base)
    except Exception:
        return False


def validate_config_file(filepath: str) -> bool:
    """
    验证配置文件是否存在且可读
    
    特别用于 .do_not_touch.cfg 文件检查
    
    Args:
        filepath: 配置文件路径
        
    Returns:
        如果文件存在且可读返回True
    """
    try:
        return os.path.isfile(filepath) and os.access(filepath, os.R_OK)
    except Exception:
        return False
