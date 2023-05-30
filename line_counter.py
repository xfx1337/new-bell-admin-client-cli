import os, sys, time
import threading
start_time = time.time()

script_name = os.path.basename(__file__)

extensions = ["py", "h", "hpp", "c", "cpp"]
max_threads = 100
current_running = 0
proccessed = 0
runned = 0
queue = []
to_del = []
counter = 0

def inc_counter(num):
    global counter
    counter += num

def dec_current_running():
    global current_running
    current_running -= 1

def inc_current_running():
    global current_running
    current_running += 1

def thread_proccessed():
    global proccessed
    dec_current_running()
    proccessed += 1

def valid_extension(filename):
    for ext in extensions:
        if filename[-len(ext)-1:len(filename)] == "." + ext:
            return True
    if len(extensions) < 1:
        return True
    return False

# checking args for path and overwriten extensions
path = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) > 1:
    path = sys.argv[1]
if len(sys.argv) > 2:
    if sys.argv[2] == "*":
        extensions.clear()
    else:
        extensions.clear()
        for arg in sys.argv[2:len(sys.argv)]:
            extensions.append(arg)

def counter_thread(name):
    try:
        local_c = 0
        f = open(name, "r", encoding='utf-8')
        for l in f.readlines():
            local_c += 1
        print(name + " - " + str(local_c))
        inc_counter(local_c)
        thread_proccessed()
    except Exception as e:
        print("catched error in: " + name)
        print(e) 
        thread_proccessed()
    

# running scan
for path, subdirs, files in os.walk(path):
    for entry in files:
        name = os.path.join(path, entry)
        if entry == script_name:
            continue
        if valid_extension(name):
            th = threading.Thread(target=counter_thread, args=(name, ))
            if current_running < max_threads:
                th.start()
                runned += 1
                inc_current_running()
            else:
                queue.append(th)

i = 0
while i < len(queue):
    if current_running < max_threads:
        queue[i].start()
        runned += 1
        i += 1
        inc_current_running()

while runned != proccessed:
    pass

print(counter)
print("execution time: " + str(time.time() - start_time))