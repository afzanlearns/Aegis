import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from exceptions import DecryptionError


class CryptoManager:
    """Handle all encryption/decryption operations using AES-256-GCM."""

    KEY_SIZE = 32
    NONCE_SIZE = 12
    TAG_SIZE = 16

    @staticmethod
    def encrypt(plaintext: str, key: bytes) -> tuple[bytes, bytes, bytes]:
        """Encrypt plaintext with AES-256-GCM. Returns (ciphertext, nonce, tag)."""
        if len(key) != CryptoManager.KEY_SIZE:
            raise ValueError(f"Key must be {CryptoManager.KEY_SIZE} bytes")

        nonce = os.urandom(CryptoManager.NONCE_SIZE)
        cipher = AESGCM(key)
        ciphertext_with_tag = cipher.encrypt(nonce, plaintext.encode(), None)

        actual_ciphertext = ciphertext_with_tag[:-CryptoManager.TAG_SIZE]
        tag = ciphertext_with_tag[-CryptoManager.TAG_SIZE:]

        return actual_ciphertext, nonce, tag

    @staticmethod
    def decrypt(ciphertext: bytes, key: bytes, nonce: bytes, tag: bytes) -> str:
        """Decrypt with AES-256-GCM. Raises DecryptionError if authentication fails."""
        if len(key) != CryptoManager.KEY_SIZE:
            raise ValueError(f"Key must be {CryptoManager.KEY_SIZE} bytes")
        if len(nonce) != CryptoManager.NONCE_SIZE:
            raise ValueError(f"Nonce must be {CryptoManager.NONCE_SIZE} bytes")

        cipher = AESGCM(key)
        try:
            plaintext = cipher.decrypt(nonce, ciphertext + tag, None)
            return plaintext.decode()
        except Exception as e:
            raise DecryptionError("Decryption failed — wrong key or corrupted data") from e
