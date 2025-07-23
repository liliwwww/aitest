import cv2

def get_supported_resolutions(camera_id=0):
    cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    supported_resolutions = []
    
    # 常见分辨率列表，可根据需要扩展
    resolutions = [
        (640, 480), (800, 600), (1024, 768), 
        (1280, 720), (1280, 800), (1280, 1024),
        (1366, 768), (1600, 900), (1920, 1080),
        (2560, 1440), (3840, 2160)
    ]
    
    for width, height in resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # 获取实际设置的分辨率
        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        # 如果设置成功，则添加到支持列表
        if actual_width == width and actual_height == height:
            supported_resolutions.append((width, height))
    
    cap.release()
    return supported_resolutions

# 使用示例
if __name__ == "__main__":
    resolutions = get_supported_resolutions(0)  # 0表示默认摄像头
    print("支持的分辨率:")
    for res in resolutions:
        print(f"{res[0]}x{res[1]}")


self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # 设置宽度
    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # 设置高度

# 640x480
# 800x600
# 1024x768
# 1280x720
# 1280x1024
# 1920x1080