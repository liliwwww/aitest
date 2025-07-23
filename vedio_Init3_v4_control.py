import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import time
from datetime import datetime
import time



class CameraMonitor:


    def __init__(self, region=(100, 100, 400, 400), mse_threshold=100, ssim_threshold=0.9, hist_threshold=0.9):
        """初始化摄像头监控器
        
        Args:
            region: 监控区域坐标(x1, y1, x2, y2)
            mse_threshold: MSE阈值，超过此值视为有变化
            ssim_threshold: SSIM阈值，低于此值视为有变化
            hist_threshold: 直方图相似度阈值，低于此值视为有变化
        """
        self.region = region  # 监控区域坐标
        self.mse_threshold = mse_threshold
        self.ssim_threshold = ssim_threshold
        self.hist_threshold = hist_threshold
        
        #self.prev_frame = None  # 前一帧区域图像
        self.cap = None       # 摄像头对象
        self.frame_count = 0  # 总帧数计数器
        

        self.start_time = time.perf_counter()

        
        

    
    



    # 省略中间的计算方法（与之前相同）
    def _calculate_metrics(self, current_region,  prev_frame):
        """计算三种差异指标"""
        mse = np.sum((current_region.astype("float") - prev_frame.astype("float")) ** 2) / np.size(current_region)
        
        # ssim_val = ssim(cv2.cvtColor(current_region, cv2.COLOR_BGR2GRAY),
        #                 cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY))
        
        # # 直方图相似度计算（优化后版本）
        # histA = cv2.calcHist([current_region], [0,1,2], None, [8,8,8], [0,256]*3)
        # histB = cv2.calcHist([prev_frame], [0,1,2], None, [8,8,8], [0,256]*3)
        # histA = cv2.normalize(histA, histA).flatten()
        # histB = cv2.normalize(histB, histB).flatten()
        # hist_sim = cv2.compareHist(histA, histB, cv2.HISTCMP_CORREL)
        
        #print(f"MSE > {mse}, SSIM < {ssim_val}, 直方图相似度 < {hist_sim}")

        return mse, 0.99, 0.99

    def _check_changes( self, mse, ssim_val, hist_sim ):
        """检测变化并处理截图"""
        mse_changed = mse > self.mse_threshold
        ssim_changed = ssim_val < self.ssim_threshold
        hist_changed = hist_sim < self.hist_threshold

        if mse_changed or ssim_changed or hist_changed:
            # if mse_changed:
            #     print(f"_check_changes{mse_changed}  {self.mse_threshold} ")
            # if ssim_changed:
            #     print(f"_check_changes{ssim_val}     {self.ssim_threshold} ")
            # if hist_changed:
            #     print(f"_check_changes{hist_changed} {self.hist_threshold}")
            return True
        else:
            return False
        
            

            



    

                