import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import time
from datetime import datetime

class CameraMonitor:
    def __init__(self, region=(100, 100, 400, 400), mse_threshold=100, ssim_threshold=0.9, hist_threshold=0.9):
        """初始化摄像头监控器
        
        Args:
            region: 监控区域坐标(x1, y1, x2, y2)
            mse_threshold: MSE阈值，超过此值视为有变化
            ssim_threshold: SSIM阈值，低于此值视为有变化
            hist_threshold: 直方图相似度阈值，低于此值视为有变化
        """
        self.region = region
        self.mse_threshold = mse_threshold
        self.ssim_threshold = ssim_threshold
        self.hist_threshold = hist_threshold
        self.prev_frame = None
        self.cap = None
        self.start_time = time.time()
        
    def open_camera(self, camera_id=0):
        """打开摄像头"""
        # 使用CAP_DSHOW后端以提高Windows兼容性
        self.cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise ValueError("无法打开摄像头")
        
        # 获取第一帧作为参考
        ret, frame = self.cap.read()
        if ret:
            self.prev_frame = self._get_region(frame)
            # 获取并保存全屏尺寸信息
            self.full_screen_shape = frame.shape
            print(f"全屏尺寸: {self.full_screen_shape[1]}x{self.full_screen_shape[0]}")
        else:
            raise ValueError("无法读取摄像头帧")
            
    def _get_region(self, frame):
        """提取指定区域"""
        x1, y1, x2, y2 = self.region
        return frame[y1:y2, x1:x2]
    
    def calculate_mse(self, imageA, imageB):
        """计算均方误差(MSE)"""
        err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        err /= float(imageA.shape[0] * imageA.shape[1])
        return err
    
    def calculate_ssim(self, imageA, imageB):
        """计算结构相似性指数(SSIM)"""
        # 转换为灰度图进行SSIM计算
        grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
        return ssim(grayA, grayB)
    
    def calculate_histogram_similarity(self, imageA, imageB):
        """计算直方图相似度"""
        histA = cv2.calcHist([imageA], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        histB = cv2.calcHist([imageB], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        
        # 归一化直方图
        histA = cv2.normalize(histA, histA).flatten()
        histB = cv2.normalize(histB, histB).flatten()
        
        # 使用相关性方法计算相似度
        return cv2.compareHist(histA, histB, cv2.HISTCMP_CORREL)
    
    def detect_changes(self):
        """检测变化并返回三种方法的结果"""
        ret, frame = self.cap.read()
        if not ret:
            return None, None, None, None, None
            
        current_region = self._get_region(frame)
        
        if self.prev_frame is None:
            self.prev_frame = current_region
            return None, None, None, None, None
            
        # 计算三种差异指标
        mse = self.calculate_mse(current_region, self.prev_frame)
        ssim_val = self.calculate_ssim(current_region, self.prev_frame)
        hist_sim = self.calculate_histogram_similarity(current_region, self.prev_frame)
        
        # 更新前一帧
        self.prev_frame = current_region
        
        return frame, current_region, mse, ssim_val, hist_sim
    
    def start_monitoring(self, output_dir="screenshots"):
        """开始监控摄像头"""
        import os
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        print(f"开始监控区域: {self.region}")
        print(f"阈值设置 - MSE: {self.mse_threshold}, SSIM: {self.ssim_threshold}, 直方图相似度: {self.hist_threshold}")
        
        last_print_time = time.time()
        
        while True:
            current_time = time.time()
            full_frame, region, mse, ssim_val, hist_sim = self.detect_changes()
            
            if mse is not None:
                # 检查是否有变化超过阈值
                mse_changed = mse > self.mse_threshold
                ssim_changed = ssim_val < self.ssim_threshold
                hist_changed = hist_sim < self.hist_threshold
                
                if mse_changed or ssim_changed or hist_changed:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # 保存全屏截图
                    full_filename = f"{output_dir}/fullscreen_{timestamp}.jpg"
                    cv2.imwrite(full_filename, full_frame)
                    
                    # 保存区域截图
                    region_filename = f"{output_dir}/region_{timestamp}.jpg"
                    cv2.imwrite(region_filename, region)
                    
                    print(f"\n变化检测 - 时间: {timestamp}")
                    print(f"MSE: {mse:.2f} (阈值: {self.mse_threshold}), 变化: {mse_changed}")
                    print(f"SSIM: {ssim_val:.2f} (阈值: {self.ssim_threshold}), 变化: {ssim_changed}")
                    print(f"直方图相似度: {hist_sim:.2f} (阈值: {self.hist_threshold}), 变化: {hist_changed}")
                    print(f"全屏截图已保存: {full_filename}")
                    print(f"区域截图已保存: {region_filename}")
                
                # 每100ms打印一次变化值
                if current_time - last_print_time >= 0.1:
                    print(f"\r当前变化值 - MSE: {mse:.2f}, SSIM: {ssim_val:.2f}, 直方图相似度: {hist_sim:.2f}", end="")
                    last_print_time = current_time
            
            # 按ESC键退出
            key = cv2.waitKey(1)
            if key == 27:  # ESC键
                break
    
    def release_resources(self):
        """释放资源"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # 设置监控区域(x1, y1, x2, y2)
    monitor_region = (558, 153, 586, 215)  # 示例区域，根据需要调整
    
    # 创建监控器实例
    monitor = CameraMonitor(
        region=monitor_region,
        mse_threshold=150,    # 调整此值以适应光照条件
        ssim_threshold=0.85,  # 调整此值以适应灵敏度
        hist_threshold=0.8    # 调整此值以适应颜色变化
    )
    
    try:
        # 打开摄像头
        monitor.open_camera()
        
        # 开始监控
        monitor.start_monitoring()
        
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 释放资源
        monitor.release_resources()    