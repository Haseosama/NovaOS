"""
NovaOS Military-Grade Secure File Shredder
Complies with DoD 5220.22-M (7-pass overwrite) to permanently destroy forensic remnants.
"""

import os

class NovaShredder:
    """Performs multi-pass military-grade data sanitization."""

    @staticmethod
    def shred_file(file_path: str, passes: int = 7) -> bool:
        """Securely shred a file on disk."""
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return False

        length = os.path.getsize(file_path)
        if length == 0:
            os.remove(file_path)
            return True

        patterns = [
            b'\x00',         # Pass 1: Zeroes
            b'\xFF',         # Pass 2: Ones
            b'\xAA',         # Pass 3: Alternate 10101010
            b'\x55',         # Pass 4: Alternate 01010101
            None,            # Pass 5: Cryptographic Random
            None,            # Pass 6: Cryptographic Random
            b'\x00',         # Pass 7: Final zero flush
        ]

        with open(file_path, "br+", buffering=0) as f:
            for p in patterns[:passes]:
                f.seek(0)
                if p is None:
                    # Write cryptographic random
                    f.write(os.urandom(length))
                else:
                    f.write(p * length)
                f.flush()
                os.fsync(f.fileno())

        # Truncate and unlink
        with open(file_path, "w") as f:
            pass
        os.remove(file_path)
        return True
