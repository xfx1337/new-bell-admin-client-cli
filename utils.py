import api.session
import getpass

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
