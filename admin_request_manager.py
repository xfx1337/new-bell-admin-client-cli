import api.session
import api.info

from selectors_manager import SelectorsManager
from sockets_manager import SocketIO
import configuration

from singleton import singleton

import uuid
import time
from datetime import datetime

from utils import bcolors

selectors_manager = SelectorsManager()
socketIO = SocketIO()

@singleton
class ADMRequestManager:
    def __init__(self):
        self.current_watching = 0
        self.watching = False
        self.temporary_wait = False
        self.responsed = False
        socketIO.set_exec_callback(self.exec_callback)
        #socketIO.set_fw_callback(self.upd_callback)

    def exec_callback(self, event, data):
        if not self.watching and not self.temporary_wait:
            return
        
        if data["execution_id"] == self.current_watching:
            if event == "response":
                print_response(data)
            elif event == "process_end":
                self.watching = False
                self.responsed = True
            elif event == "device_response_status":
                print(data["data"].lower())
                self.temporary_wait = False
            elif event == "device_response_error":
                print(data["data"].lower())

            elif event == "request_error":
                print(data.lower())

    def upd_callback(self, event, data):
        print(data)

    def lock(self, selection=None):
        print("not implemented")
        pass

    def update(self, all_devices=False, link="default"):
        if api.session.token == "":
            print("not authed")
            return
        data = {}

        if len(selectors_manager.get_selected()) > 0:
            data["ids"] = selectors_manager.get_selected()
        else:
            if all_devices != "all":
                print("no devices selected")
                return

        if all_devices == "all":
            data["ids"] = "all"

        data["type"] = "update"
        data["link"] = link

        socketIO.update(data)
        #TODO: do

    def interrupt(self, execution_id):
        data = {"type": "interrupt"}
        if execution_id == "all":
            data["execution_id"] = "all"
            data["ids"] = "all"
        
        else:
            ret, info = api.info.get_process_info(execution_id)
            if ret != 0:
                print("couldn't get process info: " + info)
                return
            
            data["execution_id"] = execution_id
            data["ids"] = self.processes[execution_id]["data"]["ids"]

        self.temporary_wait = True
        save_current_watching = self.current_watching
        self.current_watching = execution_id
        socketIO.request(data)
        while self.temporary_wait:
            time.sleep(0.1)
            pass
        self.current_watching = save_current_watching

    def execute(self, cmd):
        if api.session.token == "":
            print("not authed")
            return
        
        if len(selectors_manager.get_selected()) < 1:
            print("no devices selected")
            return
        
        ids = selectors_manager.get_selected().copy()

        data = {
            "ids": ids,
            "type": "execute",
            "content": {"failsafe_mode": configuration.failsafe_mode, 
                "failsafe_timeout": configuration.failsafe_timeout, 
                "wait_mode": configuration.wait_mode, 
                "cmd": cmd,  
                "execution_id": uuid.uuid4().hex[:6].upper()}} # generate temprorary id for data transaction
        
        print("execution_id: " + data["content"]["execution_id"])

        self.current_watching = data["content"]["execution_id"]
        socketIO.request(data)
        if configuration.wait_mode:
            self.watching = True
            self.responsed = False
            while not self.responsed:
                time.sleep(0.1)
                pass
        

    def watch(self, execution_id):
        if api.session.token == "":
            print("not authed")
            return
        
        print("")

        ret, info = api.info.get_process_info(execution_id)
        if ret != 0:
            print("couldn't get process info: " + info)
            return

        ret, info = api.info.get_process_responses(execution_id)
        if ret != 0:
            self.current_watching = execution_id
            self.watching = True
            self.responsed = False

            while not self.responsed:
                time.sleep(0.1)
                pass

        else:
            print("responses:")
            for p in info:
                print_response(p["content"])
    
    def close_process(self, execution_id):
        if api.session.token == "":
            print("not authed")
            return
        
        if execution_id != "all":
            ret, data = api.info.get_process_info(execution_id)
            if ret != 0:
                print("couldn't get process info: " + data)
                return
            
            self.temporary_wait = True
            save_current_watching = self.current_watching
            self.current_watching = execution_id
            socketIO.request({"type": "close_process", "execution_id": execution_id})
            while self.temporary_wait:
                time.sleep(0.1)
                pass
            self.current_watching = save_current_watching
        else:
            socketIO.request({"type": "close_process", "execution_id": execution_id})
            print("request sent")


    def get_process_info(self, execution_id):
        if api.session.token == "":
            print("not authed")
            return

        ret, data = api.info.get_process_info(execution_id)
        if ret != 0:
            print("couldn't get process info: " + data)
            return

        print("")
        print("execution_id: " + execution_id)
        print("status: " + str(data["status"]).lower())
        print("ids: " + str(data["ids"]).replace("[", "").replace("]", "").replace(", ", ""))
        print("cmd: " + data["cmd"])
        print("failsafe mode: " + str(data["failsafe_mode"]).lower())
        print("failsafe_timeout: " + str(data["failsafe_timeout"]))
        print("wait_mode: " + str(data["wait_mode"]).lower())


    def get_processses(self):
        ret, data = api.info.get_processes()

        print("")

        if ret != 0:
            print("couldn't get processes " + data)
            return

        if len(data) == 0:
            print("no processes")
            return

        for p in data:
            if p["status"] == "IN_PROGRESS":
                print(f'{p["execution_id"]}: {p["cmd"]} -- in progress')
        for p in data:
            if p["status"] == "DONE":
                print(f'{p["execution_id"]}: {p["cmd"]} -- done')
        for p in data:
            if p["status"] == "INTERRUPTED":
                print(f'{p["execution_id"]}: {p["cmd"]} -- interrupted')
            

        print("")

def print_response(data):
    print("device_id: " + str(data["id"]))
    print("response: " + data["response"])
    print("errors: " + data["errors"])
    print("time: " + datetime.fromtimestamp(int(data["time"])).strftime("%d.%m.%Y %H:%M:%S"))