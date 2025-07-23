import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
import threading
import time

class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("摄像头监控系统")
        self.root.geometry("1000x600")
        self.running = False
        
        # 创建UI组件
        self.create_widgets()
        
        # 摄像头和显示相关变量
        self.cap = None
        self.photo = None
        self.update_id = None
    
    def create_widgets(self):
        # 控制按钮
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 保存按钮引用
        self.open_button = ttk.Button(control_frame, text="打开摄像头", command=self.open_camera)
        self.open_button.pack(side=tk.LEFT, padx=5)
        
        self.close_button = ttk.Button(control_frame, text="关闭摄像头", command=self.close_camera, state=tk.DISABLED)
        self.close_button.pack(side=tk.LEFT, padx=5)
        
        # 图像显示Canvas
        self.canvas = tk.Canvas(self.root, bg="black", width=1000, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
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
            # 在帧上标注区域（可选）
            height, width = frame.shape[:2]
            region_x1, region_y1 = 100, 100
            region_x2, region_y2 = 300, 300
            cv2.rectangle(frame, (region_x1, region_y1), (region_x2, region_y2), (0, 0, 255), 2)
            cv2.putText(frame, "监控区域", (region_x1, region_y1-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
            
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
            
            if ratio < 1:  # 只有当需要缩小时才执行缩放
                frame_rgb = cv2.resize(frame_rgb, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # 转换为PhotoImage并显示
            self.photo = tk.PhotoImage(data=cv2.imencode('.ppm', frame_rgb)[1].tobytes())
            
            # 计算居中位置
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            
            # 显示图像
            self.canvas.create_image(x, y, image=self.photo, anchor=tk.NW)
        
        # 继续更新（约30FPS）
        self.update_id = self.root.after(33, self.update_frame)
    
    def on_closing(self):
        self.close_camera()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CameraApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()