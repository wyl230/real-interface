import time
import src.timer as timer
import change_json
import src.cpp_process
import logging, sys
import threading
import heapq


logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s',stream=sys.stdout)

forbidden_ids_lock = threading.Lock()
forbidden_ids = set()
send_address = '162.105.85.70'
# send_address = 'seu-ue-svc'

packet_start_id = {}

class ProcessControl:
    def __init__(self, time_points, real_time, simulation_time, 
    mmap, cv, mmap_mutex):
        heapq.heapify(time_points)
        self.time_points = time_points
        self.real_time = real_time
        self.simulation_time = simulation_time
        self.mmap = mmap 
        self.running_sender_cpps = {}
        self.running_receiver_cpps = {}
        self.cv = cv
        self.mmap_mutex = mmap_mutex
        self.cnt = 0
        self.duplex_client_port = [23100, 23200]
        self.duplex_server_port = [23300, 23400]
        self.short_message_id = 0

    def print_debug(self):
        print('mmap start ------------------')
        for param in self.mmap.get_dict():
            print(param)
        print('mmap end ------------------')
        print('time_points start ------------------')
        print(self.time_points)
        print('time_points end ------------------')
    
    def get_cnt(self):
        self.cnt += 1
        return self.cnt

    def wait_until_next_time_point(self, time_point):
        sooner_time_come = False
        while timer.ms() < time_point + self.real_time - self.simulation_time:
            if self.get_cnt() % 1000 == 0:
                logging.debug('system time: ', timer.ms(), 'point: ', time_point, 'real: ', self.real_time, 'simulation:', self.simulation_time)
            time.sleep(0.001) 
            with self.cv:
                # 此时有新的时间加入，并且早于当前的time_point, 此时应该：将当前的time_point塞回优先队列中，continue
                if self.time_points and self.time_points[0] < time_point:
                        heapq.heappush(self.time_points, time_point)
                        sooner_time_come = True
                        break
        return sooner_time_come

    def change_json_by_param(self, param):
        change_json.update_source_module_id(0)
        cur_duplex_client_port = 0
        cur_duplex_server_port = 0
        duplex_address = 'real-data-back-chat'
        if int(param.bizType) == 3: # 短消息
            cur_duplex_client_port = self.duplex_client_port[self.short_message_id]
            cur_duplex_server_port = self.duplex_server_port[self.short_message_id]
            # self.short_message_id ^= 1
            duplex_address = 'real-data-back-chat'
        elif int(param.bizType) == 6: # 网页
            cur_duplex_client_port = 23101
            cur_duplex_server_port = 23201
            duplex_address = 'real-data-back'
        elif 11 <= int(param.bizType) <= 13: # 腾讯会议
            cur_duplex_client_port = 22000 + (int(param.bizType) % 10) * 10
            cur_duplex_server_port = cur_duplex_client_port + 1
            duplex_address = 'real-data-back-video'


        change_json.update_id(int(param.source), int(param.destination), int(param.insId), int(param.bizType), tunnel_id=int(param.bizType), duplex_client_port=cur_duplex_client_port, duplex_server_port=cur_duplex_server_port, duplex_address=duplex_address)

    def start_single_process(self, param, time_point):
        self.change_json_by_param(param)
        # sender
        if param.insId in self.running_sender_cpps: # 如果当前业务流正在进行，先停止该业务流 && 去掉该业务流对应的endtime
            print(f'time points before stop: {self.time_points}')
            print(f'end_time: {param.endTime}')
            self.running_sender_cpps[param.insId].stop()
            if timer.ms() < param.endTime + self.real_time - self.simulation_time:
                self.time_points.remove(param.endTime)
                heapq.heapify(self.time_points)
            if time_point == 0: # 停止业务流的特定时间点
                logging.info(f'业务流 {param.insId} 停止')

        self.running_sender_cpps[param.insId] = src.cpp_process.CppProcess('sender', param.insId, ins_type = int(param.bizType))
        if param.insId in packet_start_id:
            self.running_sender_cpps[param.insId].start([send_address, str(packet_start_id[param.insId])])
        else: 
            self.running_sender_cpps[param.insId].start([send_address, '0'])
            packet_start_id[param.insId] = 1

    def start(self):
        global forbidden_ids, forbidden_ids_lock
        global packet_start_id
        forbid = {}
        with forbidden_ids_lock:
            forbid = forbidden_ids

        while True:
            # 申请锁
            with self.cv:
                while not self.time_points: # 都遍历完之后等待添加
                    print('所有业务流发送完毕')
                    self.cv.wait()
                time_point = heapq.heappop(self.time_points)
                logging.info(f'pop time_point {time_point}')
            # 执行操作
            sooner_time_come = self.wait_until_next_time_point(time_point)
            if sooner_time_come:
                continue

            with self.mmap_mutex:
                self.print_debug()
                for param in self.mmap.get(time_point):
                    # sender 
                    if param.insId in forbid:
                        logging.debug(f'forbidden id: {param.insId}')
                        continue
                    
                    logging.debug(f'start time: {param.startTime}, time point: {time_point}')
                    logging.debug(f'end time: {param.endTime}, time point: {time_point}')
                    if param.startTime == time_point:
                        self.start_single_process(param, time_point)
                    elif param.endTime == time_point:
                        self.running_sender_cpps[param.insId].stop()
                        # self.running_receiver_cpps[param.insId].stop()
                    else: 
                        print('error: neither startTime nor stop time!!')
                    self.mmap.remove(time_point, param)
