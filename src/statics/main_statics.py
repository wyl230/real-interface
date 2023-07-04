
import paho.mqtt.client as mqtt
import requests


headers = { "Content-Type": "application/json; charset=UTF-8", }

def get_route_path(source_sat, destination_sat):
    data = {
        "data": [
            {"from_id": 1, "to_id": 2}
        ]
    }
    data = [ {"from": source_sat, "to": destination_sat} , {...}]
    requests.post("http://127.0.0.1:5001/xw/param/routiong_config", headers=headers, verify=False, data=data) # todo 地址修改

def get_sat_status():
    # todo post?
    requests.post("http://127.0.0.1:5001/sat_status", headers=headers, verify=False, data=data)
    pass 

def get_ue_status():
    requests.post("http://127.0.0.1:5001/ue_status", headers=headers, verify=False, data=data)
    pass


#  162.105.85.167 -t /ue_status
#  162.105.85.167 -t /sat_status