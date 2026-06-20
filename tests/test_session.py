import os
import sys
import time
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.session import SessionManager
from exceptions import SessionExpiredError


class TestSessionManager(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.session_file = Path(self.tmp_dir) / ".session"
        self.session = SessionManager(self.session_file)

    def tearDown(self):
        self.session.destroy()

    def test_no_session_initially(self):
        self.assertFalse(self.session.is_valid())

    def test_create_and_validate(self):
        key = os.urandom(32)
        self.session.create(key, timeout=60)
        self.assertTrue(self.session.is_valid())
        self.assertEqual(self.session.get_key(), key)

    def test_session_expired(self):
        key = os.urandom(32)
        self.session.create(key, timeout=1)
        time.sleep(1.5)
        self.assertFalse(self.session.is_valid())
        with self.assertRaises(SessionExpiredError):
            self.session.get_key()

    def test_destroy(self):
        key = os.urandom(32)
        self.session.create(key)
        self.assertTrue(self.session.is_valid())
        self.session.destroy()
        self.assertFalse(self.session.is_valid())

    def test_expires_at(self):
        key = os.urandom(32)
        self.session.create(key, timeout=1800)
        expires = self.session.expires_at()
        self.assertIsNotNone(expires)

    def test_expires_at_no_session(self):
        self.assertIsNone(self.session.expires_at())

    def test_custom_timeout(self):
        key = os.urandom(32)
        self.session.create(key, timeout=3600)
        expires = self.session.expires_at()
        self.assertIsNotNone(expires)


if __name__ == "__main__":
    unittest.main()
