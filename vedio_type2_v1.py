from datetime import datetime

from datetime import datetime
import pytz

def datetime_to_milliseconds(dt_str, timezone="UTC"):
    """
    将日期时间字符串转换为自 Unix 纪元以来的毫秒数
    
    参数:
    dt_str (str): 日期时间字符串，格式为 "YYYY-MM-DD HH:MM:SS.ssssss"
    timezone (str): 时区名称，默认为 "UTC"
    
    返回:
    int: 毫秒数
    """
    # 解析字符串为 datetime 对象
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S.%f")
    
    # 设置时区（默认为 UTC）
    tz = pytz.timezone(timezone)
    dt_aware = tz.localize(dt)
    
    # 计算自 Unix 纪元以来的毫秒数
    epoch = datetime(1970, 1, 1, tzinfo=pytz.UTC)
    milliseconds = int((dt_aware - epoch).total_seconds() * 1000)
    
    return milliseconds






# timestamp = 1751602320.000
# dt_object = datetime.fromtimestamp(timestamp)

# # 提取时分秒（24小时制）
# time_str = dt_object.strftime("%H:%M:%S")
# print(time_str)  # 输出：23:19:53（UTC时间）


target_time = "2025-07-04 11:42:02.000000"
milliseconds = datetime_to_milliseconds(target_time, "Asia/Shanghai") 
print(milliseconds)