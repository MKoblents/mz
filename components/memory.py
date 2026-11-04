from components.data_path import DataPath

class Memory:
    def __init__(self, data_path: DataPath):
        self.data = [0] * 256 #TODO
        self.data_path = data_path