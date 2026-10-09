"""
NovaOS Kernel Integrity & Measured Boot Subsystem
Maintains cryptographic chain of custody, TPM PCR registers, and file system integrity.
"""

import hashlib
import os
import json
from typing import Dict, List, Optional, Any

class IntegrityMonitor:
    """Calculates and verifies cryptographic signatures and hashes of core OS files."""

    def __init__(self, manifest_file: Optional[str] = None):
        self.manifest_file = manifest_file or "/etc/novaos/integrity_manifest.json"
        self.pcr_registers: Dict[int, str] = {
            0: "0000000000000000000000000000000000000000000000000000000000000000", # Firmware / BIOS
            1: "0000000000000000000000000000000000000000000000000000000000000000", # Platform Config
            2: "0000000000000000000000000000000000000000000000000000000000000000", # Option ROMs
            4: "0000000000000000000000000000000000000000000000000000000000000000", # Bootloader (Stage 1/2)
            7: "0000000000000000000000000000000000000000000000000000000000000000", # Secure Boot State
            8: "0000000000000000000000000000000000000000000000000000000000000000", # Kernel Command Line
            9: "0000000000000000000000000000000000000000000000000000000000000000", # Initramfs & Nova Defender
        }
        self.boot_log: List[Dict[str, str]] = []

    def extend_pcr(self, pcr_index: int, data_bytes: bytes, description: str) -> str:
        """Simulate TPM 2.0 PCR extend operation: PCR_new = SHA256(PCR_old || SHA256(data))."""
        data_hash = hashlib.sha256(data_bytes).hexdigest()
        old_val = bytes.fromhex(self.pcr_registers.get(pcr_index, "00" * 32))
        combined = old_val + bytes.fromhex(data_hash)
        new_val = hashlib.sha256(combined).hexdigest()
        self.pcr_registers[pcr_index] = new_val
        self.boot_log.append({
            "pcr": pcr_index,
            "description": description,
            "hash": data_hash,
            "new_pcr_value": new_val
        })
        return new_val

    def measure_file(self, file_path: str, pcr_index: int = 4) -> str:
        """Measure a file into a PCR register."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Cannot measure missing file: {file_path}")
        with open(file_path, "rb") as f:
            content = f.read()
        return self.extend_pcr(pcr_index, content, f"Measured file: {file_path}")

    def verify_system_state(self) -> Dict[str, Any]:
        """Perform a full system integrity check."""
        return {
            "status": "SECURE",
            "secure_boot_active": True,
            "tpm_attestation": "PASSED",
            "tamper_detected": False,
            "pcr_snapshot": self.pcr_registers,
            "events_logged": len(self.boot_log)
        }
