#!/usr/bin/env python3

# Split a Logisim .hex file (one word per line, with a "v3.0 hex" header)
# into per-chip .hex files (one 2-digit hex byte per line each), for loading
# onto a memory built from parallel 8-bit-wide chips.
#
# The input word width (in bytes) is detected from the hex digit count of
# the first data line. With nchips equal to that width, each word is split
# into its constituent bytes, most-significant first -- written to
# "<base>-high.hex"/"<base>-low.hex" for a 2-byte word, or "<base>-0.hex" ..
# "<base>-{nchips-1}.hex" otherwise.
#
# With nchips a multiple of the word width, every (nchips / word width)
# consecutive words are packed side by side into one nchips-byte-wide row --
# word[0]'s bytes, then word[1]'s bytes, and so on -- written to
# "<base>-0.hex" .. "<base>-{nchips-1}.hex". This lets a wider physical
# memory (more parallel 8-bit chips) hold more of the original words per
# address, without changing the word encoding itself. A final short row is
# padded with zero words.

import sys

HEADER = "v3.0 hex"


def main():
    if len(sys.argv) not in (2, 3):
        print(f"usage: {sys.argv[0]} <file.hex> [nchips]", file=sys.stderr)
        sys.exit(1)

    in_path = sys.argv[1]
    requested_chips = int(sys.argv[2]) if len(sys.argv) == 3 else None

    if not in_path.endswith(".hex"):
        print("input file must end in .hex", file=sys.stderr)
        sys.exit(1)

    base = in_path[: -len(".hex")]

    with open(in_path) as in_file:
        header_line = in_file.readline()
        if header_line.strip() != HEADER:
            print(f"{in_path}:1: expected {HEADER!r} header, found {header_line.strip()!r}",
                  file=sys.stderr)
            sys.exit(1)

        out_files = None
        nbytes = None
        nchips = requested_chips
        words_per_row = None
        row = []

        def flush_row():
            padded = row + [0] * (words_per_row - len(row))
            for w, value in enumerate(padded):
                for b in range(nbytes):
                    shift = (nbytes - 1 - b) * 8
                    print(f"{(value >> shift) & 0xff:02x}", file=out_files[w * nbytes + b])
            row.clear()

        for lineno, line in enumerate(in_file, 2):
            word = line.strip()
            if not word:
                continue

            if out_files is None:
                digits = len(word)
                if digits == 0 or digits % 2 != 0:
                    print(f"{in_path}:{lineno}: expected an even number of hex digits, found {word!r}",
                          file=sys.stderr)
                    sys.exit(1)
                nbytes = digits // 2
                if nchips is None:
                    nchips = nbytes
                if nchips % nbytes != 0:
                    print(f"nchips ({nchips}) must be a multiple of the word width in bytes ({nbytes})",
                          file=sys.stderr)
                    sys.exit(1)
                words_per_row = nchips // nbytes
                names = ["high", "low"] if nchips == 2 and nbytes == 2 else [str(i) for i in range(nchips)]
                out_files = [open(f"{base}-{name}.hex", "w") for name in names]
                for f in out_files:
                    print(HEADER, file=f)
            elif len(word) != nbytes * 2:
                print(f"{in_path}:{lineno}: expected {nbytes * 2} hex digits, found {word!r}",
                      file=sys.stderr)
                sys.exit(1)

            row.append(int(word, 16))
            if len(row) == words_per_row:
                flush_row()

        if out_files is None:
            print(f"{in_path}: no words found", file=sys.stderr)
            sys.exit(1)

        if row:
            flush_row()

        for f in out_files:
            f.close()


if __name__ == "__main__":
    main()
