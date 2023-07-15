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
    service_table = []

    list_length = 12

    ## ue
    ue_status = []
    ue_uplink_band = {}
    ue_downlink_band = {}
    accumulate_ue_uplink = {}
    accumulate_ue_downlink = {}
    ## sat
    sat_status = {}
    sat_link = {}
    # double id 
    accumulate_sat_uplink = {}
    accumulate_sat_downlink = {}
    sat_total_uplink = {}
    sat_total_downlink = {}

    # evaluation
    throughput_all = []
    max_delay = {}
    min_delay = {}
    avg_delay = {}
    loss_rate = {}
    throughput = {}

    # ue and sat 推数据间隔
    time_diff = 5 # seconds

class AdjacentSat:
    accumulate_sat_link_forward = {} # {(1,2): kbps}
    accumulate_sat_link_recv = {}

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
    logger.info(f'set_id_to_source_and_dest {Status.id_to_source_and_dest}')

def del_id_to_source_and_dest(ins_id, source_id, destination_id):
    if Status.id_to_source_and_dest[ins_id] == (source_id, destination_id) or source_id == -1:
        Status.id_to_source_and_dest.pop(ins_id)
        logger.info(f'del_id_to_source_and_dest {Status.id_to_source_and_dest}')

def get_id_to_source_and_dest(ins_id):
    return Status.id_to_source_and_dest[ins_id]

def get_diff_list(my_list, divider=1):
    return list(map(lambda x, y: (y - x) / global_var.time_diff / divider, my_list[:-1], my_list[1:]))

def get_diff_list_with_timestamp(my_list, divider=1):
    data_list = [i[0] for i in my_list]
    timestamp_list = [i[1] for i in my_list]
    return list(map(lambda x, y, time_a, time_b: (y - x) / (time_b - time_a) / divider, data_list[:-1], data_list[1:], timestamp_list[:-1], timestamp_list[1:]))

def get_ue_uplink(ue_id):
    one_accumulate_ue_uplink = global_var.accumulate_ue_uplink[ue_id]
    return get_diff_list_with_timestamp(one_accumulate_ue_uplink, divider= 1 / 8 * 1024)

def get_ue_downlink(ue_id):
    one_accumulate_ue_downlink = global_var.accumulate_ue_downlink[ue_id]
    return get_diff_list_with_timestamp(one_accumulate_ue_downlink, divider=1 / 8 * 1024)
# ue status
#  总共的包
# { "type": "ue", "id": 0, "time": 12328190, "access_sat": 11003, "up_link_bandwidth": 10000, "down_link_bandwidth": 10000, "up_link_packet": 20000000, "down_link_packet": 20000000, "up_link_byte": 200000000, "down_link_byte": 200000000, "location": { "longitude": 13.123, "latitude": 13.123, } }
# ue status
def get_ue_id_list():
    return [ue.id for ue in global_var.ue_status]

def get_real_ue_status():
    return global_var.ue_status

def get_ue_status():
    logger.debug(f'22 accumulate_ue_uplink, {global_var.accumulate_ue_uplink}')
    logger.debug(f'11 accumulate_ue_downlink, {global_var.accumulate_ue_downlink}')
    logger.debug(f'77 global_var.ue_status, {global_var.ue_status}')
    # try:
    res = []
    for each_ue_status in global_var.ue_status:
        res.append({"ue_id": each_ue_status.id, "access_sat": each_ue_status.access_sat, "data": [each_ue_status.up_link_bandwidth / 1024, each_ue_status.down_link_bandwidth / 1024, get_ue_uplink(each_ue_status.id)[-1], get_ue_downlink(each_ue_status.id)[-1]]})

    return res

    # except:
    #     logger.info('no ue table')
    #     return []

def set_ue_status(ue_status):
    global_var.ue_status.append(ue_status)
    should_remove = [ue for ue in global_var.ue_status if time.time() - ue.time > 5]
    for ue in should_remove:
        global_var.ue_status.remove(ue)

def set_ue_related_list(ue_status):
    id = ue_status.id
    check_id_exists_or_create_blank_list(id, global_var.accumulate_ue_uplink)
    check_id_exists_or_create_blank_list(id, global_var.accumulate_ue_downlink)
    update_display_list((ue_status.up_link_byte, ue_status.time), global_var.accumulate_ue_uplink[id])
    update_display_list((ue_status.down_link_byte, ue_status.time), global_var.accumulate_ue_downlink[id])

def get_ue_uplink_band(ue_id):
    # logger.info('1359', global_var.ue_uplink_band)
    # logger.info('1356', global_var.ue_uplink_band)
    return global_var.ue_uplink_band[ue_id]

def get_ue_downlink_band(ue_id):
    return global_var.ue_downlink_band[ue_id]

def check_id_exists_or_create_blank_list(id, a_dict):
    if id not in a_dict:
        a_dict[id] = []

# sat
def get_sat_uplink(sat_id):
    # logger.info('accu', global_var.accumulate_sat_uplink)
    check_id_exists_or_create_blank_list(sat_id, global_var.accumulate_sat_uplink)
    # logger.info('diff list', get_diff_list(global_var.accumulate_sat_uplink[sat_id]))
    return get_diff_list(global_var.accumulate_sat_uplink[sat_id], divider= 1024 / 8)

def get_sat_downlink(sat_id):
    check_id_exists_or_create_blank_list(sat_id, global_var.accumulate_sat_downlink)
    return get_diff_list(global_var.accumulate_sat_downlink[sat_id], divider= 1024 / 8)

def get_single_sat_status(sat_id):
    return global_var.sat_status[sat_id]

def get_sat_status():
    return global_var.sat_status

def set_sat_status(sat_status):
    global_var.sat_total_downlink[sat_status.id] = sat_status.total_down_bandwidth
    global_var.sat_total_uplink[sat_status.id] = sat_status.total_up_bandwidth
    global_var.sat_status[sat_status.id] = sat_status
    return # todo 不需要存储相关信息
    global_var.sat_status[sat_status.id] = sat_status
    global_var.sat_status.append(sat_status)
    should_remove = [sat for sat in global_var.sat_status if time.time() - sat.time > 5]
    for sat in should_remove:
        global_var.sat_status.remove(sat)

    # todo global_var.sat_status = sat_status 

def get_sat_total_uplink(sat_id):
    return global_var.sat_total_uplink[sat_id]

def get_sat_total_downlink(sat_id):
    return global_var.sat_total_downlink[sat_id]

def check_list_using_list(id_list, list_list):
    for id, list in zip(id_list, list_list):
        check_id_exists_or_create_blank_list(id, list)


def set_sat_related_list(sat_status):
    sat_id = sat_status.id
    check_list_using_list([sat_id] * 2, [global_var.accumulate_sat_downlink, global_var.accumulate_sat_uplink])

    update_display_list(sat_status.total_up_byte, global_var.accumulate_sat_uplink[sat_id])
    update_display_list(sat_status.total_down_byte, global_var.accumulate_sat_downlink[sat_id])

    for neighbor_sat in sat_status.neighbor_sat:
        check_list_using_list([(sat_id, neighbor_sat.id)] * 2, [AdjacentSat.accumulate_sat_link_forward, AdjacentSat.accumulate_sat_link_recv])

        update_display_list(neighbor_sat.forward_byte, AdjacentSat.accumulate_sat_link_forward[sat_id, neighbor_sat.id]) 
        update_display_list(neighbor_sat.receive_byte, AdjacentSat.accumulate_sat_link_recv[sat_id, neighbor_sat.id]) 

def set_sat_link(sat_status):
    global_var.sat_link[sat_status.id] = [sat_neighbor.id for sat_neighbor in sat_status.neighbor_sat]

def delete_old_sat_link_data(list):
    last = -1
    remain_id = 0
    for i, j in zip(range(len(list)), list):
        if last >= j:
            remain_id = i
        last = j
    list = list[remain_id:]

# 4, 两个卫星之间的
def get_sat_link_recv(id1, id2):
    # 处理，如果链路之间字节数大于新的字节数，清空之前的
    # logger.info('recv', AdjacentSat.accumulate_sat_link_recv)
    delete_old_sat_link_data(AdjacentSat.accumulate_sat_link_recv[id1, id2])
    return get_diff_list(AdjacentSat.accumulate_sat_link_recv[id1, id2], divider=1 / 8 * 1024)

def get_sat_link_forward(id1, id2):
    # logger.info('forward', AdjacentSat.accumulate_sat_link_forward)
    delete_old_sat_link_data(AdjacentSat.accumulate_sat_link_forward[id1, id2])
    return get_diff_list(AdjacentSat.accumulate_sat_link_forward[id1, id2], divider=1 / 8 * 1024)

def get_sat_link(sat_id):
    return global_var.sat_link[sat_id]

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
    logger.info(f'service table:, {global_var.service_table}')
    return global_var.service_table

def set_service_table(data_dict):
    # try:
    global_var.service_table = []
    logger.debug('181 service table', data_dict)
    logger.debug('182 set_id_to_source_and_dest', Status.id_to_source_and_dest)
    data_dict = data_dict.data
    for data in data_dict:
        logger.info('qwer', get_id_to_source_and_dest(data.insId))
        source_id, dest_id = get_id_to_source_and_dest(data.insId)
        global_var.service_table.append({"ins_id": data.insId, "source_id": source_id, "dest_id": dest_id, "data": [data.throughput, data.aveDelay, data.lossRate]})
    # except Exception as e:
    #     logger.info('set_service_table', e)
    logger.debug('180 service table', global_var.service_table)

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

def del_current_ue(source, destination):
    Status.current_source_and_destination.remove((source, destination))

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

def get_mission_info_throughput(id):
    return Mission.throughput_single[id]

def get_mission_info_loss_rate(id):
    return Mission.loss_rate_single[id]

def get_mission_info_delay(id):
    return Mission.delay_single[id]

def get_mission_info_all():
    return {"delay": Mission.info_all['delay'], "throughput": Mission.info_all['throughput'], "loss_rate": Mission.info_all['loss_rate']}


def get_timestamp_list(length, time):
    return [time - 2 * (length - 1 - i)  for i in range(length)]