#!/usr/bin/env python3

# Microcode assembler

import fileinput
import re
import sys

MAX_OPCODE = 255
T_STATES = 8

IS_ALU = {"EX", "NX", "EY", "NY", "F", "NO"}
IS_BUSOUT = {"PO", "MO8L", "MO8H", "MO16L", "MO16H", "MO32", "DO", "IVO"}
IS_BUSIN = {"AI", "MI8", "MI16", "MI32", "II", "XI", "YI", "DI", "IVI"}
IS_JMP = {"JC", "JZ", "JNZ", "JGT", "JLT", "JMP"}

UCODE = {
    "AI": 0x0001,
    "DI": 0x0002,
    "II": 0x0003,
    "XI": 0x0004,
    "YI": 0x0005,
    "IVI": 0x0006,
    # --------------
    "EO": 0x8000,
    "JZ": 0x0800,
    "JGT": 0x0400,
    "JLT": 0x0200,
    "NO": 0x0100,
    "F": 0x0080,
    "NY": 0x0040,
    "EY": 0x0020,
    "NX": 0x0010,
    "EX": 0x0008,
    # --------------
    "PO": 0x0000,
    "DO": 0x0008,
    "MO8L": 0x0010,
    "MO8H": 0x0018,
    "MO16L": 0x0020,
    "MO16H": 0x0028,
    "MO32": 0x0030,
    "IVO": 0x0038,
    # --------------
    "P+1": 0x1000,
    "P+2": 0x2000,
    "P+4": 0x3000,
    "RT": 0x4000,
    "MI8": 0x5000,
    "MI16": 0x6000,
    "MI32": 0x7000,
    "IEN": 0x0047,
    "IDS": 0x0087,
    # "EO": 0x8000,
    # "EX": 0x4000,
    # "NX": 0x2000,
    # "EY": 0x1000,
    # "NY": 0x0800,
    # "F": 0x0400,
    # "NO": 0x0200,
    # "PO": 0x0000,
    # "IOH": 0x1000,
    # "IOL": 0x2000,
    # "MO": 0x3000,
    # "VO": 0x7000,  # interrupt vector register onto the bus (was a hardwired constant; now software-settable via IVI)
    #                # bus_out code 7 ("spare_o7"/backplane pin 36) -- NOT code 4 ("spare_o4"/pin 34), which
    #                # doc/CARDS.md already bodge-wires to UART 0 TX for the serial console
    # "DO": 0x6100,  # 0x6000 for the bus_out decoder (to trigger the LED), 0x0100 for the actual signal
    # "RT": 0x0002,
    # "P+": 0x0400,
    # # the 2 bits that are free to toggle when !EO (see doc/UCODE.md "Extensibility"),
    # # repurposed here as pulses to set/clear the interrupt-enable flip-flop
    # "IEN": 0x0800,  # set interrupt-enable flip-flop (same bit as NY)
    # "IDS": 0x0200,  # clear interrupt-enable flip-flop (same bit as NO)
    # "AI": 0x0020,
    # "II": 0x0040,
    # "MI": 0x0060,
    # "XI": 0x0080,
    # "YI": 0x00a0,
    # "DI": 0x00c1,  # 0x00c0 for the bus_in decoder (to trigger the LED), 0x0001 for the actual signal
    # "IVI": 0x00e0,  # interrupt vector register input from bus (previously-spare busin code 7, see doc/CARDS.md "i7")
    # "JC": 0x0002,
    # "JZ": 0x0010,
    # "JNZ": 0x000c,
    # "JGT": 0x0008,
    # "JLT": 0x0004,
    # "JMP": 0x001c,  # JLT | JGT | JZ
}

ALU = {
    "XO": "EX F",
    "YO": "EY F",
    "-2": "NX NY F",
    "-1": "NO",
    "0": "",
    "1": "NX NY F NO",
    "X-1": "EX NY F",
    "X": "EX F",
    "X+1": "EX NX NY F NO",
    "-X-2": "EX NX NY F",
    "-X-1": "EX F NO",  # == ~X
    "-X": "EX NY F NO",
    "Y-1": "NX EY F",
    "Y": "EY F",
    "Y+1": "NX EY NY F NO",
    "-Y-2": "NX EY NY F",
    "-Y-1": "EY F NO",  # == ~Y
    "-Y": "NX EY F NO",
    "X+Y": "EX EY F",
    "Y+X": "EX EY F",
    "X+Y+1": "EX NX EY NY F NO",
    "Y+X+1": "EX NX EY NY F NO",
    "X-Y-1": "EX EY NY F",
    "X-Y": "EX NX EY F NO",
    "Y-X-1": "EX NX EY F",
    "Y-X": "EX EY NY F NO",
    "-X-Y-2": "EX NX EY NY F",
    "-Y-X-2": "EX NX EY NY F",
    "-X-Y-1": "EX EY F NO",
    "-Y-X-1": "EX EY F NO",
    "~X": "EX F NO",
    "~Y": "EY F NO",
    "X&Y": "EX EY",
    "Y&X": "EX EY",
    "X|Y": "EX NX EY NY NO",
    "Y|X": "EX NX EY NY NO",
    "X&~Y": "EX EY NY",
    "~Y&X": "EX EY NY",
    "X|~Y": "EX NX EY NO",
    "~Y|X": "EX NX EY NO",
    "~X|Y": "EX EY NY NO",
    "Y|~X": "EX EY NY NO",
    "~X&Y": "EX NX EY",
    "Y&~X": "EX NX EY",
    "~X&~Y": "EX NX EY NY",
    "~(X|Y)": "EX NX EY NY",
    "~Y&~X": "EX NX EY NY",
    "~(Y|X)": "EX NX EY NY",
    "~X|~Y": "EX EY NO",
    "~(X&Y)": "EX EY NO",
    "~Y|~X": "EX EY NO",
    "~(Y&X)": "EX EY NO",
}

INSTR_RE = re.compile(r"^([a-z_0-9, ()+-]+): ?([0-9a-f]*)$", re.IGNORECASE)


class AsmError(Exception):
    pass


def die(lineno, msg):
    raise AsmError(f"line {lineno}: {msg}")


def normalize_line(line):
    line = line.rstrip("\n")
    line = re.sub(r"#.*", "", line)  # strip comments
    line = re.sub(r"^\s+", "", line)  # strip leading spaces
    line = re.sub(r"\s$", "", line)  # strip trailing spaces
    line = re.sub(r"\s+", " ", line, count=1)  # collapse spaces
    return line


def encode(uinstr, mnemonic, lineno):
    bits = uinstr.split(" ")

    have_busin = False
    have_busout = False
    have_alu = False
    have_jmp = False

    # append bits that form alu controls
    alu_bits = []
    for b in bits:
        if b in ALU:
            have_alu = True
            alu_bits.append("EO")
            if ALU[b]:
                alu_bits.extend(ALU[b].split(" "))

    bits = bits + alu_bits

    num = 0
    for b in bits:
        if b in ALU:
            continue  # skip these bits, we already appended them
        if b not in UCODE:
            die(lineno, f"unrecognised ucode: {b}")
        num |= UCODE[b]

        if b in IS_BUSIN:
            if have_busin:
                die(lineno, f"multiple busin bits: {uinstr}")
            have_busin = True
        if b in IS_BUSOUT:
            if have_busout:
                die(lineno, f"multiple busout bits: {uinstr}")
            if have_alu:
                die(lineno, f"busout conflicting with ALU: {uinstr}")
            have_busout = True
        if b in IS_ALU:
            if have_busout:
                die(lineno, f"ALU conflicting with busout: {uinstr}")
            have_alu = True
        if b in IS_JMP:
            have_jmp = True

    if have_alu and not re.search(r"\bEO\b", uinstr) and not alu_bits:
        die(lineno, f"ALU bits without EO: {uinstr}")

    if have_alu and re.search(r"\bP\+", uinstr):
        die(lineno, f"P+ with ALU not allowed: {uinstr}")

    if have_busout and not have_busin and not have_jmp and mnemonic != "slownop":
        print(
            f"line {lineno}: busout with no busin probably makes no sense: {uinstr}",
            file=sys.stderr,
        )
    if have_busin and not have_busout and not have_alu:
        print(
            f"line {lineno}: busin with no busout probably makes no sense (will get PC on bus, please specify 'PO'): {uinstr}",
            file=sys.stderr,
        )

    # the "EO" bit is active-low, so needs toggling:
    num ^= UCODE["EO"]

    return num


def emit_ucode(for_mnemonic, ucode, lineno):
    ucode = list(ucode)

    # confusing: always fetch the next instruction and increment PC, regardless of whatever
    # the last instruction was -- except for "irq", a hardware-only entry point that the
    # interrupt logic jumps to directly (forcing the instruction register's value itself),
    # so it must not perform its own fetch: doing so would fetch and execute whatever
    # instruction happened to come next, instead of running the interrupt handler.
    if not (for_mnemonic is not None and for_mnemonic == "irq"):
        ucode = [
            encode("PO AI", for_mnemonic, lineno),
            encode("MO8L II P+1", for_mnemonic, lineno),
        ] + ucode

    # pad the rest of the ucode with "reset t-state" microcode
    while len(ucode) < T_STATES:
        ucode.append(encode("RT", for_mnemonic, lineno))

    if len(ucode) > T_STATES:
        die(lineno, f"too many microinstructions: {for_mnemonic}")

    for u in ucode:
        print(f"{u:04x}")


def main():
    opcode = -1
    mnemonic = None
    block_mnemonic = None  # mnemonic that the accumulated ucode belongs to
    ucode = []

    lineno = 0

    print("v3.0 hex")  # header for Logisim hex format

    for line in fileinput.input():
        lineno = fileinput.lineno()

        line = normalize_line(line)

        if line == "":
            continue

        m = INSTR_RE.match(line)
        if m:  # new instruction starts
            mnemonic = m.group(1)
            opcode_hex = m.group(2)
            opcode += 1
            if opcode > MAX_OPCODE:
                die(lineno, f"too many opcodes: >{MAX_OPCODE}")

            # TODO: accept non-contiguous opcode (i.e. gaps)
            if opcode_hex != "" and opcode != int(opcode_hex, 16):
                die(
                    lineno,
                    f"wrong opcode for {mnemonic}: expected 0x{opcode_hex}, found {opcode}",
                )

            if ucode and opcode == 0:
                die(lineno, "initial instructions are unlabelled")
            if opcode != 0:
                emit_ucode(block_mnemonic, ucode, lineno)
            block_mnemonic = mnemonic
            ucode = []
        else:
            uinstr = encode(line, mnemonic, lineno)
            ucode.append(uinstr)

    if opcode == -1:
        raise AsmError("opcode == -1 (maybe label your instructions?)")

    emit_ucode(block_mnemonic, ucode, lineno)

    # empty ucode is a no-op
    ucode = []

    # pad the rest of the microcode space with "long nops", this is needed so that
    # illegal instructions have the "fetch" ucode in them
    for _ in range(opcode + 1, MAX_OPCODE + 1):
        emit_ucode(None, ucode, lineno)


if __name__ == "__main__":
    try:
        main()
    except AsmError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
