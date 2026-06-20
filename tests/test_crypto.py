import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.crypto import CryptoManager
from exceptions import DecryptionError


class TestCryptoManager(unittest.TestCase):

    def setUp(self):
        self.key = os.urandom(32)
        self.plaintext = "my-secret-api-key-12345!@#$"

    def test_encrypt_decrypt(self):
        ct, nonce, tag = CryptoManager.encrypt(self.plaintext, self.key)
        self.assertGreater(len(ct), 0)
        self.assertEqual(len(nonce), 12)
        self.assertEqual(len(tag), 16)

        decrypted = CryptoManager.decrypt(ct, self.key, nonce, tag)
        self.assertEqual(decrypted, self.plaintext)

    def test_wrong_key_rejected(self):
        ct, nonce, tag = CryptoManager.encrypt(self.plaintext, self.key)
        wrong_key = os.urandom(32)
        with self.assertRaises(DecryptionError):
            CryptoManager.decrypt(ct, wrong_key, nonce, tag)

    def test_wrong_nonce_rejected(self):
        ct, nonce, tag = CryptoManager.encrypt(self.plaintext, self.key)
        wrong_nonce = os.urandom(12)
        with self.assertRaises(DecryptionError):
            CryptoManager.decrypt(ct, self.key, wrong_nonce, tag)

    def test_empty_string(self):
        ct, nonce, tag = CryptoManager.encrypt("", self.key)
        decrypted = CryptoManager.decrypt(ct, self.key, nonce, tag)
        self.assertEqual(decrypted, "")

    def test_special_characters(self):
        special = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~¡™£¢∞§¶•ªº–≠"
        ct, nonce, tag = CryptoManager.encrypt(special, self.key)
        decrypted = CryptoManager.decrypt(ct, self.key, nonce, tag)
        self.assertEqual(decrypted, special)

    def test_key_size_validation(self):
        with self.assertRaises(ValueError):
            CryptoManager.encrypt("test", os.urandom(16))
        with self.assertRaises(ValueError):
            CryptoManager.decrypt(b"test", os.urandom(16), os.urandom(12), os.urandom(16))

    def test_different_iv_per_encryption(self):
        ct1, nonce1, _ = CryptoManager.encrypt(self.plaintext, self.key)
        ct2, nonce2, _ = CryptoManager.encrypt(self.plaintext, self.key)
        self.assertNotEqual(nonce1, nonce2)
        self.assertNotEqual(ct1, ct2)


if __name__ == "__main__":
    unittest.main()
