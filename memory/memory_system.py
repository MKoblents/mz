

from enum import Enum

from memory.cache import Cache, WORDS_PER_LINE, LINE_BYTES
from memory.io_ports import IOPorts
from memory.ram import Ram, RAM_LATENCY
from isa import MEMORY_BYTES, OUT_PORT, IN_PORT

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

    def tick(self, address: int, write_data: int, read: bool, write: bool) -> tuple[int, bool]:
        if self.state is State.IDLE:
            if not (read or write):
                return 0, True
            self.check_address(address)
            if address in (OUT_PORT, IN_PORT):
                self.access_io(address, write_data,read, write)
            self.pending_address = address
            self.pending_data = write_data
            self.wait = RAM_LATENCY - 1
            if write:
                if self.cache_enabled and self.cache.lookup(address):
                    self.cache.write_word(address, write_data)
                self.state=State.WRITE_RAM
                return 0, False
            if not self.cache_enabled:
                self.state = State.READ_RAM
                return 0, False
            if self.cache.lookup(address):
                self.cache.hits += 1
                self.wait = 0
                return self.cache.read_word(address), True
            self.cache.misses += 1
            self.cache.invalidate(address)
            self.fill_index = 0
            self.state = State.FILL
            return 0, False
        self.wait -= 1
        if self.wait > 0:
            return 0, False
        if self.state is State.WRITE_RAM:
            self.ram.write(self.pending_address, self.pending_data)
            self.state = State.IDLE
            return 0, True
        if self.state is State.READ_RAM:
            self.state = State.IDLE
            return self.ram.read(self.pending_address), True
        line_base = self.pending_address - self.pending_address % LINE_BYTES
        word_address = line_base + self.fill_index * 4
        self.cache.write_word(word_address, self.ram.read(word_address))
        self.fill_index += 1
        if self.fill_index < WORDS_PER_LINE:
            self.wait = RAM_LATENCY
            return 0, False
        self.cache.set_tag(self.pending_address)
        self.state = State.IDLE
        return self.cache.read_word(self.pending_address), True


    def check_address(self, address: int) -> None:
        if address & 3:
            raise ValueError(f"unaligned access {address:#x}")
        if address >= MEMORY_BYTES or address <0:
            raise ValueError(f"address out of range {address:#x}")

    def access_io(self, address: int, write_data: int, read: bool, write: bool) -> tuple[int, bool]:
        if write:
            if address != OUT_PORT:
                raise ValueError(f"bad output port {address:#x}")
            self.io.write_out(write_data)
        if read:
            if address != IN_PORT:
                raise ValueError(f"bad input port {address:#x}")
            return self.io.read_in(), True
        return 0, False
    
