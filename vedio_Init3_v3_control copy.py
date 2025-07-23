import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import time
from datetime import datetime

import serial
import time
from v_com1_go import LEDController

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
        self.prev_frame = None  # 前一帧区域图像
        self.cap = None       # 摄像头对象
        self.frame_count = 0  # 总帧数计数器
        self.last_stat_time = time.time()  # 帧率统计时间戳

        self.update_callback = None  # 添加回调函数属性

        self.start_time = time.perf_counter()

        
        # 可视化窗口相关
        self.window_name = "Camera Monitor"
        cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)

        try:
            # 创建控制器实例
            self.controller = LEDController("COM4")
            
        except serial.SerialException as e:
            print(f"串口通信错误: {e}")
        except Exception as e:
            print(f"错误: {e}")

    
    
    def send_cmd(self, cmd):
        # 发送命令并获取响应
        try:
            response = self.controller.control_led(cmd,30)
            print(f"命令: {cmd}")
            print(f"响应: {response}")
        
        except Exception as e:
            print(f"发送命令错误: {e}")

        


    def open_camera(self, camera_id=0):
        """打开摄像头并初始化"""
        self.cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise ValueError(f"无法打开摄像头ID {camera_id}")
        
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("无法获取摄像头初始帧")
            
        self.prev_frame = self._get_region(frame)
        print(f"成功打开摄像头，分辨率: {frame.shape[1]}x{frame.shape[0]}")
        print(f"监控区域: (x1,y1)={self.region[:2]}, (x2,y2)={self.region[2:]}")

    def _get_region(self, frame):
        """提取指定监控区域"""
        x1, y1, x2, y2 = self.region
        return frame[y1:y2, x1:x2]

    # 省略中间的计算方法（与之前相同）

    def start_monitoring(self, output_dir="screenshots"):
        """开始监控主循环"""
        
        print(f"\n开始监控 - 阈值设置:")
        print(f"MSE > {self.mse_threshold}, SSIM < {self.ssim_threshold}, 直方图相似度 < {self.hist_threshold}")
        print(f"按ESC键退出，窗口可显示实时监控画面\n")

        while True:
            ret, full_frame = self.cap.read()
            if not ret:
                print("错误：无法获取摄像头帧")
                break

            current_region = self._get_region(full_frame)
            self.frame_count += 1  # 帧数统计

            # 生成 combined 图像并显示
            combined = self._display_frame(full_frame, current_region)


            # 调用回调函数，将 combined 图像传递给 GUI
            if self.update_callback:
                self.update_callback(combined)

            # 仅在有前一帧时进行变化检测
            if self.prev_frame is not None:
                mse, ssim_val, hist_sim = self._calculate_metrics(current_region)
                self._check_changes(mse, ssim_val, hist_sim, full_frame, current_region, output_dir)

            # 每10秒统计帧率
            self._print_frame_statistics()

            # 退出条件
            if cv2.waitKey(1) & 0xFF == 27:  # ESC键
                print("\n接收到退出指令，正在释放资源...")
                break

    def _display_frame(self, full_frame, current_region):
        """显示带标注的实时画面"""

        
        # 在全屏画面标注监控区域
        x1, y1, x2, y2 = self.region
        annotated_frame = full_frame.copy()
        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(annotated_frame, "Monitoring Region", (x1, y1-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
        
        # 水平拼接显示全屏画面和区域画面
        try:
            region_preview = cv2.resize(current_region, (640, 480))  # 缩小区域画面便于显示
            full_preview = cv2.resize(full_frame, (int(full_frame.shape[1]*0.5), int(full_frame.shape[0]*0.5)))
            combined = np.hstack((full_preview, region_preview))
        except:
            combined = full_frame
            combined = annotated_frame
        
        cv2.imshow(self.window_name, combined)
        return combined  # 返回拼接图像
        
        

    def _calculate_metrics(self, current_region):
        """计算三种差异指标"""
        mse = np.sum((current_region.astype("float") - self.prev_frame.astype("float")) ** 2) / np.size(current_region)
        ssim_val = ssim(cv2.cvtColor(current_region, cv2.COLOR_BGR2GRAY),
                        cv2.cvtColor(self.prev_frame, cv2.COLOR_BGR2GRAY))
        
        # 直方图相似度计算（优化后版本）
        histA = cv2.calcHist([current_region], [0,1,2], None, [8,8,8], [0,256]*3)
        histB = cv2.calcHist([self.prev_frame], [0,1,2], None, [8,8,8], [0,256]*3)
        histA = cv2.normalize(histA, histA).flatten()
        histB = cv2.normalize(histB, histB).flatten()
        hist_sim = cv2.compareHist(histA, histB, cv2.HISTCMP_CORREL)
        
        self.prev_frame = current_region.copy()  # 更新前一帧
        return mse, ssim_val, hist_sim

    def _check_changes(self, mse, ssim_val, hist_sim, full_frame, current_region, output_dir):
        """检测变化并处理截图"""
        mse_changed = mse > self.mse_threshold
        ssim_changed = ssim_val < self.ssim_threshold
        hist_changed = hist_sim < self.hist_threshold
        
        if mse_changed or ssim_changed or hist_changed:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            current_time = time.perf_counter()

            if( current_time - self.start_time  > 10 ):
                #如果检测到变化，处罚单片机按钮事件；
                self.send_cmd("click23")

                self._save_screenshots(full_frame, current_region, output_dir, timestamp)
                self._print_change_log(mse, ssim_val, hist_sim, timestamp)

    def _save_screenshots(self, full_frame, current_region, output_dir, timestamp):
        """保存带标注的全屏截图和区域截图"""
        full_path = f"{output_dir}/fullscreen_{timestamp}.jpg"
        region_path = f"{output_dir}/region_{timestamp}.jpg"
        cv2.imwrite(full_path, full_frame)
        cv2.imwrite(region_path, current_region)

    def _print_change_log(self, mse, ssim_val, hist_sim, timestamp):
        """打印变化日志"""
        print(f"\n[检测到变化 @ {timestamp}]")
        print(f"MSE: {mse:.2f} (阈值: {self.mse_threshold}) | SSIM: {ssim_val:.2f} (阈值: {self.ssim_threshold})")
        print(f"直方图相似度: {hist_sim:.2f} (阈值: {self.hist_threshold}) | 已保存截图")

    def _print_frame_statistics(self):
        """每10秒打印帧率统计"""
        current_time = time.time()
        if current_time - self.last_stat_time >= 10:
            fps = self.frame_count / (current_time - self.last_stat_time)
            print(f"\n[统计信息] 过去{int(current_time - self.last_stat_time)}秒内共处理{self.frame_count}帧，平均帧率: {fps:.1f} FPS")
            self.frame_count = 0
            self.last_stat_time = current_time

    def release_resources(self):
        """释放资源"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()

        try:
            self.controller.close()      

            print("关闭串口...")  
        except Exception as e:
            print(f"错误: {str(e)}")
            # 关闭连接
                




if __name__ == "__main__":


    monitor = CameraMonitor(
        region = (558, 153, 586, 215),  # 示例区域，根据需要调整
        mse_threshold=150,
        ssim_threshold=0.85,
        hist_threshold=0.8
    )

    try:

        
            
        monitor.open_camera()
        monitor.start_monitoring()
    except Exception as e:
        print(f"错误: {str(e)}")
    finally:
        monitor.release_resources()

        