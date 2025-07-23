import serial
import time

class ESP32Controller:
    def __init__(self, port='COM4', baudrate=115200):
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=10
        )
        # 等待ESP32初始化并读取就绪信号
        self._wait_for_ready()

    def _wait_for_ready(self):
        """等待ESP32发送'ready connect'信号"""
        start_time = time.time()
        while time.time() - start_time < 5:  # 最多等待5秒
            if self.ser.in_waiting:
                line = self.ser.readline().decode().strip()
                if line == "ready connect":
                    print("已连接到ESP32")
                    return True
        raise TimeoutError("无法连接到ESP32或未收到就绪信号")

    def send_command(self, command, value):
        """发送命令到ESP32并返回结果"""
        # 清空输入缓冲区
        self.ser.reset_input_buffer()
        
        # 发送完整命令
        full_command = f"{command} {value}"
        self.ser.write(f"{full_command}\n".encode())
        
        # 读取响应
        response = self.ser.readline().decode('utf-8').strip()
        
        # 解析结果
        if response.startswith("result:"):
            try:
                return int(response.split(":")[1].strip())
            except (IndexError, ValueError):
                return None
        else:
            return response

# 使用示例
if __name__ == "__main__":
    try:
        controller = ESP32Controller(port='COM4')
        
        # 测试加法命令
        result = controller.send_command("add", 10)
        print(f"加法结果: {result}")
        
        # 测试减法命令
        result = controller.send_command("sub", 10)
        print(f"减法结果: {result}")
        
    except Exception as e:
        print(f"通信错误: {e}")    