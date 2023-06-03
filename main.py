import cmd_manager
import session_manager

print("new-bell-admin-client-cli v0.1\n")

session_manager.load_sessions()
cmd_manager.main([False])