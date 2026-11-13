from enum import IntEnum
WORD_BITS = 32
WORD_MASK = 0xFFFFFFFF
SIGN_BIT = 0x80000000
OPERAND_BITS = 24
OPCODE_SHIFT = 24
OPERAND_MASK = 0xFFFFFF
OPERAND_MIN = -(1 << (OPERAND_BITS - 1))
OPERAND_MAX = (1 << (OPERAND_BITS - 1)) - 1

MEMORY_BYTES = 0x10000
IN_PORT = 0x80
OUT_PORT = 0x84
DATA_STACK_INIT = 0xF7FC
RETURN_STACK_INIT = 0xFBFC


class Opcode(IntEnum):
    HALT = 0x00
    DUP = 0x01
    DROP = 0x02
    SWAP = 0x03
    OVER = 0x04
    RET = 0x05
    TOR = 0x06
    FROMR = 0x07
    RFETCH = 0x08
    EXEC = 0x09
    PUSH = 0x0A
    CALL = 0x10
    ADD = 0x11
    SUB = 0x12
    MUL = 0x13
    DIV = 0x14
    MOD = 0x15
    AND = 0x16
    OR = 0x17
    XOR = 0x18
    EQ = 0x19
    LT = 0x1A
    GT = 0x1B
    ULT = 0x1C
    SHL = 0x1D
    SHR = 0x1E
    LOAD = 0x20
    STORE = 0x21
    JZ = 0x30
    JMP = 0x31
    JNZ = 0x32


ADDRESS_OPCODES = {Opcode.CALL, Opcode.JZ, Opcode.JMP, Opcode.JNZ}
OPERAND_OPCODES = ADDRESS_OPCODES | {Opcode.PUSH}



def to_unsigned(value: int) -> int:
    return value & WORD_MASK


def to_signed(value: int) -> int:
    value &= WORD_MASK
    return value - (1 << WORD_BITS) if value & SIGN_BIT else value


def sign_extend(value: int, bits: int) -> int:
    masked = value & ((1 << bits) - 1)
    sign = 1 << (bits - 1)
    return to_unsigned((masked ^ sign) - sign)

def encode(opcode: Opcode, operand: int = 0) -> int:
    if not OPERAND_MIN <= operand <= OPERAND_MAX:
        raise ValueError(f"operand {operand} does not fit into {OPERAND_BITS} bits")
    return (int(opcode) << OPCODE_SHIFT) | (operand & OPERAND_MASK)


def decode(word: int) -> tuple[Opcode, int]:
    opcode = Opcode(word >> OPCODE_SHIFT)
    operand = to_signed(sign_extend(word, OPERAND_BITS))
    return opcode, operand


def format_instruction(word: int) -> str:
    opcode, operand = decode(word)
    name = opcode.name.lower()
    if opcode in ADDRESS_OPCODES:
        return f"{name} {operand:#06x}"
    if opcode is Opcode.PUSH:
        return f"{name} {operand}"
    return name


def write_image(path: str, words: list[int]) -> None:
    with open(path, "wb") as file:
        for word in words:
            file.write(to_unsigned(word).to_bytes(4, "little"))


def read_image(path: str) -> list[int]:
    with open(path, "rb") as file:
        data = file.read()
    if len(data) % 4:
        raise ValueError("image size is not a multiple of 4")
    return [int.from_bytes(data[i : i + 4], "little") for i in range(0, len(data), 4)]
