import socket
import struct
import time
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
TOTAL_ROUNDS = 12  # 通信次数

def receive_full_data(sock, expected_bytes):
    """接收指定字节数的数据，处理不完整数据包"""
    data = b''
    while len(data) < expected_bytes:
        try:
            chunk = sock.recv(expected_bytes - len(data))
            if not chunk:
                return None  # 连接关闭，数据不完整
            data += chunk
        except socket.timeout:
            logging.warning("接收数据超时")
            return None
    return data

def calculate_time_difference(server_ip, server_port):
    """
    与Java服务器进行时间同步通信（使用标准long格式）
    """
    latency_list = []
    i2_time = 0  # 第2次通信的服务器接收时间
    i11_time = 0  # 第11次通信的服务器发送完成时间
    
    logging.debug("开始与Java服务器进行时间同步...")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)  # 设置连接和接收超时
            s.connect((server_ip, server_port))
            logging.debug(f"成功连接到服务器: {server_ip}:{server_port}")
            
            for i in range(TOTAL_ROUNDS):
                # 生成客户端时间戳（毫秒级）
                client_time = int(time.time() * 1000)
                logging.debug(f"客户端时间戳: {client_time}")
                
                # 将long转换为8字节大端序数据（Java兼容格式）
                client_time_bytes = struct.pack('>q', client_time)
                s.sendall(client_time_bytes)
                logging.debug(f"第{i+1}次通信: 发送客户端时间 {client_time}")
                
                # 接收服务器时间（8字节大端序）
                server_time_data = receive_full_data(s, 8)
                if not server_time_data:
                    logging.error("接收服务器时间失败，数据不完整")
                    return "接收服务器时间失败：数据不完整"
                
                # 解析8字节为long（大端序）
                server_time = struct.unpack('>q', server_time_data)[0]
                logging.debug(f"第{i+1}次通信: 接收服务器时间 {server_time}")
                
                # 记录特殊时间点
                if i == 1:
                    i2_time = server_time  # 对应Java中的i2time
                if i == 11:
                    i11_time = int(time.time() * 1000)  # 记录客户端接收完成时间
                
                # 计算往返延迟（服务器时间 - 客户端时间）
                latency = server_time - client_time
                latency_list.append(latency)
                logging.debug(f"第{i+1}次通信: 延迟 {latency}ms")
        
        # 计算平均延迟（保持原有逻辑）
        if len(latency_list) >= 11:
            valid_latencies = latency_list[1:11]  # 索引1-10对应第2-11次
            total_latency = sum(valid_latencies)
            avg_latency = total_latency / 10.0
            
            comm_time = i11_time - i2_time
            avager_comm_delay = comm_time / 10.0 / 2.0  # /10 一次往返, /2 单程
            adject_diff = avg_latency - avager_comm_delay
            
            result = (f"完成{ TOTAL_ROUNDS }次通信\n"
                      f"1. 第2-11次平均时差: {avg_latency:.2f}ms\n"
                      f"2. 当前客户端时间: {int(time.time() * 1000)} ms \n"
                      f"3. 第2-11次通信时长: {comm_time} ms \n"
                      f"   第2-11次通信平均延迟: {avager_comm_delay:.2f}ms\n"
                      f"   第2-11次通信平均延迟(adjust): {adject_diff:.2f}ms")
        else:
            result = "通信次数不足，无法计算平均延迟"
            
        return result
        
    except socket.timeout:
        logging.error("连接或接收超时")
        return f"连接超时，服务器在10秒内无响应"
    except socket.error as e:
        logging.error(f"网络错误: {e}")
        return f"网络错误：{e}"
    except Exception as e:
        logging.error(f"未知错误: {e}")
        return f"未知错误：{e}"

# 使用示例
if __name__ == "__main__":
    SERVER_IP = "127.0.0.1"  # 替换为实际服务器IP
    SERVER_PORT = 80      # 替换为实际服务器端口
    
    result = calculate_time_difference(SERVER_IP, SERVER_PORT)
    print("\n" + result)