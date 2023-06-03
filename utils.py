import api.session
import configuration
import session_manager

import getpass
import threading
import toml

import os

privileges_list = ["owner", "admin", "user", "monitor"]

def soft_exit():
    exit_st = True
    print("exiting")
    exit() 

def get_token():
    if api.session.token == "":
        return "not authed"
    return api.session.token

def get_session():
    if api.session.token == "":
        return "not authed"
    return f"username: {api.session.username}\ntoken: {api.session.token}\nprivileges: {api.session.privileges}"

def user_register_handler():
    if api.session.token == "":
        return "not authed"
    if api.session.privileges != "owner":
        return "permission denied. you don't have owner rights. your privileges: " + api.session.privileges
    
    username = input("username: ")
    password = getpass.getpass(prompt="password:")
    privileges = input("privileges: ")
    if privileges not in privileges_list:
        return "wrong privileges. privileges list: " + str(privileges_list)
    
    return api.auth.register_user(username, password, privileges)

def approve_device_handler(id):
    if api.session.token == "":
        return "not authed"
    
    name = input("device name: ")
    region = input("region: ")
    institution = input("institution: ")

    return api.auth.approve_device(id, name, region, institution)

def get_running_threads():
    threads = []
    for thread in threading.enumerate():
        if len(thread.name.split()) > 1:
            threads.append(thread.name.split()[1].replace("(", "").replace(")", ""))
        else:
            threads.append(thread.name)
    return threads

def get_sessions_text():
    if len(api.session.sessions) == 0:
        return "no sessions found"
    text = "sessions\n"
    for s in api.session.sessions:
        text += f"{s['username']} - {s['status']}\n"
    return text

def load_configuration(session):
    configuration.monitoring_mode = session["monitoring_mode"]
    configuration.monitoring_timeout = session["monitoring_timeout"]
    configuration.colored = session["colored"]

def save_session():
    obj = {"new-bell-admin-session": {}, "new-bell-admin-configuration": {}}

    obj["new-bell-admin-session"]["host"] = api.session.host
    obj["new-bell-admin-session"]["token"] = api.session.token
    obj["new-bell-admin-session"]["username"] = api.session.username

    obj["new-bell-admin-configuration"]["monitoring_mode"] = configuration.monitoring_mode
    obj["new-bell-admin-configuration"]["monitoring_timeout"] = configuration.monitoring_timeout
    obj["new-bell-admin-configuration"]["colored"] = configuration.colored

    if api.session.current_session_file != None:
        f = open(api.session.current_session_file, "w")
        f.write(toml.dumps(obj))
        f.close()


def update_configuration(key, value):
    if key == "mon_set":
        configuration.monitoring_mode = value.mode
        configuration.monitoring_timeout = value.timeout
    else:
        exec_cmd = "configuration." + key + " = " + str(value)
        try:
            exec(exec_cmd)
        except Exception as e:
            print("couldn't update configuration: " + str(e))
    
    save_session()

def login_by_session_wrapper(username):
    session_id = session_manager.get_session_id_by_username(username)
    if session_id == -1:
        return "no session with this username"
    session = api.session.sessions[session_id]
    ret = api.auth.login_by_session(api.session.sessions[session_manager.get_session_id_by_username(username)])
    if ret != 0:
        os.remove(session["filename"])
        del api.session.sessions[session_id]
        return "session expired. login manualy"
    session_manager.set_main_session(session)
    api.session.current_session_file = api.session.sessions[session_id]["filename"]

    r = api.utils.authed_post(api.session.host + "/api/users/info", {"username": username})
    if r.status_code != 200:
        return "successfull auth, but couldn't get privileges. response: " + r.text
    api.session.privileges = r.json()["privileges"]
    if api.session.current_session_file == None:
        api.session.current_session_file = username + ".session"
    save_session()

    return "logged in " + api.session.username

def get_server_headers():
    return ["id", "verified", "name", "host", "lastseen", "lastlogs", "lastupdate", "region", "institution", "cpu_temp"] # just consts from server