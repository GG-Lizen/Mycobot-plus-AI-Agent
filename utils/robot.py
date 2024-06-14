"""
@Time    : 
@Author  : 同济子豪兄
@File    : llm.py
@Modify  : GG-Lizen
"""
import cv2
import numpy as np
import time
import configparser
from utils.VideoCapture import VideoCapture_Bufferless
from utils.colorful import ColorPrinter
import subprocess
from logs import logger

config = configparser.ConfigParser()
config.read('config.ini')
angles = config['MYCOBOT']['TOP_VIEW_ANGLES']
ANGLES_LIST = [float(angle) for angle in angles.split(',')]
coords_r = config['MYCOBOT']['COORDS_R']
COORD_R_LIST = [float(coord_r) for coord_r in coords_r.split(',')]
HEIGHT_SAFE = int(config['MYCOBOT']['HEIGHT_SAFE'])
HEIGHT_END = int(config['MYCOBOT']['HEIGHT_END'])




def get_device_path(pattern):
    try:
        # 获取 /dev/ 目录下符合指定模式的文件列表
        return subprocess.check_output(f"ls {pattern}", shell=True).decode().strip()
    except subprocess.CalledProcessError as e:
        # 处理找不到文件的情况
        logger.warning(f"No device found for pattern {pattern}: {e}")
        return None

def get_robot_port():
    # 获取 /dev/ttyACM* 和 /dev/ttyUSB* 设备路径
    robot_m5 = get_device_path("/dev/ttyUSB*")
    robot_wio =get_device_path("/dev/ttyACM*")
    if robot_m5 is None:
        robot = robot_wio
    else:
        robot = robot_m5
    # print(f'find device : {robot}' )
    logger.success('find device : ' + ColorPrinter.colorful(f'{robot}','blue') )
    return robot




def back_zero(mc):
    '''
    机械臂归零
    '''
    logger.info('机械臂归零')
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(3)

def relax_arms(mc):
    logger.info('放松机械臂关节')
    mc.release_all_servos()

def head_shake(mc):
    # 左右摆头
    mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    time.sleep(1)
    for count in range(2):
        mc.send_angle(5, 30, 80)
        time.sleep(0.5)
        mc.send_angle(5, -30,80)
        time.sleep(0.5)
    # mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    # time.sleep(1)
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(2)


def head_nod(mc):
    # 点头
    mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)
    for count in range(2):
        mc.send_angle(4, 13, 70)
        time.sleep(0.5)
        mc.send_angle(4, -20, 70)
        time.sleep(1)
        mc.send_angle(4,13,70)
        time.sleep(0.5)
    mc.send_angles([0.87,(-50.44),47.28,0.35,(-0.43),(-0.26)],70)

def move_to_coords(mc,X=150, Y=-130, height=HEIGHT_END+(HEIGHT_SAFE-HEIGHT_END)/2):
    logger.info('移动至指定坐标：X {} Y {}'.format(X, Y))
    #根据实际情况修改
    mc.send_coords([X, Y, height, COORD_R_LIST[0], COORD_R_LIST[1],COORD_R_LIST[2]], 50, 0)
    time.sleep(3)

def single_joint_move(mc,joint_index, angle):
    logger.info('关节 {} 旋转至 {} 度'.format(joint_index, angle))
    mc.send_angle(joint_index, angle, 40)
    time.sleep(2)

def move_to_top_view(mc):
    logger.info('移动至俯视姿态')
    mc.send_angles(ANGLES_LIST, 40)
    time.sleep(2)

def top_view_shot(mc,detector,check=False):
    '''
    拍摄一张图片并保存
    check：是否需要人工看屏幕确认拍照成功，再在键盘上按q键确认继续
    '''

    back_zero(mc)
    move_to_top_view(mc)
    # 获取摄像头，传入0表示获取系统默认摄像头
    # 创建一个 ConfigParser 对象
    config = configparser.ConfigParser()
    config.read('config.ini')
    # 访问 DEFAULT 部分的配置
    video_path = config['DEFAULT']['DEV_VIDEO']
    streamer = VideoCapture_Bufferless(video_path)
    try_detect_num =20
    img_bgr = None
    try:
        while cv2.waitKey(1) < 0:
            if try_detect_num == 0:
                time.sleep(2)
                back_zero(mc)
                move_to_top_view(mc)
                time.sleep(1)
                try_detect_num =20

            frame = streamer.read()
            if frame is None:
                continue
            if detector.get_calculate_params(frame) is None:
                cv2.imshow("can't find aruco", frame)
                logger.debug("未识别到aruco码")
                try_detect_num -= 1 
                continue
            else:
                img_bgr = detector.transform_frame(frame)
                break
    
    finally:
        cv2.destroyAllWindows()
        streamer.release()  # Ensure the video capture is released
    if img_bgr is None:
        logger.error("未识别到aruco码，top_view_shot运行失败")
        raise RuntimeError("未识别到aruco码，top_view_shot运行失败")
    # 保存图像
    logger.success('俯拍图像保存至temp/vl_now.jpg')
    cv2.imwrite('temp/vl_now.jpg', img_bgr)

    
    if check:

    # 屏幕上展示图像
        cv2.destroyAllWindows()   # 关闭所有opencv窗口
        cv2.imshow('vl_now', img_bgr) 
        logger.info('请确认拍照成功,按q键退出')
        while(True):
            key = cv2.waitKey(10) & 0xFF 
            if key == ord('q'): # 按q键退出
                cv2.destroyAllWindows()
                break
        
def gripper_open(mc):
    mc.set_gripper_state(0, 30)
    time.sleep(2)
def gripper_grip(mc):
    mc.set_gripper_state(1, 30)
    time.sleep(2)
def set_gripper_value(mc,val):
    mc.set_gripper_value(val, 20)
def grip_END_SAFE(mc,hight=HEIGHT_END):
    mc.send_coord(3,hight,40)
    time.sleep(3)
def grip_HEIGHT_SAFE(mc,hight=HEIGHT_SAFE):
    mc.send_coord(3,hight,40)
    time.sleep(3)
# def grip_move(mc, XY_START=[230,-50], HEIGHT_START=90, XY_END=[100,220], height_end=HEIGHT_END, hight_safe=HEIGHT_SAFE):

#     '''
#     用夹抓，将物体从起点夹起移动至终点

#     mc：机械臂实例
#     XY_START：起点机械臂坐标
#     HEIGHT_START：起点高度
#     XY_END：终点机械臂坐标
#     height_end：终点高度
#     hight_safe：搬运途中安全高度
#     '''

#     # 设置运动模式为插补
#     mc.set_fresh_mode(0)
    
#     # # 机械臂归零
#     # print('    机械臂归零')
#     # mc.send_angles([0, 0, 0, 0, 0, 0], 40)
#     # time.sleep(4)
    
#     # 吸泵移动至物体上方
#     print('    吸泵移动至物体上方')
#     mc.send_coords([XY_START[0], XY_START[1], hight_safe, 0, 180, 90], 20, 0)
#     time.sleep(4)

#     # 开启吸泵
#     gripper_open()
    
#     # 吸泵向下吸取物体
#     print('    吸泵向下吸取物体')
#     mc.send_coords([XY_START[0], XY_START[1], HEIGHT_START, 0, 180, 90], 15, 0)
#     time.sleep(4)

#     # 升起物体
#     print('    升起物体')
#     mc.send_coords([XY_START[0], XY_START[1], hight_safe, 0, 180, 90], 15, 0)
#     time.sleep(4)

#     # 搬运物体至目标上方
#     print('    搬运物体至目标上方')
#     mc.send_coords([XY_END[0], XY_END[1], hight_safe, 0, 180, 90], 15, 0)
#     time.sleep(4)

#     # 向下放下物体
#     print('    向下放下物体')
#     mc.send_coords([XY_END[0], XY_END[1], height_end, 0, 180, 90], 20, 0)
#     time.sleep(3)

#     # 关闭吸泵
#     gripper_grip()

#     # 机械臂归零
#     print('    机械臂归零')
#     mc.send_angles([0, 0, 0, 0, 0, 0], 40)
#     time.sleep(3)


