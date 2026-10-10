# SCAMP-32 backplane bus pinout

Target connector: DIN 41612 Type C, 3 rows × 32 positions (96-way), rows `a`/`b`/`c`, matching the connector in `scamp32-template`.

## Row `a` — shared 32-bit bus

`a1`–`a32` = `BUS0`–`BUS31`

## Row `b` — dedicated 32-bit address bus

`b1`–`b32` = `ADDR0`–`ADDR31`

## Row `c` — decoded control signals, clock/reset/IRQ, power

| Pin | Signal | Pin | Signal | Pin | Signal | Pin | Signal |
|---|---|---|---|---|---|---|---|
| c1 | `GND` | c9 | `NY` | c17 | `MH` | c25 | `PO` |
| c2 | `VCC_IN` | c10 | `EY` | c18 | `MW` | c26 | `SI` |
| c3 | `CLK` | c11 | `NX` | c19 | `MI` | c27 | `IVI` |
| c4 | `IRQ` | c12 | `EX` | c20 | `MO` | c28 | `YI` |
| c5 | `JMP` | c13 | `IVO` | c21 | `PP4` | c29 | `XI` |
| c6 | `EO` | c14 | `ALT` | c22 | `PP2` | c30 | `II` |
| c7 | `NO` | c15 | `SO` | c23 | `PP1` | c31 | `DI` |
| c8 | `F` | c16 | `MB` | c24 | `DO` | c32 | `AI` |

Note on `MO`/`MI`/`MW`/`MH`/`MB`: the width-specific busout/MI codes (`MO8L`/`MO8H`/`MO16L`/`MO16H`/`MO32`/`MI8`/`MI16`/`MI32`) stay internal to `scamp32-ucode`, which decodes them down to a generic memory-out strobe (`MO`), a generic memory-in/write strobe (`MI`), and three width-select lines (`MW`=word/32-bit, `MH`=half/16-bit, `MB`=byte/8-bit) before they cross the backplane — same pin-saving pattern as `ALTE`/`ALTDS` collapsing to the single `ALT` line.

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

# Memory Controller Pins
The 2 memory boards have an additional bus for memory controller pins which control 
- RAM/ROM control (ROM_EN, RAM_EN, LOAD_CLK, RAM_CLK)
- RAM/ROM select (CHIP_0, CHIP_1, CHIP_2, CHIP_3)
- Memory data bus input conroller (MI0_0->MI3_3)
- Memory data bus output conroller (MO0_0->MO3_3)

## Totals

- Row `a`: 32 pins (shared bus)
- Row `b`: 32 pins (address bus)
- Row `c`: 32 pins (30 decoded control/clock/reset/IRQ signals + 1 VCC + 1 GND)
- **96 of 96 pins used — no spares.** Worth knowing before the peripheral board's needs (extra IRQ lines, chip-selects for the CF reader/RTC/timer) come up, since this pinout has zero headroom left on this connector for that.
