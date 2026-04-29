section .data
    msg db "Hola Mundo", 0xA  ; El mensaje seguido de un salto de línea (0xA)
    len equ $ - msg           ; Cálculo automático de la longitud del mensaje

section .text
    global _start             ; Punto de entrada para el enlazador

_start:
    ; --- Preparar la llamada al sistema: sys_write (ID 1) ---
    mov rax, 1                ; ID de la función 'write'
    mov rdi, 1                ; File descriptor: 1 es 'stdout' (pantalla)
    mov rsi, msg              ; Dirección de memoria del mensaje
    mov rdx, len              ; Tamaño del mensaje en bytes
    syscall                   ; Invocar al kernel

    ; --- Preparar la llamada al sistema: sys_exit (ID 60) ---
    mov rax, 60               ; ID de la función 'exit'
    mov rdi, 0                ; Código de error: 0 (todo bien)
    syscall                   ; Invocar al kernel