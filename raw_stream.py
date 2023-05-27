class RAWStream:
    def __init__(self):
        self.data = ""
    
    def add(self, s):
        self.data += s
    
    def read(self, from_idx, to_idx):
        self.data = self.data[0:from_idx] + self.data[to_idx:len(self.data)]