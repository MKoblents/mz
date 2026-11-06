from components.data_path import DataPath
from memory.memory_system import MemorySystem
from microcode.microcode import Microinstruction

DISPATCH=11

class ControlUnit:
    def __init__(
        self,
        rom: list[Microinstruction],
        decoder: dict[int, int],
        data_path: DataPath,
        memory: MemorySystem,
    ) -> None:
        self.rom = rom
        self.decoder = decoder
        self.data_path = data_path
        self.memory = memory
        self.mpc = 0
        self.mir = rom[0]
        self.halted = False
        self.ticks = 0

    def condition_taken(self, cond: int) -> bool:
        flags = self.data_path.status_register
        conditions = {
            0: False,
            1: True,
            2: flags.z,
            3: not flags.z,
            4: flags.v,
            5: not flags.v,
            6: flags.c,
            7: not flags.c,
            8: flags.n,
            9: not flags.n,
            10: flags.n != flags.v,
        }
        if cond not in conditions:
            raise ValueError(f"bad cond {cond}")
        return conditions[cond]

    def select_next_mpc(self, cond: int) -> int:
        if cond == DISPATCH:
            return 1
        if self.condition_taken(cond):
            return 2
        return 0

    def decoder_address(self) -> int:
        opcode = self.data_path.opcode()
        if opcode not in self.decoder:
            raise ValueError(f"unknown opcode {opcode:#04x}")
        return self.decoder[opcode]
        
    def get_next_mpc(self, micro: Microinstruction) -> int:
        select = self.select_next_mpc(micro.cond)
        if select == 1:
            return self.decoder_address()
        if select == 2:
            return micro.addr
        return self.mpc + 1

    def snapshot(self, micro: Microinstruction, waiting: bool) -> str:
        state = "WAIT" if waiting else "EXEC"
        return (
            f"TICK: {self.ticks:5} MPC: {self.mpc:3} {micro.label:10} {state} "
            f"{self.data_path.snapshot()}"
        )
    
    def tick(self) -> None:
        micro = self.mir
        data, ready = self.memory.tick(
            self.data_path.address_register,
            self.data_path.data_register,
            micro.mem_rd,
            micro.mem_wr,
        )
        self.ticks += 1
        waiting = (micro.mem_rd or micro.mem_wr) and not ready
        if waiting:
            return
        if micro.halt:
            self.halted = True
            return
        next_mpc = self.next_mpc(micro)
        self.data_path.tick(micro, data if micro.mem_rd else None)
        self.mpc = next_mpc
        self.mir = self.rom[next_mpc]

    def run(self, limit: int) -> None:
        while not self.halted and self.ticks < limit:
            self.tick()