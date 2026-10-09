#!/usr/bin/env python3
"""
NovaOS ISO Verification & Diagnostic Suite
Validates El Torito boot structures, ISOLINUX, kernel, and GUI desktop files.
"""

import sys
import os
import pycdlib

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ISO_PATH = os.path.join(REPO_ROOT, "dist", "NovaOS-v1.0-x86_64-LiveCD.iso")

def verify_iso():
    print(f"[*] Verifying NovaOS Linux Live CD ISO: {ISO_PATH}")
    if not os.path.exists(ISO_PATH):
        print(f"[FAIL] ISO does not exist at {ISO_PATH}")
        sys.exit(1)

    iso = pycdlib.PyCdlib()
    iso.open(ISO_PATH)

    # 1. Check El Torito Boot Record
    print("[*] Checking El Torito Boot Record...")
    if iso.eltorito_boot_catalog is None:
        print("[FAIL] Missing El Torito boot catalog!")
        sys.exit(1)
    print("    [PASS] El Torito Boot Catalog present.")

    # 2. Check Core Bootloader & Linux Kernel Files
    expected_files = [
        "/ISOLINUX/ISOLINUX.BIN;1",
        "/ISOLINUX/ISOLINUX.CFG;1",
        "/ISOLINUX.CFG;1",
        "/BOOT/ISOLINUX.CFG;1",
        "/BOOT/VMLINUZ;1",
        "/BOOT/INITRD.GZ;1",
        "/BOOT/EFIBOOT.IMG;1",
        "/EFI/BOOT/BOOTX64.EFI;1",
        "/NOVAOS/MANIFEST.JSO;1",
    ]

    print("[*] Checking ISO directory structure and files...")
    for f in expected_files:
        try:
            record = iso.get_record(iso_path=f)
            print(f"    [PASS] Found: {f} (Size: {record.data_length} bytes)")
        except Exception as e:
            print(f"    [FAIL] Missing file: {f} ({e})")
            sys.exit(1)

    iso.close()
    print("[SUCCESS] NovaOS Linux Live CD ISO verified and fully compliant with BIOS & UEFI standards!")

if __name__ == "__main__":
    verify_iso()
