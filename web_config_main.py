import os
import time
import sys
# import pywebio
from pywebio.input import input
from pywebio import *

print('说明：网页短消息，两个用户分别对应在162.105.85.70:8080 和 162.105.85.70:8081， ')
print()

print('说明：直接在dashboard修改收端(pku-server)的配置')
print()



def main():
    t1 = '''curl -X POST -H "Content-Type: application/json" -d '{ "param": [ { "paramType": "baseTime", "paramName": "realTime", "paramValue": "''' + str(round(time.time() * 1000)) + '''"}, { "paramType": "baseTime", "paramName": "simulationTime", "paramValue": "0" } ] }' http://162.105.85.70:32549/xw/param/config'''
    print('开始时间: ', time.time() // 1, time.asctime())

    ins_id_cnt = int(input('输入起始的业务流id: '))

    print(f'业务流配置：cbr(80kpbs), vbr(2Mbps)')

    types = ['(1) cbr', '(2) vbr', '(3) 纯转发(video(vlc) | 调速率和包长 | 非网页短消息)', '(4) 网页消息 | iperf3', '(5) 外部网络 (腾讯会议 | 外部网页浏览) ', '(6) 短消息', '(7) ip电话']

    set = input('\n'.join(types) + '\n')

    set = int(set) 
    print(types[set - 1])
    if set == 1 or set == 2:
        flow_num = int(input(f"输入{'cbr' if set == 1 else 'vbr'}条数: "))
        s = [f""" {{ "insId" :{ins_id}, "startTime": 2000, "endTime": 100000000000, "source": 0, "destination": 1, "bizType": "{set}"  }} """ for ins_id in range(1 + ins_id_cnt, flow_num + 1 + ins_id_cnt) ]
        s = ",".join(s)
        t2 = f'''curl -X POST -H "Content-Type: application/json" -d '{{ "param": [{s}] }}' http://162.105.85.70:32549/simulation/loadStream'''
    elif set == 3: # 纯转发
        insId = 23023
        s = [f""" {{ "insId" :{insId}, "startTime": 2000, "endTime": 1000000000000, "source": 6, "destination": 7, "bizType": "4"  }} """]
        s = ",".join(s)
        print(s)
        t2 = f'''curl -X POST -H "Content-Type: application/json" -d '{{ "param": [{s}] }}' http://162.105.85.70:32549/simulation/loadStream'''
    elif set == 4: # 网页 | ip电话 | iperf3
        t2 = '''curl -X POST -H "Content-Type: application/json" -d '{ "param": [{ "insId": 23001, "startTime": 2000, "endTime": 100000000, "source": 0, "destination": 1, "bizType": "6"  } ] }'  http://162.105.85.70:32549/simulation/loadStream'''

    elif set == 5: # 外部网络
        req = '{ "param": [{ "insId": 1003, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 1, "bizType": "11"}, { "insId": 1004, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 1, "bizType": "12" }, { "insId": 1005, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 1, "bizType": "13" } ] }'
        t2 = '''curl -X POST -H "Content-Type: application/json" -d '{ "param": [{ "insId": 1003, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 1, "bizType": "11"} ] }' http://162.105.85.70:32549/simulation/loadStream'''

    elif set == 6: # 短消息
        t2 = '''curl -X POST -H "Content-Type: application/json" -d '{ "param": [{ "insId": 23001, "startTime": 2000, "endTime": 100000000, "source": 5, "destination": 7, "bizType": "3"  } ] }'  http://162.105.85.70:32549/simulation/loadStream'''

    elif set == 7: # ip
        t2 = '''curl -X POST -H "Content-Type: application/json" -d '{ "param": [{ "insId": 23001, "startTime": 2000, "endTime": 100000000, "source": 0, "destination": 1, "bizType": "5"  } ] }'  http://162.105.85.70:32549/simulation/loadStream'''

    print(t1)
    print(t2)
    os.system(t1)
    os.system(t2)


WEB_PORT = 23111
start_server(main, port=WEB_PORT, debug=True)