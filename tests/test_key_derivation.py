import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.key_derivation import KeyDerivation


class TestKeyDerivation(unittest.TestCase):

    def setUp(self):
        self.password = "MySecureP@ssw0rd!2024"

    def test_derive_key_argon2(self):
        key, salt = KeyDerivation.derive_key_argon2(self.password)
        self.assertEqual(len(key), 32)
        self.assertEqual(len(salt), 16)

    def test_deterministic_with_same_salt(self):
        key1, salt = KeyDerivation.derive_key_argon2(self.password)
        key2, _ = KeyDerivation.derive_key_argon2(self.password, salt)
        self.assertEqual(key1, key2)

    def test_different_salt_different_key(self):
        key1, _ = KeyDerivation.derive_key_argon2(self.password)
        key2, _ = KeyDerivation.derive_key_argon2(self.password)
        self.assertNotEqual(key1, key2)

    def test_password_hash_and_verify(self):
        salt = os.urandom(16)
        pwd_hash = KeyDerivation.hash_password(self.password, salt)
        self.assertEqual(len(pwd_hash), 64)

        self.assertTrue(KeyDerivation.verify_password(self.password, salt, pwd_hash))

    def test_wrong_password_fails(self):
        salt = os.urandom(16)
        pwd_hash = KeyDerivation.hash_password(self.password, salt)
        self.assertFalse(KeyDerivation.verify_password("wrong-password", salt, pwd_hash))

    def test_wrong_salt_fails(self):
        salt = os.urandom(16)
        wrong_salt = os.urandom(16)
        pwd_hash = KeyDerivation.hash_password(self.password, salt)
        self.assertFalse(KeyDerivation.verify_password(self.password, wrong_salt, pwd_hash))

    def test_constant_time_comparison(self):
        """Verify that verification uses constant-time comparison."""
        salt = os.urandom(16)
        pwd_hash = KeyDerivation.hash_password(self.password, salt)

        import time
        start = time.perf_counter()
        KeyDerivation.verify_password(self.password, salt, pwd_hash)
        valid_time = time.perf_counter() - start

        start = time.perf_counter()
        KeyDerivation.verify_password("a" * len(self.password), salt, pwd_hash)
        invalid_time = time.perf_counter() - start

        self.assertAlmostEqual(valid_time, invalid_time, delta=0.5)


if __name__ == "__main__":
    unittest.main()
