add x, (i8h): # Add <tt>r</tt> to <tt>x</tt>.
    MO8H AI 
    MO32 YI
    XI X+Y

out i8l, x: # Output <tt>x</tt> to address <tt>i8l</tt>.
    MO8L AI 
    XO DI 

ld x, i8l: # Load <tt>i8l</tt> into <tt>x</tt>.
    PO AI
    MO8L XI P+1

add x, i8l: # Add <tt>r</tt> to <tt>x</tt>.
    PO AI 
    MO8L YI P+1
    XI X+Y 

sub x, i8l: # Add <tt>r</tt> to <tt>x</tt>.
    PO AI 
    MO8L YI P+1
    XI X-Y 

inc x: # Increment <tt>x</tt>.
    XI X+1

dec x: # Decrement <tt>x</tt>.
    XI X-1

shl x: # Bitwise shift-left <tt>x</tt> by 1 place.
    YI X
    XI X+Y

and x, i8l: # AND <tt>i8l</tt> with <tt>x</tt>.
    PO AI 
    MO8L YI P+1
    XI X&Y

or x, i8l: # OR <tt>i8l</tt> into <tt>x</tt>.
    PO AI 
    MO8L YI P+1
    XI X|Y

xor x, y: # XOR <tt>y</tt> with <tt>x</tt>.
    # clobbers: r62
    # implicit: r62
    PO AI
    MO8H AI P+1
    MI32 X|Y
    YI ~(X&Y)
    MO32 XI
    XI X&Y


ld y, i16l: # Load <tt>i16</tt> into <tt>y</tt>.
    PO AI
    MO16L YI P+2