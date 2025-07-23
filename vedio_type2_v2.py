import time
import ctypes
import psutil
import pytz
from typing import Callable
from datetime import date, datetime, timedelta  # 新增：显式导入 timedelta

# Windows 系统提高时钟分辨率（1ms），非Windows可注释
def set_high_resolution(enable: bool):
    if enable:
        ctypes.windll.winmm.timeBeginPeriod(1)  # 提高分辨率到1ms
    else:
        ctypes.windll.winmm.timeEndPeriod(1)    # 恢复默认

def run_at_exact_time(target_time_str: str, task: Callable, process_communication_queue):
    """
    在指定时间（精确到毫秒）执行任务
    :param target_time_str: 目标时间字符串，格式如 "19:00:00.538"
    :param task: 要执行的任务函数
    """
    # 1. 解析目标时间（今天的19:00:00.538）
    today = date.today()
    target_datetime_str = f"{today} {target_time_str}"
    # 解析到毫秒（注意：strptime的%f支持微秒，需转换）
    target_datetime = datetime.strptime(
        target_datetime_str, 
        "%Y-%m-%d %H:%M:%S.%f"
    )
    # 转换为毫秒级时间戳（1970-01-01以来的毫秒数）
    target_timestamp_ms = int(target_datetime.timestamp() * 1000)

    # 2. 计算当前时间与等待时长
    current_timestamp_ms = int(time.time() * 1000)
    wait_ms = target_timestamp_ms - current_timestamp_ms

    # 处理目标时间已过的情况
    if wait_ms < 0:
        raise ValueError(f"目标时间已过！当前时间: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

    # 3. 高精度等待（启用1ms时钟分辨率）
    set_high_resolution(True)
    try:
        # 等待指定毫秒数（使用time.sleep，支持小数秒）
        time.sleep(wait_ms / 1000.0)

        # 4. 执行任务并记录实际触发时间
        actual_trigger_time = datetime.now()
        print(f"任务触发！实际时间: {actual_trigger_time.strftime('%H:%M:%S.%f')[:-3]}")
        task(actual_trigger_time, process_communication_queue)  # 执行用户任务

        # 5. 验证时间误差
        target_str = target_datetime.strftime("%H:%M:%S.%f")[:-3]
        actual_str = actual_trigger_time.strftime("%H:%M:%S.%f")[:-3]
        error_ms = (actual_trigger_time - target_datetime).total_seconds() * 1000
        print(f"目标时间: {target_str}")
        print(f"误差: {error_ms:.2f}ms")

    finally:
        # 恢复系统时钟分辨率，避免耗电
        set_high_resolution(False)

def datetime_to_milliseconds(dt_str, timezone="UTC"):
    """
    将日期时间字符串转换为自 Unix 纪元以来的毫秒数
    
    参数:
    dt_str (str): 日期时间字符串，格式为 "YYYY-MM-DD HH:MM:SS.ssssss"
    timezone (str): 时区名称，默认为 "UTC"
    
    返回:
    int: 毫秒数
    """

     # 确保 dt 是带时区的对象（如果不是，默认设为 UTC）
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.UTC)
    
    # 计算毫秒数
    epoch = datetime(1970, 1, 1, tzinfo=pytz.UTC)
    return int((dt - epoch).total_seconds() * 1000)

    # # 解析字符串为 datetime 对象
    # dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S.%f")
    
    # # 设置时区（默认为 UTC）
    # tz = pytz.timezone(timezone)
    # dt_aware = tz.localize(dt)
    
    # # 计算自 Unix 纪元以来的毫秒数
    # epoch = datetime(1970, 1, 1, tzinfo=pytz.UTC)
    # milliseconds = int((dt_aware - epoch).total_seconds() * 1000)
    



    # return milliseconds

# ----------------------
# 测试：定义要执行的任务
# ----------------------
def my_task( actual_trigger_time, process_communication_queue ):
    timeaaa = datetime_to_milliseconds(actual_trigger_time)

    ccc = time.time()
    process_communication_queue.put()
    print(f"执行定时任务：这里是需要精确触发的操作 {ccc} {actual_trigger_time} {timeaaa}")




def add_milliseconds(target_time: str, adjust_time: int) -> str:
    """
    将目标时间加上指定毫秒数，返回格式相同的字符串
    
    参数:
    target_time (str): 目标时间字符串，格式为 "HH:MM:SS.fff"
    adjust_time (int): 要添加的毫秒数
    
    返回:
    str: 相加后的时间字符串，格式为 "HH:MM:SS.fff"
    """
    # 解析时间字符串（忽略日期部分）
    time_format = "%H:%M:%S.%f"
    time_obj = datetime.strptime(target_time, time_format)
    
    # 添加指定毫秒数
    new_time = time_obj + timedelta(milliseconds=adjust_time)
    
    # 提取时间部分并格式化为相同精度（3位小数）
    return new_time.strftime(time_format)[:-3]  # 截取到毫秒（3位小数）

def do_task( target_time, tmp_adjust_time=0 ,process_communication_queue=None ):
    andriod_time = 398399
    time_Diff = 3530 
    redundant_time = 10

    time_Diff = time_Diff + redundant_time
    python_time = andriod_time + time_Diff
    damai_time = 400000

    adjust_time = python_time - damai_time

    print(f"调整时间: {adjust_time}ms  没用 {tmp_adjust_time}")

    

    # 示例使用

    print(f"调整前 : {target_time}")
    resultA = add_milliseconds(target_time, adjust_time)
    print(f"python 时间 : {resultA}")
    # 输出: 18:38:00.538 + 123ms = 18:38:00.661


    try:
        run_at_exact_time(resultA, my_task, process_communication_queue)
    except ValueError as e:
        traceback.print_exc()
        print(e)

# ----------------------
# 运行定时任务（示例）
# ----------------------
if __name__ == "__main__":

    # 提升当前进程优先级（可选，需管理员权限）

    p = psutil.Process()
    p.nice(psutil.HIGH_PRIORITY_CLASS)  # Windows 高优先级

    # 目标时间：今天的19:00:00.538（可改为其他时间，如当前时间+3秒测试）
    # 测试时建议先改为当前时间+几秒，例如："15:30:00.538"（确保未过期）
    target_time = "11:06:00.123"

    do_task(target_time)
