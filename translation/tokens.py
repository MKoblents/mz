import re
from dataclasses import dataclass

from translation.models import TranslationError

NUMBER = re.compile(r"^(-?\d+|0x[0-9a-fA-F]+|\$[0-9a-fA-F]+)$")


class Token:
    kind: str
    text: str


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    position = 0
    length = len(text)
    while position < length:
        if text[position].isspace():
            position += 1
            continue
        end = position
        while end < length and not text[end].isspace():
            end += 1
        word = text[position:end]
        position = end
        if word == "\\":
            while position < length and text[position] != "\n":
                position += 1
        elif word == "(":
            close = text.find(")", position)
            if close < 0:
                raise TranslationError("unterminated comment")
            position = close + 1
        elif word in ('s"', '."'):
            close = text.find('"', position + 1)
            if close < 0:
                raise TranslationError("unterminated string")
            tokens.append(Token("str" if word == 's"' else "print", text[position + 1 : close]))
            position = close + 1
        else:
            tokens.append(Token("word", word))
    return tokens


def parse_number(word: str) -> int | None:
    if not NUMBER.match(word):
        return None
    if word.startswith("$"):
        return int(word[1:], 16)
    return int(word, 0) if word.lstrip("-").startswith("0x") else int(word)
