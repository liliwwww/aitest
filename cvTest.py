

import cv2  
import pytesseract
from pytesseract import image_to_data, Output  


# 如果你是 Windows 系统，需要指定 Tesseract 的路径
# 安装 程序 
# pip install pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Tesseract-OCR\tesseract.exe'


# OCR识别Label  
def detect_labels(image):  
    data = image_to_data(image, output_type=Output.DICT)  
    labels = []  
    for i in range(len(data['text'])):  
        if data['conf'][i] > 60:  # 置信度过滤  
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])  
            labels.append({"text": data['text'][i], "bbox": (x, y, x+w, y+h)})  
    return labels  

# 控件检测（示例：输入框）  
def detect_input_fields(image):  
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  
    edges = cv2.Canny(gray, 50, 150)  
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  
    inputs = []  
    for cnt in contours:  
        x, y, w, h = cv2.boundingRect(cnt)  
        inputs.append({"bbox": (x, y, x+w, y+h)})  
    return inputs  



if __name__ == "__main__":
    # 读取图片
    image_path = r'C:\Users\wdp\project\auto-test\screenshots\screenshot_20250407_155424.png'
    try:
        image = cv2.imread(image_path)
        
        if image is None:
            print(f"无法读取图片: {image_path}")
        else:

            print("read image ok" )
            # 调用 detect_labels 函数
            labels = detect_labels(image)
            print("检测到的标签:")
            for label in labels:
                print(f"文本: {label['text']}, 边界框: {label['bbox']}")

            # 调用 detect_input_fields 函数
            input_fields = detect_input_fields(image)
            print("检测到的输入框:")
            for input_field in input_fields:
                print(f"边界框: {input_field['bbox']}")
    except Exception as e:
        print(f"发生错误: {e}")
    