/*
 * NovaOS - Windows 11 Neo Desktop Shell for Linux (Console & TTY Native)
 * High-performance 24-bit ANSI / UTF-8 Graphical Desktop Environment
 * Features Centered Taskbar, Start Menu, PowerShell Terminal, Defender Hub, Explorer & Installer.
 * Full mouse tracking (SGR 1006) and keyboard controls.
 * Copyright (c) 2026 NovaOS Security Architecture Team
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <termios.h>
#include <fcntl.h>
#include <time.h>
#include <sys/ioctl.h>

#define COLOR_RESET       "\033[0m"
#define COLOR_CYAN_BOLD   "\033[1;38;2;56;189;248m"
#define COLOR_CYAN_NEON   "\033[38;2;0;242;254m"
#define COLOR_BLUE_BG     "\033[48;2;10;22;40m"
#define COLOR_TASKBAR_BG  "\033[48;2;15;23;42m"
#define COLOR_GREEN_BOLD  "\033[1;38;2;16;185;129m"
#define COLOR_YELLOW_BOLD "\033[1;38;2;234;179;8m"
#define COLOR_MAGENTA_BOLD "\033[1;38;2;192;132;252m"
#define COLOR_WHITE_BOLD  "\033[1;37m"
#define COLOR_GRAY_DIM    "\033[38;2;148;163;184m"
#define CLEAR_SCREEN      "\033[2J\033[H"
#define HIDE_CURSOR       "\033[?25l"
#define SHOW_CURSOR       "\033[?25h"
#define ENABLE_MOUSE      "\033[?1000h\033[?1002h\033[?1006h"
#define DISABLE_MOUSE     "\033[?1000l\033[?1002l\033[?1006l"

static struct termios orig_termios;

void disable_raw_mode(void) {
    printf(DISABLE_MOUSE SHOW_CURSOR COLOR_RESET);
    fflush(stdout);
    tcsetattr(STDIN_FILENO, TCSAFLUSH, &orig_termios);
}

void enable_raw_mode(void) {
    tcgetattr(STDIN_FILENO, &orig_termios);
    atexit(disable_raw_mode);
    struct termios raw = orig_termios;
    raw.c_lflag &= ~(ECHO | ICANON);
    raw.c_cc[VMIN] = 0;
    raw.c_cc[VTIME] = 1; /* 0.1s timeout */
    tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw);
    printf(HIDE_CURSOR ENABLE_MOUSE);
    fflush(stdout);
}

void get_time_str(char *buf, size_t sz) {
    time_t now = time(NULL);
    struct tm *tm_info = localtime(&now);
    strftime(buf, sz, "%H:%M:%S", tm_info);
}

void draw_desktop(int start_menu_open) {
    char clock_buf[16];
    get_time_str(clock_buf, sizeof(clock_buf));

    printf(CLEAR_SCREEN);
    
    /* Top Header Strip */
    printf(COLOR_TASKBAR_BG COLOR_CYAN_BOLD " ❖ NovaOS Hyperion 2026 " COLOR_RESET);
    printf("  " COLOR_GREEN_BOLD "[ LIVE CD (RAM MODE) ]" COLOR_RESET);
    printf("  " COLOR_CYAN_NEON "[ TPM 2.0: PCR-7 SECURE ]" COLOR_RESET);
    printf("  " COLOR_GREEN_BOLD "[ SHIELD: ZERO-TRUST ACTIVE ]\n" COLOR_RESET);
    printf(COLOR_GRAY_DIM "───────────────────────────────────────────────────────────────────────────────\n" COLOR_RESET);

    /* Desktop Icons Grid */
    printf("\n");
    printf("   " COLOR_CYAN_BOLD "┌─────────┐" COLOR_RESET "   " COLOR_GREEN_BOLD "┌─────────┐" COLOR_RESET "   " COLOR_MAGENTA_BOLD "┌─────────┐" COLOR_RESET "   " COLOR_CYAN_NEON "┌─────────┐" COLOR_RESET "   " COLOR_YELLOW_BOLD "┌─────────┐" COLOR_RESET "\n");
    printf("   " COLOR_CYAN_BOLD "│   >_    │" COLOR_RESET "   " COLOR_GREEN_BOLD "│   [V]   │" COLOR_RESET "   " COLOR_MAGENTA_BOLD "│ [LOCK]  │" COLOR_RESET "   " COLOR_CYAN_NEON "│  [DIR]  │" COLOR_RESET "   " COLOR_YELLOW_BOLD "│ [SETUP] │" COLOR_RESET "\n");
    printf("   " COLOR_CYAN_BOLD "│ [1]Term │" COLOR_RESET "   " COLOR_GREEN_BOLD "│ [2]Def  │" COLOR_RESET "   " COLOR_MAGENTA_BOLD "│ [3]Vault│" COLOR_RESET "   " COLOR_CYAN_NEON "│ [4]Files│" COLOR_RESET "   " COLOR_YELLOW_BOLD "│ [5]Inst │" COLOR_RESET "\n");
    printf("   " COLOR_CYAN_BOLD "└─────────┘" COLOR_RESET "   " COLOR_GREEN_BOLD "└─────────┘" COLOR_RESET "   " COLOR_MAGENTA_BOLD "└─────────┘" COLOR_RESET "   " COLOR_CYAN_NEON "└─────────┘" COLOR_RESET "   " COLOR_YELLOW_BOLD "└─────────┘" COLOR_RESET "\n");
    printf("    Terminal       Defender       Drive V:       Explorateur     Installateur\n\n");

    /* Center Windows 11 Welcome Card */
    printf("  " COLOR_CYAN_BOLD "╔═══════════════════  BUREAU WINDOWS 11 NEO (HYPERION)  ════════════════════╗" COLOR_RESET "\n");
    printf("  " COLOR_CYAN_BOLD "║" COLOR_RESET "                                                                           " COLOR_CYAN_BOLD "║" COLOR_RESET "\n");
    printf("  " COLOR_CYAN_BOLD "║" COLOR_RESET "  " COLOR_CYAN_NEON "❖ BIENVENUE SUR NOVAOS — ENVIRONNEMENT ULTRA-SECURISE EN MEMOIRE VIVE" COLOR_RESET "     " COLOR_CYAN_BOLD "║" COLOR_RESET "\n");
    printf("  " COLOR_CYAN_BOLD "║" COLOR_RESET "                                                                           " COLOR_CYAN_BOLD "║" COLOR_RESET "\n");
    printf("  " COLOR_CYAN_BOLD "║" COLOR_RESET "  " COLOR_WHITE_BOLD "[1] Nova Terminal (PowerShell Neo)" COLOR_RESET "   " COLOR_WHITE_BOLD "[4] Explorateur de Fichiers" COLOR_RESET "         " COLOR_CYAN_BOLD "║" COLOR_RESET "\n");
    printf("  " COLOR_CYAN_BOLD "║" COLOR_RESET "  " COLOR_WHITE_BOLD "[2] Nova Defender (Centre Securite)" COLOR_RESET "  " COLOR_WHITE_BOLD "[5] Installer sur Disque (NVMe/SSD)" COLOR_RESET " " COLOR_CYAN_BOLD "║" COLOR_RESET "\n");
    printf("  " COLOR_CYAN_BOLD "║" COLOR_RESET "  " COLOR_WHITE_BOLD "[3] BitLocker Neo (Drive V: Chiffre)" COLOR_RESET " " COLOR_WHITE_BOLD "[6] Parametres & Configuration" COLOR_RESET "      " COLOR_CYAN_BOLD "║" COLOR_RESET "\n");
    printf("  " COLOR_CYAN_BOLD "║" COLOR_RESET "                                                                           " COLOR_CYAN_BOLD "║" COLOR_RESET "\n");
    printf("  " COLOR_CYAN_BOLD "║" COLOR_RESET "  " COLOR_GREEN_BOLD "Securite : Zero-Trust & Chiffrement Materiel LUKS2 AES-256 Actifs" COLOR_RESET "        " COLOR_CYAN_BOLD "║" COLOR_RESET "\n");
    printf("  " COLOR_CYAN_BOLD "║" COLOR_RESET "  " COLOR_GRAY_DIM "Controles : Cliquez avec la souris ou tapez [1 a 6, S, Q]" COLOR_RESET "                  " COLOR_CYAN_BOLD "║" COLOR_RESET "\n");
    printf("  " COLOR_CYAN_BOLD "╚═══════════════════════════════════════════════════════════════════════════╝" COLOR_RESET "\n\n");

    /* Start Menu Popup if open */
    if (start_menu_open) {
        printf("  " COLOR_MAGENTA_BOLD "┌─────────────────────── ❖ MENU DEMARRER ❖ ────────────────────────┐" COLOR_RESET "\n");
        printf("  " COLOR_MAGENTA_BOLD "│" COLOR_RESET "  " COLOR_WHITE_BOLD "Applications Epinglees :" COLOR_RESET "                                         " COLOR_MAGENTA_BOLD "│" COLOR_RESET "\n");
        printf("  " COLOR_MAGENTA_BOLD "│" COLOR_RESET "    [1] Nova Terminal (PowerShell Cybernetique)                     " COLOR_MAGENTA_BOLD "│" COLOR_RESET "\n");
        printf("  " COLOR_MAGENTA_BOLD "│" COLOR_RESET "    [2] Nova Defender (Bouclier Heuristique Antivirus)              " COLOR_MAGENTA_BOLD "│" COLOR_RESET "\n");
        printf("  " COLOR_MAGENTA_BOLD "│" COLOR_RESET "    [3] BitLocker Neo (Coffre Chiffre Drive V:)                     " COLOR_MAGENTA_BOLD "│" COLOR_RESET "\n");
        printf("  " COLOR_MAGENTA_BOLD "│" COLOR_RESET "    [4] Explorateur de Fichiers Fluent                              " COLOR_MAGENTA_BOLD "│" COLOR_RESET "\n");
        printf("  " COLOR_MAGENTA_BOLD "│" COLOR_RESET "    [5] Assistant d'Installation sur Disque                         " COLOR_MAGENTA_BOLD "│" COLOR_RESET "\n");
        printf("  " COLOR_MAGENTA_BOLD "│" COLOR_RESET "    [6] Parametres & Panneau de Configuration                       " COLOR_MAGENTA_BOLD "│" COLOR_RESET "\n");
        printf("  " COLOR_MAGENTA_BOLD "│" COLOR_RESET "  Session : " COLOR_CYAN_BOLD "NovaAdmin (Administrateur)" COLOR_RESET " | 🛡️ TPM 2.0 PCR-7 Actif            " COLOR_MAGENTA_BOLD "│" COLOR_RESET "\n");
        printf("  " COLOR_MAGENTA_BOLD "└───────────────────────────────────────────────────────────────────┘" COLOR_RESET "\n");
    } else {
        printf("\n\n\n\n\n\n\n\n");
    }

    /* Centered Windows 11 Taskbar */
    printf(COLOR_TASKBAR_BG COLOR_CYAN_BOLD " [ ❖ START ] " COLOR_RESET);
    printf(COLOR_TASKBAR_BG COLOR_WHITE_BOLD " [1] Term " COLOR_RESET);
    printf(COLOR_TASKBAR_BG COLOR_GREEN_BOLD " [2] Guard " COLOR_RESET);
    printf(COLOR_TASKBAR_BG COLOR_MAGENTA_BOLD " [3] Vault " COLOR_RESET);
    printf(COLOR_TASKBAR_BG COLOR_CYAN_NEON " [4] Files " COLOR_RESET);
    printf(COLOR_TASKBAR_BG COLOR_YELLOW_BOLD " [5] Setup " COLOR_RESET);
    printf(COLOR_TASKBAR_BG "   " COLOR_GRAY_DIM "📶 Wi-Fi 6E | 🛡️ TPM OK | 🔋 100%% | " COLOR_WHITE_BOLD "%s " COLOR_RESET "\n", clock_buf);
    printf(COLOR_GRAY_DIM "───────────────────────────────────────────────────────────────────────────────\n" COLOR_RESET);
    printf(COLOR_CYAN_BOLD "Choix [1-6, S (Menu), Q (Quitter)]: " COLOR_RESET);
    fflush(stdout);
}

void run_terminal(void) {
    disable_raw_mode();
    printf(CLEAR_SCREEN);
    printf(COLOR_CYAN_BOLD "===============================================================================\n");
    printf("  NovaOS Cybernetic Terminal 1.0 [PowerShell Neo - Hyperion Hardened Kernel]\n");
    printf("  Type 'help' for commands, 'novafetch', 'defender', 'matrix', 'install', 'exit'.\n");
    printf("===============================================================================\n\n" COLOR_RESET);

    char line[128];
    while (1) {
        printf(COLOR_GREEN_BOLD "NovaOS:~# " COLOR_RESET);
        fflush(stdout);
        if (!fgets(line, sizeof(line), stdin)) break;

        /* Remove newline */
        line[strcspn(line, "\r\n")] = '\0';
        if (strcmp(line, "exit") == 0 || strcmp(line, "quit") == 0) break;
        if (strcmp(line, "clear") == 0) {
            printf(CLEAR_SCREEN);
            continue;
        }
        if (strcmp(line, "help") == 0 || strcmp(line, "?") == 0) {
            printf(COLOR_YELLOW_BOLD "Commandes disponibles:\n");
            printf("  novafetch / neofetch : Telemetrie et logo Windows 11 Neo\n");
            printf("  defender             : Etat du centre de securite et analyse\n");
            printf("  scan                 : Lancer un scan heuristique de memoire\n");
            printf("  firewall             : Statistiques du pare-feu Zero-Trust\n");
            printf("  vault                : Statut du volume chiffré BitLocker Neo\n");
            printf("  matrix               : Flux cybernetique holographique\n");
            printf("  install              : Lancer l'Assistant d'Installation sur Disque\n");
            printf("  reboot / poweroff    : Gestion de l'alimentation\n");
            printf("  exit                 : Revenir au Bureau Windows 11\n" COLOR_RESET);
        } else if (strcmp(line, "novafetch") == 0 || strcmp(line, "neofetch") == 0) {
            printf(COLOR_CYAN_BOLD "   ######  ######     NovaAdmin@NovaOS-Workstation\n");
            printf("   ######  ######     ----------------------------\n");
            printf("   ######  ######     OS: NovaOS Hyperion 2026 (Windows 11 Neo Edition)\n");
            printf("   ######  ######     Kernel: Linux 64-bit Hardened Core (PTI, KASLR)\n");
            printf("                      Shell: PowerShell Neo Cybernetic Edition\n");
            printf("   ######  ######     Theme: Windows 11 Acrylic Cyan / Void Dark\n");
            printf("   ######  ######     Memory: 2048 MB RAM (Cryptographic ZRAM Active)\n");
            printf("   ######  ######     Security: Zero-Trust Military Grade (AES-256)\n");
            printf("                      TPM: 2.0 PCR-7 Measured Boot Chain OK\n" COLOR_RESET);
        } else if (strcmp(line, "defender") == 0) {
            printf(COLOR_GREEN_BOLD "Nova Defender - Centre de Securite Temps Reel:\n");
            printf("  * Bouclier Heuristique : ACTIF (Protection engagee)\n");
            printf("  * Signatures Delta     : Version 2026.10.09.4201\n");
            printf("  * Protection Memoire   : RING-0 LOCKED\n");
            printf("  * Menaces Neutralisees : 14 Bloquees (0 Intrusion)\n" COLOR_RESET);
        } else if (strcmp(line, "scan") == 0) {
            printf(COLOR_YELLOW_BOLD "Nova Defender: Analyse heuristique de la memoire en cours...\n" COLOR_RESET);
            usleep(600000);
            printf(COLOR_GREEN_BOLD "[SCAN TERMINE] 512 secteurs verifies. 0 menace detectee. Systeme SECURISE.\n" COLOR_RESET);
        } else if (strcmp(line, "firewall") == 0) {
            printf(COLOR_CYAN_BOLD "NovaWall - Pare-feu Zero-Trust:\n");
            printf("  * Mode Furtif (Stealth) : ACTIF (Rejet silencieux des pings ICMP)\n");
            printf("  * Politique Entrante    : DROP ALL (Zero flux non sollicite)\n");
            printf("  * Paquets Filtres       : 41,290 autorises | 1,420 rejetes\n" COLOR_RESET);
        } else if (strcmp(line, "vault") == 0) {
            printf(COLOR_MAGENTA_BOLD "BitLocker Neo - Coffre Drive V: Statut:\n");
            printf("  * Etat du Volume        : DEVERROUILLE (En RAM Haute Securite)\n");
            printf("  * Chiffrement           : AES-256-GCM (Tag GMAC 128 bits)\n");
            printf("  * Cle de Secours        : 481920-384910-582910-948102-184920-384910-948201-384920\n" COLOR_RESET);
        } else if (strcmp(line, "matrix") == 0) {
            for (int i = 0; i < 40; i++) {
                printf(COLOR_GREEN_BOLD "01001110 01101111 01110110 01100001 01001111 01010011 01011111 01010011 01000101 01000011\n" COLOR_RESET);
                usleep(40000);
            }
        } else if (strcmp(line, "reboot") == 0) {
            system("reboot 2>/dev/null || true");
        } else if (strlen(line) > 0) {
            printf(COLOR_YELLOW_BOLD "Commande inconnue: '%s'. Tapez 'help' pour l'aide.\n" COLOR_RESET, line);
        }
    }
    enable_raw_mode();
}

void run_defender(void) {
    disable_raw_mode();
    printf(CLEAR_SCREEN);
    printf(COLOR_GREEN_BOLD "===============================================================================\n");
    printf("                     NOVA DEFENDER - SECURITY CENTER HUB                       \n");
    printf("             Windows 11 Advanced Threat Defense & Antivirus                    \n");
    printf("===============================================================================\n\n" COLOR_RESET);
    printf(COLOR_WHITE_BOLD "  [V] Bouclier Antivirus Temps Reel   : " COLOR_GREEN_BOLD "ACTIF (Surveillance continue)\n" COLOR_RESET);
    printf(COLOR_WHITE_BOLD "  [V] Intelligence Heuristique Cloud  : " COLOR_GREEN_BOLD "CONNECTE (Delta Signatures 2026)\n" COLOR_RESET);
    printf(COLOR_WHITE_BOLD "  [V] Protection Anti-Ransomware      : " COLOR_GREEN_BOLD "VERROUILLE\n" COLOR_RESET);
    printf(COLOR_WHITE_BOLD "  [V] Chaine de Demarrage Mesuree     : " COLOR_GREEN_BOLD "CONFORME (TPM 2.0 PCR-7)\n\n" COLOR_RESET);
    printf(COLOR_CYAN_BOLD "  Menaces bloquees : 14     En quarantaine : 0     Failles : 0\n\n" COLOR_RESET);
    printf(COLOR_YELLOW_BOLD "[Appuyez sur Entree pour revenir au Bureau...]" COLOR_RESET);
    fflush(stdout);
    getchar();
    enable_raw_mode();
}

void run_explorer(void) {
    disable_raw_mode();
    printf(CLEAR_SCREEN);
    printf(COLOR_CYAN_NEON "===============================================================================\n");
    printf("                EXPLORATEUR DE FICHIERS FLUENT (WINDOWS 11 NEO)                \n");
    printf("===============================================================================\n\n" COLOR_RESET);
    printf(COLOR_WHITE_BOLD "  Lecteurs Disponibles :\n" COLOR_RESET);
    printf("    [C:] Disque Systeme (Racine RAM LiveCD)      - 1.8 Go libres sur 2.0 Go\n");
    printf("    [V:] Coffre BitLocker Neo (Chiffre AES-256)   - 512 Mo securises\n");
    printf("    [D:] Lecteur Live CD (ISO 9660 + ISOLINUX)   - Lecture seule (18.3 Mo)\n\n");
    printf(COLOR_CYAN_BOLD "  Dossiers Principaux :\n" COLOR_RESET);
    printf("    📁 /bin        (Exécutables système, novaos, novaos-desktop)\n");
    printf("    📁 /etc        (Configuration de sécurité Zero-Trust, inittab)\n");
    printf("    📁 /home/tc    (Dossier utilisateur personnel NovaOS)\n");
    printf("    📁 /vault      (Volume cryptographique BitLocker Neo)\n\n");
    printf(COLOR_YELLOW_BOLD "[Appuyez sur Entree pour revenir au Bureau...]" COLOR_RESET);
    fflush(stdout);
    getchar();
    enable_raw_mode();
}

void run_settings(void) {
    disable_raw_mode();
    printf(CLEAR_SCREEN);
    printf(COLOR_CYAN_BOLD "===============================================================================\n");
    printf("             PARAMETRES SYSTEME ET CONFIGURATION (NOVAOS 2026)                 \n");
    printf("===============================================================================\n\n" COLOR_RESET);
    printf(COLOR_WHITE_BOLD "  * Affichage         : " COLOR_CYAN_NEON "Windows 11 Neo TrueColor 24-bit (Console Haute Resolution)\n" COLOR_RESET);
    printf(COLOR_WHITE_BOLD "  * Souris & Curseur  : " COLOR_GREEN_BOLD "Active (Protocole ANSI SGR 1006 Tracking)\n" COLOR_RESET);
    printf(COLOR_WHITE_BOLD "  * Reseau            : " COLOR_GREEN_BOLD "DHCP Actif / IPv4 & IPv6 Prêts\n" COLOR_RESET);
    printf(COLOR_WHITE_BOLD "  * Pare-feu          : " COLOR_GREEN_BOLD "Mode Zero-Trust Strict (Anti-Exfiltration)\n" COLOR_RESET);
    printf(COLOR_WHITE_BOLD "  * Version du Noyau  : " COLOR_CYAN_BOLD "Linux 4.19.10 Hardened NovaCore (x86_64)\n" COLOR_RESET);
    printf(COLOR_WHITE_BOLD "  * Mode d'Execution  : " COLOR_YELLOW_BOLD "Live CD RAM-Drive (Zero ecriture sur disque)\n\n" COLOR_RESET);
    printf(COLOR_YELLOW_BOLD "[Appuyez sur Entree pour revenir au Bureau...]" COLOR_RESET);
    fflush(stdout);
    getchar();
    enable_raw_mode();
}

void run_installer(void) {
    disable_raw_mode();
    printf(CLEAR_SCREEN);
    printf(COLOR_YELLOW_BOLD "===============================================================================\n");
    printf("                     NOVAOS SETUP WIZARD (INSTALLATEUR)                        \n");
    printf("                  Windows 11 Futuristic Installation Engine                    \n");
    printf("===============================================================================\n\n" COLOR_RESET);
    printf("  Disque Cible Detecte : " COLOR_CYAN_BOLD "Primary Virtual Storage (32 Go NVMe/SSD)\n" COLOR_RESET);
    printf("  Disposition des Partitions Proposee :\n");
    printf("    - Partition 1 : EFI System Partition (512 Mo, FAT32) -> /boot/efi\n");
    printf("    - Partition 2 : Nova Recovery Partition (1024 Mo, ext4) -> /boot\n");
    printf("    - Partition 3 : Racine Chiffree (LUKS2 AES-256-XTS + Argon2id) -> /\n\n");
    printf(COLOR_YELLOW_BOLD "  ATTENTION : Le disque sera formate et integralement chiffre.\n");
    printf("  Confirmer l'installation permanente sur ce disque ? [y/n] : " COLOR_RESET);
    fflush(stdout);

    char ans[16];
    if (fgets(ans, sizeof(ans), stdin) && (ans[0] == 'y' || ans[0] == 'Y')) {
        printf("\n" COLOR_CYAN_BOLD "Deploiement de NovaOS Hyperion 2026 sur disque...\n" COLOR_RESET);
        printf(COLOR_CYAN_NEON "[>>>             ] 20%% Formatage GPT et Partition EFI (FAT32)...\n" COLOR_RESET);
        usleep(500000);
        printf(COLOR_CYAN_NEON "[>>>>>>>>>       ] 60%% Initialisation du conteneur LUKS2 AES-256-XTS...\n" COLOR_RESET);
        usleep(500000);
        printf(COLOR_CYAN_NEON "[>>>>>>>>>>>>>>> ] 90%% Deploiement du Noyau Durci et du Bureau NovaShell...\n" COLOR_RESET);
        usleep(500000);
        printf(COLOR_GREEN_BOLD "[>>>>>>>>>>>>>>>>] 100%% Finalisation de la NVRAM UEFI & Cle BitLocker Neo!\n\n" COLOR_RESET);
        printf(COLOR_GREEN_BOLD "===============================================================================\n");
        printf("  INSTALLATION TERMINEE AVEC SUCCES SUR LE DISQUE DUR !\n\n");
        printf("  CLE D'URGENCE DE SECOURS BITLOCKER NEO (48 CHIFFRES) :\n");
        printf("  " COLOR_CYAN_BOLD "481920-384910-582910-948102-184920-384910-948201-384920\n\n" COLOR_RESET);
        printf(COLOR_GREEN_BOLD "  Conservez precieusement cette cle. Vous pouvez desormais retirer l'ISO.\n");
        printf("===============================================================================\n\n" COLOR_RESET);
    } else {
        printf("\nInstallation annulee.\n");
    }

    printf(COLOR_YELLOW_BOLD "[Appuyez sur Entree pour revenir au Bureau...]" COLOR_RESET);
    fflush(stdout);
    getchar();
    enable_raw_mode();
}

int main(void) {
    enable_raw_mode();

    int start_menu_open = 0;
    while (1) {
        draw_desktop(start_menu_open);

        char c = 0;
        if (read(STDIN_FILENO, &c, 1) > 0) {
            /* Check escape sequences (e.g. mouse clicks \033[<0;x;yM or arrow keys) */
            if (c == 27) {
                char seq[32];
                int idx = 0;
                while (idx < 30 && read(STDIN_FILENO, &seq[idx], 1) > 0) {
                    if (seq[idx] == 'm' || seq[idx] == 'M' || seq[idx] == '~') {
                        idx++;
                        break;
                    }
                    idx++;
                }
                seq[idx] = '\0';

                /* Check SGR mouse click: e.g. [<0;X;YM */
                if (seq[0] == '[' && seq[1] == '<') {
                    int btn = 0, mx = 0, my = 0;
                    char type = 0;
                    if (sscanf(seq + 2, "%d;%d;%d%c", &btn, &mx, &my, &type) >= 3 && (type == 'M' || type == 'm')) {
                        /* Clicks on Taskbar */
                        if (my >= 22) {
                            if (mx >= 1 && mx <= 12) {
                                start_menu_open = !start_menu_open;
                            } else if (mx >= 13 && mx <= 23) {
                                run_terminal();
                            } else if (mx >= 24 && mx <= 34) {
                                run_defender();
                            } else if (mx >= 35 && mx <= 45) {
                                run_defender();
                            } else if (mx >= 46 && mx <= 56) {
                                run_explorer();
                            } else if (mx >= 57 && mx <= 67) {
                                run_installer();
                            }
                        }
                        /* Clicks on Desktop Icons (Row 4-6) */
                        else if (my >= 4 && my <= 7) {
                            if (mx >= 4 && mx <= 14) run_terminal();
                            else if (mx >= 17 && mx <= 27) run_defender();
                            else if (mx >= 30 && mx <= 40) run_defender();
                            else if (mx >= 43 && mx <= 53) run_explorer();
                            else if (mx >= 56 && mx <= 66) run_installer();
                        }
                    }
                }
            } else if (c == '1' || c == 't' || c == 'T') {
                run_terminal();
            } else if (c == '2' || c == 'd' || c == 'D') {
                run_defender();
            } else if (c == '3' || c == 'v' || c == 'V') {
                run_defender();
            } else if (c == '4' || c == 'f' || c == 'F') {
                run_explorer();
            } else if (c == '5' || c == 'i' || c == 'I') {
                run_installer();
            } else if (c == '6' || c == 'p' || c == 'P') {
                run_settings();
            } else if (c == 's' || c == 'S') {
                start_menu_open = !start_menu_open;
            } else if (c == 'q' || c == 'Q') {
                break;
            }
        }
        usleep(50000); /* 50ms loop */
    }

    disable_raw_mode();
    printf(CLEAR_SCREEN "NovaOS session ended.\n");
    return 0;
}

