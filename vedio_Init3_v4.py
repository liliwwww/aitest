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

from v_com1_go import LEDController
from vedio_Init3_v3_control import CameraMonitor




class MonitoringGUI:

    def __init__(self, root):

        

        self.monitor = CameraMonitor(
            region = (558, 153, 586, 215),  # 示例区域，根据需要调整
            mse_threshold=150,
            ssim_threshold=0.85,
            hist_threshold=0.8
        )
        
        
            

        self.root = root
        self.root.title("摄像头监控系统")
        self.root.geometry("1000x600")
        self.root.resizable(True, True)
        
        
        self.monitor_thread = None
        self.update_id = None
        
        self.create_widgets()
        self.status_var.set("系统初始化完成")
    


    def create_widgets(self):
        # 顶部控制栏
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 摄像头控制
        camera_frame = ttk.LabelFrame(control_frame, text="摄像头控制")
        camera_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(camera_frame, text="打开摄像头", command=self.open_camera).pack(side=tk.LEFT, padx=5)
        ttk.Button(camera_frame, text="关闭摄像头", command=self.close_camera, state=tk.DISABLED).pack(side=tk.LEFT, padx=5)
        
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
        
        ttk.Button(monitor_frame, text="开始监控", command=self.start_monitoring).pack(side=tk.LEFT, padx=5)
        ttk.Button(monitor_frame, text="停止监控", command=self.stop_monitoring, state=tk.DISABLED).pack(side=tk.LEFT, padx=5)
        
        # 指令控制
        cmd_frame = ttk.LabelFrame(control_frame, text="发送指令")
        cmd_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(cmd_frame, text="click23", command=lambda: self.send_command("click23")).pack(side=tk.LEFT, padx=5)
        ttk.Button(cmd_frame, text="back", command=lambda: self.send_command("back")).pack(side=tk.LEFT, padx=5)

        ttk.Button(cmd_frame, text="open", command=lambda: self.send_command("open")).pack(side=tk.LEFT, padx=5)
        ttk.Button(cmd_frame, text="close", command=lambda: self.send_command("close")).pack(side=tk.LEFT, padx=5)
        ttk.Button(cmd_frame, text="custom", command=self.send_custom_command).pack(side=tk.LEFT, padx=5)
        
        # 图像显示区域
        self.display_frame = ttk.Frame(self.root)
        self.display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.canvas = tk.Canvas(self.display_frame, bg="black", width=1200, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        
        # 监控信息区域
        info_frame = ttk.LabelFrame(self.root, text="监控信息")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
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
        self.region_var = tk.StringVar(value="558,153,586,215")
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
    
    def open_camera(self):
        try:        
            self.monitor.open_camera()        
            messagebox.showinfo("成功", "开始监控")
            print("\n开始监控\n")

        except Exception as e:
            messagebox.showerror("错误", f"打开摄像头失败: {str(e)}")
            self.status_var.set(f"错误: {str(e)}")
    
    def close_camera(self):
        try:
            messagebox.showinfo("成功", "开始监控")
            print("\n结束监控\n")
            self.status_var.set("摄像头已关闭")
            self.clear_display()
        except Exception as e:
            messagebox.showerror("错误", f"打开摄像头失败: {str(e)}")
            self.status_var.set(f"错误: {str(e)}")

        
        
    
    def enable_camera_controls(self, enabled):
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for sub_widget in widget.winfo_children():
                    if isinstance(sub_widget, ttk.Button):
                        if sub_widget["text"] in ["打开摄像头", "关闭摄像头", "开始监控", "停止监控", 
                                                "连接串口", "断开串口"]:
                            sub_widget["state"] = "normal" if enabled else "disabled"
    

    #连接串口
    def connect_serial(self, port="COM4"):
        
        try:
            self.ledController = LEDController(port)
            self.status_var.set(f"已连接到串口 {port}")
            self.enable_camera_controls(True)
            
            messagebox.showinfo("成功", f"已连接到串口 {port}")
        
        except Exception as e:
            print(f"错误: {str(e)}")
            messagebox.showerror("错误", f"连接串口 {port} 失败")
            self.status_var.set(f"连接串口 {port} 失败")

           
    #断开串口
    def disconnect_serial(self):

        try:
            self.ledController.close()      
            print("关闭串口...")  
        except Exception as e:
            print(f"错误: {str(e)}")
            # 关闭连接

        
        self.status_var.set("串口已断开")
        self.enable_camera_controls(True)
    
    
    
    def start_monitoring(self):
        if not self.monitor:
            messagebox.showerror("错误", "请先打开摄像头")
            return
        
        # 应用参数
        self.apply_parameters()
        
        self.status_var.set("开始监控...")
        self.enable_camera_controls(False)
        
        # 设置更新回调函数
        self.monitor.update_callback = self.update_display
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(
            target=self.monitor.start_monitoring
        )
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        self.status_var.set("正在监控中...")
        self.change_var.set("变化检测: 未检测到变化")
    
    def stop_monitoring(self):
        if self.monitor:
            self.monitor.stop_monitoring()
            if self.monitor_thread:
                self.monitor_thread.join(2.0)
            self.monitor_thread = None
        self.status_var.set("监控已停止")
        self.enable_camera_controls(True)
        self.clear_display()
    

    def update_display(self, frame):
        if self.root and self.root.winfo_exists():
            self.root.after(0, self._update_display_impl, frame)


    
    def _update_display_impl(self, frame):
        try:
            # 更新变化检测信息
            if hasattr(self.monitor, 'change_detected') and self.monitor.change_detected:
                self.change_var.set(f"变化检测: 已检测到 {self.monitor.change_count} 次变化")
                self.change_var.configure(foreground="red")
                self.monitor.change_detected = False
            else:
                self.change_var.set("变化检测: 未检测到变化")
                self.change_var.configure(foreground="black")
            
            # 将 combined 图像调整到画布大小
            canvas_width, canvas_height = 1200, 600
            img = cv2.resize(frame, (canvas_width, canvas_height))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # 转换为 PhotoImage
            if hasattr(self, 'photo'):
                if self.update_id:
                    self.canvas.after_cancel(self.update_id)
            
            self.photo = tk.PhotoImage(data=cv2.imencode('.ppm', img)[1].tobytes())
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            
            # 定期清理画布
            self.update_id = self.canvas.after(30, lambda: self.canvas.delete("all"))
        except Exception as e:
            print(f"更新显示界面错误: {e}")
    
    def clear_display(self):
        if hasattr(self, 'photo'):
            if self.update_id:
                self.photo.cancel(self.update_id)
            self.canvas.delete("all")
    

    # ROOT send command
    def send_command(self, cmd):
        if self.ledController:
            response = self.ledController.control_led(cmd)
            self.status_var.set(f"发送指令: {cmd}, 响应: {response}")
        else:
            messagebox.showerror("错误", "请先连接串口")
    
    # 用户输入
    def send_custom_command(self):
        cmd = simpledialog.askstring("自定义指令", "请输入要发送的指令:")
        if cmd:
            self.send_command(cmd)
    
    def set_region(self):
        region_str = self.region_var.get()
        try:
            x1, y1, x2, y2 = map(int, region_str.split(','))
            self.monitor.region = (x1, y1, x2, y2)
            self.status_var.set(f"监控区域已设置为: ({x1},{y1},{x2},{y2})")
        except Exception as e:
            messagebox.showerror("错误", f"区域格式错误: {str(e)}")
            self.status_var.set("区域格式应为: x1,y1,x2,y2")
    
    def apply_parameters(self):
        if not self.monitor:
            return
        
        try:
            mse = float(self.mse_var.get())
            ssim = float(self.ssim_var.get())
            hist = float(self.hist_var.get())
            
            self.monitor.mse_threshold = mse
            self.monitor.ssim_threshold = ssim
            self.monitor.hist_threshold = hist
            
            self.status_var.set(f"监控参数已更新: MSE={mse}, SSIM={ssim}, 直方图={hist}")
        except Exception as e:
            messagebox.showerror("错误", f"参数格式错误: {str(e)}")
            self.status_var.set("参数格式错误，请检查输入")

if __name__ == "__main__":
    root = tk.Tk()
    app = MonitoringGUI(root)
    root.mainloop()