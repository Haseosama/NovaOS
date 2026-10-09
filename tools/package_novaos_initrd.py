#!/usr/bin/env python3
"""
NovaOS Initramfs Packaging Tool
Packages the Windows 11 Desktop Shell into the Linux Live CD rootfs.
"""

import os
import sys
import subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.make_initramfs import build_initramfs

BOOT_DIR = os.path.join(REPO_ROOT, "boot")
LIVECD_DIR = os.path.join(BOOT_DIR, "livecd")

def package_initrd():
    print("[*] Compiling NovaOS Windows 11 Desktop Engine (Static ELF x86_64)...")
    subprocess.run(["gcc", "-static", "-O2", os.path.join(BOOT_DIR, "novaos-desktop.c"), "-o", os.path.join(BOOT_DIR, "novaos-desktop")], check=True)
    subprocess.run(["strip", "-s", os.path.join(BOOT_DIR, "novaos-desktop")], check=True)

    subprocess.run(["gcc", "-static", "-O2", f"-I{BOOT_DIR}", os.path.join(BOOT_DIR, "novaos-gui.c"), "-o", os.path.join(BOOT_DIR, "novaos-gui"), "-lm"], check=True)
    subprocess.run(["strip", "-s", os.path.join(BOOT_DIR, "novaos-gui")], check=True)

    with open(os.path.join(BOOT_DIR, "novaos-desktop"), "rb") as f:
        desktop_bytes = f.read()

    with open(os.path.join(BOOT_DIR, "novaos-gui"), "rb") as f:
        gui_bytes = f.read()

    launcher_script = """#!/bin/sh
export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin
export TERM=linux
if [ -c /dev/fb0 ] && /bin/novaos-gui --test 2>/dev/null; then
    /bin/novaos-gui "$@" 2>/dev/null || /bin/novaos-desktop "$@"
else
    /bin/novaos-desktop "$@"
fi
"""

    autostart_script = """#!/bin/sh
# Auto-start NovaOS Windows 11 Desktop on login
if [ -z "$NOVAOS_STARTED" ]; then
    export NOVAOS_STARTED=1
    exec /bin/novaos
fi
"""

    autologin_script = """#!/bin/busybox ash
exec login -f tc
"""

    shadow_content = """root::13525:0:99999:7:::
lp:*:13510:0:99999:7:::
nobody:*:13509:0:99999:7:::
tc::13646:0:99999:7:::
"""

    overlay_files = {
        "bin/novaos-desktop": desktop_bytes,
        "bin/novaos-gui": gui_bytes,
        "bin/novaos": launcher_script,
        "usr/bin/novaos": launcher_script,
        "sbin/autologin": autologin_script,
        "etc/shadow": shadow_content,
        "etc/profile.d/novaos.sh": autostart_script,
        "home/tc/.profile": autostart_script,
        "opt/bootlocal.sh": """#!/bin/sh
# NovaOS boot initialization
dmesg -n 1
""",
        "etc/issue": """
   NovaOS Hyperion 2026 - Windows 11 Secure Edition (x86_64)
   Login: tc (No password - Press Enter) | Root: root (No password)
   Type 'novaos' to launch Windows 11 Neo Desktop
""",
        "etc/os-release": """NAME="NovaOS"
VERSION="1.0 Hyperion 2026 (Windows 11 Neo)"
ID=novaos
PRETTY_NAME="NovaOS Hyperion 2026 Edition"
"""
    }

    overlay_path = "/tmp/novaos_overlay.cpio.gz"
    build_initramfs(overlay_path, overlay_files)

    # Base rootfs
    base_rootfs = "/tmp/tc-build/10.x/corepure64.gz"
    if not os.path.exists(base_rootfs):
        base_rootfs = os.path.join(LIVECD_DIR, "corepure64.gz")
    if not os.path.exists(base_rootfs):
        base_rootfs = os.path.join(LIVECD_DIR, "initrd.gz")

    final_initrd = os.path.join(LIVECD_DIR, "initrd.gz")
    print(f"[*] Concatenating base rootfs ({base_rootfs}) + NovaOS Windows 11 Desktop overlay...")

    with open(base_rootfs, "rb") as f1, open(overlay_path, "rb") as f2, open(final_initrd, "wb") as fout:
        fout.write(f1.read())
        fout.write(f2.read())

    print(f"[SUCCESS] Packaged {final_initrd}: {os.path.getsize(final_initrd)} bytes")

if __name__ == "__main__":
    package_initrd()
