import json
from pathlib import Path
from typing import Optional
from exceptions import VaultNotInitializedError


class ConfigManager:
    """Manage vault configuration."""

    def __init__(self, config_path: Path):
        self.config_path = config_path

    def is_initialized(self) -> bool:
        return self.config_path.exists()

    def load(self) -> dict:
        if not self.is_initialized():
            raise VaultNotInitializedError("Vault not initialized. Run 'aegis setup' first")
        return json.loads(self.config_path.read_text())

    def save(self, config: dict) -> None:
        self.config_path.write_text(json.dumps(config, indent=2))
        self.config_path.chmod(0o600)

    def get_salt(self) -> bytes:
        config = self.load()
        return bytes.fromhex(config["salt"])

    def get_password_hash(self) -> str:
        config = self.load()
        return config["password_hash"]

    def get_timeout(self) -> int:
        config = self.load()
        return config.get("max_session_timeout", 1800)
