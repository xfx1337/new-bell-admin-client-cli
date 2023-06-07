import api.session
import configuration
import session_manager

import getpass
import threading

import os

from sockets_manager import SocketIO

socketIO = SocketIO()

privileges_list = ["owner", "admin", "user", "monitor"]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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

    configuration.failsafe_mode = session["failsafe_mode"]
    configuration.failsafe_timeout = session["failsafe_timeout"]
    configuration.wait_mode = session["wait_mode"]

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
    
    session_manager.save_session()

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
    session_manager.save_session()

    return "logged in " + api.session.username

def get_server_headers():
    return ["id", "verified", "name", "host", "lastseen", "lastlogs", "lastupdate", "region", "institution", "cpu_temp"] # just consts from server

def print_configuration():
    out = f"""
monitoring_mode = {configuration.monitoring_mode}
monitoring_timeout = {configuration.monitoring_timeout}
colored = {configuration.colored}

wait_mode = {configuration.wait_mode}
failsafe_mode = {configuration.failsafe_mode}
failsafe_timeout = {configuration.failsafe_timeout}
    """
    print(out)