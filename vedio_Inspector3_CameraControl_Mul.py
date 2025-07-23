import cv2

import time
import traceback
import logging
import queue
import threading


# 配置日志
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

class CameraControl_Mul:
    def __init__(self, frame_queue, result_queue, roi_queue, use_gpu=False):
        
        
        

        #区别在于：
        #读取完，先放入 grab queue        
        self.grab_queue = queue.Queue()  # 存储待解码的帧
        
        # 处理完，放入frame_queue
        self.frame_queue = frame_queue



        self.last_stat_time = time.time()
        self.frame_count = 0
        self.running = True

        self.stopped = False

        self.num_work = 10
        self.workers = [self.num_work]


        self.cap = None


        self._retrieve_frames_num = 0
        self._grab_frames_num = 0

        

    def _do_something(self):
        # 启动多个retrieve工作线程
        for _ in range(self.num_work):
            worker = threading.Thread(target=self._retrieve_frames)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

        print("retrieve线程已启动")


        # 启动grab线程
        self.grab_thread = threading.Thread(target=self._grab_frames)
        self.grab_thread.daemon = True
        self.grab_thread.start()

        print("grab线程已启动")

        


        
    def _retrieve_frames(self):
        while not self.stopped:
            try:
                # 从grab队列获取任务
                self.grab_queue.get(timeout=1)

                
                # 执行retrieve
                ret, frame = self.cap.retrieve()

                self._retrieve_frames_num = self._retrieve_frames_num + 1
                if self._retrieve_frames_num % 100 == 0 :
                    print(f"retrieve帧数: {self._retrieve_frames_num}")
                # print(f"从_grab队列获取任务  ret{ret}  :  {self.grab_queue.qsize()}")


                #拿出来，放到frame_queue
                if ret:
                    timestamp = int(time.time() * 1000)
                    self.frame_queue.put((frame, timestamp))     

                #统计帧数
                self.frame_count = self.frame_count +1
                

                self.grab_queue.task_done()
            except queue.Empty:
                # print("_grab队列为空")
                pass

        print("retrieve线程已停止")

    def stopCamera(self):

        self.stopped = True
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

                msg = f"\n[统计信息]  过去{int(current_time - self.last_stat_time)}秒内共处理{self.frame_count}帧，平均帧率: {fps:.1f} FPS /  {current_time}   queue size>>>{self.frame_queue.qsize()}   >>>>   grab queue size {self.grab_queue.qsize()}"

                print(f"10s一统计：{msg}")
                self.frame_count = 0
                self.last_stat_time = current_time




    def _grab_frames(self,camera_id = 0):
        """主循环：捕获帧并进行 OCR"""
        
        # 打开摄像头
        self.cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        print(f"首先摄像头资源打开 ")

        
        # 设置帧率
        desired_fps = 120  # 目标帧率
        self.cap.set(cv2.CAP_PROP_FPS, desired_fps)

        # 确认实际设置的帧率
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
        print(f"请求帧率: {desired_fps} FPS")
        print(f"实际帧率: {actual_fps} FPS")


        # 设置分辨率
        # width, height = 800, 600
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        # print("设置分辨率ok")
        
        # 确认设置的分辨率
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"摄像头已打开，分辨率设置为: {actual_width}x{actual_height}")

        # 设置为MJPEG格式
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)

        # 确认设置
        actual_fourcc = int(self.cap.get(cv2.CAP_PROP_FOURCC))

        print(f"设置格式A: MJPG")
        print(f"实际格式A: {actual_fourcc}")


        if not self.cap.isOpened():
            print("无法打开摄像头")
            logging.error("无法打开摄像头")
            return

        self.cap.set(cv2.CAP_PROP_FPS, 90)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

        # 设置为MJPEG格式
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)

        time.sleep(1)

        try:
            ret, frame = self.cap.read()
            print(f"初始化完成，开始捕获视频   首   帧{ ret }" )
            if not ret:
                logging.error("读取摄像头 首帧  fail...")
                self.stopped = True
                return
        except Exception as e:
            logging.error(f"捕获视频帧失败: {e}")
            return

        
              
        print(f"初始化完成，启动 while  循环 ...." )
        

        try:

            countAA = 0

            while self.running:
                if countAA > 5:
                    logging.error("连续读取失败超过5次，停止尝试")
                    break

                grabA = self.cap.grab()
                self._grab_frames_num = self._grab_frames_num + 1
                if self._grab_frames_num % 400000 == 0 :
                    print(f"抓取帧数A: {self._grab_frames_num}")


                if not grabA:
                    logging.error(f"抓取帧失败")
                    countAA = countAA + 1
                    time.sleep(1)
                    continue

                if not ret:
                    logging.error(f"读取摄像头帧失败 ret={ret}   {countAA}")
                    countAA = countAA + 1
                    time.sleep(1)
                    continue
                

                

                # print(f"    put message to queue:{self.grab_queue.qsize()}")
                
                #is to fast
                time.sleep(0.01)
                
                #print frame
                self._print_frame_statistics()

                try:
                    self.grab_queue.put(True, timeout=1)  # 等待 1 秒，若满则抛异常
                except queue.Full:
                    # 队列满时的处理逻辑（例如丢弃旧帧）
                    print("队列已满，丢弃最新帧")



        finally:
            # 确保释放摄像头资源
            self.cap.release()
            logging.info("摄像头资源已释放")