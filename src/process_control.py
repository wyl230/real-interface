import time
import src.timer as timer
import change_json
import src.cpp_process
import logging, sys
import threading

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s',stream=sys.stdout)

forbidden_ids_lock = threading.Lock()
forbidden_ids = set()

class ProcessControl:
    def __init__(self, time_points, real_time, simulation_time, mmap):
        self.time_points = time_points
        self.real_time = real_time
        self.simulation_time = simulation_time
        self.mmap = mmap 
        self.running_sender_cpps = {}
        self.running_receiver_cpps = {}

    def start(self):
        global forbidden_ids, forbidden_ids_lock
        forbid = {}
        with forbidden_ids_lock:
            forbid = forbidden_ids
        cnt = 0
        for time_point in self.time_points:
            while timer.ms() < time_point + self.real_time - self.simulation_time:
                if (cnt:=cnt+1) % 1000 == 0:
                    print('system time: ', timer.ms(), 'point: ', time_point, 'real: ', self.real_time, 'simulation:', self.simulation_time)
                time.sleep(0.001) 

            for param in self.mmap.get(time_point):
                # sender 
                if param.insId in forbid:
                    continue
                if param.startTime == time_point:
                    change_json.update_id(int(param.source), int(param.destination), int(param.insId), int(param.bizType))
                    # sender
                    self.running_sender_cpps[param.insId] = src.cpp_process.CppProcess('sender', param.insId)
                    self.running_sender_cpps[param.insId].start(['seu-ue-svc'])
                    # receiver
                    # self.running_receiver_cpps[param.insId] = src.cpp_process.CppProcess('receiver', param.insId)
                    # try:
                    #     self.running_receiver_cpps[param.insId].start(["192.168.0.181", "pku-control-svc"])
                    # except:
                    #     print('running locally!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                    #     self.running_receiver_cpps[param.insId].start(["0.0.0.0", "0.0.0.0"])
                elif param.endTime == time_point:
                    self.running_sender_cpps[param.insId].stop()
                    # self.running_receiver_cpps[param.insId].stop()
                else: 
                    print('error: neither startTime nor stop time!!')
        print('所有业务流发送完毕')