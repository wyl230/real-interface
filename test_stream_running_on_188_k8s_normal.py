import os
import time
t1 = '''curl -X POST -H "Content-Type: application/json" -d '{ "param": [ { "paramType": "baseTime", "paramName": "realTime", "paramValue": "''' + str(round(time.time() * 1000)) + '''"}, { "paramType": "baseTime", "paramName": "simulationTime", "paramValue": "0" } ] }' http://162.105.85.188:32415/xw/param/config'''


flow_num = 5
s = [f""" {{ "insId" :{cnt}, "startTime": 2000, "endTime": 100000000, "source": 153, "destination": 283, "bizType": "2"  }} """ for cnt in range(1, flow_num)]
s = ",".join(s)

t2 = f'''curl -X POST -H "Content-Type: application/json" -d '{{ "param": [{s}] }}' http://162.105.85.188:32415/simulation/loadStream'''

print(t1)
print(t2)
os.system(t1)
os.system(t2)
