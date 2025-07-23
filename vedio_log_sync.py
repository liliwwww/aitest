import subprocess

import socket
import requests
import time
from datetime import datetime

class TimeSyncClient:
    def __init__(self, server_ip, http_port=8080 ):
        self.server_ip = "10.98.199.189"
        self.http_port = 8080
        
        self.http_url = f"http://{server_ip}:{http_port}/putLog"
    
    def time_sync(self):
        """执行时间同步并返回结果"""
        results = []
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.server_ip, self.sync_port))
                for i in range(12):
                    # 发送客户端时间
                    client_time = int(time.time() * 1000)
                    s.sendall(client_time.to_bytes(8, byteorder='long'))
                    
                    # 接收服务器时间
                    server_time_bytes = s.recv(8)
                    server_time = int.from_bytes(server_time_bytes, byteorder='long')
                    
                    latency = server_time - client_time
                    results.append(f"第{i+1}次通信: 客户端时间={client_time}, 服务器时间={server_time}, 时差={latency}ms")
        except Exception as e:
            results.append(f"时间同步错误: {str(e)}")
        
        return "\n".join(results)
    
    def upload_log(self, log_content):
        """上传日志到服务器"""
        try:
            response = requests.post(
                self.http_url,
                data=log_content,
                headers={"Content-Type": "text/plain"}
            )

            
            # print(f" upload_log{ response.text}" )
            if response.status_code == 200:
                return True, "日志上传成功"
            else:
                return False, f"上传失败，状态码: {response.status_code}"
        except Exception as e:
            return False, f"上传异常: {str(e)}"

# 使用示例
if __name__ == "__main__":
    client = TimeSyncClient("10.98.199.189")  # 替换为服务器IP
    
    
    log_content = "222-333"
    
    
    # 上传日志
    success, message = client.upload_log(log_content)
    print(f"日志上传: {'成功' if success else '失败'}, 消息: {message}")