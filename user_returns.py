HELP = """
[auth]
login [username] - login with username
session_info - info about current session

[session]
set_host [host] - change host
get_host - returns your current host
get_token - returns your token

[devices]
devices - list all devices and info about them
unverified - list all unverified devices and info about them
info [id] - get current info about device
monitor_all - real time monitoring of all devices
approve [id] - approve device with id

[admin]
get_events - get admin events
read_events - make events read
request [json] - make an admin request

[users]
delete_user [username]
register - register a user

[notes]
implemented - see really implemented functions. listed upper are not fully implemented
exit - exit
quit - quit
clear - clear screen
cls - clear screen
"""

IMPLEMENTED_LIST = """
[implemented]
cls
quit
login
session_info
set_host
get_token
get_host
get_events
read_events
register
approve
delete_user
info
devices
unverified
"""