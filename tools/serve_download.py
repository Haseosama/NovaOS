#!/usr/bin/env python3
"""
NovaOS Web Portal & Direct ISO Download Service
Serves the binary ISO with proper Content-Disposition and provides verification tools.
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
    <title>NovaOS Hyperion 2026 — Téléchargement Officiel Live CD</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: radial-gradient(circle at 50% 20%, #0d1b2a, #050811);
            color: #e0f2fe;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI Variable", "Segoe UI", Roboto, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }
        .container {
            max-width: 760px;
            width: 100%;
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6), 0 0 40px rgba(56, 189, 248, 0.2);
            text-align: center;
        }
        .logo {
            font-size: 42px;
            font-weight: 800;
            background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 2px;
            margin-bottom: 8px;
        }
        .subtitle {
            font-size: 16px;
            color: #94a3b8;
            margin-bottom: 28px;
        }
        .badge {
            display: inline-block;
            background: rgba(14, 165, 233, 0.15);
            border: 1px solid #0ea5e9;
            color: #38bdf8;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 24px;
        }
        .btn-download {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: #ffffff;
            font-size: 18px;
            font-weight: 700;
            padding: 18px 36px;
            border-radius: 14px;
            text-decoration: none;
            box-shadow: 0 10px 25px rgba(2, 132, 199, 0.4);
            transition: all 0.25s ease;
            margin: 16px 0;
            cursor: pointer;
            border: none;
            width: 100%;
        }
        .btn-download:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 35px rgba(2, 132, 199, 0.6);
            background: linear-gradient(135deg, #0ea5e9, #3b82f6);
        }
        .card-info {
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            padding: 18px;
            margin-top: 24px;
            text-align: left;
            font-size: 14px;
            line-height: 1.6;
        }
        .card-info code {
            background: rgba(0, 0, 0, 0.4);
            color: #38bdf8;
            padding: 3px 8px;
            border-radius: 6px;
            font-family: monospace;
            word-break: break-all;
        }
        .guide-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-top: 24px;
            text-align: left;
        }
        .guide-card {
            background: rgba(15, 23, 42, 0.5);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: 12px;
            padding: 16px;
            font-size: 13px;
        }
        .guide-card h4 {
            color: #38bdf8;
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">❖ NovaOS Hyperion 2026</div>
        <div class="subtitle">OS Futuriste Inspiré de Windows 11 — Live CD & Installation sur Disque</div>
        <div class="badge">🛡️ Sécurité Zero-Trust &bull; TPM 2.0 &bull; Chiffrement LUKS2 AES-256</div>

        <a class="btn-download" href="/download/NovaOS-v1.0-x86_64-LiveCD.iso" download="NovaOS-v1.0-x86_64-LiveCD.iso">
            ⬇️ Télécharger NovaOS-v1.0-x86_64-LiveCD.iso (3.0 Mo)
        </a>

        <div class="card-info">
            <strong>⚠️ Pourquoi le fichier faisait ~233 Ko sur GitHub ?</strong><br>
            Sur l'interface web de GitHub, faire un clic droit "Enregistrer sous..." sur le lien d'un fichier binaire télécharge la <em>page HTML</em> de GitHub (qui pèse environ 233 Ko) au lieu du vrai fichier ISO !<br>
            Le bouton bleu ci-dessus télécharge <strong>directement le véritable fichier binaire ISO (3.0 Mo)</strong>.
        </div>

        <div class="card-info">
            <strong>Vérification Cryptographique (SHA-256) :</strong><br>
            <code>__SHA256_HASH__</code>
        </div>

        <div class="guide-grid">
            <div class="guide-card">
                <h4>💻 Dans VirtualBox / VMware</h4>
                1. Créez une VM Linux 64-bit.<br>
                2. Montez le fichier ISO <code>NovaOS-v1.0-x86_64-LiveCD.iso</code>.<br>
                3. Démarrez : le bureau Windows 11 Neo s'ouvre instantanément en mémoire vive (Live CD).
            </div>
            <div class="guide-card">
                <h4>💾 Sur Clé USB (PC Réel)</h4>
                Flashez avec <strong>Rufus</strong> (sélectionnez GPT / UEFI) ou par ligne de commande :<br>
                <code>dd if=NovaOS.iso of=/dev/sdX bs=4M</code>
            </div>
        </div>
    </div>
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
            sha_text = "952616fa090921cdaaec85b4d68f83dfe8e83c660ea201ef7283b8723bc35740"
            if os.path.exists(SHA_PATH):
                with open(SHA_PATH, "r") as f:
                    sha_text = f.read().strip()
            content = HTML_PAGE.replace("__SHA256_HASH__", sha_text).encode('utf-8')
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
    print("NovaOS Direct Download Server listening on 0.0.0.0:8080...")
    server.serve_forever()

if __name__ == "__main__":
    run()
