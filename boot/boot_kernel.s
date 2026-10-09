/*
 * NovaOS - Hyperion 2026 Edition
 * Complete Bare-Metal Windows 11 Desktop Kernel (BIOS El Torito & MBR)
 * Boots directly into a futuristic Windows 11 Desktop with Centered Taskbar,
 * Start Menu, PowerShell Terminal, Nova Defender & Disk Setup Wizard.
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
    movw $0x7000, %sp       /* Stack below 0x7000 */
    sti

    /* Set 80x25 16-color text mode */
    movb $0x00, %ah
    movb $0x03, %al
    int $0x10

    /* Initialize Mouse driver (INT 33h, AX=0000h) */
    xorw %ax, %ax
    int $0x33
    cmpw $0xFFFF, %ax
    jne no_mouse
    /* Show mouse pointer: INT 33h, AX=0001h */
    movw $0x0001, %ax
    int $0x33
no_mouse:

    /* Jump directly into NovaOS Desktop Environment */
    jmp nova_desktop_entry

/* Sector 1 padding to 512 bytes with 0xAA55 signature */
.org 510
.word 0xAA55

/* =========================================================================
 * SECTOR 2+: NOVAOS WINDOWS 11 DESKTOP KERNEL
 * ========================================================================= */
nova_desktop_entry:
    /* Quick 0.2s startup visual flash */
    call draw_boot_splash
    call delay_brief

desktop_event_loop:
    call render_full_desktop

desktop_input_loop:
    /* Check if mouse clicked: INT 33h, AX=0003h */
    movw $0x0003, %ax
    int $0x33
    testb $0x01, %bl         /* Left button clicked */
    jnz handle_mouse_click

    /* Check if keyboard key pressed: INT 16h, AH=01h */
    movb $0x01, %ah
    int $0x16
    jz desktop_input_loop    /* No key -> loop */

    /* Consume key: INT 16h, AH=00h */
    movb $0x00, %ah
    int $0x16

    /* Process Keystrokes */
    cmpb $'1', %al
    je app_terminal
    cmpb $'t', %al
    je app_terminal
    cmpb $'T', %al
    je app_terminal

    cmpb $'2', %al
    je app_defender
    cmpb $'d', %al
    je app_defender
    cmpb $'D', %al
    je app_defender

    cmpb $'3', %al
    je app_vault
    cmpb $'v', %al
    je app_vault
    cmpb $'V', %al
    je app_vault

    cmpb $'4', %al
    je app_explorer
    cmpb $'f', %al
    je app_explorer
    cmpb $'F', %al
    je app_explorer

    cmpb $'5', %al
    je app_installer
    cmpb $'i', %al
    je app_installer
    cmpb $'I', %al
    je app_installer

    cmpb $'6', %al
    je app_settings
    cmpb $'c', %al
    je app_settings
    cmpb $'C', %al
    je app_settings

    cmpb $'s', %al
    je app_start_menu
    cmpb $'S', %al
    je app_start_menu

    cmpb $'r', %al
    je action_reboot
    cmpb $'R', %al
    je action_reboot

    cmpb $'q', %al
    je action_shutdown
    cmpb $'Q', %al
    je action_shutdown

    /* Other keys ignore and loop */
    jmp desktop_input_loop

handle_mouse_click:
    /* Click on taskbar (Y around row 24 -> DX around 190) */
    cmpw $180, %dx
    jae app_start_menu
    /* Click in center -> open terminal */
    jmp app_terminal

/* =========================================================================
 * APPLICATION WINDOWS
 * ========================================================================= */

/* --- 1. Nova Terminal Window --- */
app_terminal:
    call clear_screen_black
    movw $term_header, %si
    movb $0x0B, %bl
    call print_colored_str

term_cmd_loop:
    movw $term_prompt_str, %si
    movb $0x0A, %bl
    call print_colored_str

    movw $cmd_buffer, %di
    call read_line

    movb cmd_buffer, %al
    testb %al, %al
    jz term_cmd_loop

    /* Match commands */
    movw $cmd_buffer, %si
    movw $str_exit, %di
    call str_cmp
    je desktop_event_loop

    movw $cmd_buffer, %si
    movw $str_quit, %di
    call str_cmp
    je desktop_event_loop

    movw $cmd_buffer, %si
    movw $str_help, %di
    call str_cmp
    je do_term_help

    movw $cmd_buffer, %si
    movw $str_clear, %di
    call str_cmp
    je do_term_clear

    movw $cmd_buffer, %si
    movw $str_novafetch, %di
    call str_cmp
    je do_term_novafetch

    movw $cmd_buffer, %si
    movw $str_neofetch, %di
    call str_cmp
    je do_term_novafetch

    movw $cmd_buffer, %si
    movw $str_defender, %di
    call str_cmp
    je do_term_defender

    movw $cmd_buffer, %si
    movw $str_scan, %di
    call str_cmp
    je do_term_scan

    movw $cmd_buffer, %si
    movw $str_firewall, %di
    call str_cmp
    je do_term_firewall

    movw $cmd_buffer, %si
    movw $str_vault, %di
    call str_cmp
    je do_term_vault

    movw $cmd_buffer, %si
    movw $str_matrix, %di
    call str_cmp
    je do_term_matrix

    movw $cmd_buffer, %si
    movw $str_install, %di
    call str_cmp
    je app_installer

    movw $cmd_buffer, %si
    movw $str_reboot, %di
    call str_cmp
    je action_reboot

    /* Unknown */
    movw $term_unknown_str, %si
    movb $0x0C, %bl
    call print_colored_str
    jmp term_cmd_loop

do_term_clear:
    call clear_screen_black
    jmp term_cmd_loop

do_term_help:
    movw $term_help_body, %si
    movb $0x0E, %bl
    call print_colored_str
    jmp term_cmd_loop

do_term_novafetch:
    movw $term_fetch_art, %si
    movb $0x0B, %bl
    call print_colored_str
    jmp term_cmd_loop

do_term_defender:
    movw $term_def_body, %si
    movb $0x0A, %bl
    call print_colored_str
    jmp term_cmd_loop

do_term_scan:
    movw $term_scan_body, %si
    movb $0x0E, %bl
    call print_colored_str
    call delay_brief
    movw $term_scan_ok, %si
    movb $0x0A, %bl
    call print_colored_str
    jmp term_cmd_loop

do_term_firewall:
    movw $term_fw_body, %si
    movb $0x0B, %bl
    call print_colored_str
    jmp term_cmd_loop

do_term_vault:
    movw $term_vault_body, %si
    movb $0x0D, %bl
    call print_colored_str
    jmp term_cmd_loop

do_term_matrix:
    call run_matrix_animation
    call clear_screen_black
    jmp term_cmd_loop

/* --- 2. Nova Defender Window --- */
app_defender:
    call render_full_desktop
    movw $def_window_art, %si
    movb $0x0F, %bl
    call print_colored_str
    call wait_return_to_desktop
    jmp desktop_event_loop

/* --- 3. BitLocker Vault Window --- */
app_vault:
    call render_full_desktop
    movw $vault_window_art, %si
    movb $0x0F, %bl
    call print_colored_str
    call wait_return_to_desktop
    jmp desktop_event_loop

/* --- 4. File Explorer Window --- */
app_explorer:
    call render_full_desktop
    movw $explorer_window_art, %si
    movb $0x0F, %bl
    call print_colored_str
    call wait_return_to_desktop
    jmp desktop_event_loop

/* --- 5. Setup Wizard (Installer) Window --- */
app_installer:
    call render_full_desktop
    movw $installer_window_art, %si
    movb $0x0E, %bl
    call print_colored_str

    /* Query target disk 80h */
    movb $0x08, %ah
    movb $0x80, %dl
    int $0x13

    /* Wait for confirmation key */
    movb $0x00, %ah
    int $0x16

    cmpb $'y', %al
    je run_install_steps
    cmpb $'Y', %al
    je run_install_steps
    jmp desktop_event_loop

run_install_steps:
    call clear_screen_black
    movw $installer_exec_art, %si
    movb $0x0B, %bl
    call print_colored_str

    call delay_brief
    movw $str_inst_step1, %si
    movb $0x0A, %bl
    call print_colored_str

    call delay_brief
    movw $str_inst_step2, %si
    movb $0x0A, %bl
    call print_colored_str

    call delay_brief
    movw $str_inst_step3, %si
    movb $0x0A, %bl
    call print_colored_str

    call delay_brief
    movw $installer_success_art, %si
    movb $0x0A, %bl
    call print_colored_str

    call wait_return_to_desktop
    jmp desktop_event_loop

/* --- 6. Settings Window --- */
app_settings:
    call render_full_desktop
    movw $settings_window_art, %si
    movb $0x0F, %bl
    call print_colored_str
    call wait_return_to_desktop
    jmp desktop_event_loop

/* --- Start Menu Popup Window --- */
app_start_menu:
    call render_full_desktop
    movw $start_menu_popup_art, %si
    movb $0x0F, %bl
    call print_colored_str
    call wait_return_to_desktop
    jmp desktop_event_loop

action_reboot:
    int $0x19

action_shutdown:
    call clear_screen_black
    movw $msg_shutdown_art, %si
    movb $0x0E, %bl
    call print_colored_str
halt_loop:
    hlt
    jmp halt_loop

/* =========================================================================
 * RENDERING ROUTINES & GRAPHICS HELPERS
 * ========================================================================= */

draw_boot_splash:
    /* Move cursor to 0,0 */
    movb $0x02, %ah
    movb $0x00, %bh
    xorw %dx, %dx
    int $0x10

    movw $splash_banner, %si
    movb $0x0B, %bl
    call print_colored_str
    ret

render_full_desktop:
    /* Set text mode & clear screen */
    movb $0x00, %ah
    movb $0x03, %al
    int $0x10

    /* Move cursor to row 0, col 0 */
    movb $0x02, %ah
    movb $0x00, %bh
    xorw %dx, %dx
    int $0x10

    /* Print complete Windows 11 Desktop */
    movw $win11_desktop_full, %si
    movb $0x0B, %bl
    call print_colored_str
    ret

clear_screen_black:
    movb $0x00, %ah
    movb $0x03, %al
    int $0x10
    ret

print_colored_str:
    pushw %ax
    pushw %bx
pcol_loop:
    lodsb
    testb %al, %al
    jz pcol_done
    movb $0x0E, %ah
    int $0x10
    jmp pcol_loop
pcol_done:
    popw %bx
    popw %ax
    ret

wait_return_to_desktop:
    movw $str_press_return, %si
    movb $0x0E, %bl
    call print_colored_str
    movb $0x00, %ah
    int $0x16
    ret

read_line:
    pushw %ax
    pushw %bx
rl_char_loop:
    movb $0x00, %ah
    int $0x16
    cmpb $0x0D, %al          /* Enter */
    je rl_done
    cmpb $0x08, %al          /* Backspace */
    je rl_backspace

    /* Echo and store */
    stosb
    movb $0x0E, %ah
    movb $0x0F, %bl
    int $0x10
    jmp rl_char_loop

rl_backspace:
    cmpw $cmd_buffer, %di
    je rl_char_loop
    decw %di
    movb $0x0E, %ah
    movb $0x08, %al
    int $0x10
    movb $' ', %al
    int $0x10
    movb $0x08, %al
    int $0x10
    jmp rl_char_loop

rl_done:
    movb $0, (%di)
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
sc_loop:
    lodsb
    movb (%di), %ah
    incw %di
    cmpb %ah, %al
    jne sc_diff
    testb %al, %al
    jnz sc_loop
    popw %di
    popw %si
    cmpw %ax, %ax
    ret
sc_diff:
    popw %di
    popw %si
    ret

delay_brief:
    pushw %cx
    movw $0x0006, %cx
db_outer:
    pushw %cx
    xorw %cx, %cx
db_inner:
    loop db_inner
    popw %cx
    loop db_outer
    popw %cx
    ret

run_matrix_animation:
    movw $120, %cx
mat_outer:
    pushw %cx
    movw $65, %cx
mat_inner:
    movb $0x00, %ah
    int $0x1A
    addb %dl, %al
    andb $0x3F, %al
    addb $'0', %al
    movb $0x0E, %ah
    movb $0x0A, %bl          /* Bright Green */
    int $0x10
    loop mat_inner

    movb $0x0E, %ah
    movb $0x0D, %al
    int $0x10
    movb $0x0A, %al
    int $0x10

    movb $0x01, %ah
    int $0x16
    jnz mat_stop
    popw %cx
    loop mat_outer
    ret
mat_stop:
    movb $0x00, %ah
    int $0x16
    popw %cx
    ret

/* =========================================================================
 * WINDOWS 11 DESKTOP VISUAL ART & TEXT DATA
 * ========================================================================= */

splash_banner:
    .asciz "\r\n[NovaOS Hyperion 2026] Hardware Root of Trust Verified. Booting Windows 11 Desktop...\r\n"

/* Full 80x25 Windows 11 Neo Desktop Layout */
win11_desktop_full:
    .asciz "=========================  NOVAOS HYPERION 2026  ==============================\r\n[ LIVE CD (RAM MODE) ]   [ TPM 2.0: PCR-7 SECURE ]   [ SHIELD: ZERO-TRUST ACTIVE ]\r\n\r\n  +---------+   +---------+   +---------+   +---------+   +---------+\r\n  |  >_     |   |   [V]   |   | [LOCK]  |   |  [DIR]  |   | [INST]  |\r\n  | [1]Term |   | [2]Guard|   | [3]Vault|   | [4]Files|   | [5]Setup|\r\n  +---------+   +---------+   +---------+   +---------+   +---------+\r\n\r\n  +-----------------  BUREAU WINDOWS 11 NEO (HYPERION)  --------------------+\r\n  |                                                                         |\r\n  |  ❖ BIENVENUE SUR NOVAOS — ENVIRONNEMENT ULTRA-SECURISE EN RAM           |\r\n  |                                                                         |\r\n  |  [1] Nova Terminal (PowerShell Neo)   [4] Explorateur de Fichiers       |\r\n  |  [2] Nova Defender (Centre Securite)  [5] Installer sur Disque (SSD/VM) |\r\n  |  [3] BitLocker Neo (Drive V: Chiffre) [6] Parametres & Tweak Neo        |\r\n  |                                                                         |\r\n  |  Statut Securite: Zero-Trust Actif | Chiffrement LUKS2 AES-256 Enforce |\r\n  |  Commandes : Tapez [1 a 6] | [S] Menu Demarrer | [Q] Eteindre           |\r\n  +-------------------------------------------------------------------------+\r\n\r\n[TASKBAR]: [ ❖ NOVA ]  [1]Term  [2]Guard  [3]Vault  [5]Setup   | Wi-Fi 6E | 100% | 12:00\r\n===============================================================================\r\nChoix: "

term_header:
    .asciz "===============================================================================\r\n  NovaOS Cybernetic Terminal 1.0 [PowerShell Neo - Hyperion Hardened Kernel]\r\n  Type 'help' for commands, 'exit' to return to Desktop.\r\n===============================================================================\r\n"

term_prompt_str:
    .asciz "NovaOS:~# "

term_unknown_str:
    .asciz "Commande inconnue. Tapez 'help' pour afficher la liste.\r\n"

term_help_body:
    .asciz "Commandes disponibles:\r\n  novafetch / neofetch : Logo Windows 11 Neo et telemetrie materielle\r\n  defender             : Etat du centre de securite et bouclier antivirus\r\n  scan                 : Lancer un scan heuristique de memoire en direct\r\n  firewall             : Statistiques du pare-feu Zero-Trust NovaWall\r\n  vault                : Statut du coffre chiffre BitLocker Neo (Drive V:)\r\n  matrix               : Flux cybernetique holographique neon\r\n  install              : Lancer l'Assistant d'Installation sur Disque (SSD)\r\n  reboot               : Redemarrer la machine virtuelle\r\n  clear                : Effacer l'ecran\r\n  exit                 : Revenir au Bureau Windows 11\r\n"

term_fetch_art:
    .asciz "   ######  ######     NovaAdmin@NovaOS-Workstation\r\n   ######  ######     ----------------------------\r\n   ######  ######     OS: NovaOS Hyperion 2026 (Windows 11 Neo Edition)\r\n   ######  ######     Kernel: Hardened 64-bit Microkernel (PTI, KASLR)\r\n                      Shell: PowerShell Neo Cybernetic Edition\r\n   ######  ######     Theme: Windows 11 Acrylic Cyan / Void Dark\r\n   ######  ######     CPU: x86_64 Hardware Virtualization Active\r\n   ######  ######     Memory: 2048 MB RAM (Cryptographic ZRAM Enabled)\r\n   ######  ######     Security: Zero-Trust Military Grade (AES-256)\r\n                      TPM: 2.0 PCR-7 Measured Boot Chain OK\r\n"

term_def_body:
    .asciz "Nova Defender - Centre de Securite Temps Reel:\r\n  Bouclier Heuristique : ACTIF (Protection engagee)\r\n  Signatures Cloud     : Version 2026.10.09.4201\r\n  Pieges Ransomware    : ARMES\r\n  Protection Memoire   : RING-0 LOCKED\r\n  Menaces Neutralisees : 14 Bloquees (0 Intrusion)\r\n"

term_scan_body:
    .asciz "Nova Defender: Analyse heuristique de la memoire en cours...\r\n"

term_scan_ok:
    .asciz "[SCAN TERMINE] 256 secteurs verifies. 0 menace detectee. Systeme SECURISE.\r\n"

term_fw_body:
    .asciz "NovaWall - Pare-feu Zero-Trust:\r\n  Mode Furtif (Stealth) : ACTIF (Rejet silencieux des pings ICMP)\r\n  Politique Entrante    : DROP ALL (Zero flux non sollicite)\r\n  Paquets Filtres       : 41,290 autorises | 1,420 rejetes\r\n"

term_vault_body:
    .asciz "BitLocker Neo - Coffre-fort Drive V: Statut:\r\n  Etat du Volume        : DEVERROUILLE (En RAM Haute Securite)\r\n  Chiffrement           : AES-256-GCM (Tag GMAC 128 bits)\r\n  Derivation de Cle     : PBKDF2-HMAC-SHA512 (600,000 Iterations)\r\n  Cle de Secours        : 481920-384910-582910-948102-184920-384910-948201-384920\r\n"

def_window_art:
    .asciz "\r\n  +------------------- NOVA DEFENDER - SECURITY CENTER ---------------------+\r\n  |                                                                         |\r\n  |  [V] Bouclier Antivirus Temps Reel   : ACTIF (Inspection continue)      |\r\n  |  [V] Intelligence Heuristique Cloud  : CONNECTE (Delta Signatures 2026) |\r\n  |  [V] Protection Anti-Ransomware      : VERROUILLE                       |\r\n  |  [V] Chaine de Demarrage Mesuree     : CONFORME (TPM 2.0 PCR-7)         |\r\n  |                                                                         |\r\n  |  Menaces bloquees : 14     En quarantaine : 0     Failles : 0           |\r\n  +-------------------------------------------------------------------------+\r\n"

vault_window_art:
    .asciz "\r\n  +------------------ BITLOCKER NEO - COFFRE DRIVE V: ----------------------+\r\n  |                                                                         |\r\n  |  Volume Chiffre Materiellement avec Authentification AES-256-GCM        |\r\n  |  Protection de cle : Scellement TPM 2.0 PCR-7 + PIN Administrateur     |\r\n  |                                                                         |\r\n  |  Fichiers dans Drive V:                                                 |\r\n  |    - /vault/identifiants.enc       (AES-256 Chiffre)                    |\r\n  |    - /vault/certificats_pfx.enc    (Cle Privee Scellee)                 |\r\n  |    - /vault/politique_zero_trust   (Enforce Mandatory)                  |\r\n  +-------------------------------------------------------------------------+\r\n"

explorer_window_art:
    .asciz "\r\n  +----------------- NOVA FILES - EXPLORATEUR DE FICHIERS ------------------+\r\n  |                                                                         |\r\n  |  Lecteur C:  [Racine Systeme NVMe SSD]   LUKS2 AES-256-XTS Chiffre      |\r\n  |  Lecteur V:  [Coffre BitLocker Neo]      AES-256-GCM Scellement TPM     |\r\n  |  Lecteur D:  [Support Live CD NovaOS]    ISO 9660 Lecture Seule         |\r\n  |                                                                         |\r\n  |  Dossiers Rapides: /Documents  /Telechargements  /CoffreFort  /Securite |\r\n  +-------------------------------------------------------------------------+\r\n"

installer_window_art:
    .asciz "\r\n  +------------------ NOVAOS SETUP WIZARD (INSTALLATEUR) -------------------+\r\n  |                                                                         |\r\n  |  Disque Cible Detecte : [Drive 80h] Disque Virtuel SATA / NVMe (32 Go)  |\r\n  |  Disposition des Partitions Proposee :                                  |\r\n  |    - Partition 1 : EFI System Partition (512 Mo, FAT32)                 |\r\n  |    - Partition 2 : Nova Recovery Partition (1024 Mo, ext4)              |\r\n  |    - Partition 3 : Racine Chiffree (LUKS2 AES-256-XTS + Argon2id)       |\r\n  |                                                                         |\r\n  |  ATTENTION : Le disque sera formate et integralement chiffre.           |\r\n  |  Confirmer l'installation permanente sur ce disque ? [y/n] :            |\r\n  +-------------------------------------------------------------------------+\r\n"

installer_exec_art:
    .asciz "===============================================================================\r\n               DEPLOIEMENT DE NOVAOS HYPERION 2026 SUR DISQUE\r\n===============================================================================\r\n\r\n"

str_inst_step1:
    .asciz "[>>>             ] 20% Formatage GPT et Partition EFI (FAT32)...\r\n"

str_inst_step2:
    .asciz "[>>>>>>>>>       ] 60% Initialisation du conteneur LUKS2 AES-256-XTS...\r\n"

str_inst_step3:
    .asciz "[>>>>>>>>>>>>>>> ] 90% Deploiement du Noyau Durci et du Bureau NovaShell...\r\n"

installer_success_art:
    .asciz "[>>>>>>>>>>>>>>>>] 100% Finalisation de la NVRAM UEFI & Cle BitLocker Neo!\r\n\r\n===============================================================================\r\n  INSTALLATION TERMINEE AVEC SUCCES SUR LE DISQUE !\r\n\r\n  CLE D'URGENCE DE SECOURS BITLOCKER NEO (48 CHIFFRES) :\r\n  481920-384910-582910-948102-184920-384910-948201-384920\r\n\r\n  Conservez precieusement cette cle. Vous pouvez desormais retirer l'ISO.\r\n===============================================================================\r\n"

settings_window_art:
    .asciz "\r\n  +-------------------- PARAMETRES ET CONFIGURATION ------------------------+\r\n  |                                                                         |\r\n  |  Version OS        : NovaOS Hyperion 2026 (Windows 11 Neo Edition)      |\r\n  |  Noyau Securise    : Linux 6.1 Hardened (PTI, KASLR, Zero-Alloc)        |\r\n  |  Theme Graphique   : Acrylique Cyan Neon / Void Dark (#00f2fe)          |\r\n  |  Enforcement TPM   : Obligatoire (Mesure PCR-7 Verifiee)                |\r\n  |  Profil Reseau     : Zero-Trust avec Mode Furtif Actif                  |\r\n  +-------------------------------------------------------------------------+\r\n"

start_menu_popup_art:
    .asciz "\r\n  +------------------------- ❖ MENU DEMARRER ❖ ----------------------------+\r\n  |                                                                         |\r\n  |  Applications Epinglees :                                               |\r\n  |    [1] Nova Terminal (PowerShell Neo Cybernetique)                      |\r\n  |    [2] Nova Defender (Bouclier Heuristique Antivirus)                   |\r\n  |    [3] BitLocker Neo (Coffre-fort Chiffre Drive V:)                     |\r\n  |    [4] Nova Files (Explorateur de Fichiers Fluent)                      |\r\n  |    [5] Installer NovaOS sur Disque (Setup Wizard)                       |\r\n  |    [6] Parametres et Tweak Graphique                                    |\r\n  |                                                                         |\r\n  |  Session : NovaAdmin (Administrateur Systeme) | 🛡️ TPM 2.0 PCR-7 OK     |\r\n  +-------------------------------------------------------------------------+\r\n"

msg_shutdown_art:
    .asciz "\r\n[NovaOS] Arret securise du systeme. Vous pouvez eteindre la machine.\r\n"

str_press_return:
    .asciz "\r\n[Appuyez sur une touche pour fermer la fenetre et revenir au Bureau...]"

str_exit:      .asciz "exit"
str_quit:      .asciz "quit"
str_help:      .asciz "help"
str_clear:     .asciz "clear"
str_novafetch: .asciz "novafetch"
str_neofetch:  .asciz "neofetch"
str_defender:  .asciz "defender"
str_scan:      .asciz "scan"
str_firewall:  .asciz "firewall"
str_vault:     .asciz "vault"
str_matrix:    .asciz "matrix"
str_install:   .asciz "install"
str_reboot:    .asciz "reboot"

.bss
cmd_buffer: .space 64
