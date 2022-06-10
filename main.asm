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



; rock
rock:

PUSH EBP ; Store base pointer
MOV EBP, ESP ; Relocate base pointer to new stack top
PUSH DWORD 0 ; Declare x
PUSH DWORD 0 ; Declare y
PUSH DWORD 0 ; Declare h
; Evaluating BinOp +
MOV EBX, [EBP+8] ; Retrieve variable x from memory
PUSH EBX
MOV EBX, [EBP+12] ; Retrieve variable y from memory
POP EAX
ADD EAX, EBX
MOV EBX, EAX
MOV [EBP-4], EBX ; h = some value
MOV EBX, [EBP-4] ; Retrieve variable h from memory
MOV EAX, EBX ; Moving evaluate children return to EAX
MOV ESP, EBP ; Destroy local scope
POP EBP ; Restore base pointer
RET ; Exiting rock

; recursive
recursive:

PUSH EBP ; Store base pointer
MOV EBP, ESP ; Relocate base pointer to new stack top
PUSH DWORD 0 ; Declare x

; begin if statement
; evaluate condition >
; Evaluating BinOp >
MOV EBX, [EBP+8] ; Retrieve variable x from memory
PUSH EBX
MOV EBX, 0 ; Eval IntVal Node
POP EAX
CMP EAX, EBX
CALL binop_jg
CMP EBX, False ; if condition is false, jump to else
JE ELSE_34
; if condition is true, evaluate true statement

; begin print coroutine
MOV EBX, [EBP+8] ; Retrieve variable x from memory
PUSH EBX ; Push args to stack
CALL print ; Func call
POP EBX ; Unstack args
; end print coroutine

; Evaluating BinOp -
MOV EBX, [EBP+8] ; Retrieve variable x from memory
PUSH EBX
MOV EBX, 1 ; Eval IntVal Node
POP EAX
SUB EAX, EBX
MOV EBX, EAX
PUSH EBX ; Evaluating args in func call 

CALL recursive
MOV EBX, EAX ; Output should be EBX, but EAX is RET default
; exit once true statement is done
JMP EXIT_IF_34
ELSE_34:

; begin print coroutine
MOV EBX, [EBP+8] ; Retrieve variable x from memory
PUSH EBX ; Push args to stack
CALL print ; Func call
POP EBX ; Unstack args
; end print coroutine

EXIT_IF_34:
; end if statement

MOV ESP, EBP ; Destroy local scope
POP EBP ; Restore base pointer
RET ; Exiting recursive

; loop_up
loop_up:

PUSH EBP ; Store base pointer
MOV EBP, ESP ; Relocate base pointer to new stack top
PUSH DWORD 0 ; Declare n
PUSH DWORD 0 ; Declare i

; begin while loop
LOOP_54:
; Evaluating BinOp <
MOV EBX, [EBP+12] ; Retrieve variable i from memory
PUSH EBX
MOV EBX, [EBP+8] ; Retrieve variable n from memory
POP EAX
CMP EAX, EBX
CALL binop_jl
CMP EBX, False ; if condition is false, exit
JE EXIT_54

; begin print coroutine
MOV EBX, [EBP+12] ; Retrieve variable i from memory
PUSH EBX ; Push args to stack
CALL print ; Func call
POP EBX ; Unstack args
; end print coroutine

; Evaluating BinOp +
MOV EBX, [EBP+12] ; Retrieve variable i from memory
PUSH EBX
MOV EBX, 1 ; Eval IntVal Node
POP EAX
ADD EAX, EBX
MOV EBX, EAX
MOV [EBP+12], EBX ; i = some value
JMP LOOP_54
EXIT_54:
MOV ESP, EBP ; Destroy local scope
POP EBP ; Restore base pointer
RET ; Exiting loop_up

; main
main:

PUSH EBP ; Store base pointer
MOV EBP, ESP ; Relocate base pointer to new stack top
MOV EBX, 5 ; Eval IntVal Node
PUSH EBX ; Evaluating args in func call 

CALL recursive
MOV EBX, EAX ; Output should be EBX, but EAX is RET default
MOV EBX, 8 ; Eval IntVal Node
PUSH EBX ; Evaluating args in func call 

MOV EBX, 10 ; Eval IntVal Node
PUSH EBX ; Evaluating args in func call 

CALL loop_up
MOV EBX, EAX ; Output should be EBX, but EAX is RET default
PUSH DWORD 0 ; Declare x
MOV EBX, 2 ; Eval IntVal Node
PUSH EBX ; Evaluating args in func call 

MOV EBX, 10 ; Eval IntVal Node
PUSH EBX ; Evaluating args in func call 

CALL rock
MOV EBX, EAX ; Output should be EBX, but EAX is RET default
MOV [EBP-4], EBX ; x = some value

; begin print coroutine
MOV EBX, [EBP-4] ; Retrieve variable x from memory
PUSH EBX ; Push args to stack
CALL print ; Func call
POP EBX ; Unstack args
; end print coroutine

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
