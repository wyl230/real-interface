class ue_events:
    events = []

def set_ue_event(event):
    ue_events.events.append(event)

def get_ue_events():
    cur_events = ue_events.events[:]
    ue_events.events.clear()
    return cur_events
    