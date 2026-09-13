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


