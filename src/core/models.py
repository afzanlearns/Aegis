from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SecretEntry:
    """Represents a stored secret entry."""
    name: str
    encrypted_value: bytes
    nonce: bytes
    auth_tag: bytes
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    accessed_at: Optional[datetime] = None
    id: Optional[str] = None
    user_tag: str = "general"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "user_tag": self.user_tag,
            "created": self.created_at.isoformat() if self.created_at else None,
            "updated": self.updated_at.isoformat() if self.updated_at else None,
            "accessed": self.accessed_at.isoformat() if self.accessed_at else None,
        }


@dataclass
class AuditEntry:
    """Represents an audit log entry."""
    action: str
    secret_name: Optional[str]
    timestamp: datetime
    success: bool
    details: str = ""
    id: Optional[int] = None
