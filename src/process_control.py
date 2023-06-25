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

    def start(self):
        global forbidden_ids, forbidden_ids_lock
        global packet_start_id
        forbid = {}
        with forbidden_ids_lock:
            forbid = forbidden_ids
        cnt = 0
        while True:
            # 申请锁
            with self.cv:
                while not self.time_points: # 都遍历完之后等待添加
                    print('所有业务流发送完毕')
                    self.cv.wait()
                time_point = heapq.heappop(self.time_points)
                logging.info(f'pop time_point {time_point}')
            # 执行操作
            sooner_time_come = False
            while timer.ms() < time_point + self.real_time - self.simulation_time:
                if (cnt:=cnt+1) % 1000 == 0:
                    print('system time: ', timer.ms(), 'point: ', time_point, 'real: ', self.real_time, 'simulation:', self.simulation_time)
                time.sleep(0.001) 
                with self.cv:
                    # 此时有新的时间加入，并且早于当前的time_point, 此时应该：将当前的time_point塞回优先队列中，continue
                    if self.time_points and self.time_points[0] < time_point:
                            heapq.heappush(self.time_points, time_point)
                            sooner_time_come = True
                            break
            if sooner_time_come:
                continue

            with self.mmap_mutex:
                for param in self.mmap.get(time_point):
                    # sender 
                    if param.insId in forbid:
                        logging.debug(f'forbidden id: {param.insId}')
                        continue
                    
                    logging.debug(f'start time: {param.startTime}, time point: {time_point}')
                    logging.debug(f'end time: {param.endTime}, time point: {time_point}')
                    if param.startTime == time_point:
                        change_json.update_id(int(param.source), int(param.destination), int(param.insId), int(param.bizType))
                        # sender
                        if param.insId in self.running_sender_cpps: # 如果当前业务流正在进行，先停止该业务流
                            self.running_sender_cpps[param.insId].stop(ins_type = int(param.bizType))
                            if time_point == 0: # 停止业务流的特定时间点
                                logging.info(f'业务流 {param.insId} 停止')
                                continue

                        self.running_sender_cpps[param.insId] = src.cpp_process.CppProcess('sender', param.insId, ins_type = int(param.bizType))
                        if param.insId in packet_start_id:
                            self.running_sender_cpps[param.insId].start(['seu-ue-svc', str(packet_start_id[param.insId])], ins_type = int(param.bizType))
                        else: 
                            self.running_sender_cpps[param.insId].start(['seu-ue-svc', '0'], ins_type = int(param.bizType))
                            packet_start_id[param.insId] = 1
                        logging.debug('6')
                    elif param.endTime == time_point:
                        self.running_sender_cpps[param.insId].stop(ins_type = int(param.bizType))
                        # self.running_receiver_cpps[param.insId].stop()
                    else: 
                        print('error: neither startTime nor stop time!!')