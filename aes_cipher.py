from secrets import token_bytes
from .aes_core import add_round_key, sub_bytes, inv_sub_bytes, shift_rows, inv_shift_rows, mix_columns, inv_mix_columns
from .key_expansion import expand_key

BLOCK = 16

def encrypt_block(block: bytes, key: bytes) -> bytes:
    if len(block) != 16: raise ValueError("Blok AES harus 16 byte.")
    rounds = expand_key(key)
    s = add_round_key(list(block), rounds[0])
    for r in range(1, 10):
        s = add_round_key(mix_columns(shift_rows(sub_bytes(s))), rounds[r])
    s = add_round_key(shift_rows(sub_bytes(s)), rounds[10])
    return bytes(s)

def decrypt_block(block: bytes, key: bytes) -> bytes:
    if len(block) != 16: raise ValueError("Blok AES harus 16 byte.")
    rounds = expand_key(key)
    s = add_round_key(list(block), rounds[10])
    for r in range(9, 0, -1):
        s = inv_mix_columns(add_round_key(inv_shift_rows(inv_sub_bytes(s)), rounds[r]))
    s = add_round_key(inv_sub_bytes(inv_shift_rows(s)), rounds[0])
    return bytes(s)

def _pad(data: bytes) -> bytes:
    n = BLOCK - (len(data) % BLOCK)
    return data + bytes([n])*n

def _unpad(data: bytes) -> bytes:
    if not data or len(data) % BLOCK:
        raise ValueError("Panjang plaintext/padding tidak valid.")
    n = data[-1]
    if n < 1 or n > BLOCK or data[-n:] != bytes([n])*n:
        raise ValueError("PKCS#7 padding tidak valid.")
    return data[:-n]

def encrypt_cbc(key: bytes, plaintext: bytes, iv: bytes | None = None) -> bytes:
    if len(key) != 16: raise ValueError("Key AES-128 harus 16 byte.")
    iv = token_bytes(16) if iv is None else iv
    if len(iv) != 16: raise ValueError("IV harus 16 byte.")
    padded = _pad(plaintext)
    out = bytearray(iv)
    prev = iv
    for i in range(0, len(padded), BLOCK):
        x = bytes(a ^ b for a,b in zip(padded[i:i+BLOCK], prev))
        prev = encrypt_block(x, key)
        out.extend(prev)
    return bytes(out)  # IV || ciphertext

def decrypt_cbc(key: bytes, payload: bytes) -> bytes:
    if len(key) != 16: raise ValueError("Key AES-128 harus 16 byte.")
    if len(payload) < 32 or (len(payload)-16) % BLOCK:
        raise ValueError("Payload CBC harus berisi IV dan ciphertext lengkap.")
    iv, ct = payload[:16], payload[16:]
    prev = iv
    out = bytearray()
    for i in range(0, len(ct), BLOCK):
        block = ct[i:i+BLOCK]
        dec = decrypt_block(block, key)
        out.extend(a ^ b for a,b in zip(dec, prev))
        prev = block
    return _unpad(bytes(out))
