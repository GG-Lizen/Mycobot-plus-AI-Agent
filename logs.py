# -*- coding: utf-8 -*-
"""
@Time    : 2023/6/1 12:41
@Author  : alexanderwu
@File    : logs.py
@Modify  : GG-Lizen
"""

import sys
import os

from datetime import datetime

from loguru import logger as _logger


_print_level = "INFO"
current_working_directory = os.getcwd()

def define_log_level(print_level="INFO", logfile_level="DEBUG", name: str = None):
    """Adjust the log level to above level"""
    global _print_level
    _print_level = print_level

    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d")
    log_name = f"{name}_{formatted_date}" if name else formatted_date  # name a log with prefix name

    _logger.remove()
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm}</green> | "  # Simplified time format
        "<level>{level: <8}</level> | "  # Custom level format with fixed width
        "{file}:{line} | "  # Add file and line number
        "{message}"  # Log message
    )
    _logger.add(sys.stderr, level=print_level, format=log_format)
    _logger.add(current_working_directory +'/'+ f"logs/{log_name}.txt", level=logfile_level)
    return _logger


logger = define_log_level()


def log_llm_stream(msg):
    _llm_stream_log(msg)


def set_llm_stream_logfunc(func):
    global _llm_stream_log
    _llm_stream_log = func


def _llm_stream_log(msg):
    if _print_level in ["INFO"]:
        print(msg, end="")
