
import paho.mqtt.client as mqtt
import asyncio


# mqtt client对象
client = mqtt.Client()

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
        # 处理数据
        # print(data)

        byte_str = data
        import struct
        with open('status') as f:
            ok = f.read()

        if ok == '1':
            int_list = struct.unpack('i'*(len(byte_str)//4), byte_str)
            print(int_list)
            print('total_loss: ', int_list[0])
            print('recent_loss: ', int_list[1])
            print('max_delay: ', int_list[2])
            print('min_delay: ', int_list[3])
            print('avg_delay: ', int_list[4])
            print('avg_speed: ', int_list[5])
            print('unused: ', int_list[6])
            print('unused: ', int_list[7])
            print('-------')

            print('开始发送延迟')

            delay_data = {
                "delayData": [
                    {
                        "insId": 1,
                        "maxDelay": {int_list[2]},
                        "minDelay": int_list[3],
                        "aveDelay": int_list[4], 
                        "speed": int_list[5] 
                    }
                ]
            }

            import json
            delay_data_json = json.dumps({
                "data": [
                    {
                        "insId": 1,
                        "maxDelay": int_list[2],
                        "minDelay": int_list[3],
                        "aveDelay": int_list[4], 
                        "lossRate": -120, 
                        "throughput": -15,
                        "speed": int_list[5] 
                    }
                ]
            })

            topic = "/evaluation/business/endToEnd"
            client.publish(topic, delay_data_json)
