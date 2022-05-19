main: main.c
	python3 main.py main.c
	nasm -f elf32 -F dwarf -g main.asm
	ld -m elf_i386 -o main main.o
	./main