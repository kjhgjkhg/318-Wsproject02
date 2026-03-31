"""
utils/config.py - 常量配置模块

定义源目录、输出目录、常见标签前缀、报告文件名模板等常量。
"""

import os
from typing import Final

BASE_DIR: Final[str] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCE_DATA_DIR: Final[str] = os.path.join(BASE_DIR, "source_data")

OUTPUT_BUILD_DIR: Final[str] = os.path.join(BASE_DIR, "output_build")

PROTECTED_FILE_NAME: Final[str] = ".do_not_touch.cfg"

SEARCH_REPORT_FILE: Final[str] = "search_report.txt"
STATS_REPORT_FILE: Final[str] = "stats_report.txt"

TAG_PATTERN: str = r"#[\w\u4e00-\u9fa5/-]+"

WIKI_LINK_PATTERN: str = r"\[\[[^\]]+\]\]"

MD_EXTENSION: Final[str] = ".md"

ENCODING: Final[str] = "utf-8"

TOP_TAGS_COUNT: Final[int] = 10
