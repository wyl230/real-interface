import time

def ms():
    return int(round(time.time() * 1000))

# start_time = millis()
# time_to_wait = 1000 # 1 second

# while True:
#     elapsed_time = millis() - start_time
#     if elapsed_time >= time_to_wait:
#         print("Time up!")
#         break
#     time.sleep(0.001) # sleep for 1 millisecond