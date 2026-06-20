import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from core.models import AuditEntry


class AuditLogger:
    """Append-only audit logging for all vault operations."""

    def __init__(self, db_path: Path):
        self.db_path = db_path

    def log(self, action: str, secret_name: Optional[str], success: bool, details: str = "") -> None:
        conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute(
                "INSERT INTO audit_log (action, secret_name, timestamp, success, details) VALUES (?, ?, ?, ?, ?)",
                (action, secret_name, datetime.now().isoformat(), success, details),
            )
            conn.commit()
        finally:
            conn.close()

    def get_logs(self, limit: int = 50, action_filter: Optional[str] = None) -> List[Dict]:
        conn = sqlite3.connect(str(self.db_path))
        try:
            if action_filter:
                rows = conn.execute(
                    "SELECT id, action, secret_name, timestamp, success, details "
                    "FROM audit_log WHERE action = ? ORDER BY id DESC LIMIT ?",
                    (action_filter, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, action, secret_name, timestamp, success, details "
                    "FROM audit_log ORDER BY id DESC LIMIT ?",
                    (limit,),
                ).fetchall()

            return [
                {
                    "id": r[0], "action": r[1], "secret_name": r[2],
                    "timestamp": r[3], "success": bool(r[4]), "details": r[5],
                }
                for r in rows
            ]
        finally:
            conn.close()
