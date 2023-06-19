# 效能评估信息的处理发送
import paho.mqtt.client as mqtt
import asyncio
import time
import json
import threading

# speed

import logging
import sys
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s [%(levelname)s] %(message)s',stream=sys.stdout)
# mqtt client对象
client = mqtt.Client()

flows_msg = {}
packet_counting = {}
last_send_time_point = time.time()
total_bytes = 0
packet_result = {}

long_time_no_receive = {}

total_formal_cnt = 0

try:
    client.connect('192.168.0.100', 30004, 600)
except:
    while True:
        try:
            # client.connect('broker.emqx.io', 1883, 60)
            client.connect('162.105.85.167', 1883, 600)
            
            break
        except:
            print('retrying to connect broker.emqx.io ....')
            continue

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



class YourProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        global last_send_time_point
        global flows_msg
        global packet_counting
        global total_bytes, packet_result
        global total_formal_cnt
        # 处理数据
        # print(data)

        with open('status') as f:
            ok = f.read()

        ok = '1'
        if ok == '1':
            print('开始发送延迟')
            msg = data.decode('utf-8')
            payload = json.loads(msg) # 一个pod的传输信息
            # print(time.time(), payload)
            logging.debug(f'{time.time()} {payload}')
            # 1686895530.5503228 {'1': {'byte_num': 6936, 'id_list': [4265, 4266, 4267, 4268, 4269, 4270, 4271, 4272, 4273, 4274, 4275, 4276, 4277, 4278, 4279, 4280, 4281, 4282, 4283, 4284, 4285], 'last_min_max_delay_record': 1686895530, 'loss_rate': 0, 'max_delay': 141, 'max_packet_id': 4285, 'min_delay': 85, 'packet_num': 43, 'pod_id': '{}p[VOjCj%%"):DuBIOkAy^,X/)4[ZQdY9tN\\N^BLX6nG*==mAw[3p"!x%&OxP"p', 'sum_delay': 4457, 'total_packet_num': 43},
            # '2': {'byte_num': 1496, 'id_list': [2, 3, 1, 2], 'last_min_max_delay_record': 1686895298, 'loss_rate': 0, 'max_delay': 279, 'max_packet_id': 3, 'min_delay': 121, 'packet_num': 9, 'pod_id': '{}p[VOjCj%%"):DuBIOkAy^,X/)4[ZQdY9tN\\N^BLX6nG*==mAw[3p"!x%&OxP"p', 'sum_delay': 1562, 'total_packet_num': 9}, 
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


            #  [{ insid: {pod_id: [num, max_v], pod_id:[num, max_v]}, insid:... }, {...}] -> packet_num && max_v
            # 对每个insId求出packet_num和max_v，如果pod_id相同，packet_num和max_v直接覆盖
            # 否则packet_num相加求和，max_v取最大值
            # packet_counting {}
            # 如果是同一个pod发来的，总包数和最大id直接覆盖
            # 不同pod发来的，相加和求最大值

            def process_data(payload, result):
                for ins_id in payload:
                    if ins_id not in result:
                        result[ins_id] = {}

                    pod_id = payload[ins_id]['pod_id']
                    if pod_id not in result[ins_id]:
                        result[ins_id][pod_id] = [0, 0]

                    current_num, current_max = result[ins_id][pod_id]
                    incoming_num, incoming_max = [payload[ins_id]['total_packet_num'], payload[ins_id]['max_packet_id']]

                    result[ins_id][pod_id][0] = incoming_num
                    result[ins_id][pod_id][1] = max(current_max, incoming_max)
                    
                return result
            packet_result = process_data(payload, packet_result) 
            # for insId in payload: 
            #     v = payload[insId]
            #     if packet_counting.get(insId):
            #         for d in packet_counting[insId]:


            #     else:
            #         packet_counting[insId] = []
            #         packet_counting[insId].append({v['pod_id']: [v['total_packet_num'], v['max_packet_id']]})


            if time.time() - last_send_time_point > 2:
                print(f'formal send {(total_formal_cnt := total_formal_cnt + 1)}')
                if total_formal_cnt % 20 == 0:
                    try:
                        client.connect('192.168.0.100', 30004, 600)
                    except:
                        client.connect('162.105.85.167', 1883, 600)
                data_dict = []
                for insId in flows_msg:
                    # 丢包率检查
                    # logging.debug(f'packet_result: {packet_result}')
                    current_total_packet_num = sum([packet_result[insId][pod_id][0] for pod_id in packet_result[insId]])
                    current_max_packet_id = max([packet_result[insId][pod_id][1] for pod_id in packet_result[insId]])
                    # end
                    # id = flows_msg[insId]['pod_id']
                    # total_packet_num_for_each_flow += packet_counting[id][0]
                    v = flows_msg[insId]
                    def cal_through_out(v):
                        print('fff', v)
                        byte_num = 0
                        for pod_id in filter(lambda x: len(x) > 50, v):
                            byte_num += v[pod_id]['byte_num']

                        return round(byte_num / 1 / 1024, 2)
                    data_dict += [
                        {
                            "insId": int(insId),
                            "maxDelay": round(v['max_delay'] / 1000, 2) if v['max_delay'] > v['min_delay'] else v['min_delay'] + 0.8,
                            "minDelay": round(v['min_delay'] / 1000, 2),
                            "aveDelay": round(v['sum_delay'] / v['packet_num'] / 1000, 2),
                            "lossRate": cal_loss_rate(flows_msg, insId, cal_through_out(v)),
                            # "lossRate_old": round((1 - current_total_packet_num / (current_max_packet_id + 1)) * 100, 2), 
                            # "throughput": round(v['byte_num'] / 2 / 1024, 2), # kB/s
                            "throughput": cal_through_out(v), # kB/s
                            # "throughput": round(v['byte_num'] / (time.time() - last_send_time_point) / 1000, 2), # kB/s
                            "speed": -1
                        }
                    ]

                data_json = json.dumps({
                    "data": data_dict
                })
                # print('formal', time.time(), data_json, 'total bytes', total_bytes)

                logging.info(f'formal send: {time.time()} {data_json}, total bytes: {total_bytes}')
                topic = "/evaluation/business/endToEnd"
                client.publish(topic, data_json)

                last_send_time_point = time.time()
                long_time_no_receive = {}
                flows_msg = {}