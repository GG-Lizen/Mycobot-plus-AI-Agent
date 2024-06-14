"""
@Time    : 2024/6/5 17:25
@Author  : GG-Lizen
@File    : run.py
"""

from pymycobot.mycobot import MyCobot
from utils.robot import *
from agents import *
from utils.calibration_assist import *
from utils.asr import *
from utils.tts import *
import configparser
# 创建一个 ConfigParser 对象
config = configparser.ConfigParser()
config.read('config.ini')
# 访问 DEFAULT 部分的配置
video_path = config['DEFAULT']['DEV_VIDEO']
baud = config['DEFAULT']['MYCOBOT_BAUD']


def main():
    mc = MyCobot(get_robot_port(),baud)
    detector = Calibrator()
    if not calibration_assist(mc=mc,detect=detector):
            return
    order = '把包装盒放到小猪佩奇上'
    start_record_ok = input('是否开启录音，按r开始录制，按k打字输入，按c输入默认指令:')
    if start_record_ok == 'r':
        record()   # 录音
        order = speech_recognition() # 语音识别
    elif start_record_ok == 'k':
        order = input('请输入指令')
    elif start_record_ok == 'c':
        order = '先回到原点，然后把包装盒放到小猪佩奇上'
    # top_view_shot(mc,detector,order)
    agent_maneger(mc,detector,order)
    print("执行完成")


if __name__== "__main__" :
    main()


