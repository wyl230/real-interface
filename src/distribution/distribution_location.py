import numpy as np
# 单中心分布函数

def divide_number(number):
    remainder = number % 3 # 求余数
    quotient = number // 3 # 求商

    # 根据余数选择切片方式
    if remainder == 0:
        return [number // 3] * 3
    elif remainder == 1:
        return [quotient, quotient, quotient + 1]
    else:
        return [quotient, quotient + 1, quotient + 1]

def centric_distribution(lon_0, lat_0, ue_type, radius, ue_num, ue_id, loc_config_res, ue_loctype, center_scat, center_num):
    earth_radius = 6371  # 地球半径，单位为公里
    # 将经度、纬度转换为弧度
    lat_rad = np.radians(lat_0)
    lon_rad = np.radians(lon_0)

    # 生成中心点的位置
    center_distance = np.random.uniform(0, (1 - center_scat)*radius, center_num)
    center_angle = np.random.uniform(0, 2*np.pi, center_num)
    center_delta_lat = np.arcsin(np.sin(lat_rad) * np.cos(center_distance / earth_radius) +
                                 np.cos(lat_rad) * np.sin(center_distance / earth_radius) * np.cos(center_angle))
    center_delta_lon = lon_rad + np.arctan2(np.sin(center_angle) * np.sin(center_distance / earth_radius) * np.cos(lat_rad),
                                            np.cos(center_distance / earth_radius) - np.sin(lat_rad) * np.sin(center_delta_lat))
    
    print("分布中心点位置：", np.degrees(center_delta_lon),np.degrees(center_delta_lat))
    
    
    # 每个中心分别生成对应数量的用户
    if isinstance(ue_num, int):
        ue_num = divide_number(ue_num)
        ue_num.extend(ue_num * (center_num - 1))
    if isinstance(center_scat, float):
        center_scat = [center_scat]
        center_scat.extend(center_scat * (center_num - 1))
    Lat = np.empty((0,), dtype=np.ndarray)
    Lon = np.empty((0,), dtype=np.ndarray)
    sum_ue_num = 0
    for center_id in range(center_num):
        sum_ue_num = sum_ue_num + ue_num[center_id]
        # 生成ue_num个在圆形范围内均匀分布的随机角度和距离
        center_scat_distance = center_scat[center_id] * radius * np.random.rand(1, ue_num[center_id])
        center_scat_angle = np.random.uniform(0, 2*np.pi, ue_num[center_id])

        # 使用Haversine公式计算坐标
        delta_lat = np.arcsin(np.sin(center_delta_lat[center_id]) * np.cos(center_scat_distance / earth_radius) +
                            np.cos(center_delta_lat[center_id]) * np.sin(center_scat_distance / earth_radius) * np.cos(center_scat_angle))
        delta_lon = center_delta_lon[center_id] + np.arctan2(np.sin(center_scat_angle) * np.sin(center_scat_distance / earth_radius) * np.cos(center_delta_lat[center_id]),
                                                np.cos(center_scat_distance / earth_radius) - np.sin(center_delta_lat[center_id]) * np.sin(delta_lat))

        # 将经度、纬度转换为度数
        lat_deg = np.degrees(delta_lat)
        lon_deg = np.degrees(delta_lon)
        Lat = np.append(Lat, lat_deg)
        Lon = np.append(Lon, lon_deg)

    for i in range(sum_ue_num):
        # 纬度跨半球处理
        if Lat[i] > 90:
            Lat[i] = 180 - Lat[i]
        elif Lat[i] < -90:
            Lat[i] = -180 - Lat[i]
        # 经度跨半球处理
        if Lon[i] > 180:
            Lon[i] -= 360
        elif Lon[i] < -180:
            Lon[i] += 360
        # 将结果编辑为字典添加进distribution_result
        tmp_dict = {
            'terminalId': ue_id[0],
            'terminalName': '终端_' + str(ue_id[0]),
            'terminalType': ue_type,
            'locationType': ue_loctype,
            'longitude': Lon[i],
            'latitude': Lat[i]
        }
        ue_id[0] += 1
        loc_config_res.append(tmp_dict)
    print(Lon)
    print(Lat)
    return Lat, Lon



# if __name__=='__main__':
#     radius_km = 1000
#     ue = 10    # 可以设置各个中心的ue数量 [10, 20]
#     scat = 0.1  # 可以设置各个中心的分布情况[0.1，0.2]
#     lon = 0
#     lat = 0
#     centernum = 3
#     points_lat, points_lon = centric_distribution(lon,lat,0,radius_km,ue,0,0,0,scat,centernum)

#     # 绘制散点图
#     fig, ax = plt.subplots()
#     ax.scatter(points_lon, points_lat, s=10)
#     ax.set_xlabel('Longitude')
#     ax.set_ylabel('Latitude')
#     ax.set_title('Generated Points Distribution')

#     # 绘制圆

#     radius_lon = radius_km / (111.32 * np.cos(np.radians(50)))
#     circle = plt.Circle((0, lat), radius_lon, edgecolor='r', facecolor='none')
#     ax.add_patch(circle)

#     ax.grid(True)
#     plt.savefig("111")
