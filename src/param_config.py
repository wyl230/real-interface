# send_address = '162.105.85.120'
# client_port = 3003
ip_70 = '162.105.85.70'
ip_120 = '162.105.85.120'

send_address = ip_70
client_port = 3003

sat_routing_address = ip_70
# send_address = 'seu-ue-svc-pku'
# client_port = 9000


import json
file_name = 'init.json'
with open(file_name, 'r') as f:
    data = json.load(f)

    data['client_port'] = client_port

    with open(file_name, 'w') as f: 
        json.dump(data, f)