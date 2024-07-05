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
from logs import logger
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
    
    start_record_ok = input('是否开启录音，按r开始录制，按k打字输入，按c输入默认指令:')
    if start_record_ok == 'r':
        record()   # 录音
        order = speech_recognition() # 语音识别
    elif start_record_ok == 'k':
        order = input('请输入指令')
    elif start_record_ok == 'c':
        order = '首先把包装盒放到摩托车上，然后再把包装盒放到小猪佩奇上'
    
    agent_maneger(mc,detector,order)

    logger.success("执行完成")

if __name__== "__main__" :
    main()


