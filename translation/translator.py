from pathlib import Path

from isa import OPERAND_MAX, OPERAND_MIN, Opcode, to_signed, write_image
from translation.image import Image, build_image, listing
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

    def emit_literal(self, value: int) -> None:
        value = to_signed(value)
        if OPERAND_MIN <= value <= OPERAND_MAX:
            self.emit(Opcode.PUSH, value)
            return
        if value not in self.literals:
            self.literals[value] = self.allocate([value], [f"literal {value}"])
        self.emit(Opcode.PUSH, self.literals[value])
        self.emit(Opcode.LOAD)

    def fail(self, message: str) -> TranslationError:
        return TranslationError(f"{message} (token {self.index})")

    def next_word(self) -> str:
        self.index += 1
        if self.index >= len(self.tokens) or self.tokens[self.index].kind != "word":
            raise self.fail("name expected")
        return self.tokens[self.index].text
    
    def start_definition(self) -> None:
        name = self.next_word()
        if self.in_definition:
            raise self.fail("nested definition")
        self.in_definition = True
        self.target = self.code
        self.current_word = name
        self.current_start = self.here()
        self.words[name] = ("colon", self.current_start)

    def end_definition(self) -> None:
        if self.control:
            raise self.fail("unbalanced control structure")
        self.emit(Opcode.RET)
        self.in_definition = False
        self.target = self.entry

    def compile_word(self, word: str) -> None:
        if word in self.words:
            kind, value = self.words[word]
            if kind == "colon":
                self.emit(Opcode.CALL, value, word)
            elif kind == "var":
                self.emit(Opcode.PUSH, value, word)
            else:
                assert isinstance(value, int)
                self.emit_literal(value)
            return
        if word in PRIMITIVES:
            for opcode, operand in PRIMITIVES[word]:
                self.emit(opcode, operand)
            return
        number = parse_number(word)
        if number is not None:
            self.emit_literal(number)
            return
        raise self.fail(f"unknown word {word!r}")

    def compile_string(self, token: Token) -> None:
        self.emit(Opcode.PUSH, self.string_ref(token.text), "string")
        if token.kind == "print":
            if "pstr-type" not in self.words:
                raise self.fail("word pstr-type is required for .\"")
            self.emit(Opcode.CALL, self.words["pstr-type"][1], "pstr-type")

    def tick_word(self) -> None:
        name = self.next_word()
        if name not in self.words or self.words[name][0] == "const":
            raise self.fail(f"cannot take address of {name!r}")
        self.emit(Opcode.PUSH, self.words[name][1], name)

    def control_word(self, word: str) -> bool:
        handlers = {
            "if": self.do_if,
            "else": self.do_else,
            "then": self.do_then,
            "begin": self.do_begin,
            "until": self.do_until,
            "again": self.do_again,
            "while": self.do_while,
            "repeat": self.do_repeat,
            "do": self.do_do,
            "?do": self.do_qdo,
            "loop": self.do_loop,
        }
        if word not in handlers:
            return False
        handlers[word]()
        return True
    
    def do_if(self) -> None:
        self.control.append(("if", self.emit(Opcode.JZ), 0))

    def do_else(self) -> None:
        _, index, _ = self.pop_control("if")
        jump = self.emit(Opcode.JMP)
        self.patch(index, self.here())
        self.control.append(("else", jump, 0))

    def do_then(self) -> None:
        _, index, _ = self.pop_control("if", "else")
        self.patch(index, self.here())

    def do_begin(self) -> None:
        self.control.append(("begin", self.here(), 0))

    def do_until(self) -> None:
        _, address, _ = self.pop_control("begin")
        self.emit(Opcode.JZ, address)

    def do_again(self) -> None:
        _, address, _ = self.pop_control("begin")
        self.emit(Opcode.JMP, address)

    def do_while(self) -> None:
        self.control.append(("while", self.emit(Opcode.JZ), 0))

    def do_repeat(self) -> None:
        _, index, _ = self.pop_control("while")
        _, address, _ = self.pop_control("begin")
        self.emit(Opcode.JMP, address)
        self.patch(index, self.here())

    def do_do(self) -> None:
        self.emit(Opcode.SWAP)
        self.emit(Opcode.TOR)
        self.emit(Opcode.TOR)
        self.control.append(("do", self.here(), -1))

    def do_qdo(self) -> None:
        self.emit(Opcode.OVER)
        self.emit(Opcode.OVER)
        self.emit(Opcode.EQ)
        enter = self.emit(Opcode.JZ)
        self.emit(Opcode.DROP)
        self.emit(Opcode.DROP)
        skip = self.emit(Opcode.JMP)
        self.patch(enter, self.here())
        self.emit(Opcode.SWAP)
        self.emit(Opcode.TOR)
        self.emit(Opcode.TOR)
        self.control.append(("do", self.here(), skip))

    def do_loop(self) -> None:
        _, body, skip = self.pop_control("do")
        self.emit(Opcode.FROMR)
        self.emit(Opcode.PUSH, 1)
        self.emit(Opcode.ADD)
        self.emit(Opcode.RFETCH)
        self.emit(Opcode.OVER)
        self.emit(Opcode.EQ)
        done = self.emit(Opcode.JNZ)
        self.emit(Opcode.TOR)
        self.emit(Opcode.JMP, body)
        self.patch(done, self.here())
        self.emit(Opcode.DROP)
        self.emit(Opcode.FROMR)
        self.emit(Opcode.DROP)
        if skip >= 0:
            self.patch(skip, self.here())

    def pop_control(self, *kinds: str) -> tuple[str, int, int]:
        if not self.control or self.control[-1][0] not in kinds:
            raise self.fail(f"unexpected control word, expected {kinds}")
        return self.control.pop()

    def patch(self, index: int, address: int) -> None:
        self.code[index].operand = address

    def compile_in_definition(self, token: Token) -> None:
        if token.kind != "word":
            self.compile_string(token)
            return
        word = token.text
        if word == ";":
            self.end_definition()
        elif word == "recurse":
            self.emit(Opcode.CALL, self.current_start, self.current_word)
        elif word in ("'", "[']"):
            self.tick_word()
        elif word in ("[char]", "char"):
            self.emit_literal(ord(self.next_word()[0]))
        elif not self.control_word(word):
            self.compile_word(word)

    def flush_constants(self) -> None:
        for value in self.constants:
            self.emit_literal(value)
        self.constants = []

    def pop_constant(self) -> int:
        if not self.constants:
            raise self.fail("compile-time stack is empty")
        return self.constants.pop()

    def include(self) -> None:
        name = self.next_word()
        path = self.base_dir / name
        included = tokenize(path.read_text(encoding="utf-8"))
        self.tokens[self.index + 1 : self.index + 1] = included

    def define_data(self, word: str) -> bool:
        if word == "variable":
            name = self.next_word()
            self.words[name] = ("var", self.allocate([0], [f"variable {name}"]))
        elif word == "create":
            name = self.next_word()
            self.words[name] = ("var", DataRef(len(self.data)))
        elif word == "constant":
            name = self.next_word()
            self.words[name] = ("const", self.pop_constant())
        elif word == "allot" and self.constants:
            size = self.pop_constant()
            if size % 4:
                raise self.fail("allot size must be a multiple of 4")
            self.allocate([0] * (size // 4), ["allot"] * (size // 4))
        elif word == "," and self.constants:
            self.allocate([self.pop_constant()], ["data"])
        elif word == "cells" and self.constants:
            self.constants.append(self.pop_constant() * 4)
        else:
            return False
        return True

    def compile_top_level(self, token: Token) -> None:
        if token.kind != "word":
            self.flush_constants()
            self.compile_string(token)
            return
        word = token.text
        number = parse_number(word)
        if word == ":":
            self.flush_constants()
            self.start_definition()
        elif word == "include":
            self.include()
        elif number is not None:
            self.constants.append(number)
        elif word in self.words and self.words[word][0] == "const":
            value = self.words[word][1]
            assert isinstance(value, int)
            self.constants.append(value)
        elif not self.define_data(word):
            self.flush_constants()
            if word in ("'", "[']"):
                self.tick_word()
            else:
                self.compile_word(word)

    def translate(self, text: str) -> Image:
        self.tokens = tokenize(text)
        self.index = 0
        while self.index < len(self.tokens):
            token = self.tokens[self.index]
            if self.in_definition:
                self.compile_in_definition(token)
            else:
                self.compile_top_level(token)
            self.index += 1
        if self.in_definition:
            raise TranslationError("unterminated definition")
        self.flush_constants()
        if not self.entry or self.entry[-1].opcode is not Opcode.HALT:
            self.entry.append(Instr(Opcode.HALT))
        return build_image(self.code, self.entry, self.data, self.data_notes)

    def translate_file(self, source: Path) -> tuple[list[int], str]:
        image = self.translate(source.read_text(encoding="utf-8"))
        return image.words, listing(image)


    def run(self, argv: list[str]) -> None:
        if len(argv) != 2:
            raise SystemExit("usage: translator.py <source.fs> <target.bin>")
        source = Path(argv[0])
        self.base_dir = source.parent
        words, text = self.translate_file(source)
        write_image(argv[1], words)
        Path(argv[1] + ".hex").write_text(text, encoding="utf-8")
        lines = len(source.read_text(encoding="utf-8").splitlines())
        print(f"source LoC: {lines} words: {len(words)}")

