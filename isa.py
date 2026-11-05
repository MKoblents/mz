WORD_BITS = 32
WORD_MASK = 0xFFFFFFFF
SIGN_BIT = 0x80000000
OPERAND_BITS = 24
OPCODE_SHIFT = 24

MEMORY_BYTES = 0x10000
IN_PORT = 0x80
OUT_PORT = 0x84
DATA_STACK_INIT = 0xF7FC
RETURN_STACK_INIT = 0xFBFC


def to_unsigned(value: int) -> int:
    return value & WORD_MASK


def to_signed(value: int) -> int:
    value &= WORD_MASK
    return value - (1 << WORD_BITS) if value & SIGN_BIT else value


def sign_extend(value: int, bits: int) -> int:
    masked = value & ((1 << bits) - 1)
    sign = 1 << (bits - 1)
    return to_unsigned((masked ^ sign) - sign)