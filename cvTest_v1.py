import cv2  
import pytesseract
from pytesseract import image_to_data, Output  
import numpy as np
import time


# 如果你是 Windows 系统，需要指定 Tesseract 的路径
# 安装 程序 
# pip install pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Tesseract-OCR\tesseract.exe'
image_path = r'C:\Users\wdp\project\auto-test\screenshots\screenshot_20250407_155424.png'
image_path = r'C:\Users\wdp\project\aitest\wx_20250423185424.png'





# OCR识别Label
def detect_labels(image):
    data = image_to_data(image, output_type=Output.DICT)
    labels = []
    for i in range(len(data['text'])):
        if data['conf'][i] > 60:  # 置信度过滤
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            labels.append({"text": data['text'][i], "bbox": (x, y, x + w, y + h)})
    return labels

# 控件检测（示例：输入框）
def detect_input_fields(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    inputs = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        inputs.append({"bbox": (x, y, x + w, y + h)})
    return inputs

def classify_page(image):  
    # 检测表格线  
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  
    edges = cv2.Canny(gray, 50, 150)  
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)  
    # 若检测到密集水平/垂直线，判定为列表页  
    if len(lines) > 20:  
        print("list page")
        return "list_page"  
    else:  
        print("edit_page")
        return "edit_page"  
    

if __name__ == "__main__":
    # 读取图片
    
    try:
        image = cv2.imread(image_path)

        classify_page(image)

        '''
        if image is None:
            print(f"无法读取图片: {image_path}")
        else:
            # 调用 detect_labels 函数
            labels = detect_labels(image)
            # 调用 detect_input_fields 函数
            input_fields = detect_input_fields(image)

            # 初始化 ID
            current_id = 1

            print("检测到的标签:")
            for label in labels:
                label["id"] = current_id
                print(f"ID: {label['id']}, 文本: {label['text']}, 边界框: {label['bbox']}")
                x1, y1, x2, y2 = label['bbox']
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(image, f"ID: {label['id']}", (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                cv2.putText(image, label['text'], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                current_id += 1

            print("检测到的输入框:")
            for input_field in input_fields:
                input_field["id"] = current_id
                print(f"ID: {input_field['id']}, 边界框: {input_field['bbox']}")
                x1, y1, x2, y2 = input_field['bbox']
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(image, f"ID: {input_field['id']}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                current_id += 1

            # 保存绘制好的图片
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            output_path = f'output{timestamp}.jpg'
            cv2.imwrite(output_path, image)
            print(f"结果图片已保存到: {output_path}")
        '''
    except Exception as e:
        print(f"发生错误: {e}")
    