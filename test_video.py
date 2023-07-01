import os
import time
t1 = '''curl -X POST -H "Content-Type: application/json" -d '{ "param": [ { "paramType": "baseTime", "paramName": "realTime", "paramValue": "''' + str(round(time.time() * 1000)) + '''"}, { "paramType": "baseTime", "paramName": "simulationTime", "paramValue": "0" } ] }' http://162.105.85.70:32549/xw/param/config'''

# 视频流
print('video')
insId = 23023
s = [f""" {{ "insId" :{insId}, "startTime": 2000, "endTime": 100000000, "source": 0, "destination": 1, "bizType": "4"  }} """]
s = ",".join(s)
print(s)

t2 = f'''curl -X POST -H "Content-Type: application/json" -d '{{ "param": [{s}] }}' http://162.105.85.70:32549/simulation/loadStream'''

print(t1)
print(t2)
os.system(t1)
os.system(t2)
