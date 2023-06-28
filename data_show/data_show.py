import paho.mqtt.client as mqtt
import time
import json
import random
import matplotlib.pyplot as plt
import pywebio
from pywebio import start_server
from pywebio.output import put_html, put_image, clear, put_text
from pywebio.input import *
from pywebio.session import set_env, run_js
from io import BytesIO

max_delay = []
min_delay = []
avg_delay = []
throughput = []

ins_id = 0

def on_message(client, userdata, msg):
    global data
    global ins_id
    # print(msg.payload)
    j = json.loads(msg.payload)
    print(f'业务条数 {len(j["data"])}')
    max_delay.append(j['data'][ins_id]['maxDelay'])
    min_delay.append(j['data'][ins_id]['minDelay'])
    avg_delay.append(j['data'][ins_id]['aveDelay'])
    throughput.append(j['data'][ins_id]['throughput'])

def mqtt_subscribe():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("162.105.85.167", 1883, 60)
    client.subscribe("/evaluation/business/endToEnd", qos=0)
    client.loop_start()

data = []

def generate_data(data, length):
    y = [0] * length
    if len(data) < length:
        y = [0] * (length - len(data)) + data
    else:
        y = data[-length:]
    return y


def draw_dynamic_chart():
    plt.ion()  # 打开交互模式

    # 创建初始的空图表
    fig, ax = plt.subplots()
    fig2, ax_throughput = plt.subplots()

    line1, = ax.plot([], [], label='max delay')  # 创建一个空线段对象
    line2, = ax.plot([], [], label='min delay')  # 创建一个空线段对象
    line3, = ax.plot([], [], label='avg delay')  # 创建一个空线段对象

    line4, = ax_throughput.plot([], [], label='avg delay')  # 创建一个空线段对象
    ax.set_xlabel('time(s)')
    ax.set_ylabel('delay(ms)')

    ax_throughput.set_xlabel('time(s)')
    ax_throughput.set_ylabel('kB/s')

    # 生成随机数据并实时更新图表
    while True:
        length = max(len(max_delay), 6)
        length = min(length, 30)
        x = list(range(length))  # X轴数据
        line1.set_data(x, generate_data(max_delay, length))  
        line2.set_data(x, generate_data(min_delay, length))  
        line3.set_data(x, generate_data(avg_delay, length))  


        ax.relim()  # 重新计算数据范围
        ax.autoscale_view()  # 自动调整坐标轴范围
        buffer = BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        put_text('dalay')

        clear()

        put_image(buffer.getvalue(), width='400px', height='300px')

        line4.set_data(x, generate_data(throughput, length))  
        ax_throughput.relim()  # 重新计算数据范围
        ax_throughput.autoscale_view()  # 自动调整坐标轴范围

        buffer = BytesIO()
        fig2.savefig(buffer, format='png')
        buffer.seek(0)

        put_text('throughput')
        put_image(buffer.getvalue(), width='400px', height='300px')

        time.sleep(1.8)  # 延时1秒

if __name__ == '__main__':
    mqtt_subscribe()
    # 启动PyWebIO服务器并运行绘图函数
    start_server(draw_dynamic_chart, port=23456)

    


