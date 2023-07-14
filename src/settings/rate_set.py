from loguru import logger
import json

def set_cbr_rate(pps = 50, packet_size = 1024):
    file_name = 'init.json'
    with open(file_name, 'r') as f:
        data = json.load(f)

    data['pps'] = pps
    data['packet_size'] = packet_size

    with open(file_name, 'w') as f: 
        json.dump(data, f)
