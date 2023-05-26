import requests
import api.session

def authed_post(host, m_json=""):
    r = requests.post(host, json = m_json, headers={"Authorization": "Bearer " + api.session.token})
    return r