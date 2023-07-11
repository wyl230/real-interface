# 效能评估信息的处理发送
import paho.mqtt.client as mqtt
import asyncio
import time
import json
import requests
import config
import threading

# speed

from loguru import logger
import sys

last_list_expand = []

flows_msg = {}
packet_counting = {}
last_send_time_point = time.time()
total_bytes = 0
ins_last_send_time = {}

long_time_no_receive = {}

total_formal_cnt = 0
client = mqtt.Client()

ok = False

def run_udp_listener():
    global ok
    print('ok change')
    ok = True

def stop_udp_listener():
    global ok
    ok = False

def check_time_out():
    global total_formal_cnt
    while True:
        time.sleep(1)
        logger.debug(f'check time out: ins_last_send_time  {ins_last_send_time}')
        data_dict = []
        should_pop_id = []

        for ins_id in ins_last_send_time:
            if time.time() - ins_last_send_time[ins_id] >= 7:
                data_dict += [ { "insId": int(ins_id), "maxDelay": 0, "minDelay": 0, "aveDelay": 0, "lossRate": 100, "throughput": 0, "speed": -1 } ]
                should_pop_id.append(ins_id)
        if not data_dict:
            continue
        data_json = json.dumps({ "data": data_dict })
        # print('formal', time.time(), data_json, 'total bytes', total_bytes)
        for ins_id in should_pop_id:
            ins_last_send_time.pop(ins_id)

        logger.debug(f'formal send: {time.time()} {data_json}, total bytes: {total_bytes}')
        topic = "/evaluation/business/endToEnd"
        client.publish(topic, data_json)

async def udp_listener():
    print('udp...')
    threading.Thread

    t2 = threading.Thread(target=check_time_out)
    t2.start()

    if config.get_local_mqtt():
        client.connect('162.105.85.167', 1883, 600)
    else:
        client.connect('192.168.0.100', 30004, 600)
    YourPort = 9002
    # 创建UDP连接
    transport, protocol = await asyncio.get_running_loop().create_datagram_endpoint(
        lambda: YourProtocol(),
        local_addr=('0.0.0.0', YourPort)
    )

    # 持续等待消息
    while True:
        await asyncio.sleep(0.1)

    # 关闭连接
    transport.close()

def get_ok():
    global ok
    return ok

def if_long_time_no_receive(ins_id, cur_receive_packet_id, throughput):
    cur_send_packet_id = 0
    with open('packet_id.json') as f:
        j = json.load(f)
        cur_send_packet_id = j[str(ins_id)]

    # 音频流 50pps
    # 视频流 222pps
    # 8s收不到包报丢包率100%
    time_out = 8
    cbr_pps = 50
    vbr_pps = 222
    threshold = cbr_pps * time_out if (throughput - 10) < 5 else 1500 if (throughput - 260) < 50 else 10000

    if cur_send_packet_id - cur_receive_packet_id > threshold:
        return True
    return False


def count_discontinuous(sequence):
    count = 0
    for i in range(len(sequence) - 1):
        if sequence[i] + 1 != sequence[i + 1]:
            count += sequence[i + 1] - sequence[i] - 1
    return count

def cal_loss_rate(flows_msg, ins_id, packet_num):
    # return 0
    global last_list_expand
    try:
        id_list = flows_msg[ins_id]['id_list']
        print("packet seqence: ", id_list)

        # 计算丢包时，计算的包id 是 上一个id list没有经过计算的部分，和本次id list需要计算的部分
        save = 0.1 # 表示对于一个id list的展开版本 不会计算后 10% 部分的数据
        startid = 0
        # 展开id list 并进行排序
        list_expand = [] # 1-3展开的list = [1 2 3]

        for index in range(int(len(id_list)/3)):
            a = id_list[index*3]
            b = id_list[index*3 + 2]
            while a != b :
                list_expand.append(a)
                a = a + 1
            list_expand.append(b)
        list_expand.sort() # 排序
        # print(list_expand) # 输出本次的id list
        num = int(len(list_expand) * (1 - save)) # 本个list需要计算的包数 = 前 90%
        pack_num = num + len(last_list_expand) # 本次计算的包数 = 上个list剩下的 + 本个list需要计算的
        calcu_list = last_list_expand + list_expand[:num]
        last_list_expand = list_expand[num:]
        calcu_list.sort()
        # print('calcu', calcu_list)
        loss_num = count_discontinuous(calcu_list)
        return round(loss_num / (calcu_list[-1] - calcu_list[0]) * 100, 2)
    except Exception as e:
        print(f'loss rate error {e}')
        return -1


def cal_throughput(v):
    logger.debug('fff', v)
    byte_num = 0
    for pod_id in filter(lambda x: len(x) > 50, v):
        byte_num += v[pod_id]['byte_num']

    return round(byte_num / 1 / 1024, 2)

def update_flow_msg(payload):
    global total_bytes
    for insId in payload: # key = 业务流id
        if flows_msg.get(insId):
            value = flows_msg[insId]
            pod_id = payload[insId]['pod_id']
            if pod_id not in value:
                value[pod_id] = {}
            value[pod_id]['byte_num'] = payload[insId]['byte_num']
            value['loss_rate'] += payload[insId]['loss_rate'] # todo 
            value['max_delay'] = max(payload[insId]['max_delay'], value['max_delay'])
            value['min_delay'] = min(payload[insId]['min_delay'], value['min_delay'])
            value['packet_num'] += payload[insId]['packet_num']
            value['sum_delay'] += payload[insId]['sum_delay']
            total_bytes += payload[insId]['byte_num']
            try: 
                value['id_list'] += payload[insId]['id_list']
            except:
                value['id_list'] = payload[insId]['id_list']
        else:
            flows_msg[insId] = payload[insId]

class YourProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def reconnect_mqtt(self):
        if config.get_local_mqtt():
            client.connect('162.105.85.167', 1883, 600)
        else:
            client.connect('192.168.0.100', 30004, 600)

    def reinit(self):
        global last_send_time_point
        global flows_msg
        global long_time_no_receive
        last_send_time_point = time.time()
        long_time_no_receive = {}
        flows_msg = {}

    def send_mqtt(self, data_dict):
        global total_formal_cnt
        logger.info(f'formal send {(total_formal_cnt := total_formal_cnt + 1)}')

        if total_formal_cnt % 20 == 0:
            self.reconnect_mqtt()

        data_json = json.dumps({ "data": data_dict })
        # print('formal', time.time(), data_json, 'total bytes', total_bytes)

        logger.debug(f'formal send: {time.time()} {data_json}, total bytes: {total_bytes}')
        topic = "/evaluation/business/endToEnd"
        client.publish(topic, data_json)

    def addDictTimeoutFlow(self, data_dict):
        for ins_id in ins_last_send_time:
            if ins_last_send_time[ins_id] - time.time() >= 7:
                data_dict += [
                    {
                        "insId": int(ins_id),
                        "maxDelay": 0,
                        "minDelay": 0,
                        "aveDelay": 0,
                        "lossRate": 100,
                        "throughput": 0,
                        "speed": -1
                    }
                ]

    def update_ins_last_send_time(self):
        global flows_msg
        for insId in flows_msg:
            ins_last_send_time[insId] = time.time()

    def send_message_generate(self):
        global flows_msg

        data_dict = []
        for insId in flows_msg:
            # id = flows_msg[insId]['pod_id']
            # total_packet_num_for_each_flow += packet_counting[id][0]
            v = flows_msg[insId]
            if v['packet_num'] == 0: 
                continue
            data_dict += [
                {
                    "insId": int(insId),
                    "maxDelay": round(v['max_delay'] / 1000, 2) if v['max_delay'] > v['min_delay'] else v['min_delay'] + 0.8,
                    "minDelay": round(v['min_delay'] / 1000, 2),
                    "aveDelay": round(v['sum_delay'] / v['packet_num'] / 1000, 2),
                    "lossRate": cal_loss_rate(flows_msg, insId, v['packet_num']),
                    # "throughput": round(v['byte_num'] / 2 / 1024, 2), # kB/s
                    "throughput": cal_throughput(v) * 8, # kB/s
                    # "throughput": round(v['byte_num'] / (time.time() - last_send_time_point) / 1000, 2), # kB/s
                    "speed": -1
                }
            ]
        self.update_ins_last_send_time()
        self.addDictTimeoutFlow(data_dict)


        print('eva config service table ')
        data = {"data": data_dict}
        print(data)
        headers = { 
            'Accept': 'application/json',
            "Content-Type": "application/json; charset=UTF-8", }
        # r = requests.post("http://162.105.85.70:32549/set_service_table_and_evaluator_for_each", headers=headers, verify=False, data='''{"data": [{"insId": 4, "maxDelay": 232.85, "minDelay": 84.34, "aveDelay": 91.99, "lossRate": 0.0, "throughput": 21.44, "speed": -1}]}''') # todo 地址修改
        r = requests.post("http://162.105.85.70:32549/set_service_table_and_evaluator_for_each", headers=headers, verify=False, data=json.dumps(data)) # todo 地址修改
        print(r)
        print('eva config service table end')

        return data_dict

    def datagram_received(self, data, addr):
        global last_send_time_point

        msg = data.decode('utf-8')
        payload = json.loads(msg) # 一个pod的传输信息
        logger.debug(f'{time.time()} {payload}') # 1686895530.5503228 {'1': {'byte_num': 6936, 'id_list': [4265, 4266, 4267, 4268, 4269, 4270, 4271, 4272, 4273, 4274, 4275, 4276, 4277, 4278, 4279, 4280, 4281, 4282, 4283, 4284, 4285], 'last_min_max_delay_record': 1686895530, 'loss_rate': 0, 'max_delay': 141, 'max_packet_id': 4285, 'min_delay': 85, 'packet_num': 43, 'pod_id': '{}p[VOjCj%%"):DuBIOkAy^,X/)4[ZQdY9tN\\N^BLX6nG*==mAw[3p"!x%&OxP"p', 'sum_delay': 4457, 'total_packet_num': 43}, '2': {'byte_num': 1496, 'id_list': [2, 3, 1, 2], 'last_min_max_delay_record': 1686895298, 'loss_rate': 0, 'max_delay': 279, 'max_packet_id': 3, 'min_delay': 121, 'packet_num': 9, 'pod_id': '{}p[VOjCj%%"):DuBIOkAy^,X/)4[ZQdY9tN\\N^BLX6nG*==mAw[3p"!x%&OxP"p', 'sum_delay': 1562, 'total_packet_num': 9}, 

        update_flow_msg(payload)

        if time.time() - last_send_time_point > 2:
            self.send_mqtt(self.send_message_generate())
            self.reinit()
