HELP = """
[auth]
login [username] - login with username
session [name] - login in by session
logout - logout from account

[sessions]
sessions - list sessions
session_info - info about current session
set_host [host] - change host
get_host - returns your current host
get_token - returns your token

[devices]
devices - list all devices and info about them
unverified - list all unverified devices and info about them
info [id] - get current info about device
approve [id] - approve device with id
monitor_all - real time monitoring of all devices. enables monitoring mode
monitor_all [mode] - same as monitor_all, but with presetted monitoring mode. on_update or timeout
monitor_all timeout [seconds] - same as monitor_all, but with pressetted mode and timeout(only in timeout mode)

[monitoring mode only]
set_monitoring_mode [on_update/timeout] - sets monitoring mode
set_monitoring_timeout [timeout] - sets monitoring timeout(mode: timeout) in seconds

[admin]
get_events - get admin events
read_events - make events read
request [json] - make an admin request

[users]
delete_user [username]
register - register a user

[notes]
exit - exit
quit - quit
clear - clear screen
cls - clear screen

[debug]
dbg_show_threads - show current running threads
exec [python prompt] - execute
"""