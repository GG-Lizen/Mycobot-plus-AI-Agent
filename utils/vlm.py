# utils_vlm.py
# 同济子豪兄 2024-5-22
# 多模态大模型、可视化

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
# 创建一个 ConfigParser 对象
config = configparser.ConfigParser()
# 读取配置文件
config.read('config.ini')
# 访问 DEFAULT 部分的配置
yi_vision_api = config['DEFAULT']['YI_VISION_API']
def yi_vision_api(PROMPT='帮我把红色方块放在钢笔上', img_path='temp/vl_now.jpg'):

    '''
    零一万物大模型开放平台，yi-vision视觉语言多模态大模型API
    '''
    
    API_BASE = "https://api.lingyiwanwu.com/v1"
    API_KEY = '7e8d21628c5146c79608cef1d485b99f'
    client = OpenAI(
        api_key=API_KEY,
        base_url=API_BASE
    )
    
    # 编码为base64数据
    with open(img_path, 'rb') as image_file:
        image = 'data:image/jpg;base64,' + base64.b64encode(image_file.read()).decode('utf-8')
    
    # 向大模型发起请求
    completion = client.chat.completions.create(
      model="yi-vision",
      messages=[
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text":  PROMPT
            },
            {
              "type": "image_url",
              "image_url": {
                "url": image
              }
            }
          ]
        },
      ]
    )
    
    # 解析大模型返回结果
    result = completion.choices[0].message.content.strip()
    json_pattern = re.compile(r'```json\n(.*?)\n```', re.DOTALL)
    match = json_pattern.search(result)
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
            print("llm输出如下：\n"+result+"\n请确保llm输出格式正确！")
            print("提取json："+json_str)

            
    else:
        print("未找到 JSON 内容")
        print(result)
        print('    尝试修复')
        result = json_fix(result)
        if result is None:
            print('    修复失败')
            return None
        else:
            print('    修复成功')
            return result

    print('    大模型调用成功！')

    return json_data


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
def post_processing_viz(detector,result, img_path,check=False):
  image = cv2.imread(img_path)
  # image =detector.transform_frame(image)
  size = (image.shape[1],image.shape[0])
  for item in result:

      item['top_left'],item['right_bottom']=scale_coordinates((item['top_left'], item['right_bottom']),(1024,1024), size)
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