import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
import threading
import time
import os

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("摄像头监控系统")
        self.root.geometry("1000x600")
        self.running = False
        
        # 默认区域参数
        self.region_x1, self.region_y1 = 100, 100
        self.region_x2, self.region_y2 = 300, 300
        
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
        # 控制按钮
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.open_button = ttk.Button(control_frame, text="打开摄像头", command=self.open_camera)
        self.open_button.pack(side=tk.LEFT, padx=5)
        
        self.close_button = ttk.Button(control_frame, text="关闭摄像头", command=self.close_camera, state=tk.DISABLED)
        self.close_button.pack(side=tk.LEFT, padx=5)
        
        # 图像显示Canvas
        self.canvas = tk.Canvas(self.root, bg="black", width=1000, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 区域参数显示
        param_frame = ttk.Frame(self.root)
        param_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(param_frame, text="当前区域:").pack(side=tk.LEFT, padx=5)
        self.region_label = ttk.Label(param_frame, text=f"({self.region_x1}, {self.region_y1}, {self.region_x2}, {self.region_y2})")
        self.region_label.pack(side=tk.LEFT, padx=5)
        
        # 绑定鼠标事件
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
    
    def open_camera(self):
        # 打开摄像头
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            tk.messagebox.showerror("错误", "无法打开摄像头")
            return
        
        # 更新UI状态
        self.running = True
        self.open_button.config(state=tk.DISABLED)
        self.close_button.config(state=tk.NORMAL)
        
        # 开始更新显示
        self.update_frame()
    
    def close_camera(self):
        # 停止更新并释放资源
        self.running = False
        if self.update_id:
            self.root.after_cancel(self.update_id)
            self.update_id = None
        
        if self.cap and self.cap.isOpened():
            self.cap.release()
        
        # 清空Canvas
        self.canvas.delete("all")
        
        # 更新UI状态
        self.open_button.config(state=tk.NORMAL)
        self.close_button.config(state=tk.DISABLED)
    
    def update_frame(self):
        """从摄像头读取帧并更新Canvas显示"""
        if not self.running or not self.cap or not self.cap.isOpened():
            return
        
        # 读取摄像头帧
        ret, frame = self.cap.read()
        if ret:
            # 转换为RGB格式
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 调整尺寸以适应Canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # 保持比例缩放
            frame_height, frame_width = frame_rgb.shape[:2]
            ratio = min(canvas_width / frame_width, canvas_height / frame_height)
            new_width = int(frame_width * ratio)
            new_height = int(frame_height * ratio)
            
            # 计算显示位置
            self.image_x = (canvas_width - new_width) // 2
            self.image_y = (canvas_height - new_height) // 2
            
            # 计算区域在缩放后图像上的位置
            scaled_x1 = int(self.region_x1 * ratio) + self.image_x
            scaled_y1 = int(self.region_y1 * ratio) + self.image_y
            scaled_x2 = int(self.region_x2 * ratio) + self.image_x
            scaled_y2 = int(self.region_y2 * ratio) + self.image_y
            
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
                outline="blue", width=2, tags="region"
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
            
            # 保存坐标到文件
            self.save_region_coordinates()
            
            # 在UI上显示消息
            self.status_var = tk.StringVar(value=f"区域已更新: ({self.region_x1}, {self.region_y1}, {self.region_x2}, {self.region_y2})")
            self.status_label = ttk.Label(self.root, textvariable=self.status_var)
            self.status_label.pack(fill=tk.X, padx=10, pady=2)
            
            # 3秒后自动移除状态消息
            self.root.after(3000, lambda: self.status_label.pack_forget())
        
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