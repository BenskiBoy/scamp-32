.PHONY: all ucode code

all: ucode code

ucode:
	python3 ./ucode/uasm.py ./ucode/ucode.s > ./ucode/ucode.hex
	python3 ./ucode/splithex.py ./ucode/ucode.hex
	python3 ./ucode/mk-instructions-json.py ./ucode/ucode.s ./asm/instructions.json

code: ucode
	python3 ./asm/asm.py ./code/test.s > ./code/test.hex
	python3 ./ucode/splithex.py ./code/test.hex 4