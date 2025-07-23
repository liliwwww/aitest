




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


from v_com1_go import LEDController
from vedio_Init3_v4_control import CameraMonitor  #control 的意思就是核心算法

class TouchClickManager:
    """异步调用 touchAutoClick 方法的管理器"""
    
    def __init__(self, app_instance, max_workers=5):
        """
        初始化 TouchClickManager
        
        参数:
            app_instance: MainApplication 实例，包含 touchAutoClick 方法
            max_workers: 线程池最大工作线程数
        """
        self.app = app_instance
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.lock = threading.Lock()
        self.active_tasks = {}  # 跟踪活跃任务
        self.next_task_id = 1
        
    def touch_auto_click_async(self, frame, current_region, output_dir, callback=None):
        """
        异步调用 touchAutoClick 方法
        
        参数:
            frame: 视频帧
            current_region: 目标区域坐标
            output_dir: 输出目录
            callback: 任务完成时的回调函数，接收 (task_id, success, result) 参数
            
        返回:
            task_id: 任务唯一标识符
        """
        # 生成唯一任务ID
        with self.lock:
            task_id = self.next_task_id
            self.next_task_id += 1
        
        # 提交任务到线程池
        future = self.executor.submit(
            self._run_touch_auto_click,
            task_id, frame, current_region, output_dir, callback
        )
        
        # 记录活跃任务
        with self.lock:
            self.active_tasks[task_id] = future
            
        return task_id
    
    def _run_touch_auto_click(self, task_id, frame, current_region, output_dir, callback):
        """在线程池中运行 touchAutoClick 方法"""
        try:
            # 调用 MainApplication 的 touchAutoClick 方法
            result = self.app.touchAutoClick(frame, current_region, output_dir)
            
            # 任务完成，从活跃列表中移除
            with self.lock:
                self.active_tasks.pop(task_id, None)
                
            # 执行回调（如果提供）
            if callback and callable(callback):
                callback(task_id, True, result)
                
            return result
            
        except Exception as e:
            # 任务异常，从活跃列表中移除
            with self.lock:
                self.active_tasks.pop(task_id, None)
                
            # 执行回调（如果提供）
            if callback and callable(callback):
                callback(task_id, False, str(e))
                
            return False
    
    def get_active_tasks_count(self):
        """获取当前活跃任务数量"""
        with self.lock:
            return len(self.active_tasks)
    
    def cancel_task(self, task_id):
        """
        取消指定任务
        
        参数:
            task_id: 任务ID
            
        返回:
            bool: 是否成功取消
        """
        with self.lock:
            if task_id in self.active_tasks:
                return self.active_tasks[task_id].cancel()
        return False
    
    def shutdown(self, wait=True):
        """
        关闭线程池
        
        参数:
            wait: 是否等待所有任务完成
        """
        self.executor.shutdown(wait=wait)
        with self.lock:
            self.active_tasks.clear()




class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("摄像头监控系统")
        self.root.geometry("1000x600")
        self.running = False

        self.mse_threshold=150,
        self.ssim_threshold=0.85,
        self.hist_threshold=0.8
        
        #串口控制
        self.ledController = None

        #如果从这个角度来看， monitor不应该再有任何界面相关的内容了
        self.monitor = CameraMonitor(
            region = (558, 153, 586, 215),  # 示例区域，根据需要调整
            mse_threshold=self.mse_threshold,
            ssim_threshold=self.ssim_threshold,
            hist_threshold=self.hist_threshold
        )

        #自动触发端口
        self._touchAutoClick_ = False        
        self.autoClickCount = 0
        self.click_manager = TouchClickManager(self, max_workers=3)

        
        # 默认区域参数
        self.region_x1, self.region_y1 = 100, 100
        self.region_x2, self.region_y2 = 300, 300

        self.image_x, self.image_y = 0, 0
        
        # 从文件加载区域坐标
        self.load_region_coordinates()
        
        # 拖拽相关变量
        self.dragging = False
        self.resizing = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.resize_handle = None  # 0: 左上, 1: 右上, 2: 右下, 3: 左下
        
        # 创建UI组件
        self.create_widgets()
        
        # 摄像头和显示相关变量
        self.cap = None
        self.photo = None
        self.update_id = None
        self.region_id = None
        
        # 线程和队列
        self.frame_queue = queue.Queue(maxsize=5)  # 限制队列大小，避免内存溢出
        self.capture_thread = None
        self.frame_lock = threading.Lock()
        self.latest_frame = None

        #统计相关
        self.last_stat_time = time.time()  # 帧率统计时间戳        
        self.frame_count = 0  # 总帧数计数器
    
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
    
    def save_region_coordinates(self):
        """保存区域坐标到文件"""
        file_path = "region_coordinates.txt"
        try:
            with open(file_path, "w") as f:
                f.write(f"{self.region_x1},{self.region_y1},{self.region_x2},{self.region_y2}")
            print(f"区域坐标已保存到文件: ({self.region_x1}, {self.region_y1}, {self.region_x2}, {self.region_y2})")
        except Exception as e:
            print(f"保存坐标文件出错: {e}")
    
    def create_widgets(self):


        # 顶部控制栏
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 摄像头控制
        camera_frame = ttk.LabelFrame(control_frame, text="摄像头控制")
        camera_frame.pack(side=tk.LEFT, padx=5, pady=5)

        self.open_button = ttk.Button(camera_frame, text="打开摄像头", command=self.open_camera)
        self.open_button.pack(side=tk.LEFT, padx=5)
        
        self.close_button = ttk.Button(camera_frame, text="关闭摄像头", command=self.close_camera, state=tk.DISABLED)
        self.close_button.pack(side=tk.LEFT, padx=5)

        self.screen_Shot_button = ttk.Button(camera_frame, text="截屏", command=self.screen_Shot)
        self.screen_Shot_button.pack(side=tk.LEFT, padx=5)
        
        


        # 串口控制
        serial_frame = ttk.LabelFrame(control_frame, text="串口控制")
        serial_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.serial_port_var = tk.StringVar(value="COM4")
        ttk.Label(serial_frame, text="端口:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(serial_frame, textvariable=self.serial_port_var, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Button(serial_frame, text="连接串口", command=self.connect_serial).pack(side=tk.LEFT, padx=5)
        ttk.Button(serial_frame, text="断开串口", command=self.disconnect_serial, state=tk.DISABLED).pack(side=tk.LEFT, padx=5)
        
        # 监控控制
        monitor_frame = ttk.LabelFrame(control_frame, text="监控控制")
        monitor_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.start_Touch_button = ttk.Button(monitor_frame, text="开始监控", command=self.start_monitoring)
        self.start_Touch_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_Touch_button = ttk.Button(monitor_frame, text="停止监控", command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_Touch_button.pack(side=tk.LEFT, padx=5)
        
        # 指令控制
        cmd_frame = ttk.LabelFrame(control_frame, text="发送指令")
        cmd_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(cmd_frame, text="click23", command=lambda: self.send_command("click23")).pack(side=tk.LEFT, padx=5)
        ttk.Button(cmd_frame, text="back", command=lambda: self.send_command("back")).pack(side=tk.LEFT, padx=5)

        ttk.Button(cmd_frame, text="open", command=lambda: self.send_command("open")).pack(side=tk.LEFT, padx=5)
        ttk.Button(cmd_frame, text="close", command=lambda: self.send_command("close")).pack(side=tk.LEFT, padx=5)
        ttk.Button(cmd_frame, text="custom", command=self.send_custom_command).pack(side=tk.LEFT, padx=5)
        
        # 图像显示区域

        # 图像显示Canvas
        #self.canvas = tk.Canvas(self.root, bg="black", width=1000, height=600)
        #self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.display_frame = ttk.Frame(self.root)
        self.display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.canvas = tk.Canvas(
            self.display_frame, 
            bg="gray", 
            width=640, 
            height=480,
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
        
        ttk.Label(param_left, text="区域 (x1,y1,x2,y2):").grid(row=0, column=0, sticky=tk.W, padx=2, pady=2)
        self.region_var = tk.StringVar(value={self.region_x1,self.region_y1,self.region_x2,self.region_y2})
        ttk.Entry(param_left, textvariable=self.region_var, width=20).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(param_left, text="设置区域", command=self.set_region).grid(row=0, column=2, padx=5, pady=2)
        
        ttk.Label(param_left, text="MSE阈值:").grid(row=1, column=0, sticky=tk.W, padx=2, pady=2)
        self.mse_var = tk.StringVar(value="150")
        ttk.Entry(param_left, textvariable=self.mse_var, width=10).grid(row=1, column=1, padx=2, pady=2)
        
        ttk.Label(param_left, text="SSIM阈值:").grid(row=2, column=0, sticky=tk.W, padx=2, pady=2)
        self.ssim_var = tk.StringVar(value="0.85")
        ttk.Entry(param_left, textvariable=self.ssim_var, width=10).grid(row=2, column=1, padx=2, pady=2)
        
        ttk.Label(param_left, text="直方图阈值:").grid(row=3, column=0, sticky=tk.W, padx=2, pady=2)
        self.hist_var = tk.StringVar(value="0.8")
        ttk.Entry(param_left, textvariable=self.hist_var, width=10).grid(row=3, column=1, padx=2, pady=2)
        
        ttk.Button(param_left, text="应用参数", command=self.apply_parameters).grid(row=4, column=0, columnspan=2, pady=5)


        # 区域参数显示
        param_frame = ttk.Frame(self.root)
        param_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(param_frame, text="当前区域:").pack(side=tk.LEFT, padx=5)
        self.region_label = ttk.Label(param_frame, text=f"({self.region_x1}, {self.region_y1}, {self.region_x2}, {self.region_y2})")
        self.region_label.pack(side=tk.LEFT, padx=5)
        
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
    
    
    def _get_region(self, frame):
        """提取指定监控区域"""
        x1 = self.region_x1 
        y1 = self.region_y1
        x2 = self.region_x2
        y2 = self.region_y2
        return frame[y1:y2, x1:x2]
    
    def _print_frame_statistics(self):
        """每10秒打印帧率统计"""
        current_time = time.time()
        if current_time - self.last_stat_time >= 10:
            fps = self.frame_count / (current_time - self.last_stat_time)
            print(f"\n[统计信息] 过去{int(current_time - self.last_stat_time)}秒内共处理{self.frame_count}帧，平均帧率: {fps:.1f} FPS")
            self.frame_count = 0
            self.last_stat_time = current_time

    

    def touchAutoClick( self,frame, current_region, output_dir):
        print(f"需要思考一下， 怎么发送指令，因为要第一事件发送指令，所以不能等截图: {self.autoClickCount}")

        self.autoClickCount = self.autoClickCount +1
        time.sleep( 100 )
                        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.monitor._save_screenshots(frame, current_region, output_dir, timestamp)
        self.monitor._print_change_log(self.mse_threshold, self.ssim_val_threshold, self.hist_sim_threshold, timestamp)

    def camera_capture_thread(self, output_dir="screenshots"):

        print(f"\n开始监控 - 阈值设置:")
        print(f"MSE > {self.mse_threshold}, SSIM < {self.ssim_threshold}, 直方图相似度 < {self.hist_threshold}")
        print(f"按ESC键退出，窗口可显示实时监控画面\n")


        """摄像头捕获线程函数"""
        while self.running and self.cap.isOpened():
            #第2次读，循环读
            ret, frame = self.cap.read()

            # 帧数统计+= 1  # 帧数统计
            self.frame_count = self.frame_count + 1
            
            if not ret:
                print("错误：无法获取摄像头帧")
                break

            #不停的拿出frame
            current_region = self._get_region(frame)
            

            # 仅在有前一帧时进行变化检测
            if self.prev_frame is not None:
                mse, ssim_val, hist_sim = self.monitor._calculate_metrics(current_region, self.prev_frame )

                isChange = self.monitor._check_changes(mse, ssim_val, hist_sim)
                if isChange:
                    #调用自动执行代码
                    if self._touchAutoClick_ :
                        # 异步处理，不阻塞主线程
                        self.click_manager.touch_auto_click_async(
                            frame=frame,
                            current_region=current_region,
                            output_dir=output_dir,
                            callback=self.touchAutoClick
                        )
                        #self.touchAutoClick(frame,current_region,output_dir)
                    

            # 计算完成后， 更新前一帧
            self.prev_frame = current_region.copy()  # 更新前一帧

            # 每10秒统计帧率
            self._print_frame_statistics()

            # 退出条件
            if cv2.waitKey(1) & 0xFF == 27:  # ESC键
                print("\n接收到退出指令，正在释放资源...")
                break
            
            
            # 将最新帧存入队列
            try:
                # 如果队列满了，先移除最旧的帧
                if self.frame_queue.full():
                    self.frame_queue.get_nowait()
                self.frame_queue.put_nowait(frame)
                
                # 同时保存到共享变量，以便UI线程快速访问
                with self.frame_lock:
                    self.latest_frame = frame
            except queue.Full:
                # 队列已满，丢弃此帧
                pass
            
            # 不添加延时，让捕获线程尽可能快地运行
    
    def connect_serial(self, port="COM4"):
        print("\n connect_serial \n")
        try:
            self.ledController = LEDController(port)
            self.status_var.set(f"已连接到串口 {port}")
            messagebox.showinfo("成功", f"已连接到串口 {port}")
        
        except Exception as e:
            print(f"错误: {str(e)}")
            messagebox.showerror("错误", f"连接串口 {port} 失败")
            self.status_var.set(f"连接串口 {port} 失败")

    
    def disconnect_serial(self):
        print("\n disconnect_serial \n")

        try:
            self.ledController.close()      
            print("关闭串口...")  
        except Exception as e:
            print(f"错误: {str(e)}")
            # 关闭连接
        
        self.status_var.set("串口已断开")
        


    def start_monitoring(self):
        #简单， 设置一个参数， 为True, 当变化，就触发
        self._touchAutoClick_ = True
        self.status_varM1.set("自动触发点击 打开")

        self.start_Touch_button.config(state=tk.DISABLED)
        self.stop_Touch_button.config(state=tk.NORMAL)

        print("\n start_monitoring \n")


    def stop_monitoring(self):
        #简单， 设置一个参数， 为False, 当变化，就不触发。 
        self._touchAutoClick_ = False
        self.status_varM1.set("自动触发点击 关闭")
        self.start_Touch_button.config(state=tk.NORMAL)
        self.stop_Touch_button.config(state=tk.DISABLED)
        print("\n stop_monitoring \n")


    def send_command(self,cmd):
        print("\n send_command \n")
        if self.ledController:
            response = self.ledController.control_led(cmd)
            self.status_var.set(f"发送指令: {cmd}, 响应: {response}")
        else:
            messagebox.showerror("错误", "请先连接串口")

    def send_custom_command(self):
        print("\n send_custom_command \n")
        cmd = simpledialog.askstring("自定义指令", "请输入要发送的指令:")
        if cmd:
            self.send_command(cmd)

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
            
            
            #self.cap.set(cv2.CAP_PROP_FPS, 200)
            
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            print(f"摄像头帧率设置为: {actual_fps} FPS")

            #第1次读；
            ret, frame = self.cap.read()
            if not ret:
                raise ValueError("无法获取摄像头初始帧")                
            self.prev_frame = self._get_region(frame)
            
            
            
            # 更新UI状态
            self.running = True
            self.open_button.config(state=tk.DISABLED)
            self.close_button.config(state=tk.NORMAL)
            self.status_var.set(f"摄像头已打开 ({actual_fps} FPS)")
            
            # 启动捕获线程
            self.capture_thread = threading.Thread(target=self.camera_capture_thread)
            self.capture_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
            self.capture_thread.start()
            
            # 开始更新显示
            self.update_frame()
        else:
            tk.messagebox.showerror("错误", "无法打开摄像头")
    
    def close_camera(self):
        # 停止更新并释放资源
        self.running = False
        
        # 等待捕获线程结束
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=1.0)
        
        # 取消更新任务
        if self.update_id:
            self.root.after_cancel(self.update_id)
            self.update_id = None
        
        # 清空队列
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break
        
        # 释放摄像头
        if self.cap and self.cap.isOpened():
            self.cap.release()
        
        # 清空Canvas
        self.canvas.delete("all")
        
        # 更新UI状态
        self.open_button.config(state=tk.NORMAL)
        self.close_button.config(state=tk.DISABLED)
        self.status_var.set("就绪")
    
    def screen_Shot( self, output_dir="screenshots" ):

        

        #去缓存拿一下；

        # 尝试从队列获取最新帧
        frame = None
        try:
            # 非阻塞方式获取帧
            if not self.frame_queue.empty():
                frame = self.frame_queue.get_nowait()
            else:
                # 如果队列为空，使用共享变量中的最新帧
                with self.frame_lock:
                    frame = self.latest_frame
        except queue.Empty:
            # 队列为空，使用共享变量中的最新帧
            with self.frame_lock:
                frame = self.latest_frame
        
        if frame is not None:
            """保存带标注的全屏截图和区域截图"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            full_path = f"{output_dir}/fullscreen_{timestamp}.jpg"
            region_path = f"{output_dir}/region_{timestamp}.jpg"
            cv2.imwrite(full_path, frame)
            cv2.imwrite(region_path, self._get_region(frame))
            print(fr"手动截屏至 \n1{full_path} \n2{region_path}")
            
        



    def update_frame(self):
        """从队列获取帧并更新Canvas显示"""
        if not self.running:
            return
        
        # 尝试从队列获取最新帧
        frame = None
        try:
            # 非阻塞方式获取帧
            if not self.frame_queue.empty():
                frame = self.frame_queue.get_nowait()
            else:
                # 如果队列为空，使用共享变量中的最新帧
                with self.frame_lock:
                    frame = self.latest_frame
        except queue.Empty:
            # 队列为空，使用共享变量中的最新帧
            with self.frame_lock:
                frame = self.latest_frame
        
        if frame is not None:
            # 转换为RGB格式
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
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
            self.region_id = self.canvas.create_rectangle(
                scaled_x1, scaled_y1, scaled_x2, scaled_y2,
                outline="red", width=1, tags="region"
            )
            
            # 绘制调整手柄
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
            
            # 更新区域参数显示
            self.region_label.config(text=f"({self.region_x1}, {self.region_y1}, {self.region_x2}, {self.region_y2})")
        
        # 继续更新（约30FPS）
        self.update_id = self.root.after(33, self.update_frame)
    
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
        
        # 记录起始位置
        self.drag_start_x = x
        self.drag_start_y = y
    
    def on_mouse_drag(self, event):
        """鼠标拖拽事件处理"""
        if not self.running or not (self.dragging or self.resizing):
            return
        
        # 获取当前鼠标位置
        x, y = event.x, event.y
        dx, dy = x - self.drag_start_x, y - self.drag_start_y
        
        # 获取图像缩放比例
        ratio = self.get_ratio()
        
        if self.dragging:
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
        
        # 记录当前位置作为新的起始位置
        self.drag_start_x, self.drag_start_y = x, y
    
    def on_mouse_up(self, event):
        """鼠标释放事件处理"""
        # 检查是否发生了拖拽或调整大小
        if self.dragging or self.resizing:
            # 打印区域坐标
            print(f"区域坐标已更新: ({self.region_x1}, {self.region_y1}, {self.region_x2}, {self.region_y2})")
            # 在配置区显示

            msg = fr"A{self.region_x1},  A {self.region_y1}, A {self.region_x2}, A {self.region_y2}"

            self.region_var.set( msg )
            # 在UI上显示消息
            self.status_var.set(f"区域已更新: ({self.region_x1}, {self.region_y1}, {self.region_x2}, {self.region_y2})")
            
            # 保存坐标到文件
            self.save_region_coordinates()
            
            
            
            # 3秒后恢复原始状态
            self.root.after(3000, lambda: self.status_var.set(f"摄像头已打开 ({self.cap.get(cv2.CAP_PROP_FPS)} FPS)"))
        
        self.dragging = False
        self.resizing = False
    
    def get_ratio(self):
        """获取图像缩放比例"""
        if not self.cap or not self.cap.isOpened():
            return 1.0
        
        # 获取摄像头帧尺寸
        frame_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        frame_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        # 获取Canvas尺寸
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # 计算缩放比例
        return min(canvas_width / frame_width, canvas_height / frame_height)
    
    def get_frame_size(self):
        """获取原始摄像头帧尺寸"""
        if not self.cap or not self.cap.isOpened():
            return 640, 480  # 默认尺寸
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return width, height
    
    def on_closing(self):
        self.close_camera()
        self.root.destroy()


    


if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()