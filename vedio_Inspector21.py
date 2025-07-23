import cv2

import cv2
import time

#结论：
#不设置帧率，不可以   
# MJPG实际格式: 1196444237 
# 默认 实际格式: 844715353 ， 不可以
#不设置格式，不可以



def test_camera_fps(camera_id=0, resolution=(800, 600), duration=10):
    """
    测试摄像头在指定分辨率下的平均帧率
    
    参数:
        camera_id: 摄像头ID，默认0
        resolution: 分辨率，元组(width, height)，默认(1024, 768)
        duration: 测试持续时间(秒)，默认10秒
    """
    

    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
    print(f"可用后端:{cv2.CAP_DSHOW}")
    for backend in backends:
        cap = cv2.VideoCapture(camera_id, backend)
        if cap.isOpened():
            print(f"Backend {backend} works")
            break
        cap.release()
        
    
        
    return 100

if __name__ == "__main__":
    # 测试1024×768分辨率下的帧率
    avg_fps = test_camera_fps(camera_id=0, duration=10)
    print(f"测试完成！\n在分辨率下的平均帧率: {avg_fps:.2f} FPS")