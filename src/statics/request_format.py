from pydantic.main import BaseModel
from typing import List

# ue_status
# { "type": "ue", "id": 0, "time": 12328190, "access_sat": 11003, "up_link_bandwidth": 10000, "down_link_bandwidth": 10000, "up_link_packet": 20000000, "down_link_packet": 20000000, "up_link_byte": 200000000, "down_link_byte": 200000000, "location": { "longitude": 13.123, "latitude": 13.123, } }

class UeLocation(BaseModel):
    longitude: float
    latitude: float

class UeStatus(BaseModel):
    type: str
    id: int
    time: float
    access_sat: int
    up_link_bandwidth: int
    down_link_bandwidth: int
    up_link_packet: int
    down_link_packet: int
    up_link_byte: int
    down_link_byte: int
    location: UeLocation


# sat_status
# 都不清零 链路变化会清零
# 
# { "type": "sat", "id": 10001, "time": 12312, "location": { "longitude": 0, "latitude": 0 }, "neighbor_sat": [ { "id": 10001, "forward_packet": 10000, "receive_packet": 10000, "forward_byte": 10000, "receive_byte": 10000 }, { "id": 10002, "forward_packet": 10000, "receive_packet": 10000, "forward_byte": 10000, "receive_byte": 10000 } ], "total_up_packet": 10000, "total_down_packet": 10000, "total_up_byte": 1000000, "total_down_byte": 1000000 }


class SatLocation(BaseModel):
    longitude: float
    latitude: float

class neighbor_sat(BaseModel):
    id: int 
    forward_packet: int 
    receive_packet: int
    forward_byte: int 
    receive_byte: int
    bandwidth: int

# 星地*2 星间*2
class SatStatus(BaseModel):
    type: str
    id: int
    time: int
    location: SatLocation
    neighbor_sat: List[neighbor_sat]
    total_up_packet: int
    total_down_packet: int
    total_up_byte: int
    total_down_byte: int
    total_up_bandwidth: int
    total_down_bandwidth: int

# 
class single_ue_id(BaseModel):
    ue_id: int

class single_sat_id(BaseModel):
    sat_id: int

class double_sat_id(BaseModel):
    sat_id1: int
    sat_id2: int

class mission_type(BaseModel):
    interval: List[int]
    loss: List[int]
    throughput: List[int]
    avg_interval: int
    avg_loss: int
    avg_throughput: int

class UE_events(BaseModel):
    event: int
    time: float
    ue_id: int
    session_dst_ue_id: int 
    access_sat_id: int 
    switch_sat_id: int

class SetCBRRate(BaseModel):
    pps: int
    packet_size: int

class DelayTest(BaseModel):
    start_id: List[int]
    end_id: List[int]
    set_delay: List[int]
    real_delay: List[int]
