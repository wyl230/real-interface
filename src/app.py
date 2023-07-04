# app文件，定义接口路由，mqtt示例

import multiprocessing
import paho.mqtt.client as mqtt

from fastapi import FastAPI
import json
from . import routes
import config

# cors problems
from fastapi.middleware.cors import CORSMiddleware
api = FastAPI()
origins = ["*"]
api.add_middleware( CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)
# 

client = mqtt.Client()

# 路由
api.include_router(routes.router, prefix='', tags=['real-paths'])

# mqtt消息测试：mosquitto_pub -h broker.emqx.io -t test_w -m "Hello World22222"
def consume_topic():
    # 指定回调函数
    client.on_connect = on_connect
    client.on_message = on_message
    # 建立连接

    if config.get_local_mqtt():
        client.connect('162.105.85.167', 1883, 600)
    else:
        client.connect('192.168.0.100', 30004, 600)

    # 发布消息
    # client.publish(topic='test_w', payload='wwwwwww', qos=0)
    # client.publish(topic='testtopic/1', payload='Hello World11111', qos=0)
    client.loop_forever()

# 消息接收回调
def on_message(bind_client, userdata, msg):
    try:
        print('mqtt message:', msg.topic + " " + str(msg.payload, encoding="utf-8"))
    except:
        print(msg.topic, '===', msg.payload)
    # client.publish(topic='test_w', payload='wwwwwww', qos=0)

    # if init: on_init() init = False print('-----')

    if msg.topic == '/simulation/command':
        on_command(msg.payload)

# 连接成功回调
def on_connect(bind_client, userdata, flags, rc):
    print('Connected with result code ' + str(rc))
    # client.subscribe('test_w/#')
    client.subscribe('/simulation/init')
    client.subscribe('/simulation/command')
    # client.subscribe('testtopic/#')

# 接口5，系统命令：启动/停止
# 测试：mosquitto_pub -h broker.emqx.io -t /simulation/command -m '{"command": "1"}'
def on_command(payload):
    print(payload)
    command = json.loads(payload)
    if command['command'] == '1':
        print('启动')
    elif command['command'] == '0':
        print('暂停')

# 工程启动时开启mqtt订阅
@api.on_event("startup")
def before_start():
    mp = multiprocessing.Process(target=consume_topic)
    mp.start()

