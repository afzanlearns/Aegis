import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from core.models import SecretEntry, AuditEntry
from exceptions import SecretNotFoundError


class DatabaseManager:
    """SQLite database wrapper for secret storage."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self) -> None:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS secrets (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                user_tag TEXT DEFAULT 'general',
                encrypted_value BLOB NOT NULL,
                nonce BLOB NOT NULL,
                auth_tag BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accessed_at TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                secret_name TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT 1,
                details TEXT DEFAULT ''
            )
        """)

        conn.commit()
        conn.close()
        self._migrate_schema()

    def _migrate_schema(self) -> None:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        has_old_tag = False
        has_secret_type = False
        try:
            cursor.execute("SELECT tag FROM secrets LIMIT 1")
            has_old_tag = True
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("SELECT secret_type FROM secrets LIMIT 1")
            has_secret_type = True
        except sqlite3.OperationalError:
            pass

        if has_old_tag:
            try:
                cursor.execute("SELECT auth_tag FROM secrets LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE secrets ADD COLUMN auth_tag BLOB")
                cursor.execute("UPDATE secrets SET auth_tag = tag")
                conn.commit()

            # Drop the old `tag` column to avoid NOT NULL constraint on INSERT
            try:
                cursor.execute("ALTER TABLE secrets DROP COLUMN tag")
                conn.commit()
            except sqlite3.OperationalError:
                pass

        if has_secret_type:
            try:
                cursor.execute("SELECT user_tag FROM secrets LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute("ALTER TABLE secrets ADD COLUMN user_tag TEXT DEFAULT 'general'")
                cursor.execute("UPDATE secrets SET user_tag = secret_type")
                conn.commit()

        conn.close()
        self.db_path.chmod(0o600)

    def save_secret(self, entry: SecretEntry) -> bool:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id FROM secrets WHERE name = ?", (entry.name,)
            )
            existing = cursor.fetchone()
            is_update = existing is not None

            if is_update:
                cursor.execute("""
                    UPDATE secrets SET
                        user_tag = ?, encrypted_value = ?, nonce = ?,
                        auth_tag = ?, updated_at = ?
                    WHERE name = ?
                """, (
                    entry.user_tag,
                    entry.encrypted_value,
                    entry.nonce,
                    entry.auth_tag,
                    entry.updated_at.isoformat(),
                    entry.name,
                ))
            else:
                cursor.execute("""
                    INSERT INTO secrets
                        (id, name, user_tag, encrypted_value, nonce, auth_tag, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.id or os.urandom(16).hex(),
                    entry.name,
                    entry.user_tag,
                    entry.encrypted_value,
                    entry.nonce,
                    entry.auth_tag,
                    entry.created_at.isoformat(),
                    entry.updated_at.isoformat(),
                ))
            conn.commit()
            return is_update
        finally:
            conn.close()

    def get_secret(self, name: str) -> SecretEntry:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, name, user_tag, encrypted_value, nonce, auth_tag, created_at, updated_at, accessed_at "
                "FROM secrets WHERE name = ?", (name,)
            )
            row = cursor.fetchone()
            if not row:
                raise SecretNotFoundError(f"Secret '{name}' not found")

            entry = SecretEntry(
                id=row[0], name=row[1], user_tag=row[2],
                encrypted_value=row[3], nonce=row[4], auth_tag=row[5],
                created_at=datetime.fromisoformat(row[6]) if row[6] else datetime.now(),
                updated_at=datetime.fromisoformat(row[7]) if row[7] else datetime.now(),
                accessed_at=datetime.fromisoformat(row[8]) if row[8] else None,
            )

            cursor.execute(
                "UPDATE secrets SET accessed_at = ? WHERE name = ?",
                (datetime.now().isoformat(), name),
            )
            conn.commit()
            return entry
        finally:
            conn.close()

    def list_secrets(self) -> List[Dict]:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT name, user_tag, created_at, accessed_at "
                "FROM secrets ORDER BY accessed_at DESC"
            )
            rows = cursor.fetchall()
            secrets = []
            for row in rows:
                secrets.append({
                    "name": row[0],
                    "user_tag": row[1] or "general",
                    "created": row[2],
                    "accessed": row[3],
                })
            return secrets
        finally:
            conn.close()

    def list_secrets_by_tag(self, tag: str) -> List[Dict]:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT name, user_tag, created_at, accessed_at "
                "FROM secrets WHERE user_tag = ? ORDER BY accessed_at DESC", (tag,)
            )
            rows = cursor.fetchall()
            return [
                {"name": r[0], "user_tag": r[1] or "general", "created": r[2], "accessed": r[3]}
                for r in rows
            ]
        finally:
            conn.close()

    def delete_secret(self, name: str) -> bool:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM secrets WHERE name = ?", (name,))
            if cursor.rowcount == 0:
                raise SecretNotFoundError(f"Secret '{name}' not found")
            conn.commit()
            return True
        finally:
            conn.close()

    def search_secrets(self, query: str) -> List[Dict]:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT name, user_tag, created_at, accessed_at "
                "FROM secrets WHERE name LIKE ? ORDER BY accessed_at DESC",
                (f"%{query}%",)
            )
            rows = cursor.fetchall()
            return [
                {"name": r[0], "user_tag": r[1] or "general", "created": r[2], "accessed": r[3]}
                for r in rows
            ]
        finally:
            conn.close()

    def get_all_entries(self) -> List[SecretEntry]:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, name, user_tag, encrypted_value, nonce, auth_tag, created_at, updated_at, accessed_at "
                "FROM secrets ORDER BY name"
            )
            rows = cursor.fetchall()
            entries = []
            for row in rows:
                entries.append(SecretEntry(
                    id=row[0], name=row[1], user_tag=row[2],
                    encrypted_value=row[3], nonce=row[4], auth_tag=row[5],
                    created_at=datetime.fromisoformat(row[6]) if row[6] else datetime.now(),
                    updated_at=datetime.fromisoformat(row[7]) if row[7] else datetime.now(),
                    accessed_at=datetime.fromisoformat(row[8]) if row[8] else None,
                ))
            return entries
        finally:
            conn.close()

    def bulk_import(self, entries: List[SecretEntry]) -> int:
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        count = 0
        try:
            for entry in entries:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO secrets
                            (id, name, user_tag, encrypted_value, nonce, auth_tag, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        entry.id or os.urandom(16).hex(),
                        entry.name, entry.user_tag,
                        entry.encrypted_value, entry.nonce, entry.auth_tag,
                        entry.created_at.isoformat(), entry.updated_at.isoformat(),
                    ))
                    count += 1
                except sqlite3.IntegrityError:
                    continue
            conn.commit()
            return count
        finally:
            conn.close()

    def entry_count(self) -> int:
        conn = sqlite3.connect(str(self.db_path))
        try:
            return conn.execute("SELECT COUNT(*) FROM secrets").fetchone()[0]
        finally:
            conn.close()
