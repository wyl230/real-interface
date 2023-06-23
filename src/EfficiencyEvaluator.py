# 效能评估信息的处理发送
import paho.mqtt.client as mqtt
import asyncio
import time
import json
import config
import threading

# speed

import logging
import sys
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s [%(levelname)s] %(message)s',stream=sys.stdout)

flows_msg = {}
packet_counting = {}
last_send_time_point = time.time()
total_bytes = 0

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

async def udp_listener():
    print('udp...')
    if config.get_local_matt():
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

    threshold = 300 if (throughput - 10) < 5 else 1500 if (throughput - 260) < 50 else 10000

    if cur_send_packet_id - cur_receive_packet_id > threshold:
        return True
    return False

def cal_loss_rate(flows_msg, ins_id, throughput):
    id_list = flows_msg[ins_id]['id_list']
    try:
        id_list = sorted(list(set(id_list))) # 去重并排序
        print('id list, rignt', id_list)
    except:
        print(id_list, 'error')
        return round(0, 2)

    count = 0

    # if if_long_time_no_receive(ins_id, id_list[-1], throughput):
    #     return round(100, 2)

    for i in range(1, len(id_list)):
        if id_list[i] <= id_list[i-1]:
            count += (id_list[i] - id_list[i-1] - 1)
    
    return round(count / len(id_list), 2)


def cal_through_out(v):
    print('fff', v)
    byte_num = 0
    for pod_id in filter(lambda x: len(x) > 50, v):
        byte_num += v[pod_id]['byte_num']

    return round(byte_num / 1 / 1024, 2)

def update_flow_msg(payload):
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
        if config.get_local_matt():
            client.connect('162.105.85.167', 1883, 600)
        else:
            client.connect('192.168.0.100', 30004, 600)

    def reinit(self):
        global last_send_time_point
        global flows_msg
        last_send_time_point = time.time()
        long_time_no_receive = {}
        flows_msg = {}

    def send_mqtt(self, data_dict):
        global total_formal_cnt
        print(f'formal send {(total_formal_cnt := total_formal_cnt + 1)}')

        if total_formal_cnt % 20 == 0:
            self.reconnect_mqtt()

        data_json = json.dumps({ "data": data_dict })
        # print('formal', time.time(), data_json, 'total bytes', total_bytes)

        logging.info(f'formal send: {time.time()} {data_json}, total bytes: {total_bytes}')
        topic = "/evaluation/business/endToEnd"
        client.publish(topic, data_json)

    def send_message_generate(self):
        global flows_msg

        data_dict = []
        for insId in flows_msg:
            # id = flows_msg[insId]['pod_id']
            # total_packet_num_for_each_flow += packet_counting[id][0]
            v = flows_msg[insId]
            data_dict += [
                {
                    "insId": int(insId),
                    "maxDelay": round(v['max_delay'] / 1000, 2) if v['max_delay'] > v['min_delay'] else v['min_delay'] + 0.8,
                    "minDelay": round(v['min_delay'] / 1000, 2),
                    "aveDelay": round(v['sum_delay'] / v['packet_num'] / 1000, 2),
                    "lossRate": cal_loss_rate(flows_msg, insId, cal_through_out(v)),
                    # "throughput": round(v['byte_num'] / 2 / 1024, 2), # kB/s
                    "throughput": cal_through_out(v), # kB/s
                    # "throughput": round(v['byte_num'] / (time.time() - last_send_time_point) / 1000, 2), # kB/s
                    "speed": -1
                }
            ]
        return data_dict

    def datagram_received(self, data, addr):
        global last_send_time_point

        print('开始发送延迟')
        msg = data.decode('utf-8')
        payload = json.loads(msg) # 一个pod的传输信息
        logging.debug(f'{time.time()} {payload}') # 1686895530.5503228 {'1': {'byte_num': 6936, 'id_list': [4265, 4266, 4267, 4268, 4269, 4270, 4271, 4272, 4273, 4274, 4275, 4276, 4277, 4278, 4279, 4280, 4281, 4282, 4283, 4284, 4285], 'last_min_max_delay_record': 1686895530, 'loss_rate': 0, 'max_delay': 141, 'max_packet_id': 4285, 'min_delay': 85, 'packet_num': 43, 'pod_id': '{}p[VOjCj%%"):DuBIOkAy^,X/)4[ZQdY9tN\\N^BLX6nG*==mAw[3p"!x%&OxP"p', 'sum_delay': 4457, 'total_packet_num': 43}, '2': {'byte_num': 1496, 'id_list': [2, 3, 1, 2], 'last_min_max_delay_record': 1686895298, 'loss_rate': 0, 'max_delay': 279, 'max_packet_id': 3, 'min_delay': 121, 'packet_num': 9, 'pod_id': '{}p[VOjCj%%"):DuBIOkAy^,X/)4[ZQdY9tN\\N^BLX6nG*==mAw[3p"!x%&OxP"p', 'sum_delay': 1562, 'total_packet_num': 9}, 

        update_flow_msg(payload)

        if time.time() - last_send_time_point > 2:
            self.send_mqtt(self.send_message_generate())
            self.reinit()