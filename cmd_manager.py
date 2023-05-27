import os, sys
import getpass

import api.session
import api.auth
import api.info

import user_returns
import monitoring
import utils

def main(exit_st, entry_point="main", cmd_controller=None, wait_st=[True]):
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
                cmd_controller(cmd)
            
            elif cmd.startswith("set_monitoring_mode"):
                if entry_point != "monitoring":
                    print("you are not in monitoring mode")
                    continue
                wait_st[0] = False
                cmd_controller(cmd.split()[1])

            elif cmd.startswith("login"):
                username = cmd.split()[1]
                password = getpass.getpass(prompt="password:")
                print(api.auth.login(username, password))

            elif cmd.startswith("set_host"):
                api.session.host = cmd.split()[1]
                print("host changed")

            elif cmd.startswith("get_host"):
                print(api.session.host)

            elif cmd.startswith("get_token"):
                print(utils.get_token())

            elif cmd.startswith("session_info"):
                print(utils.get_session())

            elif cmd.startswith("get_events"):
                print(api.info.get_events())

            elif cmd.startswith("read_events"):
                ids = cmd.split()[1:len(cmd)]
                print(api.info.read_events(ids))

            elif cmd.startswith("register"):
                print(utils.user_register_handler())

            elif cmd.startswith("delete_user"):
                print(api.auth.delete_user(cmd.split()[1]))

            elif cmd.startswith("approve"):
                print(utils.approve_device_handler(cmd.split()[1]))

            elif cmd.startswith("info"):
                print(api.info.get_device_info(cmd.split()[1]))

            elif cmd.startswith("devices"):
                if entry_point != "main":
                    print("exit the table first")
                    continue
                ret, data = api.info.get_devices()
                if ret != 0:
                    print(data)
                    continue
                monitor = monitoring.Monitoring(data, [False])
                monitor.show_devices()
            elif cmd.startswith("unverified"):
                if entry_point != "main":
                    print("exit the table first")
                    continue
                ret, data = api.info.get_devices(True)
                if ret != 0:
                    print(data)
                    continue
                monitoring.show_devices(data, os.get_terminal_size())

            elif cmd.startswith("monitor_all"):
                if entry_point != "main":
                    print("exit the table first")
                    continue
                ret, term_st, update_mode = monitoring.monitor_all(os.get_terminal_size())
                while ret != False: # for reloading
                    ret = monitoring.monitor_all(os.get_terminal_size(), term_st=term_st, update_mode=update_mode)

            elif cmd.startswith("implemented"):
                print(user_returns.IMPLEMENTED_LIST)

            elif cmd.startswith("help"):
                print(user_returns.HELP)
            elif cmd.startswith("exit") or cmd.startswith("quit") or cmd.startswith("q"):
                if entry_point != "main":
                    return # it will return us in monitoring
                utils.soft_exit()
            elif cmd.startswith("clear") or cmd.startswith("cls"):
                os.system('cls' if os.name == 'nt' else 'clear')
            else:
                print("syntax error. read help")

        except KeyboardInterrupt:
            print("^C")
            continue
        except Exception as e:
            print(e)
            print("syntax error. read help")
    return