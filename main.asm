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

_start:

PUSH EBP ; guarda o base pointer
MOV EBP, ESP ; estabelece um novo base pointer

; codigo manualmente adicionado toda vez 
MOV EDX, 0

; codigo gerado pelo compilador

PUSH DWORD 0 ; Declare x
MOV EBX, 3 ; Eval IntVal Node
MOV [EBP-4], EBX ; x = 3

; begin if statement
; evaluate condition Node(>)=>[Node(x)=>[] Node(2)=>[]]
; Evaluating BinOp >
MOV EBX, [EBP-4] ; Retrieve variable x from memory
PUSH EBX
MOV EBX, 2 ; Eval IntVal Node
POP EAX
CMP EAX, EBX
CALL binop_jg
MOV EBX, EAX
CMP EBX, False ; if condition is false, jump to else
JE ELSE_14
; if condition is true, evaluate true statement
MOV EBX, [EBP-4] ; Retrieve variable x from memory

; begin print coroutine
PUSH EBX ; Push args to stack
CALL print ; Func call
POP EBX ; Unstack args
; exit once true statement is done
JMP EXIT_IF_14
ELSE_14:
MOV EBX, 2 ; Eval IntVal Node

; begin print coroutine
PUSH EBX ; Push args to stack
CALL print ; Func call
POP EBX ; Unstack args
EXIT_IF_14:
; end if statement


; begin while loop
LOOP_26:
; Evaluating BinOp >
MOV EBX, [EBP-4] ; Retrieve variable x from memory
PUSH EBX
MOV EBX, 0 ; Eval IntVal Node
POP EAX
CMP EAX, EBX
CALL binop_jg
MOV EBX, EAX
CMP EBX, False ; if condition is false, exit
JE EXIT_26
MOV EBX, [EBP-4] ; Retrieve variable x from memory

; begin print coroutine
PUSH EBX ; Push args to stack
CALL print ; Func call
POP EBX ; Unstack args
; Evaluating BinOp -
MOV EBX, [EBP-4] ; Retrieve variable x from memory
PUSH EBX
MOV EBX, 1 ; Eval IntVal Node
POP EAX
SUB EAX, EBX
MOV EBX, EAX
MOV [EBP-4], EBX ; x = 2
JMP LOOP_26
EXIT_26:


; interrupcao de saida
POP EBP
MOV EAX, 1
INT 0x80
