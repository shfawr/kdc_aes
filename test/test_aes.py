import unittest
from aes.aes_cipher import encrypt_block, decrypt_block, encrypt_cbc, decrypt_cbc
from utils.encoding import require_aes128_key

def run_aes_self_test():
    key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    pt = bytes.fromhex("00112233445566778899aabbccddeeff")
    expected = bytes.fromhex("69c4e0d86a7b0430d8cdb78070b4c55a")
    got = encrypt_block(pt, key)
    if got != expected:
        raise SystemExit(f"AES test FAILED: {got.hex()}")
    if decrypt_block(got, key) != pt:
        raise SystemExit("AES decrypt test FAILED")
    msg = b"Hello CBC"
    payload = encrypt_cbc(key, msg)
    if decrypt_cbc(key, payload) != msg:
        raise SystemExit("CBC test FAILED")
    print("[SELF-TEST] AES-128 encrypt/decrypt/CBC: PASSED")
    print(f"  FIPS-197 vector = {got.hex()}")

class AESTests(unittest.TestCase):
    def test_fips197_vector(self):
        key = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
        pt = bytes.fromhex("00112233445566778899aabbccddeeff")
        self.assertEqual(encrypt_block(pt,key).hex(), "69c4e0d86a7b0430d8cdb78070b4c55a")
        self.assertEqual(decrypt_block(encrypt_block(pt,key),key), pt)

    def test_cbc_roundtrip(self):
        key = b"0123456789ABCDEF"
        for msg in (b"", b"A", b"1234567890123456", b"hello world"):
            self.assertEqual(decrypt_cbc(key, encrypt_cbc(key,msg)), msg)

    def test_bad_padding_rejected(self):
        key = b"0123456789ABCDEF"
        payload = encrypt_cbc(key,b"sample")
        bad = payload[:-1] + bytes([payload[-1] ^ 1])
        with self.assertRaises(ValueError):
            decrypt_cbc(key,bad)
