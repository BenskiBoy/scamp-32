# 19: summing numbers in a list, using auto-increment
.def ptr r12
ld ptr, list19
ld x, 0
ld r0, 10
L3:
    ld y, x
    ld x, (ptr++), 1
    add x, y
    out 1, x
    dec r0
    jnz L3
out 1, x
jmp after19
list19:
.byte 1
.byte 2
.byte 5
.byte 0
.byte 0
.byte 3
.byte 3
.byte 4
.byte 0
.byte 1
after19:


# 0
ld x, 0
out 0, x

# 1
ld x, 1
out 0, x

# 2
ld x, 2
out 0, x

# 3
ld x, 3
out 0, x

# 4: add 1+3
ld x, 1
add x, 3
out 0, x

# 5: sub 100-95
ld x, 100
sub x, 95
out 0, x

# 6: inc 5+1
ld x, 5
inc x
out 0, x

# 7: dec 8-1
ld x, 8
dec x
out 0, x

# 8: shl 4
ld x, 4
shl x
out 0, x

# 9: 1001 == 1000 | 0001
ld x, 8
or x, 1
out 0, x

# 10: 1010 == 1110 & 1011
ld x, 14
and x, 11
out 0, x


# 11: 1011 == 11101 ^ 10110
ld x, 29
ld y, 22
xor x, y
out 0, x


# 12,13: push 13, push 12, pop, out, pop, out
ld sp, 2048
push8 12
push8 13
ld x, 42
pop8 x
out 0, x
pop8 x
out 0, x

# 14: unconditional jump
ld x, 14
jmp L
ld x, 42
L: out 0, x

# 15: conditional jump
ld r0, 0
ld x, 15
L2:
inc r0
dec x
jnz L2
out 0, r0

# 16: shift-right by 8
ld r0, 0x1000
ld r62, 0
tbsz r0, 0x8000
sb r62, 0x80
tbsz r0, 0x4000
sb r62, 0x40
tbsz r0, 0x2000
sb r62, 0x20
tbsz r0, 0x1000
sb r62, 0x10
tbsz r0, 0x0800
sb r62, 0x08
tbsz r0, 0x0400
sb r62, 0x04
tbsz r0, 0x0200
sb r62, 0x02
tbsz r0, 0x0100
sb r62, 0x01
# if we're lucky, r62 now has 0x1000 >> 8
out 0, r62

# 17: xor x, y
# 17 = 0x0011 = 0b0000000000010001
#            a: 0b0110100101010010 = 0x6952
#            b: 0b0110100101000011 = 0x6943
ld x, 0x6952
ld y, x
ld x, 0x6943
xor x, y
out 0, x

# 18: relative jump
ld r0, 18
jr+ 3
ld r0, 0
out 0, r0
