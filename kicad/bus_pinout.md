# SCAMP-32 backplane bus pinout

Target connector: DIN 41612 Type C, 3 rows × 32 positions (96-way), rows `a`/`b`/`c`, matching the connector in `scamp32-template`.

Supersedes the earlier raw-control-word draft. Per `bus_pinout_fix.md`: individual control signals are decoded centrally on the `scamp32-ucode` board (which also hosts `IR`) and broadcast as their own dedicated lines, rather than sending the raw 16-bit microcode word for every board to decode locally. Signals that are entirely consumed within `scamp32-ucode` (including `IR`, which lives on that board) never leave it, so they don't need a backplane pin at all — that's what trims the control-signal list down to exactly 32, filling row `c` precisely.

## Row `a` — shared 32-bit bus

`a1`–`a32` = `BUS0`–`BUS31`

## Row `b` — dedicated 32-bit address bus

`b1`–`b32` = `ADDR0`–`ADDR31`

## Row `c` — decoded control signals, clock/reset/IRQ, power

| Pin | Signal | Pin | Signal | Pin | Signal | Pin | Signal |
|---|---|---|---|---|---|---|---|
| c1 | `AI` | c9 | `DO` | c17 | `MB` | c25 | `F` |
| c2 | `DI` | c10 | `PP1` | c18 | `SO` | c26 | `NO` |
| c3 | `II` | c11 | `PP2` | c19 | `ALT` | c27 | `EO` |
| c4 | `XI` | c12 | `PP4` | c20 | `IVO` | c28 | `JMP` |
| c5 | `YI` | c13 | `MO` | c21 | `EX` | c29 | `IRQ` |
| c6 | `IVI` | c14 | `MI` | c22 | `NX` | c30 | `CLK` |
| c7 | `SI` | c15 | `MW` | c23 | `EY` | c31 | `VCC` |
| c8 | `PO` | c16 | `MH` | c24 | `NY` | c32 | `GND` |

Note on `MO`/`MI`/`MW`/`MH`/`MB`: the width-specific busout/MI codes (`MO8L`/`MO8H`/`MO16L`/`MO16H`/`MO32`/`MI8`/`MI16`/`MI32`) stay internal to `scamp32-ucode`, which decodes them down to a generic memory-out strobe (`MO`), a generic memory-in/write strobe (`MI`), and three width-select lines (`MW`=word/32-bit, `MH`=half/16-bit, `MB`=byte/8-bit) before they cross the backplane — same pin-saving pattern as `ALTE`/`ALTDS` collapsing to the single `ALT` line.

Only 1 `VCC` / 1 `GND` pin on this connector (c31/c32) — flagging this against the earlier research note that a single pin per rail is under-spec'd for board current at this chip count (each DIN 41612 pin is typically only rated ~1-3A). If board power is meant to come from a **separate** dedicated power connector/bus bar rather than through this signal connector, that resolves it — worth confirming that's the plan rather than assuming.

## Internal-only signals (never leave `scamp32-ucode`)

These live entirely within the ucode board (which also hosts `IR`) and don't need a backplane pin:

| Signal | Note |
|---|---|
| `MO8L`, `MO8H`, `MO16L`, `MO16H`, `MO32` | width-specific memory-out codes — decoded down to `MO`+`MW`/`MH`/`MB` before leaving the board |
| `RT` | reset T-state — local to ucode sequencing |
| `MI8`, `MI16`, `MI32` | width-specific memory-in codes — decoded down to `MI`+`MW`/`MH`/`MB` |
| `IEN`, `IDS` | interrupt enable/disable pulses — local to ucode's interrupt logic |
| `ALTDS`, `ALTE` | alt-bank switch pulses — decoded down to the single `ALT` line |
| `JLT`, `JGT`, `JZ` | jump condition bits — consumed locally by ucode's own jump logic (only the resulting `JMP` decision crosses the backplane) |
| `IOH`, `IOL` | `IR`-internal (instruction register byte/halfword select) |

## Totals

- Row `a`: 32 pins (shared bus)
- Row `b`: 32 pins (address bus)
- Row `c`: 32 pins (30 decoded control/clock/reset/IRQ signals + 1 VCC + 1 GND)
- **96 of 96 pins used — no spares.** Worth knowing before the peripheral board's needs (extra IRQ lines, chip-selects for the CF reader/RTC/timer) come up, since this pinout has zero headroom left on this connector for that.
