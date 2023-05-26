import os

import api.session
import api.utils

from datetime import datetime

def get_events():
    if api.session.token == "":
        return "not authed"
    r = api.utils.authed_post(api.session.host + "/api/admin/get_events")
    if r.status_code != 200:
        return "couldn't get events. response: " + r.text
    
    data = r.json()
    if "events" not in data:
        return "something internal"
    if len(data["events"]) == 0:
        return "no events"
    
    output = "events:\n\n"
    for evt in data["events"]:
        evt_t = ""
        for key in evt.keys():
            if key == "time":
                evt_t += (f"{key}: {datetime.fromtimestamp(evt[key])}\n")
            else:    
                evt_t += (f"{key}: {evt[key]}\n")
        output += (evt_t + "\n")
    
    return output[:-2]
        
def read_events(ids):
    if api.session.token == "":
        return "not authed"
    r = api.utils.authed_post(api.session.host + "/api/admin/read_events", {"ids": ids})
    if r.status_code != 200:
        return "couldn't read events. response: " + r.text
    return "events marked as read"

def get_device_info(id):
    if api.session.token == "":
        return "not authed"
    r = api.utils.authed_post(api.session.host + "/api/devices/info", {"id": int(id)})
    if r.status_code != 200:
        return "couldn't get info. reponse: " + r.text
    
    data = r.json()
    output = "\ndevice:\n"
    for key in data.keys():
        if key == "time":
            output += (f"{key}: {datetime.fromtimestamp(data[key])}\n")
        else:    
            output += (f"{key}: {data[key]}\n")
    return output

def get_devices(unverified=False):
    if api.session.token == "":
        return -1, "not authed"
    r = api.utils.authed_post(api.session.host + "/api/admin/devices", {"unverified": unverified})
    data = r.json()
    if len(data) == 0:
        return -1, "no devices"
    return 0, data
