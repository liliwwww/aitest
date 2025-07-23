import serial
import time
import argparse

class LEDController:
    def __init__(self, port, baudrate=115200, timeout=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # 等待ESP32初始化
        self._flush_input()
        
    def _flush_input(self):
        print(f" get 1")
        while True:
            if self.ser.in_waiting > 0:
                data = self.ser.readline().decode('utf-8').strip()
                if data == "ESP32 LED Control Ready":
                    print("收到初始化消息:", data)
                    break

        print(f" get 2")

        
    def control_led(self, pin_index, state):
        if pin_index not in [0, 1, 2]:
            raise ValueError("Pin index must be 0, 1, or 2")
        if state not in [0, 1]:
            raise ValueError("State must be 0 (OFF) or 1 (ON)")
            
        command = f"{pin_index}{state}\n"
        self.ser.write(command.encode())
        response = self.ser.readline().decode().strip()
        return response
    
    def close(self):
        self.ser.close()

def main():
    parser = argparse.ArgumentParser(description='Control ESP32 LEDs via serial port')
    parser.add_argument('--port', required=True, help='Serial port (e.g., COM3 on Windows, /dev/ttyUSB0 on Linux)')
    parser.add_argument('--pin', type=int, choices=[0, 1, 2], required=True, help='LED pin index (0=GPIO13, 1=GPIO14, 2=GPIO15)')
    parser.add_argument('--state', type=int, choices=[0, 1], required=True, help='LED state (0=OFF, 1=ON)')
    
    args = parser.parse_args()
    
    try:

        print("A1")
        controller = LEDController(args.port)
        print("A2")
        response = controller.control_led(args.pin, args.state)
        print("A3")
        print(f"Command sent: Pin {args.pin} set to {'ON' if args.state else 'OFF'}")
        print(f"Response: {response}")
        controller.close()
    except serial.SerialException as e:
        print(f"Serial communication error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()    


# PS C:\dev\project\aitest> & C:/dev/project/aitest/venvaitest/Scripts/python.exe c:/dev/project/aitest/v_com1_old.py --port COM4 --pin 0 --state 0
# Command sent: Pin 0 set to OFF
# Response: OK: Pin 13 set to 0