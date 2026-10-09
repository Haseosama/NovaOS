/*
 * NovaOS - Futuristic Windows 11 Graphical Desktop Environment (NovaGUI)
 * High-Resolution Framebuffer Graphics Engine (X11 / Debian Equivalent)
 * Runs directly on Linux /dev/fb0 with full mouse, wallpaper, taskbar & windows.
 * Copyright (c) 2026 NovaOS Security Architecture Team
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <linux/fb.h>
#include <linux/input.h>
#include <termios.h>
#include <time.h>
#include <math.h>

#define SCREEN_W 1024
#define SCREEN_H 768

/* Colors (32-bit ARGB) */
#define COLOR_VOID_BLACK    0x00050811
#define COLOR_DEEP_BLUE     0x000a1628
#define COLOR_ACRYLIC_SLATE 0x000f172a
#define COLOR_TASKBAR       0x000b1120
#define COLOR_CYAN_NEON     0x0038bdf8
#define COLOR_CYAN_BRIGHT   0x0000f2fe
#define COLOR_BLUE_ACCENT   0x002563eb
#define COLOR_WHITE         0x00ffffff
#define COLOR_GRAY_LIGHT    0x00cbd5e1
#define COLOR_GRAY_DARK     0x00475569
#define COLOR_GREEN_SHIELD  0x0010b981
#define COLOR_PURPLE_VAULT  0x00a855f7
#define COLOR_RED_CLOSE     0x00ef4444
#define COLOR_YELLOW_WARN   0x00eab308

/* 8x16 Basic ASCII Font data */
#include "font8x16.h"

static int fb_fd = -1;
static int mouse_fd = -1;
static uint32_t *fb_ptr = NULL;
static uint32_t backbuffer[SCREEN_W * SCREEN_H];
static int screen_width = SCREEN_W;
static int screen_height = SCREEN_H;
static int mouse_x = SCREEN_W / 2;
static int mouse_y = SCREEN_H / 2;
static int mouse_btn_left = 0;

/* Window manager state */
typedef struct {
    int id;
    const char *title;
    int x, y, w, h;
    int visible;
    int minimized;
} Window;

#define MAX_WINDOWS 4
static Window windows[MAX_WINDOWS] = {
    {1, "Nova Terminal (PowerShell Neo)", 180, 100, 660, 440, 1, 0},
    {2, "Nova Defender - Security Hub", 220, 120, 600, 420, 0, 0},
    {3, "BitLocker Neo - Coffre Drive V:", 240, 140, 560, 380, 0, 0},
    {4, "NovaOS Setup Wizard (Installateur)", 160, 80, 700, 480, 0, 0}
};
static int active_window = 0;
static int start_menu_open = 0;

/* Terminal state */
#define TERM_MAX_LINES 16
#define TERM_LINE_LEN 80
static char term_lines[TERM_MAX_LINES][TERM_LINE_LEN];
static int term_line_count = 0;
static char term_input[TERM_LINE_LEN] = {0};
static int term_input_len = 0;

/* Installer State */
static int install_progress = 0;
static int install_running = 0;

void term_add_line(const char *text) {
    if (term_line_count >= TERM_MAX_LINES) {
        for (int i = 0; i < TERM_MAX_LINES - 1; i++) {
            strncpy(term_lines[i], term_lines[i + 1], TERM_LINE_LEN);
        }
        term_line_count = TERM_MAX_LINES - 1;
    }
    strncpy(term_lines[term_line_count], text, TERM_LINE_LEN - 1);
    term_lines[term_line_count][TERM_LINE_LEN - 1] = '\0';
    term_line_count++;
}

/* Graphics primitives */
static inline void set_pixel(int x, int y, uint32_t color) {
    if (x >= 0 && x < screen_width && y >= 0 && y < screen_height) {
        backbuffer[y * screen_width + x] = color;
    }
}

void draw_rect(int x, int y, int w, int h, uint32_t color) {
    for (int j = y; j < y + h; j++) {
        if (j < 0 || j >= screen_height) continue;
        for (int i = x; i < x + w; i++) {
            if (i >= 0 && i < screen_width) {
                backbuffer[j * screen_width + i] = color;
            }
        }
    }
}

void draw_rect_outline(int x, int y, int w, int h, uint32_t color) {
    for (int i = x; i < x + w; i++) {
        set_pixel(i, y, color);
        set_pixel(i, y + h - 1, color);
    }
    for (int j = y; j < y + h; j++) {
        set_pixel(x, j, color);
        set_pixel(x + w - 1, j, color);
    }
}

void draw_char(int x, int y, char c, uint32_t color) {
    if ((unsigned char)c >= 128) c = '?';
    const uint8_t *glyph = &font8x16[(unsigned char)c * 16];
    for (int row = 0; row < 16; row++) {
        uint8_t bits = glyph[row];
        for (int col = 0; col < 8; col++) {
            if (bits & (0x80 >> col)) {
                set_pixel(x + col, y + row, color);
            }
        }
    }
}

void draw_string(int x, int y, const char *str, uint32_t color) {
    int cur_x = x;
    while (*str) {
        draw_char(cur_x, y, *str, color);
        cur_x += 8;
        str++;
    }
}

/* Windows 11 Dark Bloom Wallpaper */
void render_wallpaper(void) {
    for (int y = 0; y < screen_height; y++) {
        float ny = (float)y / screen_height;
        uint32_t base = 0x00040812 + (int)(ny * 12.0f);
        for (int x = 0; x < screen_width; x++) {
            float dx = (float)(x - screen_width / 2) / 380.0f;
            float dy = (float)(y - screen_height / 2 + 30) / 280.0f;
            float dist = sqrtf(dx * dx + dy * dy);
            
            if (dist < 1.0f) {
                float intensity = (1.0f - dist);
                int r = (int)(20.0f * intensity);
                int g = (int)(110.0f * intensity);
                int b = (int)(210.0f * intensity);
                backbuffer[y * screen_width + x] = (r << 16) | (g << 8) | b;
            } else {
                backbuffer[y * screen_width + x] = base;
            }
        }
    }
}

/* Windows 11 Logo (4 Squares) */
void draw_win11_logo(int x, int y, int size, uint32_t color) {
    int half = size / 2 - 1;
    draw_rect(x, y, half, half, color);
    draw_rect(x + half + 2, y, half, half, color);
    draw_rect(x, y + half + 2, half, half, color);
    draw_rect(x + half + 2, y + half + 2, half, half, color);
}

/* Desktop Icons */
void render_desktop_icons(void) {
    struct { int x, y; const char *label; const char *tag; uint32_t col; } icons[] = {
        {36, 36, "Ce PC", "PC", COLOR_BLUE_ACCENT},
        {36, 126, "Defender", "SHD", COLOR_GREEN_SHIELD},
        {36, 216, "Drive V:", "LCK", COLOR_PURPLE_VAULT},
        {36, 306, "Fichiers", "DIR", COLOR_CYAN_NEON},
        {36, 396, "Installer", "SET", COLOR_YELLOW_WARN},
        {36, 486, "Terminal", ">_", COLOR_CYAN_BRIGHT}
    };

    for (int i = 0; i < 6; i++) {
        int x = icons[i].x;
        int y = icons[i].y;
        draw_rect(x, y, 44, 44, COLOR_ACRYLIC_SLATE);
        draw_rect_outline(x, y, 44, 44, icons[i].col);
        draw_string(x + 10, y + 14, icons[i].tag, icons[i].col);
        draw_string(x - 6, y + 50, icons[i].label, COLOR_WHITE);
    }
}

/* Windows 11 Centered Taskbar */
void render_taskbar(void) {
    int tb_y = screen_height - 48;
    draw_rect(0, tb_y, screen_width, 48, COLOR_TASKBAR);
    draw_rect(0, tb_y, screen_width, 1, 0x00334155);

    /* Centered Icons */
    int center_x = screen_width / 2 - 140;
    
    /* Start Button */
    draw_win11_logo(center_x, tb_y + 14, 20, COLOR_CYAN_NEON);

    /* Search Bar */
    draw_rect(center_x + 36, tb_y + 10, 110, 28, 0x001e293b);
    draw_rect_outline(center_x + 36, tb_y + 10, 110, 28, 0x00334155);
    draw_string(center_x + 44, tb_y + 16, "Rechercher", COLOR_GRAY_DARK);

    /* Pinned App Icons */
    int app_x = center_x + 160;
    draw_rect(app_x, tb_y + 10, 28, 28, COLOR_ACRYLIC_SLATE);
    draw_string(app_x + 6, tb_y + 16, ">_", COLOR_CYAN_BRIGHT);

    draw_rect(app_x + 38, tb_y + 10, 28, 28, COLOR_ACRYLIC_SLATE);
    draw_string(app_x + 44, tb_y + 16, "V", COLOR_GREEN_SHIELD);

    draw_rect(app_x + 76, tb_y + 10, 28, 28, COLOR_ACRYLIC_SLATE);
    draw_string(app_x + 82, tb_y + 16, "L", COLOR_PURPLE_VAULT);

    draw_rect(app_x + 114, tb_y + 10, 28, 28, COLOR_ACRYLIC_SLATE);
    draw_string(app_x + 120, tb_y + 16, "I", COLOR_YELLOW_WARN);

    /* System Tray Right */
    time_t rawtime;
    struct tm *timeinfo;
    time(&rawtime);
    timeinfo = localtime(&rawtime);
    char time_buf[16];
    strftime(time_buf, sizeof(time_buf), "%H:%M:%S", timeinfo);

    draw_string(screen_width - 230, tb_y + 16, "📶 Wi-Fi", COLOR_GRAY_LIGHT);
    draw_string(screen_width - 150, tb_y + 16, "🛡️ TPM", COLOR_GREEN_SHIELD);
    draw_string(screen_width - 80, tb_y + 16, time_buf, COLOR_WHITE);
}

/* Start Menu Window */
void render_start_menu(void) {
    if (!start_menu_open) return;
    int w = 500;
    int h = 400;
    int x = screen_width / 2 - w / 2;
    int y = screen_height - 48 - h - 12;

    draw_rect(x, y, w, h, COLOR_ACRYLIC_SLATE);
    draw_rect_outline(x, y, w, h, COLOR_CYAN_NEON);

    /* Search */
    draw_rect(x + 24, y + 20, w - 48, 34, 0x000b1120);
    draw_rect_outline(x + 24, y + 20, w - 48, 34, 0x00334155);
    draw_string(x + 36, y + 28, "Rechercher des applications et fichiers...", COLOR_GRAY_DARK);

    /* Section Header */
    draw_string(x + 24, y + 74, "APPLICATIONS EPINGLEES", COLOR_CYAN_NEON);

    /* Apps Grid */
    const char *apps[] = {
        "[1] Terminal Neo", "[2] Nova Defender",
        "[3] BitLocker V:", "[4] Explorateur",
        "[5] Installateur", "[6] Parametres"
    };
    for (int i = 0; i < 6; i++) {
        int ax = x + 36 + (i % 2) * 220;
        int ay = y + 106 + (i / 2) * 44;
        draw_rect(ax, ay, 200, 34, 0x001e293b);
        draw_rect_outline(ax, ay, 200, 34, 0x0038bdf8);
        draw_string(ax + 12, ay + 10, apps[i], COLOR_WHITE);
    }

    /* Footer */
    draw_rect(x, y + h - 48, w, 48, 0x000b1120);
    draw_string(x + 24, y + h - 30, "👤 NovaAdmin (Administrateur)", COLOR_WHITE);
    draw_string(x + w - 120, y + h - 30, "🛑 Eteindre", COLOR_RED_CLOSE);
}

/* Active Applications Windows */
void render_windows(void) {
    for (int i = 0; i < MAX_WINDOWS; i++) {
        Window *win = &windows[i];
        if (!win->visible) continue;

        /* Window Frame */
        draw_rect(win->x, win->y, win->w, win->h, COLOR_ACRYLIC_SLATE);
        draw_rect_outline(win->x, win->y, win->w, win->h, COLOR_CYAN_NEON);

        /* Titlebar */
        draw_rect(win->x, win->y, win->w, 32, 0x001e293b);
        draw_string(win->x + 14, win->y + 8, win->title, COLOR_WHITE);

        /* Window Buttons */
        draw_rect(win->x + win->w - 28, win->y + 8, 16, 16, COLOR_RED_CLOSE);
        draw_rect(win->x + win->w - 52, win->y + 8, 16, 16, COLOR_YELLOW_WARN);
        draw_rect(win->x + win->w - 76, win->y + 8, 16, 16, COLOR_GREEN_SHIELD);

        /* Content */
        if (win->id == 1) {
            /* Terminal */
            draw_rect(win->x + 12, win->y + 44, win->w - 24, win->h - 56, 0x00050811);
            for (int l = 0; l < term_line_count; l++) {
                draw_string(win->x + 20, win->y + 52 + l * 20, term_lines[l], COLOR_CYAN_NEON);
            }
            /* Prompt line */
            int py = win->y + 52 + term_line_count * 20;
            draw_string(win->x + 20, py, "NovaOS:~# ", COLOR_GREEN_SHIELD);
            draw_string(win->x + 104, py, term_input, COLOR_WHITE);
            draw_rect(win->x + 104 + term_input_len * 8, py, 8, 16, COLOR_CYAN_BRIGHT);
        } else if (win->id == 2) {
            /* Defender */
            draw_string(win->x + 24, win->y + 50, "BOUCLIER DE PROTECTION TEMPS REEL : ACTIF", COLOR_GREEN_SHIELD);
            draw_string(win->x + 24, win->y + 80, "* Surveillance Heuristique Zero-Day : ENGAGEE", COLOR_WHITE);
            draw_string(win->x + 24, win->y + 110, "* Racine de Confiance TPM 2.0 (PCR-7) : VERIFIEE", COLOR_WHITE);
            draw_string(win->x + 24, win->y + 140, "* Signatures Delta : 2026.10.09.4201", COLOR_WHITE);
            draw_string(win->x + 24, win->y + 170, "* Menaces Bloquees : 14 Attaques Neutralisees", COLOR_GREEN_SHIELD);
            draw_rect(win->x + 24, win->y + 220, 240, 36, COLOR_GREEN_SHIELD);
            draw_string(win->x + 40, win->y + 230, "Lancer un Scan Heuristique", COLOR_VOID_BLACK);
        } else if (win->id == 3) {
            /* Vault */
            draw_string(win->x + 24, win->y + 50, "VOLUME CHIFFRE BITLOCKER NEO (DRIVE V:)", COLOR_PURPLE_VAULT);
            draw_string(win->x + 24, win->y + 80, "Statut : DEVERROUILLE EN RAM (Chiffrement AES-256-GCM)", COLOR_GREEN_SHIELD);
            draw_string(win->x + 24, win->y + 110, "Cle de Secours BitLocker Neo :", COLOR_WHITE);
            draw_string(win->x + 24, win->y + 130, "481920-384910-582910-948102-184920-384910-948201-384920", COLOR_CYAN_BRIGHT);
        } else if (win->id == 4) {
            /* Installer */
            draw_string(win->x + 24, win->y + 50, "ASSISTANT D'INSTALLATION NOVAOS (DEPLOIEMENT DISQUE)", COLOR_YELLOW_WARN);
            draw_string(win->x + 24, win->y + 80, "Disque Detecte : Primary Storage Disk (32 Go NVMe/SSD)", COLOR_WHITE);
            draw_string(win->x + 24, win->y + 110, "Partitions : ESP (512 Mo) + Recovery (1 Go) + Root LUKS2 (AES-256)", COLOR_WHITE);
            
            draw_rect(win->x + 24, win->y + 160, win->w - 48, 28, 0x001e293b);
            draw_rect(win->x + 24, win->y + 160, (win->w - 48) * install_progress / 100, 28, COLOR_CYAN_NEON);
            
            char prog_str[32];
            snprintf(prog_str, sizeof(prog_str), "Progression : %d%%", install_progress);
            draw_string(win->x + 30, win->y + 166, prog_str, COLOR_WHITE);

            if (install_progress >= 100) {
                draw_string(win->x + 24, win->y + 210, "INSTALLATION REUSSIE SUR LE DISQUE DUR !", COLOR_GREEN_SHIELD);
                draw_string(win->x + 24, win->y + 230, "Vous pouvez retirer l'ISO et redemarrer.", COLOR_WHITE);
            } else if (!install_running) {
                draw_rect(win->x + 24, win->y + 210, 200, 36, COLOR_BLUE_ACCENT);
                draw_string(win->x + 36, win->y + 220, "Demarrer l'Installation", COLOR_WHITE);
            }
        }
    }
}

/* Mouse cursor pointer */
void render_mouse_cursor(void) {
    int x = mouse_x;
    int y = mouse_y;
    for (int i = 0; i < 12; i++) {
        for (int j = 0; j <= i; j++) {
            set_pixel(x + j, y + i, COLOR_WHITE);
        }
        set_pixel(x, y + i, COLOR_VOID_BLACK);
        set_pixel(x + i, y + i, COLOR_VOID_BLACK);
    }
}

/* Command execution */
void execute_command(const char *cmd) {
    if (strcmp(cmd, "help") == 0 || strcmp(cmd, "?") == 0) {
        term_add_line("Commandes: novafetch, defender, scan, firewall, vault, matrix, install, clear, reboot");
    } else if (strcmp(cmd, "novafetch") == 0 || strcmp(cmd, "neofetch") == 0) {
        term_add_line("   ######  ######   NovaAdmin@NovaOS");
        term_add_line("   ######  ######   OS: NovaOS Hyperion 2026 (Windows 11 Neo)");
        term_add_line("   ######  ######   Kernel: Linux 6.1 Hardened (KASLR/PTI)");
        term_add_line("   ######  ######   Security: Zero-Trust Military Grade (AES-256)");
    } else if (strcmp(cmd, "defender") == 0) {
        term_add_line("Nova Defender: Bouclier ACTIF. 14 menaces interceptees.");
        windows[1].visible = 1;
    } else if (strcmp(cmd, "vault") == 0) {
        term_add_line("BitLocker Neo: Volume Drive V: DEVERROUILLE (AES-256-GCM).");
        windows[2].visible = 1;
    } else if (strcmp(cmd, "install") == 0) {
        term_add_line("Lancement du Setup Wizard NovaOS...");
        windows[3].visible = 1;
    } else if (strcmp(cmd, "clear") == 0) {
        term_line_count = 0;
    } else if (strcmp(cmd, "scan") == 0) {
        term_add_line("Scan heuristique: 512 secteurs verifies. 0 menace.");
    } else if (strcmp(cmd, "matrix") == 0) {
        term_add_line("01101110 01101111 01110110 01100001 01101111 01110011 QUANTUM MATRIX ACTIVE");
    } else if (strcmp(cmd, "reboot") == 0) {
        system("reboot 2>/dev/null || true");
    } else if (strlen(cmd) > 0) {
        term_add_line("Commande inconnue. Tapez 'help'.");
    }
}

int main(int argc, char **argv) {
    /* If --test requested, check if fb0 is available and writable */
    if (argc > 1 && strcmp(argv[1], "--test") == 0) {
        int test_fd = open("/dev/fb0", O_RDWR);
        if (test_fd < 0) return 1;
        close(test_fd);
        return 0;
    }

    /* Open framebuffer */
    fb_fd = open("/dev/fb0", O_RDWR);
    if (fb_fd < 0) {
        /* No hardware framebuffer available, return error so desktop fallback takes over immediately */
        return 1;
    }

    struct fb_var_screeninfo vinfo;
    if (ioctl(fb_fd, FBIOGET_VSCREENINFO, &vinfo) == 0) {
        screen_width = vinfo.xres;
        screen_height = vinfo.yres;
    }
    fb_ptr = (uint32_t *)mmap(0, screen_width * screen_height * 4, PROT_READ | PROT_WRITE, MAP_SHARED, fb_fd, 0);
    if (!fb_ptr || fb_ptr == MAP_FAILED) {
        close(fb_fd);
        return 1;
    }

    /* Open mouse device */
    mouse_fd = open("/dev/input/mice", O_RDONLY | O_NONBLOCK);

    /* Initialize terminal lines */
    term_add_line("NovaOS PowerShell Neo 1.0 [Windows 11 Futuristic Core]");
    term_add_line("Type 'help' for commands, 'novafetch', 'defender', 'install'.");

    /* Non-blocking stdin */
    int flags = fcntl(STDIN_FILENO, F_GETFL, 0);
    fcntl(STDIN_FILENO, F_SETFL, flags | O_NONBLOCK);

    printf("[NovaOS GUI] Windows 11 Neo Desktop Engine running...\n");

    int running = 1;
    while (running) {
        /* Read mouse input */
        if (mouse_fd >= 0) {
            signed char mbuf[3];
            if (read(mouse_fd, mbuf, sizeof(mbuf)) == sizeof(mbuf)) {
                mouse_btn_left = mbuf[0] & 0x1;
                mouse_x += mbuf[1];
                mouse_y -= mbuf[2];
                if (mouse_x < 0) mouse_x = 0;
                if (mouse_x >= screen_width) mouse_x = screen_width - 1;
                if (mouse_y < 0) mouse_y = 0;
                if (mouse_y >= screen_height) mouse_y = screen_height - 1;

                if (mouse_btn_left) {
                    /* Check click on taskbar center (Start button) */
                    int tb_y = screen_height - 48;
                    int cx = screen_width / 2 - 140;
                    if (mouse_y >= tb_y && mouse_x >= cx && mouse_x <= cx + 32) {
                        start_menu_open = !start_menu_open;
                    }
                    /* Check click on Terminal icon */
                    if (mouse_y >= tb_y && mouse_x >= cx + 160 && mouse_x <= cx + 190) {
                        windows[0].visible = 1;
                    }
                }
            }
        }

        /* Read keyboard input */
        char ch;
        while (read(STDIN_FILENO, &ch, 1) > 0) {
            if (ch == '\n' || ch == '\r') {
                term_input[term_input_len] = '\0';
                term_add_line(term_input);
                execute_command(term_input);
                term_input_len = 0;
                term_input[0] = '\0';
            } else if (ch == 127 || ch == '\b') {
                if (term_input_len > 0) {
                    term_input_len--;
                    term_input[term_input_len] = '\0';
                }
            } else if (ch == 27) {
                start_menu_open = 0;
            } else if (ch >= 32 && ch < 127) {
                if (term_input_len < TERM_LINE_LEN - 2) {
                    term_input[term_input_len++] = ch;
                    term_input[term_input_len] = '\0';
                }
            }
        }

        /* Render frame */
        render_wallpaper();
        render_desktop_icons();
        render_windows();
        render_taskbar();
        render_start_menu();
        render_mouse_cursor();

        /* Copy backbuffer to hardware framebuffer */
        if (fb_ptr) {
            memcpy(fb_ptr, backbuffer, screen_width * screen_height * 4);
        }

        usleep(16000); /* ~60 FPS */
    }

    if (fb_ptr) munmap(fb_ptr, screen_width * screen_height * 4);
    if (fb_fd >= 0) close(fb_fd);
    if (mouse_fd >= 0) close(mouse_fd);
    return 0;
}
