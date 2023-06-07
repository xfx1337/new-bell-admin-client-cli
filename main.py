import cmd_manager
import session_manager
from admin_request_manager import ADMRequestManager

print("new-bell-admin-client-cli v1.0\n")

session_manager.load_sessions()
ADMRequestManager() # singleton
cmd_manager.main([False])