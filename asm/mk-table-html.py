#!/usr/bin/env python3


import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ucode")
)
from uasm import ALU  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

CLOBSYM = {"x": "!", "y": "^", "flags": "+"}

# every ALU expression name -- if a microcode line uses one, that instruction
# sets flags as a side effect. Sourced directly from uasm.py's own ALU dict
# instead of a hand-maintained copy, so it can't drift out of sync.
USES_ALU = set(ALU.keys())


def load_instructions():
    path = os.path.join(SCRIPT_DIR, "instructions.json")
    with open(path) as fh:
        return json.load(fh)


# how many bytes (beyond the opcode byte) this instruction's own encoding
# takes: each "(i8h)"/i8l/i8h param is 1 byte, i16l/i16h are 2, i32 is 4,
# plus 1 more for an implicit register and/or an implicit byte, if present.
def instruction_bytes(mnemonic, inst):
    parts = mnemonic.split(" ", 1)
    params_str = parts[1] if len(parts) > 1 else ""
    params = re.split(r"\s*,\s*", params_str) if params_str else []

    n = 0
    for p in params:
        if re.search(r"i8", p):
            n += 1
        elif re.search(r"i32", p):
            n += 4
        elif re.search(r"i16", p):
            n += 2
    if inst.get("implicit_reg") is not None:
        n += 1
    if inst.get("implicit_byte") is not None:
        n += 1
    return 1 + n


def derived_clobbers(inst):
    clobbers = set(inst.get("clobbers", []))
    clobbers_flags = False
    for uinstr in inst.get("ucode", []):
        tokens = uinstr.split(" ")
        if "XI" in tokens:
            clobbers.add("x")
        if "YI" in tokens:
            clobbers.add("y")
        if any(t in USES_ALU for t in tokens):
            clobbers_flags = True
    if clobbers_flags:
        clobbers.add("flags")
    return clobbers, clobbers_flags


def render_microcode(inst):
    lines = []
    for uinstr in inst.get("ucode", []):
        uops = []
        for uop in uinstr.split(" "):
            if uop in USES_ALU:
                uop = f'<span class="clobflags">{uop}</span>'
            uops.append(uop)
        lines.append(" ".join(uops))
    escaped = [line.replace("&", "&amp;") for line in lines]
    return "<br>".join(f"&nbsp;&nbsp;{line}" for line in escaped)


def render_cell(opcode, mnemonic, inst):
    if mnemonic is None:
        return '<td class="inst"></td>\n'

    display = mnemonic.replace("(i8h)", "r")

    clobbers, _ = derived_clobbers(inst)
    # x/y showing up as the instruction's own operand isn't a surprising
    # side effect -- it's the point of the instruction -- so don't flag it.
    if re.match(r"^\S+ x\b", display) or "x++" in display:
        clobbers.discard("x")
    if re.match(r"^\S+ y\b", display) or "y++" in display:
        clobbers.discard("y")

    clobber_warnings = "".join(
        f'<span class="clob{c}">{CLOBSYM.get(c, "*")}</span>' for c in sorted(clobbers)
    )
    clobbers_display = (
        ", ".join(f'<span class="clob{c}">{c}</span>' for c in sorted(clobbers))
        if clobbers
        else "(none)"
    )

    microcode = render_microcode(inst)
    remark = inst.get("remark", "")

    instop, _, instargs = display.partition(" ")
    instopcss = instop
    if instop.startswith("j"):
        instopcss = "j"
    if instop == "sb":
        instopcss = "tbsz"

    nbytes = instruction_bytes(mnemonic, inst)
    cycles = inst.get("cycles", "")

    return (
        f'<td class="inst inst-{instopcss}">'
        f'<div style="padding:2px"><span style="font-weight:bold">{instop}</span> '
        f"{instargs} {clobber_warnings}</div>"
        f'<div class="popup"><b>Opcode:</b> {opcode:02x}<br>'
        f"<b>Bytes:</b> {nbytes}<br>"
        f"<b>Cycles:</b> {cycles}<br>"
        f"<b>Clobbers:</b> {clobbers_display}<b><br>Microcode:</b><br>{microcode}<br>"
        f'<span class="remark">{remark}</span></div></td>\n'
    )


def render_table(instructions):
    op2inst = {inst["opcode"]: mnemonic for mnemonic, inst in instructions.items()}

    hexdigits = "0123456789abcdef"
    out = ["<table>\n", "<tr><td></td>"]
    for b in hexdigits:
        out.append(f"<th>_{b}</th>")
    out.append("</tr>\n")

    for a in hexdigits:
        out.append(f"<tr><th>{a}_</th>")
        for b in hexdigits:
            opcode = int(a + b, 16)
            mnemonic = op2inst.get(opcode)
            inst = instructions.get(mnemonic) if mnemonic is not None else None
            out.append(render_cell(opcode, mnemonic, inst))
        out.append("</tr>\n")
    out.append("</table>\n")
    return "".join(out)


HEADER = """<html>
<head>
<title>SCAMP-32 Instruction Set Cheatsheet</title>
<style type="text/css">
body {
    font-family: sans-serif;
}
table {
    margin-right: 150px;
    font-size: 1.0em;
    font-family: monospace;
}
td {
    background-color: #ccc;
    color: black;
    padding: 2px;
    vertical-align: top;
}
td.inst-add { background-color: #dcc; }
td.inst-cmp { background-color: #dbb; }
td.inst-inc { background-color: #cbb; }
td.inst-sub { background-color: #cdc; }
td.inst-dec { background-color: #bcb; }
td.inst-and { background-color: #ccd; }
td.inst-not { background-color: #dcb; }
td.inst-test { background-color: #bdd; }
td.inst-neg { background-color: #dbd; }
td.inst-or { background-color: #ddc; }
td.inst-nand { background-color: #cdd; }
td.inst-nor { background-color: #dcd; }
td.inst-xor { background-color: #bcd; }
td.inst-in { background-color: #cbc; }
td.inst-out { background-color: #bdc; }
td.inst-ld { background-color: #bcc; }
td.inst-push, td.inst-pop { background-color: #bbc; }
td.inst-j { background-color: #ccb; }
td.inst-shl, td.inst-shl2, td.inst-shl3 { background-color: #cbd; }
td.inst-tbsz { background-color: #cdb; }
td.inst-call, td.inst-ret { background-color: #dbc; }

td.inst:hover {
    background-color: #eee;
}
td.inst:hover div.popup {
    display: block;
}
td.inst div.popup {
    display:none;
}
div.popup {
    pointer-events: none;
    position: absolute;
    background: #eee;
    width: 200px;
    padding: 2px;
}
th {
    background-color: #333;
    color: white;
    padding: 2px;
}
.clobflags {
    color: #080;
}
.clobx {
    color: #f00;
    font-weight: bold;
}
.cloby {
    color: #888;
}
.remark {
    font-family: sans-serif;
    font-size: 0.8em;
}
tt {
    font-weight: bold;
    font-size: 1.2em;
}
</style>
</head>
<body>
<h1>SCAMP-32 Instruction Set Cheatsheet</h1>
<ul>
<li>The bus and registers are 32 bits wide. <tt>i8l</tt>/<tt>i16l</tt> parameters are zero-extended
onto the bus; <tt>i8h</tt>/<tt>i16h</tt> are extended with the upper bits set to 1 instead
(e.g. so a pseudo-register's address, top of memory, fits in a single byte operand).</li>
<li>Typically the first parameter is the destination and first operand, and the second parameter is the other operand.</li>
<li>Side effects on <tt>flags</tt>, <tt>x</tt>, or <tt>y</tt> are documented as "clobbers", derived
automatically from whether an instruction's own microcode writes <tt>x</tt>/<tt>y</tt> or uses the ALU.
A clobber of some other register (e.g. a scratch register touched via a computed address) is called out
explicitly with a <tt># clobbers: rN</tt> comment in <tt>ucode.s</tt> instead, since that can't be
derived from a token scan.</li>
<li><tt>++</tt> refers to post-increment of a pointer stored in a register.</li>
</ul>
"""

FOOTER = """<ul>
<li>The <tt>x</tt> register functions as an accumulator.</li>
<li>The <tt>y</tt> register is only exposed for a few instructions (like <tt>xor x, y</tt>)
where routing the operation through a pseudo-register would cost too many cycles.</li>
<li><tt>r</tt> parameters are "pseudo-registers": <tt>r0</tt>..<tt>r63</tt>, each 32 bits wide,
living at the top of memory (<tt>r0</tt> is <tt>0xffffff00</tt>, <tt>r1</tt> is <tt>0xffffff04</tt>,
and so on, 4 bytes apart), addressed with a single <tt>(i8h)</tt> byte operand.</li>
<li><tt>sp</tt> is its own physical register (not a pseudo-register), with dedicated
<tt>SI</tt>/<tt>SO</tt> bus codes.</li>
<li>No pseudo-register has a fixed architectural role; by convention <tt>r62</tt> is used as
scratch space where an instruction needs one (e.g. <tt>xor</tt>), documented per-instruction
with a <tt># implicit: rN</tt>/<tt># clobbers: rN</tt> comment in <tt>ucode.s</tt> rather than
hardcoded here.</li>
<li>The flags are set whenever the ALU is used (see the <tt>+</tt> marker). <tt>JZ</tt> jumps if
the ALU output was 0; <tt>JGT</tt>/<tt>JLT</tt> jump if it was greater/less than 0.</li>
</ul></body>
</html>
"""


def main():
    instructions = load_instructions()
    sys.stdout.write(HEADER)
    sys.stdout.write(render_table(instructions))
    sys.stdout.write(
        f'<div class="clobflags"><tt>{CLOBSYM["flags"]}</tt> sets <tt>flags</tt></div>\n'
    )
    sys.stdout.write(
        f'<div class="clobx"><tt>{CLOBSYM["x"]}</tt> clobbers <tt>x</tt></div>\n'
    )
    sys.stdout.write(
        f'<div class="cloby"><tt>{CLOBSYM["y"]}</tt> clobbers <tt>y</tt></div>\n'
    )
    sys.stdout.write(FOOTER)


if __name__ == "__main__":
    main()
