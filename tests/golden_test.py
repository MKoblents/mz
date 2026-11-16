import logging
import os
import shutil
import tempfile
from pathlib import Path

import pytest
import yaml

from machine import simulation
from translation.translator import Translator

ROOT = Path(__file__).resolve().parent.parent
GOLDEN_DIR = ROOT / "tests" / "golden"
EXAMPLES_DIR = ROOT / "examples"
LIMIT = 50_000_000
LOG_HEAD = 60
LOG_TAIL = 10

CASES = [
    ("hello", "hello.fs", ""),
    ("cat", "cat.fs", "foo\nbar\n"),
    ("hello_user_name", "hello_user_name.fs", "Alice\n"),
    ("sort", "sort.fs", "5 3 1 4 2 9\n"),
    ("double", "double.fs", ""),
    ("is_prime_283", "is_prime.fs", "283\n"),
    ("is_prime_zero", "is_prime.fs", "0\n"),
    ("format_string", "format_string.fs", "Foo %d bar %d\n232\n43\n"),
    ("format_string_align", "format_string.fs", "%5d|%-5d|\n42\n-42\n"),
    ("format_string_error", "format_string.fs", "%d\nabc\n"),
    ("linear_filter", "linear_filter.fs", "5 1 2 3 4 5\n"),
    ("xt", "xt.fs", ""),
]


class Capture(logging.Handler):
    def __init__(self) -> None:
        super().__init__(logging.DEBUG)
        self.lines: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.lines.append(record.getMessage())


def trim(lines: list[str]) -> str:
    if len(lines) > LOG_HEAD + LOG_TAIL:
        skipped = len(lines) - LOG_HEAD - LOG_TAIL
        lines = [*lines[:LOG_HEAD], f"... {skipped} lines skipped ...", *lines[-LOG_TAIL:]]
    return "\n".join(lines) + "\n"


def run_case(source_text: str, stdin: str) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "program.fs"
        source.write_text(source_text, encoding="utf-8")
        shutil.copy(EXAMPLES_DIR / "lib.fs", directory)
        image, code = Translator(source.parent).translate_file(source)
    capture = Capture()
    logger = logging.getLogger()
    old_level = logger.level
    logger.addHandler(capture)
    logger.setLevel(logging.DEBUG)
    try:
        output, control_unit, memory = simulation(image, stdin, LIMIT, cache_enabled=True)
    finally:
        logger.removeHandler(capture)
        logger.setLevel(old_level)
    _, plain_unit, _ = simulation(image, stdin, LIMIT, cache_enabled=False)
    return {
        "out_code": code,
        "out_stdout": output,
        "out_ticks": control_unit.ticks,
        "out_ticks_no_cache": plain_unit.ticks,
        "out_cache_hits": memory.cache.hits,
        "out_cache_misses": memory.cache.misses,
        "out_log": trim(capture.lines),
    }


def build_golden(_name: str, example: str, stdin: str) -> dict[str, object]:
    source_text = (EXAMPLES_DIR / example).read_text(encoding="utf-8")
    data: dict[str, object] = {"in_source": source_text, "in_stdin": stdin}
    data.update(run_case(source_text, stdin))
    return data


def dump(data: dict[str, object]) -> str:
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_style=None)


def str_presenter(dumper: yaml.Dumper, value: str) -> yaml.ScalarNode:
    style = "|" if "\n" in value else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


yaml.add_representer(str, str_presenter, Dumper=yaml.SafeDumper)  # type: ignore[arg-type]


def update_goldens() -> None:
    GOLDEN_DIR.mkdir(exist_ok=True)
    for name, example, stdin in CASES:
        (GOLDEN_DIR / f"{name}.yml").write_text(
            dump(build_golden(name, example, stdin)), encoding="utf-8"
        )


@pytest.mark.parametrize("path", sorted(GOLDEN_DIR.glob("*.yml")), ids=lambda p: p.stem)
def test_golden(path: Path) -> None:
    expected = yaml.safe_load(path.read_text(encoding="utf-8"))
    actual = run_case(expected["in_source"], expected["in_stdin"])
    for key, value in actual.items():
        assert value == expected[key], key


if os.environ.get("UPDATE_GOLDENS"):
    update_goldens()
