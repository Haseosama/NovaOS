"""
NovaOS Initramfs Generator
Packages NovaOS system root, security modules, shell, and init scripts into a bootable cpio.gz ramdisk.
"""

import os
import io
import gzip
import struct

def make_cpio_entry(filename: str, data: bytes, mode: int = 0o100755, mtime: int = 1728500000) -> bytes:
    """Creates a standard POSIX newc cpio entry."""
    # Magic "070701"
    name_bytes = filename.encode('ascii') + b'\x00'
    name_len = len(name_bytes)
    data_len = len(data)

    header = (
        f"070701"
        f"{1:08x}"           # ino
        f"{mode:08x}"        # mode
        f"{0:08x}"           # uid
        f"{0:08x}"           # gid
        f"{1:08x}"           # nlink
        f"{mtime:08x}"       # mtime
        f"{data_len:08x}"    # filesize
        f"{0:08x}"           # devmajor
        f"{0:08x}"           # devminor
        f"{0:08x}"           # rdevmajor
        f"{0:08x}"           # rdevminor
        f"{name_len:08x}"    # namesize
        f"{0:08x}"           # check
    ).encode('ascii')

    # Pad header + filename to 4 bytes
    pad_header = (4 - (len(header) + len(name_bytes)) % 4) % 4
    pad_data = (4 - data_len % 4) % 4

    return header + name_bytes + (b'\x00' * pad_header) + data + (b'\x00' * pad_data)

def make_cpio_trailer() -> bytes:
    return make_cpio_entry("TRAILER!!!", b"", mode=0)

def build_initramfs(output_path: str, files_dict: dict) -> int:
    """Builds a compressed initramfs (cpio.gz) containing the provided files."""
    bio = io.BytesIO()
    for filename, content in files_dict.items():
        if isinstance(content, str):
            content = content.encode('utf-8')
        bio.write(make_cpio_entry(filename, content))
    bio.write(make_cpio_trailer())
    
    raw_cpio = bio.getvalue()
    with gzip.open(output_path, "wb") as f_out:
        f_out.write(raw_cpio)

    return os.path.getsize(output_path)
