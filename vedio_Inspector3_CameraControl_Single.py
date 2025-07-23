import cv2

import time
import traceback
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

class CameraControl:
    def __init__(self, frame_queue, result_queue, roi_queue, use_gpu=False):
        
        
        # 队列初始化
        self.frame_queue = frame_queue

        self.last_stat_time = time.time()
        self.frame_count = 0
        self.running = True


    def stopCamera(self):
        self.running = False
        print("Camera status:", self.running)

    # def update_roi(self):
    #     """更新 ROI 区域"""
    #     while not self.roi_queue.empty():
    #         self.roi = self.roi_queue.get()

    def _print_frame_statistics(self):
            """每10秒打印帧率统计"""
            current_time = time.time()
            if current_time - self.last_stat_time >= 10:
                fps = self.frame_count / (current_time - self.last_stat_time)

                msg = f"\n[统计信息]  过去{int(current_time - self.last_stat_time)}秒内共处理{self.frame_count}帧，平均帧率: {fps:.1f} FPS /  {current_time}   queue size>>>{self.frame_queue.qsize()}"

                print(f"10s一统计：{msg}")
                self.frame_count = 0
                self.last_stat_time = current_time
                
    def run(self,camera_id = 0):
        """主循环：捕获帧并进行 OCR"""
        
        
        # 打开摄像头
        cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        print(f"首先摄像头资源打开 ")

        
        # 设置帧率
        desired_fps = 120  # 目标帧率
        cap.set(cv2.CAP_PROP_FPS, desired_fps)

        # 确认实际设置的帧率
        actual_fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"请求帧率: {desired_fps} FPS")
        print(f"实际帧率: {actual_fps} FPS")


        # 设置分辨率
        # width, height = 800, 600
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        # print("设置分辨率ok")
        
        # 确认设置的分辨率
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))        
        print(f"摄像头已打开，分辨率设置为: {actual_width}x{actual_height}")

        # 设置为MJPEG格式
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        cap.set(cv2.CAP_PROP_FOURCC, fourcc)

        # 确认设置
        actual_fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        
        print(f"设置格式A: MJPG")
        print(f"实际格式A: {actual_fourcc}")


        if not cap.isOpened():
            print("无法打开摄像头")
            logging.error("无法打开摄像头")
            return
        
        
        # 设置为MJPEG格式
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        cap.set(cv2.CAP_PROP_FOURCC, fourcc)

        time.sleep(1)

        try:
            ret, frame = cap.read()
            print(f"初始化完成，开始捕获视频   首   帧{ ret }" )
        except Exception as e:
            logging.error(f"捕获视频帧失败: {e}")
            return

        try:

            countAA = 0

            while self.running:
                if countAA > 5:
                    logging.error("连续读取失败超过5次，停止尝试")
                    break
                
                grabA = cap.grab()
                if not grabA:
                    logging.error(f"抓取帧失败")
                    countAA = countAA + 1
                    time.sleep(1)
                    continue
                # 检索帧（比read()更快）
                ret, frame = cap.retrieve()
                if not ret:
                    logging.error(f"读取摄像头帧失败 ret={ret}   {countAA}")
                    countAA = countAA + 1
                    time.sleep(1)
                    continue
                
                self.frame_count = self.frame_count +1
                self._print_frame_statistics()
                timestamp = int(time.time() * 1000)
                self.frame_queue.put((frame, timestamp))        
        finally:
            # 确保释放摄像头资源
            cap.release()
            logging.info("摄像头资源已释放")