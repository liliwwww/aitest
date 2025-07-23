
import serial
import time
from typing import Optional
import traceback

class ArduinoController:
    def __init__(self, port: str = "COM4", baudrate: int = 115200):
        self.ser = serial.Serial(port, baudrate, bytesize=serial.EIGHTBITS,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    timeout=10)
        time.sleep(2)  # 等待串口初始化
        print("已连接到Arduino")

        
        self._print_welcome_message()

    def _print_welcome_message(self):
        self.ser.reset_input_buffer()    
        # 修改解码方式，忽略或替换非法字节
        response = self.ser.read_until(b'\n').decode().strip()
        print(f"        >>>COM5 IN 1")
        if response:
            print(f">>>Arduino响应：{response}")
        

        
        print("\n支持的指令：")
        print("1. click_Qiang          - 开始5秒点击模拟")
        print("2. open_LED [pin]       - 打开指定LED（例：open_LED 13）")
        print("3. close_LED [pin]      - 关闭指定LED（例：close_LED 13）")
        print("4. switch_LED [pin]     - 切换指定LED状态（例：switch_LED 13）")
        print("输入 'exit' 退出程序\n")

    def send_command(self, cmd: str):

        #清空输入缓冲区
        self.ser.reset_input_buffer()


        """发送指令到Arduino"""
        cmd += "\n"  # 添加换行符作为结束符'
        print(f"        >>>COM5 OUT {cmd}")
        self.ser.write(cmd.encode())
        print(f"        >>>COM5 OUT 1")
        time.sleep(0.1)  # 等待指令处理
        
        
        # 修改解码方式，忽略或替换非法字节
        response = self.ser.read_until(b'\n').decode('utf-8', errors='replace').strip()
        print(f"        >>>COM5 IN 1")
        if response:
            print(f">>>Arduino响应：{response}")

        # 读取后清空输入缓冲区
        self.ser.reset_input_buffer()

    def start_click_simulation(self):
        self.send_command("click_Qiang")

    def control_led(self, action: str, pin: int):
        
        print(f"control_led  >>>{action}, {pin}\n")
        if action not in ["open_LED", "close_LED", "switch_LED"]:
            raise ValueError("无效操作类型，需为open/close/switch")
        
        print(f"control_led  send>>>{action}, {pin}\n")
        self.send_command(f"{action} {pin}")

        print(f"control_led  receive>>>\n")

    def close_connection(self):
        self.ser.close()
        print("已断开串口连接")

if __name__ == "__main__":
    # 修改为你的Arduino串口端口（如COM3、/dev/ttyUSB0等）
    PORT = "COM4"
    
    try:
        controller = ArduinoController(PORT)
        
        while True:
            user_input = input("请输入指令：").strip()
            user_input_cmd_lowercase = user_input.lower()

            print(f" low case:{user_input_cmd_lowercase}" );
            
            if user_input == "exit":
                controller.close_connection()
                break
            
            # 解析指令
            if user_input_cmd_lowercase.startswith("click_qiang"):
                controller.start_click_simulation()
                
            elif user_input_cmd_lowercase.startswith(("open_led", "close_led", "switch_led")):
                try:
                    action, pin = user_input.split()
                    controller.control_led(action, int(pin))
                except Exception as e:
                    # 打印基本异常信息
                    print(f"异常类型: {type(e).__name__}")
                    print(f"异常消息: {str(e)}")
                    
                    # 获取完整堆栈跟踪信息
                    stack_trace = traceback.format_exc()
                    print(f"堆栈跟踪:\n{stack_trace}")

            else:
                print("未知指令，请重新输入")
                
    except serial.SerialException as e:
        print(f"串口连接失败：{e}")
    except Exception as e:
        print(f"发生错误：{e}")