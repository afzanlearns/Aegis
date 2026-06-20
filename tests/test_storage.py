import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from storage.database import DatabaseManager
from core.models import SecretEntry
from exceptions import SecretNotFoundError


class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.tmp_dir / "test.db"
        self.db = DatabaseManager(self.db_path)

    def tearDown(self):
        if self.db_path.exists():
            self.db_path.unlink()

    def test_save_and_get_secret(self):
        entry = SecretEntry(
            name="test-key", secret_type="api-key",
            encrypted_value=b"encrypted_data", nonce=b"nonce12345678", tag=b"tag123456789012",
        )
        self.db.save_secret(entry)
        result = self.db.get_secret("test-key")
        self.assertEqual(result.name, "test-key")
        self.assertEqual(result.encrypted_value, b"encrypted_data")

    def test_get_nonexistent_secret(self):
        with self.assertRaises(SecretNotFoundError):
            self.db.get_secret("nonexistent")

    def test_list_secrets(self):
        entries = [
            SecretEntry(name="key1", secret_type="password",
                        encrypted_value=b"e1", nonce=b"n"*12, tag=b"t"*16),
            SecretEntry(name="key2", secret_type="api-key",
                        encrypted_value=b"e2", nonce=b"n"*12, tag=b"t"*16),
        ]
        for e in entries:
            self.db.save_secret(e)

        secrets = self.db.list_secrets()
        self.assertEqual(len(secrets), 2)
        names = [s["name"] for s in secrets]
        self.assertIn("key1", names)
        self.assertIn("key2", names)

    def test_delete_secret(self):
        entry = SecretEntry(
            name="delete-me", secret_type="password",
            encrypted_value=b"data", nonce=b"n"*12, tag=b"t"*16,
        )
        self.db.save_secret(entry)
        self.db.delete_secret("delete-me")
        with self.assertRaises(SecretNotFoundError):
            self.db.get_secret("delete-me")

    def test_delete_nonexistent(self):
        with self.assertRaises(SecretNotFoundError):
            self.db.delete_secret("does-not-exist")

    def test_search_secrets(self):
        entries = [
            SecretEntry(name="github-token", secret_type="api-key",
                        encrypted_value=b"e1", nonce=b"n"*12, tag=b"t"*16),
            SecretEntry(name="gitlab-token", secret_type="api-key",
                        encrypted_value=b"e2", nonce=b"n"*12, tag=b"t"*16),
            SecretEntry(name="aws-key", secret_type="duo",
                        encrypted_value=b"e3", nonce=b"n"*12, tag=b"t"*16),
        ]
        for e in entries:
            self.db.save_secret(e)

        results = self.db.search_secrets("git")
        self.assertEqual(len(results), 2)

        results = self.db.search_secrets("aws")
        self.assertEqual(len(results), 1)

        results = self.db.search_secrets("nonexistent")
        self.assertEqual(len(results), 0)

    def test_entry_count(self):
        self.assertEqual(self.db.entry_count(), 0)
        entry = SecretEntry(
            name="count-test", secret_type="password",
            encrypted_value=b"data", nonce=b"n"*12, tag=b"t"*16,
        )
        self.db.save_secret(entry)
        self.assertEqual(self.db.entry_count(), 1)


if __name__ == "__main__":
    unittest.main()
