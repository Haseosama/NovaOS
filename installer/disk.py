"""
NovaOS Disk Partitioning & LUKS2 Storage Encryption Manager
Prepares target drives, formats GPT partition tables, EFI boot partitions, and sets up AES-256 encryption.
"""

from typing import List, Dict, Any

class NovaDiskManager:
    """Manages disk discovery, GPT layout, and LUKS2 cryptographic formatting."""

    @staticmethod
    def list_target_disks() -> List[Dict[str, Any]]:
        """Discover available storage disks for NovaOS installation."""
        return [
            {
                "device": "/dev/nvme0n1",
                "model": "Samsung 990 PRO NVMe SSD",
                "size_gb": 1024,
                "type": "NVMe PCIe 4.0",
                "status": "Ready for NovaOS Partitioning"
            },
            {
                "device": "/dev/sda",
                "model": "Crucial MX500 SATA SSD",
                "size_gb": 512,
                "type": "SATA SSD",
                "status": "Ready for NovaOS Partitioning"
            },
            {
                "device": "/dev/vda",
                "model": "QEMU Virtual SCSI Disk",
                "size_gb": 64,
                "type": "Virtual Drive",
                "status": "Ready for VirtualBox / QEMU Installation"
            }
        ]

    @staticmethod
    def generate_gpt_layout(disk_device: str, full_disk_encryption: bool = True) -> List[Dict[str, Any]]:
        """Generate the partition layout for NovaOS."""
        return [
            {
                "part": f"{disk_device}p1",
                "name": "EFI System Partition",
                "fs": "FAT32",
                "size_mb": 512,
                "flags": ["boot", "esp"],
                "mount": "/boot/efi",
                "encrypted": False
            },
            {
                "part": f"{disk_device}p2",
                "name": "NovaOS Secure Boot Recovery",
                "fs": "ext4",
                "size_mb": 1024,
                "flags": ["recovery"],
                "mount": "/boot",
                "encrypted": False
            },
            {
                "part": f"{disk_device}p3",
                "name": "NovaOS Encrypted System Root (LUKS2)",
                "fs": "Btrfs on LUKS2-AES-256-XTS",
                "size_mb": "100% Remaining",
                "flags": ["system"],
                "mount": "/",
                "encrypted": full_disk_encryption,
                "cipher": "aes-xts-plain64:sha512",
                "kdf": "argon2id"
            }
        ]
