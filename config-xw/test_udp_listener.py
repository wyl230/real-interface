import socket
import time

UDP_IP = "127.0.0.1"  # 目标 IP
UDP_PORT = 8000     # 目标端口
# MESSAGE = b"00000000000000Hello, World!" * 80   # 发送的数据，这里发送了 "Hello, World!" 10 次
MESSAGE = b'\x00\x00\x00\x01\x00\x00\x00\x02\x00\x02\x00\x03\x00\x00\x00\x04\x00\x00\x00\x05\x00\x00\x00\x06\x00\x00\x00\x07\x5f\xb9\x12\x17\x27\x00\x00\x00' + b'1' * 1000

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP

while True:
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))  # 发送数据
    print('send...')
    time.sleep(0.0001)  # 休眠 1 秒钟
