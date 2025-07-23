import cv2
import time
import os
from datetime import datetime

def list_available_cameras(max_tries=10):
    """列出所有可用的摄像头设备"""
    available = []
    for i in range(max_tries):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            available.append(i)
            cap.release()
    return available

def capture_image(camera_id=0, output_dir="captures", display_preview=True):
    """
    从指定摄像头捕获单帧图像
    
    Args:
        camera_id: 摄像头设备ID
        output_dir: 截图保存目录
        display_preview: 是否显示预览窗口
        
    Returns:
        成功时返回保存的图像路径，失败时返回None
    """
    # 确保保存目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 尝试打开摄像头（使用DSHOW后端以避免常见问题）
    cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print(f"错误：无法打开摄像头ID {camera_id}")
        return None
    
    print(f"成功连接到摄像头ID {camera_id}")
    
    try:
        # 让摄像头有时间初始化（某些摄像头需要预热时间）
        print("正在初始化摄像头...")
        time.sleep(1)
        
        # 尝试多次捕获以获取稳定的帧
        for _ in range(5):

            print("正在初始化摄像头1...")
            ret, frame = cap.read()
            print("正在初始化摄像头2...")
            if ret:
                break
            time.sleep(0.1)
        
        if not ret:
            print("错误：无法捕获图像")
            return None
        
        # 显示预览（如果需要）
        if display_preview:
            cv2.imshow("摄像头预览 (按任意键保存并退出)", frame)
            cv2.waitKey(0)
        
        # 生成保存文件名（带时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"capture_{timestamp}.jpg")
        
        # 保存图像
        cv2.imwrite(filename, frame)
        print(f"图像已保存至: {filename}")
        
        return filename
        
    finally:
        # 释放资源
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # 列出可用摄像头
    cameras = list_available_cameras()
    
    if not cameras:
        print("错误：未检测到可用摄像头")
    else:
        print(f"检测到以下可用摄像头: {cameras}")
        # 默认使用第一个摄像头
        capture_image(camera_id=cameras[0])    