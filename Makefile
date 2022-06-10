compile: main.py main.c 
	python3 main.py main.c
	
assemble: compile
	nasm -f elf32 -F dwarf -g main.asm
	
link: assemble
	ld -m elf_i386 -o main main.o
	
run: link
	./main