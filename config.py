import time
class global_var:
    '''需要定义全局变量的放在这里，最好定义一个初始值'''
    name = 'my_name'
    server = None
    local_mqtt = False
    ue_status = []
    sat_status = {}
    service_table = []

    list_length = 12

    # wj
    ue_uplink_band = {}
    ue_downlink_band = {}
    # double id 
    sat_link_forward = {}
    sat_link_recv = {}
    sat_link = {}
    accumulate_ue_uplink = {}
    accumulate_ue_downlink = {}
    accumulate_sat_uplink = {}
    accumulate_sat_downlink = {}
    # evaluation
    throughput_all = []
    max_delay = {}
    min_delay = {}
    avg_delay = {}
    loss_rate = {}
    throughput = {}

class Status:
    current_source_and_destination = []
    current_ue_to_sat = {}
    id_to_source_and_dest = {}

class Mission:
    recv_num = 10
    info = []

    info_all = {"delay": [], "throughput": [], "loss_rate": []}

    delay_single = {i:[] for i in range(10)}
    throughput_single = {i:[] for i in range(10)}
    loss_rate_single = {i:[] for i in range(10)}

def set_id_to_source_and_dest(ins_id, source_id, destination_id):
    Status.id_to_source_and_dest[ins_id] = (source_id, destination_id)
    print('set_id_to_source_and_dest', Status.id_to_source_and_dest)

def get_id_to_source_and_dest(ins_id):
    print('50', ins_id)
    return Status.id_to_source_and_dest[ins_id]

def get_diff_list(my_list):
    time_diff = 5 # seconds
    return list(map(lambda x, y: (y - x) / time_diff, my_list[:-1], my_list[1:]))

def get_ue_uplink(ue_id):
    one_accumulate_ue_uplink = global_var.accumulate_ue_uplink[ue_id]
    return get_diff_list(one_accumulate_ue_uplink)

def get_ue_downlink(ue_id):
    one_accumulate_ue_downlink = global_var.accumulate_ue_downlink[ue_id]
    return get_diff_list(one_accumulate_ue_downlink)
# ue status
#  总共的包
# { "type": "ue", "id": 0, "time": 12328190, "access_sat": 11003, "up_link_bandwidth": 10000, "down_link_bandwidth": 10000, "up_link_packet": 20000000, "down_link_packet": 20000000, "up_link_byte": 200000000, "down_link_byte": 200000000, "location": { "longitude": 13.123, "latitude": 13.123, } }
# ue status
def get_ue_id_list():
    return [ue.id for ue in global_var.ue_status]

def get_real_ue_status():
    return global_var.ue_status

def get_ue_status():
    print('22',global_var.accumulate_ue_uplink)
    print('11', global_var.accumulate_ue_downlink)
    print('77 ', global_var.ue_status)
    try:
        print([{"ue_id": each_ue_status.id, "access_sat": each_ue_status.access_sat, "data": [each_ue_status.up_link_bandwidth, each_ue_status.down_link_bandwidth, get_ue_uplink(each_ue_status.id)[-1], get_ue_downlink(each_ue_status.id)[-1]]} for each_ue_status in global_var.ue_status])

        return [{"ue_id": each_ue_status.id, "access_sat": each_ue_status.access_sat, "data": [each_ue_status.up_link_bandwidth, each_ue_status.down_link_bandwidth, get_ue_uplink(each_ue_status.id)[-1] * 8 / 1024, get_ue_downlink(each_ue_status.id)[-1] * 8 / 1024]} for each_ue_status in global_var.ue_status]
    except:
        print('no ue table')
        return []

def set_ue_status(ue_status):
    global_var.ue_status.append(ue_status)
    should_remove = [ue for ue in global_var.ue_status if time.time() - ue.time > 5]
    for ue in should_remove:
        global_var.ue_status.remove(ue)

def set_ue_related_list(ue_status):
    id = ue_status.id
    check_id_exists_or_create_blank_list(id, global_var.accumulate_ue_uplink)
    check_id_exists_or_create_blank_list(id, global_var.accumulate_ue_downlink)
    update_display_list(ue_status.up_link_byte, global_var.accumulate_ue_uplink[id])
    update_display_list(ue_status.down_link_byte, global_var.accumulate_ue_downlink[id])

def get_ue_uplink_band(ue_id):
    return global_var.ue_uplink_band[ue_id]

def get_ue_downlink_band(ue_id):
    return global_var.ue_downlink_band[ue_id]

def check_id_exists_or_create_blank_list(id, a_dict):
    if id not in a_dict:
        a_dict[id] = []

# sat
def get_sat_uplink(sat_id):
    print('accu', global_var.accumulate_sat_uplink)
    check_id_exists_or_create_blank_list(sat_id, global_var.accumulate_sat_uplink)
    print('diff list', get_diff_list(global_var.accumulate_sat_uplink[sat_id]))
    return get_diff_list(global_var.accumulate_sat_uplink[sat_id])

def get_sat_downlink(sat_id):
    check_id_exists_or_create_blank_list(sat_id, global_var.accumulate_sat_downlink)
    return get_diff_list(global_var.accumulate_sat_downlink[sat_id])

def get_sat_status():
    return global_var.ue_status

def set_sat_status(sat_status):
    global_var.sat_status = sat_status

def set_sat_related_list(sat_status):
    id = sat_status.id
    check_id_exists_or_create_blank_list(id, global_var.accumulate_sat_downlink)
    check_id_exists_or_create_blank_list(id, global_var.accumulate_sat_uplink)

    update_display_list(sat_status.total_up_byte, global_var.accumulate_sat_uplink[id])
    update_display_list(sat_status.total_down_byte, global_var.accumulate_sat_downlink[id])

    for neighbor_sat in sat_status.neighbor_sat:
        check_id_exists_or_create_blank_list((id, neighbor_sat.id), global_var.sat_link_forward)

        update_display_list(neighbor_sat.forward_byte, global_var.sat_link_forward[id, neighbor_sat.id]) # todo forward 

def set_sat_link(sat_status):
    global_var.sat_link = [sat_neighbor.id for sat_neighbor in sat_status.neighbor_sat]

# 4, 两个卫星之间的
def get_sat_link_recv(id1, id2):
    return get_sat_link_recv[id1, id2]

def get_sat_link_forward(id1, id2):
    return get_sat_link_forward[id1, id2]

# 效能评估
def get_throughput_all():
    return global_var.throughput_all

def get_throughput(ins_id):
    return global_var.throughput[ins_id]

def get_loss_rate(ins_id):
    return global_var.loss_rate[ins_id]

def get_max_delay(ins_id):
    return global_var.max_delay[ins_id]

def get_min_delay(ins_id):
    return global_var.min_delay[ins_id]

def get_avg_delay(ins_id):
    return global_var.avg_delay[ins_id]

def get_loss_rate(ins_id):
    return global_var.loss_rate[ins_id]

def update_display_list(data, list, max_length = global_var.list_length):
    if len(list) >= max_length:
        list.pop(0)
    list.append(data)

def set_evaluator_for_each(data_dict):
    throughput_all_data = 0
    data_dict = data_dict.data
    for flow_msg in data_dict:
        ins_id = flow_msg.insId

        check_id_exists_or_create_blank_list(ins_id, global_var.throughput)
        check_id_exists_or_create_blank_list(ins_id, global_var.max_delay)
        check_id_exists_or_create_blank_list(ins_id, global_var.min_delay)
        check_id_exists_or_create_blank_list(ins_id, global_var.avg_delay)
        check_id_exists_or_create_blank_list(ins_id, global_var.loss_rate)

        update_display_list(flow_msg.throughput, global_var.throughput[ins_id])
        update_display_list(flow_msg.maxDelay, global_var.max_delay[ins_id])
        update_display_list(flow_msg.minDelay, global_var.min_delay[ins_id])
        update_display_list(flow_msg.aveDelay, global_var.avg_delay[ins_id])
        update_display_list(flow_msg.lossRate, global_var.loss_rate[ins_id])

        throughput_all_data += flow_msg.throughput
    update_display_list(throughput_all_data, global_var.throughput_all)

# chz
# service table
def get_service_table():
    print('service table:', global_var.service_table)
    return global_var.service_table

def set_service_table(data_dict):
    # try:
    global_var.service_table = []
    print('181 service table', data_dict)
    print('182 set_id_to_source_and_dest', Status.id_to_source_and_dest)
    data_dict = data_dict.data
    for data in data_dict:
        print('qwer', get_id_to_source_and_dest(data.insId))
        source_id, dest_id = get_id_to_source_and_dest(data.insId)
        global_var.service_table.append({"ins_id": data.insId, "source_id": source_id, "dest_id": dest_id, "data": [data.throughput, data.aveDelay, data.lossRate]})
    # except Exception as e:
    #     print('set_service_table', e)
    print('180 service table', global_var.service_table)

# gf

# other
def set_server(server):
    global_var.server = server

def get_server():
    return global_var.server

def set_local_mqtt(local_mqtt):
    global_var.local_mqtt = local_mqtt

def get_local_mqtt():
    return global_var.local_mqtt

# 目前运行的ue
def get_current_ue():
    return Status.current_source_and_destination

def set_current_ue(source, destination):
    Status.current_source_and_destination.append((source, destination))

# ue to sat
def set_current_ue_to_sat(ue_status):
    Status.current_ue_to_sat[ue_status.id] = ue_status.access_sat

def get_current_ue_to_sat(ue_id):
    return Status.current_ue_to_sat[ue_id]

# 使领馆
def set_mission_info(info):
    Mission.info = info

def get_mission_info():
    return Mission.info

def set_mission_related_list(mission_info):
    for i in range(Mission.recv_num):
        update_display_list(mission_info.interval[i], Mission.delay_single[i])
        update_display_list(mission_info.throughput[i], Mission.throughput_single[i])
        update_display_list(mission_info.loss[i], Mission.loss_rate_single[i])
    update_display_list(mission_info.avg_interval, Mission.info_all['delay'])
    update_display_list(mission_info.avg_loss, Mission.info_all['loss_rate'])
    update_display_list(mission_info.avg_throughput, Mission.info_all['throughput'])