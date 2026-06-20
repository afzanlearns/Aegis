import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from core.crypto import CryptoManager
from core.key_derivation import KeyDerivation
from core.session import SessionManager
from core.config import ConfigManager
from core.models import SecretEntry
from storage.database import DatabaseManager
from storage.audit_log import AuditLogger
from security.clipboard import secure_copy
from security.permissions import enforce_file_permissions, enforce_dir_permissions
from exceptions import (
    VaultNotInitializedError, AuthenticationError, WeakPasswordError,
    RateLimitError, SecretNotFoundError, DecryptionError, ExportError,
)


class VaultManager:
    """Central vault orchestrator — manages auth, encryption, storage, and audit."""

    MAX_AUTH_ATTEMPTS = 3
    RATE_LOCKOUT_MINUTES = 5

    def __init__(self, vault_dir: Optional[Path] = None):
        if vault_dir is None:
            vault_dir = Path.home() / ".aegis"
        self.vault_dir = vault_dir
        self.vault_dir.mkdir(exist_ok=True)
        enforce_dir_permissions(self.vault_dir, 0o700)

        self.db_path = self.vault_dir / "secrets.db"
        self.config_path = self.vault_dir / "config.json"
        self.session_file = self.vault_dir / ".session"
        self.lockout_file = self.vault_dir / ".lockout"

        self.db = DatabaseManager(self.db_path)
        self.audit = AuditLogger(self.db_path)
        self.config_mgr = ConfigManager(self.config_path)
        self.session = SessionManager(self.session_file)

        enforce_file_permissions(self.db_path, 0o600)

    def setup(self, master_password: str) -> bool:
        """Initialize vault with master password. Called once during first use."""
        if self.config_mgr.is_initialized():
            raise ValueError("Vault already initialized")

        if len(master_password) < 12:
            raise WeakPasswordError("Master password must be at least 12 characters")

        if not self._is_strong_password(master_password):
            raise WeakPasswordError("Password too weak — use uppercase, lowercase, numbers, and symbols")

        key, salt = KeyDerivation.derive_key_argon2(master_password)
        password_hash = KeyDerivation.hash_password(master_password, salt)

        config = {
            "version": "1.0",
            "password_hash": password_hash,
            "salt": salt.hex(),
            "initialized_at": datetime.now().isoformat(),
            "max_session_timeout": 1800,
        }
        self.config_mgr.save(config)
        enforce_file_permissions(self.config_path, 0o600)

        self.audit.log("vault_initialized", None, True)
        return True

    def authenticate(self, master_password: str) -> bool:
        """Authenticate to vault with master password. Establishes a session."""
        self._check_lockout()

        if not self.config_mgr.is_initialized():
            raise VaultNotInitializedError("Vault not initialized. Run 'aegis setup' first")

        config = self.config_mgr.load()
        salt = bytes.fromhex(config["salt"])

        if not KeyDerivation.verify_password(master_password, salt, config["password_hash"]):
            self._record_failed_attempt()
            self.audit.log("auth_failed", None, False, "Invalid password")
            raise AuthenticationError("Invalid master password")

        key, _ = KeyDerivation.derive_key_argon2(master_password, salt)
        timeout = config.get("max_session_timeout", 1800)
        self.session.create(key, timeout)
        self._clear_lockout()

        self.audit.log("auth_success", None, True)
        return True

    def is_authenticated(self) -> bool:
        """Check if the current session is valid."""
        return self.session.is_valid()

    def save_secret(self, name: str, value: str, tag: str = "general") -> bool:
        """Save an encrypted secret."""
        self._require_auth()

        if not name or len(name) > 100:
            raise ValueError("Invalid secret name — must be 1-100 characters")

        key = self.session.get_key()
        ciphertext, nonce, auth_tag = CryptoManager.encrypt(value, key)

        now = datetime.now()
        entry = SecretEntry(
            name=name, user_tag=tag,
            encrypted_value=ciphertext, nonce=nonce, auth_tag=auth_tag,
            created_at=now, updated_at=now,
        )

        self.db.save_secret(entry)
        self.audit.log("save_secret", name, True)
        return True

    def get_secret(self, name: str, copy: bool = False) -> str:
        """Retrieve and decrypt a secret. Optionally copy to clipboard."""
        self._require_auth()
        key = self.session.get_key()

        entry = self.db.get_secret(name)
        try:
            plaintext = CryptoManager.decrypt(
                entry.encrypted_value, key, entry.nonce, entry.auth_tag
            )
        except DecryptionError:
            self.audit.log("get_secret", name, False, "Decryption failed")
            raise DecryptionError("Failed to decrypt secret — key may have changed or data is corrupted")

        self.audit.log("get_secret", name, True)

        if copy:
            secure_copy(plaintext)

        return plaintext

    def list_secrets(self) -> List[Dict]:
        """List all stored secrets with metadata (values redacted)."""
        self._require_auth()
        return self.db.list_secrets()

    def list_secrets_by_tag(self, tag: str) -> List[Dict]:
        """List secrets filtered by tag."""
        self._require_auth()
        return self.db.list_secrets_by_tag(tag)

    def search_secrets(self, query: str) -> List[Dict]:
        """Search secrets by name."""
        self._require_auth()
        return self.db.search_secrets(query)

    def delete_secret(self, name: str) -> bool:
        """Delete a secret by name."""
        self._require_auth()
        self.db.delete_secret(name)
        self.audit.log("delete_secret", name, True)
        return True

    def generate_password(self, length: int = 32, symbols: bool = True) -> str:
        """Generate a cryptographically secure random password."""
        import string
        chars = string.ascii_letters + string.digits
        if symbols:
            chars += "!@#$%^&*()_+-=[]{}|:;<>?,./"

        password = ""
        for _ in range(length):
            idx = int.from_bytes(os.urandom(1), "big") % len(chars)
            password += chars[idx]
        return password

    def export_backup(self, path: Path, export_password: Optional[str] = None) -> bool:
        """Export all secrets as an encrypted JSON backup."""
        self._require_auth()
        key = self.session.get_key()
        entries = self.db.get_all_entries()

        backup_data = []
        for entry in entries:
            try:
                plaintext = CryptoManager.decrypt(
                    entry.encrypted_value, key, entry.nonce, entry.auth_tag
                )
                backup_data.append({
                    "name": entry.name,
                    "tag": entry.user_tag,
                    "value": plaintext,
                    "created_at": entry.created_at.isoformat() if entry.created_at else None,
                    "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
                })
            except DecryptionError:
                continue

        json_data = json.dumps(backup_data, indent=2)

        if export_password:
            export_key, export_salt = KeyDerivation.derive_key_argon2(export_password)
            ct, nonce, tag = CryptoManager.encrypt(json_data, export_key)
            payload = {
                "version": "1.0",
                "type": "aegis-encrypted-export",
                "salt": export_salt.hex(),
                "nonce": nonce.hex(),
                "tag": tag.hex(),
                "data": ct.hex(),
                "count": len(backup_data),
            }
        else:
            payload = {
                "version": "1.0",
                "type": "aegis-export",
                "data": json_data,
                "count": len(backup_data),
            }

        path.write_text(json.dumps(payload, indent=2))
        self.audit.log("export", None, True, f"{len(backup_data)} secrets")
        return True

    def import_backup(self, path: Path, export_password: Optional[str] = None) -> int:
        """Import secrets from an encrypted JSON backup."""
        self._require_auth()

        if not path.exists():
            raise ExportError(f"Backup file not found: {path}")

        payload = json.loads(path.read_text())
        if payload.get("type") == "aegis-encrypted-export" and export_password:
            export_salt = bytes.fromhex(payload["salt"]) if "salt" in payload else None
            export_key, _ = KeyDerivation.derive_key_argon2(export_password, export_salt)
            try:
                json_data = CryptoManager.decrypt(
                    bytes.fromhex(payload["data"]),
                    export_key,
                    bytes.fromhex(payload["nonce"]),
                    bytes.fromhex(payload["tag"]),
                )
            except DecryptionError:
                raise ExportError("Failed to decrypt backup — wrong password or corrupted file")
            backup_data = json.loads(json_data)
        elif payload.get("type") == "aegis-export":
            backup_data = json.loads(payload["data"])
        else:
            raise ExportError("Unknown backup format")

        key = self.session.get_key()
        entries = []
        for item in backup_data:
            ct, nonce, auth_tag = CryptoManager.encrypt(item["value"], key)
            now = datetime.now()
            entry = SecretEntry(
                name=item["name"], user_tag=item.get("tag", "general"),
                encrypted_value=ct, nonce=nonce, auth_tag=auth_tag,
                created_at=now, updated_at=now,
            )
            entries.append(entry)

        count = self.db.bulk_import(entries)
        self.audit.log("import", None, True, f"{count} secrets imported")
        return count

    def logout(self) -> None:
        """End the current session."""
        self.session.destroy()
        self.audit.log("logout", None, True)

    def get_audit_logs(self, limit: int = 50) -> List[Dict]:
        """Retrieve recent audit log entries."""
        return self.audit.get_logs(limit=limit)

    def vault_info(self) -> Dict:
        """Return vault metadata."""
        info = {"initialized": self.config_mgr.is_initialized()}
        if info["initialized"]:
            config = self.config_mgr.load()
            info["version"] = config.get("version", "unknown")
            info["initialized_at"] = config.get("initialized_at", "unknown")
            info["secret_count"] = self.db.entry_count()
            info["authenticated"] = self.session.is_valid()
            if info["authenticated"]:
                expires = self.session.expires_at()
                if expires:
                    remaining = (expires - datetime.now()).total_seconds()
                    info["session_expires_in"] = int(remaining)
        return info

    def _require_auth(self) -> None:
        """Ensure user is authenticated before sensitive operations."""
        if not self.session.is_valid():
            raise AuthenticationError("Not authenticated. Run 'aegis auth' first")

    def _check_lockout(self) -> None:
        """Check if the user is currently rate-limited."""
        if not self.lockout_file.exists():
            return

        data = json.loads(self.lockout_file.read_text())
        lockout_str = data.get("lockout_until", "")
        if not lockout_str:
            return

        lockout_until = datetime.fromisoformat(lockout_str)
        if datetime.now() < lockout_until:
            remaining = int((lockout_until - datetime.now()).total_seconds())
            raise RateLimitError(
                f"Too many failed attempts. Try again in {remaining} seconds"
            )
        self.lockout_file.unlink(missing_ok=True)

    def _record_failed_attempt(self) -> None:
        """Track failed authentication attempts for rate limiting."""
        attempts = 1
        if self.lockout_file.exists():
            try:
                data = json.loads(self.lockout_file.read_text())
                attempts = data.get("attempts", 0) + 1
            except (json.JSONDecodeError, OSError):
                attempts = 1

        if attempts >= self.MAX_AUTH_ATTEMPTS:
            lockout_until = datetime.now() + timedelta(minutes=self.RATE_LOCKOUT_MINUTES)
            self.lockout_file.write_text(json.dumps({
                "attempts": attempts,
                "lockout_until": lockout_until.isoformat(),
            }))
            self.lockout_file.chmod(0o600)
            raise RateLimitError(
                f"Too many failed attempts. Locked out for {self.RATE_LOCKOUT_MINUTES} minutes"
            )
        else:
            self.lockout_file.write_text(json.dumps({
                "attempts": attempts,
                "lockout_until": "",
            }))
            self.lockout_file.chmod(0o600)

    def _clear_lockout(self) -> None:
        """Clear lockout state on successful auth."""
        self.lockout_file.unlink(missing_ok=True)

    @staticmethod
    def _is_strong_password(password: str) -> bool:
        """Validate password strength requirements."""
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in "!@#$%^&*()_+-=[]{}|:;<>?,./" for c in password)
        return all([has_upper, has_lower, has_digit, has_symbol])
