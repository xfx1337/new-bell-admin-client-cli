import api.session

from selectors_manager import SelectorsManager
from sockets_manager import SocketIO
import configuration

from singleton import singleton

import uuid

from utils import bcolors

selectors_manager = SelectorsManager()
socketIO = SocketIO()

@singleton
class ADMRequestManager:
    def __init__(self):
        self.processes = {}
        self.current_watching = 0
        self.responsed = True
        socketIO.set_exec_callback(self.callback)

    def callback(self, event, data):
        if data["content"]["execution_id"] in self.processes.keys():
            self.processes[data["content"]["execution_id"]]["responses"][data["content"]["device_id"]] = data["content"]

            if self.current_watching == data["content"]["execution_id"] and self.processes[data["content"]["execution_id"]]["data"]["content"]["wait_mode"]:
                print_response(data)

            if len(self.processes[data["content"]["execution_id"]]["responses"]) == len(self.processes[data["content"]["execution_id"]]["data"]["ids"]):
                self.processes[data["content"]["execution_id"]]["done"] = True
                if self.current_watching == data["content"]["execution_id"]:
                    self.responsed = True

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

        #TODO: do it...

    def interrupt(self, execution_id):
        data = {"type": "interrupt"}
        if execution_id == "all":
            data["execution_id"] = "all"
            data["ids"] = "all"
        else:
            if execution_id not in self.processes.keys():
                print("couldn't find process")
                return
            data["execution_id"] = execution_id
            data["ids"] = self.processes[execution_id]["data"]["ids"]

        socketIO.request(data)

    def execute(self, cmd):
        if api.session.token == "":
            print("not authed")
            return
        
        if len(selectors_manager.get_selected()) < 1:
            print("no devices selected")
            return
        
        ids = selectors_manager.get_selected().copy()
        self.responsed = False

        data = {
            "ids": ids,
            "type": "execute",
            "content": {"failsafe_mode": configuration.failsafe_mode, 
                "failsafe_timeout": configuration.failsafe_timeout, 
                "wait_mode": configuration.wait_mode, 
                "cmd": cmd,  
                "execution_id": uuid.uuid4().hex[:6].upper()}} # generate temprorary id for data transaction
        
        print("execution_id: " + data["content"]["execution_id"])

        self.processes[data["content"]["execution_id"]] = {"data": data, "responses": {}, "done": False}
        self.current_watching = data["content"]["execution_id"]
        socketIO.request(data)
        if configuration.wait_mode:
            while not self.responsed:
                pass
            del self.processes[data["content"]["execution_id"]]

    def watch(self, execution_id):
        if api.session.token == "":
            print("not authed")
            return
        
        if execution_id not in self.processes.keys():
            print("couldn't find process")
            return
        self.current_watching = execution_id
        self.responsed = False

        for r in self.processes[execution_id]["responses"]:
            print_response(r)

        if self.processes[execution_id]["done"]:
            return

        while not self.responsed:
            pass
    
    def close_process(self, execution_id):
        if api.session.token == "":
            print("not authed")
            return
        
        if execution_id == "all":
            self.processes = {}
            return

        if execution_id not in self.processes.keys():
            print("couldn't find process")
            return
        del self.processes[execution_id]

    def get_process_info(self, execution_id):
        if api.session.token == "":
            print("not authed")
            return
        if execution_id not in self.processes.keys():
            print("couldn't find process")
            return
        process = self.processes[execution_id]
        process_data = process["data"]
        print("")
        print("execution_id: " + execution_id)
        print("done: " + str(process["done"]).lower())
        print("ids: " + str(process_data["ids"]))
        print("type: " + process_data["type"])
        print("cmd: " + process_data["content"]["cmd"])
        print("failsafe mode: " + str(process_data["content"]["failsafe_mode"]).lower())
        print("failsafe_timeout: " + str(process_data["content"]["failsafe_timeout"]))
        print("wait_mode: " + str(process_data["content"]["wait_mode"]).lower())


    def get_processses(self):
        if len(self.processes.keys()) < 1:
            print("no processes running or executed")
            return
        
        print("")

        for p in self.processes.keys():
            p = self.processes[p]
            if p["done"] == False:
                print(f'{p["data"]["content"]["execution_id"]}: {p["data"]["type"]} -- {p["data"]["content"]["cmd"]} -- in progress')
        for p in self.processes.keys():
            p = self.processes[p]
            if p["done"] == True:
                print(f'{p["data"]["content"]["execution_id"]}: {p["data"]["type"]} -- {p["data"]["content"]["cmd"]} -- done')

        print("")

def print_response(data):
    print("device_id: " + str(data["content"]["device_id"]))
    print("response: " + data["content"]["response"])