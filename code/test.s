ld sp, 2048
ld iv, int_handler
ld x, iv
out 0, x

ien

jmp post_int_handler

int_handler:
    ld x, 69
    out 0, x
    ien
    reti

post_int_handler:

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
push8 13
push8 12
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

# 19: summing numbers in a list, using auto-increment
ld r0, 10
ld r1, 1
ld r2, 2
ld r3, 5
ld r4, 0
ld r5, 0
ld r6, 3
ld r7, 3
ld r8, 4
ld r9, 0
ld r10, 1
.def ptr r12
ld ptr, 0xffffff04
ld x, 0
L3:
    add32 x, (r12)
    inc r12
    inc r12
    inc r12
    inc r12

    dec r0
    jnz L3
out 0, x

# 20: subroutine call
ld sp, 2048
ld r0, 10
call double
out 0, r0

# 21: shr8 subroutine call
ld r0, 0x1500 # (21 << 8)
call shr8
out 0, r0

# 22: stack-relative
push8 22
push8 40
ld8 x, 2(sp)
out 0, x

# 23: indirect call
push32 10
push32 5
push32 8
ld x, add3
ld (funcptr), x
call (funcptr)
out 0, r0

# 24: 8 * 3
push32 8
push32 3
call mul
out 0, r0

# print a string
ld sp, 2048
ld x, str
push32 x
call print

jr- 2

# double 1 arg from the stack and return the result in r0
double:
    shl r0
    ret

# >>8 input:r0 output:r0. clobbers x, y, r63, r62.
shr8:
    ld r63, 0
    ld r62, 8
    shr8_loop:
        shl r63
        tbsz r0, 0x8000
        sb r63, 0x01
        shl r0
        dec r62
        jnz shr8_loop
    ld r0, r63
    ret

# add 3 args from the stack and return the result in r0
add3:
    ld r0, 0
    ld32 x, 8(sp)
    add r0, x
    ld32 x, 12(sp)
    add r0, x
    ld32 x, 16(sp)
    add r0, x
    ret 12

# multiply 2 numbers from stack and return result in r0
mul:
    ld32 x, 8(sp)
    ld r2, x # r2 = arg1 (2nd-pushed value, sits right above the return address)
    ld32 x, 12(sp)
    ld r1, x # r1 = arg2 (1st-pushed value, one slot further up)
    ld r0, 0 # result
    ld r3, 1 # (1 << i)

    mul_loop:
        ld x, r2 # x = arg1
        and x, r3 # x = arg1 & (1 << i)
        jz mul_cont # skip the "add" if this bit is not set
        add r0, r1 # result += resultn
    mul_cont:
        shl r1 # resultn += resultn
        shl r3 # i++
        jnz mul_loop # loop again if the mask has not overflowed

    ret 8 # discard both 4-byte arguments

# take a pointer to a nul-terminated string, and print it
print:
    ld32 x, 8(sp)
    ld r0, x
    print_loop:
        out8 2, (r0)
        inc r0
        test8 (r0)
        jnz print_loop
    ret 4


str: .str "Hello, world!\n\0"

# XXX: ".at 0x400" so that funcptr is writable (first 256 bytes are rom)
.at 0x400
funcptr:
