




import time
import queue
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import os
import serial
import traceback
import concurrent.futures
import threading
import time
import signal
import sys

from v_com1_go import LEDController
from vedio_Init3_v4_control import CameraMonitor  #control 的意思就是核心算法

import concurrent.futures
import threading
import uuid
import time
from typing import Callable, Optional, Tuple, Any
from vedio_log_sync import TimeSyncClient
from vedio_TouchClickManager import TouchClickManager
from vedio_PerformanceStats import PerformanceStats

class Logger:
    def __init__(self, log_file):
        self.terminal = sys.stdout
        self.log = open(log_file, "a")  # "a" 表示追加模式

    def write(self, message):
        self.terminal.write(message)  # 输出到控制台
        self.log.write(message)       # 输出到文件

    def flush(self):
        self.terminal.flush()
        self.log.flush()

# 使用方法
sys.stdout = Logger("outputAA.log")

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("摄像头监控系统")
        self.root.geometry("1400x1200")

        self.client = TimeSyncClient("10.98.199.189")  # 替换为服务器IP

        self._width = 1024
        self._height = 768



        self.mse_threshold=250
        self.ssim_threshold=0.60
        self.hist_threshold=0.95
        
        #串口控制
        self.ledController = None

        #如果从这个角度来看， monitor不应该再有任何界面相关的内容了
        self.monitor = CameraMonitor(
            region = (558, 153, 586, 215),  # 示例区域，根据需要调整
            mse_threshold=self.mse_threshold,
            ssim_threshold=self.ssim_threshold,
            hist_threshold=self.hist_threshold
        )

        # 打开摄像头
        # __init__ 默认不开摄像头
        self.runningCamera = False

        #自动触发端口
        self._touchAutoClick_ = False  


        self.autoClickCount = 0
        self.click_manager = TouchClickManager(self)

        # 截图控制 1s内并发高
        self.fileSeq = 0

        # 初始化23号按钮的次数目标变量
        self.click23_Num = 1

        
        # 确认区域参数
        self.region_x1, self.region_y1 = 100, 100
        self.region_x2, self.region_y2 = 300, 300

        # 重试区域参数
        self.region_retry_x1, self.region_retry_y1 = 101, 103
        self.region_retry_x2, self.region_retry_y2 = 302, 304

        self.image_x, self.image_y = 0, 0
        
        # 从文件加载区域坐标
        self.load_region_coordinates()
        
        # 拖拽相关变量
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.dragging = False
        self.resizing = False
        self.resize_handle = None  # 0: 左上, 1: 右上, 2: 右下, 3: 左下

        self.dragging_retry = False
        self.resizing_retry = False        
        self.resize_handle_retry = None  # 0: 左上, 1: 右上, 2: 右下, 3: 左下

        
        # 创建UI组件
        self.create_widgets()
        
        # 摄像头和显示相关变量
        self.cap = None
        self.photo = None
        self.update_id = None
        self.region_id = None
        
        # 线程和队列
        # camera_capture_thread()
        # 这个线程， 读cap,         
        self.grab_queue = queue.Queue(maxsize=50000)  # 存储待解码的帧
        


        # 处理frame， 然后放入frame_queue
        # _retrieve_frames
        #self.frame_queue = queue.Queue(maxsize=50000)  # 限制队列大小，避免内存溢出
        
        self.capture_thread = None
        self.frame_lock = threading.Lock()
        self.latest_frame = None

        self.lastChangeDetected = time.time()*1000
        self.lastIn = time.time()*1000


        


        #统计相关
        self.last_stat_time = time.time()  # 帧率统计时间戳        
        self.frame_count = 0  # 总帧数计数器
        self.performance_stats = PerformanceStats()  # 创建统计实例

        #输出目录 
        self.output_dir = "screen_shot_A"

        self.latest_frame = None  # Shared variable for the latest processed frame
        self.frame_lock = threading.Lock()  # Lock for thread-safe access
        self.video_writer = None  # For video recording


        # 处理单片机队列
        self.task_queue = None
        self.thread = None

        #控制只点状态
        self.oneclickRest_flag = True
        self.oneclickRest_hasDone = False

    def load_region_coordinates(self):
        """从文件加载区域坐标"""
        file_path = "region_coordinates.txt"
        
        # 检查文件是否存在
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    line = f.readline().strip()
                    # 解析坐标
                    coords = line.split(",")
                    if len(coords) == 4:
                        self.region_x1 = int(coords[0])
                        self.region_y1 = int(coords[1])
                        self.region_x2 = int(coords[2])
                        self.region_y2 = int(coords[3])
                        print(f"已从文件加载区域坐标: ({self.region_x1}, {self.region_y1}, {self.region_x2}, {self.region_y2})")
                    else:
                        print("坐标文件格式错误，使用默认值")
            except Exception as e:
                print(f"加载坐标文件出错: {e}")
                print("使用默认区域坐标")
        else:
            print("坐标文件不存在，使用默认区域坐标")



        """从文件加载区域坐标"""
        file_path = "region_coordinates_retry.txt"
        
        # 检查文件是否存在
        if os.path.exists(file_path):
            try:
                with open(file_path, "r") as f:
                    line = f.readline().strip()
                    # 解析坐标
                    coords = line.split(",")
                    if len(coords) == 4:
                        self.region_retry_x1 = int(coords[0])
                        self.region_retry_y1 = int(coords[1])
                        self.region_retry_x2 = int(coords[2])
                        self.region_retry_y2 = int(coords[3])
                        print(f"已从文件加载区域坐标: ({self.region_retry_x1}, {self.region_retry_y1}, {self.region_retry_x2}, {self.region_retry_y2})")
                    else:
                        print("坐标文件格式错误，使用默认值")
            except Exception as e:
                print(f"加载坐标文件出错: {e}")
                print("使用默认区域坐标")
        else:
            print("坐标文件不存在，使用默认区域坐标")
    
    def save_region_coordinates(self):
        """保存区域坐标到文件"""
        file_path = "region_coordinates.txt"
        try:
            with open(file_path, "w") as f:
                f.write(f"{self.region_x1},{self.region_y1},{self.region_x2},{self.region_y2}")
            print(f"区域坐标已保存到文件: ({self.region_x1}, {self.region_y1}, {self.region_x2}, {self.region_y2})")
        except Exception as e:
            print(f"保存坐标文件出错: {e}")

        """保存区域坐标到文件"""
        file_path = "region_coordinates_retry.txt"
        try:
            with open(file_path, "w") as f:
                f.write(f"{self.region_retry_x1},{self.region_retry_y1},{self.region_retry_x2},{self.region_retry_y2}")
            print(f"区域坐标已保存到文件: ({self.region_retry_x1}, {self.region_retry_y1}, {self.region_retry_x2}, {self.region_retry_y2})")
        except Exception as e:
            print(f"保存坐标文件出错: {e}")    
    
    def create_widgets(self):


        # 顶部控制栏
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # 使用 grid 布局替代 pack
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)

        # 第一行 - 摄像头控制和串口控制
        row1_frame = ttk.Frame(control_frame)
        row1_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        
        # 摄像头控制
        camera_frame = ttk.LabelFrame(row1_frame, text="摄像头控制")
        camera_frame.pack(side=tk.LEFT, padx=5, pady=5)

        self.open_button = ttk.Button(row1_frame, text="打开摄像头", command=self.open_camera)
        self.open_button.pack(side=tk.LEFT, padx=5)
        
        self.close_button = ttk.Button(row1_frame, text="关闭摄像头", command=self.close_camera, state=tk.DISABLED)
        self.close_button.pack(side=tk.LEFT, padx=5)

        self.screen_Shot_button = ttk.Button(row1_frame, text="截屏", command=self.screen_Shot)
        self.screen_Shot_button.pack(side=tk.LEFT, padx=5)
        
        


        # 串口控制
        serial_frame = ttk.LabelFrame(row1_frame, text="串口控制")
        serial_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.serial_port_var = tk.StringVar(value="COM8")
        ttk.Label(serial_frame, text="端口:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(serial_frame, textvariable=self.serial_port_var, width=8).pack(side=tk.LEFT, padx=5)
        
        
        self.conn_Serial = ttk.Button(serial_frame, text="连接串口", command=self.connect_serial)
        self.conn_Serial.pack(side=tk.LEFT, padx=5)
        self.disconn_Serial = ttk.Button(serial_frame, text="断开串口", command=self.disconnect_serial, state=tk.DISABLED)
        self.disconn_Serial.pack(side=tk.LEFT, padx=5)

        # 监控控制
        monitor_frame = ttk.LabelFrame(row1_frame, text="监控控制")
        monitor_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.start_Touch_button = ttk.Button(monitor_frame, text="开始监控", command=self.start_monitoring)
        self.start_Touch_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_Touch_button = ttk.Button(monitor_frame, text="停止监控", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_Touch_button.pack(side=tk.LEFT, padx=5)

        self.oneClickRest_button = ttk.Button(monitor_frame, text="OneClickRest", command=self.oneClickRest, state=tk.NORMAL)
        self.oneClickRest_button.pack(side=tk.LEFT, padx=5)


        # 第二行 - 监控控制和指令控制
        row2_frame = ttk.Frame(control_frame)
        row2_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # 指令控制
        cmd_frame = ttk.LabelFrame(row2_frame, text="发送指令")
        cmd_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(cmd_frame, text="click23", command=lambda: self.send_command("click23")).pack(side=tk.LEFT, padx=5)
        ttk.Button(cmd_frame, text="back", command=lambda: self.send_command("back")).pack(side=tk.LEFT, padx=5)

        ttk.Button(cmd_frame, text="open", command=lambda: self.send_command("open")).pack(side=tk.LEFT, padx=5)
        ttk.Button(cmd_frame, text="close", command=lambda: self.send_command("close")).pack(side=tk.LEFT, padx=5)
        ttk.Button(cmd_frame, text="custom", command=self.send_custom_command).pack(side=tk.LEFT, padx=5)

        ttk.Button(cmd_frame, text="speed", command=self.send_speed_command).pack(side=tk.LEFT, padx=5)
        ttk.Button(cmd_frame, text="speed", command=self.send_thread_command).pack(side=tk.LEFT, padx=5)

        
        # 图像显示区域

        # 图像显示Canvas
        #self.canvas = tk.Canvas(self.root, bg="black", width=1000, height=600)
        #self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.display_frame = ttk.Frame(self.root)
        self.display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.canvas = tk.Canvas(
            self.display_frame, 
            bg="gray", 
            width=self._width, 
            height=self._height,
            borderwidth=0,          # 移除边框
            highlightthickness=0    # 移除高亮边框
        )
        self.canvas.pack(side=tk.TOP, fill=None, expand=False)

        # 可选：添加滚动条以处理窗口缩小时的情况
        self.scrollbar = tk.Scrollbar(self.display_frame, orient="horizontal")
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        
        # 监控信息区域
        info_frame = ttk.LabelFrame(self.root, text="监控信息")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.status_varM1 = tk.StringVar(value="自动触发状态")
        ttk.Label(info_frame, textvariable=self.status_varM1, anchor=tk.W).pack(fill=tk.X, padx=5, pady=2)

        self.status_var = tk.StringVar(value="系统状态")
        ttk.Label(info_frame, textvariable=self.status_var, anchor=tk.W).pack(fill=tk.X, padx=5, pady=2)
        
        self.metrics_var = tk.StringVar(value="差异指标: --")
        ttk.Label(info_frame, textvariable=self.metrics_var, anchor=tk.W).pack(fill=tk.X, padx=5, pady=2)
        
        self.change_var = tk.StringVar(value="变化检测: 未检测到变化")
        ttk.Label(info_frame, textvariable=self.change_var, anchor=tk.W, foreground="red").pack(fill=tk.X, padx=5, pady=2)
        
        # 监控参数设置
        param_frame = ttk.LabelFrame(self.root, text="监控参数")
        param_frame.pack(fill=tk.X, padx=10, pady=5)
        
        param_left = ttk.Frame(param_frame)
        param_left.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Label(param_left, text="点击区域 (x1,y1,x2,y2):").grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.region_var = tk.StringVar(value={self.region_x1,self.region_y1,self.region_x2,self.region_y2})
        ttk.Entry(param_left, textvariable=self.region_var, width=20).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(param_left, text="设置区域", command=self.set_region).grid(row=0, column=2, padx=5, pady=2)

        
        ttk.Label(param_left, text="重新尝试区域 (x1,y1,x2,y2):").grid(row=0, column=3, sticky=tk.W, padx=2, pady=2)
        self.region_var_Retry = tk.StringVar(value={self.region_retry_x1, self.region_retry_y1, self.region_retry_x2, self.region_retry_y2})
        ttk.Entry(param_left, textvariable=self.region_var_Retry, width=20).grid(row=0, column=4, padx=2, pady=2)
        ttk.Button(param_left, text="设置区域1", command=self.set_region).grid(row=0, column=5, padx=5, pady=2)

        
        #参数第1行
        ttk.Label(param_left, text="MSE阈值:").grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.mse_var = tk.StringVar(value="150")
        ttk.Entry(param_left, textvariable=self.mse_var, width=10).grid(row=1, column=1, padx=2, pady=2)
        
        ttk.Label(param_left, text="SSIM阈值:").grid(row=1, column=2, sticky=tk.W, padx=2, pady=2)
        self.ssim_var = tk.StringVar(value="0.85")
        ttk.Entry(param_left, textvariable=self.ssim_var, width=10).grid(row=1, column=3, padx=2, pady=2)
        
        ttk.Label(param_left, text="直方图阈值:").grid(row=1, column=4, sticky=tk.W, padx=2, pady=2)
        self.hist_var = tk.StringVar(value="0.8")
        ttk.Entry(param_left, textvariable=self.hist_var, width=10).grid(row=1, column=5, padx=2, pady=2)

        #参数第2行
        ttk.Label(param_left, text="CLCIK23 次数:").grid(row=2, column=0, sticky=tk.W, padx=2, pady=2)
        self.click23_var = tk.StringVar(value="20")
        ttk.Entry(param_left, textvariable=self.click23_var, width=10).grid(row=2, column=1, padx=2, pady=2)
        
        # 为变量添加追踪回调
        self.click23_var.trace_add("write", self.update_click23_num)

        
        ttk.Button(param_left, text="应用参数", command=self.apply_parameters).grid(row=3, column=0, columnspan=2, pady=5)


        # 区域参数显示
        param_frame = ttk.Frame(self.root)
        param_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(param_frame, text="当前区域:").pack(side=tk.LEFT, padx=5)
        self.region_label = ttk.Label(param_frame, text=f"({self.region_x1}, {self.region_y1}, {self.region_x2}, {self.region_y2})")
        self.region_label.pack(side=tk.LEFT, padx=5)

        ttk.Label(param_frame, text="重试区域:").pack(side=tk.LEFT, padx=5)
        self.region_retry_label = ttk.Label(param_frame, text=f"({self.region_retry_x1}, {self.region_retry_y1}, {self.region_retry_x2}, {self.region_retry_y2})")
        self.region_retry_label.pack(side=tk.LEFT, padx=5)
        
        # 状态显示

        self.status_varM1 = tk.StringVar(value="就1绪")
        self.status_label = ttk.Label(param_frame, textvariable=self.status_varM1)
        self.status_label.pack(side=tk.RIGHT, padx=5)


        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(param_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # 绑定鼠标事件
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
    
    #更新点击次数 回调
    def update_click23_num(self, *args):
        """当 click23_var 变化时自动调用此函数"""
        print(f"update_click23_num {args}")
        try:
            # 获取当前值并转换为整数
            value = self.click23_var.get()
            self.click23_Num = int(value)
            # 更新显示
            # self.click23_num_label.config(text=f"Click23 Num: {self.click23_Num}")
            print(f"click23_Num 已更新为: {self.click23_Num}")
        except ValueError:
            # 处理转换错误
            print("警告: 输入值无法转换为整数")

    
    def _get_region(self, frame, type=1):
        x1, x2,y1, y2 = 0, 0, 0, 0

        """提取指定监控区域"""
        # 如果type是1 就返回确认区域， 如果type是2就返回重试区域
        if type == 1 :
            x1 = self.region_x1 
            y1 = self.region_y1
            x2 = self.region_x2
            y2 = self.region_y2

        if type == 2 :
            x1 = self.region_retry_x1 
            y1 = self.region_retry_y1
            x2 = self.region_retry_x2
            y2 = self.region_retry_y2

        #print(f"_get_region type{type} >>>{x1}:{y1}:{x2}:{y2}")
        return frame[y1:y2, x1:x2]
    
    def _print_frame_statistics(self):
        """每10秒打印帧率统计"""
        current_time = time.time()
        if current_time - self.last_stat_time >= 10:
            fps = self.frame_count / (current_time - self.last_stat_time)

            msg = f"\n[统计信息]  过去{int(current_time - self.last_stat_time)}秒内共处理{self.frame_count}帧，平均帧率: {fps:.1f} FPS /  {current_time}"            
            #要确保代码有90帧
            print(msg)


            #一次点击状态
            print(f"一次点击状态 {self.oneclickRest_flag}   ：：： {self.oneclickRest_hasDone}")
            
            #统计耗时
            self.performance_stats.printStats()


            self.status_var.set(msg)
            self.frame_count = 0
            self.last_stat_time = current_time

    
        
    # 触发变化的时候，发送串口，并截屏
    # 1点击， 2截屏，3并截取区域 4.保存目录
    def touchAutoClick( self, frame, current_region,timestampIn, timpstampDiff, output_dir):
        #print(f"需要思考一下， 怎么发送指令，因为要第一事件发送指令，所以不能等截图: {self.autoClickCount}")

        autoClickCmd = 'back'
        self.autoClickCount = self.autoClickCount +1

        #到点击事件
        
        bbb = 0

        # 发送命令并获取响应
        try:
            

            if self.ledController is None:
                print(f"请连接串口")
                return
            
            #如果没有做完            
            if not self.oneclickRest_hasDone:                        
                
                #print(f"命令AUTO: {autoClickCmd}  {self.click23_Num}")
                response = self.ledController.control_led( autoClickCmd, self.click23_Num)
                #点击完成
                bbb = time.time()*1000
                print(f"响应AUTO->: {response}")
                if( "Unknown command" in response ):
                    print("touchAutoClick 单片机执行异常...\n\n\n ")
                
                
                
                # 如果是一次触发， 置标志位已经做完
                if self.oneclickRest_flag:
                    self.oneclickRest_hasDone = True


            self.client.upload_log(f"STEP3 CLICK---@{time.time()*1000}")
            
            
            interval1 = timpstampDiff - timestampIn            
            interval3 = bbb - timpstampDiff            
            interval4 = bbb - timestampIn

            # 原有打印语句（修复格式错误）
            print(f"从读取到frame到触发 耗时step1检测出差异({interval1}) step3执行点击完成({interval3}) step4总耗时({interval4})毫秒") 

            # 记录时间间隔数据
            self.performance_stats.add_sample(interval1, 0, interval3, interval4)
            
        
        except Exception as e:
            print(f"发送命令错误: {e}")
        
        self._save_screenshots(frame, current_region, timestampIn, output_dir)
        #self._print_change_log(self.mse_threshold, self.ssim_threshold, self.hist_threshold, timestamp)
        #print(f"需要思考一下， 怎么发送指令，因为要第一事件发送指令，所以不能等截图1: {self.autoClickCount}")

    def on_touchAutoClick_ok( self,frame, current_region, output_dir):
        print(f"on_touchAutoClick_ok 干后续的吧: ")


    # 异步方法，被单片机处理线程调用
    def _process_touch_tasks(self):
        while True:
            try:
                # 获取任务（带超时，避免永久阻塞）
                task = self.task_queue.get(timeout=1)
                if task is None:  # 退出信号
                    break
                #print("_process_touch_tasks 拿到任务了...")
                # 执行任务
                func, args = task
                func(*args)
                self.task_queue.task_done()
            except queue.Empty:
                continue

    # 计算帧差异， 二级方法， 嵌套在retrieve_frames线程中
    # 我需要的时间：1.从摄像头读出， 2.检测出变化， 3.按钮发送
    # 这里是第二步的时间；
    def _calculateDiff(self, frameFull, timestampIn, output_dir ):

        # print(f"\n开始监控 - 阈值设置:")
        # print(f"MSE > {self.mse_threshold}, SSIM < {self.ssim_threshold}, 直方图相似度 < {self.hist_threshold}")
        # print(f"按ESC键退出,窗口可显示实时监控画面\n")

        # 不停的拿出frame
        current_region = self._get_region(frameFull)
        

        # 仅在有前一帧时进行变化检测
        if self.prev_frame is not None:
            mse, ssim_val, hist_sim = self.monitor._calculate_metrics(current_region, self.prev_frame )

            isChange = self.monitor._check_changes(mse, ssim_val, hist_sim)                
            if self._touchAutoClick_ and isChange:
                #调用自动执行代码
                print(f"检查到变化...{mse} {ssim_val} {hist_sim}")
                aaa = time.time()*1000
                
                interval1 = aaa - timestampIn
                interval2 = timestampIn - self.lastIn
                interval3 = aaa-self.lastChangeDetected

                print(f"python耗时...{interval1}毫秒  距离上次In 时间 {interval2}毫秒  距上次变化{interval3}毫秒")
                
                self.lastChangeDetected = aaa
                self.lastIn = timestampIn   

                                
                # 将任务放入队列，由后台线程处理
                self.task_queue.put((self.touchAutoClick, (frameFull, current_region, timestampIn, aaa, output_dir)))
                self.client.upload_log(f"STEP2 _DIFF---@{time.time()*1000}")
                

        # 计算完成后， 更新前一帧
        self.prev_frame = current_region.copy()  # 更新前一帧

    # 二级方法， 
    # 嵌套在 camera_capture_thread 方法中
    def _movieRecord(self, frame, timestampIn,output_dir):

        #只有启动监控的时候， 才录
        # 判断是否启动监控            
        if self._touchAutoClick_ :
            print("记录当前帧吗")
            # 记录当前帧
            self._save_Movie(frame, timestampIn, output_dir)
            
    # Replace the update_frame thread with a main-thread function:
    def update_gui(self):
        if self.runningCamera:
            with self.frame_lock:
                if self.latest_frame is not None:
                    self._update_frame_draw(self.latest_frame)
            self.root.after(100, self.update_gui)  # Update every 100ms
            
    
    # 这个线程， 读grab_queue, 然后放入frame_queue
    # 我需要的时间：1.从摄像头读出， 2.检测出变化， 3.按钮发送
    
    def retrieve_frames(self):
        # _retrieve_frames_count = 0
        while self.runningCamera:
            try:
                # _retrieve_frames_count += 1
                # if _retrieve_frames_count % 1000 == 0:
                #     print(f"retrieve帧数 ->1: {self.grab_queue.qsize()} ")

                # 从grab队列获取任务
                frame, timestampIn = self.grab_queue.get(timeout=1)

                # 处理图片差异；
                # 放入完整frame
                self._calculateDiff(frame, timestampIn, self.output_dir)

                # Update latest_frame for GUI
                with self.frame_lock:
                    self.latest_frame = frame.copy()
                
                # Record to video if monitoring is active
                #if self._touchAutoClick_ and self.video_writer:
                #    self.video_writer.write(frame)
                    
            except queue.Empty:
                # print("_grab队列为空")
                pass

        print(f"retrieve_frames 线程已停止")

    
    
    # 读取帧
    # 我需要的时间：1.从摄像头读出， 2.检测出变化， 3.按钮发送
    def camera_capture_thread(self, output_dir="screenshots"):
      

        """摄像头捕获线程函数"""
        # countA = 0 
        while self.runningCamera and self.cap.isOpened():
            
            #第2次读，循环读
            ret, frame = self.cap.read()
            #在这里，启动一个新的线程， 然后把FRAME，timestamp放入队列

            if ret:
                timestampIn = int(time.time() * 1000)
                self.grab_queue.put((frame, timestampIn))

            # 帧数统计+= 1  # 帧数统计
            self.frame_count = self.frame_count + 1
            
            # countA = countA +1
            # if countA % 1000 == 0 :
            #    print(f" camera_capture_thread read frame size {countA} queue size {self.grab_queue.qsize()}")
            
            if not ret:
                print("错误：无法获取摄像头帧")
                break            

            # 每10秒统计帧率
            self._print_frame_statistics()

        print(f"camera_capture_thread 线程已停止")

    # # 第3个线程， 更新界面， 和录像
    # def update_frame(self):

    #     countUpdateFrame = 0

    #     while self.runningCamera:

            
    #         # 尝试从队列获取最新帧
    #         frame = None
    #         try:
    #             # 非阻塞方式获取帧
    #             if not self.frame_queue.empty():
    #                 while( self.frame_queue.qsize() > 1):   
    #                     countUpdateFrame += 1

    #                     frame,timestampIn = self.frame_queue.get_nowait()
    #                     #录像
    #                     self._movieRecord(frame, timestampIn, self.output_dir)

    #                     # 更新画面 10帧更新一次画面
    #                     if countUpdateFrame % 10 == 0:
    #                         self._update_frame_draw(frame)
    #         except queue.Empty:
    #             # 队列为空，使用共享变量中的最新帧
    #             with self.frame_lock:
    #                 frame = self.latest_frame
            
            

        print(f"update_frame 线程已停止")


    def connect_serial(self, port="COM8"):
        print("\n connect_serial \n")
        try:
            if not self.ledController:
                self.ledController = LEDController(port)    
                self.status_var.set(f"已连接到串口 {port}")
                messagebox.showinfo("成功", f"已连接到串口 {port}")


                self.conn_Serial.config(state=tk.DISABLED)
                self.disconn_Serial.config(state=tk.NORMAL)

        except Exception as e:
            print(f"错误: {str(e)}")
            messagebox.showerror("错误", f"连接串口 {port} 失败")
            self.status_var.set(f"连接串口 {port} 失败")

    
    def disconnect_serial(self):
        print("\n disconnect_serial \n")

        try:
            self.ledController.close()      
            print("关闭串口...")  

            self.ledController = None
        except Exception as e:
            print(f"错误: {str(e)}")
            # 关闭连接
        
        self.status_var.set("串口已断开")
        self.conn_Serial.config(state=tk.NORMAL)
        self.disconn_Serial.config(state=tk.DISABLED)
        
        


    def start_monitoring(self):
        #简单， 设置一个参数， 为True, 当变化，就触发
        self._touchAutoClick_ = True
        self.status_varM1.set("自动触发点击 打开")
        self.start_Touch_button.config(state=tk.DISABLED)
        self.stop_Touch_button.config(state=tk.NORMAL)

        self.task_queue = queue.Queue()
        self.thread = threading.Thread(target=self._process_touch_tasks, daemon=True)
        self.thread.start()
        print("启动单片机线程")

        # Initialize VideoWriter
        # fourcc = cv2.VideoWriter_fourcc(*'XVID')
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # video_path = f"{self.output_dir}/movie_{timestamp}.avi"
        # self.video_writer = cv2.VideoWriter(video_path, fourcc, 30.0, (self._width, self._height))
        # print(f"Started recording to {video_path}")


    def stop_monitoring(self):
        #简单， 设置一个参数， 为False, 当变化，就不触发。 
        self._touchAutoClick_ = False
        self.status_varM1.set("自动触发点击 关闭")
        self.start_Touch_button.config(state=tk.NORMAL)
        self.stop_Touch_button.config(state=tk.DISABLED)

        # 停止后台线程
        self.task_queue.put(None)  # 发送退出信号
        self.thread.join(timeout=2)  # 等待线程结束
        print("停止单片机线程")
        
        # if self.video_writer:
        #     self.video_writer.release()
        #     self.video_writer = None
        #     print("Stopped recording")
        print("\n stop_monitoring \n")

    # OneClickRest
    def oneClickRest(self):

        
        self.oneclickRest_flag = not self.oneclickRest_flag
        self.oneclickRest_hasDone = False

        print(f"Rest OneClickRest triggered {self.oneclickRest_flag} {self.oneclickRest_hasDone}")
        if(self.oneclickRest_flag):
            print("只触发一次")
        else:
            print("每次差异都触发")

        
        self.performance_stats.clear()
        print("已清空性能统计数据")

        self.oneClickRest_button.config(text=f"OneClickRest {self.oneclickRest_flag}")

    def send_command(self,cmd):

        print(f"\n send_command {self.ledController}\n")
        if self.ledController:
            response = self.ledController.control_led(cmd)
            self.status_var.set(f"发送指令: {cmd}, 响应: {response}")
            if "Unknown command" in response:
                print("send_command 异常 未知指令\n\n")
        else:
            messagebox.showerror("错误", "请先连接串口")

    def send_custom_command(self):
        print("\n send_custom_command \n")
        cmd = simpledialog.askstring("自定义指令", "请输入要发送的指令:")
        
        try:
            num = int(cmd)  # 尝试转换为整数
            autoClickCmd = "back"
            aaa = time.time()*1000
            
            print(f"send_custom_command {autoClickCmd}->{cmd} ")
            response = self.ledController.control_led( autoClickCmd, num)
            
            #点击完成
            bbb = time.time()*1000
            
            print(f"响应AUTO->: {response}   {bbb-aaa}")
            if( "Unknown command" in response ):
                print("touchAutoClick 单片机执行异常...\n\n\n ")

        except ValueError:
            print(f"错误：无法将参数 {num} 转换为整数")
            return

            

    def send_speed_command( self ):
        print("\n ****send_speed_command**** \n")
        if self.ledController:
            current_timeA = time.time()
            response = self.ledController.control_led("speed")
            current_timeB = time.time()
            self.status_var.set(f"发送指令: speed, 响应: {response}")
            print(f"单片机 速度 {current_timeB-current_timeA}")

        else:
            messagebox.showerror("错误", "请先连接串口")

        print("\n ****send_speed_command**** \n")

    def send_thread_command( self ):
        print("\n ****send_thread_command**** \n")
        # 获取当前进程中的所有活动线程
        threads = threading.enumerate()
        # 打印线程数量
        print(f"当前进程中的线程数量: {len(threads)}")

        # 可选：打印每个线程的名称和 ID
        for thread in threads:
            print(f"线程名称: {thread.name}, 线程 ID: {thread.ident}")

        print("\n ****send_thread_command**** \n")


    def set_region(self):
        print("\n set_region \n")

    def apply_parameters(self):
        print("\n apply_parameters \n")



    # 当打开摄像头， 就开始不同的扫描图案了
    def open_camera(self):
        # 打开摄像头
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        # 尝试设置高帧率
        if self.cap.isOpened():
            # 尝试设置为200FPS（根据摄像头支持情况）

            desired_fps = 120  # 目标帧率
            self.cap.set(cv2.CAP_PROP_FPS, desired_fps)



            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
            
            # 设置为MJPEG格式
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            self.cap.set(cv2.CAP_PROP_FOURCC, fourcc)
            
            #确认分辨率
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"摄像头已打开，分辨率设置为: {actual_width}x{actual_height}")
            

            #确认帧率
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            print(f"摄像头帧率设置为: {actual_fps} FPS")

            # 确认格式
            actual_fourcc = int(self.cap.get(cv2.CAP_PROP_FOURCC))
            print(f"摄像头格式设置为: {actual_fourcc} ")

            #第1次读；
            ret, frame = self.cap.read()
            if not ret:
                raise ValueError("无法获取摄像头初始帧")                
            self.prev_frame = self._get_region(frame)
            
            
            
            # 更新UI状态
            self.runningCamera = True
            self.open_button.config(state=tk.DISABLED)
            self.close_button.config(state=tk.NORMAL)
            self.status_var.set(f"摄像头已打开 ({actual_fps} FPS)")
            
            
            #启动三个线程：
            # 摄像头捕获线程
            self.capture_thread = threading.Thread(target=self.camera_capture_thread)
            self.capture_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
            self.capture_thread.start()
            print(f"## 摄像头捕获线程已启动 1/3# ")


            # 帧处理线程
            self.process_thread = threading.Thread(target=self.retrieve_frames)
            self.process_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
            self.process_thread.start()
            print(f"## 帧处理线程已启动 2/3# ")

            # 现实和录像线程
            
            # self.ui_update_thread = threading.Thread(target=self.update_frame)
            # self.ui_update_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
            # self.ui_update_thread.start()
            
            # Start GUI updates in main thread
            self.update_gui()
            print(f"## UI 更新线程已启动 3/3# ")

        else:
            tk.messagebox.showerror("错误", "无法打开摄像头")
    
    def close_camera(self):
        
        # 停止更新并释放资源
        # camera_capture_thread
        # 开启摄像头 
        self.runningCamera = False


        # 等待捕获线程结束
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)

        if self.process_thread and self.process_thread.is_alive():
            self.process_thread.join(timeout=1.0)
        
        
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
        
        
        
        
        # 释放摄像头
        if self.cap and self.cap.isOpened():
            self.cap.release()
        
        # 清空Canvas
        self.canvas.delete("all")
        
        # 更新UI状态
        self.open_button.config(state=tk.NORMAL)
        self.close_button.config(state=tk.DISABLED)
        self.status_var.set("就绪")
    
    
    
    
    # 这个是给 截屏 按钮使用的
    def screen_Shot( self, output_dir="screenshots" ):

        

        #去缓存拿一下；

        # 尝试从队列获取最新帧
        # frame = None
        # try:
        #     # 非阻塞方式获取帧
        #     if not self.frame_queue.empty():
        #         frame = self.frame_queue.get_nowait()
        #     else:
        #         # 如果队列为空，使用共享变量中的最新帧
        #         with self.frame_lock:
        #             frame = self.latest_frame
        # except queue.Empty:
        #     # 队列为空，使用共享变量中的最新帧
        #     with self.frame_lock:
        #         frame = self.latest_frame
        
        if self.latest_frame is not None:

            #如果一秒钟有多个文件，可能会重复
            self.fileSeq = self.fileSeq +1

            """保存带标注的全屏截图和区域截图"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            full_path = f"{output_dir}/fullscreen_{timestamp}_{self.fileSeq}.jpg"
            region_path = f"{output_dir}/region_{timestamp}_{self.fileSeq}.jpg"
            cv2.imwrite(full_path, self.latest_frame)
            cv2.imwrite(region_path, self._get_region(self.latest_frame))
            print(fr"手动截屏至 \n1{full_path} \n2{region_path}")
            
        
    # 只负责画，不控制
    def _update_frame_draw(self, frame):
        if frame is not None:
            # 转换为RGB格式
            # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


            # 不转化，看看是否可以
            frame_rgb = frame

            # 调整尺寸以适应Canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            #print(f"调整尺寸以适应Canvas {canvas_width} , {canvas_height} ")
            
            # 保持比例缩放
            frame_height, frame_width = frame_rgb.shape[:2]
            ratio = min(canvas_width / frame_width, canvas_height / frame_height)
            new_width = int(frame_width * ratio)
            new_height = int(frame_height * ratio)
            
            # 计算显示位置
            self.image_x = 0 // 2
            self.image_y = 0 // 2
            
            # 计算区域在缩放后图像上的位置
            #scaled_x1 = int(self.region_x1 * ratio) + self.image_x
            #scaled_y1 = int(self.region_y1 * ratio) + self.image_y
            #scaled_x2 = int(self.region_x2 * ratio) + self.image_x
            #scaled_y2 = int(self.region_y2 * ratio) + self.image_y

            scaled_x1 = int(self.region_x1)
            scaled_y1 = int(self.region_y1)
            scaled_x2 = int(self.region_x2)
            scaled_y2 = int(self.region_y2)

            scaled_retry_x1 = int(self.region_retry_x1)
            scaled_retry_y1 = int(self.region_retry_y1)
            scaled_retry_x2 = int(self.region_retry_x2)
            scaled_retry_y2 = int(self.region_retry_y2)

            
            # 只有当需要缩小时才执行缩放
            if ratio < 1:
                frame_rgb = cv2.resize(frame_rgb, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # 转换为PhotoImage并显示
            self.photo = tk.PhotoImage(data=cv2.imencode('.ppm', frame_rgb)[1].tobytes())
            
            # 清除之前的所有内容
            self.canvas.delete("all")
            
            # 显示图像
            self.canvas.create_image(self.image_x, self.image_y, image=self.photo, anchor=tk.NW, tags="image")
            
            # 绘制监控区域
            # 红色，主监控区
            self.region_id = self.canvas.create_rectangle(
                scaled_x1, scaled_y1, scaled_x2, scaled_y2,
                outline="red", width=1, tags="region"
            )

            self.region_retry_id = self.canvas.create_rectangle(
                scaled_retry_x1, scaled_retry_y1, scaled_retry_x2, scaled_retry_y2,
                outline="yellow", width=1, tags="retry"
            )


            
            # 绘制调整手柄A
            handle_size = 6
            self.canvas.create_rectangle(
                scaled_x1 - handle_size, scaled_y1 - handle_size,
                scaled_x1 + handle_size, scaled_y1 + handle_size,
                fill="blue", outline="white", tags="handle"
            )
            self.canvas.create_rectangle(
                scaled_x2 - handle_size, scaled_y1 - handle_size,
                scaled_x2 + handle_size, scaled_y1 + handle_size,
                fill="blue", outline="white", tags="handle"
            )
            self.canvas.create_rectangle(
                scaled_x2 - handle_size, scaled_y2 - handle_size,
                scaled_x2 + handle_size, scaled_y2 + handle_size,
                fill="blue", outline="white", tags="handle"
            )
            self.canvas.create_rectangle(
                scaled_x1 - handle_size, scaled_y2 - handle_size,
                scaled_x1 + handle_size, scaled_y2 + handle_size,
                fill="blue", outline="white", tags="handle"
            )



            # 绘制调整手柄B
            handle_size = 6
            self.canvas.create_rectangle(
                scaled_retry_x1 - handle_size, scaled_retry_y1 - handle_size,
                scaled_retry_x1 + handle_size, scaled_retry_y1 + handle_size,
                fill="blue", outline="white", tags="handle"
            )
            self.canvas.create_rectangle(
                scaled_retry_x2 - handle_size, scaled_retry_y1 - handle_size,
                scaled_retry_x2 + handle_size, scaled_retry_y1 + handle_size,
                fill="blue", outline="white", tags="handle"
            )
            self.canvas.create_rectangle(
                scaled_retry_x2 - handle_size, scaled_retry_y2 - handle_size,
                scaled_retry_x2 + handle_size, scaled_retry_y2 + handle_size,
                fill="blue", outline="white", tags="handle"
            )
            self.canvas.create_rectangle(
                scaled_retry_x1 - handle_size, scaled_retry_y2 - handle_size,
                scaled_retry_x1 + handle_size, scaled_retry_y2 + handle_size,
                fill="blue", outline="white", tags="handle"
            )
            
            # 更新区域参数显示
            self.region_label.config(text=f"({self.region_x1}, {self.region_y1}, {self.region_x2}, {self.region_y2})")

            # 更新区域TODO参数显示
            self.region_retry_label.config(text=f"({self.region_retry_x1}, {self.region_retry_y1}, {self.region_retry_x2}, {self.region_retry_y2})")
       

    
    

    def on_mouse_down(self, event):
        """鼠标按下事件处理"""
        # 获取鼠标在Canvas上的位置
        x, y = event.x, event.y
        
        # 检查是否点击了调整手柄
        handle_size = 6
        scaled_x1 = int(self.region_x1 * self.get_ratio()) + self.image_x
        scaled_y1 = int(self.region_y1 * self.get_ratio()) + self.image_y
        scaled_x2 = int(self.region_x2 * self.get_ratio()) + self.image_x
        scaled_y2 = int(self.region_y2 * self.get_ratio()) + self.image_y


        scaled_retry_x1 = int(self.region_retry_x1 * self.get_ratio()) + self.image_x
        scaled_retry_y1 = int(self.region_retry_y1 * self.get_ratio()) + self.image_y
        scaled_retry_x2 = int(self.region_retry_x2 * self.get_ratio()) + self.image_x
        scaled_retry_y2 = int(self.region_retry_y2 * self.get_ratio()) + self.image_y


        
        # 检查四个角的手柄
        if abs(x - scaled_x1) < handle_size and abs(y - scaled_y1) < handle_size:
            self.resizing = True
            self.resize_handle = 0  # 左上角
        elif abs(x - scaled_x2) < handle_size and abs(y - scaled_y1) < handle_size:
            self.resizing = True
            self.resize_handle = 1  # 右上角
        elif abs(x - scaled_x2) < handle_size and abs(y - scaled_y2) < handle_size:
            self.resizing = True
            self.resize_handle = 2  # 右下角
        elif abs(x - scaled_x1) < handle_size and abs(y - scaled_y2) < handle_size:
            self.resizing = True
            self.resize_handle = 3  # 左下角
        # 检查是否点击了区域内部（用于拖拽）
        elif scaled_x1 <= x <= scaled_x2 and scaled_y1 <= y <= scaled_y2:
            self.dragging = True

        # 检查四个角的手柄
        if abs(x - scaled_retry_x1) < handle_size and abs(y - scaled_retry_y1) < handle_size:
            self.resizing_retry = True
            self.resize_handle_retry = 0  # 左上角
        elif abs(x - scaled_retry_x2) < handle_size and abs(y - scaled_retry_y1) < handle_size:
            self.resizing_retry = True
            self.resize_handle_retry = 1  # 右上角
        elif abs(x - scaled_retry_x2) < handle_size and abs(y - scaled_retry_y2) < handle_size:
            self.resizing_retry = True
            self.resize_handle_retry = 2  # 右下角
        elif abs(x - scaled_retry_x1) < handle_size and abs(y - scaled_retry_y2) < handle_size:
            self.resizing_retry = True
            self.resize_handle_retry = 3  # 左下角
        # 检查是否点击了区域内部（用于拖拽）
        elif scaled_retry_x1 <= x <= scaled_retry_x2 and scaled_retry_y1 <= y <= scaled_retry_y2:
            self.dragging_retry = True
        
        # 记录起始位置
        self.drag_start_x = x
        self.drag_start_y = y
    
    def on_mouse_drag(self, event):
        """鼠标拖拽事件处理"""
        #print("here **")
        if not self.runningCamera or not (self.dragging or self.resizing or self.dragging_retry or self.resizing_retry):
            print("here ??")
            return
        
        # 获取当前鼠标位置
        x, y = event.x, event.y
        dx, dy = x - self.drag_start_x, y - self.drag_start_y
        
        # 获取图像缩放比例
        ratio = 1
        
        if self.dragging:
            #print(">>> on_mouse_drag >>> self.dragging")
            # 拖拽整个区域
            new_x1 = self.region_x1 + int(dx / ratio)
            new_y1 = self.region_y1 + int(dy / ratio)
            new_x2 = self.region_x2 + int(dx / ratio)
            new_y2 = self.region_y2 + int(dy / ratio)
            
            # 确保区域在图像范围内
            frame_width, frame_height = self.get_frame_size()
            new_x1 = max(0, min(new_x1, frame_width - 10))
            new_y1 = max(0, min(new_y1, frame_height - 10))
            new_x2 = max(10, min(new_x2, frame_width))
            new_y2 = max(10, min(new_y2, frame_height))
            
            # 确保区域有最小尺寸
            if new_x2 - new_x1 < 10:
                new_x2 = new_x1 + 10
            if new_y2 - new_y1 < 10:
                new_y2 = new_y1 + 10
            
            # 更新区域参数
            self.region_x1, self.region_y1 = new_x1, new_y1
            self.region_x2, self.region_y2 = new_x2, new_y2
        
        elif self.resizing:
            #print(f">>> on_mouse_drag >>> self.resizing {self.resizing}")
            # 调整区域大小
            if self.resize_handle == 0:  # 左上角
                new_x1 = self.region_x1 + int(dx / ratio)
                new_y1 = self.region_y1 + int(dy / ratio)
                
                # 确保区域在图像范围内且有最小尺寸
                frame_width, frame_height = self.get_frame_size()
                new_x1 = max(0, min(new_x1, self.region_x2 - 10))
                new_y1 = max(0, min(new_y1, self.region_y2 - 10))
                
                # 更新区域参数
                self.region_x1, self.region_y1 = new_x1, new_y1
            
            elif self.resize_handle == 1:  # 右上角
                new_x2 = self.region_x2 + int(dx / ratio)
                new_y1 = self.region_y1 + int(dy / ratio)
                
                # 确保区域在图像范围内且有最小尺寸
                frame_width, frame_height = self.get_frame_size()
                new_x2 = max(10, min(new_x2, frame_width))
                new_y1 = max(0, min(new_y1, self.region_y2 - 10))
                
                # 更新区域参数
                self.region_x2, self.region_y1 = new_x2, new_y1
            
            elif self.resize_handle == 2:  # 右下角
                new_x2 = self.region_x2 + int(dx / ratio)
                new_y2 = self.region_y2 + int(dy / ratio)
                
                # 确保区域在图像范围内且有最小尺寸
                frame_width, frame_height = self.get_frame_size()
                new_x2 = max(10, min(new_x2, frame_width))
                new_y2 = max(10, min(new_y2, frame_height))
                
                # 更新区域参数
                self.region_x2, self.region_y2 = new_x2, new_y2
            
            elif self.resize_handle == 3:  # 左下角
                new_x1 = self.region_x1 + int(dx / ratio)
                new_y2 = self.region_y2 + int(dy / ratio)
                
                # 确保区域在图像范围内且有最小尺寸
                frame_width, frame_height = self.get_frame_size()
                new_x1 = max(0, min(new_x1, self.region_x2 - 10))
                new_y2 = max(10, min(new_y2, frame_height))
                
                # 更新区域参数
                self.region_x1, self.region_y2 = new_x1, new_y2
        


        if self.dragging_retry:
            # print(">>> on_mouse_drag >>> self.dragging_retry")
            # 拖拽整个区域
            new_x1 = self.region_retry_x1 + int(dx / ratio)
            new_y1 = self.region_retry_y1 + int(dy / ratio)
            new_x2 = self.region_retry_x2 + int(dx / ratio)
            new_y2 = self.region_retry_y2 + int(dy / ratio)
            
            # 确保区域在图像范围内
            frame_width, frame_height = self.get_frame_size()
            new_x1 = max(0, min(new_x1, frame_width - 10))
            new_y1 = max(0, min(new_y1, frame_height - 10))
            new_x2 = max(10, min(new_x2, frame_width))
            new_y2 = max(10, min(new_y2, frame_height))
            
            # 确保区域有最小尺寸
            if new_x2 - new_x1 < 10:
                new_x2 = new_x1 + 10
            if new_y2 - new_y1 < 10:
                new_y2 = new_y1 + 10
            
            # 更新区域参数
            self.region_retry_x1, self.region_retry_y1 = new_x1, new_y1
            self.region_retry_x2, self.region_retry_y2 = new_x2, new_y2
        
        elif self.resizing_retry:
            # print(f">>> on_mouse_drag >>> self.resizing_retry {self.resize_handle_retry}")
            # 调整区域大小
            if self.resize_handle_retry == 0:  # 左上角
                new_x1 = self.region_retry_x1 + int(dx / ratio)
                new_y1 = self.region_retry_y1 + int(dy / ratio)
                
                # 确保区域在图像范围内且有最小尺寸
                frame_width, frame_height = self.get_frame_size()
                new_x1 = max(0, min(new_x1, self.region_retry_x2 - 10))
                new_y1 = max(0, min(new_y1, self.region_retry_y2 - 10))
                
                # 更新区域参数
                self.region_retry_x1, self.region_retry_y1 = new_x1, new_y1
            
            elif self.resize_handle_retry == 1:  # 右上角
                new_x2 = self.region_retry_x2 + int(dx / ratio)
                new_y1 = self.region_retry_y1 + int(dy / ratio)
                
                # 确保区域在图像范围内且有最小尺寸
                frame_width, frame_height = self.get_frame_size()
                new_x2 = max(10, min(new_x2, frame_width))
                new_y1 = max(0, min(new_y1, self.region_retry_y2 - 10))
                
                # 更新区域参数
                self.region_retry_x2, self.region_retry_y1 = new_x2, new_y1
            
            elif self.resize_handle_retry == 2:  # 右下角
                new_x2 = self.region_retry_x2 + int(dx / ratio)
                new_y2 = self.region_retry_y2 + int(dy / ratio)
                
                # 确保区域在图像范围内且有最小尺寸
                frame_width, frame_height = self.get_frame_size()
                new_x2 = max(10, min(new_x2, frame_width))
                new_y2 = max(10, min(new_y2, frame_height))
                
                # 更新区域参数
                self.region_retry_x2, self.region_retry_y2 = new_x2, new_y2
            
            elif self.resize_handle_retry == 3:  # 左下角
                new_x1 = self.region_retry_x1 + int(dx / ratio)
                new_y2 = self.region_retry_y2 + int(dy / ratio)
                
                # 确保区域在图像范围内且有最小尺寸
                frame_width, frame_height = self.get_frame_size()
                new_x1 = max(0, min(new_x1, self.region_retry_x2 - 10))
                new_y2 = max(10, min(new_y2, frame_height))
                
                # 更新区域参数
                self.region_retry_x1, self.region_retry_y2 = new_x1, new_y2

        # 记录当前位置作为新的起始位置
        self.drag_start_x, self.drag_start_y = x, y
    
    def on_mouse_up(self, event):
        """鼠标释放事件处理"""
        #print(">>> on_mouse_up")
        # 检查是否发生了拖拽或调整大小
        if self.dragging or self.resizing:
            #print(f">>> on_mouse_up {self.dragging} { self.resizing}")    
            
            # 打印区域坐标
            #print(f"区域坐标已更新: ({self.region_x1}, {self.region_y1}, {self.region_x2}, {self.region_y2})")
            # 在配置区显示

            msg = fr"A{self.region_x1},  A {self.region_y1}, A {self.region_x2}, A {self.region_y2}"

            self.region_var.set( msg )
            # 在UI上显示消息
            self.status_var.set(f"区域已更新: ({self.region_x1}, {self.region_y1}, {self.region_x2}, {self.region_y2})")
            
            # 保存坐标到文件
            self.save_region_coordinates()
            
            
            
            # 3秒后恢复原始状态
            #self.root.after(3000, lambda: self.status_var.set(f"摄像头已打开 ({self.cap.get(cv2.CAP_PROP_FPS)} FPS)"))
        
            self.dragging = False
            self.resizing = False

        # 检查是否发生了拖拽或调整大小
        if self.dragging_retry or self.resizing_retry:
            #print(f">>> on_mouse_up {self.dragging_retry} { self.resizing_retry}")    

            # 打印区域坐标
            #print(f"区域坐标已更新: ({self.region_retry_x1}, {self.region_retry_y1}, {self.region_retry_x2}, {self.region_retry_y2})")
            # 在配置区显示

            msg = fr"{self.region_retry_x1},  {self.region_retry_y1}, {self.region_retry_x2}, {self.region_retry_y2}"

            self.region_var.set( msg )
            # 在UI上显示消息
            self.status_var.set(f"区域已更新: ({self.region_retry_x1}, {self.region_retry_y1}, {self.region_retry_x2}, {self.region_retry_y2})")
            
            # 保存坐标到文件
            self.save_region_coordinates()
                       
            
            # 3秒后恢复原始状态
            #self.root.after(3000, lambda: self.status_var.set(f"摄像头已打开 ({self.cap.get(cv2.CAP_PROP_FPS)} FPS)"))
        
            self.dragging_retry = False
            self.resizing_retry = False

    
    def get_ratio(self):
        """获取图像缩放比例"""
        # if not self.cap or not self.cap.isOpened():
        #     return 1.0
        
        # # 获取摄像头帧尺寸
        # frame_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        # frame_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        # # 获取Canvas尺寸
        # canvas_width = self.canvas.winfo_width()
        # canvas_height = self.canvas.winfo_height()
        
        # # 计算缩放比例
        # return min(canvas_width / frame_width, canvas_height / frame_height)

        return  1
    
    def get_frame_size(self):
        """获取原始摄像头帧尺寸"""
        if not self.cap or not self.cap.isOpened():
            return self._width, self._height  # 默认尺寸
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f"获取原始摄像头帧尺寸 ({width },{height} )" )
        return width, height
    
    def on_closing(self):

        self.runningCamera = False
        self.close_camera()        
        self.root.destroy()


    # 保存录像, 带时间戳
    def _save_Movie(self, full_frame, timestamp, output_dir="Movie"):
        """保存带标注的全屏截图和区域截图"""
        self.fileSeq = self.fileSeq +1
        movie_path = f"{output_dir}/Movie_{timestamp}_{self.fileSeq}.jpg"        
        cv2.imwrite(movie_path, full_frame)
        

    # 保存截图, 带时间戳
    def _save_screenshots(self, full_frame, current_region, timestamp, output_dir):
        """保存带标注的全屏截图和区域截图"""
        self.fileSeq = self.fileSeq +1
        full_path = f"{output_dir}/fullscreen_{timestamp}_{self.fileSeq}.jpg"
        region_path = f"{output_dir}/region_{timestamp}_{self.fileSeq}.jpg"
        cv2.imwrite(full_path, full_frame)
        cv2.imwrite(region_path, current_region)

    def _print_change_log(self, mse, ssim_val, hist_sim, timestamp):

        """打印变化日志"""
        print(f"\n[检测到变化 @ {timestamp}]")
        print(f"mse_threshold: MSE阈值，超过此值视为有变化")
        print(f"ssim_threshold: SSIM阈值，低于此值视为有变化")
        print(f"hist_threshold: 直方图相似度阈值，低于此值视为有变化")

        print(f"MSE: {mse:.2f} (阈值: {self.mse_threshold}) ")
        print(f"SSIM: {ssim_val:.2f} (阈值: {self.ssim_threshold})")
        print(f"直方图相似度: {hist_sim:.2f} (阈值: {self.hist_threshold}) | 已保存截图")


def signal_handler(sig, frame):
    """信号处理函数，处理Ctrl+C"""
    print("\n接收到Ctrl+C信号，正在退出...")
    app.exiting = True
    app.close_camera()
    root.destroy()
    sys.exit(0)

if __name__ == "__main__":

    # 注册信号处理函数
    signal.signal(signal.SIGINT, signal_handler)


    root = tk.Tk()
    app = CameraApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()