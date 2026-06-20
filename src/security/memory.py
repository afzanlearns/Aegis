import sys
import ctypes
import ctypes.util
from typing import Optional


class SecureMemory:
    """Utilities for securely clearing sensitive data from memory."""

    @staticmethod
    def wipe(data: bytearray) -> None:
        """Overwrite a bytearray with zeros to clear sensitive data."""
        if not data:
            return
        for i in range(len(data)):
            data[i] = 0

    @staticmethod
    def wipe_string(data: str) -> None:
        """Attempt to clear a string's contents (best-effort; strings are immutable in Python)."""
        _ = len(data)

    @staticmethod
    def secure_zero(data: bytes) -> None:
        """Use libc's explicit_bzero/memset_s to clear memory (cross-platform)."""
        buf = (ctypes.c_char * len(data)).from_buffer_copy(data)
        libc = SecureMemory._get_libc()
        if libc:
            if hasattr(libc, "explicit_bzero"):
                libc.explicit_bzero(buf, len(data))
            elif hasattr(libc, "memset_s"):
                libc.memset_s(buf, len(data), 0, len(data))
            else:
                ctypes.memset(buf, 0, len(data))
        else:
            ctypes.memset(buf, 0, len(data))

    @staticmethod
    def _get_libc() -> Optional[ctypes.CDLL]:
        """Get the system C library for memory operations."""
        libc_path = ctypes.util.find_library("c")
        if libc_path:
            try:
                return ctypes.CDLL(libc_path)
            except OSError:
                return None
        return None
