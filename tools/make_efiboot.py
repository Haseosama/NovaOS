"""
NovaOS EFI Boot Image Generator
Creates a standard FAT12/FAT16 EFI System Partition image (efiboot.img)
containing /EFI/BOOT/BOOTX64.EFI for El Torito UEFI boot.
"""

import os
import struct

def create_fat12_efi_image(output_path: str, efi_binary_path: str) -> int:
    """Creates a 2.88MB FAT12 disk image with /EFI/BOOT/BOOTX64.EFI."""
    total_sectors = 5760 # 2.88 MB
    bytes_per_sector = 512
    total_bytes = total_sectors * bytes_per_sector

    with open(efi_binary_path, "rb") as f:
        efi_data = f.read()

    efi_size = len(efi_data)
    sectors_per_cluster = 1
    reserved_sectors = 1
    num_fats = 2
    root_entries = 224
    sectors_per_fat = 9
    root_dir_sectors = (root_entries * 32 + bytes_per_sector - 1) // bytes_per_sector

    img = bytearray(total_bytes)

    # Boot Sector (BPB)
    img[0:3] = b'\xeb\x3c\x90'
    img[3:11] = b'MSWIN4.1'
    struct.pack_into('<H', img, 11, bytes_per_sector)
    img[13] = sectors_per_cluster
    struct.pack_into('<H', img, 14, reserved_sectors)
    img[16] = num_fats
    struct.pack_into('<H', img, 17, root_entries)
    struct.pack_into('<H', img, 19, total_sectors)
    img[21] = 0xF0 # 3.5" floppy / disk
    struct.pack_into('<H', img, 22, sectors_per_fat)
    struct.pack_into('<H', img, 24, 18) # sectors per track
    struct.pack_into('<H', img, 26, 2)  # num heads
    img[38] = 0x29 # extended boot signature
    struct.pack_into('<I', img, 39, 0x12345678)
    img[43:54] = b'NOVAOS_EFI '
    img[54:62] = b'FAT12   '
    img[510:512] = b'\x55\xaa'

    # FAT Tables (FAT1 and FAT2)
    fat1_offset = reserved_sectors * bytes_per_sector
    fat2_offset = (reserved_sectors + sectors_per_fat) * bytes_per_sector
    img[fat1_offset:fat1_offset+3] = b'\xf0\xff\xff'
    img[fat2_offset:fat2_offset+3] = b'\xf0\xff\xff'

    # Root Directory
    root_dir_offset = (reserved_sectors + num_fats * sectors_per_fat) * bytes_per_sector
    data_cluster_offset = root_dir_offset + (root_dir_sectors * bytes_per_sector)

    # Cluster 2: EFI Directory
    # Directory entry in Root for 'EFI        ' (Attr: 0x10 Directory)
    img[root_dir_offset:root_dir_offset+11] = b'EFI        '
    img[root_dir_offset+11] = 0x10 # Subdirectory
    struct.pack_into('<H', img, root_dir_offset+26, 2) # First cluster = 2

    # Cluster 3: BOOT Directory
    efi_dir_offset = data_cluster_offset + (2 - 2) * bytes_per_sector * sectors_per_cluster
    img[efi_dir_offset:efi_dir_offset+11] = b'BOOT       '
    img[efi_dir_offset+11] = 0x10
    struct.pack_into('<H', img, efi_dir_offset+26, 3)

    # Cluster 4+: BOOTX64.EFI
    boot_dir_offset = data_cluster_offset + (3 - 2) * bytes_per_sector * sectors_per_cluster
    img[boot_dir_offset:boot_dir_offset+11] = b'BOOTX64 EFI'
    img[boot_dir_offset+11] = 0x20 # Archive
    struct.pack_into('<H', img, boot_dir_offset+26, 4) # First cluster = 4
    struct.pack_into('<I', img, boot_dir_offset+28, efi_size)

    # Write EFI binary data starting at Cluster 4
    file_cluster_offset = data_cluster_offset + (4 - 2) * bytes_per_sector * sectors_per_cluster
    img[file_cluster_offset:file_cluster_offset+efi_size] = efi_data

    # Update FAT table for clusters 2, 3, 4..N
    clusters_needed = (efi_size + bytes_per_sector - 1) // bytes_per_sector
    
    # Helper to set FAT12 entry
    def set_fat12_entry(cluster, value):
        for base in [fat1_offset, fat2_offset]:
            offset = base + (cluster * 3) // 2
            if cluster % 2 == 0:
                img[offset] = value & 0xFF
                img[offset+1] = (img[offset+1] & 0xF0) | ((value >> 8) & 0x0F)
            else:
                img[offset] = (img[offset] & 0x0F) | ((value << 4) & 0xF0)
                img[offset+1] = (value >> 4) & 0xFF

    set_fat12_entry(2, 0xFFF) # EOF for EFI dir
    set_fat12_entry(3, 0xFFF) # EOF for BOOT dir
    start_c = 4
    for i in range(clusters_needed):
        cur = start_c + i
        nxt = 0xFFF if i == clusters_needed - 1 else cur + 1
        set_fat12_entry(cur, nxt)

    with open(output_path, "wb") as f_out:
        f_out.write(img)

    return os.path.getsize(output_path)
