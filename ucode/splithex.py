#!/usr/bin/env python3

# Split a 16-bit-word Logisim .hex file (one 4-digit hex word per line, with
# a "v3.0 hex" header) into per-chip .hex files (one 2-digit hex byte per
# line each), for loading onto a memory built from parallel 8-bit-wide chips.
#
# With the default of 2 chips, each 16-bit word is split into its high and
# low byte, written to "<base>-high.hex" and "<base>-low.hex".
#
# With N chips (N even, N>2), every N/2 consecutive 16-bit words are packed
# side by side into one N-byte-wide row -- word[0]'s high byte, word[0]'s low
# byte, word[1]'s high byte, word[1]'s low byte, and so on -- written to
# "<base>-0.hex" .. "<base>-{N-1}.hex". This lets a wider physical memory
# (more parallel 8-bit chips) hold more of the original 16-bit words per
# address, without changing the 16-bit instruction encoding itself. A final
# short row is padded with zero words.

import sys

HEADER = "v3.0 hex"


def main():
    if len(sys.argv) not in (2, 3):
        print(f"usage: {sys.argv[0]} <file.hex> [nchips]", file=sys.stderr)
        sys.exit(1)

    in_path = sys.argv[1]
    nchips = int(sys.argv[2]) if len(sys.argv) == 3 else 2

    if nchips < 2 or nchips % 2 != 0:
        print("nchips must be an even number >= 2", file=sys.stderr)
        sys.exit(1)

    if not in_path.endswith(".hex"):
        print("input file must end in .hex", file=sys.stderr)
        sys.exit(1)

    base = in_path[: -len(".hex")]
    names = ["high", "low"] if nchips == 2 else [str(i) for i in range(nchips)]
    words_per_row = nchips // 2

    out_files = [open(f"{base}-{name}.hex", "w") for name in names]

    try:
        for f in out_files:
            print(HEADER, file=f)

        with open(in_path) as in_file:
            header_line = in_file.readline()
            if header_line.strip() != HEADER:
                print(f"{in_path}:1: expected {HEADER!r} header, found {header_line.strip()!r}",
                      file=sys.stderr)
                sys.exit(1)

            row = []

            def flush_row():
                padded = row + [0] * (words_per_row - len(row))
                for w, value in enumerate(padded):
                    print(f"{value >> 8:02x}", file=out_files[w * 2])
                    print(f"{value & 0xff:02x}", file=out_files[w * 2 + 1])
                row.clear()

            for lineno, line in enumerate(in_file, 2):
                word = line.strip()
                if not word:
                    continue
                if len(word) != 4:
                    print(f"{in_path}:{lineno}: expected 4 hex digits, found {word!r}",
                          file=sys.stderr)
                    sys.exit(1)
                row.append(int(word, 16))
                if len(row) == words_per_row:
                    flush_row()

            if row:
                flush_row()
    finally:
        for f in out_files:
            f.close()


if __name__ == "__main__":
    main()
