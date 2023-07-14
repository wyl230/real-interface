class ue_events:
    events = []

def set_ue_event(event):
    ue_events.events.append(event)

def get_ue_events():
    cur_events = ue_events.events[:]
    if len(ue_events.events) > 20:
        ue_events.events = ue_events.events[-20:]
    return cur_events
    