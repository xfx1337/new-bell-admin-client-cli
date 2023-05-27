class Stream:
    def __init__(self):
        self.queue = []
    
    def add(self, body):
        self.queue.append(body)
    def read(self):
        del self.queue[0]