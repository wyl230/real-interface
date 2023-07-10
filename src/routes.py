# http接口定义

import heapq
import time
import src.timer as timer
import json
import change_json
import paho.mqtt.client as mqtt
import requests
from fastapi import APIRouter, BackgroundTasks
from pydantic.main import BaseModel
from typing import List
import asyncio
from src.EfficiencyEvaluator import udp_listener
from src.EfficiencyEvaluator import ok
import src.cpp_process
import logging, sys
import src.distribution.distribution_task_functions as func
import threading
import config
from src.statics.request_format import *

from src.process_control import ProcessControl 
from src.process_control import forbidden_ids_lock, forbidden_ids
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s',stream=sys.stdout)

start_send_delay_ok = False

def start_send_delay():
    global start_send_delay_ok
    return start_send_delay_ok

router = APIRouter()

# cpp
# 接口1，参数配置
# 东北调此系统
# 本地测试: ok
# curl -X POST -H "Content-Type: application/json" -d '{ "param": [ { "paramType": "baseTime", "paramName": "realTime", "paramValue": "1680055825000" }, { "paramType": "baseTime", "paramName": "simulationTime", "paramValue": "1640970000000" } ] }' http://127.0.0.1:5002/param/config

# round(time.time() * 1000)

process_control_init = False
real_time = 0
simulation_time = 0
class Param(BaseModel):
    paramType: str
    paramName: str
    paramValue: int

class Configuration(BaseModel):
    param: List[Param]

@router.post("/xw/param/config")
def param_config(request_body: Configuration):
    global process_control_init
    global real_time, simulation_time
    # return "param is " + str(request_body.param) # 测试是否收到并解析request
    success = True
    code = 1 if success else 0
    message = 'SUCCESS' if success else '失败原因'

    for param in request_body.param:
        if param.paramName.find('real') != -1:
            real_time = param.paramValue
        elif param.paramName.find('simulationTime') != -1:
            simulation_time = param.paramValue

    # 启动任务管理
    if not process_control_init:
        process_control_init = True
        headers = { "Content-Type": "application/json; charset=UTF-8", }
        requests.post("http://127.0.0.1:5002/process_control", headers=headers, verify=False, data={})

    return {
        "code": code,
        "message": f"{message}",
        "data": 'null' # 暂时为空
    }

class Dongbei(BaseModel):
    moduleCode: str
    paramType: List[str]

@router.post("/xw/param/query")
def param_query(request_body: Dongbei):
    # return str(request_body) # 测试是否收到并解析request
    return { "code": 1, "message": "SUCCESS", "data": { "param": [ { "paramType": "baseTime", "paramName": "realTime", "paramValue": "1680055825000" }, { "paramType": "baseTime", "paramName": "simulationTime", "paramValue": "1640970000000" } ] } }

class Empty(BaseModel):
    pass

# 接口4，初始化时发送mqtt消息
def on_init_use_mqtt():
    client = mqtt.Client()

    if config.get_local_mqtt():
        client.connect('162.105.85.167', 1883, 600)
    else:
        client.connect('192.168.0.100', 30004, 600)

    init_message = {
        "moduleCode": "pku",
        "initStatus": "1"
    }
    init_message_json = json.dumps(init_message)

    topic = "/simulation/init"
    client.publish(topic, init_message_json)

@router.post("/simulation/init")
def simulation_init(request_body: Empty):
    # return "param is " + str(request_body.param) # 测试是否收到并解析request
    success = True
    code = 1 if success else 0
    message = 'SUCCESS' if success else '失败原因'
    # 发布mqtt消息
    
    on_init_use_mqtt()

    return {
        "code": code,
        "message": f"{message}",
        "data": 'null' # 暂时为空
    }

current_cpp_id = 0
running_sender_cpps = {}
running_receiver_cpps = {}

class single_id(BaseModel):
    insId: int

@router.post('/simulation/stopStream')
def stopStream(body: single_id):
    global forbidden_ids, forbidden_ids_lock
    # with open('status', 'w') as f:
    #     f.write('0')
    with forbidden_ids_lock:
        forbidden_ids.add(body.insId)

    # todo 删除对应的time_point中的mmap映射的param，同时停止进程
    # todo 访问loadstream，及时停止 
    headers = { "Content-Type": "application/json; charset=UTF-8", }
    requests.post("http://127.0.0.1:5002/simulation/loadStream", headers=headers, verify=False, data={"param": [ { "insId" : body.insId , "startTime": 0, "endTime": 0, "source": 153, "destination": 283, "bizType": "1"  } ]})

    return {
        "code": 1,
        "message": "SUCCESS",
        "data": None
    }

class ParamStream(BaseModel):
    insId: int
    startTime: int
    endTime: int
    source: int
    destination: int
    bizType: str

class LoadStream(BaseModel):
    param: List[ParamStream]

from src.multimap import Multimap
time_points = []
mmap = Multimap()

mutex = threading.Lock() 
cv = threading.Condition(mutex) 

mmap_mutex = threading.Lock() 
mmap_cv = threading.Condition(mmap_mutex) 

@router.post("/simulation/loadStream")
def load_stream(request_body: LoadStream):
    global start_send_delay_ok
    global ok
    global mmap, time_points
    global forbidden_ids, forbidden_ids_lock
    success = True
    code = 1 if success else 0
    message = 'SUCCESS' if success else '失败原因'

    for param in request_body.param:
        mmap.add(param.startTime, param)
        mmap.add(param.endTime, param)
        with cv:
            print('time_points before: ', time_points)
            heapq.heappush(time_points, param.endTime)
            print('time_points add end: ', time_points)
            heapq.heappush(time_points, param.startTime)
            print('time_points add start: ', time_points)
            logging.info(f'添加了时间 s: {param.startTime}, e: {param.endTime}')
            cv.notify_all()
        with forbidden_ids_lock:
            if int(param.insId) in forbidden_ids:
                forbidden_ids.remove(param.insId)

    start_send_delay_ok = True
    ok = True
    with open('status', 'w') as f:
        f.write('1')

    return {
        "code": code,
        "message": f"{message}",
        "data": 'null' # 暂时为空
    }

class HttpServiceModel(BaseModel):
    api_path: str
    data: object

# 发起http请求示例
# 参数示例：
# {
#     "api_path": "http://ip:8081/cz/configParam",
#     "data": {
#         "key1": "value1"
#     }
# }

@router.post("/call_request")
def call_request(body: HttpServiceModel):
    url = body.api_path
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
    }

    response = requests.post(url, headers=headers, verify=False, data=json.dumps(body.data))
    resp = json.loads(response.text)
    return resp

def start_asyncio():
    print('start asyncio')
    asyncio.run(udp_listener())


# *生成用户分布接口
# test: 
# curl -X POST -H "Content-Type: application/json" -d '{ "config": [ { "totalNums": 300, "terminalType":"1", "locationType": "1", "modelType": "1", "model": "1", "longitude": 123.32, "latitude": 43.34, "range": 200 }, { "totalNums": 300, "terminalType":"1", "locationType": "1", "modelType": "1", "model": "1", "longitude": 123.32, "latitude": 43.34, "range": 200 } ] }' http://127.0.0.1:5002/terminal/generate

class TerminalConfig(BaseModel):
    totalNums: int
    terminalType: str
    locationType: str
    modelType: str
    model: str
    longitude: float
    latitude: float
    range: int

class TerminalsConfig(BaseModel):
    config: List[TerminalConfig]

@router.post("/terminal/generate")
def terminal_config(body: TerminalsConfig):
    terminals = []
    get_terminal = lambda id, name, type, location_type, longitude, latitude, positions: { "terminalId": id, "terminalName": name, "terminalType": type, "locationType": location_type, "longitude": longitude, "latitude": latitude, "positions": positions }

    def get_positions():
        return {
            "positions": [
                {
                    "timestamp": 957110400000,
                    "longitude": 123.23,
                    "latitude": 43.34
                }
            ] * 3
        }

    terminal = get_terminal(1, 'terminal_1', '1', '1', 123.32, 43.34, get_positions())

    terminals = [terminal] * 2

    # if body.config.locationType == '1':
    print('body config', body.config)
    return func.location_config(body.config)
    # else:
        # return { "terminals": terminals }

# *生成业务流分布

# { "composition": [ { "bizType": "1", "weight": 0.3 }, { "bizType": "2", "weight": 0.7 } ], "time": "1", "totalNum": 100, "timeRange": [1679796935000, 1682475335693] }

class single_composition(BaseModel):
    bizType: str
    weight: float

class biz_request(BaseModel):
    composition: List[single_composition]
    time: str 
    totalNum: int 
    timeRange: List[int]

@router.post("/bizStream/streamModel")
def terminal_config(body: biz_request):
    def get_data():
        return {
            "startTime": 1680055825000,
            "endTime": 1680055835000,
            "source": "1",
            "destination": "2",
            "bizType": "1"
        }

    data = [get_data()] * 2
    data = func.task_config(body)
    return {
        "code": 1,
        "message": "SUCCESS",
        "data": data

    }

import threading


@router.post('/submit-task/')
async def submit_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(long_running_task)
    return {"message": "Task submitted to run in the background."}


def long_running_task():
    global real_time, simulation_time
    global mmap, time_points
    if real_time == 0:
        logging.error('param config first!!!')
        return {'process control': 'error: not param configured'}

    time_points.sort()
    logging.info('time_points: ' + str(time_points))

    process_control_a = ProcessControl(time_points, real_time, simulation_time, mmap, cv, mmap_mutex)
    process_control_a.start()
    time_points = []
    mmap = Multimap()

@router.post("/process_control")
async def process_control(background_tasks: BackgroundTasks):
    background_tasks.add_task(long_running_task)
    return {'process control': 'running'}

@router.post("/other_config")
async def b():
    # @router.get("/b")
    # loop = asyncio.get_event_loop()
    # result = await loop.run_in_executor(None, sleep_print, 2)
    return {"message": "线程池中运行sleep函数"}


## pku数据统计部分
# chz
import random
@router.post("/test_data")
def test_data(request_body: Empty):
    return [random.randint(100,1000) for i in range(7)]

@router.post("/throughput_all")
def throughput_all(request_body: Empty):
    return config.get_throughput_all()

@router.post("/delay_single")
def throughput_all(request_body: single_id):
    return {
        "avg": config.get_avg_delay(single_id.ins_id),
        "min": config.get_min_delay(single_id.ins_id),
        "max": config.get_max_delay(single_id.ins_id),
    }

@router.post("/loss_rate")
def get_loss_rate(request_body: single_id):
    return get_loss_rate(single_id.ins_id)

@router.post("/throughput")
def get_throughput(request_body: single_id):
    return get_throughput(single_id.ins_id)

@router.post("/service_table")
def get_service_table(request_body: Empty):
    return config.get_service_table()

@router.post("/ue_table") # done
def get_ue_table(request_body: Empty):
    return config.get_ue_status()

# ue link band
@router.post("/ue_uplink_band") # 实时的
def get_ue_uplink_band(request_body: single_ue_id):
    return config.get_ue_uplink(request_body.ue_id)

@router.post("/ue_downlink_band")
def get_ue_downlink_band(request_body: single_ue_id):
    return config.get_ue_downlink(request_body.ue_id)

# sat link band
@router.post("/sat_uplink")
def get_sat_uplink(body: single_sat_id):
    return config.get_sat_uplink(body.sat_id)

@router.post("/sat_downlink")
def get_ue_downlink_band(body: single_sat_id):
    return config.get_sat_downlink(body.sat_id)

@router.post("/sat_link_forward")
def get_sat_link_forward(body: double_sat_id):
    try:
        return config.get_sat_link_forward(body.sat_id1, body.sat_id2)
    except:
        return []

@router.post("/sat_link_recv")
def get_sat_link_recv(body: double_sat_id):
    try:
        return config.get_sat_link_recv(body.sat_id1, body.sat_id2)
    except:
        return []

@router.post("/sat_link")
def get_ue_downlink_band(body: single_sat_id):
    return config.get_sat_link(body.sat_id)

# wj
@router.post("/ue_status")
def get_ue_status(ue_status: UeStatus):
    # print('from wj', ue_status)
    config.set_ue_status(ue_status)
    config.set_ue_related_list(ue_status)
    config.set_current_ue_to_sat(ue_status)
    return {"status": 1}

@router.post("/sat_status")
def get_sat_status(sat_status: SatStatus):
    # print('from wj', sat_status)
    config.set_sat_status(sat_status)
    config.set_sat_related_list(sat_status)
    config.set_sat_link(sat_status)
    return {"status": 1}

# gf
@router.post("/routing")
def get_routing(routing: Empty):
    print(config.get_current_ue)
    headers = { "Content-Type": "application/json; charset=UTF-8", }
    data = [ {"from": config.get_current_ue_to_sat(source_ue), "to": config.get_current_ue_to_sat(destination_ue)} for (source_ue, destination_ue) in config.get_current_ue() ]
    r = requests.post("http://162.105.85.70:5001/xw/param/routing_config", headers=headers, verify=False, data=data)

    print('from gf', r.text)

    return []

# query

# json(数组) 70:32549 

# 列表都是10个，端到端间隔 丢包 吞吐量 
# /mission_info
# 
# { "interval": [10us], "loss": [10], "throughput": [10 kbps], "avg_interval": , avg_loss: 1, avg_throughput: }
# 


@router.post('/mission_info')
def get_mission_info(mission_info: mission_type):
    print(mission_info)
    config.set_mission_info(mission_info)
    config.set_mission_related_list(mission_info)
    return {"status": 1}

    
@router.post('/mission_info_table')
def get_mission_info_table(body: Empty):
    mission_info = get_mission_info_table()
    id_to_position = ["北京-中国人民大会堂", "北京-中央电视台", "上海市人民政府", "上海证券交易所", "广州市政协", "广州市人民政府", "北京-市政府", "北京-国务院", "上海国际金融中心", "上海合作组织秘书处"]
    return [{"id": i + 1, "source": '国外', "dest": id_to_position[i], "delay": mission_info.interval[i], "throughput": mission_info.throughput[i], "loss_rate": mission_info.loss[i],} for i in range(10)]

@router.post('/mission_info_all')
def get_mission_info_table(body: Empty):
    return {"delay": [], "throughput": [], "loss_rate": []}

@router.post('/mission_info_throughput')
def get_mission_info_throughput(body: single_id):
    pass 

@router.post('/mission_info_loss_rate')
def get_mission_info_loss_rate(body: single_id):
    pass 

@router.post('/mission_info_delay')
def get_mission_info_delay(body: single_id):
    pass 

# timestamp

@router.post('/start_time')
def get_start_time(body: Empty):
    # query for start time
    return {"status": True, "start_time": int}

# 跨文件
# 1
class data_class(BaseModel):
    insId: int
    maxDelay: float
    minDelay: float
    aveDelay: float
    lossRate: float
    throughput: float
    speed: float

class data_dict_class(BaseModel):
    data: List[data_class]

@router.post('/set_service_table_and_evaluator_for_each')
def get_set_service_table(body: data_dict_class):
    print('set_service_table_and_evaluator_for_each before')
    config.set_service_table(body)
    config.set_evaluator_for_each(body)
    print('set_service_table_and_evaluator_for_each ok')
    return {"status": True}

# 2
class set_current_ue_and_id_to_source_and_dest_class(BaseModel):
    ins_id: int
    source: int
    dest: int

@router.post('/set_current_ue_and_id_to_source_and_dest')
def set_current_ue_and_id_to_source_and_dest(body: set_current_ue_and_id_to_source_and_dest_class):
    print('set_current_ue_and_id_to_source_and_dest before')
    config.set_current_ue(body.source, body.dest)
    config.set_id_to_source_and_dest(body.ins_id, body.source, body.dest)
    print('set_current_ue_and_id_to_source_and_dest ok')
    return {"status": True}