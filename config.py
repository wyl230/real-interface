class global_var:
    '''需要定义全局变量的放在这里，最好定义一个初始值'''
    name = 'my_name'
    server = None
    local_mqtt = False
    ue_status = {}
    sat_status = {}
    service_table = {}

    list_length = 12

    ue_uplink_band = []
    ue_downlink_band = []
    sat_uplink = []
    sat_downlink = []
    sat_link_forward = []
    sat_link_recv = []
    sat_link = []
    # 
    throughput_all = []
    max_delay = {}
    min_delay = {}
    avg_delay = {}
    loss_rate = {}
    throughput = {}

# 效能评估
def get_throughput(ins_id):
    return global_var.throughput[ins_id]

def get_delay_single(ins_id):
    return global_var.throughput[ins_id]

def get_loss_rate(ins_id):
    return global_var.throughput[ins_id]

def get_throughput_all():
    return global_var.throughput_all

def get_throughput(ins_id):
    return global_var.throughput_all

def get_max_delay(ins_id):
    return global_var.max_delay

def get_min_delay(ins_id):
    return global_var.min_delay

def get_avg_delay(ins_id):
    return global_var.min_delay

def get_loss_rate(ins_id):
    return global_var.loss_rate

def update_display_list(data, list, max_length = global_var.list_length):
    if len(list) >= max_length:
        list.pop(0)
    list.append(data)

def set_evaluator_for_each(data_dict):
    throughput_all_data = 0
    for flow_msg in data_dict:
        ins_id = flow_msg['ins_id']
        update_display_list(flow_msg['throughput'], global_var.throughput[ins_id])
        update_display_list(flow_msg['max_delay'], global_var.max_delay[ins_id])
        update_display_list(flow_msg['min_delay'], global_var.min_delay[ins_id])
        update_display_list(flow_msg['ave_delay'], global_var.avg_delay[ins_id])
        update_display_list(flow_msg['loss_rate'], global_var.loss_rate[ins_id])

        throughput_all_data += flow_msg['throughput']
    update_display_list(throughput_all_data, global_var.throughput_all)
# chz

# ue
#  总共的包
# { "type": "ue", "id": 0, "time": 12328190, "access_sat": 11003, "up_link_bandwidth": 10000, "down_link_bandwidth": 10000, "up_link_packet": 20000000, "down_link_packet": 20000000, "up_link_byte": 200000000, "down_link_byte": 200000000, "location": { "longitude": 13.123, "latitude": 13.123, } }

def set_ue_related_list(ue_status):
    update_display_list(ue_status.up_link_bandwidth, global_var.ue_uplink_band)
    update_display_list(ue_status.downlink_bandwidth, global_var.ue_downlink_band)

def get_ue_uplink_band():
    return global_var.ue_uplink_band
def get_ue_downlink_band():
    return global_var.ue_downlink_band

# sat
def set_sat_related_list(sat_status):
    update_display_list(sat_status.total_up_byte, global_var.sat_uplink)
    update_display_list(sat_status.total_down_byte, global_var.sat_downlink)
    update_display_list(sat_status.neighborsat[0].forward_byte, global_var.sat_link_forward) # todo forward 
    update_display_list(sat_status.neighborsat[1].receive_byte, global_var.sat_link_forward) # todo receive 

def set_sat_link(sat_status):
    global_var.sat_link = [sat_neighbor.id for sat_neighbor in sat_status.neighbor_sat]

def set_sat_link_recv(sat_status):
    update_display_list(sat_status.total_up_byte, global_var.sat_uplink_band)

def set_sat_link(sat_status):
    update_display_list(sat_status.total_up_byte, global_var.sat_uplink_band)

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

# ue status
def get_ue_status():
    return global_var.ue_status

def set_ue_status(ue_status):
    global_var.ue_status = ue_status

# sat status
def get_sat_status():
    return global_var.ue_status

def set_sat_status(sat_status):
    global_var.sat_status = sat_status

# service table
def get_service_table():
    return global_var.service_table


def set_service_table(data_dict):
    global_var.service_table = data_dict

def set_indicator(data_dict):
    update_display_list(global_var.delay_all['max']) # todo 