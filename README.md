# Mycobot Plus AI Agent

基于[同济子豪兄大象机械臂Mycobot 280 Pi教程](https://github.com/TommyZihao/Mycobot_Tutorials.git) 项目开发。

作为机械臂以及ROS零基础的小白，这个项目无疑是具有难度，不过最终还是成功运行，并修改和加入了一些东西。希望该项目对你有帮助！

不同点：

- 使用夹爪而非吸泵
  - 若要使用吸泵请在utils.robot中编写吸泵打开和关闭函数，并添加到CONTROL_SYS_PROMT中，同时修改夹爪为吸泵

- 没有连接树梅派
- 添加标定助手:`calibration_assist.py`，辅助手眼标定
- 修改agent，目前共有三类agent:
  - 大脑
    - agent_maneger：管理组织其他代理行为
  - 感知
    - detection_agent：识别目标的位置
  - 行动         
    - control_agent：生成控制代码，并运行，实现机械臂控制
    - llm_led：根据提示改变机械臂led灯颜色
- 将重要参数写入配置文件中，方便修改
- yolo分支采用yolov8进行目标检测

## Get Started

系统：ubuntu20.04.1

机械臂: Mycobot 280 m5

### Installation

```
conda create -n mycobot python=3.11 && conda activate mycobot
```

> 最好不要折腾系统的python，关于conda的安装见tips.md

```
pip install -r requirements.txt
```

> PyAudio 可能无法安装成功，执行以下命令：
>
> ```
> sudo apt-get install python-all-dev 
> sudo apt-get install portaudio19-dev
> ```
>
> 然后再
>
> ```
> pip install pyaudio
> ```

### Configuration

#### [DEFAULT]

把`config.ini.template`修改为`config.ini`，并在`YOUR_API_TOKEN`，填入你的API_TOKEN，`dev_video`填入机械臂摄像头设备号，`MYCOBOT_BAUD`一般不需要修改。

```
#查看机械臂摄像头设备号
ls /dev/video*
#查看机械臂端口号
ls /dev/ttyACM*
#or
ls /dev/ttyUSB*
```

> windows要安装驱动参考：https://docs.elephantrobotics.com/docs/mycobot-m5-cn/4-BasicApplication/4.1-myStudio/4.1.1-myStudio_download_driverinstalled.html

修改机械臂端口权限

```
sudo chmod a+rw /dev/ttyACM0 #改成你的设备号
```

#### [Carlibration]

不需要修改

#### [MYCOBOT]

**这一部分要通过实际调试后写入**

`top_view_angles`，是机械臂俯身拍摄时机械臂的角度;`HEIGHT_END` 是机械臂下降到抓取位置的高度 ;`HEIGHT_SAFE`是机械臂上升到搬运位置的高度;`COORDS_R`是移动到指定坐标时的rx,ry,rz值

```
mc.send_angles([0, 0, 0, 0, 0, 0], 40)#机械臂归零
mc.release_all_servos()#释放所有关节
mc.release_servo(1)#释放关节1
mc.get_angles()#获取角度
mc.get_coords()#获取当前机械臂末端的x,y,z,rx,ry,rz,其中z就是高度
```

### Usage

打印彩纸，确保左下角aruco码为6x6，id2，左上角为6x6,id1，同时两aruco必须都出现在画面中，否则会识别不成功。参考或直接使用asset下的彩纸打印。

> aruco码生成网站：https://chev.me/arucogen/

面对机械臂屏幕方向为x轴，彩纸按方向放好。运行程序：

```
python run.py
```

> 出现title为can't find aruco的画面是因为找不到aruco码，或aruco码没按规则摆放

其中标定点1为左下角aruco码，标定点为右上角aruco码

![image-20240612204145922](README.assets/image-20240612204145922.png)

> 标定时确保机械底座位置不能改变，释放机械臂时记得扶好机械臂
>
> 完成一次标定后，只要机械臂彩纸位置不变可不用再标定

> 由于我的机械臂第四关节常常有无法保持的情况，导致在目标检测，拍摄俯视图时会有拍摄不到彩纸的情况，因此每次拍摄都强制检测两端的aruco码是否存在。

### example

yolo分支，使用默认命令，且已完成一次标定

命令行输出：

```
$ python run.py 
ls: cannot access '/dev/ttyUSB*': No such file or directory
2024-06-26 18:35 | WARNING  | robot.py:34 | No device found for pattern /dev/ttyUSB*: Command 'ls /dev/ttyUSB*' returned non-zero exit status 2.
2024-06-26 18:35 | SUCCESS  | robot.py:46 | find device : /dev/ttyACM0
2024-06-26 18:35 | INFO     | robot.py:56 | 机械臂归零
2024-06-26 18:35 | INFO     | robot.py:103 | 移动至俯视姿态
是否进行机械臂标定，输入'n'取消:n
2024-06-26 18:35 | INFO     | calibration_assist.py:112 | 将从配置文件中读取机械臂标定点，请确保点位正确
2024-06-26 18:35 | SUCCESS  | calibration_assist.py:132 | 标定完成
是否开启录音，按r开始录制，按k打字输入，按c输入默认指令:c
2024-06-26 18:35 | INFO     | agents.py:112 | 
******Agent智能体启动******

2024-06-26 18:35 | INFO     | agents.py:31 | 
******Agent智能体编排任务******

2024-06-26 18:35 | INFO     | agents.py:122 | llm生成任务如下：
[
    {
        "task_id": "1",
        "dependent_task_ids": [],
        "instruction": "定位到包装盒",
        "task_type": "detection"
    },
    {
        "task_id": "2",
        "dependent_task_ids": [
            "1"
        ],
        "instruction": "抓取包装盒",
        "task_type": "control"
    },
    {
        "task_id": "3",
        "dependent_task_ids": [
            "2"
        ],
        "instruction": "移动到摩托车位置",
        "task_type": "control"
    },
    {
        "task_id": "4",
        "dependent_task_ids": [
            "3"
        ],
        "instruction": "放置包装盒到摩托车上",
        "task_type": "control"
    },
    {
        "task_id": "5",
        "dependent_task_ids": [
            "4"
        ],
        "instruction": "定位到小猪佩奇",
        "task_type": "detection"
    },
    {
        "task_id": "6",
        "dependent_task_ids": [
            "5"
        ],
        "instruction": "移动到小猪佩奇位置",
        "task_type": "control"
    },
    {
        "task_id": "7",
        "dependent_task_ids": [
            "6"
        ],
        "instruction": "放置包装盒到小猪佩奇上",
        "task_type": "control"
    }
]
2024-06-26 18:35 | INFO     | agents.py:150 | 执行任务 1: 定位到包装盒, 类型: DETECTION
2024-06-26 18:35 | INFO     | agents.py:96 | 
******detection智能体执行动作******

2024-06-26 18:35 | INFO     | robot.py:56 | 机械臂归零
2024-06-26 18:35 | INFO     | robot.py:103 | 移动至俯视姿态
2024-06-26 18:35 | SUCCESS  | robot.py:152 | 俯拍图像保存至temp/vl_now.jpg
2024-06-26 18:35 | INFO     | agents.py:100 | 目标检测

image 1/1 /home/lizen/Task/Mycobot Plus AI Agent/temp/vl_now.jpg: 448x640 1 basketball, 1 motor, 1 pig, 1 box, 9.7ms
Speed: 1.8ms preprocess, 9.7ms inference, 1.0ms postprocess per image at shape (1, 3, 448, 640)
{'basketball': (-67, -116), 'box': (58, -140), 'motor': (105, -193), 'pig': (3, -189)}
2024-06-26 18:35 | INFO     | agents.py:144 | 执行任务 2: 抓取包装盒, 类型: CONTROL
2024-06-26 18:35 | INFO     | agents.py:60 | 
******control智能体执行动作******

ls: cannot access '/dev/ttyUSB*': No such file or directory
2024-06-26 18:35 | WARNING  | robot.py:34 | No device found for pattern /dev/ttyUSB*: Command 'ls /dev/ttyUSB*' returned non-zero exit status 2.
2024-06-26 18:35 | SUCCESS  | robot.py:46 | find device : /dev/ttyACM0
2024-06-26 18:35 | INFO     | agents.py:40 | 
0001: from pymycobot.mycobot import MyCobot
0002: from utils.robot import *
0003: mc = MyCobot('/dev/ttyACM0',115200)
0004: # 首先让机械臂回到原点
0005: back_zero(mc)
0006: 
0007: # 移动到包装盒的坐标位置
0008: move_to_coords(mc, X=58, Y=-140)
0009: 
0010: # 打开夹爪，准备夹取物体
0011: gripper_open(mc)
0012: 
0013: # 下降到夹取物体的安全高度
0014: grip_END_SAFE(mc)
0015: 
0016: # 关闭夹爪，夹取物体
0017: gripper_grip(mc)
0018: 
0019: # 夹取物体后，夹爪上升到搬运途中的安全高度
0020: grip_HEIGHT_SAFE(mc)
0021: 

2024-06-26 18:36 | INFO     | agents.py:144 | 执行任务 3: 移动到摩托车位置, 类型: CONTROL
2024-06-26 18:36 | INFO     | agents.py:60 | 
******control智能体执行动作******

ls: cannot access '/dev/ttyUSB*': No such file or directory
2024-06-26 18:36 | WARNING  | robot.py:34 | No device found for pattern /dev/ttyUSB*: Command 'ls /dev/ttyUSB*' returned non-zero exit status 2.
2024-06-26 18:36 | SUCCESS  | robot.py:46 | find device : /dev/ttyACM0
2024-06-26 18:36 | INFO     | agents.py:40 | 
0001: from pymycobot.mycobot import MyCobot
0002: from utils.robot import *
0003: mc = MyCobot('/dev/ttyACM0',115200)
0004: # 首先，让机械臂回到原点（如果 Excuted_code 或 Context 中没有这一步的话）
0005: back_zero(mc)
0006: 
0007: # 移动到摩托车的坐标位置
0008: move_to_coords(mc, X=105, Y=-193)
0009: 
0010: # 根据贴士，如果接下来要夹取物体，需要执行以下步骤：
0011: gripper_open(mc)  # 打开夹爪
0012: grip_END_SAFE(mc)  # 下降到夹取物体的安全高度
0013: gripper_grip(mc)  # 关闭夹爪，夹取物体
0014: grip_HEIGHT_SAFE(mc)  # 夹取物体后，夹爪上升到搬运途中的安全高度
0015: 

2024-06-26 18:36 | INFO     | agents.py:144 | 执行任务 4: 放置包装盒到摩托车上, 类型: CONTROL
2024-06-26 18:36 | INFO     | agents.py:60 | 
******control智能体执行动作******

ls: cannot access '/dev/ttyUSB*': No such file or directory
2024-06-26 18:36 | WARNING  | robot.py:34 | No device found for pattern /dev/ttyUSB*: Command 'ls /dev/ttyUSB*' returned non-zero exit status 2.
2024-06-26 18:36 | SUCCESS  | robot.py:46 | find device : /dev/ttyACM0
2024-06-26 18:36 | INFO     | agents.py:40 | 
0001: from pymycobot.mycobot import MyCobot
0002: from utils.robot import *
0003: mc = MyCobot('/dev/ttyACM0',115200)
0004: # 假定已经执行了Excuted_code中的内容
0005: 
0006: # 移动到盒子的坐标位置
0007: move_to_coords(mc, X=58, Y=-140)
0008: 
0009: # 打开夹爪
0010: gripper_open(mc)
0011: 
0012: # 下降到夹取物体的安全高度
0013: grip_END_SAFE(mc)
0014: 
0015: # 关闭夹爪，夹取物体
0016: gripper_grip(mc)
0017: 
0018: # 夹取物体后，夹爪上升到搬运途中的安全高度
0019: grip_HEIGHT_SAFE(mc)
0020: 
0021: # 移动到摩托车的坐标位置
0022: move_to_coords(mc, X=105, Y=-193)
0023: 
0024: # 下降到放置物体的安全高度
0025: grip_END_SAFE(mc)
0026: 
0027: # 打开夹爪，放置物体
0028: gripper_open(mc)
0029: 
0030: # 夹爪上升到搬运途中的安全高度
0031: grip_HEIGHT_SAFE(mc)
0032: 

2024-06-26 18:37 | INFO     | agents.py:150 | 执行任务 5: 定位到小猪佩奇, 类型: DETECTION
2024-06-26 18:37 | INFO     | agents.py:96 | 
******detection智能体执行动作******

2024-06-26 18:37 | INFO     | robot.py:56 | 机械臂归零
2024-06-26 18:37 | INFO     | robot.py:103 | 移动至俯视姿态
2024-06-26 18:37 | SUCCESS  | robot.py:152 | 俯拍图像保存至temp/vl_now.jpg
2024-06-26 18:37 | INFO     | agents.py:100 | 目标检测

image 1/1 /home/lizen/Task/Mycobot Plus AI Agent/temp/vl_now.jpg: 448x640 1 basketball, 1 pig, 1 box, 6.7ms
Speed: 2.2ms preprocess, 6.7ms inference, 0.9ms postprocess per image at shape (1, 3, 448, 640)
{'basketball': (-63, -116), 'box': (106, -178), 'motor': (105, -193), 'pig': (10, -186)}
2024-06-26 18:37 | INFO     | agents.py:144 | 执行任务 6: 移动到小猪佩奇位置, 类型: CONTROL
2024-06-26 18:37 | INFO     | agents.py:60 | 
******control智能体执行动作******

ls: cannot access '/dev/ttyUSB*': No such file or directory
2024-06-26 18:37 | WARNING  | robot.py:34 | No device found for pattern /dev/ttyUSB*: Command 'ls /dev/ttyUSB*' returned non-zero exit status 2.
2024-06-26 18:37 | SUCCESS  | robot.py:46 | find device : /dev/ttyACM0
2024-06-26 18:37 | INFO     | agents.py:40 | 
0001: from pymycobot.mycobot import MyCobot
0002: from utils.robot import *
0003: mc = MyCobot('/dev/ttyACM0',115200)
0004: move_to_coords(mc, X=10, Y=-186)
0005: 

2024-06-26 18:37 | INFO     | agents.py:144 | 执行任务 7: 放置包装盒到小猪佩奇上, 类型: CONTROL
2024-06-26 18:37 | INFO     | agents.py:60 | 
******control智能体执行动作******

ls: cannot access '/dev/ttyUSB*': No such file or directory
2024-06-26 18:37 | WARNING  | robot.py:34 | No device found for pattern /dev/ttyUSB*: Command 'ls /dev/ttyUSB*' returned non-zero exit status 2.
2024-06-26 18:37 | SUCCESS  | robot.py:46 | find device : /dev/ttyACM0
2024-06-26 18:37 | INFO     | agents.py:40 | 
0001: from pymycobot.mycobot import MyCobot
0002: from utils.robot import *
0003: mc = MyCobot('/dev/ttyACM0',115200)
0004: from pymycobot.mycobot import MyCobot
0005: from utils.robot import *
0006: 
0007: # 初始化机械臂
0008: mc = MyCobot('/dev/ttyACM0',115200)
0009: 
0010: # 位置归零（如果 Excuted_code 中没有显示调用过该函数）
0011: back_zero(mc)
0012: 
0013: # 移动到包装盒位置
0014: move_to_coords(mc, X=106, Y=-178)
0015: 
0016: # 打开夹爪
0017: gripper_open(mc)
0018: 
0019: # 下降到夹取物体的安全高度
0020: grip_END_SAFE(mc)
0021: 
0022: # 关闭夹爪，夹住物体
0023: gripper_grip(mc)
0024: 
0025: # 上升到搬运途中的安全高度
0026: grip_HEIGHT_SAFE(mc)
0027: 
0028: # 移动到小猪佩奇的位置
0029: move_to_coords(mc, X=10, Y=-186)
0030: 
0031: # 下降到放置物体的安全高度
0032: grip_END_SAFE(mc)
0033: 
0034: # 打开夹爪，放置物体
0035: gripper_open(mc)
0036: 
0037: # 上升到搬运途中的安全高度
0038: grip_HEIGHT_SAFE(mc)
0039: 

2024-06-26 18:38 | SUCCESS  | run.py:39 | 执行完成
(yolo) lizen@Y7000:Mycobot Plus AI Agent$ python run.py 
ls: cannot access '/dev/ttyUSB*': No such file or directory
2024-06-26 18:46 | WARNING  | robot.py:34 | No device found for pattern /dev/ttyUSB*: Command 'ls /dev/ttyUSB*' returned non-zero exit status 2.
2024-06-26 18:46 | SUCCESS  | robot.py:46 | find device : /dev/ttyACM0
2024-06-26 18:46 | INFO     | robot.py:56 | 机械臂归零
2024-06-26 18:46 | INFO     | robot.py:103 | 移动至俯视姿态
是否进行机械臂标定，输入'n'取消:n
2024-06-26 18:46 | INFO     | calibration_assist.py:112 | 将从配置文件中读取机械臂标定点，请确保点位正确
2024-06-26 18:46 | SUCCESS  | calibration_assist.py:132 | 标定完成
是否开启录音，按r开始录制，按k打字输入，按c输入默认指令:c
2024-06-26 18:46 | INFO     | agents.py:112 | 
******Agent智能体启动******

2024-06-26 18:46 | INFO     | agents.py:31 | 
******Agent智能体编排任务******

2024-06-26 18:46 | INFO     | agents.py:122 | llm生成任务如下：
[
    {
        "task_id": "1",
        "dependent_task_ids": [],
        "instruction": "定位并检测到包装盒",
        "task_type": "detection"
    },
    {
        "task_id": "2",
        "dependent_task_ids": [
            "1"
        ],
        "instruction": "将包装盒放到摩托车上",
        "task_type": "control"
    },
    {
        "task_id": "3",
        "dependent_task_ids": [
            "2"
        ],
        "instruction": "定位并检测到小猪佩奇",
        "task_type": "detection"
    },
    {
        "task_id": "4",
        "dependent_task_ids": [
            "3"
        ],
        "instruction": "将包装盒放到小猪佩奇上",
        "task_type": "control"
    }
]
2024-06-26 18:46 | INFO     | agents.py:150 | 执行任务 1: 定位并检测到包装盒, 类型: DETECTION
2024-06-26 18:46 | INFO     | agents.py:96 | 
******detection智能体执行动作******

2024-06-26 18:46 | INFO     | robot.py:56 | 机械臂归零
2024-06-26 18:46 | INFO     | robot.py:103 | 移动至俯视姿态
2024-06-26 18:46 | SUCCESS  | robot.py:152 | 俯拍图像保存至temp/vl_now.jpg
2024-06-26 18:46 | INFO     | agents.py:100 | 目标检测

image 1/1 /home/lizen/Task/Mycobot Plus AI Agent/temp/vl_now.jpg: 448x640 1 basketball, 1 motor, 1 pig, 1 box, 9.8ms
Speed: 1.4ms preprocess, 9.8ms inference, 1.0ms postprocess per image at shape (1, 3, 448, 640)
2024-06-26 18:46 | INFO     | agents.py:144 | 执行任务 2: 将包装盒放到摩托车上, 类型: CONTROL
2024-06-26 18:46 | INFO     | agents.py:60 | 
******control智能体执行动作******

ls: cannot access '/dev/ttyUSB*': No such file or directory
2024-06-26 18:46 | WARNING  | robot.py:34 | No device found for pattern /dev/ttyUSB*: Command 'ls /dev/ttyUSB*' returned non-zero exit status 2.
2024-06-26 18:46 | SUCCESS  | robot.py:46 | find device : /dev/ttyACM0
2024-06-26 18:46 | INFO     | agents.py:40 | 
0001: from pymycobot.mycobot import MyCobot
0002: from utils.robot import *
0003: mc = MyCobot('/dev/ttyACM0',115200)
0004: # 假设mc是机械臂的控制实例
0005: 
0006: # 1. 归零机械臂
0007: back_zero(mc)
0008: 
0009: # 2. 打开夹爪
0010: gripper_open(mc)
0011: 
0012: # 3. 移动到包装盒的位置，并下降到夹取物体时的安全高度
0013: move_to_coords(mc, X=3, Y=-174)
0014: grip_END_SAFE(mc)
0015: 
0016: # 4. 关闭夹爪，夹取物体
0017: gripper_grip(mc)
0018: 
0019: # 5. 夹爪上升到搬运途中的安全高度
0020: grip_HEIGHT_SAFE(mc)
0021: 
0022: # 6. 移动到摩托车的位置
0023: move_to_coords(mc, X=113, Y=-190)
0024: 
0025: # 7. 下降到放置物体时的安全高度
0026: grip_END_SAFE(mc)
0027: 
0028: # 8. 打开夹爪，放下物体
0029: gripper_open(mc)
0030: 
0031: # 9. 夹爪上升到搬运途中的安全高度
0032: grip_HEIGHT_SAFE(mc)
0033: 

2024-06-26 18:47 | INFO     | agents.py:150 | 执行任务 3: 定位并检测到小猪佩奇, 类型: DETECTION
2024-06-26 18:47 | INFO     | agents.py:96 | 
******detection智能体执行动作******

2024-06-26 18:47 | INFO     | robot.py:56 | 机械臂归零
2024-06-26 18:47 | INFO     | robot.py:103 | 移动至俯视姿态
2024-06-26 18:47 | SUCCESS  | robot.py:152 | 俯拍图像保存至temp/vl_now.jpg
2024-06-26 18:47 | INFO     | agents.py:100 | 目标检测

image 1/1 /home/lizen/Task/Mycobot Plus AI Agent/temp/vl_now.jpg: 448x640 1 basketball, 1 pig, 1 box, 7.2ms
Speed: 1.4ms preprocess, 7.2ms inference, 0.8ms postprocess per image at shape (1, 3, 448, 640)
2024-06-26 18:47 | INFO     | agents.py:144 | 执行任务 4: 将包装盒放到小猪佩奇上, 类型: CONTROL
2024-06-26 18:47 | INFO     | agents.py:60 | 
******control智能体执行动作******

ls: cannot access '/dev/ttyUSB*': No such file or directory
2024-06-26 18:47 | WARNING  | robot.py:34 | No device found for pattern /dev/ttyUSB*: Command 'ls /dev/ttyUSB*' returned non-zero exit status 2.
2024-06-26 18:47 | SUCCESS  | robot.py:46 | find device : /dev/ttyACM0
2024-06-26 18:47 | INFO     | agents.py:40 | 
0001: from pymycobot.mycobot import MyCobot
0002: from utils.robot import *
0003: mc = MyCobot('/dev/ttyACM0',115200)
0004: # 首先确保机械臂位置归零
0005: back_zero(mc)
0006: 
0007: # 移动到包装盒的位置
0008: move_to_coords(mc, X=111, Y=-181)
0009: 
0010: # 打开夹爪准备夹取物体
0011: gripper_open(mc)
0012: 
0013: # 下降到夹取物体的安全高度
0014: grip_END_SAFE(mc)
0015: 
0016: # 关闭夹爪夹取物体
0017: gripper_grip(mc)
0018: 
0019: # 夹取物体后上升到搬运途中安全高度
0020: grip_HEIGHT_SAFE(mc)
0021: 
0022: # 移动到小猪佩奇的位置放下物体
0023: move_to_coords(mc, X=10, Y=-189)
0024: 
0025: # 下降到放置物体的安全高度
0026: grip_END_SAFE(mc)
0027: 
0028: # 打开夹爪放置物体
0029: gripper_open(mc)
0030: 
0031: # 放置完物体后，夹爪上升到搬运途中安全高度
0032: grip_HEIGHT_SAFE(mc)
0033: 
0034: # 最后回到机械臂的原点位置
0035: back_zero(mc)
0036: 
2024-06-26 18:48 | SUCCESS  | run.py:39 | 执行完成
```

机械臂运行视频：没有录

## what's more

[tips.md](https://github.com/GG-Lizen/Mycobot-plus-AI-Agent/blob/main/tips.md)包含：ROS安装，相机内参标定，安装moveit，安装mycobot_ros

> rospy不支持 python3.11

# 存在的问题

- cv2多进程
  - 如何设计使得可以流畅的展示画面又不影响获取最新的帧
- 语音识别不准确
- 路径规划问题，先移动到xy坐标再下降到z坐标，可能导致机械臂超出限位
  - 目前解决方法：先下降一定高度
- 未考虑识别物体不存在问题
