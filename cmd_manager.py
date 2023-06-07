import os, sys
import getpass
import time
import threading

import api.session
import api.auth
import api.info
from admin_request_manager import ADMRequestManager

import session_manager
from selectors_manager import SelectorsManager
import configuration

import user_returns
import monitoring.monitoring as monitoring
import utils

from sockets_manager import SocketIO

adm_request_manager = ADMRequestManager()
socketIO = SocketIO()

def main(exit_st, entry_point="main", cmd_controller=None, wait_st=[True]):
    selectors_manager = SelectorsManager() # singleton
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
                cmd_controller(cmd.split()[1])

            elif cmd.startswith("set_monitoring_timeout"):
                if entry_point != "monitoring":
                    print("you are not in monitoring mode")
                    continue
                cmd_controller(cmd)

            elif cmd.startswith("login"):
                session_manager.logout()
                api.auth.logout()
                username = cmd.split()[1]
                password = getpass.getpass(prompt="password:")
                print(api.auth.login(username, password))
                socketIO.wait_for_connection_established()

            elif cmd == "logout":
                api.auth.logout()
            
            elif cmd == "sessions":
                print(utils.get_sessions_text())
            
            elif cmd == "session_info":
                print(utils.get_session())

            elif cmd.startswith("session"):
                print(utils.login_by_session_wrapper(cmd.split()[1]))
                socketIO.wait_for_connection_established()

            elif cmd.startswith("set_host"):
                api.session.host = cmd.split()[1]
                session_manager.save_session()()
                print("host changed")

            elif cmd == "get_host":
                print(api.session.host)

            elif cmd == "get_token":
                print(utils.get_token())

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

            elif cmd.startswith("only_selected"):
                st = cmd.split()[1]
                if st == "true":
                    configuration.only_selected = True
                    configuration.only_down = False
                elif st == "false":
                    configuration.only_selected = False
                else:
                    print("true/false only")
                    
            elif cmd.startswith("only_down"):
                st = cmd.split()[1]
                if st == "true":
                    configuration.only_down = True
                    configuration.only_selected = False
                elif st == "false":
                    configuration.only_down = False
                else:
                    print("true/false only")

            elif cmd.startswith("monitor_all"):
                if entry_point != "main":
                    print("exit the table first")
                    continue
                
                monitoring_set = monitoring.MonitoringSet()
                if len(cmd.split()) > 1:
                    monitoring_set.mode = cmd.split()[1]
                    if len(cmd.split()) > 2:
                        monitoring_set.timeout = int(cmd.split()[2])

                ret, monitoring_set = monitoring.monitor_all(os.get_terminal_size(), monitoring_set)
                while ret != False: # for reloading
                    ret, monitoring_set = monitoring.monitor_all(os.get_terminal_size(), monitoring_set)

            elif cmd.startswith("source"):
                if len(cmd.split()) < 2:
                    print("you didn't select source of data. read help")
                    continue
                source = cmd.split()[1]
                if source == "monitoring":
                    if entry_point != "monitoring":
                        print("you are not in monitoring mode")
                        continue
                    selectors_manager.set_data_source(cmd_controller(-2))
                elif source == "request":
                    selectors_manager.set_data_source(api.info.get_devices()[1])
                else:
                    print("invalid data source")
                    continue
            
            elif cmd.startswith("select_sql"):
                print(selectors_manager.sql_get(cmd[11:]))

            elif cmd.startswith("select_by"):
                key = cmd.split()[1].split("=")[0]
                value = cmd.split("=")[-1].split()[0]
                print(selectors_manager.select_by(key, value))
            
            elif cmd.startswith("update_data"):
                selectors_manager.set_data_source(api.info.get_devices()[1])

            elif cmd.startswith("clear_selected"):
                selectors_manager.clear_current_bank()

            elif cmd.startswith("select"):
                print(selectors_manager.select(list(map(int, cmd.split()[1:]))))
    
            elif cmd.startswith("current_ids"):
                print("ids")
                print(*selectors_manager.get_selected())

            elif cmd.startswith("current"):
                if entry_point != "main":
                    print("exit the table first")
                    continue
                if selectors_manager.data == None:
                    print("set data source first. read help")
                    continue
                monitor = monitoring.Monitoring(selectors_manager.data, [False])
                monitor.show_devices()

            elif cmd.startswith("update_custom"):
                link = cmd.split()[1]
                all_devices = False
                if len(cmd.split()) > 2:
                    all_devices = cmd.split()[2]
                adm_request_manager.update(all_devices=all_devices, link=link)

            elif cmd.startswith("update"):
                if len(cmd.split()) > 1:
                    adm_request_manager.update(all_devices=cmd.split()[1])
                else:
                    adm_request_manager.update()

            elif cmd == "configuration":
                utils.print_configuration()

            elif cmd == "show_processes":
                adm_request_manager.get_processses()
            
            elif cmd.startswith("process_info"):
                adm_request_manager.get_process_info(cmd.split()[1])

            elif cmd.startswith("watch_process"):
                adm_request_manager.watch(cmd.split()[1])
            
            elif cmd.startswith("close_process"):
                adm_request_manager.close_process(cmd.split()[1])

            elif cmd.startswith("execute_failsafe_timeout"):
                sec = cmd.split()[1]
                configuration.failsafe_timeout = float(sec)
                session_manager.save_session()

            elif cmd.startswith("execute_failsafe"):
                st = cmd.split()[1]
                if st == "true":
                    configuration.failsafe_mode = True
                elif st == "false":
                    configuration.failsafe_mode = False
                else:
                    print("true/false only")
                session_manager.save_session()

            elif cmd.startswith("execute_wait_mode"):
                st = cmd.split()[1]
                if st == "true":
                    configuration.wait_mode = True
                elif st == "false":
                    configuration.wait_mode = False
                else:
                    print("true/false only")
                session_manager.save_session()

            elif cmd.startswith("execute"):
                real_cmd = cmd[8:]
                adm_request_manager.execute(real_cmd)

            elif cmd == "dbg_show_threads":
                for t in threading.enumerate():
                    print(t.name)
            
            elif cmd.startswith("dbg_interrupt"):
                adm_request_manager.interrupt(cmd.split()[1])

            elif cmd.startswith("dbg_colored"):
                st = cmd.split()[1]
                if st == "true":
                    configuration.colored = True
                    session_manager.save_session()
                elif st == "false":
                    configuration.colored = False
                    session_manager.save_session()
                else:
                    print("true/false only")
                

            elif cmd.startswith("dbg_exec"):
                exec(cmd[9:])

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