#!/usr/bin/env python3

# Assembler

import argparse
import fileinput
import json
import os
import re
import struct
import sys


class AsmError(Exception):
    pass


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

HELP_TEXT = """This is the SCAMP assembler.

Usage: asm [-v] < source.s > binary.hex

Options:

    -h,--help            Show this help.
    -v,--verbose         Annotate the generated hex with the source.
    --verbose-file FILE  Write annotated hex (like with -v) into FILE.
"""


def print_help(rc):
    print(HELP_TEXT, end="")
    sys.exit(rc)


def load_instructions():
    path = os.path.join(SCRIPT_DIR, "instructions.json")
    try:
        with open(path) as fh:
            return json.load(fh)
    except OSError as e:
        raise AsmError(f"can't read {path}: {e.strerror}")


class Assembler:
    def __init__(self, instructions):
        self.instructions = instructions

        self.instrs_by_op = {}
        for inst in instructions:
            op = inst.split(" ", 1)[0]
            self.instrs_by_op.setdefault(op, []).append(inst)

        self.macro = {}
        self.macros = []
        self.label = {}
        self.pc = 0
        self.code = []
        self.lineno = 0

        self.addmacro("sp", "(0xffff)")

        # add macros for ".def r0 (0xff00)" for 0..255
        # TODO: maybe add a flag to turn off the the default macros?
        for i in range(256):
            self.macro[f"r{i}"] = True
        self.macros.append(
            lambda s: re.sub(r"\br(\d+)\b", lambda m: "(0xff%02x)" % int(m.group(1)), s)
        )

    def die(self, msg):
        raise AsmError(f"error: line {self.lineno}: {msg}")

    def addmacro(self, frm, to):
        if self.macro.get(frm):
            raise AsmError(f"duplicate macro: {frm}")
        self.macro[frm] = True

        pattern = re.compile(r"\b" + re.escape(frm) + r"\b")
        self.macros.append(lambda s: pattern.sub(lambda m: to, s))

    def emit(self, word):
        self.code.append(word)
        if not str(word).startswith("__asm"):
            self.pc += 1

    # examples:
    # x => die
    # (x) => die
    # (65535)++ => 65535
    # 605 => 605
    # (val) => val
    # 1((65535)) => 1
    # 1(x) => 1
    def arg2num(self, arg):
        if re.match(r"^(x|y|pc)$", arg):
            self.die(f"can't convert register to number: {arg}")

        m = re.search(r"(\d+)\(x\)", arg)
        if m:
            return int(m.group(1))
        m = re.search(r"(\d+)\(\(65535\)\)", arg)
        if m:
            return int(m.group(1))
        m = re.search(r"(\d+)\+\(65535\)", arg)
        if m:
            return int(m.group(1))

        # remove (, ), +, -
        arg = re.sub(r"[()+-]", "", arg)
        if re.match(r"^-?\d+$", arg):
            return int(arg)
        return arg

    # examples:
    # x => x
    # (x) => \(x\)
    # (65535)++ => \((i8h|i16)\)\+\+
    # 605 => i16
    def arg2pattern(self, arg):
        # escape \, (, ), +
        arg = re.sub(r"([\\()+])", r"\\\1", arg)

        def subst(m):
            v = m.group(1)
            if re.match(r"^(x|y|pc)$", v):
                return v
            if re.match(r"^\d+$", v):
                n = int(v)
                if 0xFF00 <= n <= 0xFFFF:
                    return f"(i8h|i16|{v})"
                if 0x0000 <= n <= 0x00FF:
                    return f"(i8l|i16|{v})"
            return f"(i16|{v})"

        arg = re.sub(r"\b([a-z_0-9]+)\b", subst, arg, flags=re.IGNORECASE)
        return arg

    def namearg(self, arg):
        if not re.match(r"^[a-z_][a-z_0-9]*$", arg, re.IGNORECASE):
            self.die(f"invalid name: {arg}")
        if re.match(r"^(x|y)$", arg, re.IGNORECASE):
            self.die(f"'{arg}' is a reserved name")
        return arg

    def numarg(self, arg):
        val = arg
        neg = val.startswith("-")
        if neg:
            val = val[1:]
        m = re.match(r"^0x([0-9a-f]+)$", val, re.IGNORECASE)
        if m:
            val = str(int(m.group(1), 16))
        if not re.match(r"^[0-9]+$", val):
            self.die(f"invalid number: {arg}")
        n = int(val)
        return -n if neg else n

    def params(self, op, n, args):
        if len(args) != n:
            self.die(f"{op}: expected {n} arguments, found {len(args)}")

    def process_line(self, line):
        orig_line = line

        # strip comments, whitespace
        if not re.match(r"^\s*\.str", line):
            line = re.sub(r"#.*", "", line)
        line = re.sub(r"^\s+", "", line)
        line = re.sub(r"\s+$", "", line)

        # apply macro substitutions
        for m in self.macros:
            line = m(line)

        # resolve hex
        line = re.sub(
            r"\b0x([0-9a-f]+)\b",
            lambda m: str(int(m.group(1), 16)),
            line,
            flags=re.IGNORECASE,
        )

        # store labels
        while True:
            m = re.match(r"^([a-z_][a-z_0-9]*):\s*", line, re.IGNORECASE)
            if not m:
                break
            name = self.namearg(m.group(1))
            if name in self.label:
                self.die(f"duplicate label name: {name}")
            self.label[name] = self.pc
            line = line[m.end() :]

        if line == "":
            self.emit(f"__asm_annotation {orig_line}")
            return

        self.emit(f"__asm_addr_{self.pc}")

        parts = line.split(None, 1)
        op = parts[0]
        args_str = parts[1] if len(parts) > 1 else ""
        args = re.split(r"\s*,\s*", args_str) if args_str else []

        if op in (".d", ".def"):
            args = re.split(r"\s+", args_str) if args_str else []
            self.params(op, 2, args)
            name = self.namearg(args[0])
            if self.macro.get(name):
                self.die(f"duplicate macro name: {name}")
            # note: `op` is used unescaped here (a literal "." matches as a
            # regex wildcard), matching the original Perl assembler exactly
            line = re.sub(r"\s*" + op + r"\s*" + re.escape(name) + r"\s*", "", line)
            self.addmacro(name, line)
        elif op == ".at":
            self.params(op, 1, args)
            at = self.numarg(args[0])
            if self.pc != 0:
                if at < self.pc:
                    self.die(f".at {at} but we're already at {self.pc}")
                for _ in range(self.pc + 1, at + 1):
                    self.emit(0x0000)
            self.pc = at
        elif op in (".g", ".gap"):
            self.params(op, 1, args)
            for _ in range(self.numarg(args[0])):
                self.emit(0x0000)
        elif op in (".w", ".word"):
            self.params(op, 1, args)
            if re.match(r"^[a-z_][a-z_0-9]*$", args[0], re.IGNORECASE):
                self.emit(args[0])
            else:
                self.emit(self.numarg(args[0]))
        elif op == ".str":
            s = line
            # note: `.str` is used unescaped here too, same as `.d`/`.def` above
            s = re.sub(r'^\s*.str\s*"', "", s)
            s = re.sub(r'"\s*(#.*)?$', "", s)
            s = s.replace("\\r", "\r")
            s = s.replace("\\n", "\n")
            s = s.replace("\\t", "\t")
            s = s.replace("\\[", "[")
            s = re.sub(r"\\x(..)", lambda m: str(int(m.group(1), 16)), s)
            s = s.replace("\\0", "\0")
            s = s.replace("\\\\", "\\")
            for ch in s:
                self.emit(ord(ch))
        else:
            # turn the arguments into a pattern
            argpattern = [self.arg2pattern(a) for a in args]
            re_str = re.escape(op)
            if argpattern:
                re_str += " " + ", ".join(argpattern)
            regex = re.compile("^" + re_str + "$")

            # find instructions that match the pattern
            match = [i for i in self.instrs_by_op.get(op, []) if regex.match(i)]
            if not match:
                self.die(f"unrecognised operation: {line}")

            # sort the matches by cycle count, so we choose the fastest match;
            # we can get multiple matches in cases like "ld r0, r1" where
            # both "ld (i16), (i8h)" and "ld (i8h), (i16)" match
            # (we sort twice so that the ordering is always the same)
            match = sorted(match)
            match = sorted(match, key=lambda m: self.instructions[m]["cycles"])

            # generate code:
            #  - upper 8 bits of instruction come from opcode
            #  - lower 8 bits of instruction are i8l/i8h, if any,
            #    otherwise ignored (so 0)
            #  - the i16 argument comes next, if any
            #  - if we don't yet know the address for a label, just
            #    store the text and it'll get filled in later
            opcode = self.instructions[match[0]]["opcode"] << 8
            operands = []

            instr_parts = match[0].split(" ", 1)
            params_str = instr_parts[1] if len(instr_parts) > 1 else ""
            params = re.split(r"\s*,\s*", params_str) if params_str else []

            for i in range(len(argpattern)):
                if re.search(r"i8", params[i]):
                    opcode |= self.arg2num(args[i]) & 0xFF
                elif re.search(r"i16", params[i]):
                    operands.append(self.arg2num(args[i]))

            self.emit(opcode)
            for o in operands:
                self.emit(o)

        self.emit(f"__asm_annotation {orig_line}")

    def write_output(self, fh, verbose):
        chars_on_line = 0

        if not verbose:
            fh.write("v3.0 hex\n")  # header for Logisim hex format

        # now turn the code into hex output
        for c in self.code:
            if isinstance(c, str):
                m = re.match(r"__asm_addr_(\d+)", c)
                if m:
                    if verbose:
                        fh.write("%04x:  " % int(m.group(1)))
                        chars_on_line += 7
                    continue

                if c.startswith("__asm_annotation "):
                    c = c[len("__asm_annotation ") :]
                    if verbose:
                        fh.write(" " * max(0, 18 - chars_on_line))
                        fh.write(f"# {c}\n")
                        chars_on_line = 0
                    continue

            if not re.match(r"^-?\d+$", str(c)):
                if c not in self.label:
                    raise AsmError(f"error: label {c} not found")
                c = self.label[c]

            c = int(c)
            if c < 0:
                c += 65536
            if c < 0 or c > 0xFFFF:
                raise AsmError(f"error: {c} out of range")
            fh.write("%04x%s" % (c, " " if verbose else "\n"))
            chars_on_line += 5


def build_parser():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--verbose-file")
    parser.add_argument("--externs-list")
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("files", nargs="*")

    def error(message):
        print_help(1)

    parser.error = error
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.help:
        print_help(0)

    instructions = load_instructions()
    asm = Assembler(instructions)

    for line in fileinput.input(args.files):
        asm.lineno = fileinput.lineno()
        asm.process_line(line.rstrip("\n"))

    asm.write_output(sys.stdout, args.verbose)

    if args.verbose_file:
        with open(args.verbose_file, "w") as fh:
            asm.write_output(fh, True)

    # create the externs list, if any
    if args.externs_list:
        with open(args.externs_list, "wb") as fh:
            for name in sorted(asm.label):
                if name.startswith("_"):
                    slang_name = name[1:]
                    fh.write(struct.pack(">h", asm.label[name]))
                    for c in slang_name:
                        fh.write(b"\0" + c.encode("ascii"))
                    fh.write(b"\0\n")


if __name__ == "__main__":
    try:
        main()
    except AsmError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
