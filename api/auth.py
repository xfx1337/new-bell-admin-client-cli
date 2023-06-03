import requests
import hashlib

import api.session
import api.utils

import utils

def logout():
    api.session.username = ""
    api.session.token = ""
    api.session.privileges = ""
    api.session.current_session_file = None

def login_by_session(session):
    r = requests.post(session["host"] + "/api/valid_token", headers={"Authorization": "Bearer " + session["token"]})
    if r.status_code != 200:
        return -1
    return 0

def login(username, password):
    data = {"username": username, "password": hashlib.md5(password.encode("utf-8")).hexdigest()}
    r = requests.post(api.session.host + "/api/login", json = data)
    if r.status_code != 200:
        return "can't login. response: " + r.text
    else:
        api.session.username = username
        api.session.token = r.json()["token"]

        r = api.utils.authed_post(api.session.host + "/api/users/info", {"username": username})
        if r.status_code != 200:
            return "successfull auth, but couldn't get privileges. response: " + r.text
        api.session.privileges = r.json()["privileges"]
        if api.session.current_session_file == None:
            api.session.current_session_file = username + ".session"
        utils.save_session()
        return "successfull auth"

def register_user(username, password, privileges):
    r = api.utils.authed_post(api.session.host + "/api/users/register", {"user": {"username": username, 
                                                                               "password": hashlib.md5(password.encode("utf-8")).hexdigest(), 
                                                                               "privileges": privileges}})
    
    if r.status_code != 200:
        return "couldn't register user. response: " + r.text
    return "registered"

def approve_device(id, name, region, institution):
    r = api.utils.authed_post(api.session.host + "/api/admin/approve", {"device": {"id": int(id), "name": name, "region": region, "institution": institution}})
    if r.status_code != 200:
        return "couldn't approve. response: " + r.text
    return "approved"

def delete_user(username):
    if api.session.token == "":
        return "not authed"
    if api.session.privileges != "owner":
        return "permission denied. you don't have owner rights. your privileges: " + api.session.privileges
    
    r = api.utils.authed_post(api.session.host + "/api/users/delete", {"username": username})
    
    if r.status_code != 200:
        return "couldn't delete user. reponse: " + r.text
    return "deleted"