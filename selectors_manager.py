from singleton import singleton

import api.session
import api.info

import utils

@singleton
class SelectorsManager:
    def __init__(self):
        self.current_bank = None
        self.data = None

    def set_data_source(self, data):
        self.data = data

    def select(self, ids):
        self.current_bank = {"key": "ids", "value": None, "ids": ids}
        return "selected"

    def select_by(self, key, value):
        if self.data == None:
            return "select data source first"
        ids = []
        for i in range(len(self.data)):
            id = get_id_by_key(self.data, key)
            if id != -1:
                if self.data[i][get_id_by_key(self.data, key)] == value:
                    ids.append(i+1) 

        # key and value if using local selection system. if user request server for sql query(sql_query func here!!!): key=sql, value=[sql prompt]. 
        self.current_bank = {"key": key, "value": value, "ids": ids} 
        return "selected"

    def sql_get(self, sql):
        ret, ids = api.info.get_sql(sql)
        if ret != 0:
            return "couldn't make sql query. error: " + str(ids)
        self.current_bank = {"key": "sql", "value": sql, "ids": ids}  
        return "selected"

    def clear_current_bank(self):
        self.current_bank = None

    def get_selected(self):
        if self.current_bank != None:
            return self.current_bank["ids"]
        else:
            return []
        
def get_id_by_key(data, key):
    headers = utils.get_server_headers()
    for i in range(len(headers)):
        if headers[i] == key:
            return i
    return -1