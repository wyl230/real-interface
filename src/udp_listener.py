
import paho.mqtt.client as mqtt
import asyncio
import time
import json

# speed

# mqtt client对象
client = mqtt.Client()

flows_msg = {}
packet_counting = {}
last_send_time_point = time.time()
total_bytes = 0
packet_result = {}

try:
    client.connect('192.168.0.100', 30004, 60)
except:
    while True:
        try:
            # client.connect('broker.emqx.io', 1883, 60)
            client.connect('162.105.85.167', 1883, 60)
            
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

class YourProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        global last_send_time_point
        global flows_msg
        global packet_counting
        global total_bytes, packet_result
        # 处理数据
        # print(data)

        with open('status') as f:
            ok = f.read()

        ok = '1'
        if ok == '1':
            print('开始发送延迟')
            msg = data.decode('utf-8')
            payload = json.loads(msg) # 一个pod的传输信息
            print(time.time(), payload)
            # {'1': {'byte_num': 10152, 'last_min_max_delay_record': 1686383148, 'loss_rate': 536870912, 'max_delay': 129, 'min_delay': 57, 'packet_num': 47, 'sum_delay': 3490}}
            for insId in payload: # key = 业务流id
                if flows_msg.get(insId):
                    value = flows_msg[insId]
                    value['byte_num'] += payload[insId]['byte_num']
                    value['loss_rate'] += payload[insId]['loss_rate'] # todo 
                    value['max_delay'] = max(payload[insId]['max_delay'], value['max_delay'])
                    value['min_delay'] = min(payload[insId]['min_delay'], value['min_delay'])
                    value['packet_num'] += payload[insId]['packet_num']
                    value['sum_delay'] += payload[insId]['sum_delay']
                    total_bytes += payload[insId]['byte_num']
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
                print('formal send')
                for insId in flows_msg:
                    # 丢包率检查
                    print('packet_result', packet_result)
                    current_total_packet_num = sum([packet_result[insId][pod_id][0] for pod_id in packet_result[insId]])
                    current_max_packet_id = max([packet_result[insId][pod_id][1] for pod_id in packet_result[insId]])
                    # end
                    # id = flows_msg[insId]['pod_id']
                    # total_packet_num_for_each_flow += packet_counting[id][0]
                    v = flows_msg[insId]
                    data_json = json.dumps({
                        "data": [
                            {
                                "insId": int(insId),
                                "maxDelay": v['max_delay'],
                                "minDelay": v['min_delay'],
                                "aveDelay": v['sum_delay'] / v['packet_num'],
                                "lossRate": 1 - current_total_packet_num / (current_max_packet_id + 1), 
                                "throughput": v['byte_num'] / (time.time() - last_send_time_point) / 1000, # KBps
                                "speed": -1
                            }
                        ]
                    })
                    print('formal', time.time(), data_json, 'total bytes', total_bytes)

                    topic = "/evaluation/business/endToEnd"
                    client.publish(topic, data_json)
                last_send_time_point = time.time()
                flows_msg = {}
