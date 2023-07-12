import json
import os

def update_id(source_id, dest_id, flow_id, type, tunnel_id=0, duplex_client_port=0, duplex_server_port=0, source_module_id=0, video_in=30027, duplex_address='real-data-back'):
    file_name = 'init.json'
    # 读取JSON文件
    with open(file_name, 'r') as f:
        data = json.load(f)

    # 修改字段
    data['source_id'] = source_id
    data['dest_id'] = dest_id
    data['flow_id'] = flow_id
    data['send_type'] = type
    data['tunnel_id'] = tunnel_id
    data['duplex_client_port'] = duplex_client_port
    data['duplex_server_port'] = duplex_server_port
    data['duplex_client_address'] = duplex_address
    data['duplex_server_address'] = duplex_address
    print(duplex_client_port)
    print(duplex_server_port)

    # 写回JSON文件
    with open(file_name, 'w') as f: 
        json.dump(data, f)

    os.system('cat init.json >> normal.log')
    os.system('echo \n >> normal.log')


def update_source_module_id(source_module_id):
    file_name = 'init.json'
    with open(file_name, 'r') as f:
        data = json.load(f)

    data['source_module_id'] = source_module_id

    data['flow_id'] += 100000 if source_module_id == 100 else 0
    os.system(f'echo source module id {source_module_id}\n >> double.log')
    with open(file_name, 'w') as f: 
        json.dump(data, f)

    os.system('cat init.json >> double.log')
    os.system('echo \n >> double.log')
