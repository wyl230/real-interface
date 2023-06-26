import os
import time
t1 = '''curl -X POST -H "Content-Type: application/json" -d '{ "param": [ { "paramType": "baseTime", "paramName": "realTime", "paramValue": "''' + str(round(time.time() * 1000)) + '''"}, { "paramType": "baseTime", "paramName": "simulationTime", "paramValue": "0" } ] }' http://127.0.0.1:5001/xw/param/config'''

t2 = '''curl -X POST -H "Content-Type: application/json" -d '{ "param": [{ "insId": 234, "startTime": 2000, "endTime": 10000, "source": 153, "destination": 283, "bizType": "1" }, { "insId": 2, "startTime": 4000, "endTime": 600000, "source": 154, "destination": 284, "bizType": "1" } ] }' http://127.0.0.1:5001/simulation/loadStream'''

os.system(t1)
os.system(t2)
