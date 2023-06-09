import json

def update_id(source_id, dest_id, flow_id, type):
    file_name = 'init.json'
    # 读取JSON文件
    with open(file_name, 'r') as f:
        data = json.load(f)

    # 修改字段
    data['source_id'] = source_id
    data['dest_id'] = dest_id
    data['flow_id'] = flow_id
    data['send_type'] = type

    # 写回JSON文件
    with open(file_name, 'w') as f: 
        json.dump(data, f)
