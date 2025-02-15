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

def create_event(status, message):
    if api.session.token == "":
        return "not authed"
    r = api.utils.authed_post(api.session.host + "/api/admin/create_event", {"status": status, "message": message})
    if r.status_code != 200:
        return "couldn't create event. response: " + r.text
    return "event created"

def get_device_info(id):
    if api.session.token == "":
        return "not authed"
    r = api.utils.authed_post(api.session.host + "/api/devices/info", {"id": int(id)})
    if r.status_code != 200:
        return "couldn't get info. reponse: " + r.text

    data = r.json()
    output = "\ndevice:\n"
    for key in data.keys():
        if key == "time" or key == "lastseen":
            output += (f"{key}: {datetime.fromtimestamp(int(data[key])).strftime('%d.%m %H:%M')}\n")
        else:    
            info = str(data[key]).replace('\n', '\\n')
            output += (f"{key}: {info}\n")
    return output

def get_devices(unverified=False):
    if api.session.token == "":
        return -1, "not authed"
    r = api.utils.authed_post(api.session.host + "/api/admin/devices", {"unverified": unverified})
    data = r.json()
    if len(data) == 0:
        return -1, "no devices"
    return 0, data

def get_sql(sql):
    if api.session.token == "":
        return -1, "not authed"
    r = api.utils.authed_post(api.session.host + "/api/admin/sql_get", {"query": sql})
    if r.status_code != 200:
        return -1, r.text
    data = r.json()
    if len(data["data"]) == 0:
        return -1, "nothing found"
    return 0, data["data"]

def get_process_info(execution_id):
    if api.session.token == "":
        return -1, "not authed"
    r = api.utils.authed_post(api.session.host + "/api/admin/process_info", {"execution_id": execution_id})
    if r.status_code != 200:
        return -1, r.text
    data = r.json()
    return 0, data["data"]

def get_process_responses(execution_id):
    if api.session.token == "":
        return -1, "not authed"
    r = api.utils.authed_post(api.session.host + "/api/admin/get_process_responses", {"execution_id": execution_id})
    if r.status_code != 200:
        return -1, r.text
    data = r.json()
    return 0, data["data"]

def get_processes():
    if api.session.token == "":
        return -1, "not authed"
    r = api.utils.authed_post(api.session.host + "/api/admin/get_processes", {})
    if r.status_code != 200:
        return -1, r.text
    data = r.json()
    return 0, data["data"]