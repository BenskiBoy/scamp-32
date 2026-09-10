#!/usr/bin/env python3

# Generate parser for SCAMP assembler, based on instructions from instructions.json
#
# Most of the instruction text needs to exactly match, with "Char" or "String"
# "i8l" and "i8h" have to be constants in 0x0000..0x00ff and 0xff00..0xffff
# "i16" can be any constant, or a label
#
# TODO: [mem] instead of writing SLANG code with [] arrays, write asm code instead so that
#       we don't waste a load of memory on initialising the arrays
# TODO: [bug] the problem with this is that it references "IndirectionEquals" etc. by name
#       before such a time that those functions are initialised; we need to come up with a
#       way either for asm.sl to initialise them before including asmparser.sl, or else
#       to not use them until after they're initialised

import json
import os
import re
import sys
import time


class GenError(Exception):
    pass


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

TOKEN_RE = re.compile(r"i8l|i8h|i16|\(i8h\)|\(i16\)|\(\d+\)|.")
SPECIAL_RE = re.compile(r"i8l|i8h|i16|\(i8h\)|\(i16\)|\(\d+\)")


def load_instructions():
    path = os.path.join(SCRIPT_DIR, "instructions.json")
    try:
        with open(path) as fh:
            return json.load(fh)
    except OSError as e:
        raise GenError(f"can't read {path}: {e.strerror}")


def safemnem(mnem):
    # make a copy of $mnem safe for use in identifiers
    return mnem.replace("+", "plus").replace("-", "minus")


class ParserGenerator:
    def __init__(self, instructions):
        self.instructions = instructions

        self.mnemonic = {}
        self.argparser = {}
        self.argparsernum = 0

        self.interned = {}
        self.internlabel = 0

        for instr in sorted(instructions):
            opcode = instructions[instr]["opcode"]
            cycles = instructions[instr]["cycles"]

            parts = instr.split(" ", 1)
            mnem = parts[0]
            args = parts[1] if len(parts) > 1 else ""
            self.mnemonic.setdefault(mnem, []).append((args, opcode, cycles))

    def generate(self):
        out = []

        out.append(self.parser_header())

        for mnem in sorted(self.mnemonic):
            out.append(self.mkparser(mnem, self.mnemonic[mnem]))

        out.append(self.parser_footer())

        return "\n".join(out) + "\n"

    def _char_or_string_part(self, s):
        if len(s) == 1:
            return "    .word myChar\n    .word %s\n" % ("0x%02x" % ord(s))
        return f"    .word myString\n    .word {self.intern(s)}\n"

    def mkargparser(self, args):
        if self.argparser.get(args):
            return ""

        name = f"Instr_{args}_{self.argparsernum}"
        self.argparsernum += 1
        name = name.replace("+", "p")
        name = name.replace("-", "m")
        name = re.sub(r"[^a-zA-Z0-9]", "_", name)
        name = re.sub(r"_+", "_", name)

        self.argparser[args] = name

        src = f"# {args}\n"
        src += f"var {name} = asm {{\n"

        i16 = False
        i8 = False

        s = ""
        parts = []

        for m in TOKEN_RE.finditer(args):
            bit = m.group(0)
            if SPECIAL_RE.search(bit):
                if s:
                    parts.append(self._char_or_string_part(s))
                    s = ""

                if bit == "i8l":
                    i8 = True
                    parts.append("    .word myI8l\n    .word 0\n")
                elif bit == "i8h":
                    i8 = True
                    parts.append("    .word myI8h\n    .word 0\n")
                elif bit == "i16":
                    i16 = True
                    parts.append("    .word myI16\n    .word 0\n")
                elif bit == "(i8h)":
                    i8 = True
                    parts.append("    .word myIndirection\n    .word 8\n")
                elif bit == "(i16)":
                    i16 = True
                    parts.append("    .word myIndirection\n    .word 16\n")
                elif re.match(r"^\(\d+\)$", bit):
                    # indirection on a constant - abuse Indirection(16)
                    val = re.search(r"(\d+)", bit).group(1)
                    parts.append(f"    .word myIndirectionEquals\n    .word {val}\n")
                else:
                    raise GenError(f"unrecognised bit: {bit}")
            else:
                s += bit

        if s:
            parts.append(self._char_or_string_part(s))

        emit_val = 0
        if i8:
            emit_val |= 1
        if i16:
            emit_val |= 2
        src += f"    .word {emit_val}\n"

        src += "".join(parts)

        src += "    .word 0\n"
        src += "};\n"

        return src

    def get_argparser(self, args):
        name = self.argparser.get(args)
        if not name:
            raise GenError(f"no parser for: {args}")
        return name

    def mkparser(self, mnem, instrs):
        # for ambiguous instructions, try the fastest ones first
        instrs = sorted(instrs, key=lambda mode: mode[2])

        src = ""
        for instr, opcode, cycles in instrs:
            src += self.mkargparser(instr)

        src += f"var Instr_{safemnem(mnem)} = [\n"
        src += f'    "{mnem}",\n'
        for instr, opcode, cycles in instrs:
            src += "    " + self.get_argparser(instr) + "," + ("0x%04x" % (opcode << 8)) + ",\n"
        src += "];\n"

        return src

    def parser_header(self):
        src = ""

        src += f"# generated by mk-asm-parser {time.asctime(time.gmtime())}\n"
        src += "\n"
        src += 'include "parse.sl";\n'
        src += "\n"

        src += "var I8l;\n"
        src += "var I8h;\n"
        src += "var I16;\n"
        src += "var Indirection;\n"
        src += "var IndirectionEquals;\n"
        src += "var Instr_args;\n"
        src += "var Instr_anyargs;\n"
        src += "var emit;\n"
        src += "var emit_i16;\n"
        src += "var asm_i8;\n"
        src += "var asm_i16;\n"
        src += "var i16_identifier;\n"
        src += "var opcode;\n"

        # TODO: [perf] find a way to avoid the indirect function call
        src += "asm {\n"
        for func in ("Char", "String", "I8l", "I8h", "I16", "Indirection", "IndirectionEquals"):
            src += f"my{func}: jmp (_{func})\n"
        src += "};\n"

        return src

    def parser_footer(self):
        src = ""

        src += "var Instr = func(x) {\n"
        src += "    skip();\n"
        src += "    var ch = peekchar();\n"

        group = ""
        for mnem in sorted(self.mnemonic):
            ch = mnem[0]
            if ch != group:
                if group:
                    src += "    } else\n"
                src += f"    if (ch == '{ch}') {{\n"
                group = ch

            src += f"        if (parse(Instr_anyargs,Instr_{safemnem(mnem)})) return 1;\n"

        if group:
            src += "    };\n"

        src += "    return 0;\n"
        src += "};\n\n"

        src += "asm {\n"
        for s in sorted(self.interned, key=lambda s: self.interned[s]):
            src += f'{self.interned[s]}: .str "{s}\\0"\n'
        src += "};\n"

        return src

    def intern(self, s):
        if s not in self.interned:
            self.interned[s] = f"str{self.internlabel}"
            self.internlabel += 1
        return self.interned[s]


def main():
    instructions = load_instructions()
    gen = ParserGenerator(instructions)
    print(gen.generate(), end="")


if __name__ == "__main__":
    try:
        main()
    except GenError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
