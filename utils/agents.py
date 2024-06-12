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
from run import mc
from utils.colorful import ColorPrinter
#物体机械臂坐标
objects_coord={}
colorPrinter=ColorPrinter()

AGENT_SYS_PROMPT = '''
你是我的机械臂助手，机械臂内置了一些函数，请你根据我的指令，以json形式输出要运行的对应函数和你给我的回复

【以下是所有内置函数介绍】
机械臂位置归零，所有关节回到原点：back_zero()
放松机械臂，所有关节都可以自由手动拖拽活动：back_zero()
做出摇头动作：head_shake()
做出点头动作：head_nod()
做出跳舞动作：head_dance()
打开吸泵：pump_on()
关闭吸泵：pump_off()
移动到指定XY坐标，比如移动到X坐标150，Y坐标-120：move_to_coords(X=150, Y=-120)
指定关节旋转，比如关节1旋转到60度，总共有6个关节：single_joint_move(1, 60)
移动至俯视姿态：move_to_top_view()
拍一张俯视图：top_view_shot()
开启摄像头，在屏幕上实时显示摄像头拍摄的画面：check_camera()
LED灯改变颜色，比如：llm_led('帮我把LED灯的颜色改为贝加尔湖的颜色')
将一个物体移动到另一个物体的位置上，比如：vlm_move('帮我把红色方块放在小猪佩奇上')
拖动示教，我可以拽着机械臂运动，然后机械臂模仿复现出一样的动作：drag_teach()

【输出json格式】
你直接输出json即可，从{开始，不要输出包含```json的开头或结尾
在'function'键中，输出函数名列表，列表中每个元素都是字符串，代表要运行的函数名称和参数。每个函数既可以单独运行，也可以和其他函数先后运行。列表元素的先后顺序，表示执行函数的先后顺序
在'response'键中，根据我的指令和你编排的动作，以第一人称，输出你回复我的话，要简短一些，可以幽默和发散，用上歌词、台词、互联网热梗、名场面。比如李云龙的台词、甄嬛传的台词、练习时长两年半。

【以下是一些具体的例子】
我的指令：回到原点。你输出：{'function':['back_zero()'], 'response':'回家吧，回到最初的美好'}
我的指令：先回到原点，然后跳舞。你输出：{'function':['back_zero()', 'head_dance()'], 'response':'我的舞姿，练习时长两年半'}
我的指令：先回到原点，然后移动到180, -90坐标。你输出：{'function':['back_zero()', 'move_to_coords(X=180, Y=-90)'], 'response':'精准不，老子打的就是精锐'}
我的指令：先打开吸泵，再把关节2旋转到30度。你输出：{'function':['pump_on()', single_joint_move(2, 30)], 'response':'你之前做的指星笔，就是通过关节2调俯仰角'}
我的指令：移动到X为160，Y为-30的地方。你输出：{'function':['move_to_coords(X=160, Y=-30)'], 'response':'坐标移动已完成'}
我的指令：拍一张俯视图，然后把LED灯的颜色改为黄金的颜色。你输出：{'function':['top_view_shot()', llm_led('把LED灯的颜色改为黄金的颜色')], 'response':'人工智能未来比黄金值钱，你信不信'}
我的指令：帮我把绿色方块放在小猪佩奇上面。你输出：{'function':[vlm_move('帮我把绿色方块放在小猪佩奇上面')], 'response':'它的弟弟乔治呢？'}
我的指令：帮我把红色方块放在李云龙的脸上。你输出：{'function':[vlm_move('帮我把红色方块放在李云龙的脸上')], 'response':'你他娘的真是个天才'}
我的指令：关闭吸泵，打开摄像头。你输出：{'function':[pump_off(), check_camera()], 'response':'你是我的眼，带我阅读浩瀚的书海'}
我的指令：先归零，再把LED灯的颜色改为墨绿色。你输出：{'function':[back_zero(), llm_led('把LED灯的颜色改为墨绿色')], 'response':'这种墨绿色，很像蜀南竹海的竹子'}
我的指令：我拽着你运动，然后你模仿复现出这个运动。你输出：{'function':['drag_teach()'], 'response':'你有本事拽一个鸡你太美'}
我的指令：开启拖动示教。你输出：{'function':['drag_teach()'], 'response':'你要我模仿我自己？'}
我的指令：先回到原点，再打开吸泵，把LED灯的颜色改成中国红，最后把绿色方块移动到摩托车上。你输出：{'function':['back_zero()', 'pump_on()', llm_led('把LED灯的颜色改为中国红色', vlm_move('把绿色方块移动到摩托车上'))], 'response':'如果奇迹有颜色，那一定是中国红'}

【一些李云龙相关的台词，如果和李云龙相关，可以在response中提及对应的台词】
学习？学个屁
给你半斤地瓜烧
老子打的就是精锐
二营长，你的意大利炮呢
你他娘的真是个天才
咱老李也是十里八乡的俊后生
不报此仇，我李云龙誓不为人
你猜旅长怎么说
逢敌必亮剑，绝不含糊！
老子当初怎么教他打枪，现在就教他怎么打仗！
你咋就不敢跟旅长干一架呢？
你猪八戒戴眼镜充什么大学生啊？
我李云龙八岁习武，南拳北腿略知一二。
死，也要死在冲锋的路上！


【一些小猪佩奇相关的台词】
这是我的弟弟乔治

【我现在的指令是】
'''
TASK_TYPE="""
以下为所有任务类型及其解释：
[
    {
        "task_type": "control",
        "description":"机械臂控制"
    },
    {
        "task_type": "led",
        "description":"led灯控制"
    },
    {
        "task_type": "detection",
        "description":"目标检测，涉及到具体物体时要先其进行目标检测"
    },
]



"""
TASK_OUTPUT_FORMAT = """
返回内容包括：
task_id：任务序号
dependent_task_ids：该任务依赖的任物编号
instruction：该任务需要执行的指令
task_type：任务类型。
每项输出都应是严格意义上的任务列表，采用 json 格式，如下所示:

```json
[
    {
        "task_id": "1",
        "dependent_task_ids": [],
        "instruction": "回到原点",
        "task_type": "control"
    },
    ...
]
```

"""
TASK_SYS_PROMPT="""
你是我的机械臂任务编排助手，你需要根据User_Requirement,生成任务列表。要确保每一个物体都进行了目标检测,且都在一次detection任务中完成。
# User_Requirement
{user_requirement}

"""

def agent_task_plan(AGENT_PROMPT='先回到原点，再把LED灯改为墨绿色，然后把绿色方块放在篮球上'):
    print( colorPrinter.colorful("\n******Agent智能体编排任务******\n",'green'))
   
    PROMPT = TASK_SYS_PROMPT.format(user_requirement=AGENT_PROMPT) +TASK_TYPE+TASK_OUTPUT_FORMAT
    agent_plan = llm_zhipu(PROMPT)
    return agent_plan
 

CONTROL_SYS_PROMT="""
你是我的机械臂助手，机械臂内置了一些函数，请你根据User_Requirement的指令，以python代码输出要运行的对应函数。物体坐标必须是具体数值，且从Objects_coord中获取。Context是之前根据User_requirement生成的代码及其报错信息，Context如果不为空，请根据报错信息对代码进行修改，否则生成新的代码。
# User_Requirement
{user_requirement}
#Objects_coord
{objects_coord}
#Context
{context}
#Context end

【以下是所有内置函数介绍】
机械臂位置归零，所有关节回到原点：back_zero(mc)
放松机械臂，所有关节都可以自由手动拖拽活动：relax_arms(mc)
做出摇头动作：head_shake(mc)
做出点头动作：head_nod(mc)
打开夹爪：gripper_open(mc)
关闭夹爪：gripper_grip(mc)
移动到指定XY坐标，比如移动到X坐标150，Y坐标-120：move_to_coords(mc,X=150, Y=-120)
夹爪上升到搬运途中高度：grip_HEIGHT_SAFE(mc)
夹爪下降到夹取物体时高度：grip_END_SAFE(mc)
指定关节旋转，比如关节1旋转到60度，总共有6个关节：single_joint_move(mc,1, 60)
移动至俯视姿态：move_to_top_view(mc)
拍一张俯视图：top_view_shot(mc)
开启摄像头，在屏幕上实时显示摄像头拍摄的画面：check_camera()
拖动示教，我可以拽着机械臂运动，然后机械臂模仿复现出一样的动作：drag_teach(mc)
用夹抓，将物体从起点夹起移动至终点,mc：机械臂实例,XY_START：起点机械臂坐标,HEIGHT_START：起点高度,Y_END：终点机械臂坐标,HEIGHT_END：终点高度,HEIGHT_SAFE：搬运途中安全高度grip_move(mc, XY_START=[230,-50], HEIGHT_START=90, XY_END=[100,220], HEIGHT_END=100, HEIGHT_SAFE=220)
【这里是贴士】
0.一开始机械臂位置要归零
1.如果要夹取物体，要先打开夹爪
2.为了夹住物体要先下降到夹取物体时安全高度
3.为了夹住物体需要关闭夹爪
4.夹取物体后夹爪上升到搬运途中安全高度
5.放置完物体后要上升到搬运途中安全高度

每项输出都应是严格意义上的python代码，格式如下所示:

```python
back_zero(mc)
head_shake(mc)
```
"""



MYCOBOT_INIT_CODE="""
from pymycobot.mycobot import MyCobot
from utils.robot import *
mc = MyCobot('{port}',{baud})
"""
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
    print( colorPrinter.colorful("\n******control智能体执行动作******\n",'green'))
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
        port = config['DEFAULT']['MYCOBOT_PORT']
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

DETECTION_SYS_PROMPT = """
你是我的机械臂视觉助手,请你根据User_Requirement的指令,帮我从这句话中提取出所有物体,并从这张图中分别找到这些物体左上角和右下角的像素坐标,输出json数据结构。
# User_Requirement
{user_requirement}
"""
DETECTION_OUTPUT_FORMAT="""
返回内容包括：
name:物体名称,从User_Requirement中提取
top_left:左上角的像素二维坐标
right_bottom:右下角的像素二维坐标
每项输出都应是严格意义上的物体列表，采用 json 格式，如下所示:
```json
[
    {
        "name": "object1",
        "top_left": [x1, y1],
        "right_bottom": [x2, y2]
    },
    ...
]
```
"""
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
def detection_agent(detector,AGENT_PROMPT='进行目标检测确保小猪佩奇和摩托车被检测到'):
    print( colorPrinter.colorful("\n******detection智能体执行动作******\n",'green'))
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




def agent_maneger(detector,AGENT_PROMPT='先回到原点，再把LED灯改为小猪佩奇色，然后把小猪佩奇放在摩托车上'):
    print( colorPrinter.colorful("\n******Agent智能体启动******\n",'magenta'))
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
            print( colorPrinter.colorful(f"执行任务 {task.task_id}: {task.instruction}, 类型: CONTROL",'yellow'))
            control_agent(task.instruction)
        elif task.task_type == TaskType.LED:
            print( colorPrinter.colorful(f"执行任务 {task.task_id}: {task.instruction}, 类型: LED",'yellow'))
            llm_led(mc,task.instruction)
        elif task.task_type == TaskType.DETECTION:
            print( colorPrinter.colorful(f"执行任务 {task.task_id}: {task.instruction}, 类型: DETECTION",'yellow'))
            detection_agent(detector,task.instruction)
        else:
            print( colorPrinter.colorful(f"未知的任务类型 {task.task_id}: {task.instruction}",'red'))
            raise
    

    
