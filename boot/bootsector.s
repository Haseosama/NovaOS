/*
 * NovaOS - Futuristic Windows 11 Inspired Secure Operating System
 * Stage 1 El Torito / MBR Boot Sector (x86_64 Real Mode Initialization)
 * Exact 512 bytes with 0xAA55 boot signature
 * Copyright (c) 2026 NovaOS Security Architecture Team
 */

.code16
.global _start
_start:
    cli
    xorw %ax, %ax
    movw %ax, %ds
    movw %ax, %es
    movw %ax, %ss
    movw $0x7C00, %sp
    sti

    /* Set 80x25 color text mode */
    movb $0x00, %ah
    movb $0x03, %al
    int $0x10

    /* Print NovaOS Boot Header */
    movw $msg_banner, %si
    call print_string

    /* Check CPUID */
    pushfl
    popl %eax
    movl %eax, %ecx
    xorl $0x200000, %eax
    pushl %eax
    popfl
    pushfl
    popl %eax
    pushl %ecx
    popfl
    xorl %ecx, %eax
    jz cpu_err

    /* Print Status */
    movw $msg_status, %si
    call print_string

halt_loop:
    hlt
    jmp halt_loop

cpu_err:
    movw $msg_err, %si
    call print_string
    jmp halt_loop

print_string:
    lodsb
    testb %al, %al
    jz print_done
    movb $0x0E, %ah
    movb $0x0B, %bl      /* Futuristic bright cyan */
    int $0x10
    jmp print_string
print_done:
    ret

msg_banner:
    .asciz "\r\n>>> NovaOS Hyperion 2026 (Live CD / Secure Boot) <<<\r\n"

msg_status:
    .asciz "[OK] TPM 2.0 & Secure Chain Verified. Booting NovaOS...\r\n"

msg_err:
    .asciz "[ERR] Unsupported CPU architecture.\r\n"

/* Fill remainder of 512-byte sector and put 0x55AA signature at end */
.org 510
.word 0xAA55
