import os
import time
t1 = '''curl -X POST -H "Content-Type: application/json" -d '{ "param": [ { "paramType": "baseTime", "paramName": "realTime", "paramValue": "''' + str(round(time.time() * 1000)) + '''"}, { "paramType": "baseTime", "paramName": "simulationTime", "paramValue": "0" } ] }' http://162.105.85.70:32549/xw/param/config'''

print('tencent video')

req = '{ "param": [{ "insId": 1003, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 1, "bizType": "11}, { "insId": 1004, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 1, "bizType": "12" }, { "insId": 1005, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 1, "bizType": "13" } ] }'
t2 = '''curl -X POST -H "Content-Type: application/json" -d '{ "param": [{ "insId": 1003, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 1, "bizType": "11"}, { "insId": 1004, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 1, "bizType": "12" }, { "insId": 1005, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 1, "bizType": "13" } ] }' http://162.105.85.70:32549/simulation/loadStream''' 


                                                                         # , { "insId": 1004, "startTime": 4000, "endTime": 600000000000, "source": 0, "destination": 1, "bizType": "3" } ] }' http://162.105.85.70:32549/simulation/loadStream'''


print(t1)
print(t2)
os.system(t1)
os.system(t2)
