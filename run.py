
from utils.robot import *
from utils.agents import *
from utils.asr import *
from utils.tts import *
from pymycobot.mycobot import MyCobot
from Calibrator import Calibrator
import configparser
from utils.calibration_assist import *
import multiprocessing as mp
import configparser
# 创建一个 ConfigParser 对象
config = configparser.ConfigParser()
config.read('config.ini')
# 访问 DEFAULT 部分的配置
video_path = config['DEFAULT']['DEV_VIDEO']
port = config['DEFAULT']['MYCOBOT_PORT']
baud = config['DEFAULT']['MYCOBOT_BAUD']

mc = MyCobot(port,baud)
# 设置运动模式为插补
mc.set_fresh_mode(0)
detector = Calibrator()


def main():
    if not calibration_assist(mc=mc,detect=detector):
            return
    order = '先回到原点，然后把包装盒放到小猪佩奇上'
    start_record_ok = input('是否开启录音，按r开始录制，按k打字输入，按c输入默认指令:')
    if start_record_ok == 'r':
        record()   # 录音
        order = speech_recognition() # 语音识别
    elif start_record_ok == 'k':
        order = input('请输入指令')
    elif start_record_ok == 'c':
        order = '先回到原点，然后把包装盒放到小猪佩奇上'
    


    agent_maneger(detector,order)
    print("执行完成")


if __name__== "__main__" :
    main()



    
