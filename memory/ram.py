from isa import MEMORY_BYTES, WORD_MASK

RAM_LATENCY = 10


class Ram:
    def __init__(self) -> None:
        self.words = [0] * (MEMORY_BYTES // 4)

    def read(self, address: int) -> int:
        if address < 0 or address >= MEMORY_BYTES:
            raise ValueError(f"address {address:#04x} out of range")
        word_index = address // 4
        return self.words[word_index]

    def write(self, address: int, value: int) -> None:
        if address < 0 or address >= MEMORY_BYTES:
            raise ValueError(f"address {address:#04x} out of range")
        word_index = address // 4
        self.words[word_index] = value & WORD_MASK

    def load_image(self, image: list[int], base: int = 0) -> None:
        for offset, word in enumerate(image):
            self.write(base + offset * 4, word)
