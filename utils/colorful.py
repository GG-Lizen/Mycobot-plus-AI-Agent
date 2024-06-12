#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/11/22
@Author  : GG-Lizen
@File    : colorful.py
@Desc:     colorful the output of cmd
"""
class ColorPrinter:
    """用于在命令行输出带指定颜色的文本的类"""

    # ANSI 转义码映射
    COLORS = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'magenta': '\033[95m',
        'purple' : '\033[95m'
    }
    
    RESET = '\033[0m'  # 重置样式

    def __init__(self):
        pass

    def colorful(self, text, color):
        """
        Outputs text with the specified color to the command line

        args:
        text (str): Text string to be output
        color (str): Color name, can be 'red', 'green', 'yellow', 'blue', 'cyan', 'magenta', 'purple'

        return: str
        """
        # 检查输入的颜色是否有效
        if color not in self.COLORS:
            return text

        # 打印带指定颜色的文本
        return f"{self.COLORS[color]}{text}{self.RESET}"