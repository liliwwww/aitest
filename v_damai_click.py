import serial
import time
import argparse

class LEDController:
    def __init__(self, port, baudrate=115200, timeout=1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # 等待ESP32初始化
        self._flush_input()
        
    def _flush_input(self):
        while self.ser.in_waiting:
            self.ser.readline()
    
    def control_led(self, pin_index, state):
        if pin_index not in [0, 1, 2]:
            raise ValueError("Pin index must be 0, 1, or 2")
        if state not in [0, 1, 2, 3]:
            raise ValueError("State must be 0 (OFF) or 1 (ON)")
            
        command = f"{pin_index}{state}\n"
        self.ser.write(command.encode())
        response = self.ser.readline().decode().strip()
        return response
    
    def close(self):
        self.ser.close()

def main():
    # parser = argparse.ArgumentParser(description='Control ESP32 LEDs via serial port')
    # parser.add_argument('--port', required=True, help='Serial port (e.g., COM3 on Windows, /dev/ttyUSB0 on Linux)')
    # parser.add_argument('--pin', type=int, choices=[0, 1, 2], required=True, help='LED pin index (0=GPIO13, 1=GPIO14, 2=GPIO15)')
    # parser.add_argument('--state', type=int, choices=[0, 1], required=True, help='LED state (0=OFF, 1=ON)')
    
    # args = parser.parse_args()

    port = 'COM5'
    pin = 0
    state = 0
    
    try:
        controller = LEDController(port)
        response = controller.control_led(pin, state)
        print(f"Command sent: Pin {pin} set to {'ON' if state else 'OFF'}")
        print(f"    ESP32>>>Response: {response}")
        controller.close()
    except serial.SerialException as e:
        print(f"Serial communication error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()    