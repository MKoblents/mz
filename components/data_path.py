from dataclasses import dataclass

from isa import (
    DATA_STACK_INIT,
    OPCODE_SHIFT,
    OPERAND_BITS,
    RETURN_STACK_INIT,
    SIGN_BIT,
    WORD_MASK,
    sign_extend,
    to_signed,
    to_unsigned,
)
from microcode.microcode import Microinstruction


@dataclass(frozen=True)
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
    def __init__(self) -> None:
        self.second = 0
        self.program_counter = 0
        self.stack_pointer = DATA_STACK_INIT
        self.return_stack_pointer = RETURN_STACK_INIT
        self.data_register = 0
        self.return_register = 0
        self.top = 0
        self.address_register = 0
        self.instruction_register = 0
        self.status_register = Flags()

    def opcode(self) -> int:
        return self.instruction_register >> OPCODE_SHIFT

    def select_a(self, signal: int) -> int:
        if signal == 0:
            return sign_extend(self.instruction_register, OPERAND_BITS)
        if signal == 1:
            return self.second
        if signal == 2:
            return self.program_counter
        if signal == 3:
            return self.stack_pointer
        if signal == 4:
            return self.return_stack_pointer
        if signal == 5:
            return self.data_register
        raise ValueError(f"bad mux_a_sel {signal}")

    def divide(self, op: int, a: int, b: int) -> int:
        dividend, divisor = to_signed(a), to_signed(b)
        if divisor == 0:
            raise ZeroDivisionError("division by zero")
        quotient = abs(dividend) // abs(divisor)
        if (dividend < 0) != (divisor < 0):
            quotient = -quotient
        if op == ALU_DIV:
            return to_unsigned(quotient)
        return to_unsigned(dividend - quotient * divisor)

    def select_b(self, signal: int, const_signal: int | None = None) -> int:
        if signal == 0:
            return self.data_register
        if signal == 1:
            return self.return_register
        if signal == 2:
            return self.top
        if signal == 3:
            return self.select_constant(const_signal)
        if signal == 4:
            return self.address_register
        raise ValueError(f"bad mux_b_sel {signal}")

    def select_constant(self, signal: int) -> int:
        constants = {0: 0, 1: 1, 2: 4, 3: 8}
        if signal not in constants:
            raise ValueError(f"bad const_sel {signal}")
        return constants[signal]

    def select_alu(self, signal: int, a: int, b: int) -> tuple[int, Flags]:
        carry = False
        overflow = False
        if signal == ALU_PLUS:
            full = a + b
            result = full & WORD_MASK
            carry = full > WORD_MASK
            overflow = bool((a ^ result) & (b ^ result) & SIGN_BIT)
        elif signal == ALU_MINUS:
            result = (a - b) & WORD_MASK
            carry = a < b
            overflow = bool((a ^ b) & (a ^ result) & SIGN_BIT)
        elif signal == ALU_MUL:
            result = to_unsigned(to_signed(a) * to_signed(b))
        elif signal in (ALU_DIV, ALU_MOD):
            result = self.divide(signal, a, b)
        elif signal == ALU_AND:
            result = a & b
        elif signal == ALU_OR:
            result = a | b
        elif signal == ALU_XOR:
            result = a ^ b
        elif signal == ALU_PASS_A:
            result = a
        elif signal == ALU_PASS_B:
            result = b
        elif signal == ALU_SHL:
            result = to_unsigned(a << (b & 31))
        elif signal == ALU_SHR:
            result = a >> (b & 31)
        else:
            raise ValueError(f"bad alu_op {signal}")
        flags = Flags(n=bool(result & SIGN_BIT), z=result == 0, v=overflow, c=carry)
        return result, flags

    def snapshot(self) -> str:
        flags = self.status_register
        return (
            f"PC:{self.program_counter:#06x} SP:{self.stack_pointer:#06x} "
            f"RSP:{self.return_stack_pointer:#06x} T:{to_signed(self.top)} "
            f"S:{to_signed(self.second)} R:{self.return_register:#x} "
            f"AR:{self.address_register:#06x} DR:{to_signed(self.data_register)} "
            f"IR:{self.instruction_register:#010x} "
            f"NZVC:{int(flags.n)}{int(flags.z)}{int(flags.v)}{int(flags.c)}"
        )

    def compute(self, micro: Microinstruction) -> tuple[int, Flags]:
        a = self.select_a(micro.mux_a_sel)
        b = self.select_b(micro.mux_b_sel, micro.const_sel)
        return self.select_alu(micro.alu_op, a, b)

    def tick(self, micro: Microinstruction, memory_data: int | None) -> None:
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
