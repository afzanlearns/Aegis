class AegisError(Exception):
    """Base exception for all Aegis errors."""

class VaultNotInitializedError(AegisError):
    """Raised when attempting to use an uninitialized vault."""

class AuthenticationError(AegisError):
    """Raised when authentication fails."""

class SessionExpiredError(AegisError):
    """Raised when the session has timed out."""

class SecretNotFoundError(AegisError):
    """Raised when a requested secret does not exist."""

class SecretAlreadyExistsError(AegisError):
    """Raised when trying to save a secret with a duplicate name."""

class DecryptionError(AegisError):
    """Raised when decryption fails (wrong key or corrupted data)."""

class WeakPasswordError(AegisError):
    """Raised when the master password is too weak."""

class RateLimitError(AegisError):
    """Raised when too many failed auth attempts occur."""

class PermissionError(AegisError):
    """Raised when file permissions are insecure."""

class ExportError(AegisError):
    """Raised when export/import operations fail."""
