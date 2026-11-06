

from enum import Enum

from memory.cache import Cache
from memory.io_ports import IOPorts
from memory.ram import Ram

class State(Enum):
    IDLE = 0
    FILL = 1
    READ_RAM = 2
    WRITE_RAM = 3

class MemorySystem: 
    def __init__(self, io: IOPorts, cache_enabled: bool=True)->None:
        self.ram = Ram()
        self.cache = Cache()
        self.io = io
        self.cache_enabled = cache_enabled
        self.state = State.IDLE
        self.wait = 0
        self.fill_index=0
        self.pending_address = 0
        self.pending_data = 0

    def tick(self):
        if self.state is State.IDLE:
            return