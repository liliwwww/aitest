import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from vedio_Inspector3_DisplayWidget import DisplayWidget
from vedio_Inspector3_CameraControl_Single import CameraControl
from threading import Thread  # 导入线程模块

import cv2
import queue
import argparse

class ImageSaverA:
    def __init__(self):
        self.is_saving = False
    
    def start_save(self):
        self.is_saving = True
        print("开始保存图像")
    
    def stop_save(self):
        print(f"停止保存图像: {self.is_saving}")
        self.is_saving = False


if __name__ == '__main__':
    # 解析命令行参数
    parser = argparse.ArgumentParser()
    parser.add_argument('--use_gpu', action='store_true', help='Enable GPU acceleration if available')
    args = parser.parse_args()

    # 设置多进程启动方式
    
    imageCount = 0

    frame_queue = queue.Queue(maxsize=50000)
    result_queue = queue.Queue()
    roi_queue = queue.Queue()

    print("INIT:1 构建Queue")


    # 启动摄像头进程
    # 这个frame_queue用于传输摄像头帧数据， 在CameraControl类中被生产
    cam_control = CameraControl(frame_queue, result_queue, roi_queue, use_gpu=args.use_gpu)
    cam_thread = Thread(target=cam_control.run)  # 创建线程
    cam_thread.start()  # 启动线程
    print("INIT:2 摄像头进程已启动1")


    isSaveImage = False
    image_saver = ImageSaverA()

    

    # 启动 GUI
    app = QApplication(sys.argv)
    display = DisplayWidget( image_saver )
    display.show()
    print("INIT:4 启动GUI")

    def startSaveImage():        
        isSaveImage = True
        print(f"set开始保存图像:{isSaveImage}")

    def stopSaveImage():
        print(f"set停止保存图像:{isSaveImage}")
        isSaveImage = False




    
    # 定义一个方法更新图像
    def update_image():


        global imageCount
        #print(f"更新图像 {frame_queue.qsize()}")

        if not frame_queue.empty():
            frame, timestamp = frame_queue.get() 

            imageCount = imageCount +1

            ###
            if image_saver.is_saving and imageCount % 100 == 0:
                filename = f"screenshot/frame_{timestamp}.jpg"
                # 保存帧为图片
                cv2.imwrite(filename, frame)
                print(f"帧已保存为: {filename}   queue size{frame_queue.qsize() }")

            # 先显示一帧
            display.set_image(frame)

            # 拿空队列
            while frame_queue.qsize() >1 :
               frame, timestamp = frame_queue.get() 

    print("INIT:5 绑定CPU")

    # 定义一个定时器
    timer = QTimer()
    timer.timeout.connect(update_image)
    timer.start(33)  # 约 30fps


    # 添加退出处理
    def cleanup():
        print("清理资源并退出...")
        cam_control.stopCamera()

        print("cleanup1")        
        
        print("cleanup3")
        
        print("cleanup4")
        
        print("cleanup5")

        

    # 处理Ctrl+C信号
    def signal_handler(sig, frame):
        print("\n收到Ctrl+C信号，准备退出...")
        cleanup()
        sys.exit(0)
    
    

    #配置退出事件
    app.aboutToQuit.connect(cleanup)
    sys.exit(app.exec_())