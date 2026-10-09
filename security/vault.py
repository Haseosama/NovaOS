"""
NovaOS BitLocker Neo / Secure Encrypted Vault
Provides encrypted volume management with AES-256-GCM, automated locking, and BitLocker recovery key support.
"""

import os
import json
import time
from typing import Dict, List, Optional
from security.crypto_engine import NovaCryptoEngine

class NovaVault:
    """Encrypted storage container (equivalent to BitLocker Virtual Drive)."""

    def __init__(self, vault_path: str = "/tmp/novaos_vault.nvault"):
        self.vault_path = vault_path
        self.is_unlocked: bool = False
        self._master_key_hash: Optional[str] = None
        self._cached_passphrase: Optional[str] = None
        self.files: Dict[str, bytes] = {}
        self.metadata: Dict[str, any] = {
            "created_at": time.time(),
            "cipher": "AES-256-GCM-600K-PBKDF2",
            "recovery_key": "",
            "volume_label": "NovaOS Secure Vault (Drive V:)",
            "lock_timeout_sec": 300,
            "last_activity": time.time(),
        }

    def initialize(self, passphrase: str) -> str:
        """Create a new encrypted vault and return the generated 48-digit BitLocker recovery key."""
        recovery_key = NovaCryptoEngine.generate_recovery_key()
        self.metadata["recovery_key"] = recovery_key
        self._cached_passphrase = passphrase
        self.is_unlocked = True
        
        # Add default secure system files
        self.files["welcome.txt"] = b"=== NovaOS Secure Vault (Drive V:) ===\nProtected with military-grade AES-256-GCM encryption.\n"
        self.files["security_policy.conf"] = b"ZERO_TRUST=1\nENFORCE_SELINUX=1\nTPM_MEASURED_BOOT=1\n"
        
        self.save()
        return recovery_key

    def unlock(self, key_or_passphrase: str) -> bool:
        """Unlock vault using user password/PIN or the BitLocker 48-digit recovery key."""
        if not os.path.exists(self.vault_path):
            return False
            
        with open(self.vault_path, "r", encoding="utf-8") as f:
            envelope = json.load(f)
            
        try:
            # Attempt decryption with provided credential
            decrypted_raw = NovaCryptoEngine.decrypt_data(envelope["encrypted_body"], key_or_passphrase)
            unpacked = json.loads(decrypted_raw.decode('utf-8'))
            
            self.metadata = unpacked["metadata"]
            self.files = {k: base64_to_bytes(v) for k, v in unpacked["files"].items()}
            self._cached_passphrase = key_or_passphrase
            self.is_unlocked = True
            self.metadata["last_activity"] = time.time()
            return True
        except Exception:
            # Check if unlocking via Recovery Key
            if "recovery_encrypted_body" in envelope:
                try:
                    decrypted_raw = NovaCryptoEngine.decrypt_data(envelope["recovery_encrypted_body"], key_or_passphrase)
                    unpacked = json.loads(decrypted_raw.decode('utf-8'))
                    self.metadata = unpacked["metadata"]
                    self.files = {k: base64_to_bytes(v) for k, v in unpacked["files"].items()}
                    self._cached_passphrase = key_or_passphrase
                    self.is_unlocked = True
                    return True
                except Exception:
                    pass
            return False

    def lock(self) -> None:
        """Lock the vault and clear memory contents."""
        if self.is_unlocked:
            self.save()
        self.files.clear()
        self._cached_passphrase = None
        self.is_unlocked = False

    def save(self) -> None:
        """Encrypt and serialize vault state to disk."""
        if not self.is_unlocked or not self._cached_passphrase:
            return
            
        payload = {
            "metadata": self.metadata,
            "files": {k: bytes_to_base64(v) for k, v in self.files.items()}
        }
        raw_bytes = json.dumps(payload).encode('utf-8')
        encrypted_body = NovaCryptoEngine.encrypt_data(raw_bytes, self._cached_passphrase)
        
        # Also encrypt with recovery key
        recovery_body = NovaCryptoEngine.encrypt_data(raw_bytes, self.metadata["recovery_key"])
        
        envelope = {
            "version": "1.0",
            "type": "NovaOS.BitLockerNeo.Container",
            "encrypted_body": encrypted_body,
            "recovery_encrypted_body": recovery_body
        }
        
        os.makedirs(os.path.dirname(os.path.abspath(self.vault_path)), exist_ok=True)
        with open(self.vault_path, "w", encoding="utf-8") as f:
            json.dump(envelope, f, indent=2)

    def write_file(self, filename: str, content: bytes) -> None:
        if not self.is_unlocked:
            raise PermissionError("Vault is locked")
        self.files[filename] = content
        self.metadata["last_activity"] = time.time()
        self.save()

    def read_file(self, filename: str) -> bytes:
        if not self.is_unlocked:
            raise PermissionError("Vault is locked")
        if filename not in self.files:
            raise FileNotFoundError(f"File '{filename}' not found in vault")
        return self.files[filename]

    def list_files(self) -> List[Dict[str, any]]:
        if not self.is_unlocked:
            return []
        return [{"name": name, "size": len(data), "modified": time.time()} for name, data in self.files.items()]

def bytes_to_base64(b: bytes) -> str:
    import base64
    return base64.b64encode(b).decode('ascii')

def base64_to_bytes(s: str) -> bytes:
    import base64
    return base64.b64decode(s.encode('ascii'))
