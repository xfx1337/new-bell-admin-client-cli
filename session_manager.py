import os
import toml

import api.session
import api.auth

import utils

import configuration

from sockets_manager import SocketIO

socketIO = SocketIO()

def _process_session(obj):
    session = {}
    if "new-bell-admin-session" not in obj or "new-bell-admin-configuration" not in obj:
        session["status"] = "not nba session"
        return session
    try:
        session["host"] = obj["new-bell-admin-session"]["host"]
        session["username"] = obj["new-bell-admin-session"]["username"]
        session["token"] = obj["new-bell-admin-session"]["token"]

        session["monitoring_mode"] = obj["new-bell-admin-configuration"]["monitoring_mode"]
        session["monitoring_timeout"] = obj["new-bell-admin-configuration"]["monitoring_timeout"]

        session["colored"] = obj["new-bell-admin-configuration"]["colored"]

        session["failsafe_mode"] = obj["new-bell-admin-configuration"]["failsafe_mode"]
        session["failsafe_timeout"] = obj["new-bell-admin-configuration"]["failsafe_timeout"]
        session["wait_mode"] = obj["new-bell-admin-configuration"]["wait_mode"]
    except:
        session["status"] = "invalid nba session"
        return session
    
    session["status"] = "ok"
    
    return session

def set_main_session(session):
    api.session.host = session["host"]
    api.session.username = session["username"]
    api.session.token = session["token"]
    session["status"] = "logged in"

    utils.load_configuration(session)

def logout():
    if api.session.token != "":
        api.session.sessions[get_session_id_by_username(api.session.username)]["status"] = "ok"

def _process_files(files_list):
    if len(files_list) < 1:
        return "No saved sessions found"
    for filename in files_list:
        try:
            text = open(filename, "r").read()
            session = _process_session(toml.loads(text))
            session["filename"] = filename
            api.session.sessions.append(session)
        except Exception as e:
            print(f"error while loading session [{filename}]: {str(e)}")

    if len(api.session.sessions) == 1:
        ret = api.auth.login_by_session(api.session.sessions[0])
        if ret != 0:
            print("session expired. login manualy")
            api.session.sessions = []
        if ret == 0:
            set_main_session(api.session.sessions[0])
            api.session.current_session_file = api.session.sessions[0]["filename"]
            print("logged in " + api.session.username)
            socketIO.wait_for_connection_established()
    else:
        print("found multiple sessions. you can login with: session [session_name]")
        print("to list sessions use: sessions")
    

def load_sessions():
    path = os.path.realpath(__file__)
    path = ("\\" if os.name == 'nt' else '/').join((path.split("\\") if os.name == 'nt' else path.split("/"))[0:-1])

    files = os.listdir(path)
    files_list = []

    for filename in files:
        if len(filename.split(".")) > 1:
            if filename.split(".")[-1] == "session":
                f = open(filename, "r")
                fr = f.read()
                if "[new-bell-admin-session]" not in fr:
                    f.close()
                    continue
                files_list.append(filename)
    _process_files(files_list)

def get_session_id_by_username(username):
    for i in range(len(api.session.sessions)):
        if api.session.sessions[i]["username"] == username:
            return i
    return -1

def save_session():
    obj = {"new-bell-admin-session": {}, "new-bell-admin-configuration": {}}

    obj["new-bell-admin-session"]["host"] = api.session.host
    obj["new-bell-admin-session"]["token"] = api.session.token
    obj["new-bell-admin-session"]["username"] = api.session.username

    obj["new-bell-admin-configuration"]["monitoring_mode"] = configuration.monitoring_mode
    obj["new-bell-admin-configuration"]["monitoring_timeout"] = configuration.monitoring_timeout
    
    obj["new-bell-admin-configuration"]["colored"] = configuration.colored

    obj["new-bell-admin-configuration"]["failsafe_mode"] = configuration.failsafe_mode
    obj["new-bell-admin-configuration"]["failsafe_timeout"] = configuration.failsafe_timeout
    obj["new-bell-admin-configuration"]["wait_mode"] = configuration.wait_mode

    if api.session.current_session_file != None:
        f = open(api.session.current_session_file, "w")
        f.write(toml.dumps(obj))
        f.close()
