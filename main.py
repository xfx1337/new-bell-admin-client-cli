import cmd_manager
import session_manager
from admin_request_manager import ADMRequestManager
import os, signal

def ignore(signum, frame):
    pass

signal.signal(signal.SIGINT, ignore)
#signal.signal(signal.CTRL_C_EVENT, ignore)
signal.signal(signal.SIGBREAK, ignore)
#signal.signal(signal.CTRL_BREAK_EVENT, ignore)



print("new-bell-admin-client-cli v1.0\n")

session_manager.load_sessions()
ADMRequestManager() # singleton
cmd_manager.main([False])