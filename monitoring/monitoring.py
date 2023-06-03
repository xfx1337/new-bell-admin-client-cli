import requests
import threading
import re
import json
import copy

import socketio


import api.session
import api.info

import os
import time
from datetime import datetime, timedelta

from monitoring.kbhit import KBHit

import cmd_manager
import configuration
import utils

import socketio

class MonitoringSet:
    def __init__(self):
        self.timeout = 5
        self.terminal_enabled_st = False
        self.mode = "on_update"

class Monitoring:
    def __init__(self, data, exit_st, set: MonitoringSet): # size - terminal size
        self.exit_st = exit_st
        self.data = data
        self.size = os.get_terminal_size()
        self.update = True
        self.reload_st = True
        self.last_update = datetime.now()
        self.pause = False
        self._force_st = False
        self._first_run = True
        self.wait_st = [True]

        self.packets_got = 0

        self.set = set

        self.headers = ["id", "verified", "name", "host", "lastseen", "lastlogs", "lastupdate", "region", "institution", "cpu_temp"] # just consts from server

        self.real_columns = len(self.data[0])-1 # not showing password
        self.real_lines = (self.size.lines-7) // 2

        self.last_id = 0 # variable storing from what id table is displaing

        for i in range(len(data)):
            self.data[i] = self.data[i][0:4] + self.data[i][5:len(self.data[i])]

        if not self.set.terminal_enabled_st:
            self._keyboard_thread = threading.Thread(target=self._key_reader, daemon=True)
            self._keyboard_thread.start()

        if self.set.mode == "timeout":
            self.update = False

    def show_devices(self):
        try:
            while not self.exit_st[0]:
                if not self._force_st:
                    if self.pause:
                        continue
                    if not self.update:
                        if self.set.mode == "timeout":
                            if not self._first_run:
                                if datetime.now() > self.last_update + timedelta(seconds=self.set.timeout):
                                    self.last_update = datetime.now()
                                else:    
                                    continue
                        else:
                            continue
                    else:
                        if self.set.mode != "on_update":
                            self.update = False
                            continue
                else:
                    self._force_st = False

                self.size = os.get_terminal_size()

                os.system('cls' if os.name == 'nt' else 'clear')
                
                print(f"showing devices from {self.last_id+1} to {(len(self.data)-1 if self.last_id+self.real_lines > len(self.data)-1 else self.last_id+self.real_lines-1)+1}. total: {len(self.data)}")
                print("")

                column_size = self._calculate_column_size()    
                
                positions = [0]
                headers_str = ""
                for i in range(self.real_columns):
                    headers_str += (self.headers[i] + column_size*" ")
                    positions.append(len(headers_str))

                headers_str = headers_str[0:len(headers_str)-column_size]
                print(headers_str + "\n")
                
                output = ""

                for i in range(self.last_id, (len(self.data) if self.last_id+self.real_lines > len(self.data)-1 else self.last_id+self.real_lines)):
                    headers_str = ""
                    for j in range(len(self.data[i])):
                        info = self.data[i][j]
                        if len(str(info)) > len(self.headers[j])+column_size//2:
                            info = str(info)[0:len(self.headers[j])+column_size//2-4] + "..."
                        headers_str = headers_str + " "*(positions[j]-len(headers_str))
                        headers_str += str(info)
                    output = output + headers_str + "\n\n" 
                print(output)
                print("press [d] to scroll down and [u] to scroll up. [r] - data reload. [t] - terminal. [q] - to quit")

                self.update = False
                self.wait_st[0] = True

                if self.set.terminal_enabled_st and self._first_run:
                    self._pause()
                    threading.Thread(target=self._enter_terminal, daemon=True).start()
                self._first_run = False

            return
        except Exception as e:
            print("something went wrong. error: " + str(e))
            self.exit_st[0] = True
            return
        
    def _scroll_down(self):
        if (len(self.data) if self.last_id+self.real_lines > len(self.data)-1 else self.last_id+self.real_lines) != len(self.data):
            self.last_id = (len(self.data) if self.last_id+self.real_lines > len(self.data)-1 else self.last_id+self.real_lines)
            self.update = True

    def _scroll_up(self):
        self.last_id =  (0 if self.last_id-self.real_lines < 0 else self.last_id-self.real_lines)
        self.update = True

    def _enter_terminal(self):
        if not self.set.terminal_enabled_st:
            self._pause()
            print("you are in monitoring mode terminal. you can go back to monitoring by pressing [q]. [d], [u], [r] works too.")
        self.set.terminal_enabled_st = True
        self.wait_st[0] = True
        cmd_manager.main(self.exit_st, entry_point="monitoring", cmd_controller=self._cmd_controller, wait_st=self.wait_st)
        time.sleep(3)
        self.set.terminal_enabled_st = False
        self._unpause()
        self._force_st = True
        self._keyboard_thread = threading.Thread(target=self._key_reader, daemon=True)
        self._keyboard_thread.start()

    def _cmd_controller(self, cmd):
        if cmd == "d":
            self._force_st = True
            self._scroll_down()
        elif cmd == "u":
            self._force_st = True
            self._scroll_up()
        elif cmd == "r":
            self._force_st = True
            return -1 # exit status for cmd_manager. he will stop his work and call full reload
        elif cmd == "timeout" or cmd == "on_update":
            self.set.mode = cmd
            utils.update_configuration("monitoring_mode", cmd)

        elif cmd == -1:
            self._reload()

        else:
            if type(cmd) == type(""):
                if cmd.startswith("set_monitoring_timeout"):
                    self.set.timeout = int(cmd.split()[1])
                    utils.update_configuration("monitoring_timeout", int(cmd.split()[1]))

        return 0

    def _reload(self):
        self.exit_st[0] = True
        os.system('cls' if os.name == 'nt' else 'clear')
        print("full data reload")
        self.reload_st = True

    def _pause(self):
        self.pause = True
    def _unpause(self):
        self.pause = False

    def _quit(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.reload_st = False
        self.set.terminal_enabled_st = False
        self.exit_st[0] = True

    def _update(self):
        self.update = True

    def _calculate_column_size(self):
        headers_text_count = len(str(self.headers).replace("[", "").replace("]", "").replace(", ", "").replace("'", ""))
        column = (self.size.columns - headers_text_count) // (self.real_columns-1)
        return column

    def _key_reader(self):
        kb = KBHit()
        while not self.exit_st[0]:
            if kb.kbhit():
                c = kb.getch()
                if c == "d":
                    self._scroll_down()
                elif c == "u":
                    self._scroll_up()
                elif c == "r":
                    self._reload()
                elif c == "t":
                    self._pause()
                    self._enter_terminal()
                    return
                elif c == "q":
                    self._quit()
                    break
    
    def inc_packets_got(self):
        self.packets_got += 1

def _process_body(data, body, monitor: Monitoring):
    for i in range(len(data)):
        if data[i][0] == body["id"]:
            for key in body.keys():
                try:
                    idx = monitor.headers.index(key)
                    data[i][idx] = body[key]
                except: pass
            if monitor.set.mode == "on_update":
                monitor._update()
            break

def _data_parse_stream(monitor: Monitoring):
    sio = socketio.Client()

    @sio.event(namespace="/monitoring")
    def update(data):
        monitor.inc_packets_got()
        _process_body(monitor.data, data, monitor)

    @sio.event(namespace="/monitoring")
    def disconnect():
        monitor.exit_st[0] = True

    def disconnection_task(exit_st):
        while not exit_st[0]:
            pass
        sio.disconnect()

    sio.connect(api.session.host, headers={"Authorization": "Bearer " + api.session.token}, namespaces=["/monitoring"])
    disconnection_task_thread = sio.start_background_task(disconnection_task, monitor.exit_st)
    sio.wait()


def monitor_all(size, set: MonitoringSet):
    utils.update_configuration("mon_set", set)
    
    if api.session.token == "":
        print("not authed")
        return False, set
    
    print("setting up")

    ret, data = api.info.get_devices()
    if ret != 0:
        print(data)
        return
    exit_st = [False] # pointers fuck u...

    monitor = Monitoring(data, exit_st, set)

    data_thread = threading.Thread(target=_data_parse_stream, args=(monitor, ), daemon=True)
    data_thread.start()

    ui_thread = threading.Thread(target=monitor.show_devices, daemon=True)
    ui_thread.start()

    while not exit_st[0]:
        pass

    return monitor.reload_st, copy.deepcopy(monitor.set)