from singleton import singleton

import socketio
import threading
import time

import api.session

@singleton
class SocketIO:
    def __init__(self):
        self.connected = False

        self.mon_callback = None
        self.exec_callback = None
        self.fw_callback = None
        
        self.sio = None

        self._socket_thread = None

        self.exit_st = [False]
        self.exit_st_force = [False]
        self.__exit_st = [False]

    def socket_thread(self):
        self.sio = socketio.Client()

        @self.sio.event(namespace="/mainIO")
        def update(data):
            if self.mon_callback != None:
                self.mon_callback("update", data)

        @self.sio.event(namespace="/mainIO")
        def fw_update(data):
            if self.fw_callback != None:
                self.fw_callback("fw_update", data)

        @self.sio.event(namespace="/mainIO")
        def disconnect():
            if self.mon_callback != None:
                self.mon_callback("update", "EXIT")

        @self.sio.event(namespace="/mainIO")
        def connect():
            if self.mon_callback != None:
                self.mon_callback("establish", {})
            self.connected = True

        @self.sio.event(namespace="/mainIO")
        def response(data):
            if self.exec_callback != None:
                self.exec_callback("response", data)

        def disconnection_task(exit_st, exit_st_force):
            while not exit_st[0] and not self.exit_st_force[0]:
                time.sleep(0.1)
                pass
            self.sio.disconnect()
            self.connected = False
            self.exit_st_force[0] = False

        self.sio.connect(api.session.host, headers={"Authorization": "Bearer " + api.session.token}, namespaces=["/mainIO"], wait_timeout = 10)
        disconnection_task_thread = self.sio.start_background_task(disconnection_task, self.exit_st, self.exit_st_force)
        self.sio.wait()
    
    def set_fw_callback(self, callback):
        self.fw_callback = callback

    def set_mon_callback(self, callback):
        self.mon_callback = callback

    def set_exec_callback(self, callback):
        self.exec_callback = callback

    def request(self, data):
        self.sio.emit("request", data, namespace="/mainIO")

    def re_run(self):
        while api.session.token == "":
            time.sleep(0.1)
            pass

        self._socket_thread = threading.Thread(target=self.socket_thread, daemon=True)
        self._socket_thread.start() 

        while not self.exit_st[0]:
            time.sleep(0.1)
            if self.__exit_st[0] == True:
                self.__exit_st[0] = False
                self.connected = False
                self.exit_st_force[0] = True
                while self.exit_st_force[0]:
                    time.sleep(0.1)
                    pass
                while self._socket_thread.is_alive(): 
                    time.sleep(0.1)
                    pass
                self._socket_thread = threading.Thread(target=self.socket_thread, daemon=True)
                try: self._socket_thread.start() 
                except: breakpoint()
            pass

    def reconnect(self):
        self.__exit_st[0] = True

    def wait_for_connection_established(self):
        if api.session.token == "":
            return
        if self.connected:
            self.reconnect()
        else:
            self.re_run_thread = threading.Thread(target=self.re_run, daemon=True)
            self.re_run_thread.start()
        print("[socketio] connecting to server")
        while not self.connected:
            time.sleep(0.1)
            pass
        print("[socketio] connection established")