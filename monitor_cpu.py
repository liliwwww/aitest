import psutil
import time
import os

def get_process_cpu_usage(duration=10):
    # 获取当前进程的 PID
    process = psutil.Process(os.getpid())
    
    # 收集 CPU 使用率样本
    cpu_percentages = []
    start_time = time.time()
    
    # 在 10 秒内每 0.1 秒采样一次
    while time.time() - start_time < duration:
        cpu_percent = process.cpu_percent(interval=0.1) / psutil.cpu_count()
        cpu_percentages.append(cpu_percent)
        time.sleep(0.1)
    
    # 计算平均 CPU 使用率
    if cpu_percentages:
        avg_cpu_usage = sum(cpu_percentages) / len(cpu_percentages)
        return avg_cpu_usage
    else:
        return 0.0

# 执行监控
try:
    print(f"Collecting CPU usage for {os.getpid()} over 10 seconds...")
    avg_cpu = get_process_cpu_usage(10)
    print(f"Average CPU usage over 10 seconds: {avg_cpu:.2f}%")
except psutil.NoSuchProcess:
    print("Error: Process does not exist.")
except Exception as e:
    print(f"Error: {e}")