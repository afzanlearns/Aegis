import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from exceptions import SessionExpiredError


class SessionManager:
    """Manage authenticated sessions with timeout enforcement."""

    DEFAULT_TIMEOUT = 1800

    def __init__(self, session_file: Path):
        self.session_file = session_file

    def create(self, key: bytes, timeout: int | None = None) -> None:
        """Create a new session file with derived key and expiry."""
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT

        now = datetime.now()
        session_data = {
            "authenticated_at": now.isoformat(),
            "expires_at": (now + timedelta(seconds=timeout)).isoformat(),
            "key": key.hex(),
        }
        self.session_file.write_text(json.dumps(session_data, indent=2))
        self.session_file.chmod(0o600)

    def is_valid(self) -> bool:
        """Check if the current session is still valid."""
        session = self._load()
        if session is None:
            return False

        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.now() > expires_at:
            self.destroy()
            return False
        return True

    def get_key(self) -> bytes:
        """Get the encryption key from the current session."""
        session = self._load()
        if session is None:
            raise SessionExpiredError("No active session")

        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.now() > expires_at:
            self.destroy()
            raise SessionExpiredError("Session has expired")

        return bytes.fromhex(session["key"])

    def expires_at(self) -> Optional[datetime]:
        """Return the session expiry time, or None if no session."""
        session = self._load()
        if session is None:
            return None
        return datetime.fromisoformat(session["expires_at"])

    def destroy(self) -> None:
        """Remove the session file and clear session data."""
        if self.session_file.exists():
            self.session_file.unlink()

    def _load(self) -> Optional[dict]:
        """Load session data from file."""
        if not self.session_file.exists():
            return None
        try:
            return json.loads(self.session_file.read_text())
        except (json.JSONDecodeError, OSError):
            return None
