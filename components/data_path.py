from typeguard import value

from microcode import Microinstruction

class Flags:
    n: bool = False
    z: bool = False
    v: bool = False
    c: bool = False

ALU_PLUS = 0
ALU_MINUS = 1
ALU_MUL = 2
ALU_DIV = 3
ALU_MOD = 4
ALU_AND = 5
ALU_OR = 6
ALU_XOR = 7
ALU_PASS_A = 8
ALU_PASS_B = 9
ALU_SHL = 10
ALU_SHR = 11

class DataPath:
    def __init__(self)->None:
        self.second=0
        self.program_counter=0
        self.stack_pointer=4096 #TODO ?
        self.return_stack_pointer=5000 #TODO ?
        self.data_register=0
        self.return_register=0
        self.top=0
        self.address_register=0
        self.instruction_register=0
        self.const=0
        self.status_register=Flags()

    def opcode(self) -> int:
        return self.instruction_register >> 8
    
    def select_a(self, signal):
        signal = int(signal, 2)
        if signal == 0:
            return self.sign_extend(self.instruction_register)
        elif signal == 1:
            return self.second
        elif signal == 2:
            return self.program_counter
        elif signal == 3:
            return self.stack_pointer
        elif signal == 4:
            return self.return_stack_pointer
        elif signal == 5:
            return self.data_register
        raise ValueError(f"bad mux_a_sel {signal}")


    def sign_extend(self, value:bytes):
        x=value[24]
        return x*8+value[24:] #TODO

    def divide(self, op: int, a: int, b: int) -> int:
        dividend, divisor = self.sign_extend(a), self.sign_extend(b)
        if divisor == 0:
            raise ZeroDivisionError("division by zero")
        quotient = abs(dividend) // abs(divisor)
        if (dividend < 0) != (divisor < 0):
            quotient = -quotient
        if op == 5:
            return int(quotient)
        return int(dividend - quotient * divisor)


    def select_b(self, signal:int, const_signal:int = None) -> int:
        signal = int(signal, 2)
        if signal == 0:
            return self.data_register
        elif signal == 1:
            return self.return_register
        elif signal == 2:
            return self.top
        elif signal == 3:
            return self.select_constant(const_signal)
        elif signal == 4:
            return self.address_register
        raise ValueError(f"bad mux_a_sel {signal}")


    def select_constant(self, signal: int) -> int:
        constants = {0: 0, 1: 1, 2: 4, 3: 8}
        if signal not in constants:
            raise ValueError(f"bad const_sel {signal}")
        return constants[signal]
        
    def select_alu(self, signal, A, B):
        signal = int(signal, 2)
        if signal == ALU_PLUS:
            return A + B
        elif signal == ALU_MINUS:
            return A - B
        elif signal == ALU_MUL:
            return A * B
        elif signal in (ALU_DIV, ALU_MOD):
            result = self.divide(signal, A, B)
        elif signal == ALU_AND:
            return A & B
        elif signal == ALU_OR:
            return A | B
        elif signal == ALU_XOR:
            return A ^ B
        elif signal == ALU_PASS_A:
            return A
        elif signal == ALU_PASS_B:
            return B
        elif signal == ALU_SHL:
            result = A << (B & 31)
        elif signal == ALU_SHR:
            result = A >> (B & 31)
        else:
            raise ValueError(f"bad alu_op {signal}")
        return result

    def deal(self, instruction_set):
        self.const = self.select_constant(instruction_set.get("const_sel"))
        res = self.select_alu(instruction_set.get("alu_sel"), self.select_a(instruction_set.get("mux_a_sel")), self.select_b(instruction_set.get("mux_b_sel")))
        if instruction_set.get("latch_s"):
            self.second = res
        if instruction_set.get("latch_pc"):
            self.program_counter = res
        if instruction_set.get("latch_sp"):
            self.stack_pointer = res
        if instruction_set.get("latch_rsp"):
            self.return_stack_pointer = res
        if instruction_set.get("latch_dr_alu"):
            self.data_register = res
        # if instruction_set.get("latch_dr_mem"):
            # self.data_register = res
        if instruction_set.get("latch_r"):
            self.return_register = res
        if instruction_set.get("latch_t"):
            self.top = res
        if instruction_set.get("latch_ar"):
            self.address_register = res
        if instruction_set.get("latch_ir"):
            self.instruction_register = res
        if instruction_set.get("latch_sr"):
            self.status_register = res

    def snapshot(self) -> str:
        flags = self.status_register
        return (
            f"PC:{self.program_counter:#06x} SP:{self.stack_pointer:#06x} "
            f"RSP:{self.return_stack_pointer:#06x} T:{self.sign_extend(self.top)} "
            f"S:{self.sign_extend(self.second)} R:{self.return_register:#x} "
            f"AR:{self.address_register:#06x} DR:{self.sign_extend(self.data_register)} "
            f"IR:{self.instruction_register:#010x} "
            f"NZVC:{int(flags.n)}{int(flags.z)}{int(flags.v)}{int(flags.c)}"
        )

    def compute(self, micro: Microinstruction) -> tuple[int, Flags]:
        a = self.select_a(micro.mux_a_sel)
        b = self.select_b(micro.mux_b_sel, micro.const_sel)
        return self.select_alu(micro.alu_op, a, b)

    def step(self, micro: Microinstruction, memory_data: int | None) -> None:
        result, flags = self.compute(micro)
        if micro.latch_s:
            self.second = result
        if micro.latch_pc:
            self.program_counter = result
        if micro.latch_sp:
            self.stack_pointer = result
        if micro.latch_rsp:
            self.return_stack_pointer = result
        if micro.latch_dr_alu:
            self.data_register = result
        if micro.latch_dr_mem and memory_data is not None:
            self.data_register = memory_data
        if micro.latch_r:
            self.return_register = result
        if micro.latch_t:
            self.top = result
        if micro.latch_ar:
            self.address_register = result
        if micro.latch_ir:
            self.instruction_register = result
        if micro.latch_sr:
            self.status_register = flags
    