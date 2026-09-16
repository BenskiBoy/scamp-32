add x, (i8h): # Add <tt>r</tt> to <tt>x</tt>.
    MO8H AI 
    MO32 YI
    XI X+Y

ld sp, i32: # Load <tt>i32</tt> into <tt>sp</tt>.
    PO AI
    MO32 SI P+4

out i8l, x: # Output <tt>x</tt> to address <tt>i8l</tt>.
    IOL AI P+1 
    XO DI 

ld x, i8l: # Load <tt>i8l</tt> into <tt>x</tt>.
    IOL XI P+1

ld x, i16l: # Load <tt>i16l</tt> into <tt>x</tt>.
    PO AI
    MO16L XI P+2

ld y, x: # Load <tt>x</tt> into <tt>y</tt>.
    YI XO

add x, i8l: # Add <tt>i8l</tt> to <tt>x</tt>.
    IOL YI P+1
    XI X+Y 

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

ld (i8h), i32: # Load <tt>i32</tt> into <tt>r</tt>.
    P+1
    PO AI 
    MO32 YI P+4
    IOH AI
    MI32 YO

inc (i8h): # Increment <tt>r</tt>.
    IOH AI P+1
    MO32 YI
    MI32 Y+1


jnz i32: # Jump to <tt>i32</tt> if <tt>Z</tt> is not set.
    PO AI
    MO32 JNZ P+4

jr+ i8l: # Jump forwards relative to the address of the next instruction. <tt>jr+ 0</tt> is a no-op.
    P+1
    PO YI
    IOL XI 
    JMP X+Y


out i32, (i8h): # Output <tt>r</tt> to address <tt>i32</tt>.
    # byte-order: 1,0
    PO AI
    MO8H AI P+1
    MO32 YI P+4
    YO AI
    DI YO

tbsz (i8h), i32: # Test bits: if none of the bits set in <tt>i32</tt> are also set in <tt>r</tt>, skip the next <tt>sb</tt>. Use in tandem with <tt>sb</tt> to compute bitwise shift-right of 8 or more bits.
    IOH AI P+1
    MO32 XI
    PO AI
    MO32 YI P+4
    X&Y
    PO JNZ P+2
    PO JNZ P+2

sb (i8h), i8l: # Set bits in the register at <tt>r</tt> based on <tt>i8l</tt>. i.e. <tt>r |= i8l</tt>.
    IOH AI P+1
    MO32 XI
    PO AI
    MO8L YI P+1
    IOH AI
    MI32 X|Y