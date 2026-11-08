import csv
from dataclasses import dataclass

MICROCODE_WIDTH = 39
LABEL_COLUMN = 2
BITS_COLUMN = 3
ADDR_START = 30


class Microinstruction:
    latch_s: bool
    latch_pc: bool
    latch_sp: bool
    latch_rsp: bool
    latch_dr_alu: bool
    latch_dr_mem: bool
    latch_r: bool
    latch_t: bool
    latch_ar: bool
    latch_ir: bool
    latch_sr: bool
    mux_a_sel: int
    mux_b_sel: int
    const_sel: int
    alu_op: int
    mem_rd: bool
    mem_wr: bool
    halt: bool
    cond: int
    addr: int
    label: str = ""


def parse_microinstruction(bits: str, label: str = "") -> Microinstruction:
    if len(bits) != MICROCODE_WIDTH or set(bits) - {"0", "1"}:
        raise ValueError(f"bad microinstruction {label!r}: {bits!r}")

    def flag(index: int) -> bool:
        return bits[index] == "1"

    def number(start: int, stop: int) -> int:
        return int(bits[start:stop], 2)

    return Microinstruction(
        latch_s=flag(0),
        latch_pc=flag(1),
        latch_sp=flag(2),
        latch_rsp=flag(3),
        latch_dr_alu=flag(4),
        latch_dr_mem=flag(5),
        latch_r=flag(6),
        latch_t=flag(7),
        latch_ar=flag(8),
        latch_ir=flag(9),
        latch_sr=flag(10),
        mux_a_sel=number(11, 14),
        mux_b_sel=number(14, 17),
        const_sel=number(17, 19),
        alu_op=number(19, 23),
        mem_rd=flag(23),
        mem_wr=flag(24),
        halt=flag(25),
        cond=number(26, 30),
        addr=number(30, 39),
        label=label,
    )


def cell_to_bit(cell: str) -> str:
    return "1" if cell.strip() == "1" else "0"


def cells_to_bits(label: str, cells: list[str], labels: dict[str, int]) -> str:
    cells = cells + [""] * (MICROCODE_WIDTH - len(cells))
    head = "".join(cell_to_bit(cell) for cell in cells[:ADDR_START])
    target = cells[ADDR_START].strip()
    if target in labels:
        return head + format(labels[target], "09b")
    if target and not set(target) <= {"0", "1"}:
        raise ValueError(f"unknown jump label {target!r} in {label!r}")
    return head + "".join(cell_to_bit(cell) for cell in cells[ADDR_START:MICROCODE_WIDTH])


def load_microcode(path: str) -> tuple[list[Microinstruction], dict[str, int]]:
    rows: list[tuple[str, list[str]]] = []
    with open(path, newline="", encoding="utf-8") as file:
        for row in csv.reader(file):
            label = row[LABEL_COLUMN].strip() if len(row) > LABEL_COLUMN else ""
            if label and label != "метка":
                rows.append((label, row[BITS_COLUMN : BITS_COLUMN + MICROCODE_WIDTH]))
    labels = {label: index for index, (label, _) in enumerate(rows)}
    if len(labels) != len(rows):
        raise ValueError("duplicate microinstruction labels")
    rom = [parse_microinstruction(cells_to_bits(label, cells, labels), label) for label, cells in rows]
    return rom, labels


def load_decoder(path: str, labels: dict[str, int]) -> dict[int, int]:
    decoder: dict[int, int] = {}
    with open(path, newline="", encoding="utf-8") as file:
        for row in csv.reader(file):
            if len(row) < 2 or not row[0].strip():
                continue
            label = row[1].strip()
            if label not in labels:
                raise ValueError(f"unknown label {label!r} in decoder")
            decoder[int(row[0], 16)] = labels[label]
    return decoder