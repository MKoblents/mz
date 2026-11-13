from pathlib import Path

from isa import OPERAND_MAX, OPERAND_MIN, Opcode, to_signed
from translation.image import Image, build_image
from translation.models import DataRef, Instr, Operand, TranslationError
from translation.primitives import PRIMITIVES
from translation.tokens import Token, parse_number, tokenize

class Translator:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.code:list[Instr] = [Instr(Opcode.JMP, 0, "entry")]
        self.entry:list[Instr] = []
        self.data:list[int] = []
        self.data_notes:list[str] = []
        self.target = self.entry
        self.words: dict[str, tuple[str, Operand]] = {}
        self.control: list[tuple[str, int, int]] = []
        self.constants: list[int] = []
        self.strings: dict[str, DataRef] = {}
        self.literals: dict[int, DataRef] = {}
        self.current_word = ""
        self.current_start = 0
        self.in_definition = False
        self.tokens: list[Token] = []
        self.index = 0

        def emit(self, opcode: Opcode, operand: Operand = 0, note: str = "") -> int:
            self.target.append(Instr(opcode, operand, note))
        return len(self.target) - 1

        def here(self) -> int:
            return len(self.code) * 4

        def allocate(self, words: list[int], notes: list[str]) -> DataRef:
            ref = DataRef(len(self.data))
            self.data.extend(words)
            self.data_notes.extend(notes)
        return ref

        def string_ref(self, text: str) -> DataRef:
            if text not in self.strings:
                words = [len(text)] + [ord(char) for char in text]
                notes = [f"length of {text!r}"] + [repr(char) for char in text]
                self.strings[text] = self.allocate(words, notes)
            return self.strings[text]

