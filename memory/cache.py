
CACHE_LINES = 64
WORDS_PER_LINE = 4
LINE_BYTES = WORDS_PER_LINE * 4

class Cache:
    def __init__(self)->None:
        self.tags = [0] * CACHE_LINES
        self.data = [[0] * WORDS_PER_LINE for _ in range(CACHE_LINES)]
        self.valid = [False] * CACHE_LINES
        self.hits = 0
        self.misses = 0

    def split_address(self, address: int) -> tuple[int, int, int]:
        word = (address >> 2) % WORDS_PER_LINE
        index = (address >> 4) % CACHE_LINES
        tag = address >> 10
        return index, word, tag

    def lookup(self, address: int) -> bool:
        tag, index, _ = self.split(address)
        return self.valid[index] and self.tags[index] == tag

    def read_word(self, address: int) -> int:
        _, index, word = self.split(address)
        return self.data[index][word]

    def write_word(self, address: int, value: int) -> None:
        _, index, word = self.split(address)
        self.data[index][word] = value

    def invalidate(self, address: int) -> None:
        _, index, _ = self.split(address)
        self.valid[index] = False

    def set_tag(self, address: int) -> None:
        tag, index, _ = self.split(address)
        self.tags[index] = tag
        self.valid[index] = True