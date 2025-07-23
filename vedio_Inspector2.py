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
    desired_fps = 120  # 目标帧率
    
    # 打开摄像头
    cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
    
    
    # 设置帧率
    # cap.set(cv2.CAP_PROP_FPS, desired_fps)

    # 确认实际设置的帧率
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"请求帧率: {desired_fps} FPS")
    print(f"实际帧率: {actual_fps} FPS")


    # 设置分辨率
    width, height = resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    print("设置分辨率ok")
    
    add = cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    #print(f"设置缓冲区大小ok{add}")

    # 确认设置的分辨率
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"摄像头已打开，分辨率设置为: {actual_width}x{actual_height}")

    # 设置为MJPEG格式
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    cap.set(cv2.CAP_PROP_FOURCC, fourcc)

    # 确认设置
    actual_fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    #fourcc_code = chr(actual_fourcc & 0xFF) + chr((actual_fourcc >> 8) & 0xFF) + \
    #            chr((actual_fourcc >> 16) & 0xFF) + chr((actual_fourcc >> 24) & 0xFF)

    print(f"设置格式: MJPG")
    print(f"实际格式: {actual_fourcc}")


    
    # 初始化变量
    frame_count = 0
    start_time = time.time()
    prev_time = start_time
    
    # 开始测试
    print(f"开始测试帧率，持续时间: {duration}秒")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法读取帧，退出测试")
            break
        
        # 计算当前帧率
        current_time = time.time()
        elapsed_time = current_time - prev_time
        
        # 显示当前帧率
        if elapsed_time > 0:
            fps = 1 / elapsed_time
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # 显示图像
        cv2.imshow('Camera Test', frame)
        
        # 更新时间和帧数
        frame_count += 1
        prev_time = current_time
        
        # 按ESC键或达到测试时间退出
        if cv2.waitKey(1) == 27 or (current_time - start_time) >= duration:
            break
    
    # 计算平均帧率
    total_time = time.time() - start_time
    avg_fps = frame_count / total_time
    
    # 释放资源
    cap.release()
    cv2.destroyAllWindows()
    
    return avg_fps

if __name__ == "__main__":
    # 测试1024×768分辨率下的帧率
    avg_fps = test_camera_fps(camera_id=0, duration=10)
    print(f"测试完成！\n在分辨率下的平均帧率: {avg_fps:.2f} FPS")