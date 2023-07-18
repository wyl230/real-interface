class Status:
    last_compressed_packet_id_list = {}

def check_worse_situation(sorted_list, ins_id, save = 5):
    if len(sorted_list) > save:
        Status.last_compressed_packet_id_list[ins_id] = sorted_list[save:]
        return sorted_list[:save]
    else: 
        Status.last_compressed_packet_id_list[ins_id] = []
        return sorted_list

def cal_loss_rate_using_compressed_packed_id(packet_id_list, ins_id, divider=True):
    if divider:
        packet_id_list = [packet_id for packet_id in packet_id_list if packet_id != -1]

    if ins_id in Status.last_compressed_packet_id_list:
        packet_id_list = Status.last_compressed_packet_id_list + packet_id_list
    
    from_list = packet_id_list[::2]
    to_list = packet_id_list[1::2]

    sorted_packet_id_list = sorted([(from_id, to_id) for from_id, to_id in zip(from_list, to_list)], key=lambda x: x[0])

    sorted_packet_id_list = check_worse_situation(sorted_packet_id_list, ins_id)

    loss_rate = sum(list(map(lambda x, y: y[0] - x[1] - 1, sorted_packet_id_list[:-1], sorted_packet_id_list[1:] ))) / (packet_id_list[-1] - packet_id_list[0])
    return loss_rate

# print(cal_loss_rate_using_compressed_packed_id([1, -1, 10, 15, -1, 100, 1000, -1, 2000], 3))