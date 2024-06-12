"""
@Time    : 2024/6/5 17:25
@Author  : GG-Lizen
@File    : calibration_assist.py
"""
import cv2
from utils.robot import *
from pymycobot.mycobot import MyCobot
from Calibrator import Calibrator
import configparser
import ast

# 创建一个 ConfigParser 对象
config = configparser.ConfigParser()
config.read('config.ini')
# 访问 DEFAULT 部分的配置
video_path = config['DEFAULT']['DEV_VIDEO']
# 读取配置文件
config.read('config.ini')
def calibration_assist(mc:MyCobot,detect:Calibrator):
    cap = cv2.VideoCapture(video_path)
    init_num = 0
    nparams = 0
    back_zero(mc)
    gripper_open(mc)
    move_to_top_view(mc)
    #指示是否完成aruco码识别
    aruco_detect_flag=False
    while cv2.waitKey(1) < 0:
        # get a frame

        ret, frame = cap.read()
        frame = detect.transform_frame(frame)
        
        cv2.imshow("press 'q' to quit ", frame)

        # calculate the parameters of camera clipping
        if init_num < 20:
            
            if detect.get_calculate_params(frame) is None:
                cv2.imshow("can't find aruco", frame)
                continue
            else:
                x1, x2, y1, y2 = detect.get_calculate_params(frame)
                detect.draw_marker(frame, x1, y1)
                detect.draw_marker(frame, x2, y2)
                detect.sum_x1 += x1
                detect.sum_x2 += x2
                detect.sum_y1 += y1
                detect.sum_y2 += y2
                init_num = init_num+ 1
                # print(init_num)
                continue
        elif init_num == 20:
            detect.set_cut_params(
                (detect.sum_x1)/20.0,
                (detect.sum_y1)/20.0,
                (detect.sum_x2)/20.0,
                (detect.sum_y2)/20.0,
            )
            detect.sum_x1 = detect.sum_x2 = detect.sum_y1 = detect.sum_y2 = 0
            init_num =init_num+ 1
            cv2.destroyAllWindows()
            continue

        # calculate params of the coords between cube and mycobot
        if nparams < 10:
            if detect.get_calculate_params(frame) is None:
                cv2.imshow("figure", frame)
                continue
            else:
                x1, x2, y1, y2 = detect.get_calculate_params(frame)
                detect.draw_marker(frame, x1, y1)
                detect.draw_marker(frame, x2, y2)
                detect.sum_x1 += x1
                detect.sum_x2 += x2
                detect.sum_y1 += y1
                detect.sum_y2 += y2
                nparams += 1
                continue
        elif nparams == 10:
            nparams += 1
            # calculate and set params of calculating real coord between cube and mycobot
            detect.set_params(
                (detect.sum_x1+detect.sum_x2)/20.0,
                (detect.sum_y1+detect.sum_y2)/20.0,
                abs(detect.sum_x1-detect.sum_x2)/10.0 +
                abs(detect.sum_y1-detect.sum_y2)/10.0
            )
            detect.set_aruco_coord(
                detect.sum_x1/10,
                detect.sum_y1/10,
                detect.sum_x2/10,
                detect.sum_y2/10,
            )
            # cv2.circle(frame,(int(detect.aruco_x1),int(detect.aruco_y1)),2, (0, 0, 255),4)
            # cv2.circle(frame,(int(detect.aruco_x2),int(detect.aruco_y2)),2, (0, 0, 255),4)
            # cv2.imshow("check", frame)
            aruco_detect_flag = True
            cv2.destroyAllWindows()
            # print ("ok")
            continue
        # get detect result

        # print(detect.eye2hand(detect.x1,detect.y1))
        # print(detect.x1)
        # print(detect.y1)
        # print(detect.eye2hand(detect.x2,detect.y2))
        # print(detect.eye2hand(494,411))

        # cv2.imwrite("out.jpg",frame)
        # break
        # cv2.imshow("figure", frame)
    cap.release()
    cv2.destroyAllWindows()
    if not aruco_detect_flag:
        print("arcuo码识别错误")
        return False
    
    while True:
        user_input = input("是否进行机械臂标定，输入'n'取消:")
        if user_input == 'n':
            print('将从配置文件中读取，请确保点位正确')
            # 访问 Carlibration 部分的配置
            point1 = config['Carlibration']['point1']
            point2 = config['Carlibration']['point2']

            # 解析点数据，将字符串形式的元组转换为实际元组
            point1= ast.literal_eval(point1)
            point2 = ast.literal_eval(point2)
            detect.set_arm_aruco_coord(point1[0],point1[1],point2[0],point2[1])
            break
        else:
            print('开始标定')
            detect.get_robotic_arm_coord(mc)
            #将机械臂标定坐标写入文件
            config['Carlibration']['point1']=str((detect.arm_x1,detect.arm_y1))
            config['Carlibration']['point2']=str((detect.arm_x2,detect.arm_y2))
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            break
    gripper_open(mc)
    print("标定完成")
    return True