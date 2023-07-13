import os
import time
import sys
from pywebio.input import *
from pywebio.output import *
from pywebio import *

def main():
    # put_table(['234','123'])
    put_text('说明：网页短消息，两个用户分别对应在162.105.85.70:8082 和 162.105.85.70:8081， ')
    put_text()

    put_text('说明：直接在dashboard修改收端(pku-server)的配置')
    put_text()

    curl_head = 'curl -X POST -H "Content-Type: application/json" -d '
    load_stream_address = ' http://162.105.85.70:32549/simulation/loadStream'

    t1 = '''curl -X POST -H "Content-Type: application/json" -d '{ "param": [ { "paramType": "baseTime", "paramName": "realTime", "paramValue": "''' + str(round(time.time() * 1000)) + '''"}, { "paramType": "baseTime", "paramName": "simulationTime", "paramValue": "0" } ] }' http://162.105.85.70:32549/xw/param/config'''
    put_text('开始时间: ', time.time() // 1, time.asctime())

    ins_id_cnt = int(input.input('输入起始的业务流id: '))
    put_text(f'业务流id开始于{ins_id_cnt}')

    put_text(f'业务流配置：cbr(80kpbs), vbr(2Mbps)')

    types = ['(1) cbr', '(2) vbr', '(3) 纯转发(video(vlc) | 调速率和包长 | 非网页短消息)', '(4) 网页消息 | iperf3', '(5) 外部网络 (腾讯会议 | 外部网页浏览) ', '(6) 短消息', '(7) ip电话', '(8) 双人腾讯会议']

    set = input.input('\n'.join(types) + '\n')
    set = int(set) 

    put_text(f'选择了 {types[set - 1]}.')

    put_text(types[set - 1])
    if set == 1 or set == 2:
        flow_num = int(input.input(f"输入{'cbr' if set == 1 else 'vbr'}条数: "))
        s = [f""" {{ "insId" :{ins_id}, "startTime": 2000, "endTime": 100000000000, "source": 0, "destination": 1, "bizType": "{set}"  }} """ for ins_id in range(1 + ins_id_cnt, flow_num + 1 + ins_id_cnt) ]
        s = ",".join(s)
        t2 = f''' '{{ "param": [{s}] }}' '''
    elif set == 3: # 纯转发
        insId = 23023
        s = [f""" {{ "insId" :{insId}, "startTime": 2000, "endTime": 1000000000000, "source": 9, "destination": 17, "bizType": "4"  }} """]
        s = ",".join(s)
        put_text(s)
        t2 = f'''curl -X POST -H "Content-Type: application/json" -d '{{ "param": [{s}] }}' '''
    elif set == 4: # 网页 | ip电话 | iperf3
        t2 = ''' '{ "param": [{ "insId": 23001, "startTime": 2000, "endTime": 100000000, "source": 9, "destination": 17, "bizType": "6"  } ] }'  '''

    elif set == 5: # 外部网络
        # req = '{ "param": [{ "insId": 1003, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 1, "bizType": "11"}, { "insId": 1004, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 1, "bizType": "12" }, { "insId": 1005, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 1, "bizType": "13" } ] }'
        t2 = ''' '{ "param": [{ "insId": 1003, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 1, "bizType": "11"} ] }' '''

    elif set == 6: # 短消息
        t2 = ''' '{ "param": [{ "insId": 23001, "startTime": 2000, "endTime": 100000000, "source": 5, "destination": 7, "bizType": "3"  } ] }'  '''

    elif set == 7: # ip
        t2 = ''' '{ "param": [{ "insId": 23001, "startTime": 2000, "endTime": 100000000, "source": 0, "destination": 1, "bizType": "5"  } ] }'  '''

    elif set == 8: # 两人腾讯会议
        # req = '{ "param": [{ "insId": 1003, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 1, "bizType": "11"}, { "insId": 1004, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 1, "bizType": "12" }, { "insId": 1005, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 1, "bizType": "13" } ] }'
        t2 = ''' '{ "param": [{ "insId": 1003, "startTime": 2000, "endTime": 10000000, "source": 0, "destination": 2, "bizType": "11"} , { "insId": 1004, "startTime": 2000, "endTime": 10000000, "source": 8, "destination": 0, "bizType": "12" }] }' '''

    put_text(t1)
    put_text(curl_head + t2 + load_stream_address)
    os.system(t1)
    os.system(t2)


WEB_PORT = 28188
start_server(main, port=WEB_PORT, debug=True)