import socket
import time

UDP_IP = "162.105.85.70"  # 目标 IP
# UDP_IP = "127.0.0.1"
# UDP_PORT = 30027     # 目标端口
UDP_PORT = 30027     # 目标端口
# UDP_PORT = 31510

print(UDP_IP, UDP_PORT)
MESSAGE = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\xbf\x00\xc7\x00\x00\x59\xef\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" + b't' * 2500

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
import time 
init_time = time.time()
cnt = 0

interval = 0.0004

while True:
    if time.time() - init_time > cnt * interval:
        cnt += 1
        # if time.time() - init_time > 1:
        #     print(cnt)
        #     break
        if cnt % 1000 == 0:
            print(cnt)
            print(len(MESSAGE), f'rate={len(MESSAGE) / interval / 1024}kB/s rate={len(MESSAGE) / interval / 1024 * 8 }kbps')
            print(len(MESSAGE), f'rate={len(MESSAGE) * cnt / 1024 / (time.time() - init_time)}kB/s rate={len(MESSAGE) * cnt / 1024 / (time.time() - init_time) * 8 }kbps')
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))  # 发送数据


