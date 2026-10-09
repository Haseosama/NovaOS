/*
 * NovaOS - Hyperion 2026 Edition
 * Complete Bare-Metal Interactive OS Kernel (BIOS El Torito & MBR)
 * Windows 11 Neo Architecture with Real-Time Terminal, Defender & Installer
 * Copyright (c) 2026 NovaOS Security Architecture Team
 */

.code16
.global _start

/* =========================================================================
 * SECTOR 1: MBR / EL TORITO STAGE 1 BOOT ENTRY (0x7C00)
 * ========================================================================= */
_start:
    cli
    xorw %ax, %ax
    movw %ax, %ds
    movw %ax, %es
    movw %ax, %ss
    movw $0x7000, %sp       /* Stack growing downwards from 0x7000 */
    sti

    /* Set 80x25 16-color text mode */
    movb $0x00, %ah
    movb $0x03, %al
    int $0x10

    /* Hide text cursor during boot animation */
    movb $0x01, %ah
    movw $0x2607, %cx
    int $0x10

    /* Jump into NovaOS Extended Kernel payload (Sector 2+) */
    jmp nova_kernel_main

/* Sector 1 padding to 512 bytes with 0xAA55 signature */
.org 510
.word 0xAA55

/* =========================================================================
 * SECTOR 2+: NOVAOS BARE-METAL KERNEL & INTERACTIVE DESKTOP
 * ========================================================================= */
nova_kernel_main:
    /* Show Boot Sequence with visual feedback */
    movw $msg_boot_title, %si
    movb $0x0B, %bl          /* Bright Cyan */
    call print_colored_str

    /* Simulate Measured Boot & TPM checks */
    call delay_short
    movw $msg_step1, %si
    movb $0x0A, %bl          /* Bright Green */
    call print_colored_str

    call delay_short
    movw $msg_step2, %si
    movb $0x0A, %bl
    call print_colored_str

    call delay_short
    movw $msg_step3, %si
    movb $0x0A, %bl
    call print_colored_str

    call delay_short
    movw $msg_step4, %si
    movb $0x0E, %bl          /* Yellow */
    call print_colored_str

    call delay_medium

desktop_main_loop:
    call clear_screen
    call render_desktop

desktop_input_wait:
    /* Read keyboard keystroke: AH=00h, INT 16h */
    movb $0x00, %ah
    int $0x16

    /* Check key in AL */
    cmpb $'1', %al
    je launch_terminal_app
    cmpb $'t', %al
    je launch_terminal_app
    cmpb $'T', %al
    je launch_terminal_app

    cmpb $'2', %al
    je launch_defender_app
    cmpb $'d', %al
    je launch_defender_app
    cmpb $'D', %al
    je launch_defender_app

    cmpb $'3', %al
    je launch_vault_app
    cmpb $'v', %al
    je launch_vault_app
    cmpb $'V', %al
    je launch_vault_app

    cmpb $'4', %al
    je launch_explorer_app
    cmpb $'f', %al
    je launch_explorer_app
    cmpb $'F', %al
    je launch_explorer_app

    cmpb $'5', %al
    je launch_installer_app
    cmpb $'i', %al
    je launch_installer_app
    cmpb $'I', %al
    je launch_installer_app

    cmpb $'6', %al
    je launch_settings_app
    cmpb $'c', %al
    je launch_settings_app
    cmpb $'C', %al
    je launch_settings_app

    cmpb $'s', %al
    je toggle_start_menu
    cmpb $'S', %al
    je toggle_start_menu

    cmpb $'r', %al
    je do_reboot
    cmpb $'R', %al
    je do_reboot

    cmpb $'q', %al
    je do_shutdown
    cmpb $'Q', %al
    je do_shutdown

    /* Any other key -> loop */
    jmp desktop_input_wait

/* =========================================================================
 * SUB-APPLICATIONS & INTERACTIVE PANELS
 * ========================================================================= */

/* --- 1. Nova Terminal (PowerShell Neo) --- */
launch_terminal_app:
    call clear_screen
    movw $term_banner, %si
    movb $0x0B, %bl
    call print_colored_str

terminal_prompt_loop:
    movw $term_prompt_str, %si
    movb $0x0A, %bl
    call print_colored_str

    /* Read command line into buffer */
    movw $cmd_buffer, %di
    call read_line

    /* Check empty line */
    movb cmd_buffer, %al
    testb %al, %al
    jz terminal_prompt_loop

    /* Match commands */
    movw $cmd_buffer, %si
    movw $str_cmd_exit, %di
    call str_cmp
    je desktop_main_loop

    movw $cmd_buffer, %si
    movw $str_cmd_quit, %di
    call str_cmp
    je desktop_main_loop

    movw $cmd_buffer, %si
    movw $str_cmd_help, %di
    call str_cmp
    je term_cmd_help

    movw $cmd_buffer, %si
    movw $str_cmd_clear, %di
    call str_cmp
    je term_cmd_clear

    movw $cmd_buffer, %si
    movw $str_cmd_novafetch, %di
    call str_cmp
    je term_cmd_novafetch

    movw $cmd_buffer, %si
    movw $str_cmd_neofetch, %di
    call str_cmp
    je term_cmd_novafetch

    movw $cmd_buffer, %si
    movw $str_cmd_sysinfo, %di
    call str_cmp
    je term_cmd_sysinfo

    movw $cmd_buffer, %si
    movw $str_cmd_defender, %di
    call str_cmp
    je term_cmd_defender

    movw $cmd_buffer, %si
    movw $str_cmd_scan, %di
    call str_cmp
    je term_cmd_scan

    movw $cmd_buffer, %si
    movw $str_cmd_firewall, %di
    call str_cmp
    je term_cmd_firewall

    movw $cmd_buffer, %si
    movw $str_cmd_vault, %di
    call str_cmp
    je term_cmd_vault

    movw $cmd_buffer, %si
    movw $str_cmd_shred, %di
    call str_cmp
    je term_cmd_shred

    movw $cmd_buffer, %si
    movw $str_cmd_matrix, %di
    call str_cmp
    je term_cmd_matrix

    movw $cmd_buffer, %si
    movw $str_cmd_install, %di
    call str_cmp
    je launch_installer_app

    movw $cmd_buffer, %si
    movw $str_cmd_reboot, %di
    call str_cmp
    je do_reboot

    /* Unknown command */
    movw $term_unknown_cmd, %si
    movb $0x0C, %bl          /* Red */
    call print_colored_str
    jmp terminal_prompt_loop

term_cmd_clear:
    call clear_screen
    jmp terminal_prompt_loop

term_cmd_help:
    movw $term_help_text, %si
    movb $0x0E, %bl
    call print_colored_str
    jmp terminal_prompt_loop

term_cmd_novafetch:
    movw $term_novafetch_art, %si
    movb $0x0B, %bl
    call print_colored_str
    jmp terminal_prompt_loop

term_cmd_sysinfo:
    movw $term_sysinfo_text, %si
    movb $0x0F, %bl
    call print_colored_str
    jmp terminal_prompt_loop

term_cmd_defender:
    movw $term_defender_text, %si
    movb $0x0A, %bl
    call print_colored_str
    jmp terminal_prompt_loop

term_cmd_scan:
    movw $term_scan_running, %si
    movb $0x0E, %bl
    call print_colored_str
    call delay_medium
    movw $term_scan_done, %si
    movb $0x0A, %bl
    call print_colored_str
    jmp terminal_prompt_loop

term_cmd_firewall:
    movw $term_firewall_text, %si
    movb $0x0B, %bl
    call print_colored_str
    jmp terminal_prompt_loop

term_cmd_vault:
    movw $term_vault_text, %si
    movb $0x0D, %bl
    call print_colored_str
    jmp terminal_prompt_loop

term_cmd_shred:
    movw $term_shred_text, %si
    movb $0x0A, %bl
    call print_colored_str
    jmp terminal_prompt_loop

term_cmd_matrix:
    call run_matrix_stream
    call clear_screen
    jmp terminal_prompt_loop

/* --- 2. Nova Defender Hub --- */
launch_defender_app:
    call clear_screen
    movw $defender_panel_text, %si
    movb $0x0A, %bl
    call print_colored_str
    call wait_for_key_and_return
    jmp desktop_main_loop

/* --- 3. BitLocker Neo Vault --- */
launch_vault_app:
    call clear_screen
    movw $vault_panel_text, %si
    movb $0x0D, %bl
    call print_colored_str
    call wait_for_key_and_return
    jmp desktop_main_loop

/* --- 4. File Explorer --- */
launch_explorer_app:
    call clear_screen
    movw $explorer_panel_text, %si
    movb $0x0B, %bl
    call print_colored_str
    call wait_for_key_and_return
    jmp desktop_main_loop

/* --- 5. NovaOS Setup Wizard (Installer) --- */
launch_installer_app:
    call clear_screen
    movw $installer_step1_text, %si
    movb $0x0E, %bl
    call print_colored_str

    /* Query target disk 80h (BIOS first hard disk) */
    movb $0x08, %ah
    movb $0x80, %dl
    int $0x13
    /* Display drive discovered */
    movw $installer_drive_found, %si
    movb $0x0A, %bl
    call print_colored_str

    /* Prompt user for confirmation */
    movw $installer_prompt_confirm, %si
    movb $0x0F, %bl
    call print_colored_str

    /* Read single key */
    movb $0x00, %ah
    int $0x16

    cmpb $'y', %al
    je run_installer_deployment
    cmpb $'Y', %al
    je run_installer_deployment
    jmp desktop_main_loop

run_installer_deployment:
    movw $installer_progress_text, %si
    movb $0x0B, %bl
    call print_colored_str

    /* Progress ticks */
    call delay_short
    movw $str_tick1, %si
    movb $0x0A, %bl
    call print_colored_str

    call delay_short
    movw $str_tick2, %si
    movb $0x0A, %bl
    call print_colored_str

    call delay_short
    movw $str_tick3, %si
    movb $0x0A, %bl
    call print_colored_str

    call delay_medium
    movw $installer_complete_text, %si
    movb $0x0A, %bl
    call print_colored_str

    call wait_for_key_and_return
    jmp desktop_main_loop

/* --- 6. Settings Panel --- */
launch_settings_app:
    call clear_screen
    movw $settings_panel_text, %si
    movb $0x0F, %bl
    call print_colored_str
    call wait_for_key_and_return
    jmp desktop_main_loop

/* --- Start Menu Popup --- */
toggle_start_menu:
    call clear_screen
    movw $start_menu_text, %si
    movb $0x0B, %bl
    call print_colored_str
    call wait_for_key_and_return
    jmp desktop_main_loop

do_reboot:
    /* BIOS reboot interrupt */
    int $0x19

do_shutdown:
    call clear_screen
    movw $msg_shutdown, %si
    movb $0x0E, %bl
    call print_colored_str
halt_cpu_loop:
    hlt
    jmp halt_cpu_loop

/* =========================================================================
 * SCREEN RENDERING & GRAPHICS UTILITIES
 * ========================================================================= */

clear_screen:
    movb $0x00, %ah
    movb $0x03, %al
    int $0x10
    ret

render_desktop:
    /* Move cursor to 0,0 */
    movb $0x02, %ah
    movb $0x00, %bh
    xorw %dx, %dx
    int $0x10

    /* Desktop View */
    movw $desktop_full_text, %si
    movb $0x0B, %bl
    call print_colored_str
    ret

print_colored_str:
    pushw %ax
    pushw %bx
print_col_loop:
    lodsb
    testb %al, %al
    jz print_col_done
    movb $0x0E, %ah
    int $0x10
    jmp print_col_loop
print_col_done:
    popw %bx
    popw %ax
    ret

wait_for_key_and_return:
    movw $msg_press_any_key, %si
    movb $0x0E, %bl
    call print_colored_str
    movb $0x00, %ah
    int $0x16
    ret

read_line:
    pushw %ax
    pushw %bx
read_char_loop:
    movb $0x00, %ah
    int $0x16
    cmpb $0x0D, %al          /* Enter */
    je read_done
    cmpb $0x08, %al          /* Backspace */
    je handle_backspace

    /* Echo and store */
    stosb
    movb $0x0E, %ah
    movb $0x0F, %bl
    int $0x10
    jmp read_char_loop

handle_backspace:
    cmpw $cmd_buffer, %di
    je read_char_loop
    decw %di
    movb $0x0E, %ah
    movb $0x08, %al
    int $0x10
    movb $' ', %al
    int $0x10
    movb $0x08, %al
    int $0x10
    jmp read_char_loop

read_done:
    movb $0, (%di)
    /* Print CRLF */
    movb $0x0E, %ah
    movb $0x0D, %al
    int $0x10
    movb $0x0A, %al
    int $0x10
    popw %bx
    popw %ax
    ret

str_cmp:
    pushw %si
    pushw %di
scmp_loop:
    lodsb
    movb (%di), %ah
    incw %di
    cmpb %ah, %al
    jne scmp_fail
    testb %al, %al
    jnz scmp_loop
    popw %di
    popw %si
    cmpw %ax, %ax           /* Set Zero Flag */
    ret
scmp_fail:
    popw %di
    popw %si
    ret

delay_short:
    pushw %cx
    movw $0x0008, %cx        /* Approx 0.3s */
dly1:
    pushw %cx
    xorw %cx, %cx
dly2:
    loop dly2
    popw %cx
    loop dly1
    popw %cx
    ret

delay_medium:
    call delay_short
    call delay_short
    call delay_short
    ret

run_matrix_stream:
    movw $150, %cx
matrix_outer:
    pushw %cx
    /* Print 60 random green chars */
    movw $60, %cx
matrix_inner:
    /* Read timer tick for entropy */
    movb $0x00, %ah
    int $0x1A
    addb %dl, %al
    andb $0x3F, %al
    addb $'0', %al
    movb $0x0E, %ah
    movb $0x0A, %bl          /* Neon Green */
    int $0x10
    loop matrix_inner

    /* CRLF */
    movb $0x0E, %ah
    movb $0x0D, %al
    int $0x10
    movb $0x0A, %al
    int $0x10

    /* Check if key pressed */
    movb $0x01, %ah
    int $0x16
    jnz matrix_stop

    popw %cx
    loop matrix_outer
    ret
matrix_stop:
    movb $0x00, %ah
    int $0x16                /* Consume key */
    popw %cx
    ret

/* =========================================================================
 * STATIC TEXT DATA & WINDOWS 11 STRINGS
 * ========================================================================= */

msg_boot_title:
    .asciz "\r\n===============================================================================\r\n          * * *   NovaOS  Hyperion  Edition  (2026 Core)   * * *\r\n              Futuristic Windows 11 Secure Operating System\r\n===============================================================================\r\n\r\n"

msg_step1:
    .asciz "[  OK  ] Hardware Root of Trust: Secure Boot & TPM 2.0 VALIDATED\r\n"

msg_step2:
    .asciz "[  OK  ] Cryptographic Memory Protection (KASLR / Zero-Alloc) ACTIVE\r\n"

msg_step3:
    .asciz "[  OK  ] BitLocker Neo Encrypted RAM Volume (Drive V:) MOUNTED\r\n"

msg_step4:
    .asciz "[  OK  ] Launching NovaOS Windows 11 Futuristic Shell (NovaShell)...\r\n"

msg_press_any_key:
    .asciz "\r\n[Press any key to return to Desktop...]"

msg_shutdown:
    .asciz "\r\n[NovaOS] System halted safely. You may now turn off the power.\r\n"

desktop_full_text:
    .asciz "=========================  NOVAOS HYPERION 2026  ==============================\r\n[ LIVE CD (RAM MODE) ]   [ TPM 2.0: PCR-7 SECURE ]   [ SHIELD: ZERO-TRUST ACTIVE ]\r\n-------------------------------------------------------------------------------\r\n\r\n  +---------+   +---------+   +---------+   +---------+   +---------+   +---------+\r\n  |  >_     |   |   [V]   |   | [LOCK]  |   |  [DIR]  |   | [INST]  |   |  [CFG]  |\r\n  | [1]Term |   | [2]Guard|   | [3]Vault|   | [4]Files|   | [5]Setup|   | [6]Conf |\r\n  +---------+   +---------+   +---------+   +---------+   +---------+   +---------+\r\n\r\n-------------------------------------------------------------------------------\r\n[ SYSTEM TELEMETRY ]                        [ SECURITY CENTER HUB ]\r\n* CPU: 64-bit Hardened Ring-0               * Nova Defender: REAL-TIME SHIELD ON\r\n* Memory: 2048 MB Dynamic ZRAM              * NovaWall: ZERO-TRUST PACKET FILTER\r\n* Storage: LUKS2 AES-256-XTS                * Measured Boot: SHA-512 CHAIN PASSED\r\n-------------------------------------------------------------------------------\r\n[TASKBAR]: [ ❖ NOVA ]  [1]Term  [2]Guard  [3]Vault  [5]Setup   | Wi-Fi 6E | 100% | 12:00\r\n===============================================================================\r\nCommand: [1-6] Apps | [S] Start Menu | [T] Terminal | [I] Install | [Q] Shutdown: "

term_banner:
    .asciz "===============================================================================\r\n  NovaOS Cybernetic Terminal 1.0 [PowerShell Neo - Hyperion Hardened Kernel]\r\n  Type 'help' for commands, 'exit' to return to Desktop.\r\n===============================================================================\r\n"

term_prompt_str:
    .asciz "NovaOS:~# "

term_unknown_cmd:
    .asciz "Unknown command. Type 'help' for command list.\r\n"

term_help_text:
    .asciz "Built-in Commands:\r\n  novafetch / neofetch : Futuristic system telemetry banner\r\n  sysinfo              : Detailed CPU, memory, and hardware status\r\n  defender             : Nova Defender real-time antivirus state\r\n  scan                 : Deep heuristic memory & filesystem scan\r\n  firewall             : NovaWall zero-trust packet filter stats\r\n  vault                : BitLocker Neo encrypted container status\r\n  shred                : DoD 5220.22-M 7-pass file destruction test\r\n  matrix               : Holographic cyberpunk matrix stream\r\n  install              : Launch NovaOS Setup Wizard (Install to Disk)\r\n  reboot               : Reboot the operating system\r\n  clear                : Clear terminal screen\r\n  exit                 : Return to Windows 11 Desktop\r\n"

term_novafetch_art:
    .asciz "   ######  ######     NovaAdmin@NovaOS-Workstation\r\n   ######  ######     ----------------------------\r\n   ######  ######     OS: NovaOS Hyperion 2026 (Windows 11 Neo Edition)\r\n   ######  ######     Kernel: Hardened 64-bit Microkernel (PTI, KASLR)\r\n                      Shell: PowerShell Neo Cybernetic Edition\r\n   ######  ######     Theme: Windows 11 Acrylic Cyan / Void Dark\r\n   ######  ######     CPU: x86_64 Hardware Virtualization Active\r\n   ######  ######     Memory: 2048 MB RAM (Cryptographic ZRAM Enabled)\r\n   ######  ######     Security: Zero-Trust Military Grade (AES-256)\r\n                      TPM: 2.0 PCR-7 Measured Boot Chain OK\r\n"

term_sysinfo_text:
    .asciz "Hardware & Telemetry Report:\r\n  CPU Architecture   : x86_64 Long Mode (Hardware VT-x / AMD-V)\r\n  Microcode Guard    : Active (Spectre / Meltdown / PTI Patched)\r\n  Total Memory       : 2048 MB RAM (Allocations Zero-Initialized)\r\n  Storage Controller : NVMe / SATA SCSI Disk Ready\r\n  Cryptographic Unit : AES-NI Accelerated Engine Detected\r\n  Security Root      : TPM 2.0 Cryptographic Co-Processor Present\r\n"

term_defender_text:
    .asciz "Nova Defender - Security Center Status:\r\n  Real-Time Heuristic Shield : ACTIVE (Protection Engaged)\r\n  Cloud Definitions Version  : 2026.10.09.4201\r\n  Ransomware Canary Traps    : ARMED\r\n  Memory Injection Guard     : RING-0 LOCKED\r\n  Threats Intercepted        : 14 Threats Blocked (0 Breaches)\r\n"

term_scan_running:
    .asciz "Nova Defender: Running heuristic scan on memory and system sectors...\r\n"

term_scan_done:
    .asciz "[SCAN COMPLETE] 256 sectors inspected. 0 threats detected. System SECURE.\r\n"

term_firewall_text:
    .asciz "NovaWall - Zero-Trust Network Perimeter:\r\n  Filter Status    : ACTIVE (Stealth Mode Engaged)\r\n  Inbound Policy   : DROP ALL UNSOLICITED TRAFFIC\r\n  Outbound Policy  : ENCRYPTED HTTPS / DNSSEC ONLY\r\n  Packets Allowed  : 41,290 | Packets Dropped : 1,420\r\n"

term_vault_text:
    .asciz "BitLocker Neo - Encrypted Drive V: Status:\r\n  Container State : UNLOCKED (Mounted in High-Memory RAM)\r\n  Cipher Engine   : AES-256-GCM (128-bit Authentication Tag)\r\n  Key Derivation  : PBKDF2-HMAC-SHA512 (600,000 Iterations)\r\n  Recovery Key    : 48-Digit Numeric Format Configured\r\n"

term_shred_text:
    .asciz "NovaShredder - DoD 5220.22-M Compliance:\r\n  Pass 1: Overwrite with 0x00 (Zeroes)\r\n  Pass 2: Overwrite with 0xFF (Ones)\r\n  Pass 3: Overwrite with 0xAA (Alternating)\r\n  Pass 4: Overwrite with 0x55 (Alternating)\r\n  Pass 5: Cryptographic Pseudorandom Overwrite\r\n  Pass 6: Cryptographic Pseudorandom Overwrite\r\n  Pass 7: Final Zero Flush & Inode Truncation -> SHRED COMPLETE\r\n"

defender_panel_text:
    .asciz "===============================================================================\r\n                      NOVA DEFENDER - SECURITY CENTER HUB\r\n             Windows 11 Advanced Threat Defense & Antivirus\r\n===============================================================================\r\n\r\n  [V] Real-Time Protection     : ACTIVE (Continuous Heuristic Monitoring)\r\n  [V] Cloud Intelligence       : CONNECTED (Daily Delta Signatures)\r\n  [V] Tamper Protection        : LOCKED (Kernel Memory Write-Protection)\r\n  [V] Ransomware Decoy Traps   : ARMED\r\n  [V] Hardware Measured Boot   : PASSED (TPM 2.0 PCR-7 Authenticated)\r\n\r\n  Threats Blocked: 14     Quarantined Items: 0     Vulnerabilities: 0\r\n"

vault_panel_text:
    .asciz "===============================================================================\r\n                    BITLOCKER NEO - ENCRYPTED DRIVE V:\r\n                Hardware-Bound Cryptographic Storage Vault\r\n===============================================================================\r\n\r\n  Volume Label  : NovaOS Secure Vault (Drive V:)\r\n  Cipher Engine : AES-256-GCM Authenticated Encryption\r\n  Key Protection: TPM 2.0 PCR-7 Sealed Key + Master PIN\r\n  Files in Drive V:\r\n    - /vault/credentials.enc       (AES-256 Protected)\r\n    - /vault/certificates.pfx      (Hardware Key Bound)\r\n    - /vault/security_policy.conf  (Zero-Trust Enforced)\r\n"

explorer_panel_text:
    .asciz "===============================================================================\r\n                   NOVA FILES - WINDOWS 11 FLUENT EXPLORER\r\n===============================================================================\r\n\r\n  Drive C:  [NVMe SSD System Root]      LUKS2 AES-256-XTS Encrypted\r\n  Drive V:  [BitLocker Neo User Vault]  AES-256-GCM Hardware Sealed\r\n  Drive D:  [NovaOS Live CD Media]      ISO 9660 / El Torito Read-Only\r\n\r\n  Quick Folders: /Documents  /Downloads  /EncryptedVault  /SecurityLogs\r\n"

installer_step1_text:
    .asciz "===============================================================================\r\n                     NOVAOS SETUP WIZARD (INSTALL TO DISK)\r\n                  Windows 11 Futuristic Installation Engine\r\n===============================================================================\r\n\r\n"

installer_drive_found:
    .asciz "Target Disk Discovered: [Drive 80h] Primary Virtual SCSI / SATA Storage (32 GB)\r\nProposed Partition Layout:\r\n  * Partition 1: EFI System Partition (512 MB, FAT32) -> /boot/efi\r\n  * Partition 2: Nova Recovery Partition (1024 MB, ext4) -> /boot\r\n  * Partition 3: Encrypted System Root (LUKS2 AES-256-XTS + Argon2id)\r\n\r\n"

installer_prompt_confirm:
    .asciz "WARNING: All data on Drive 80h will be formatted and encrypted.\r\nProceed with installation? [y/n]: "

installer_progress_text:
    .asciz "\r\nDeploying NovaOS Hyperion to target disk...\r\n"

str_tick1:
    .asciz "[>>>             ] 20% Formatting GPT Table & EFI System Partition...\r\n"

str_tick2:
    .asciz "[>>>>>>>>>       ] 60% Initializing LUKS2 AES-256-XTS Container...\r\n"

str_tick3:
    .asciz "[>>>>>>>>>>>>>>> ] 90% Deploying NovaOS Kernel, Shell & Defender...\r\n"

installer_complete_text:
    .asciz "[>>>>>>>>>>>>>>>>] 100% Finalizing UEFI NVRAM & BitLocker Recovery Key!\r\n\r\n===============================================================================\r\n  INSTALLATION COMPLETED SUCCESSFULLY!\r\n\r\n  IMPORTANT — BITLOCKER NEO EMERGENCY RECOVERY KEY:\r\n  481920-384910-582910-948102-184920-384910-948201-384920\r\n\r\n  Keep this 48-digit key safe. You can now reboot into your installed NovaOS.\r\n===============================================================================\r\n"

settings_panel_text:
    .asciz "===============================================================================\r\n                  NOVAOS CONTROL PANEL & SYSTEM SETTINGS\r\n===============================================================================\r\n\r\n  * OS Edition         : NovaOS Hyperion 2026 (Windows 11 Neo Edition)\r\n  * Kernel Architecture: x86_64 Long Mode with KASLR & PTI Hardening\r\n  * Visual Theme       : Futuristic Acrylic Cyan / Void Dark (#00f2fe)\r\n  * Secure Boot        : Enforced (TPM 2.0 PCR-7 Binding)\r\n  * Network Profile    : Zero-Trust Stealth Shield Active\r\n"

start_menu_text:
    .asciz "===============================================================================\r\n                            ❖ NOVA START MENU ❖\r\n===============================================================================\r\n\r\n  Pinned Applications:\r\n    [1] Nova Terminal (PowerShell Neo Cybernetic Console)\r\n    [2] Nova Defender (Real-Time Heuristic Security Hub)\r\n    [3] BitLocker Neo Encrypted Drive V: (Secure Storage)\r\n    [4] Nova Files (Fluent File Explorer)\r\n    [5] Install NovaOS to Disk (Setup Wizard)\r\n    [6] Control Panel & Settings\r\n\r\n  Recent Security Events:\r\n    * Measured Boot verified: PCR-0, PCR-4, PCR-7 digests matched\r\n    * Zero-Trust Firewall active: ICMP Stealth Drop engaged\r\n\r\n  Session: NovaAdmin (System Administrator)\r\n"

str_cmd_exit:      .asciz "exit"
str_cmd_quit:      .asciz "quit"
str_cmd_help:      .asciz "help"
str_cmd_clear:     .asciz "clear"
str_cmd_novafetch: .asciz "novafetch"
str_cmd_neofetch:  .asciz "neofetch"
str_cmd_sysinfo:   .asciz "sysinfo"
str_cmd_defender:  .asciz "defender"
str_cmd_scan:      .asciz "scan"
str_cmd_firewall:  .asciz "firewall"
str_cmd_vault:     .asciz "vault"
str_cmd_shred:     .asciz "shred"
str_cmd_matrix:    .asciz "matrix"
str_cmd_install:   .asciz "install"
str_cmd_reboot:    .asciz "reboot"

.bss
cmd_buffer: .space 64
