import os
import hashlib
import hmac
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id


class KeyDerivation:
    """Secure key derivation from master password using Argon2 + PBKDF2 verification."""

    SALT_SIZE = 16
    KEY_SIZE = 32
    PBKDF2_ITERATIONS = 100_000

    @staticmethod
    def derive_key_argon2(password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
        """Derive encryption key from password using Argon2id (memory-hard, GPU-resistant)."""
        if salt is None:
            salt = os.urandom(KeyDerivation.SALT_SIZE)

        kdf = Argon2id(
            salt=salt,
            length=KeyDerivation.KEY_SIZE,
            iterations=2,
            lanes=8,
            memory_cost=65540,
        )

        key = kdf.derive(password.encode())
        return key, salt

    @staticmethod
    def hash_password(password: str, salt: bytes) -> str:
        """Hash password for verification using PBKDF2-HMAC-SHA256 (not for encryption)."""
        pwd_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt,
            KeyDerivation.PBKDF2_ITERATIONS,
            dklen=32,
        )
        return pwd_hash.hex()

    @staticmethod
    def verify_password(password: str, salt: bytes, stored_hash: str) -> bool:
        """Verify master password using constant-time comparison."""
        computed_hash = KeyDerivation.hash_password(password, salt)
        return hmac.compare_digest(computed_hash, stored_hash)
