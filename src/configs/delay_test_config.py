class DelayTestConfig:
    cur = {}

def set(info):
    DelayTestConfig.cur = info

def get():
    cur = DelayTestConfig.cur
    return [ {
        "start_id": start_id,
        "end_id": end_id,
        "set_delay": set_delay,
        "real_delay": real_delay,
    } for start_id, end_id, set_delay, real_delay in zip(cur.start_id, cur.end_id, cur.set_delay, cur.real_delay)]
    