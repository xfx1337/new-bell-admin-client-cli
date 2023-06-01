import socketio

sio = socketio.Client()
sio.connect('http://localhost:5000', namespaces="/monitoring")

sio.emit('message', {'from': 'client'})


@sio.on('response')
def response(data):
    print(data)  # {'from': 'server'}

@sio.on('update')
def update(data):
    print(data)

@sio.on("update")
def update2(data):
    print(data)
    
@sio.on('*')
def catch_all(event, sid, *args):
    print(f'catch_all(event={event}, sid={sid}, args={args})')