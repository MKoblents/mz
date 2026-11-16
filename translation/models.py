from dataclasses import dataclass

from isa import Opcode


class TranslationError(Exception):
    pass


@dataclass(frozen=True)
class DataRef:
    offset: int


Operand = int | DataRef


@dataclass
class Instr:
    opcode: Opcode
    operand: Operand = 0
    note: str = ""
