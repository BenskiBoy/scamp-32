add x, (i8h): # Add <tt>r</tt> to <tt>x</tt>.
    MO8H AI 
    MO32 YI
    XI X+Y

out i8l, x: # Output <tt>x</tt> to address <tt>i8l</tt>.
    MO8L AI
    XO DI

ld x, i8l: # Load <tt>i8l</tt> into <tt>x</tt>.
    MO8L XI
