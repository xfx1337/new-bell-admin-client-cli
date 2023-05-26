import requests
import threading
import re
import json

import api.session
import api.info

from simple_stream import Stream

import os
import time

from kbhit import KBHit

def _key_reader(exit_st, cmd):
    kb = KBHit()
    while not exit_st[0]:
        if kb.kbhit():
            cmd[0] = kb.getch()

def show_devices(data, size, saver={}): # size - terminal size(columns and lines)
    try:
        #math...
        headers = ["id", "verified", "name", "host", "lastseen", "lastlogs", "lastupdate", "region", "institution", "cpu_temp"]

        real_columns = len(data[0])-1 # not showing password
        real_lines = (size.lines-7) // 2

        last_id = 0
        exit_st = [False]
        local_exit = False
        cmd = [-1]
        lasthit = -1

        if saver != {}:
            last_id = saver["last_id"]
            exit_st = saver["exit_st"]
            cmd = saver["cmd"]
        else:
            pass
            #thread_keyboard = threading.Thread(target=_key_reader, args=(exit_st, cmd))
            #thread_keyboard.start()
        
        
        cmd[0] = -2

        while not exit_st[0]:
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print(f"showing devices from {last_id+1} to {(len(data)-1 if last_id+real_lines > len(data)-1 else last_id+real_lines-1)+1}. total: {len(data)}")
            print("")

            column_size = _calculate_column_size(headers, size.columns, real_columns)    
            
            positions = [0]
            headers_str = ""
            for i in range(real_columns):
                headers_str += (headers[i] + column_size*" ")
                positions.append(len(headers_str))

            headers_str = headers_str[0:len(headers_str)-column_size]
            print(headers_str + "\n")
            
            for i in range(last_id, (len(data) if last_id+real_lines > len(data)-1 else last_id+real_lines)):
                headers_str = ""
                real_data = data[i][0:4] + data[i][5:len(data)]    
                for j in range(len(real_data)):
                    info = real_data[j]
                    if len(str(info)) > len(headers[j])+column_size//2:
                        info = str(info)[0:len(headers[j])+column_size//2-3] + "..."
                    headers_str = headers_str + " "*(positions[j]-len(headers_str))
                    headers_str += str(info)

                print(headers_str + "\n")

            cmd = input("d - down, u - up. q - quit: ")

            if cmd == "d" or cmd == "down":
                if (len(data) if last_id+real_lines > len(data)-1 else last_id+real_lines) != len(data):
                    last_id = (len(data) if last_id+real_lines > len(data)-1 else last_id+real_lines)
            elif cmd == "u" or cmd == "up":
                last_id =  (0 if last_id-real_lines < 0 else last_id-real_lines)
            if cmd == "q" or cmd == "quit":
                os.system('cls' if os.name == 'nt' else 'clear')
                exit_st = [True]
            saver["last_id"] = last_id

            if local_exit == True:
                return
        return
    except:
        return

def _calculate_column_size(headers, columns, real_columns):
    headers_text_count = len(str(headers).replace("[", "").replace("]", "").replace(", ", "").replace("'", ""))
    column = (columns - headers_text_count) // (real_columns-1)
    return column

def _data_thread_worker(local_stream, exit_st):
    r = requests.post(api.session.host + "/api/admin/statistics", headers={"Authorization": "Bearer " + api.session.token}, stream=True)
    for line in r.iter_lines():
        if exit_st[0]: # by pointer
            break
        if line:
            decoded_line = line.decode('utf-8')
            result = re.search('[ResponseStart](.*)[ResponseEnd]', decoded_line).group(1)
            got = json.loads(result)["data"]
            local_stream.add(got)

def _data_thread_setter(local_stream, data, exit_st):
    while not exit_st[0]:
        if len(local_stream.queue) > 0:
            for body in local_stream[0]:
                _process_body(data, body)
            local_stream.read()

def _process_body(data, body):
    for entity in data:
        if entity["content"]["id"] == body["id"]:
            for key in body.keys():
                data[key] = body[key]


def monitor_all(size):
    if api.session.token == "":
        print("not authed")
        return
    ret, data = api.info.get_devices()
    if ret != 0:
        print(data)
        return
    exit_st = [False] # pointers fuck u...

    saver = {"last_id": 0, "exit_st": exit_st, "cmd": [-1]}

    local_stream = Stream()
    data_getting_thread = threading.Thread(target=_data_thread_worker, args=(local_stream, exit_st, ))
    data_setting_thread = threading.Thread(target=_data_thread_setter, args=(local_stream, data, exit_st, ))

    keyboard_thread = threading.Thread(target=_key_reader, args=(exit_st, saver["cmd"], ))
    keyboard_thread.start()

    #data_getting_thread.start()
    #data_setting_thread.start()

    while not exit_st[0]:
        threading.Thread(target=show_devices, args=(data, size, saver, )).start()
        time.sleep(5)
        return