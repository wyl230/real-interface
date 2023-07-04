import socket
import time

UDP_IP = "192.168.0.100"  # 目标 IP
# UDP_IP = "127.0.0.1"
UDP_PORT = 30027     # 目标端口
MESSAGE = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\xbf\x00\xc7\x00\x00\x59\xef\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" + b't' * 1300

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
import time 
init_time = time.time()
cnt = 0

while True:
    if time.time() - init_time > cnt * 0.001:
        cnt += 1
        # if time.time() - init_time > 1:
        #     print(cnt)
        #     break
        if cnt % 1000 == 0:
            print(cnt)
            print(len(MESSAGE))
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))  # 发送数据
    time.sleep(0.0001)  # 休眠 1 秒钟

