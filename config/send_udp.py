import socket
import time

UDP_IP = "127.0.0.1"  # 目标 IP
UDP_PORT = 23200     # 目标端口
# UDP_PORT = 8000     # 目标端口

print(UDP_IP, UDP_PORT)
MESSAGE = b"qwer23\x00qwer"
# MESSAGE = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\xbf\x00\xc7\x00\x00\x59\xef\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" + b't' * 1300

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP

while True:
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))  # 发送数据
    # time.sleep(1)  # 休眠 1 秒钟
    time.sleep(0.001)  # 休眠 1 秒钟

# struct my_package {
#   uint32_t tunnel_id;
#   uint32_t source_module_id;
#   uint16_t source_user_id;
#   uint16_t dest_user_id;
#   uint32_t flow_id;
#   uint32_t service_id;
#   uint32_t qos_id;
#   uint32_t packet_id;
#   timespec timestamp;
#   uint32_t ext_flag;
# };
