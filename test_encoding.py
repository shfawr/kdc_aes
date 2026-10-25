import unittest
from utils.encoding import require_aes128_key, ascii_bytes, to_hex, from_hex

class EncodingTests(unittest.TestCase):
    def test_key_length(self):
        self.assertEqual(len(require_aes128_key("0123456789ABCDEF")),16)
        with self.assertRaises(ValueError): require_aes128_key("short")
    def test_non_ascii_rejected(self):
        with self.assertRaises(ValueError): ascii_bytes("Halo 👋")
    def test_hex_roundtrip(self):
        data = b"hello"
        self.assertEqual(from_hex(to_hex(data)), data)
