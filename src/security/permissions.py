import os
import stat
from pathlib import Path


def enforce_file_permissions(path: Path, mode: int = 0o600) -> None:
    """Set restrictive file permissions (owner-only). Windows is best-effort."""
    if os.name == "posix":
        try:
            current = stat.S_IMODE(path.stat().st_mode)
            if current != mode:
                path.chmod(mode)
        except OSError:
            pass


def enforce_dir_permissions(path: Path, mode: int = 0o700) -> None:
    """Set restrictive directory permissions (owner-only). Windows is best-effort."""
    if os.name == "posix":
        try:
            current = stat.S_IMODE(path.stat().st_mode)
            if current != mode:
                path.chmod(mode)
        except OSError:
            pass


def check_file_permissions(path: Path) -> bool:
    """Check that file permissions are sufficiently restrictive."""
    if os.name != "posix":
        return True
    try:
        current = stat.S_IMODE(path.stat().st_mode)
        return current <= 0o700
    except OSError:
        return False
