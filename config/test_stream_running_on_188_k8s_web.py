import os
import time
t1 = '''curl -X POST -H "Content-Type: application/json" -d '{ "param": [ { "paramType": "baseTime", "paramName": "realTime", "paramValue": "''' + str(round(time.time() * 1000)) + '''"}, { "paramType": "baseTime", "paramName": "simulationTime", "paramValue": "0" } ] }' http://162.105.85.70:32549/xw/param/config'''

print('web')
t2 = '''curl -X POST -H "Content-Type: application/json" -d '{ "param": [{ "insId": 234, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 1, "bizType": "6" } ] }' http://162.105.85.70:32549/simulation/loadStream'''

print(t2)
os.system(t1)
os.system(t2)
