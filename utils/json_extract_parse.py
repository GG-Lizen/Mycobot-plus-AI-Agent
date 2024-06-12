"""
@Time    : 2024/6/5 17:25
@Author  : GG-Lizen
@File    : json_extract_parse.py
"""
import json
import re
def josn_extract(text):
    json_pattern = re.compile(r'```json\n(.*?)\n```', re.DOTALL)
    match = json_pattern.search(text)
    json_data:json
    if match:
        json_str = match.group(1)
        # 将提取的 JSON 字符串转换为 Python 对象
        try:
            json_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            # print(f"JSON解析错误: {e}")
            return None
    else:
        # print("未找到 JSON 内容")
        return None
    return json_data
def json_fix(text:str):
    text = "```json\n"+text+"\n```"
    jsondata=josn_extract(text)
    return jsondata

