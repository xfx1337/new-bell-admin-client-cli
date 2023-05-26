import os, sys
import getpass

import api.session
import api.auth
import api.info

import user_returns
import monitoring
import utils

exit_st = False # global variable to forcly exit

print("new-bell-client-cli v0.1")

while not exit_st:
    try:
        cmd = input(">>> ")

        if cmd == "":
            pass

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
            ret, data = api.info.get_devices()
            if ret != 0:
                print(data)
                continue
            monitoring.show_devices(data, os.get_terminal_size())
        elif cmd.startswith("unverified"):
            ret, data = api.info.get_devices(True)
            if ret != 0:
                print(data)
                continue
            monitoring.show_devices(data, os.get_terminal_size())

        elif cmd.startswith("monitor_all"):
            monitoring.monitor_all(os.get_terminal_size())

        elif cmd.startswith("implemented"):
            print(user_returns.IMPLEMENTED_LIST)

        elif cmd.startswith("help"):
            print(user_returns.HELP)
        elif cmd.startswith("exit") or cmd.startswith("quit") or cmd.startswith("q"):
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