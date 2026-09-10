.PHONY: all ucode code

all: ucode code

ucode:
	python3 ./ucode/uasm.py ./ucode/ucode.s > ./ucode/ucode.hex
	python3 ./ucode/splithex.py ./ucode/ucode.hex

code:
	python3 ./asm/asm.py ./code/test.s > ./code/test.hex
	python3 ./ucode/splithex.py ./code/test.hex 4