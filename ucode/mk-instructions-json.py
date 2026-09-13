#!/usr/bin/env python3

# Derive asm/instructions.json (the SCAMP assembler's instruction table) from
# ucode/ucode.s, which is the actual source of truth for mnemonic -> opcode
# assignment: each labelled block gets the next sequential opcode, exactly
# as uasm.py assigns it when building the microcode ROM.
#
# "cycles" is set to T_STATES for every instruction, since this architecture
# always pads a block's microcode out to a fixed number of T-states -- every
# instruction genuinely takes the same number of cycles. It only matters to
# the assembler for tie-breaking when multiple opcodes could match the same
# typed arguments.

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uasm import INSTR_RE, MAX_OPCODE, T_STATES, AsmError, normalize_line  # noqa: E402

# "# implicit: rN" on a line inside an instruction's block means the
# assembler should silently append an i8h-style operand addressing pseudo-
# register N, without the programmer writing it -- e.g. "xor x, y" needs a
# scratch register, but shouldn't require the caller to name one.
IMPLICIT_RE = re.compile(r"#\s*implicit:\s*r(\d+)\b", re.IGNORECASE)

# "# byte-order: 1,0" on a line inside an instruction's block overrides the
# order operand bytes are emitted in, independent of the order the caller
# types them (and the signature's own param order, used for matching). E.g.
# "out i32, (i8h)" keeps its natural "value, address" typing order, but the
# microcode wants the address (index 1) fetched before the value (index 0)
# to avoid clobbering AI -- "# byte-order: 1,0" emits param 1's bytes first.
BYTE_ORDER_RE = re.compile(r"#\s*byte-order:\s*([\d,\s]+)", re.IGNORECASE)


def extract_instructions(path):
    instructions = {}
    opcode = -1
    current_mnemonic = None

    with open(path) as fh:
        for lineno, raw_line in enumerate(fh, 1):
            m_implicit = IMPLICIT_RE.search(raw_line)
            if m_implicit and current_mnemonic is not None:
                instructions[current_mnemonic]["implicit_reg"] = int(m_implicit.group(1))

            m_byte_order = BYTE_ORDER_RE.search(raw_line)
            if m_byte_order and current_mnemonic is not None:
                instructions[current_mnemonic]["byte_order"] = [
                    int(n) for n in m_byte_order.group(1).split(",") if n.strip() != ""
                ]

            line = normalize_line(raw_line)
            if line == "":
                continue

            m = INSTR_RE.match(line)
            if not m:
                continue  # a microinstruction line, not a header

            mnemonic = m.group(1)
            opcode_hex = m.group(2)
            opcode += 1

            if opcode > MAX_OPCODE:
                raise AsmError(f"line {lineno}: too many opcodes: >{MAX_OPCODE}")
            if opcode_hex != "" and opcode != int(opcode_hex, 16):
                raise AsmError(
                    f"line {lineno}: wrong opcode for {mnemonic}: "
                    f"expected 0x{opcode_hex}, found {opcode}"
                )
            if mnemonic in instructions:
                raise AsmError(f"line {lineno}: duplicate instruction: {mnemonic}")

            instructions[mnemonic] = {"opcode": opcode, "cycles": T_STATES}
            current_mnemonic = mnemonic

    if opcode == -1:
        raise AsmError("opcode == -1 (maybe label your instructions?)")

    return instructions


def main():
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <ucode.s> <instructions.json>", file=sys.stderr)
        sys.exit(1)

    ucode_path, out_path = sys.argv[1], sys.argv[2]
    instructions = extract_instructions(ucode_path)

    with open(out_path, "w") as fh:
        json.dump(instructions, fh, indent=4, sort_keys=True)
        fh.write("\n")


if __name__ == "__main__":
    try:
        main()
    except AsmError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
