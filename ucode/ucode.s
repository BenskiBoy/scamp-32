add x, (i8h): # Add <tt>r</tt> to <tt>x</tt>.
    MO8H AI P+1
    MO32 YI
    XI X+Y

add8 x, ((i8h)): # Add the byte value at <tt>(r)</tt> to <tt>x</tt>.
    IOH AI P+1
    MO32 AI
    MO8L YI
    XI X+Y

add16 x, ((i8h)): # Add the 16-bit value at <tt>(r)</tt> to <tt>x</tt>.
    IOH AI P+1
    MO32 AI
    MO16L YI
    XI X+Y

add32 x, ((i8h)): # Add the 32-bit value at <tt>(r)</tt> to <tt>x</tt>.
    IOH AI P+1
    MO32 AI
    MO32 YI
    XI X+Y

add (i8h), (i32): # Add <tt>(i32)</tt> to the value in <tt>r</tt>.
    P+1
    PO AI
    MO32 AI P+4
    MO32 XI
    IOH AI
    MO32 YI
    MI32 Y+X

ld sp, i32: # Load <tt>i32</tt> into <tt>sp</tt>.
    PO AI
    MO32 SI P+4

ld iv, i32: # Load <tt>i32</tt> into the interrupt vector register.
    PO AI
    MO32 IVI P+4

ld x, iv: # Load the interrupt vector register into <tt>x</tt>.
    IVO XI

ien: # Enable interrupts.
    IEN

ids: # Disable interrupts.
    IDS

ld8 x, i8l(sp): # Load the byte value at <tt>(sp+i8l)</tt> into <tt>x</tt>.
    SO YI
    IOL XI P+1
    XI X+Y
    XO AI
    MO8L XI

ld16 x, i8l(sp): # Load the 16-bit value at <tt>(sp+i8l)</tt> into <tt>x</tt>.
    SO YI
    IOL XI P+1
    XI X+Y
    XO AI
    MO16L XI

ld32 x, i8l(sp): # Load the 32-bit value at <tt>(sp+i8l)</tt> into <tt>x</tt>.
    SO YI
    IOL XI P+1
    XI X+Y
    XO AI
    MO32 XI

ld x, (i8h): # Load <tt>r</tt> into <tt>x</tt>.
    IOH AI P+1
    MO32 XI

ld (i32), x: # Load <tt>x</tt> into the value in <tt>(i32)</tt>.
    PO AI
    MO32 AI P+4
    MI32 XO

out i8l, x: # Output <tt>x</tt> to address <tt>i8l</tt>.
    IOL AI P+1 
    XO DI 


ld x, i8l: # Load <tt>i8l</tt> into <tt>x</tt>.
    IOL XI P+1

ld x, i16l: # Load <tt>i16l</tt> into <tt>x</tt>.
    PO AI
    MO16L XI P+2

ld x, i32: # Load <tt>i32l</tt> into <tt>x</tt>.
    PO AI
    MO32 XI P+4

ld y, x: # Load <tt>x</tt> into <tt>y</tt>.
    YI XO

add x, i8l: # Add <tt>i8l</tt> to <tt>x</tt>.
    IOL YI P+1
    XI X+Y 

add (i8h), i32: # Add <tt>i32</tt> to <tt>r</tt>.
    P+1
    PO AI
    MO32 YI P+4
    IOH AI
    MO32 XI
    MI32 Y+X

add (i8h), x: # Add <tt>x</tt> to <tt>r</tt>.
    IOH AI P+1
    MO32 YI
    MI32 Y+X

ld x, (i8h+i8l): # Load the value at (r)+i8l into x.
    IOH AI P+1
    MO32 YI
    PO AI
    MO8L XI P+1
    XI X+Y
    XO AI
    MO32 XI

ld x, ((i8h)++), i8l: # Load the byte at (r) into x. Advance the pointer stored in r by i8l.
    IOH AI P+1
    MO32 YI
    PO AI
    MO8L XI P+1
    XI X+Y
    IOH AI
    XO MI32
    YO AI
    MO8L XI

add x, y: # Add <tt>y</tt> to <tt>x</tt>.
    XI X+Y


sub x, i8l: # Subtract <tt>i8l</tt> from <tt>x</tt>.
    IOL YI P+1
    XI X-Y

inc x: # Increment <tt>x</tt>.
    XI X+1 

dec x: # Decrement <tt>x</tt>.
    XI X-1 

dec (i8h): # Decrement <tt>r</tt>.
    IOH AI P+1
    MO32 YI
    MI32 Y-1

shl x: # Bitwise shift-left <tt>x</tt> by 1 place.
    YI X
    XI X+Y

and x, i8l: # AND <tt>i8l</tt> with <tt>x</tt>.
    IOL YI P+1
    XI X&Y

and x, (i8h): # AND <tt>r</tt> with <tt>x</tt>.
    IOH AI P+1
    MO32 YI
    XI X&Y

or x, i8l: # OR <tt>i8l</tt> into <tt>x</tt>.
    IOL YI P+1
    XI X|Y

xor x, y: # XOR <tt>y</tt> with <tt>x</tt>.
    # clobbers: r62
    # implicit: r62
    IOH AI P+1
    MI32 X|Y
    YI ~(X&Y)
    MO32 XI
    XI X&Y


ld y, i16l: # Load <tt>i16</tt> into <tt>y</tt>.
    PO AI
    MO16L YI P+2

push8 i8l: # Store <tt>i8l</tt> to the value in <tt>(sp)</tt>. Post-decrement <tt>sp</tt> by 1.
    # implicit-byte: 1
    SO YI P+1
    YO AI 
    MI8 IOL 
    PO AI P+1
    MO8L XI 
    Y-X SI

push16 i16l: # Store <tt>i16l</tt> to the value in <tt>(sp)</tt>. Post-decrement <tt>sp</tt> by 2.
    # implicit-byte: 2
    PO AI
    MO16L XI P+2
    SO YI
    YO AI
    XO MI16
    PO AI
    MO8L XI P+1
    Y-X SI

push32 i32: # Store <tt>i32</tt> to the value in <tt>(sp)</tt>. Post-decrement <tt>sp</tt> by 4.
    # implicit-byte: 4
    PO AI
    MO32 XI P+4
    SO YI
    YO AI
    XO MI32
    PO AI
    MO8L XI P+1
    Y-X SI

push8 x: # Store the low byte of <tt>x</tt> to the value in <tt>(sp)</tt>. Post-decrement <tt>sp</tt> by 1.
    # implicit-byte: 1
    SO YI
    YO AI
    XO MI8
    IOL XI P+1
    Y-X SI

push16 x: # Store the low 16 bits of <tt>x</tt> to the value in <tt>(sp)</tt>. Post-decrement <tt>sp</tt> by 2.
    # implicit-byte: 2
    SO YI
    YO AI
    XO MI16
    IOL XI P+1
    Y-X SI

push32 x: # Store <tt>x</tt> to the value in <tt>(sp)</tt>. Post-decrement <tt>sp</tt> by 4.
    # implicit-byte: 4
    SO YI
    YO AI
    XO MI32
    IOL XI P+1
    Y-X SI

pop8 x: # Pre-increment <tt>sp</tt> by 1. Load <tt>x</tt> from the low byte of the value in <tt>(sp)</tt>.
    # implicit-byte: 1
    SO YI
    IOL XI P+1
    Y+X YI
    YO SI
    YO AI
    MO8L XI

pop16 x: # Pre-increment <tt>sp</tt> by 2. Load <tt>x</tt> from the low 16 bits of the value in <tt>(sp)</tt>.
    # implicit-byte: 2
    SO YI
    IOL XI P+1
    Y+X YI
    YO SI
    YO AI
    MO16L XI

pop32 x: # Pre-increment <tt>sp</tt> by 4. Load <tt>x</tt> from the value in <tt>(sp)</tt>.
    # implicit-byte: 4
    SO YI
    IOL XI P+1
    Y+X YI
    YO SI
    YO AI
    MO32 XI

jmp i32: # Jump to <tt>i32</tt>.
    PO AI
    MO32 JMP

ld (i8h), i8l: # Load <tt>i8</tt> into <tt>r</tt>.
    P+1
    PO AI 
    MO8L YI P+1
    IOH AI
    MI32 YO
    
ld (i8h), i16l: # Load <tt>i16</tt> into <tt>r</tt>.
    P+1
    PO AI 
    MO16L YI P+2
    IOH AI
    MI32 YO

ld (i8h), i32: # Load <tt>i32</tt> into <tt>r</tt>.
    P+1
    PO AI 
    MO32 YI P+4
    IOH AI
    MI32 YO

ld (i8h), x: # Load <tt>x</tt> into <tt>r</tt>.
    IOH AI P+1
    MI32 XO

ld (i8h), (i8h): # Load the value in the second <tt>r</tt> into the first <tt>r</tt>.
    IOH AI P+1
    PO AI
    MO8H AI P+1
    MO32 YI
    IOH AI
    MI32 YO

shl (i8h): # Bitwise shift-left <tt>r</tt> by 1 place.
    IOH AI P+1
    MO32 XI
    YI X
    MI32 X+Y

inc (i8h): # Increment <tt>r</tt>.
    IOH AI P+1
    MO32 YI
    MI32 Y+1

test8 ((i8h)): # Set flags based on the byte value at <tt>(r)</tt>.
    IOH AI P+1
    MO32 AI
    MO8L YI
    Y

test16 ((i8h)): # Set flags based on the 16-bit value at <tt>(r)</tt>.
    IOH AI P+1
    MO32 AI
    MO16L YI
    Y

test32 ((i8h)): # Set flags based on the 32-bit value at <tt>(r)</tt>.
    IOH AI P+1
    MO32 AI
    MO32 YI
    Y


jnz i32: # Jump to <tt>i32</tt> if <tt>Z</tt> is not set.
    PO AI
    MO32 JNZ P+4

jr+ i8l: # Jump forwards relative to the address of the next instruction. <tt>jr+ 0</tt> is a no-op.
    P+1
    PO YI 
    IOL XI 
    JMP X+Y


jr- i8l: # Jump backwards relative to the address of the next instruction. <tt>jr- 0</tt> is a no-op. <tt>jr- 1</tt> is an infinite loop.
    P+1
    PO YI
    IOL XI 
    JMP Y-X

jz i32: # Jump to <tt>i32</tt> if <tt>Z</tt> is set.
    PO AI
    MO32 JZ P+4

out i32, (i8h): # Output <tt>r</tt> to address <tt>i32</tt>.
    # byte-order: 1,0
    IOH AI P+1
    MO32 YI
    PO AI
    MO32 AI P+4
    YO DI

out8 i32, ((i8h)): # Output the byte value at <tt>(r)</tt> to address <tt>i32</tt>.
    # byte-order: 1,0
    IOH AI P+1
    MO32 AI
    MO8L YI
    PO AI
    MO32 AI P+4
    YO DI

out16 i32, ((i8h)): # Output the 16-bit value at <tt>(r)</tt> to address <tt>i32</tt>.
    # byte-order: 1,0
    IOH AI P+1
    MO32 AI
    MO16L YI
    PO AI
    MO32 AI P+4
    YO DI

out32 i32, ((i8h)): # Output the 32-bit value at <tt>(r)</tt> to address <tt>i32</tt>.
    # byte-order: 1,0
    IOH AI P+1
    MO32 AI
    MO32 YI
    PO AI
    MO32 AI P+4
    YO DI

tbsz (i8h), i32: # Test bits: if none of the bits set in <tt>i32</tt> are also set in <tt>r</tt>, skip the next <tt>sb</tt>. Use in tandem with <tt>sb</tt> to compute bitwise shift-right of 8 or more bits.
    IOH AI P+1
    MO32 XI
    PO AI
    MO32 YI P+4
    X&Y
    PO JNZ P+2
    PO JNZ P+1

sb (i8h), i8l: # Set bits in the register at <tt>r</tt> based on <tt>i8l</tt>. i.e. <tt>r |= i8l</tt>.
    IOH AI P+1
    MO32 XI
    PO AI
    MO8L YI P+1
    IOH AI
    MI32 X|Y

call i32: # Push the return address onto <tt>(sp)</tt>. Post-decrement <tt>sp</tt> by 4. Jump to <tt>i32</tt>.
    # implicit-byte: 4
    P+4
    PO AI
    MO8L XI P+1
    SO YI
    YO AI
    PO MI32
    Y-X SI
    PO YI
    YI Y-X-1
    YO AI
    MO32 JMP

call (i32): # Push the return address onto <tt>(sp)</tt>. Post-decrement <tt>sp</tt> by 4. Jump to the address stored at <tt>(i32)</tt>.
    # implicit-byte: 4
    P+4
    PO AI
    MO8L XI P+1
    SO YI
    YO AI
    PO MI32
    Y-X SI
    PO YI
    YI Y-X-1
    YO AI
    MO32 YI
    YO AI
    MO32 JMP


ret: # Pre-increment <tt>sp</tt> by 4. Pop the return address off <tt>(sp)</tt> and jump to it.
    # implicit-byte: 4
    SO YI
    IOL XI P+1
    Y+X YI
    YO SI
    YO AI
    MO32 JMP

reti: # Pre-increment <tt>sp</tt> by 4. Pop the return address off <tt>(sp)</tt>, re-enable interrupts, and jump to it. Use to return from an interrupt handler entered via <tt>irq</tt>.
    # implicit-byte: 4
    SO YI
    IOL XI P+1
    Y+X YI
    YO SI
    YO AI
    MO32 JMP

ret i8l: # Pop the return address off <tt>(sp)</tt> and jump to it, then discard <tt>i8l</tt> further bytes of caller-pushed arguments (i.e. pre-increment <tt>sp</tt> by <tt>4+i8l</tt>).
    SO YI
    IOL XI P+1
    YI Y+1
    YI Y+1
    YI Y+1
    YI Y+1
    YO AI
    XI X+Y
    XO SI
    MO32 JMP

irq: # Hardware interrupt entry point (never called directly -- see doc/UCODE.md "Extensibility"). Disables interrupts (re-enable with <tt>ien</tt> once safe -- otherwise the handler's own first fetch would immediately re-trigger irq). Push the return address onto <tt>(sp)</tt>. Post-decrement <tt>sp</tt> by 4 (width muxed in alongside the forced opcode, read via IOL). Jump to the address in the interrupt vector register.
    IDS
    SO YI
    YO AI
    PO MI32
    IOL XI
    Y-X SI
    IVO JMP