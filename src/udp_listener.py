
import paho.mqtt.client as mqtt
import asyncio
import time
import json


# mqtt client对象
client = mqtt.Client()

flows_msg = {}
last_send_time_point = time.time()

try:
    client.connect('192.168.0.100', 30004, 60)
except:
    while True:
        try:
            client.connect('broker.emqx.io', 1883, 60)
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
        # 处理数据
        # print(data)

        with open('status') as f:
            ok = f.read()

        ok = '1'
        if ok == '1':
            print('开始发送延迟')
            msg = data.decode('utf-8')
            payload = json.loads(msg)
            print(payload)
            # {'1': {'byte_num': 10152, 'last_min_max_delay_record': 1686383148, 'loss_rate': 536870912, 'max_delay': 129, 'min_delay': 57, 'packet_num': 47, 'sum_delay': 3490}}
            for key in payload:
                if flows_msg.get(key):
                    value = flows_msg[key]
                    value['byte_num'] += payload[key]['byte_num']
                    value['loss_rate'] += payload[key]['loss_rate'] # todo 
                    value['max_delay'] = max(payload[key]['max_delay'], value['max_delay'])
                    value['min_delay'] = min(payload[key]['min_delay'], value['min_delay'])
                    value['packet_num'] += payload[key]['packet_num']
                    value['sum_delay'] += payload[key]['sum_delay']
                else:
                    flows_msg[key] = payload[key]


            if time.time() - last_send_time_point > 2:
                print('formal send')
                for key in flows_msg:
                    v = flows_msg[key]
                    data_json = json.dumps({
                        "data": [
                            {
                                "insId": int(key),
                                "maxDelay": v['max_delay'],
                                "minDelay": v['min_delay'],
                                "aveDelay": v['sum_delay'] / v['packet_num'],
                                "lossRate": -1, 
                                "throughput": v['byte_num'] / (time.time() - last_send_time_point) / 1000, # KBps
                                "speed": -1
                            }
                        ]
                    })
                    print('formal', data_json)

                    topic = "/evaluation/business/endToEnd"
                    client.publish(topic, data_json)
                last_send_time_point = time.time()
                flows_msg = {}
