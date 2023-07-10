
import paho.mqtt.client as mqtt
import requests
import config


headers = { "Content-Type": "application/json; charset=UTF-8", }

# chz 


# todo gf 
def get_route_path(source_sat, destination_sat):
    data = {
        "data": [
            {"from_id": 1, "to_id": 2}
        ]
    }
    data = [ {"from": source_sat, "to": destination_sat} , {...}]
    requests.post("http://127.0.0.1:5001/xw/param/routing_config", headers=headers, verify=False, data=data) # todo 地址修改


#  162.105.85.167 -t /ue_status
#  162.105.85.167 -t /sat_status