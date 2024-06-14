"""
@Time    : 2024/6/5 17:25
@Author  : GG-Lizen
@File    : agents.py
"""
# Agent智能体相关函数

from utils.llm import *
import re
import json
import subprocess
import configparser
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
from task_type import Task,topological_sort,TaskType
from utils.robot import *
from utils.vlm import *
from utils.led import *
from utils.colorful import ColorPrinter
from prompt import *
#物体机械臂坐标
objects_coord={}



def agent_task_plan(AGENT_PROMPT='先回到原点，再把LED灯改为墨绿色，然后把绿色方块放在篮球上'):
    print( ColorPrinter.colorful("\n******Agent智能体编排任务******\n",'green'))
   
    PROMPT = TASK_SYS_PROMPT.format(user_requirement=AGENT_PROMPT) +TASK_TYPE+TASK_OUTPUT_FORMAT
    agent_plan = llm_zhipu(PROMPT)
    return agent_plan
 
def exec_code(code_text):
    # 使用 Pygments 进行语法高亮和行号显示
    formatter = TerminalFormatter(linenos=True)
    highlighted_code = highlight(code_text, PythonLexer(), formatter)
    print(highlighted_code)
    result = subprocess.run(["python", "-c", code_text], capture_output=True, text=True)
    code_result = result.stdout
    code_err= result.stderr
    if len(code_err)>0:
        return False,code_err
    else:
        return True,code_result

def control_agent(AGENT_PROMPT='把小猪佩奇放在摩托车上'):
    print( ColorPrinter.colorful("\n******control智能体执行动作******\n",'green'))
    request_num = 3
    PROMPT = CONTROL_SYS_PROMT.format(user_requirement=AGENT_PROMPT,objects_coord=json.dumps(objects_coord),context = '')
    while request_num >0:

        request_num+=1
        res = llm_zhipu(PROMPT)
        pattern = r"```python\s*([^`]+)```"
        match = re.search(pattern, res, re.DOTALL)
        if match:
            code_to_excute= match.group(1).strip()
        else:
            return None
        
        config = configparser.ConfigParser()
        config.read('config.ini')
        # 访问 DEFAULT 部分的配置
        video_path = config['DEFAULT']['DEV_VIDEO']
        port = get_robot_port()
        baud = config['DEFAULT']['MYCOBOT_BAUD']
        code_text = MYCOBOT_INIT_CODE.format(port=port,baud=baud) +code_to_excute
        ret,result=exec_code(code_text)
        # print(result)
        if ret:
            break
        else:
            print(result)
            PROMPT = CONTROL_SYS_PROMT.format(user_requirement=AGENT_PROMPT,objects_coord=json.dumps(objects_coord),context = code_text + "\n"+result)

    return code_to_excute


def detect_result_valid(data):
    if not isinstance(data, list):
        return False
    for item in data:
        if not isinstance(item, dict):
            return False
        
        if "name" not in item or "top_left" not in item or "right_bottom" not in item:
            return False
        
        if not isinstance(item["name"], str):
            return False
        
        if not (isinstance(item["top_left"], list) and len(item["top_left"]) == 2):
            return False
        
        if not (isinstance(item["right_bottom"], list) and len(item["right_bottom"]) == 2):
            return False
        
        x1, y1 = item["top_left"]
        x2, y2 = item["right_bottom"]
        
        if not (isinstance(x1, (int, float)) and isinstance(y1, (int, float))):
            return False
        
        if not (isinstance(x2, (int, float)) and isinstance(y2, (int, float))):
            return False
    
    return True
def detection_agent(mc,detector,AGENT_PROMPT='进行目标检测确保小猪佩奇和摩托车被检测到'):
    print( ColorPrinter.colorful("\n******detection智能体执行动作******\n",'green'))
    print('拍摄俯视图')
    top_view_shot(mc,detector,check=False)
    
    ## 第四步：将图片输入给多模态视觉大模型
    print('将图片输入给多模态视觉大模型')
    PROMPT = DETECTION_SYS_PROMPT.format(user_requirement=AGENT_PROMPT)+DETECTION_OUTPUT_FORMAT
    n = 1
    while n < 5:
        try:
            print('    尝试第 {} 次访问多模态大模型'.format(n))
            result = yi_vision_api(PROMPT, img_path='temp/vl_now.jpg')
            print('    多模态大模型调用成功！')
            
        except Exception as e:
            print( e)
            n += 1
        if result is None:
            print('    多模态大模型返回数据结构错误，再尝试一次')
            n += 1
            continue
        else:
            if not detect_result_valid(result):
                print("格式错误")
                n += 1
                if n==5:
                    raise RuntimeError('目标检测失败')
                continue
            break
    
    for item in result:
        item['top_left'] = tuple(item['top_left'])
        item['right_bottom'] = tuple(item['right_bottom'])
    result = post_processing_viz(detector,result,'temp/vl_now.jpg')
   
    for item in result:
        # print(item)
        # print(item['center'])
        # print(item['center'][0])
        objects_coord[item['name']]=detector.eye2hand(item['center'][0],item['center'][1])
        print(objects_coord)
    # print(result)
    # print(objects_coord)




def agent_maneger(mc,detector,AGENT_PROMPT='先回到原点，再把LED灯改为小猪佩奇色，然后把小猪佩奇放在摩托车上'):
    print( ColorPrinter.colorful("\n******Agent智能体启动******\n",'magenta'))
    task_plan = agent_task_plan(AGENT_PROMPT)
    json_pattern = re.compile(r'```json\n(.*?)\n```', re.DOTALL)
    match = json_pattern.search(task_plan)
    json_data:json
    if match:
        json_str = match.group(1)
        # 将提取的 JSON 字符串转换为 Python 对象
        try:
            json_data = json.loads(json_str)
            print('解析成功！llm生成任务如下：')
            print(json.dumps(json_data, indent=4, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print("llm输出如下：\n"+task_plan+"\n请确保llm输出格式正确！")
            return False
    else:
        print("未找到 JSON 内容")
        return False
    # 转换为任务对象
    tasks = [Task(**task) for task in json_data]

    # 执行任务
    sorted_task_ids = topological_sort(tasks)
    id_to_task = {task.task_id: task for task in tasks}
    for task_id in sorted_task_ids:
        task = id_to_task[task_id]
        if not task.is_valid_task_type():
            raise ValueError(f"Invalid task type for task {task_id}: {task.task_type}")
        
        # 执行任务，根据任务类型进行处理
        if task.task_type == TaskType.CONTROL:
            print( ColorPrinter.colorful(f"执行任务 {task.task_id}: {task.instruction}, 类型: CONTROL",'yellow'))
            control_agent(task.instruction)
        elif task.task_type == TaskType.LED:
            print( ColorPrinter.colorful(f"执行任务 {task.task_id}: {task.instruction}, 类型: LED",'yellow'))
            llm_led(mc,task.instruction)
        elif task.task_type == TaskType.DETECTION:
            print( ColorPrinter.colorful(f"执行任务 {task.task_id}: {task.instruction}, 类型: DETECTION",'yellow'))
            detection_agent(mc,detector,task.instruction)
        else:
            print( ColorPrinter.colorful(f"未知的任务类型 {task.task_id}: {task.instruction}",'red'))
            raise
    

    
