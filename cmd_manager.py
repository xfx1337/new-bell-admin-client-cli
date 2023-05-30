import os, sys
import getpass

import api.session
import api.auth
import api.info

import user_returns
import monitoring
import utils
import time

def main(exit_st, entry_point="main", cmd_controller=None, wait_st=[True]):
    local_st = 0
    while not exit_st[0]:
        if entry_point == "monitoring": 
            if not wait_st[0]: # waiting for table to be showed
                continue
        try:
            cmd = input(">>> ")

            if cmd == "":
                pass
            
            elif cmd == "d" or cmd == "u" or cmd == "r":
                if entry_point != "monitoring":
                    print("you are not in monitoring mode")
                    continue
                wait_st[0] = False
                ret = cmd_controller(cmd)
                if ret == -1:
                    local_st = -1
                    break # exit func because main thread said
            
            elif cmd.startswith("set_monitoring_mode"):
                if entry_point != "monitoring":
                    print("you are not in monitoring mode")
                    continue
                wait_st[0] = False
                if cmd.split()[1] == "timeout":
                    print("terminal is not supported in this mode. you can go back in terminal by pressing [t]")
                    time.sleep(3)
                cmd_controller(cmd.split()[1])
                if cmd.split()[1] == "timeout":
                    cmd_controller("q")
                    local_st = -1
                    break # exit func because main thread said


            elif cmd.startswith("login"):
                username = cmd.split()[1]
                password = getpass.getpass(prompt="password:")
                print(api.auth.login(username, password))

            elif cmd.startswith("set_host"):
                api.session.host = cmd.split()[1]
                print("host changed")

            elif cmd == "get_host":
                print(api.session.host)

            elif cmd == "get_token":
                print(utils.get_token())

            elif cmd == "session_info":
                print(utils.get_session())

            elif cmd == "get_events":
                print(api.info.get_events())

            elif cmd.startswith("read_events"):
                ids = cmd.split()[1:len(cmd)]
                if len(ids) == 0:
                    print("no ids specified")
                    continue
                print(api.info.read_events(ids))

            elif cmd == "register":
                print(utils.user_register_handler())

            elif cmd.startswith("delete_user"):
                print(api.auth.delete_user(cmd.split()[1]))

            elif cmd.startswith("approve"):
                print(utils.approve_device_handler(cmd.split()[1]))

            elif cmd.startswith("info"):
                print(api.info.get_device_info(cmd.split()[1]))

            elif cmd == "devices":
                if entry_point != "main":
                    print("exit the table first")
                    continue
                ret, data = api.info.get_devices()
                if ret != 0:
                    print(data)
                    continue
                monitor = monitoring.Monitoring(data, [False])
                monitor.show_devices()
            elif cmd == "unverified":
                if entry_point != "main":
                    print("exit the table first")
                    continue
                ret, data = api.info.get_devices(True)
                if ret != 0:
                    print(data)
                    continue
                monitoring.show_devices(data, os.get_terminal_size())

            elif cmd == "monitor_all":
                if entry_point != "main":
                    print("exit the table first")
                    continue
                ret, term_st, update_mode = monitoring.monitor_all(os.get_terminal_size())
                while ret != False: # for reloading
                    ret, term_st, update_mode = monitoring.monitor_all(os.get_terminal_size(), term_st=term_st, update_mode=update_mode)

            elif cmd == "implemented":
                print(user_returns.IMPLEMENTED_LIST)

            elif cmd == "help":
                print(user_returns.HELP)
            elif cmd == "exit" or cmd == "quit" or cmd == "q":
                if entry_point == "monitoring":
                    local_st = 2
                    break
                utils.soft_exit()
            elif cmd == "clear" or cmd == "cls":
                os.system('cls' if os.name == 'nt' else 'clear')
            else:
                print("syntax error. read help")

        except KeyboardInterrupt:
            print("^C")
            continue
        except Exception as e:
            print(e)
            print("syntax error. read help")
    if local_st == -1:
        cmd_controller(-1)
    return