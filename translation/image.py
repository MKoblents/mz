from isa import (
    ADDRESS_OPCODES,
    IMAGE_LIMIT,
    decode,
    encode,
    format_instruction,
    to_signed,
)
from translation.models import DataRef, Instr, TranslationError


class Image:
    words: list[int]
    instruction_count: int
    notes: list[str]


def build_image(code: list[Instr], entry: list[Instr], data: list[int], data_notes: list[str]) -> Image:
    code[0].operand = len(code) * 4
    instructions = code + entry
    data_base = len(instructions) * 4
    words = []
    for instr in instructions:
        operand = instr.operand
        if isinstance(operand, DataRef):
            operand = data_base + operand.offset * 4
        words.append(encode(instr.opcode, operand))
    words.extend(data)
    if len(words) * 4 > IMAGE_LIMIT:
        raise TranslationError("program does not fit into memory")
    notes = [instr.note for instr in instructions] + data_notes
    return Image(words, len(instructions), notes)


def listing(image: Image) -> str:
    lines = []
    for index, word in enumerate(image.words):
        note = image.notes[index]
        if index < image.instruction_count:
            text = format_instruction(word)
            opcode, _ = decode(word)
            if opcode in ADDRESS_OPCODES and note:
                text += f" ; {note}"
        else:
            text = f".word {to_signed(word)}"
            if note:
                text += f" ; {note}"
        lines.append(f"{index * 4:04x} - {word:08X} - {text}")
    return "\n".join(lines) + "\n"
