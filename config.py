import time
import sys
from loguru import logger
logger.remove()  # 这行很关键，先删除logger自动产生的handler，不然会出现重复输出的问题
logger.add(sys.stderr, level='INFO')  # 只输出警告以上的日志

class global_var:
    '''需要定义全局变量的放在这里，最好定义一个初始值'''
    headers = { "Content-Type": "application/json; charset=UTF-8", }
    name = 'my_name'
    server = None
    local_mqtt = False

# other
def set_server(server):
    global_var.server = server

def get_server():
    return global_var.server

def set_local_mqtt(local_mqtt):
    global_var.local_mqtt = local_mqtt

def get_local_mqtt():
    return global_var.local_mqtt
