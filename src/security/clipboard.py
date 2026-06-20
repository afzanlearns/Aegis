import threading
import time
from typing import Optional

try:
    import pyperclip
except ImportError:
    pyperclip = None


class ClipboardManager:
    """Secure clipboard operations with auto-clear functionality."""

    AUTO_CLEAR_SECONDS = 30
    _clear_timer: Optional[threading.Timer] = None
    _lock = threading.Lock()

    @classmethod
    def copy(cls, text: str) -> None:
        """Copy text to clipboard and schedule auto-clear."""
        if pyperclip is None:
            raise RuntimeError(
                "pyperclip is not installed. Install it with: pip install pyperclip"
            )

        cls._cancel_clear()
        pyperclip.copy(text)

        cls._clear_timer = threading.Timer(cls.AUTO_CLEAR_SECONDS, cls._clear)
        cls._clear_timer.daemon = True
        cls._clear_timer.start()

    @classmethod
    def _clear(cls) -> None:
        """Clear the clipboard contents."""
        with cls._lock:
            try:
                if pyperclip:
                    pyperclip.copy("")
            except Exception:
                pass
            cls._clear_timer = None

    @classmethod
    def _cancel_clear(cls) -> None:
        """Cancel a pending clipboard clear."""
        with cls._lock:
            if cls._clear_timer and cls._clear_timer.is_alive():
                cls._clear_timer.cancel()
            cls._clear_timer = None

    @classmethod
    def get_clear_remaining(cls) -> int:
        """Return seconds remaining before clipboard auto-clear."""
        return cls.AUTO_CLEAR_SECONDS


def secure_copy(text: str) -> None:
    """Convenience function to copy and auto-clear."""
    ClipboardManager.copy(text)
