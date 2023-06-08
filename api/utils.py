import requests
import api.session
from datetime import datetime, timedelta

TIMEOUT = 5
import time

def authed_post(host, m_json=""):
    start_time = datetime.now()
    done = True
    while datetime.now() < start_time + timedelta(seconds=TIMEOUT):
        try:
            r = requests.post(host, json = m_json, headers={"Authorization": "Bearer " + api.session.token})
            done = True
            break
        except:
            time.sleep(0.1)
            done = False
    if done == False:
        print("[requests] http connection is broken")
    return r