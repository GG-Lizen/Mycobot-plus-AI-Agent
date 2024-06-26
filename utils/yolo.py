"""
@Time    : 2024-6-26
@Author  : GG-Lizen
@File    : yolo.py
"""

import cv2
import threading
import numpy as np
from PIL import Image
from PIL import ImageFont, ImageDraw
# 导入中文字体，指定字号
font = ImageFont.truetype('asset/SimHei.ttf', 26)
# Yi-Vision调用函数
import openai
from openai import OpenAI
import base64
import configparser
import json
import re
from utils.json_extract_parse import json_fix
from logs import logger
from ultralytics import YOLO
import matplotlib.pyplot as plt

# 创建一个 ConfigParser 对象
config = configparser.ConfigParser()
# 读取配置文件
config.read('config.ini')
# 访问 DEFAULT 部分的配置
YOLO_PATH = config['LOCAL_MODEL']['YOLO_PATH']
def detect(img_path='temp/vl_now.jpg',debug = True):
  '''
   使用yolo进行目标检测，返回结果如下
   [
    {
      name:str,
      top_left:(x1,y1),
      right_bottom:(x2,y2)
    },
    ...
   ]
  ''' 
  yolo = YOLO(YOLO_PATH,task="detect")
  result = yolo(source=img_path)[0]
  ret = []
  for box in result.boxes:
    item={}
    cords = box.xyxy[0].tolist()
    class_id = box.cls[0].item()
    conf = box.conf[0].item()
    item['name']  = result.names[class_id]
    item['top_left'] = (cords[0],cords[1])
    item['right_bottom'] = (cords[2],cords[3])
    ret.append(item)

  if debug:
     plt.imshow(result.plot()[:,:,::-1])

  return ret




def scale_coordinates(original_coords, original_size, new_size):
    """
    Scale coordinates from the original image size to the new image size.
    
    Parameters:
    original_coords (tuple): A tuple of the form ((x1, y1), (x2, y2)) representing the top-left and bottom-right coordinates of the bounding box.
    original_size (tuple): A tuple (width, height) representing the size of the original image.
    new_size (tuple): A tuple (width, height) representing the size of the new image.
    
    Returns:
    tuple: A tuple of the form ((new_x1, new_y1), (new_x2, new_y2)) representing the scaled coordinates.
    """
    (x1, y1), (x2, y2) = original_coords
    original_width, original_height = original_size
    new_width, new_height = new_size
    
    # Calculate scaling factors
    x_scale = new_width / original_width
    y_scale = new_height / original_height
    
    # Scale coordinates
    new_x1 = int(x1 * x_scale)
    new_y1 = int(y1 * y_scale)
    new_x2 = int(x2 * x_scale)
    new_y2 = int(y2 * y_scale)
    
    return (new_x1, new_y1), (new_x2, new_y2)
def get_center_coordinate(top_left, right_bottom):
    center_x = (top_left[0] + right_bottom[0]) / 2
    center_y = (top_left[1] + right_bottom[1]) / 2
    return (center_x, center_y)
def cv2imshow(image):
    cv2.imshow('Image', image)
    # 等待窗口关闭
    cv2.waitKey(0)
    cv2.destroyAllWindows()
def post_processing_viz(result, img_path,check=False):
  image = cv2.imread(img_path)
  size = (image.shape[1],image.shape[0])
  for item in result:
      item['top_left']=tuple(map(int, item['top_left']))
      item['right_bottom']=tuple(map(int, item['right_bottom']))
      # item['top_left'],item['right_bottom']=scale_coordinates((item['top_left'], item['right_bottom']),(1024,1024), size)
      item['center']=get_center_coordinate(item['top_left'],item['right_bottom'])
      cv2.rectangle(
              image,
              item['top_left'],
              item['right_bottom'],
              (0, 255, 0),
              thickness=2,
              lineType=cv2.FONT_HERSHEY_COMPLEX,
          )
      # 写中文物体名称
      img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # BGR 转 RGB
      img_pil = Image.fromarray(img_rgb) # array 转 pil
      draw = ImageDraw.Draw(img_pil)
      # 写起点物体中文名称
      draw.text(item['top_left'], item['name'], font=font, fill=(255, 0, 0, 1)) # 文字坐标，中文字符串，字体，rgba颜色
      image = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR) # RGB转BGR
  if check:
    cv2.imshow('Image', image)
    # 等待窗口关闭
    cv2.waitKey(0)
    cv2.destroyAllWindows()

  return result