"""
@Time    : 2024/6/5 17:25
@Author  : GG-Lizen
@File    : llm.py
"""
from zhipuai import ZhipuAI
import configparser

# 创建一个 ConfigParser 对象
config = configparser.ConfigParser()

# 读取配置文件
config.read('config.ini')
zhipu_api = config['DEFAULT']['ZHIPU_API']

def llm_zhipu(PROMPT='你好，你是谁？'):
    '''
    智谱大模型API
    '''
    
    client = ZhipuAI(api_key=zhipu_api) # 填写您自己的APIKey
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[
            {"role": "user", "content": PROMPT}
        ],
    )
    result = response.choices[0].message.content.strip()
    return result
    