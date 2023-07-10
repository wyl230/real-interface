import os
import time
t1 = '''curl -X POST -H "Content-Type: application/json" -d '{ "param": [ { "paramType": "baseTime", "paramName": "realTime", "paramValue": "''' + str(round(time.time() * 1000)) + '''"}, { "paramType": "baseTime", "paramName": "simulationTime", "paramValue": "0" } ] }' http://127.0.0.1:5002/xw/param/config'''

t2 = '''curl -X POST -H "Content-Type: application/json" -d '{ "param": [{ "insId": 234, "startTime": 12000, "endTime": 20000, "source": 153, "destination": 283, "bizType": "1" }, { "insId": 2, "startTime": 14000, "endTime": 16000, "source": 154, "destination": 284, "bizType": "1" } ] }' http://127.0.0.1:5002/simulation/loadStream'''

os.system(t1)
os.system(t2)
