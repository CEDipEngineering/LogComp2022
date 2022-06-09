; constantes
SYS_EXIT equ 1
SYS_READ equ 3
SYS_WRITE equ 4
STDIN equ 0
STDOUT equ 1
True equ 1
False equ 0

segment .data

segment .bss  ; variaveis
res RESB 1

section .text
global _start

print:  ; subrotina print

PUSH EBP ; guarda o base pointer
MOV EBP, ESP ; estabelece um novo base pointer

MOV EAX, [EBP+8] ; 1 argumento antes do RET e EBP
XOR ESI, ESI

print_dec: ; empilha todos os digitos
MOV EDX, 0
MOV EBX, 0x000A
DIV EBX
ADD EDX, '0'
PUSH EDX
INC ESI ; contador de digitos
CMP EAX, 0
JZ print_next ; quando acabar pula
JMP print_dec

print_next:
CMP ESI, 0
JZ print_exit ; quando acabar de imprimir
DEC ESI

MOV EAX, SYS_WRITE
MOV EBX, STDOUT

POP ECX
MOV [res], ECX
MOV ECX, res

MOV EDX, 1
INT 0x80
JMP print_next

print_exit:
POP EBP
RET

; subrotinas if/while
binop_je:
JE binop_true
JMP binop_false

binop_jg:
JG binop_true
JMP binop_false

binop_jl:
JL binop_true
JMP binop_false

binop_false:
MOV EBX, False
JMP binop_exit
binop_true:
MOV EBX, True
binop_exit:
RET



; main
main:

PUSH EBP ; Store base pointer
MOV EBP, ESP ; Relocate base pointer to new stack top

; begin print coroutine
MOV EBX, 5 ; Eval IntVal Node
PUSH EBX ; Push args to stack
CALL print ; Func call
POP EBX ; Unstack args
; end print coroutine

MOV EBX, 5 ; Eval IntVal Node
MOV EBX, 5 ; Eval IntVal Node
MOV EAX, EBX ; Moving evaluate children return to EAX
MOV ESP, EBP ; Destroy local scope
POP EBP ; Restore base pointer
RET ; Exiting main


PUSH EBP ; Store base pointer
MOV EBP, ESP ; Relocate base pointer to new stack top
_start:


CALL main
MOV EBX, EAX ; Output should be EBX, but EAX is RET default


; interrupcao de saida
POP EBP
MOV EAX, 1
INT 0x80
