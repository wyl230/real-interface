import sys
import config
def set_local_mqtt():
    args = sys.argv
    arg1 = 0
    if len(args) > 1:
        arg1 = int(args[1])
        print('local mqtt')
    if arg1 == 1:
        config.set_local_mqtt(True)
    else:
        config.set_local_mqtt(False)
set_local_mqtt()

import uvicorn
import time
from src.routes import start_asyncio

# 异步接受udp消息
import asyncio
import threading


if __name__ == "__main__":

    with open('status', 'w') as f:
        f.write('0')
    with open('packet_id.json', 'w') as f:
        f.write('{"1": 0}')
    # t1 = threading.Thread(target=worker, args=(1,))
    # t1 = threading.Thread(target=check_cpp_output)
    t2 = threading.Thread(target=start_asyncio)

    t2.start()

    uvicorn.run(app="src.app:api", host='0.0.0.0', reload=True, port=5002, log_level='error')

    t2.join()
