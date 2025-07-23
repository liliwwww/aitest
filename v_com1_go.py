import serial
import time
import argparse
import random

class LEDController:
    def __init__(self, port, baudrate=115200, timeout=1):
        """初始化串口连接"""
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # 等待ESP32初始化
        self._flush_input()
        print(f"已连接到 {port}，波特率 {baudrate}")
        
    def _flush_input(self):
        """清空输入缓冲区"""
        while self.ser.in_waiting:
            self.ser.readline()
    
    def do_cmd(self, state ):
        # 发送命令
        command = f"{state}\n"

        # print(f"v_com1_go.py do_cmd Sending raw bytes: {command.encode()!r}") 
        self.ser.write(command.encode())
        
        # 读取ESP32的响应
        response = self.ser.readline().decode().strip()
        # print(f"do_cmd{state} {response}")
        return response

    def control_led(self, state, num=1):
        """控制LED开关状态"""
        #if state not in ["open", "close", "click23", "back"]:
        #    raise ValueError("状态必须为 'open' 或 'close'")

        start_time = time.time()*1000

        # 循环调用方法100次
        response = ""
        #random_number = 0
        for i in range(num):
            try:
                response = self.do_cmd(state)
                # print(f"do_cmd {state} ->{response}<- duration ")
            except Exception as e:
                print(f"调用 {state} 第{i+1}次 出错: {e}")
            
            #执行多次的时候，为了降低频率
            # if num > 1: 
            #     random_number = random.randint(200, 400)
            #     print(f"随机休眠时间: {random_number} 毫秒")
            #     time.sleep(random_number/1000)

        end_time = time.time()*1000
        total_time = end_time - start_time
        # print(fr"单片机 总耗时时:{total_time}  response{response}")
        return response
    
    def close(self):

        """关闭串口连接"""
        self.ser.close()
        print("串口连接已关闭")

def main():
    """主函数：处理命令行参数并控制LED"""
    parser = argparse.ArgumentParser(description='通过串口控制ESP32的LED')
    #parser.add_argument('--port', required=True, help='串口名称 (例如 Windows: COM3, Linux: /dev/ttyUSB0)')
    parser.add_argument('--state', choices=['open', 'close','click23','back'], required=True, help='LED状态: open=打开, close=关闭')
    
    args = parser.parse_args()
    
    try:
        # 创建控制器实例
        controller = LEDController("COM4")
        
        # 发送命令并获取响应
        response = controller.control_led(args.state)
        print(f"命令: {args.state}")
        print(f"响应: {response}")
        
        # 关闭连接
        controller.close()
        
    except serial.SerialException as e:
        print(f"串口通信错误: {e}")
    except Exception as e:
        print(f"错误: {e}")

def main1():
    """主函数：处理命令行参数并控制LED"""
    #parser = argparse.ArgumentParser(description='通过串口控制ESP32的LED')
    #parser.add_argument('--port', required=True, help='串口名称 (例如 Windows: COM3, Linux: /dev/ttyUSB0)')
    #parser.add_argument('--state', choices=['open', 'close','click23','back'], required=True, help='LED状态: open=打开, close=关闭')
    
    #args = parser.parse_args()
    
    try:
        # 创建控制器实例
        controller = LEDController("COM4")
        
        # 发送命令并获取响应
        for i in range(5):
            response = controller.control_led("click23")
            response = controller.control_led("back")
        print(f"命令: click23")
        print(f"响应: {response}")
        
        # 关闭连接
        controller.close()
        
    except serial.SerialException as e:
        print(f"串口通信错误: {e}")
    except Exception as e:
        print(f"错误: {e}")        

if __name__ == "__main__":
    main1()
