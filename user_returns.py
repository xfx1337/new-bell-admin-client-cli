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

[device selecting]
current - print currently selected devices
current_ids - print list of selected ids
source [monitoring/request] - select source of data. monitoring - real time data(works only in monitoring mode)
update_data - update data for selecting(works only for request source mode)
select [ids] - select by ids
select_by [key] = [value] - sql style selecting
select_sql [sql] - sql query to server
clear_selected - disable selection

[device execution]
execute [cmd] - execute cmd on selected devices
show_processes - show opened processes on devices
process_info [execution_id] - print process info
watch_process [execution_id] - wait for responses if wait_mode was disabled
close_process [execution_id] - disable watching on process. no outputs will be provided
close_process all - close all processes
execute_failsafe [true/false] - enable failsafe command interruption. [false] is really not recommended
execute_failsafe_timeout [seconds] - time before command will be automatically interrupted
execute_wait_mode [true/false] - wait for output of the execution

[device locking]
#lock - lock selected devices
#lock [id] - lock device with id
#unlock - unlock selected devices
#unlock [id] - unlock device with id

[device updating]
#update - update selected devices
#update all - update all devices
#update_custom [link] - update selected devices with custom git link
#update_custom [link] all - update all devices with custom git link

[admin]
get_events - get admin events
read_events - make events read
request [json] - make an admin request

[users]
delete_user [username]
register - register a user

[notes]
help - show this menu
configuration - show configuration
exit - exit
quit - quit
clear - clear screen
cls - clear screen

[debug]
dbg_show_threads - show current running threads
dbg_exec [python prompt] - execute
dbg_colored [true/false] - enable/disable colored output
dbg_interrupt [execution_id] - interrupt process
dbg_interrupt all - interrupt all processes that were started by administration
"""