class global_var:
    '''需要定义全局变量的放在这里，最好定义一个初始值'''
    name = 'my_name'
    server = None
    local_mqtt = False

# 对于每个全局变量，都需要定义get_value和set_value接口
def set_name(name):
    global_var.name = name
def get_name():
    return global_var.name

def set_server(server):
    global_var.server = server

def get_server():
    return global_var.server

def set_local_mqtt(local_mqtt):
    global_var.local_mqtt = local_mqtt

def get_local_mqtt():
    return global_var.local_mqtt