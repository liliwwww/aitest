




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

class TouchClickManager:
    """
    单线程任务队列管理器，用于异步调用 MainApplication 的 touchAutoClick 方法
    
    特点:
    - 仅使用一个工作线程
    - 任务执行中时，新任务会被直接抛弃
    - 支持结果回调
    - 提供任务状态查询
    """
    
    def __init__(self, app_instance):
        """
        初始化管理器
        
        参数:
            app_instance: MainApplication 实例
        """
        self.app = app_instance
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.lock = threading.Lock()
        self.current_task_id = None
        self.is_processing = False

        
        
    def touch_auto_click_async(self, frame, current_region, output_dir, 
                               callback: Optional[Callable[[str, bool, Any], None]] = None) -> Optional[str]:
        """
        异步调用 touchAutoClick 方法
        
        参数:
            frame: 视频帧
            current_region: 目标区域坐标 (x1, y1, x2, y2)
            output_dir: 输出目录
            callback: 处理完成后的回调函数，接收参数 (task_id, success, result)
            
        返回:
            str: 任务ID，失败时返回 None
        """
        with self.lock:
            # 如果当前有任务在执行，直接返回 None 表示任务被抛弃
            if self.is_processing:
                print(f"任务被抛弃: 已有任务 {self.current_task_id} 在执行中")
                return None
                
            # 生成唯一任务ID
            task_id = str(uuid.uuid4())[:8]
            self.current_task_id = task_id
            self.is_processing = True
            
        # 提交任务到线程池
        future = self.executor.submit(
            self._execute_task,
            task_id,
            frame,
            current_region,
            output_dir,
            callback
        )
        
        return task_id
    
    def _execute_task(self, task_id, frame, current_region, output_dir, callback):
        """
        执行实际任务
        
        参数:
            task_id: 任务ID
            frame: 视频帧
            current_region: 目标区域坐标
            output_dir: 输出目录
            callback: 回调函数
        """
        try:
            print(f"开始执行任务 {task_id}")
            
            # 调用主应用的 touchAutoClick 方法
            result = self.app.touchAutoClick(frame, current_region, output_dir)
            
            # 任务成功完成
            print(f"任务 {task_id} 执行完成")
            
            # 调用回调函数
            if callback and callable(callback):
                callback(task_id, True, result)
                
            return result
            
        except Exception as e:
            print(f"任务 {task_id} 执行异常: {str(e)}")
            
            # 调用回调函数，传递错误信息
            if callback and callable(callback):
                callback(task_id, False, str(e))
                
            return False
            
        finally:
            # 无论任务成功与否，都标记任务已完成
            with self.lock:
                self.is_processing = False
                self.current_task_id = None
    
    def is_task_in_progress(self) -> bool:
        """
        检查是否有任务正在执行
        
        返回:
            bool: 是否有任务在执行
        """
        with self.lock:
            return self.is_processing
    
    def get_current_task_id(self) -> Optional[str]:
        """
        获取当前执行中的任务ID
        
        返回:
            str: 当前任务ID，无任务时返回 None
        """
        with self.lock:
            return self.current_task_id
    
    def shutdown(self, wait: bool = True):
        """
        关闭线程池
        
        参数:
            wait: 是否等待当前任务完成
        """
        self.executor.shutdown(wait=wait)
        print("TouchClickManager 已关闭")
