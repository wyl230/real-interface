import os
import select
import subprocess
import fcntl
import threading
import random
from time import sleep
import logging
import sys
import src.timer as timer



logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s',stream=sys.stdout)

# logging.debug('debug message')
# logging.info('info message')
# logging.warning('warning message')
# logging.error('error message')
# logging.critical('critical message')

class CppProcess:
    def __init__(self, file_name, id):
        self.id = id
        self.file_name = file_name
        self.process = None
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.read_output)
        self.running = False
        # logging.info('CppProcess __init__')
        self.init = False

    def start_thread(self):
        self.running = True
        self.thread.start()

    def stop_thread(self):
        self.running = False
        self.thread.join()

    # def start(self, address='0.0.0.0'):
    def start(self, address=['seu-ue-svc'], ins_type = 1):
        # "-c", "(./sender seu-ue-svc client.json &);(./sender seu-ue-svc server.json)"]
        logging.info(f'start: {self.file_name}[{self.id}]') 
        with self.lock:
            if ins_type == 6:
                self.process = subprocess.Popen([f"./sender_duplex", 'seu-ue-svc', 'client.json'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.process = subprocess.Popen([f"./sender_duplex", 'seu-ue-svc', 'server.json'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                flags_stdout = fcntl.fcntl(self.process.stdout.fileno(), fcntl.F_GETFL)
                fcntl.fcntl(self.process.stdout.fileno(), fcntl.F_SETFL, flags_stdout | os.O_NONBLOCK)
                flags_stderr = fcntl.fcntl(self.process.stderr.fileno(), fcntl.F_GETFL)
                fcntl.fcntl(self.process.stderr.fileno(), fcntl.F_SETFL, flags_stderr | os.O_NONBLOCK)
            else:
                self.process = subprocess.Popen([f"./{self.file_name}", *address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # set the stdout and stderr pipes as non-blocking
                flags_stdout = fcntl.fcntl(self.process.stdout.fileno(), fcntl.F_GETFL)
                fcntl.fcntl(self.process.stdout.fileno(), fcntl.F_SETFL, flags_stdout | os.O_NONBLOCK)
                flags_stderr = fcntl.fcntl(self.process.stderr.fileno(), fcntl.F_GETFL)
                fcntl.fcntl(self.process.stderr.fileno(), fcntl.F_SETFL, flags_stderr | os.O_NONBLOCK)

            if not self.init:
                self.init = True
                self.start_thread()

    def stop(self, ins_type = 1):
        logging.info(f'trying to stop: {self.file_name}[{self.id}]') 
        with self.lock:
            if self.process:
                self.process.kill()
                logging.info(f'stop: {self.file_name}[{self.id}]') 
            else:
                logging.warning('no process to stop')

    def is_running(self):
        if self.process and self.process.poll() is None:
            return True
        return False

    def test(self):
        try:
            print(self.process.pid)
        except:
            print('notype')

    def read_output(self):
        global id
        output = ''
        while True:
            # 准备好的文件列表，返回包含3个列表的元组
            ready_to_read, ready_to_write, in_error = select.select([self.process.stdout], [], [self.process.stderr], 0)

            for pipe in ready_to_read:
                line = pipe.readline().decode('utf-8')
                output += line
                print('stdout:', self.file_name + f'[{self.id}]', line.strip())

            for pipe in in_error:
                line = pipe.readline().decode('utf-8')
                output += line
                print('error: ', self.file_name + f'[{self.id}]', line.strip())

            if self.process.poll() is not None:
                break


