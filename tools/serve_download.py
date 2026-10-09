#!/usr/bin/env python3
"""
NovaOS Web Portal & Live Preview Simulator
Serves the binary Live CD ISO and provides an interactive Windows 11 Neo OS simulator.
"""

import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ISO_PATH = os.path.join(REPO_ROOT, "dist", "NovaOS-v1.0-x86_64-LiveCD.iso")
SHA_PATH = os.path.join(REPO_ROOT, "dist", "SHA256SUMS")

HTML_PAGE = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NovaOS Hyperion 2026 — Live Preview & ISO Download</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: #050811;
            color: #e0f2fe;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI Variable", "Segoe UI", Roboto, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }
        /* Top Navigation Header */
        header {
            background: rgba(11, 17, 32, 0.85);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid rgba(56, 189, 248, 0.2);
            padding: 12px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 20px;
            font-weight: 800;
            color: #38bdf8;
            letter-spacing: 1px;
        }
        .brand-badge {
            background: rgba(14, 165, 233, 0.15);
            border: 1px solid #0284c7;
            color: #38bdf8;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
        }
        .btn-download-top {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: #fff;
            padding: 10px 20px;
            border-radius: 10px;
            text-decoration: none;
            font-weight: 700;
            font-size: 14px;
            box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4);
            transition: all 0.2s;
        }
        .btn-download-top:hover {
            transform: translateY(-2px);
            background: linear-gradient(135deg, #0ea5e9, #3b82f6);
            box-shadow: 0 6px 20px rgba(2, 132, 199, 0.6);
        }

        /* Banner & Info */
        .info-strip {
            background: rgba(14, 165, 233, 0.08);
            border-bottom: 1px solid rgba(56, 189, 248, 0.15);
            padding: 10px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 13px;
        }
        .info-strip code {
            background: rgba(0, 0, 0, 0.4);
            padding: 2px 8px;
            border-radius: 4px;
            color: #38bdf8;
            font-family: monospace;
        }

        /* Desktop Environment Container */
        .desktop-container {
            flex: 1;
            position: relative;
            background: radial-gradient(ellipse at 50% 30%, #0c4a6e33, #050811 75%);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 24px 24px 0 24px;
            min-height: calc(100vh - 120px);
        }

        /* Desktop Grid Icons */
        .desktop-icons {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
            gap: 20px;
            max-width: 700px;
            z-index: 10;
        }
        .desk-icon {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            padding: 12px 8px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s;
            user-select: none;
        }
        .desk-icon:hover {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(8px);
        }
        .desk-icon-svg {
            width: 52px;
            height: 52px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 14px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
            font-size: 24px;
        }
        .desk-icon span {
            font-size: 12px;
            text-align: center;
            text-shadow: 0 1px 3px rgba(0,0,0,0.8);
            font-weight: 500;
        }

        /* Active Window / Popups */
        .window {
            position: absolute;
            top: 60px;
            left: 50%;
            transform: translateX(-50%);
            width: 760px;
            max-width: 95%;
            background: rgba(15, 23, 42, 0.92);
            backdrop-filter: blur(24px);
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: 16px;
            box-shadow: 0 25px 60px rgba(0,0,0,0.8), 0 0 30px rgba(56, 189, 248, 0.2);
            display: none;
            flex-direction: column;
            overflow: hidden;
            z-index: 50;
        }
        .window-header {
            background: rgba(30, 41, 59, 0.6);
            border-bottom: 1px solid rgba(255,255,255,0.08);
            padding: 12px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 13px;
            font-weight: 600;
        }
        .window-controls {
            display: flex;
            gap: 8px;
        }
        .win-btn {
            width: 14px;
            height: 14px;
            border-radius: 50%;
            cursor: pointer;
            border: none;
        }
        .win-close { background: #ef4444; }
        .win-min { background: #eab308; }
        .win-max { background: #22c55e; }
        .window-body {
            padding: 20px;
            max-height: 520px;
            overflow-y: auto;
            font-family: "Cascadia Code", "JetBrains Mono", Consolas, monospace;
            font-size: 13px;
            line-height: 1.6;
        }

        /* Terminal styling */
        .terminal-screen {
            background: #030712;
            color: #a7f3d0;
            padding: 16px;
            border-radius: 8px;
            min-height: 300px;
        }
        .term-input-row {
            display: flex;
            gap: 8px;
            margin-top: 10px;
            align-items: center;
        }
        .term-prompt {
            color: #38bdf8;
            font-weight: bold;
        }
        .term-input {
            background: transparent;
            border: none;
            outline: none;
            color: #fff;
            font-family: inherit;
            font-size: 13px;
            flex: 1;
        }

        /* Start Menu Popup */
        .start-menu {
            position: absolute;
            bottom: 70px;
            left: 50%;
            transform: translateX(-50%);
            width: 580px;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(28px);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 18px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.8), 0 0 25px rgba(56, 189, 248, 0.2);
            padding: 24px;
            display: none;
            z-index: 60;
        }
        .start-search {
            width: 100%;
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 10px 16px;
            color: #fff;
            font-size: 13px;
            margin-bottom: 20px;
            outline: none;
        }
        .start-pinned-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }
        .start-item {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .start-item:hover {
            background: rgba(56, 189, 248, 0.15);
            border-color: rgba(56, 189, 248, 0.4);
        }
        .start-footer {
            border-top: 1px solid rgba(255,255,255,0.08);
            padding-top: 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 12px;
        }

        /* Windows 11 Centered Taskbar */
        .taskbar {
            height: 56px;
            background: rgba(11, 17, 32, 0.85);
            backdrop-filter: blur(20px);
            border-top: 1px solid rgba(56, 189, 248, 0.25);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 16px;
            position: relative;
            z-index: 80;
        }
        .taskbar-center {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .tb-btn {
            width: 42px;
            height: 42px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 20px;
            border: none;
            background: transparent;
            color: #fff;
        }
        .tb-btn:hover {
            background: rgba(255, 255, 255, 0.12);
        }
        .tb-btn.active {
            background: rgba(56, 189, 248, 0.2);
            border-bottom: 2px solid #38bdf8;
        }
        .start-btn {
            background: linear-gradient(135deg, #0284c7, #38bdf8);
            color: #050811;
            font-weight: bold;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
        }
        .taskbar-tray {
            display: flex;
            align-items: center;
            gap: 14px;
            font-size: 12px;
            color: #94a3b8;
        }
        .tray-badge {
            display: flex;
            align-items: center;
            gap: 6px;
            background: rgba(30, 41, 59, 0.6);
            padding: 6px 10px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.05);
        }
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <span>❖ NovaOS Hyperion 2026</span>
            <span class="brand-badge">Windows 11 Secure Neo Edition</span>
        </div>
        <a class="btn-download-top" href="/download/NovaOS-v1.0-x86_64-LiveCD.iso" download="NovaOS-v1.0-x86_64-LiveCD.iso">
            ⬇️ Télécharger l'ISO (3.0 Mo)
        </a>
    </header>

    <div class="info-strip">
        <div>
            <strong>Empreinte SHA-256 :</strong> <code>b547d4f986f0b081dbc74a41440a6dcb16bf85655fea10da36cf2f2ecf4f60ad</code>
        </div>
        <div>
            <strong>Mode Live CD :</strong> Démarrage direct en RAM &bull; Chiffrement LUKS2 AES-256 &bull; TPM 2.0
        </div>
    </div>

    <div class="desktop-container" onclick="handleDesktopClick(event)">
        <!-- Desktop Icons Grid -->
        <div class="desktop-icons">
            <div class="desk-icon" onclick="openWindow('win-terminal')">
                <div class="desk-icon-svg" style="background: linear-gradient(135deg, #0f172a, #1e293b); border: 1px solid #38bdf8; color: #38bdf8;">>_</div>
                <span>Terminal</span>
            </div>
            <div class="desk-icon" onclick="openWindow('win-defender')">
                <div class="desk-icon-svg" style="background: linear-gradient(135deg, #065f46, #10b981); color: #fff;">🛡️</div>
                <span>Defender</span>
            </div>
            <div class="desk-icon" onclick="openWindow('win-vault')">
                <div class="desk-icon-svg" style="background: linear-gradient(135deg, #581c87, #a855f7); color: #fff;">🔒</div>
                <span>Drive V:</span>
            </div>
            <div class="desk-icon" onclick="openWindow('win-explorer')">
                <div class="desk-icon-svg" style="background: linear-gradient(135deg, #0369a1, #38bdf8); color: #fff;">📁</div>
                <span>Explorateur</span>
            </div>
            <div class="desk-icon" onclick="openWindow('win-installer')">
                <div class="desk-icon-svg" style="background: linear-gradient(135deg, #991b1b, #ef4444); color: #fff;">💿</div>
                <span>Installateur</span>
            </div>
            <div class="desk-icon" onclick="openWindow('win-settings')">
                <div class="desk-icon-svg" style="background: linear-gradient(135deg, #334155, #64748b); color: #fff;">⚙️</div>
                <span>Paramètres</span>
            </div>
        </div>

        <!-- Window: Terminal -->
        <div id="win-terminal" class="window" style="display: block;">
            <div class="window-header">
                <span>NovaOS PowerShell Neo 1.0 — x86_64 Hardened Core</span>
                <div class="window-controls">
                    <button class="win-btn win-close" onclick="closeWindow('win-terminal')"></button>
                </div>
            </div>
            <div class="window-body">
                <div class="terminal-screen" id="term-screen">
                    <pre style="color: #38bdf8;">======================================================================
  NovaOS Cybernetic Terminal [PowerShell Neo - Hyperion 2026 Core]
  Type 'help' for commands | 'defender' | 'matrix' | 'install'
======================================================================</pre>
                    <div id="term-log"></div>
                    <div class="term-input-row">
                        <span class="term-prompt">NovaOS:~#</span>
                        <input type="text" class="term-input" id="term-input" autofocus onkeydown="handleTermKey(event)">
                    </div>
                </div>
            </div>
        </div>

        <!-- Window: Defender -->
        <div id="win-defender" class="window">
            <div class="window-header">
                <span>🛡️ Nova Defender — Security Center Hub</span>
                <div class="window-controls">
                    <button class="win-btn win-close" onclick="closeWindow('win-defender')"></button>
                </div>
            </div>
            <div class="window-body">
                <h3 style="color: #10b981; margin-bottom: 12px;">Bouclier de Sécurité Temps Réel : ACTIF</h3>
                <p style="margin-bottom: 16px; color: #94a3b8;">Surveillance heuristique continue contre les ransomwares, wipers et injections de processus.</p>
                <div style="background: rgba(0,0,0,0.3); padding: 14px; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.3);">
                    <div>• Protection Heuristique en direct : <strong style="color: #10b981;">ENGAGÉE</strong></div>
                    <div>• Démarrage Mesuré TPM 2.0 (PCR-7) : <strong style="color: #38bdf8;">VÉRIFIÉ</strong></div>
                    <div>• Version des signatures delta : <strong>2026.10.09.4201</strong></div>
                    <div>• Menaces neutralisées : <strong>14 bloquées (0 intrusion)</strong></div>
                </div>
                <button onclick="runWebScan()" style="margin-top: 16px; padding: 10px 18px; background: #10b981; color: #000; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">Lancer une analyse rapide</button>
                <div id="scan-res" style="margin-top: 12px; color: #a7f3d0;"></div>
            </div>
        </div>

        <!-- Window: Vault V: -->
        <div id="win-vault" class="window">
            <div class="window-header">
                <span>🔒 BitLocker Neo — Coffre-fort Chiffré (Drive V:)</span>
                <div class="window-controls">
                    <button class="win-btn win-close" onclick="closeWindow('win-vault')"></button>
                </div>
            </div>
            <div class="window-body">
                <h3 style="color: #c084fc; margin-bottom: 8px;">Volume Chiffré Matériellement (AES-256-GCM)</h3>
                <p style="color: #94a3b8; margin-bottom: 16px;">Ce volume en RAM est scellé avec les registres PCR du TPM 2.0 et verrouille la mémoire en cas d'inactivité.</p>
                <div style="background: rgba(0,0,0,0.3); padding: 14px; border-radius: 8px;">
                    <div>Statut : <span style="color: #22c55e; font-weight: bold;">DÉVERROUILLÉ (Monté sur V:)</span></div>
                    <div>Algorithme : <code>AES-256-GCM (Tag GMAC 128-bit)</code></div>
                    <div>Clé de récupération d'urgence : <code>481920-384910-582910-948102-184920-384910-948201-384920</code></div>
                </div>
            </div>
        </div>

        <!-- Window: Installer -->
        <div id="win-installer" class="window">
            <div class="window-header">
                <span>💿 Assistant d'Installation NovaOS (Setup Wizard)</span>
                <div class="window-controls">
                    <button class="win-btn win-close" onclick="closeWindow('win-installer')"></button>
                </div>
            </div>
            <div class="window-body">
                <h3 style="color: #38bdf8; margin-bottom: 8px;">Déploiement de NovaOS Hyperion 2026 sur Disque</h3>
                <p style="color: #94a3b8; margin-bottom: 16px;">Installez NovaOS de façon permanente sur NVMe / SSD avec chiffrement intégral LUKS2.</p>
                <div style="background: rgba(0,0,0,0.3); padding: 14px; border-radius: 8px; margin-bottom: 16px;">
                    <div>Cible détectée : <strong>Disque Virtuel 32 Go (Primary Storage)</strong></div>
                    <div>Disposition GPT : <code>ESP (512 Mo) + Recovery (1 Go) + Root LUKS2 (AES-256-XTS)</code></div>
                </div>
                <button id="btn-start-install" onclick="startWebInstall()" style="padding: 12px 24px; background: #0284c7; color: #fff; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">Lancer le formatage et l'installation</button>
                <div id="install-prog" style="margin-top: 16px;"></div>
            </div>
        </div>

        <!-- Start Menu -->
        <div id="start-menu" class="start-menu">
            <input type="text" class="start-search" placeholder="Rechercher des applications, fichiers, paramètres...">
            <div style="font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 700; margin-bottom: 12px;">Applications Épinglées</div>
            <div class="start-pinned-grid">
                <div class="start-item" onclick="openWindow('win-terminal'); toggleStartMenu();">
                    <span style="font-size: 20px;">>_</span>
                    <div><strong>Terminal</strong><br><small style="color: #94a3b8;">PowerShell Neo</small></div>
                </div>
                <div class="start-item" onclick="openWindow('win-defender'); toggleStartMenu();">
                    <span style="font-size: 20px;">🛡️</span>
                    <div><strong>Defender</strong><br><small style="color: #94a3b8;">Sécurité Hub</small></div>
                </div>
                <div class="start-item" onclick="openWindow('win-vault'); toggleStartMenu();">
                    <span style="font-size: 20px;">🔒</span>
                    <div><strong>Coffre V:</strong><br><small style="color: #94a3b8;">BitLocker Neo</small></div>
                </div>
                <div class="start-item" onclick="openWindow('win-installer'); toggleStartMenu();">
                    <span style="font-size: 20px;">💿</span>
                    <div><strong>Installateur</strong><br><small style="color: #94a3b8;">Déployer SSD</small></div>
                </div>
                <div class="start-item" onclick="openWindow('win-explorer'); toggleStartMenu();">
                    <span style="font-size: 20px;">📁</span>
                    <div><strong>Fichiers</strong><br><small style="color: #94a3b8;">Explorateur</small></div>
                </div>
                <div class="start-item" onclick="openWindow('win-settings'); toggleStartMenu();">
                    <span style="font-size: 20px;">⚙️</span>
                    <div><strong>Paramètres</strong><br><small style="color: #94a3b8;">Configuration</small></div>
                </div>
            </div>
            <div class="start-footer">
                <div>Session : <strong style="color: #38bdf8;">NovaAdmin (Administrateur)</strong></div>
                <div style="color: #94a3b8;">🛡️ Secure Boot Actif</div>
            </div>
        </div>

        <!-- Windows 11 Centered Taskbar -->
        <div class="taskbar">
            <div></div>
            <div class="taskbar-center">
                <button class="tb-btn start-btn" onclick="toggleStartMenu()" title="Menu Démarrer">❖</button>
                <button class="tb-btn" onclick="openWindow('win-terminal')" title="Terminal">>_</button>
                <button class="tb-btn" onclick="openWindow('win-defender')" title="Defender">🛡️</button>
                <button class="tb-btn" onclick="openWindow('win-vault')" title="Coffre V:">🔒</button>
                <button class="tb-btn" onclick="openWindow('win-installer')" title="Installateur">💿</button>
            </div>
            <div class="taskbar-tray">
                <div class="tray-badge">📶 Wi-Fi 6E</div>
                <div class="tray-badge">🛡️ TPM 2.0 OK</div>
                <div class="tray-badge">🔋 100%</div>
                <div id="tray-clock" style="font-weight: 600; color: #fff;">12:00:00</div>
            </div>
        </div>
    </div>

    <script>
        function updateClock() {
            const now = new Date();
            document.getElementById('tray-clock').textContent = now.toLocaleTimeString('fr-FR');
        }
        setInterval(updateClock, 1000);
        updateClock();

        function toggleStartMenu() {
            const menu = document.getElementById('start-menu');
            menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
        }

        function openWindow(id) {
            document.querySelectorAll('.window').forEach(w => w.style.display = 'none');
            const target = document.getElementById(id);
            if (target) target.style.display = 'flex';
        }

        function closeWindow(id) {
            const target = document.getElementById(id);
            if (target) target.style.display = 'none';
        }

        function handleDesktopClick(e) {
            const menu = document.getElementById('start-menu');
            if (menu.style.display === 'block' && !e.target.closest('#start-menu') && !e.target.closest('.start-btn')) {
                menu.style.display = 'none';
            }
        }

        // Terminal Interactive Simulator
        function handleTermKey(e) {
            if (e.key === 'Enter') {
                const input = document.getElementById('term-input');
                const cmd = input.value.trim();
                input.value = '';
                executeTermCmd(cmd);
            }
        }

        function executeTermCmd(cmd) {
            const log = document.getElementById('term-log');
            const p = document.createElement('div');
            p.innerHTML = `<span style="color: #38bdf8;">NovaOS:~#</span> ${cmd}`;
            log.appendChild(p);

            const res = document.createElement('div');
            const lower = cmd.toLowerCase();

            if (lower === 'help' || lower === '?') {
                res.innerHTML = `<pre style="color: #eab308;">Commandes disponibles:
  novafetch / neofetch : Télémétrie Windows 11 Neo
  defender             : État du bouclier antivirus temps réel
  scan                 : Lancer un scan heuristique de mémoire
  firewall             : État du pare-feu Zero-Trust NovaWall
  vault                : Statut du volume chiffré BitLocker Neo
  install              : Lancer l'assistant d'installation sur disque
  matrix               : Flux cybernétique néon
  clear                : Effacer l'écran</pre>`;
            } else if (lower === 'novafetch' || lower === 'neofetch') {
                res.innerHTML = `<pre style="color: #38bdf8;">   ######  ######     NovaAdmin@NovaOS-Workstation
   ######  ######     ----------------------------
   ######  ######     OS: NovaOS Hyperion 2026 (Windows 11 Neo)
   ######  ######     Kernel: x86_64 Hardened Microkernel (KASLR/PTI)
                      Shell: PowerShell Neo Cybernetic Edition
   ######  ######     Theme: Windows 11 Acrylic Cyan / Void Dark
   ######  ######     Memory: 2048 MB RAM (Cryptographic ZRAM)
   ######  ######     Security: Zero-Trust Military Grade (AES-256)
                      TPM: 2.0 PCR-7 Authenticated</pre>`;
            } else if (lower === 'defender') {
                res.innerHTML = `<pre style="color: #10b981;">Nova Defender - Real-Time Protection Hub:
  • Protection heuristique : ACTIVE
  • Protection mémoire : RING-0 LOCKED
  • Menaces interceptées : 14 bloquées (0 faille)</pre>`;
            } else if (lower === 'scan') {
                res.innerHTML = `<pre style="color: #eab308;">Analyse en cours... 256 secteurs vérifiés. 0 menace détectée. Système SÉCURISÉ.</pre>`;
            } else if (lower === 'firewall') {
                res.innerHTML = `<pre style="color: #38bdf8;">NovaWall Zero-Trust : Mode Furtif ACTIF (ICMP Drop). Paquets filtrés : 41,290.</pre>`;
            } else if (lower === 'vault') {
                res.innerHTML = `<pre style="color: #c084fc;">Drive V: DÉVERROUILLÉ. Protégé par AES-256-GCM + Argon2id.</pre>`;
            } else if (lower === 'matrix') {
                res.innerHTML = `<pre style="color: #22c55e;">01101110 01101111 01110110 01100001 01101111 01110011 01011111 01110011
01100101 01100011 01110101 01110010 01100101 01011111 00110010 00110000
QUANTUM MATRIX ENGAGED — SYSTEM HARDENED TO ZERO-TRUST LEVEL</pre>`;
            } else if (lower === 'install') {
                openWindow('win-installer');
                res.innerHTML = `<span style="color: #38bdf8;">Ouverture du Setup Wizard...</span>`;
            } else if (lower === 'clear') {
                log.innerHTML = '';
                return;
            } else if (cmd) {
                res.innerHTML = `<span style="color: #ef4444;">Commande inconnue: '${cmd}'. Tapez 'help' pour la liste.</span>`;
            }

            log.appendChild(res);
            const screen = document.getElementById('term-screen');
            screen.scrollTop = screen.scrollHeight;
        }

        function runWebScan() {
            const div = document.getElementById('scan-res');
            div.innerHTML = "Analyse heuristique en cours...";
            setTimeout(() => {
                div.innerHTML = "✅ Analyse terminée : 512 fichiers et descripteurs de mémoire inspectés. Aucune menace.";
            }, 800);
        }

        function startWebInstall() {
            const btn = document.getElementById('btn-start-install');
            btn.disabled = true;
            btn.style.opacity = 0.5;
            const prog = document.getElementById('install-prog');

            const steps = [
                "20% — Formatage de la table GPT et partition EFI (FAT32)...",
                "50% — Initialisation du conteneur LUKS2 AES-256-XTS...",
                "80% — Déploiement du noyau durci NovaOS et des modules de sécurité...",
                "100% — Finalisation de la NVRAM UEFI et création de la clé de secours !"
            ];

            let i = 0;
            const interval = setInterval(() => {
                if (i < steps.length) {
                    prog.innerHTML = `<div style="color: #38bdf8; font-weight: bold;">[${steps[i]}]</div>`;
                    i++;
                } else {
                    clearInterval(interval);
                    prog.innerHTML = `<div style="background: rgba(34, 197, 94, 0.2); border: 1px solid #22c55e; padding: 14px; border-radius: 8px; margin-top: 10px;">
                        <strong style="color: #22c55e;">✅ Installation terminée avec succès !</strong><br><br>
                        <strong>Clé d'Urgence BitLocker Neo :</strong><br>
                        <code style="font-size: 14px; color: #38bdf8;">481920-384910-582910-948102-184920-384910-948201-384920</code><br><br>
                        Vous pouvez redémarrer sur votre disque chiffré.
                    </div>`;
                }
            }, 700);
        }
    </script>
</body>
</html>
"""

class DownloadHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path.endswith(".iso") or parsed.path == "/download/NovaOS-v1.0-x86_64-LiveCD.iso":
            size = os.path.getsize(ISO_PATH) if os.path.exists(ISO_PATH) else 0
            self.send_response(200)
            self.send_header("Content-Type", "application/x-iso9660-image")
            self.send_header("Content-Length", str(size))
            self.send_header("Content-Disposition", 'attachment; filename="NovaOS-v1.0-x86_64-LiveCD.iso"')
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            content = HTML_PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        elif parsed.path.endswith(".iso") or parsed.path == "/download/NovaOS-v1.0-x86_64-LiveCD.iso":
            if not os.path.exists(ISO_PATH):
                self.send_error(404, "ISO file not found")
                return
            size = os.path.getsize(ISO_PATH)
            self.send_response(200)
            self.send_header("Content-Type", "application/x-iso9660-image")
            self.send_header("Content-Length", str(size))
            self.send_header("Content-Disposition", 'attachment; filename="NovaOS-v1.0-x86_64-LiveCD.iso"')
            self.end_headers()
            with open(ISO_PATH, "rb") as f:
                while chunk := f.read(65536):
                    self.wfile.write(chunk)
        elif parsed.path in ("/SHA256SUMS", "/dist/SHA256SUMS"):
            if os.path.exists(SHA_PATH):
                with open(SHA_PATH, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_error(404)
        else:
            self.send_error(404)

def run():
    server = HTTPServer(("0.0.0.0", 8080), DownloadHandler)
    print("NovaOS Live Preview & Download Portal running on 0.0.0.0:8080...")
    server.serve_forever()

if __name__ == "__main__":
    run()
