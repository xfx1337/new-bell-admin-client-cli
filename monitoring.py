import requests
import threading
import re
import json

import api.session
import api.info

from simple_stream import Stream
from raw_stream import RAWStream

import os
import time
from datetime import datetime, timedelta

from kbhit import KBHit

import cmd_manager

class Monitoring:
    def __init__(self, data, exit_st, terminal_enabled_st=False, update_mode="on_update"): # size - terminal size
        self.exit_st = exit_st
        self.data = data
        self.size = os.get_terminal_size()
        self.update = True
        self.reload_st = True
        self.timeout = 5
        self.last_update = datetime.now()
        self.pause = False
        self._force_st = False
        self._first_run = True
        self.wait_st = [True]
        self.terminal_enabled_st = terminal_enabled_st
        self.update_mode = update_mode

        self.headers = ["id", "verified", "name", "host", "lastseen", "lastlogs", "lastupdate", "region", "institution", "cpu_temp"] # just consts from server

        self.real_columns = len(self.data[0])-1 # not showing password
        self.real_lines = (self.size.lines-7) // 2

        self.last_id = 0 # variable storing from what id table is displaing

        for i in range(len(data)):
            self.data[i] = self.data[i][0:4] + self.data[i][5:len(self.data[i])]

        if not terminal_enabled_st:
            self._keyboard_thread = threading.Thread(target=self._key_reader, daemon=True)
            self._keyboard_thread.start()

    def show_devices(self):
        try:
            while not self.exit_st[0]:
                if not self._force_st:
                    if not self.update:
                        if self.update_mode == "timeout":
                            if datetime.now() > self.last_update + timedelta(seconds=self.timeout):
                                self.last_update = datetime.now()
                            else:    
                                continue
                        else:
                            continue
                    else:
                        if self.update_mode != "on_update":
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

                if self.terminal_enabled_st and self._first_run:
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
        if not self.terminal_enabled_st:
            self._pause()
            print("you are in monitoring mode terminal. you can go back to monitoring by pressing [q]. [d], [u], [r] works too.")
        self.terminal_enabled_st = True
        self.wait_st[0] = True
        cmd_manager.main(self.exit_st, entry_point="monitoring", cmd_controller=self._cmd_controller, wait_st=self.wait_st)
        self.terminal_enabled_st = False
        self._unpause()
        self._force_st = True
        self._keyboard_thread = threading.Thread(target=self._key_reader, daemon=True)
        self._keyboard_thread.start()

    def _cmd_controller(self, cmd):
        self._force_st = True
        if cmd == "d":
            self._scroll_down()
        elif cmd == "u":
            self._scroll_up()
        elif cmd == "r":
            return -1 # exit status for cmd_manager. he will stop his work and call full reload
        elif cmd == "timeout" or cmd == "on_update":
            self.update_mode = cmd
        
        elif cmd == -1:
            self._reload()

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
        self.terminal_enabled_st = False
        self.exit_st[0] = True

    def _force_update(self):
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

def _data_thread_getter(local_stream_raw, exit_st):
    while not exit_st[0]:
        try:
            r = requests.post(api.session.host + "/api/admin/statistics", headers={"Authorization": "Bearer " + api.session.token}, stream=True)
            for line in r.iter_lines():
                if exit_st[0]: # by pointer
                    break
                if line:
                    decoded_line = line.decode('utf-8')
                    local_stream_raw.add(decoded_line)
        except:
            pass

def _data_thread_handler(local_stream_raw: RAWStream, local_stream: Stream, exit_st):
    while not exit_st[0]:
        if "[ResponseStart]" in local_stream_raw.data and "[ResponseEnd]" in local_stream_raw.data:
            data = local_stream_raw.data
            start_idx = data.index("[ResponseStart]")
            end_idx = data.index("[ResponseEnd]")
            response = data[start_idx+15:end_idx]
            local_stream.add(json.loads(response))
            local_stream_raw.read(start_idx, end_idx+13)

def _data_thread_setter(local_stream: Stream, data, headers, exit_st):
    while not exit_st[0]:
        if len(local_stream.queue) > 0:
            for body in local_stream.queue[0]["data"]:
                _process_body(data, body, headers)
            local_stream.read()

def _process_body(data, body, monitor: Monitoring):
    for i in range(len(data)):
        if data[i][0] == body["content"]["id"]:
            for key in body["content"].keys():
                try:
                    idx = monitor.headers.index(key)
                    data[i][idx] = body["content"][key]
                except: pass
            monitor._force_update()
            break


def monitor_all(size, term_st=False, update_mode="on_update"):
    if api.session.token == "":
        print("not authed")
        return
    ret, data = api.info.get_devices()
    if ret != 0:
        print(data)
        return
    exit_st = [False] # pointers fuck u...

    
    monitor = Monitoring(data, exit_st, term_st, update_mode)
    local_stream = Stream()
    local_stream_raw = RAWStream()

    ui_thread = threading.Thread(target=monitor.show_devices, daemon=True)

    data_getting_thread = threading.Thread(target=_data_thread_getter, args=(local_stream_raw, exit_st, ), daemon=True)
    data_handling_thread = threading.Thread(target=_data_thread_handler, args=(local_stream_raw, local_stream, exit_st, ), daemon=True)
    data_setting_thread = threading.Thread(target=_data_thread_setter, args=(local_stream, data, monitor, exit_st, ), daemon=True)

    ui_thread.start()

    data_getting_thread.start()
    data_handling_thread.start()
    data_setting_thread.start()

    while not exit_st[0]:
        pass

    return monitor.reload_st, monitor.terminal_enabled_st, monitor.update_mode