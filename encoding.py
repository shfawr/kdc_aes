import json

def ascii_bytes(text: str) -> bytes:
    try:
        return text.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError("Input harus menggunakan karakter ASCII.") from exc

def require_aes128_key(key: str) -> bytes:
    raw = ascii_bytes(key)
    if len(raw) != 16:
        raise ValueError("Key AES-128 harus tepat 16 byte ASCII.")
    return raw

def json_bytes(obj: dict) -> bytes:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=True).encode("ascii")

def parse_json_bytes(data: bytes) -> dict:
    return json.loads(data.decode("ascii"))

def to_hex(data: bytes) -> str:
    return data.hex()

def from_hex(value: str) -> bytes:
    try:
        return bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError("Data Hex tidak valid.") from exc
