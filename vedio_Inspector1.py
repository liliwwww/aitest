import cv2

def get_supported_fps(camera_id=0):
    cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    supported_modes = {}
    
    # 常见分辨率列表
    resolutions = [
        (640, 480),(800, 600), (1024, 768),(1280, 720), (1920, 1080)
    ]
    
    # 常见帧率列表（根据设备可能需要调整）
    fps_list = [15, 30, 60, 120, 240, 360, 480, 600]
    
    for width, height in resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # 检查此分辨率下支持的最大帧率
        supported_fps = []
        for fps in fps_list:
            cap.set(cv2.CAP_PROP_FPS, fps)
            actual_fps = cap.get(cv2.CAP_PROP_FPS)
            
            # 如果设置的帧率与实际帧率相近，则认为支持
            if abs(actual_fps - fps) < 1:
                supported_fps.append(fps)
        
        if supported_fps:
            supported_modes[f"{width}x{height}"] = supported_fps
    
    cap.release()
    return supported_modes

# 使用示例
if __name__ == "__main__":
    modes = get_supported_fps(0)
    print("支持的分辨率及最大帧率:")
    for res, fps_list in modes.items():
        print(f"{res}: 最大帧率 = {max(fps_list)} FPS")