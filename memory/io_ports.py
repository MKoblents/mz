
class IOPorts:

    def __init__(self, input_text: str="")->None:
        self.input_buffer = list(input_text)
        self.output: list[str] = []

    def read_in(self) -> int:
        if not self.input_buffer:
            raise EOFError("input buffer is empty")
        return ord( self.input_buffer.pop(0))

    def write_out(self, value: int) -> None:
        self.output.append(chr(value & 0xFF))