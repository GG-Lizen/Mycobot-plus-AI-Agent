
import cv2
from utils.robot import *
from pymycobot.mycobot import MyCobot
class Calibrator():
    def __init__(self, camera_x=150, camera_y=-10):
         # choose place to set cube
        self.color = 0
        # parameters to calculate camera clipping parameters
        self.x1 = self.x2 = self.y1 = self.y2 = 0
        #机械臂在第一标定点第二标定点的坐标
        self.arm_x1 = self.arm_x2 = self.arm_y1 = self.arm_y2 = 0
        #第一标定点第二标定点的坐标
        self.aruco_x1 = self.aruco_x2 = self.aruco_y1 = self.aruco_y2 = 0
        # set cache of real coord
        self.cache_x = self.cache_y = 0
        # use to calculate coord between cube and mycobot
        self.sum_x1 = self.sum_x2 = self.sum_y2 = self.sum_y1 = 0
        # The coordinates of the grab center point relative to the mycobot
        self.camera_x, self.camera_y = camera_x, camera_y
        # The coordinates of the cube relative to the mycobot
        self.c_x, self.c_y = 0, 0
         # The ratio of pixels to actual values
        self.ratio = 0
        # Get ArUco marker dict that can be detected.
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_50)
        # Get ArUco marker params.
        self.aruco_params = cv2.aruco.DetectorParameters()
    def draw_marker(self, img, x, y):
        # draw rectangle on img
        cv2.rectangle(
            img,
            (x - 20, y - 20),
            (x + 20, y + 20),
            (0, 255, 0),
            thickness=2,
            lineType=cv2.FONT_HERSHEY_COMPLEX,
        )
        # add text on rectangle
        cv2.putText(img, "({},{})".format(x, y), (x, y),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (243, 0, 0), 2,)
    def get_calculate_params(self,img):
        if img is None:
            # print("None")
            return None
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Detect ArUco marker.
        dictionary =  self.aruco_dict
        parameters=  self.aruco_params 
        detector = cv2.aruco.ArucoDetector(dictionary, parameters)
        corners, ids, rejectImaPoint = detector.detectMarkers(gray)
        """
        Two Arucos must be present in the picture and in the same order.
        There are two Arucos in the Corners, and each aruco contains the pixels of its four corners.
        Determine the center of the aruco by the four corners of the aruco.
        """
        if len(corners) > 0:
            if ids is not None:
                if len(corners) <= 1 or ids[0] == 1:
                    return None

                x1 = x2 = y1 = y2 = 0
                point_11, point_21, point_31, point_41 = corners[0][0]
                x1, y1 = int((point_11[0] + point_21[0] + point_31[0] + point_41[0]) / 4.0), int(
                    (point_11[1] + point_21[1] + point_31[1] + point_41[1]) / 4.0)
                point_1, point_2, point_3, point_4 = corners[1][0]
                x2, y2 = int((point_1[0] + point_2[0] + point_3[0] + point_4[0]) / 4.0), int(
                    (point_1[1] + point_2[1] + point_3[1] + point_4[1]) / 4.0)
                return x1, x2, y1, y2
        return None    
    def transform_frame(self, frame):
    # enlarge the image by 1.5 times
        fx = 1.5
        fy = 1.5
        # origin_size=(frame.shape[1],frame.shape[0])
        # new_size=(frame.shape[1]*fx,frame.shape[0]*fx)
        frame = cv2.resize(frame, (0, 0), fx=fx, fy=fy,
                        interpolation=cv2.INTER_CUBIC)
        if self.x1 != self.x2:
            # the cutting ratio here is adjusted according to the actual situation
            frame = frame[int(self.y2*0.2):int(self.y1*1.15),
                        int(self.x1*0.7):int(self.x2*1.15)]
        # point1=scale_coordinates((self.x1,self.y1),origin_size,new_size)
        # point2=scale_coordinates((self.x2,self.y2),origin_size,new_size)
        return frame
    def set_cut_params(self, x1, y1, x2, y2):
        self.x1 = int(x1)
        self.y1 = int(y1)
        self.x2 = int(x2)
        self.y2 = int(y2)
        # print(self.x1, self.y1, self.x2, self.y2)
        # set parameters to calculate the coords between cube and mycobot
    def set_params(self, c_x, c_y, ratio):
        self.c_x = c_x
        self.c_y = c_y
        self.ratio = 250.0/ratio
    def set_arm_aruco_coord(self, x1, y1, x2,y2):
        self.arm_x1 =x1
        self.arm_y1 =y1
        self.arm_x2 =x2
        self.arm_y2 =y2
    def set_aruco_coord(self, aruco_x1, aruco_y1, aruco_x2,aruco_y2):
        self.aruco_x1 =aruco_x1
        self.aruco_y1 =aruco_y1
        self.aruco_x2 =aruco_x2
        self.aruco_y2 =aruco_y2
     # calculate the coords between cube and mycobot
    def get_position(self, x, y):
        return ((y - self.c_y)*self.ratio + self.camera_x), ((x - self.c_x)*self.ratio + self.camera_y)


    def get_robotic_arm_coord(self, mc: MyCobot):
        # 已完成标定点 0 ～ 2
        cali_num = 0
        while (1):
            user_input = input("即将释放机械臂，请扶好机械臂，扶好请输入'y':")
            if user_input == 'y':
                relax_arms(mc)
            print(f"请将机械臂夹爪移至第标定点{cali_num+1}")
            print("完成请输入'y':")

            while (1):
                # 模拟某种条件检测，可以根据需要调整
                user_input=input()
                coords = mc.get_coords()
                if user_input=='y':
                    if cali_num == 0:
                        self.arm_x1 = coords[0]
                        self.arm_y1 = coords[1]
                    elif cali_num == 1:
                        self.arm_x2 = coords[0]
                        self.arm_y2 = coords[1]
                    cali_num += 1
                    show = False    
                    back_zero(mc)
                    time.sleep(2)
                    break
                else :
                    print("无效输入")

            if cali_num == 2:
                print("完成标定")
                break    

        if cali_num != 2:
            print("程序异常终止")
        
        # cv2.destroyAllWindows()
    def eye2hand(self,X_im=160, Y_im=120):
        '''
        输入目标点在图像中的像素坐标，转换为机械臂坐标
        '''
        # 整理两个标定点的坐标
        cali_1_im = [self.aruco_x1,self.aruco_y1]                     # 左下角，第一个标定点的像素坐标，要手动填！
        cali_1_mc = [self.arm_x1, self.arm_y1]                  # 左下角，第一个标定点的机械臂坐标，要手动填！
        cali_2_im = [self.aruco_x2,self.aruco_y2]                      # 右上角，第二个标定点的像素坐标
        cali_2_mc = [self.arm_x2, self.arm_y2]                    # 右上角，第二个标定点的机械臂坐标，要手动填！
        
        X_cali_im = [cali_1_im[0], cali_2_im[0]]     # 像素坐标
        X_cali_mc = [cali_1_mc[0], cali_2_mc[0]]     # 机械臂坐标
        Y_cali_im = [cali_2_im[1], cali_1_im[1]]     # 像素坐标，先小后大
        Y_cali_mc = [cali_2_mc[1], cali_1_mc[1]]     # 机械臂坐标，先大后小

        # X差值
        X_mc = int(np.interp(X_im, X_cali_im, X_cali_mc))

        # Y差值
        Y_mc = int(np.interp(Y_im, Y_cali_im, Y_cali_mc))
        return (X_mc, Y_mc)
