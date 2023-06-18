# 包含位置配置函数以及业务配置函数
# 输入输出参数采取json字符串格式
import json
import math
import numpy as np
import random
from functools import reduce

groups_num = []

# 位置配置函数
def location_config(location_par):
    global groups_num
    # 解析为python列表
    # par_list = json.loads(location_par)
    par_list = location_par
    # 分布结果
    loc_config_res = []
    groups_num = []
    # 维护id变量
    ue_id = [0]
    print('par list:', par_list)
    for par in par_list:
        print('par', par)
        # 中心点经纬度

        center_longitude = par.longitude
        center_latitude = par.latitude
        # 区域半径（单位默认为km）
        radius = par.range
        # 用户数目
        ue_num = par.totalNums
        groups_num.append(ue_num)
        # 终端类型（全区域统一）
        ue_type = par.terminalType
        # 终端运动类型
        ue_loctype = par.locationType
        # 分布模型类型
        model_type = par.modelType
        # 分布类型
        distribution_type = par.model
        # 1 确定性分布：
        # 1 使领馆分布 2 省会城市分布

        # 2 区域随机分布：
        # 1 单中心集中分布
        # 2 多中心集中分布
        # 3 多中心随机分布
        # 4 均匀分布
        # 生成用户分布
        if model_type == '2':
            if distribution_type == '1':
                distribution_result = monocentric_distribution(center_longitude, center_latitude, ue_type, radius, ue_num, ue_id, loc_config_res, ue_loctype, center_scat=0.1)
            elif distribution_type == '2':
                distribution_result = uniform_distribution(center_longitude, center_latitude, ue_type, radius, ue_num, ue_id, loc_config_res, ue_loctype)
            elif distribution_type == '3':
                distribution_result = uniform_distribution(center_longitude, center_latitude, ue_type, radius, ue_num, ue_id, loc_config_res, ue_loctype)
            elif distribution_type == '4':
                distribution_result = uniform_distribution(center_longitude, center_latitude, ue_type, radius, ue_num, ue_id, loc_config_res, ue_loctype)
    # loc_config_res = json.dumps(loc_config_res, ensure_ascii=False)
    return {"terminals": loc_config_res }

# 均匀分布函数
def uniform_distribution(lon_0, lat_0, ue_type, radius, ue_num, ue_id, loc_config_res, ue_loctype):
    disrtribution_result = []
    # 地球半径（单位km）
    ARC = 6371.393
    # 偏移角度与距离计算
    for i in range(ue_num):
        theta = 2 * np.pi * np.random.rand()
        r = radius * np.sqrt(np.random.rand())

        lat = lat_0 + 360 * r * np.cos(theta) / (2 * np.pi * ARC)
        lon = lon_0 + 360 * r * np.sin(theta) / (2 * np.pi * ARC * np.cos(lat * np.pi / 180))
        # 纬度跨半球处理
        if lat > 90:
            lat = 180 - lat
        elif lat < -90:
            lat = -180 - lat
        # 经度跨半球处理
        if lon > 180:
            lon -= 360
        elif lon < -180:
            lon += 360

        # 将结果编辑为字典添加进distribution_result
        tmp_dict = {
            'terminalId': ue_id[0],
            'terminalName': '终端_' + str(ue_id[0]),
            'terminalType': ue_type,
            'locationType': ue_loctype,
            'longitude': lon,
            'latitude': lat
        }
        ue_id[0] += 1
        loc_config_res.append(tmp_dict)

def monocentric_distribution(lon_0, lat_0, ue_type, radius, ue_num, ue_id, loc_config_res, ue_loctype, center_scat):
    earth_radius = 6371  # 地球半径，单位为公里
    # 将经度、纬度转换为弧度
    lat_rad = np.radians(lat_0)
    lon_rad = np.radians(lon_0)

    # 生成中心点的位置
    center_distance = np.random.uniform(0, (1 - center_scat)*radius, 1)
    center_angle = np.random.uniform(0, 2*np.pi, 1)
    center_delta_lat = np.arcsin(np.sin(lat_rad) * np.cos(center_distance / earth_radius) +
                                 np.cos(lat_rad) * np.sin(center_distance / earth_radius) * np.cos(center_angle))
    center_delta_lon = lon_rad + np.arctan2(np.sin(center_angle) * np.sin(center_distance / earth_radius) * np.cos(lat_rad),
                                            np.cos(center_distance / earth_radius) - np.sin(lat_rad) * np.sin(center_delta_lat))
    
    # print("分布中心点位置：", np.degrees(center_delta_lon),np.degrees(center_delta_lat))
    
    # 生成num_points个在圆形范围内均匀分布的随机角度和距离
    center_scat_distance = center_scat * radius * np.random.rand(1, ue_num)
    center_scat_angle = np.random.uniform(0, 2*np.pi, ue_num)

    # 使用Haversine公式计算坐标
    delta_lat = np.arcsin(np.sin(center_delta_lat) * np.cos(center_scat_distance / earth_radius) +
                          np.cos(center_delta_lat) * np.sin(center_scat_distance / earth_radius) * np.cos(center_scat_angle))
    delta_lon = center_delta_lon + np.arctan2(np.sin(center_scat_angle) * np.sin(center_scat_distance / earth_radius) * np.cos(center_delta_lat),
                                               np.cos(center_scat_distance / earth_radius) - np.sin(center_delta_lat) * np.sin(delta_lat))

    # 将经度、纬度转换为度数
    lat_deg = np.degrees(delta_lat)
    lon_deg = np.degrees(delta_lon)

    for i in range(ue_num):
        # 纬度跨半球处理
        if lat_deg[0,i] > 90:
            lat_deg[0,i] = 180 - lat_deg[0,i]
        elif lat_deg[0,i] < -90:
            lat_deg[0,i] = -180 - lat_deg[0,i]
        # 经度跨半球处理
        if lon_deg[0,i] > 180:
            lon_deg[0,i] -= 360
        elif lon_deg[0,i] < -180:
            lon_deg[0,i] += 360
        # 将结果编辑为字典添加进distribution_result
        tmp_dict = {
            'terminalId': ue_id[0],
            'terminalName': '终端_' + str(ue_id[0]),
            'terminalType': ue_type,
            'locationType': ue_loctype,
            'longitude': lon_deg[0,i],
            'latitude': lat_deg[0,i]
        }
        ue_id[0] += 1
        loc_config_res.append(tmp_dict)

    return lat_deg, lon_deg



def single_center_centralized_distribution(lon_0, lat_0, ue_type, radius, ue_num, ue_id, loc_config_res, ue_loctype):
    pass 

def multicenter_centralized_distribution(lon_0, lat_0, ue_type, radius, ue_num, ue_id, loc_config_res, ue_loctype):
    pass 

def multicenter_random_distribution():
    pass 

# 业务配置函数
def task_config(task_par):
    # 解析为python字典
    # par = json.loads(task_par)
    par = task_par
    # 任务起始/结束时间（单位ms换算为s）
    task_time = par.timeRange
    start_time = task_time[0] / 1000
    end_time = task_time[1] / 1000
    time_type = par.time # 任务时间分布类型 均匀分布、泊松分布
    task_num = par.totalNum # 总业务数
    task_composition = par.composition # 业务组成

    # 业务配置返回值
    biz_data = []
    # 生成视频业务配置
    for biz_comp in task_composition:
        # todo
        if time_type == '1': # 均匀分布
            multi_flow_biz_config(biz_comp, task_num, biz_data, start_time, end_time)
        if time_type == '2':
            biz_config(biz_comp, task_num, biz_data, start_time, end_time)

    # 转化为json字符串输出
    config_result = biz_data
    return config_result

# 解析发端/收端用户标识函数（返回一个tup）
def id_analysis(ue):
    # 使用 split() 方法按 "-" 分割字符串
    numbers = ue.split("-")
    # 转化为整数
    id1 = int(numbers[0])
    id2 = int(numbers[1])
    return (id1, id2)

def multi_flow_biz_config(biz_comp, task_num, biz_data, start_time, end_time):
    for i in range(0, task_num):
        # 生成一对收发端id
        source_id, dest_id = id_gen()
        tmpdict = {
            'startTime': start_time * 1000,
            'endTime': end_time * 1000,
            'source': source_id,
            'destination': dest_id,
            'bizType': biz_comp.bizType
        }
        biz_data.append(tmpdict)

# 业务泊松分布
def biz_config(biz_comp, task_num, biz_data, start_time, end_time, biz_duration=180, max_biz=1):
    # 记录业务起始时间（队列）
    biz_starttime = []
    # 过程持续时间（单位s）
    duration = end_time - start_time
    # 期望业务数及计算泊松强度
    E_task_num = task_num * biz_comp.weight
    timedispar = (E_task_num / duration) * 1.17

    sum_time = 0.0
    while sum_time < duration:
        delta_time = np.random.exponential(1.0 / timedispar)
        sum_time += delta_time
        if sum_time > duration:
            break
        elif ifcollide(start_time, max_biz, biz_starttime, sum_time, biz_duration):
            biz_starttime.append(start_time + sum_time)

    # 测试用
    # print(video_starttime)

    n = len(biz_starttime)
    # 处理返回值

    for i in range(0, n):
        # 生成一对收发端id
        source_id, dest_id = id_gen()
        tmpdict = {
            'startTime': biz_starttime[i] * 1000,
            'endTime': min(biz_starttime[i] + biz_duration, end_time) * 1000,
            'source': source_id,
            'destination': dest_id,
            'bizType': biz_comp.bizType
        }
        biz_data.append(tmpdict)

# 收发端id生成（参数为两个元组）
def id_gen():
    global groups_num
    # print(groups_num)
    if len(groups_num) == 1: # 在该群体内部随机选两个点，实际意义存疑
        return random.sample(list(range(groups_num[0])), 2)
    # 任选两个用户群 
    id_for_each_groups = reduce(lambda acc, x: acc + [acc[-1] + x], groups_num[1:], [groups_num[0]])
    # print(id_for_each_groups)
    selected_groups = random.sample(list(range(len(groups_num))), 2)
    # 
    s, d = selected_groups
    source_id = random.randint(1, id_for_each_groups[s]) if s == 0 else random.randint(id_for_each_groups[s - 1] + 1, id_for_each_groups[s])
    dest_id = random.randint(1, id_for_each_groups[d]) if d == 0 else random.randint(id_for_each_groups[d - 1] + 1, id_for_each_groups[d])
    return (source_id, dest_id)

# 泊松分布判断是否无碰撞（true为无碰撞）
def ifcollide(start_time, max_biz, video_starttime, sum_time, biz_duration):
    length = len(video_starttime)
    if max_biz > length:
        return True
    elif video_starttime[length - max_biz] - start_time + biz_duration > sum_time:
        return False
    else:
        return True

