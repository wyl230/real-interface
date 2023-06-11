import uvicorn
import time
import sys
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

    uvicorn.run(app="src.app:api", host='0.0.0.0', reload=True, port=5001)

    t2.join()
