import argparse
import logging
import sys
from pathlib import Path

from components.control_unit import ControlUnit
from components.data_path import DataPath
from isa import read_image
from memory.io_ports import IOPorts
from memory.memory_system import MemorySystem
from microcode.microcode import load_decoder, load_microcode

BASE_DIR = Path(__file__).resolve().parent
MICROCODE_PATH = str(BASE_DIR / "microcode" / "microcode.csv")
DECODER_PATH = str(BASE_DIR / "microcode" / "decoder.csv")
DEFAULT_LIMIT = 10_000_000

logger = logging.getLogger(__name__)


def simulation(
    image: list[int], input_text: str, limit: int, cache_enabled: bool = True
) -> tuple[str, ControlUnit, MemorySystem]:
    rom, labels = load_microcode(MICROCODE_PATH)
    decoder = load_decoder(DECODER_PATH, labels)
    io = IOPorts(input_text)
    memory = MemorySystem(io, cache_enabled)
    memory.ram.load_image(image)
    control_unit = ControlUnit(rom, decoder, DataPath(), memory)
    try:
        control_unit.run(limit)
    except EOFError:
        logger.warning("Input buffer is empty!")
    return "".join(io.output), control_unit, memory


def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("input")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--journal", default="")
    args = parser.parse_args(argv)
    if args.journal:
        logging.basicConfig(
            filename=args.journal, filemode="w", level=logging.DEBUG, format="%(message)s"
        )
    with Path(args.input).open(encoding="utf-8") as file:
        input_text = file.read()
    output, control_unit, memory = simulation(
        read_image(args.image), input_text, args.limit, not args.no_cache
    )
    print(output)
    print(f"ticks: {control_unit.ticks}")
    print(f"cache hits: {memory.cache.hits}, misses: {memory.cache.misses}")


if __name__ == "__main__":
    main(sys.argv[1:])
