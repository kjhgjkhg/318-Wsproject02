"""
utils/validators.py - 输入校验模块

提供关键词合法性校验、路径存在校验、标签格式校验等功能。
"""

import os
import re
from typing import List, Optional, Tuple

from utils.config import SOURCE_DATA_DIR, OUTPUT_BUILD_DIR, MD_EXTENSION


def validate_directory(path: str) -> Tuple[bool, Optional[str]]:
    """
    校验目录是否存在且可访问。

    Args:
        path: 目录路径

    Returns:
        (是否有效, 错误信息)
    """
    if not os.path.exists(path):
        return False, f"目录不存在: {path}"
    if not os.path.isdir(path):
        return False, f"路径不是目录: {path}"
    if not os.access(path, os.R_OK):
        return False, f"目录不可读: {path}"
    return True, None


def validate_source_directory() -> Tuple[bool, Optional[str]]:
    """
    校验源数据目录。

    Returns:
        (是否有效, 错误信息)
    """
    return validate_directory(SOURCE_DATA_DIR)


def validate_output_directory() -> Tuple[bool, Optional[str]]:
    """
    校验输出目录，不存在则尝试创建。

    Returns:
        (是否有效, 错误信息)
    """
    if not os.path.exists(OUTPUT_BUILD_DIR):
        try:
            os.makedirs(OUTPUT_BUILD_DIR, exist_ok=True)
            return True, None
        except OSError as e:
            return False, f"无法创建输出目录: {e}"
    if not os.path.isdir(OUTPUT_BUILD_DIR):
        return False, f"输出路径不是目录: {OUTPUT_BUILD_DIR}"
    if not os.access(OUTPUT_BUILD_DIR, os.W_OK):
        return False, f"输出目录不可写: {OUTPUT_BUILD_DIR}"
    return True, None


def validate_keyword(keyword: str) -> Tuple[bool, Optional[str]]:
    """
    校验搜索关键词是否合法。

    Args:
        keyword: 搜索关键词

    Returns:
        (是否有效, 错误信息)
    """
    if not keyword or not keyword.strip():
        return False, "关键词不能为空"
    if len(keyword) > 200:
        return False, "关键词长度不能超过200个字符"
    return True, None


def validate_keywords(keywords: List[str]) -> Tuple[bool, Optional[str]]:
    """
    校验多个关键词。

    Args:
        keywords: 关键词列表

    Returns:
        (是否有效, 错误信息)
    """
    if not keywords:
        return False, "关键词列表不能为空"
    for kw in keywords:
        is_valid, error = validate_keyword(kw)
        if not is_valid:
            return False, error
    return True, None


def validate_tag(tag: str) -> Tuple[bool, Optional[str]]:
    """
    校验标签格式是否合法。

    Args:
        tag: 标签字符串

    Returns:
        (是否有效, 错误信息)
    """
    if not tag:
        return False, "标签不能为空"
    pattern = r"^#[\w\u4e00-\u9fa5/-]+$"
    if not re.match(pattern, tag):
        return False, f"标签格式不正确: {tag}"
    return True, None


def validate_tag_filter(tag: str) -> Tuple[bool, Optional[str]]:
    """
    校验标签过滤参数（允许不带#前缀）。

    Args:
        tag: 标签或标签名

    Returns:
        (是否有效, 错误信息)
    """
    if not tag or not tag.strip():
        return False, "标签过滤参数不能为空"
    normalized = tag.strip()
    if not normalized.startswith("#"):
        normalized = "#" + normalized
    return validate_tag(normalized)


def is_markdown_file(filename: str) -> bool:
    """
    判断文件是否为 Markdown 文件。

    Args:
        filename: 文件名

    Returns:
        是否为 .md 文件
    """
    return filename.lower().endswith(MD_EXTENSION)


def normalize_tag(tag: str) -> str:
    """
    标准化标签格式。

    Args:
        tag: 原始标签

    Returns:
        标准化后的标签
    """
    tag = tag.strip()
    if not tag.startswith("#"):
        tag = "#" + tag
    return tag
